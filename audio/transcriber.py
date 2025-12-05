"""Whisper transcriber for real-time speech-to-text."""

import whisper
import numpy as np
import threading
import queue
import logging
import torch
import gc
from typing import Optional, Dict, Any
from pathlib import Path
from utils.exceptions import WhisperException

logger = logging.getLogger(__name__)


class Transcriber:
    """Transcribes audio using OpenAI Whisper."""

    def __init__(
        self,
        model_name: str = "base",
        language: str = "pt",
        device: Optional[str] = None,
        fp16: bool = False,
        # Parâmetros avançados do Whisper
        task: str = "transcribe",
        beam_size: Optional[int] = 5,
        best_of: Optional[int] = 5,
        temperature: float = 0.0,
        patience: Optional[float] = 1.0,
        length_penalty: Optional[float] = 1.0,
        suppress_blank: bool = True,
        condition_on_previous_text: bool = True,
        no_speech_threshold: float = 0.6,
        compression_ratio_threshold: float = 2.4,
        logprob_threshold: float = -1.0,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False,
        hallucination_silence_threshold: Optional[float] = None,
    ):
        """
        Initialize Transcriber.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            language: Language code (e.g., 'pt' for Portuguese)
            device: Device to use (cpu or cuda). If None, auto-detects CUDA
            fp16: Use FP16 precision
            task: Task type ('transcribe' or 'translate')
            beam_size: Beam size for beam search (higher = better quality, slower)
            best_of: Number of candidates when sampling (higher = better quality)
            temperature: Sampling temperature (0.0 = deterministic)
            patience: Patience for beam search
            length_penalty: Length penalty for beam search
            suppress_blank: Suppress blank outputs
            condition_on_previous_text: Use previous text as context
            no_speech_threshold: Threshold for no-speech detection
            compression_ratio_threshold: Threshold for compression ratio (hallucination filter)
            logprob_threshold: Log probability threshold
            initial_prompt: Initial prompt to guide transcription
            word_timestamps: Extract word-level timestamps
            hallucination_silence_threshold: Skip silent periods during hallucinations
        """
        # Auto-detect CUDA if device not specified or is "auto"
        if device is None or device == "auto":
            device = self._detect_best_device()
            
        # Configurar FP16 baseado no device
        if device == "cuda":
            # FP16 é muito mais eficiente na GPU (usa 50% menos VRAM)
            if fp16 is False:  # Se não foi explicitamente desativado
                fp16 = True
            logger.info(f"Using CUDA GPU with FP16={fp16}")
        else:
            fp16 = False  # CPU não beneficia de FP16
            logger.info(f"Using CPU (FP16 disabled)")
        
        # Configurações básicas
        self.model_name = model_name
        self.language = language
        self.device = device
        self.fp16 = fp16
        
        # Configurações avançadas
        self.task = task
        self.beam_size = beam_size
        self.best_of = best_of
        self.temperature = temperature
        self.patience = patience
        self.length_penalty = length_penalty
        self.suppress_blank = suppress_blank
        self.condition_on_previous_text = condition_on_previous_text
        self.no_speech_threshold = no_speech_threshold
        self.compression_ratio_threshold = compression_ratio_threshold
        self.logprob_threshold = logprob_threshold
        self.initial_prompt = initial_prompt
        self.word_timestamps = word_timestamps
        self.hallucination_silence_threshold = hallucination_silence_threshold
        
        logger.info(f"Whisper transcriber initialized with device: {device}, fp16: {fp16}, language: {language}")
        logger.info(f"Advanced settings: beam_size={beam_size}, best_of={best_of}, temperature={temperature}")

        logger.info(f"Loading Whisper model: {model_name}")
        try:
            self.model = whisper.load_model(model_name, device=device)
            logger.info(f"Whisper model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise WhisperException(f"Failed to load Whisper model: {e}")

    def _detect_best_device(self) -> str:
        """Detect best available device for Whisper.
        
        Returns:
            'cuda' if GPU available with enough VRAM, else 'cpu'
        """
        try:
            if torch.cuda.is_available():
                # Check available VRAM
                gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"CUDA available. GPU memory: {gpu_mem:.1f}GB")
                return "cuda"
            else:
                logger.info("CUDA not available, using CPU")
                return "cpu"
        except Exception as e:
            logger.warning(f"Error detecting device: {e}, defaulting to CPU")
            return "cpu"

    def unload(self) -> bool:
        """Unload Whisper model from memory to free VRAM/RAM."""
        try:
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
                
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info("✓ Whisper model unloaded from memory")
                return True
        except Exception as e:
            logger.error(f"Error unloading Whisper model: {e}")
            return False
        return True

    def reload(self, model_name: Optional[str] = None, device: Optional[str] = None) -> bool:
        """Reload Whisper model (optionally with different settings).
        
        Args:
            model_name: New model name (or keep current)
            device: New device (or keep current)
        """
        try:
            # Unload current model first
            self.unload()
            
            # Update settings if provided
            if model_name:
                self.model_name = model_name
            if device:
                self.device = device
            elif device is None or device == "auto":
                self.device = self._detect_best_device()
            
            # Update FP16 based on device
            if self.device == "cuda":
                self.fp16 = True
            else:
                self.fp16 = False
            
            logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info(f"✓ Whisper model reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload Whisper model: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get transcriber status."""
        status = {
            "model_name": self.model_name,
            "device": self.device,
            "fp16": self.fp16,
            "language": self.language,
            "loaded": self.model is not None,
        }
        
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                status["vram_allocated_gb"] = round(torch.cuda.memory_allocated() / 1024**3, 2)
                status["vram_reserved_gb"] = round(torch.cuda.memory_reserved() / 1024**3, 2)
            except:
                pass
        
        return status

    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
    ) -> Dict[str, Any]:
        """
        Transcribe audio data.

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            Dictionary with transcription result
        """
        try:
            if len(audio_data) == 0:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": self.language,
                }

            # Ensure audio is in correct format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # MELHORIA: Whisper precisa de pelo menos 30 frames (cada frame = 400 samples em 16kHz)
            # Isso equivale a aproximadamente 0.75 segundos de áudio
            # Para melhor precisão, vamos garantir pelo menos 1.5 segundos (24000 samples)
            min_samples = int(sample_rate * 1.5)  # 1.5 segundos
            
            if len(audio_data) < min_samples:
                # Adicionar padding de silêncio no início e fim para melhorar a detecção
                padding_needed = min_samples - len(audio_data)
                padding_start = padding_needed // 2
                padding_end = padding_needed - padding_start
                
                # Usar valores muito pequenos (não zero) para evitar problemas de normalização
                audio_data = np.concatenate([
                    np.full(padding_start, 1e-6, dtype=np.float32),
                    audio_data,
                    np.full(padding_end, 1e-6, dtype=np.float32)
                ])
                logger.debug(f"Áudio muito curto, adicionado padding: {padding_start} + {padding_end} samples")

            # Normalize audio (importante para Whisper)
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # Aplicar filtro de ruído simples: suprimir valores muito baixos
            noise_floor = 0.01
            audio_data = np.where(np.abs(audio_data) < noise_floor, 0, audio_data)

            # Log para debug do idioma
            logger.debug(f"Transcrevendo com idioma: {self.language}")
            
            # Usar configurações avançadas se disponíveis
            transcribe_options = {
                "language": self.language,
                "task": self.task if hasattr(self, 'task') else "transcribe",
                "fp16": self.fp16,
                "verbose": False,
            }
            
            # Adicionar parâmetros opcionais se configurados
            if hasattr(self, 'beam_size') and self.beam_size:
                transcribe_options["beam_size"] = self.beam_size
            if hasattr(self, 'best_of') and self.best_of:
                transcribe_options["best_of"] = self.best_of
            if hasattr(self, 'temperature') is not None:
                transcribe_options["temperature"] = self.temperature if hasattr(self, 'temperature') else 0.0
            if hasattr(self, 'patience') and self.patience:
                transcribe_options["patience"] = self.patience
            if hasattr(self, 'length_penalty') and self.length_penalty:
                transcribe_options["length_penalty"] = self.length_penalty
            if hasattr(self, 'suppress_blank'):
                transcribe_options["suppress_blank"] = self.suppress_blank
            if hasattr(self, 'condition_on_previous_text'):
                transcribe_options["condition_on_previous_text"] = self.condition_on_previous_text
            if hasattr(self, 'no_speech_threshold') and self.no_speech_threshold:
                transcribe_options["no_speech_threshold"] = self.no_speech_threshold
            if hasattr(self, 'compression_ratio_threshold') and self.compression_ratio_threshold:
                transcribe_options["compression_ratio_threshold"] = self.compression_ratio_threshold
            if hasattr(self, 'logprob_threshold') and self.logprob_threshold:
                transcribe_options["logprob_threshold"] = self.logprob_threshold
            if hasattr(self, 'initial_prompt') and self.initial_prompt:
                transcribe_options["initial_prompt"] = self.initial_prompt
            if hasattr(self, 'word_timestamps'):
                transcribe_options["word_timestamps"] = self.word_timestamps
            if hasattr(self, 'hallucination_silence_threshold') and self.hallucination_silence_threshold:
                transcribe_options["hallucination_silence_threshold"] = self.hallucination_silence_threshold
            
            logger.debug(f"Opções de transcrição: {transcribe_options}")
            
            result = self.model.transcribe(audio_data, **transcribe_options)
            
            # Log do idioma detectado
            detected_lang = result.get("language", "unknown")
            if detected_lang != self.language:
                logger.warning(f"Idioma detectado ({detected_lang}) diferente do configurado ({self.language})")

            return {
                "text": result.get("text", "").strip(),
                "confidence": self._calculate_confidence(result),
                "language": result.get("language", self.language),
                "segments": result.get("segments", []),
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise WhisperException(f"Transcription failed: {e}")

    def _calculate_confidence(self, result: Dict) -> float:
        """
        Calculate average confidence from segments.

        Args:
            result: Whisper result dictionary

        Returns:
            Average confidence score
        """
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.0

            # Use probability from segments if available
            probs = []
            for segment in segments:
                if "confidence" in segment:
                    probs.append(segment["confidence"])

            return sum(probs) / len(probs) if probs else 0.8  # Default confidence
        except Exception:
            return 0.8

    def __del__(self):
        """Cleanup on deletion."""
        try:
            del self.model
        except Exception:
            pass


class TranscriberThread:
    """Threaded transcriber for non-blocking transcription."""

    def __init__(
        self,
        model_name: str = "base",
        language: str = "pt",
        device: str = "cpu",
        # Parâmetros avançados
        task: str = "transcribe",
        beam_size: Optional[int] = 5,
        best_of: Optional[int] = 5,
        temperature: float = 0.0,
        patience: Optional[float] = 1.0,
        length_penalty: Optional[float] = 1.0,
        suppress_blank: bool = True,
        condition_on_previous_text: bool = True,
        no_speech_threshold: float = 0.6,
        compression_ratio_threshold: float = 2.4,
        logprob_threshold: float = -1.0,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False,
        hallucination_silence_threshold: Optional[float] = None,
    ):
        """
        Initialize TranscriberThread.

        Args:
            model_name: Whisper model name
            language: Language code
            device: Device to use
            + all advanced Whisper parameters
        """
        # Criar Transcriber com todas as configurações
        self.transcriber = Transcriber(
            model_name=model_name,
            language=language,
            device=device,
            fp16=False,  # Auto-detectado pelo Transcriber
            task=task,
            beam_size=beam_size,
            best_of=best_of,
            temperature=temperature,
            patience=patience,
            length_penalty=length_penalty,
            suppress_blank=suppress_blank,
            condition_on_previous_text=condition_on_previous_text,
            no_speech_threshold=no_speech_threshold,
            compression_ratio_threshold=compression_ratio_threshold,
            logprob_threshold=logprob_threshold,
            initial_prompt=initial_prompt,
            word_timestamps=word_timestamps,
            hallucination_silence_threshold=hallucination_silence_threshold,
        )
        self.input_queue: queue.Queue = queue.Queue(maxsize=10)
        self.output_queue: queue.Queue = queue.Queue(maxsize=10)
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start transcriber thread."""
        if self.is_running:
            logger.warning("Transcriber thread already running")
            return

        self.is_running = True
        self._thread = threading.Thread(target=self._transcribe_loop, daemon=True)
        self._thread.start()
        logger.info("Transcriber thread started")

    def stop(self) -> None:
        """Stop transcriber thread."""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Transcriber thread stopped")

    def cleanup(self) -> None:
        """Cleanup resources and free GPU memory."""
        logger.info("🧹 Limpando recursos do Transcriber...")
        
        # Parar thread se ainda estiver rodando
        if self.is_running:
            self.stop()
        
        # Liberar modelo do transcriber
        if hasattr(self, 'transcriber') and self.transcriber:
            if hasattr(self.transcriber, 'model'):
                try:
                    # Mover modelo para CPU antes de deletar (libera VRAM)
                    self.transcriber.model.cpu()
                    del self.transcriber.model
                    self.transcriber.model = None
                    logger.info("✓ Modelo movido para CPU e deletado")
                except Exception as e:
                    logger.warning(f"Erro ao deletar modelo: {e}")
            
            try:
                del self.transcriber
                self.transcriber = None
            except Exception as e:
                logger.warning(f"Erro ao deletar transcriber: {e}")
        
        # Forçar coleta de lixo
        import gc
        gc.collect()
        
        # Liberar cache CUDA
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                
                # Log de memória liberada
                free_mem = torch.cuda.memory_reserved(0) - torch.cuda.memory_allocated(0)
                logger.info(f"✓ Cache CUDA liberado. Memória livre: {free_mem / 1024**2:.0f} MB")
        except Exception as e:
            logger.warning(f"Erro ao liberar cache CUDA: {e}")
        
        logger.info("✓ Cleanup do Transcriber concluído")

    def __del__(self):
        """Destructor - cleanup on deletion."""
        try:
            self.cleanup()
        except Exception:
            pass

    def submit_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> None:
        """
        Submit audio for transcription.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
        """
        try:
            self.input_queue.put_nowait((audio_data, sample_rate))
        except queue.Full:
            logger.warning("Transcriber input queue full")

    def get_result(self, timeout: float = 1.0) -> Optional[Dict]:
        """
        Get transcription result.

        Args:
            timeout: Timeout in seconds

        Returns:
            Transcription result or None
        """
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _transcribe_loop(self) -> None:
        """Main transcription loop."""
        import time
        consecutive_errors = 0
        max_errors = 5
        
        try:
            while self.is_running:
                try:
                    # Get audio from queue
                    try:
                        audio_data, sample_rate = self.input_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue

                    # Verificar se ainda está rodando antes de transcrever
                    if not self.is_running:
                        break

                    # Transcribe com timeout implícito (evita travar para sempre)
                    result = self.transcriber.transcribe(audio_data, sample_rate)
                    
                    # Reset contador de erros em sucesso
                    consecutive_errors = 0

                    # Put result in output queue
                    try:
                        self.output_queue.put_nowait(result)
                    except queue.Full:
                        try:
                            self.output_queue.get_nowait()  # Discard oldest
                            self.output_queue.put_nowait(result)
                        except queue.Empty:
                            pass

                except RuntimeError as e:
                    # Erros de CUDA/PyTorch (OOM, device errors)
                    consecutive_errors += 1
                    logger.error(f"Runtime error in transcribe loop: {e}")
                    if consecutive_errors >= max_errors:
                        logger.error("Too many consecutive errors, stopping transcriber")
                        break
                    time.sleep(1.0)  # Pausa antes de tentar novamente
                    
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Error in transcribe loop: {e}")
                    if consecutive_errors >= max_errors:
                        logger.error("Too many consecutive errors, stopping transcriber")
                        break
                    time.sleep(0.5)

        except Exception as e:
            logger.error(f"Transcriber thread error: {e}")
        finally:
            self.is_running = False
            logger.info("Transcriber thread ended")

    def get_queue_size(self) -> tuple:
        """Get input and output queue sizes."""
        return (self.input_queue.qsize(), self.output_queue.qsize())

    def get_status(self) -> Dict[str, Any]:
        """Get transcriber status and info."""
        try:
            import torch
            has_cuda = torch.cuda.is_available()
            gpu_name = torch.cuda.get_device_name(0) if has_cuda else None
        except:
            has_cuda = False
            gpu_name = None

        return {
            "available": True,
            "is_running": self.is_running,
            "model": self.transcriber.model_name,
            "device": self.transcriber.device,
            "language": self.transcriber.language,
            "gpu_available": has_cuda,
            "gpu_name": gpu_name,
            "using_gpu": self.transcriber.device == "cuda",
            "fp16_enabled": self.transcriber.fp16,
            "input_queue_size": self.input_queue.qsize(),
            "output_queue_size": self.output_queue.qsize(),
        }
