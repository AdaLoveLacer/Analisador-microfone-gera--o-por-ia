"""Main analyzer orchestrating audio capture, transcription, detection and playback."""

import threading
import queue
import logging
import time
import numpy as np
from typing import Optional, Callable, Dict, Any
from collections import deque
from datetime import datetime

from core.config_manager import ConfigManager
from core.event_logger import get_logger
from audio.processor import AudioProcessor
from audio.transcriber import TranscriberThread
from audio.audio_utils import apply_gain
from ai.keyword_detector import KeywordDetector
from ai.context_analyzer import ContextAnalyzer
from ai.llm_engine import LLMEngine
from sound.player import SoundManager
from database.db_manager import DatabaseManager

logger = get_logger(__name__)


class MicrophoneAnalyzer:
    """Main analyzer that orchestrates everything."""

    def __init__(
        self,
        config_dir: str = ".",
        database_dir: str = ".",
    ):
        """
        Initialize MicrophoneAnalyzer.

        Args:
            config_dir: Configuration directory
            database_dir: Database directory
        """
        # Initialize components
        self.config = ConfigManager(config_dir)
        self.database = DatabaseManager(database_dir)

        # Audio components
        self.audio_processor: Optional[AudioProcessor] = None
        self.transcriber: Optional[TranscriberThread] = None

        # AI components (lazy loaded - disabled by default to save memory)
        self.keyword_detector = KeywordDetector(self.config.get_keywords())
        self._context_analyzer: Optional[ContextAnalyzer] = None
        self._llm_engine: Optional[LLMEngine] = None

        # Sound component
        self.sound_manager = SoundManager(self.config.get_sounds())

        # State
        self.is_running = False
        self.is_capturing = False
        self.current_transcript = ""
        self.last_detected_keyword = None

        # Queues
        self.event_queue = queue.Queue()

        # Callbacks
        self._transcription_callbacks = []
        self._detection_callbacks = []
        self._status_callbacks = []
        self._audio_level_callbacks = []

        # Threads
        self._processor_thread: Optional[threading.Thread] = None
        self._event_thread: Optional[threading.Thread] = None

        # Restart protection: prevent tight restart loops if capture is failing
        self._restart_timestamps = deque()
        self._delayed_restart_scheduled = False
        # Device change lock to prevent concurrent device changes
        self._device_change_lock = threading.Lock()

        # Thread synchronization (CORREÇÃO: race conditions)
        self._state_lock = threading.Lock()
        self._callback_lock = threading.Lock()

        logger.info("MicrophoneAnalyzer initialized (AI modules disabled by default)")

    @property
    def context_analyzer(self) -> ContextAnalyzer:
        """Get context analyzer (lazy loaded)."""
        if self._context_analyzer is None:
            self._context_analyzer = ContextAnalyzer()
        return self._context_analyzer

    @property
    def llm_engine(self) -> LLMEngine:
        """Get LLM engine (lazy loaded)."""
        if self._llm_engine is None:
            self._llm_engine = LLMEngine()
        return self._llm_engine

    def start(self) -> None:
        """Start the analyzer."""
        try:
            with self._state_lock:
                if self.is_running:
                    logger.warning("Analyzer already running")
                    return

                self.is_running = True

            # CORREÇÃO: Limpeza automática de registros antigos (libera espaço em disco)
            # Limpar registros com mais de 7 dias a cada inicialização
            try:
                self.database.clear_old_records(days=7)
            except Exception as e:
                logger.warning(f"Failed to clear old database records: {e}")

            # START: Restart protection check
            # Avoid repeated quick restarts when there were multiple restarts recently.
            try:
                # Read limits from config with safe defaults
                restart_limit = int(self.config.get("app.restart_limit", 3))
                restart_window = float(self.config.get("app.restart_window_seconds", 60.0))
                cooldown_seconds = float(self.config.get("app.restart_cooldown_seconds", 30.0))

                # Prune old timestamps
                now_ts = time.time()
                while self._restart_timestamps and (now_ts - self._restart_timestamps[0]) > restart_window:
                    self._restart_timestamps.popleft()

                if len(self._restart_timestamps) >= restart_limit:
                    logger.warning(
                        "Too many recent analyzer startups: %s within %ss. Scheduling delayed restart in %ss",
                        len(self._restart_timestamps), restart_window, cooldown_seconds,
                    )

                    # If we already scheduled a delayed restart, skip scheduling again
                    if not self._delayed_restart_scheduled:
                        def delayed_start():
                            try:
                                time.sleep(cooldown_seconds)
                                self._delayed_restart_scheduled = False
                                # try start again once
                                self.start()
                            except Exception as e:
                                logger.error(f"Delayed restart failed: {e}")

                        self._delayed_restart_scheduled = True
                        t = threading.Thread(target=delayed_start, daemon=True)
                        t.start()

                    # Do not proceed with immediate start to avoid loops
                    self.is_running = False
                    return

            except Exception as e:
                # If anything with restart protection fails, just continue to attempt starting
                logger.debug(f"Restart protection check failed: {e}")
            # END: Restart protection check

            # CORREÇÃO: Reutilizar AudioProcessor ao invés de recriar
            if not self.audio_processor:
                audio_config = self.config.get("audio")
                self.audio_processor = AudioProcessor(
                    device_id=audio_config.get("device_id", -1),
                    sample_rate=audio_config.get("sample_rate", 16000),
                    chunk_size=audio_config.get("chunk_size", 2048),
                    channels=audio_config.get("channels", 1),
                    silence_threshold=audio_config.get("silence_threshold", 0.02),
                )

            # Start audio capture
            if not self.audio_processor.is_recording:
                self.audio_processor.start()

            # CORREÇÃO: Reutilizar Transcriber ao invés de recriar
            if not self.transcriber:
                whisper_config = self.config.get("whisper", {})
                
                # Auto-detect device (prefer GPU)
                device = whisper_config.get("device", "auto")
                if device == "auto":
                    try:
                        import torch
                        device = "cuda" if torch.cuda.is_available() else "cpu"
                        logger.info(f"Auto-detected Whisper device: {device}")
                    except:
                        device = "cpu"
                
                # Criar TranscriberThread com todas as configurações avançadas
                self.transcriber = TranscriberThread(
                    model_name=whisper_config.get("model", "base"),
                    language=whisper_config.get("language", "pt"),
                    device=device,
                    task=whisper_config.get("task", "transcribe"),
                    beam_size=whisper_config.get("beam_size", 5),
                    best_of=whisper_config.get("best_of", 5),
                    temperature=whisper_config.get("temperature", 0.0),
                    patience=whisper_config.get("patience", 1.0),
                    length_penalty=whisper_config.get("length_penalty", 1.0),
                    suppress_blank=whisper_config.get("suppress_blank", True),
                    condition_on_previous_text=whisper_config.get("condition_on_previous_text", True),
                    no_speech_threshold=whisper_config.get("no_speech_threshold", 0.6),
                    compression_ratio_threshold=whisper_config.get("compression_ratio_threshold", 2.4),
                    logprob_threshold=whisper_config.get("logprob_threshold", -1.0),
                    initial_prompt=whisper_config.get("initial_prompt", "Esta é uma transcrição em português brasileiro."),
                    word_timestamps=whisper_config.get("word_timestamps", False),
                    hallucination_silence_threshold=whisper_config.get("hallucination_silence_threshold"),
                )
            
            if hasattr(self.transcriber, 'is_running') and not self.transcriber.is_running:
                self.transcriber.start()

            # Start processing thread
            self._processor_thread = threading.Thread(
                target=self._processing_loop, daemon=True
            )
            self._processor_thread.start()

            # Start event thread
            self._event_thread = threading.Thread(
                target=self._event_loop, daemon=True
            )
            self._event_thread.start()

            # Record successful start attempt (timestamp) so restart protection can track
            try:
                self._restart_timestamps.append(time.time())
            except Exception:
                pass

            self.is_capturing = True
            self._notify_status()

            logger.info("Analyzer started")
            self.database.add_event("analyzer_started")

        except Exception as e:
            logger.error(f"Failed to start analyzer: {e}")
            self.is_running = False
            raise

    def stop(self) -> None:
        """Stop the analyzer."""
        try:
            with self._state_lock:
                self.is_running = False
                self.is_capturing = False

            # Stop components
            if self.audio_processor and self.audio_processor.is_recording:
                self.audio_processor.stop()

            if self.transcriber and hasattr(self.transcriber, 'is_running') and self.transcriber.is_running:
                self.transcriber.stop()

            if self.sound_manager:
                self.sound_manager.stop_sound()

            logger.info("Analyzer stopped")
            self.database.add_event("analyzer_stopped")
            self._notify_status()

        except Exception as e:
            logger.error(f"Error stopping analyzer: {e}")

    def _processing_loop(self) -> None:
        """Main processing loop with VAD (Voice Activity Detection) for complete sentences."""
        try:
            audio_buffer = []
            min_duration = self.config.get("audio.min_duration_seconds", 1.5)
            max_duration = self.config.get("audio.max_duration_seconds", 15.0)  # Máximo 15 segundos
            silence_duration_to_stop = self.config.get("audio.silence_duration_to_stop", 1.0)  # 1 segundo de silêncio = fim da frase
            sample_rate = self.config.get("audio.sample_rate", 16000)
            min_samples = int(min_duration * sample_rate)
            max_samples = int(max_duration * sample_rate)
            silence_samples_threshold = int(silence_duration_to_stop * sample_rate)
            
            # Estado do VAD (Voice Activity Detection)
            consecutive_silence_samples = 0
            has_speech_started = False
            speech_threshold = self.config.get("audio.speech_threshold", 0.015)  # Threshold para detectar fala

            while self.is_running:
                try:
                    # Get audio chunk
                    chunk = self.audio_processor.get_chunk(timeout=0.5)
                    if chunk is None:
                        continue

                    # Calcular e enviar o nível de áudio
                    # CORREÇÃO: Usar RMS para melhor representação visual
                    # O áudio de microfone típico tem RMS entre 0.001 e 0.3
                    rms = np.sqrt(np.mean(chunk ** 2))
                    peak = np.max(np.abs(chunk))
                    
                    # Usar escala logarítmica mais sensível para microfone
                    # Mapeamento: 0.001 (-60dB) a 0.3 (-10dB) → 0 a 1
                    # Formula: level = (20*log10(rms) + 60) / 50
                    if rms > 1e-6:
                        db = 20 * np.log10(rms)
                        # Mapear -60dB a -10dB para 0 a 1 (range mais sensível)
                        normalized_level = max(0.0, min(1.0, (db + 60) / 50))
                    else:
                        normalized_level = 0.0
                    
                    energy = rms
                    
                    with self._callback_lock:
                        for callback in self._audio_level_callbacks:
                            try:
                                callback({"level": float(normalized_level), "energy": float(energy)})
                            except Exception as e:
                                logger.error(f"Error in audio level callback: {e}")

                    # VAD: Detectar se há fala ou silêncio
                    is_speech = rms > speech_threshold
                    
                    if is_speech:
                        has_speech_started = True
                        consecutive_silence_samples = 0
                    else:
                        consecutive_silence_samples += len(chunk)

                    # Detect sustained low audio (possible wrong mic gain/threshold)
                    try:
                        silence_threshold = (
                            self.audio_processor.silence_threshold
                            if self.audio_processor
                            else self.config.get("audio.silence_threshold", 0.02)
                        )
                        if not hasattr(self, "_consecutive_silent_count"):
                            self._consecutive_silent_count = 0

                        if normalized_level < silence_threshold:
                            self._consecutive_silent_count += 1
                        else:
                            self._consecutive_silent_count = 0

                        # If we've seen a sustained period of silence, warn once every X occurrences
                        if self._consecutive_silent_count and self._consecutive_silent_count % 50 == 0:
                            logger.warning(
                                "Sustained low audio detected (normalized_level=%.4f < threshold=%.4f) - check microphone gain or silence_threshold",
                                normalized_level,
                                silence_threshold,
                            )
                    except Exception:
                        pass

                    # Add to buffer
                    audio_buffer.append(chunk)
                    total_samples = sum(len(c) for c in audio_buffer)

                    # Decidir quando enviar para transcrição:
                    # 1. Se atingiu o máximo de duração (forçar envio)
                    # 2. Se já passou o mínimo E detectou pausa longa após fala
                    should_transcribe = False
                    
                    if total_samples >= max_samples:
                        # Atingiu máximo - enviar imediatamente
                        should_transcribe = True
                        logger.debug(f"Enviando para transcrição: atingiu máximo ({max_duration}s)")
                    elif total_samples >= min_samples and has_speech_started:
                        # Já tem o mínimo e detectou fala - verificar se há pausa
                        if consecutive_silence_samples >= silence_samples_threshold:
                            should_transcribe = True
                            logger.debug(f"Enviando para transcrição: pausa detectada após {total_samples/sample_rate:.1f}s de áudio")
                    
                    if should_transcribe and len(audio_buffer) > 0:
                        # Combine chunks
                        audio_data = np.concatenate(audio_buffer)

                        # Apply auto-gain normalization if enabled and submit for transcription
                        try:
                            prepared = self._prepare_audio_for_transcription(audio_data, sample_rate)
                        except Exception as e:
                            logger.error(f"Error preparing audio for transcription: {e}")
                            prepared = audio_data

                        self.transcriber.submit_audio(prepared, sample_rate)

                        # Clear buffer e resetar VAD
                        audio_buffer = []
                        consecutive_silence_samples = 0
                        has_speech_started = False

                        # Get transcription result
                        result = self.transcriber.get_result(timeout=15.0)
                        if result:
                            self._handle_transcription(result)

                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
                    time.sleep(0.1)

        except Exception as e:
            logger.error(f"Processing loop crashed: {e}")
            self.is_running = False

    def _handle_transcription(self, result: Dict[str, Any]) -> None:
        """
        Handle transcription result.

        Args:
            result: Transcription result from Whisper
        """
        try:
            text = result.get("text", "").strip()
            confidence = result.get("confidence", 0.0)

            if not text:
                return

            self.current_transcript = text

            # Log transcription
            self.database.add_transcription(text, confidence, 0.0)

            # Notify callbacks
            for callback in self._transcription_callbacks:
                try:
                    callback(text, confidence)
                except Exception as e:
                    logger.error(f"Error in transcription callback: {e}")

            # Detect keywords
            self._detect_keywords(text)

        except Exception as e:
            logger.error(f"Error handling transcription: {e}")

    def _prepare_audio_for_transcription(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply auto-gain if enabled in config.

        Uses RMS-based dB estimation and applies a limited gain to reach target dB.
        """
        try:
            # Check if auto gain is enabled (default True)
            auto_gain = bool(self.config.get("audio.auto_gain_enabled", True))
            if not auto_gain:
                return audio_data

            target_db = float(self.config.get("audio.target_db", -20.0))
            max_gain_db = float(self.config.get("audio.max_gain_db", 20.0))

            # Compute current RMS and dB
            rms = np.sqrt(np.mean(audio_data ** 2)) if audio_data.size > 0 else 0.0
            current_db = 20 * np.log10(max(rms, 1e-6))

            # If current dB is already >= target, do nothing
            if current_db >= target_db:
                return audio_data

            gain_db = target_db - current_db
            # Cap the gain to avoid extreme amplification
            gain_db = max(min(gain_db, max_gain_db), -max_gain_db)

            if abs(gain_db) < 0.1:
                return audio_data

            # Apply gain in dB
            return apply_gain(audio_data, gain_db)
        except Exception as e:
            logger.debug(f"Autotuning failed: {e}")
            return audio_data

    def _detect_keywords(self, text: str) -> None:
        """
        Detect keywords in text.

        Args:
            text: Text to analyze
        """
        try:
            keyword_id, confidence = self.keyword_detector.detect(text)

            if not keyword_id:
                return

            logger.info(f"Keyword detected: {keyword_id} (confidence={confidence})")

            # Perform context analysis if enabled (DISABLED by default)
            context_score = 0.0
            if self.config.get("ai.context_analysis_enabled", False):
                keyword_data = self.config.get_keyword(keyword_id)
                if keyword_data:
                    context_keywords = keyword_data.get("context_keywords", [])
                    context_score = self.context_analyzer.analyze(
                        text, context_keywords
                    )

            # Check threshold
            min_context = self.config.get("ai.min_context_confidence", 0.6)
            if context_score < min_context and context_score > 0:
                logger.info(f"Context score below threshold: {context_score}")
                return

            # Play sound
            keyword_data = self.config.get_keyword(keyword_id)
            if keyword_data:
                sound_id = keyword_data.get("sound_id")
                if sound_id:
                    self.sound_manager.play_sound(sound_id)
                    self.last_detected_keyword = keyword_id

            # Log detection
            self.database.add_detection(
                text=text,
                keyword_matched=keyword_id,
                confidence=confidence,
                context_score=context_score,
                sound_played=keyword_data.get("sound_id") if keyword_data else None,
            )

            # Notify callbacks
            for callback in self._detection_callbacks:
                try:
                    callback(keyword_id, text, confidence, context_score)
                except Exception as e:
                    logger.error(f"Error in detection callback: {e}")

        except Exception as e:
            logger.error(f"Error detecting keywords: {e}")

    def _event_loop(self) -> None:
        """Process events from queue."""
        while self.is_running:
            try:
                event = self.event_queue.get(timeout=1.0)
                logger.debug(f"Processing event: {event}")
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in event loop: {e}")

    def register_transcription_callback(self, callback: Callable) -> None:
        """Register callback for transcriptions."""
        with self._callback_lock:
            self._transcription_callbacks.append(callback)

    def register_detection_callback(self, callback: Callable) -> None:
        """Register callback for detections."""
        with self._callback_lock:
            self._detection_callbacks.append(callback)

    def register_status_callback(self, callback: Callable) -> None:
        """Register callback for status updates."""
        with self._callback_lock:
            self._status_callbacks.append(callback)

    def register_audio_level_callback(self, callback: Callable) -> None:
        """Register callback for audio level updates."""
        with self._callback_lock:
            self._audio_level_callbacks.append(callback)

    def _notify_status(self) -> None:
        """Notify status callbacks."""
        status = {
            "is_running": self.is_running,
            "is_capturing": self.is_capturing,
            "timestamp": datetime.now().isoformat(),
        }
        with self._callback_lock:
            for callback in self._status_callbacks:
                try:
                    callback(status)
                except Exception as e:
                    logger.error(f"Error in status callback: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        with self._state_lock:
            # Informações básicas do Whisper
            whisper_info = {}
            if self.transcriber:
                if hasattr(self.transcriber, 'transcriber'):
                    # TranscriberThread
                    whisper_info = {
                        "whisper_available": True,
                        "whisper_running": self.transcriber.is_running,
                        "whisper_model": getattr(self.transcriber.transcriber, 'model_name', 'base'),
                        "whisper_device": getattr(self.transcriber.transcriber, 'device', 'cpu'),
                        "whisper_language": getattr(self.transcriber.transcriber, 'language', 'pt'),
                    }
                else:
                    whisper_info = {
                        "whisper_available": True,
                        "whisper_running": True,
                        "whisper_model": getattr(self.transcriber, 'model_name', 'base'),
                        "whisper_device": getattr(self.transcriber, 'device', 'cpu'),
                        "whisper_language": getattr(self.transcriber, 'language', 'pt'),
                    }
            else:
                whisper_info = {
                    "whisper_available": False,
                    "whisper_running": False,
                    "whisper_model": None,
                    "whisper_device": None,
                    "whisper_language": None,
                }
            
            return {
                "is_running": self.is_running,
                "is_capturing": self.is_capturing,
                "current_transcript": self.current_transcript,
                "last_detected_keyword": self.last_detected_keyword,
                "audio_queue_size": (
                    self.audio_processor.get_queue_size()
                    if self.audio_processor
                    else 0
                ),
                "timestamp": datetime.now().isoformat(),
                **whisper_info,
            }

    def reload_config(self) -> None:
        """Reload configuration from file."""
        try:
            self.config.load_config()
            self.keyword_detector.update_keywords(self.config.get_keywords())
            self.sound_manager.update_sounds_config(self.config.get_sounds())
            logger.info("Configuration reloaded")
        except Exception as e:
            logger.error(f"Error reloading config: {e}")

    def set_input_device(self, device_id: int, persist: bool = True) -> None:
        """
        Safely change the audio input device.

        Ensures config is updated and restarts the analyzer if necessary in a thread-safe manner.

        Args:
            device_id: device index (int)
            persist: whether to persist into config
        """
        try:
            logger.info(f"Requested set_input_device: {device_id}")

            # Determine current device (check both keys for backwards compatibility)
            current_cfg_device = self.config.get("audio.device_id", None)
            current_input_device = self.config.get("audio.input_device", None)
            current_processor_device = (
                self.audio_processor.device_id if self.audio_processor else None
            )

            # Prefer processor value if available, then device_id, then input_device
            current_device = (
                current_processor_device
                if current_processor_device is not None
                else current_cfg_device
                if current_cfg_device is not None
                else current_input_device
            )

            # If value is the same, just persist config and return (no restart)
            if current_device == device_id:
                logger.info(f"Input device unchanged (already {device_id}) - updating config only")
                self.config.set("audio.device_id", device_id, persist=persist)
                self.config.set("audio.input_device", device_id, persist=persist)
                return

            # Update config keys consistently
            self.config.set("audio.device_id", device_id, persist=persist)
            self.config.set("audio.input_device", device_id, persist=persist)

            # If analyzer running, perform ordered restart to change device safely
            with self._state_lock:
                was_running = self.is_running

            if was_running:
                try:
                    logger.info("Changing device: performing stop -> set -> start sequence")
                    # Prevent concurrent device changes
                    with self._device_change_lock:
                        # Stop analyzer (this will stop audio processor and transcriber)
                        self.stop()

                    # Apply device to audio processor
                    if self.audio_processor:
                        try:
                            self.audio_processor.set_device(device_id)
                        except Exception as e:
                            logger.error(f"Failed to apply device to audio_processor: {e}")

                        # Restart analyzer
                        self.start()

                except Exception as e:
                    logger.error(f"Error while changing input device: {e}")
            else:
                # Not running - set device on processor if exists
                if self.audio_processor:
                    try:
                        self.audio_processor.set_device(device_id)
                    except Exception as e:
                        logger.error(f"Failed to set device when analyzer not running: {e}")

        except Exception as e:
            logger.error(f"set_input_device failed: {e}")

    def get_devices(self) -> list:
        """Get list of available audio devices."""
        try:
            # Se audio_processor já existe, usar dele
            if self.audio_processor:
                return self.audio_processor.list_devices()
            
            # Caso contrário, criar um temporário só para listar dispositivos
            temp_processor = AudioProcessor()
            devices = temp_processor.list_devices()
            # Limpar recursos temporários
            if hasattr(temp_processor, 'pa') and temp_processor.pa:
                temp_processor.pa.terminate()
            return devices
        except Exception as e:
            logger.warning(f"Error getting audio devices: {e}")
            return []
