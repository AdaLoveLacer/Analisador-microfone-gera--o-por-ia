"""Audio processor for real-time microphone capture."""

import pyaudio
import numpy as np
import threading
import queue
import logging
from typing import Optional, Callable, List
from utils.exceptions import AudioDeviceException, AudioCaptureException
from .audio_utils import detect_silence, get_audio_energy, convert_bytes_to_numpy

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Captures audio from microphone in real-time."""

    def __init__(
        self,
        device_id: int = -1,
        sample_rate: int = 16000,
        chunk_size: int = 2048,
        channels: int = 1,
        silence_threshold: float = 0.02,
    ):
        """
        Initialize AudioProcessor.

        Args:
            device_id: Audio device ID (-1 for default)
            sample_rate: Sample rate in Hz
            chunk_size: Chunk size in samples
            channels: Number of audio channels
            silence_threshold: Silence detection threshold
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.silence_threshold = silence_threshold

        self.pa = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.is_recording = False
        self.audio_queue: queue.Queue = queue.Queue(maxsize=100)
        
        # Lock para proteger acesso ao stream de áudio (evita race conditions)
        self._stream_lock = threading.Lock()
        self._capture_thread: Optional[threading.Thread] = None

        self._validate_device()

    def _validate_device(self) -> None:
        """Validate that audio device is available."""
        try:
            if self.device_id == -1:
                # Use default device
                return

            info = self.pa.get_device_info_by_index(self.device_id)
            if not info:
                raise AudioDeviceException(f"Audio device {self.device_id} not found")

            if info["maxInputChannels"] < self.channels:
                raise AudioDeviceException(
                    f"Device {self.device_id} doesn't support {self.channels} channels"
                )
        except Exception as e:
            raise AudioDeviceException(f"Failed to validate audio device: {e}")

    def list_devices(self) -> List[dict]:
        """List available audio devices."""
        devices = []
        try:
            default_input_device = self.pa.get_default_input_device_info()["index"]
        except Exception:
            default_input_device = None
            
        for i in range(self.pa.get_device_count()):
            try:
                info = self.pa.get_device_info_by_index(i)
                devices.append(
                    {
                        "index": i,
                        "name": info["name"],
                        "max_input_channels": info["maxInputChannels"],
                        "max_output_channels": info["maxOutputChannels"],
                        "default_input": i == default_input_device,
                    }
                )
            except Exception as e:
                logger.warning(f"Error listing device {i}: {e}")
        return devices

    def start(self) -> None:
        """Start audio capture."""
        try:
            if self.is_recording:
                logger.warning("Recording already in progress")
                return

            # Log tentativa de abertura
            logger.info(f"Attempting to open audio stream (device={self.device_id}, sr={self.sample_rate})")
            
            # Tentar abrir o device
            try:
                self.stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.device_id if self.device_id != -1 else None,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=None,  # We'll use blocking mode
                )
            except Exception as e:
                logger.error(f"Failed to open audio stream with device {self.device_id}: {e}")
                logger.warning("Falling back to default audio device")
                # Tentar com device padrão
                self.device_id = -1
                self.stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=None,  # Use default
                    frames_per_buffer=self.chunk_size,
                    stream_callback=None,
                )

            self.is_recording = True
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._capture_thread.start()

            # CORREÇÃO: Aguardar um pouco para a fila começar a ser preenchida
            # Evita o timeout inicial no primeiro get_chunk()
            import time
            time.sleep(0.1)

            logger.info(f"Audio capture started (device={self.device_id}, sr={self.sample_rate})")
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            raise AudioCaptureException(f"Failed to start audio capture: {e}")

    def stop(self) -> None:
        """Stop audio capture."""
        try:
            self.is_recording = False
            
            # Aguardar thread de captura terminar
            if self._capture_thread and self._capture_thread.is_alive():
                self._capture_thread.join(timeout=2.0)

            with self._stream_lock:
                if self.stream:
                    try:
                        self.stream.stop_stream()
                        self.stream.close()
                    except Exception as e:
                        logger.warning(f"Error closing stream: {e}")
                    finally:
                        self.stream = None

            logger.info("Audio capture stopped")
        except Exception as e:
            logger.error(f"Error stopping audio capture: {e}")
            raise AudioCaptureException(f"Error stopping audio capture: {e}")

    def _capture_loop(self) -> None:
        """Main audio capture loop."""
        import time
        try:
            logger.info(f"Audio capture loop started. Device: {self.device_id}, SR: {self.sample_rate}")
            error_count = 0
            max_errors = 10
            consecutive_errors = 0
            
            while self.is_recording:
                try:
                    # Verificar se o stream ainda é válido
                    with self._stream_lock:
                        if not self.stream or not self.is_recording:
                            break
                        
                        # Read audio chunk com proteção
                        try:
                            audio_bytes = self.stream.read(self.chunk_size, exception_on_overflow=False)
                        except OSError as e:
                            # Stream foi fechado ou dispositivo desconectado
                            logger.error(f"Stream read OSError: {e}")
                            break
                    
                    if not audio_bytes or len(audio_bytes) == 0:
                        logger.warning("Empty audio bytes received from stream")
                        consecutive_errors += 1
                        if consecutive_errors > max_errors:
                            logger.error(f"Too many empty reads ({consecutive_errors}), stopping capture")
                            break
                        time.sleep(0.01)  # Pequena pausa antes de tentar novamente
                        continue
                    
                    audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
                    
                    # Reset error count on successful read
                    consecutive_errors = 0

                    # Check if queue is full
                    if self.audio_queue.full():
                        try:
                            self.audio_queue.get_nowait()  # Discard oldest
                        except queue.Empty:
                            pass

                    # Add to queue (non-blocking para evitar deadlock)
                    try:
                        self.audio_queue.put_nowait(audio_data)
                    except queue.Full:
                        pass  # Ignorar se a fila estiver cheia

                except IOError as e:
                    # Erro de I/O no stream de áudio - provavelmente dispositivo desconectado
                    logger.error(f"Audio I/O error: {e}")
                    break
                    
                except Exception as e:
                    consecutive_errors += 1
                    error_count += 1
                    
                    # Avoid spamming the logs every single error; escalate severity
                    if consecutive_errors <= 3:
                        logger.warning(f"Error in capture loop (attempt {consecutive_errors}): {e}")
                    elif consecutive_errors < max_errors:
                        logger.error(f"Error in capture loop (attempt {consecutive_errors}): {e}")
                    else:
                        logger.error(f"Too many capture errors ({consecutive_errors}), stopping: {e}")
                        break

                    # Exponential backoff to avoid tight restart cycles
                    backoff = min(2 ** consecutive_errors, 30)
                    time.sleep(backoff * 0.1)
                    
        except Exception as e:
            logger.error(f"Capture loop failed: {e}")
        finally:
            self.is_recording = False
            logger.info("Audio capture loop ended")

    def get_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get audio chunk from queue.

        Args:
            timeout: Timeout in seconds

        Returns:
            Audio data as numpy array or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_energy(self) -> float:
        """Get current audio energy level."""
        try:
            # Peek at queue without removing
            chunk = self.audio_queue.get(timeout=0.1)
            energy = get_audio_energy(chunk)
            self.audio_queue.put(chunk)  # Put it back
            return energy
        except queue.Empty:
            return 0.0

    def is_silent(self) -> bool:
        """Check if current audio is silent."""
        try:
            chunk = self.audio_queue.get(timeout=0.1)
            is_silent, _ = detect_silence(chunk, self.sample_rate, self.silence_threshold)
            self.audio_queue.put(chunk)
            return is_silent
        except queue.Empty:
            return True

    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self.audio_queue.qsize()

    def clear_queue(self) -> None:
        """Clear audio queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def set_device(self, device_id: int) -> None:
        """Change audio input device.
        
        Args:
            device_id: New device ID
        """
        was_recording = self.is_recording
        if was_recording:
            self.stop()
        
        self.device_id = device_id
        self._validate_device()
        
        if was_recording:
            self.start()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.stop()
            if self.pa:
                self.pa.terminate()
        except Exception:
            pass
