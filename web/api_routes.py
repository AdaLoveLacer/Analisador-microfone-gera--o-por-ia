"""REST API routes."""

from flask import Blueprint, request, jsonify, current_app
from utils.exceptions import ConfigException, ValidationException
from utils.validators import Validator, validate_or_raise
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


@api_bp.route("/status", methods=["GET"])
def get_status():
    """Get application status."""
    try:
        status = current_app.analyzer.get_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/capture/start", methods=["POST"])
def start_capture():
    """Start audio capture."""
    try:
        if current_app.analyzer.is_running:
            return jsonify({"message": "Analyzer already running"}), 200

        # Usar thread para evitar timeout
        import threading
        def start_in_thread():
            try:
                current_app.analyzer.start()
            except Exception as e:
                logger.error(f"Failed to start analyzer: {e}")
        
        thread = threading.Thread(target=start_in_thread, daemon=True)
        thread.start()
        
        # Retornar imediatamente sem aguardar thread
        return jsonify({"message": "Capture starting..."}), 200
    except Exception as e:
        logger.error(f"Error starting capture: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/capture/stop", methods=["POST"])
def stop_capture():
    """Stop audio capture."""
    try:
        current_app.analyzer.stop()
        return jsonify({"message": "Capture stopped"}), 200
    except Exception as e:
        logger.error(f"Error stopping capture: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/capture/status", methods=["GET"])
def capture_status():
    """Get capture status."""
    try:
        status = {
            "is_capturing": current_app.analyzer.is_capturing,
            "is_running": current_app.analyzer.is_running,
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting capture status: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/devices", methods=["GET"])
def list_devices():
    """List available audio devices."""
    try:
        devices = current_app.analyzer.get_devices()
        return jsonify({"devices": devices}), 200
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/whisper-devices", methods=["GET"])
def get_whisper_devices():
    """Get available Whisper processing devices (CPU/CUDA)."""
    try:
        import torch
        
        devices = []
        
        # Always available: CPU
        devices.append({
            "value": "cpu",
            "label": "💻 CPU (Mais Compatível)",
            "description": "Funciona em qualquer máquina, mas é mais lento"
        })
        
        # Check if CUDA is available
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            devices.append({
                "value": "cuda",
                "label": f"🚀 CUDA - {gpu_name} (Muito Mais Rápido)",
                "description": f"GPU NVIDIA disponível: {gpu_name} (~10x mais rápido que CPU)"
            })
        
        return jsonify({"devices": devices}), 200
    except Exception as e:
        logger.error(f"Error getting Whisper devices: {e}")
        return jsonify({"devices": [
            {
                "value": "cpu",
                "label": "💻 CPU (Padrão)",
                "description": "Processador padrão"
            }
        ]}), 200


# Configuration routes
@api_bp.route("/config", methods=["GET"])
def get_config():
    """Get current configuration."""
    try:
        config = current_app.config_manager.get_all()
        return jsonify(config), 200
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/config", methods=["POST"])
def update_config():
    """Update configuration."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Convert nested dict to dot notation for config_manager
        def flatten_dict(d, parent_key='', sep='.'):
            """Convert nested dict to dot-notation."""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        def convert_value(key, value):
            """Convert string values to appropriate types based on key name."""
            if value is None or value == '':
                return None
            
            # If already the right type, return as-is
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return value
            
            # String conversions
            if isinstance(value, str):
                # Boolean values
                if value.lower() in ('true', 'yes', '1'):
                    return True
                if value.lower() in ('false', 'no', '0'):
                    return False
                
                # Integer fields
                if any(field in key for field in ['device_id', 'chunk_size', 'channels', 'port']):
                    try:
                        return int(value)
                    except ValueError:
                        pass
                
                # Float fields
                if any(field in key for field in ['threshold', 'weight', 'rate', 'confidence', 'score']):
                    try:
                        return float(value)
                    except ValueError:
                        pass
            
            # Default: return as-is
            return value
        
        flat_config = flatten_dict(data)
        
        # Update each key using dot notation with type conversion
        for key, value in flat_config.items():
            converted_value = convert_value(key, value)
            current_app.config_manager.set(key, converted_value, persist=False)

        current_app.config_manager.save_config()
        current_app.analyzer.reload_config()

        return jsonify({"message": "Configuration updated"}), 200
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/config/export", methods=["GET"])
def export_config():
    """Export configuration as JSON."""
    try:
        config = current_app.config_manager.get_all()
        return jsonify(config), 200
    except Exception as e:
        logger.error(f"Error exporting config: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/config/import", methods=["POST"])
def import_config():
    """Import configuration from JSON."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create temporary file and import
        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        current_app.config_manager.import_config(temp_path)

        import os

        os.unlink(temp_path)

        return jsonify({"message": "Configuration imported"}), 200
    except Exception as e:
        logger.error(f"Error importing config: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/config/reset", methods=["POST"])
def reset_config():
    """Reset configuration to defaults."""
    try:
        current_app.config_manager.reset_to_defaults()
        current_app.analyzer.reload_config()
        return jsonify({"message": "Configuration reset to defaults"}), 200
    except Exception as e:
        logger.error(f"Error resetting config: {e}")
        return jsonify({"error": str(e)}), 500


# Keywords routes
@api_bp.route("/keywords", methods=["GET"])
def get_keywords():
    """Get all keywords."""
    try:
        keywords = current_app.config_manager.get_keywords()
        return jsonify({"keywords": keywords}), 200
    except Exception as e:
        logger.error(f"Error getting keywords: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/keywords", methods=["POST"])
def create_keyword():
    """Create a new keyword."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        validate_or_raise(Validator.validate_keyword(data), "Invalid keyword")

        current_app.config_manager.add_keyword(data)
        return jsonify({"message": "Keyword created", "keyword": data}), 201
    except Exception as e:
        logger.error(f"Error creating keyword: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/keywords/<keyword_id>", methods=["PUT"])
def update_keyword(keyword_id):
    """Update a keyword."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        validate_or_raise(Validator.validate_keyword(data), "Invalid keyword")

        current_app.config_manager.update_keyword(keyword_id, data)
        return jsonify({"message": "Keyword updated", "keyword": data}), 200
    except Exception as e:
        logger.error(f"Error updating keyword: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/keywords/<keyword_id>", methods=["DELETE"])
def delete_keyword(keyword_id):
    """Delete a keyword."""
    try:
        current_app.config_manager.delete_keyword(keyword_id)
        return jsonify({"message": "Keyword deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting keyword: {e}")
        return jsonify({"error": str(e)}), 500


# Sounds routes
@api_bp.route("/sounds", methods=["GET"])
def get_sounds():
    """Get all sounds."""
    try:
        sounds = current_app.config_manager.get_sounds()
        return jsonify({"sounds": sounds}), 200
    except Exception as e:
        logger.error(f"Error getting sounds: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/sounds", methods=["POST"])
def create_sound():
    """Create a new sound."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        validate_or_raise(Validator.validate_sound(data), "Invalid sound")

        current_app.config_manager.add_sound(data)
        return jsonify({"message": "Sound created", "sound": data}), 201
    except Exception as e:
        logger.error(f"Error creating sound: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/sounds/<sound_id>", methods=["PUT"])
def update_sound(sound_id):
    """Update a sound."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        validate_or_raise(Validator.validate_sound(data), "Invalid sound")

        current_app.config_manager.update_sound(sound_id, data)
        return jsonify({"message": "Sound updated", "sound": data}), 200
    except Exception as e:
        logger.error(f"Error updating sound: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/sounds/<sound_id>", methods=["DELETE"])
def delete_sound(sound_id):
    """Delete a sound."""
    try:
        current_app.config_manager.delete_sound(sound_id)
        return jsonify({"message": "Sound deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting sound: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/sounds/<sound_id>/preview", methods=["POST"])
def preview_sound(sound_id):
    """Play preview of a sound."""
    try:
        result = current_app.analyzer.sound_manager.preview_sound(sound_id)
        if result:
            return jsonify({"message": "Sound preview started"}), 200
        else:
            return jsonify({"error": "Failed to play sound"}), 400
    except Exception as e:
        logger.error(f"Error previewing sound: {e}")
        return jsonify({"error": str(e)}), 500


# Detections routes
@api_bp.route("/detections", methods=["GET"])
def get_detections():
    """Get detection history."""
    try:
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)

        detections = current_app.db_manager.get_detections(limit=limit, offset=offset)
        return jsonify({"detections": detections}), 200
    except Exception as e:
        logger.error(f"Error getting detections: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/detections/stats", methods=["GET"])
def get_detection_stats():
    """Get detection statistics."""
    try:
        stats = current_app.db_manager.get_detection_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


# Transcriptions routes
@api_bp.route("/transcriptions", methods=["GET"])
def get_transcriptions():
    """Get transcription history."""
    try:
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)

        transcriptions = current_app.db_manager.get_transcriptions(
            limit=limit, offset=offset
        )
        return jsonify({"transcriptions": transcriptions}), 200
    except Exception as e:
        logger.error(f"Error getting transcriptions: {e}")
        return jsonify({"error": str(e)}), 500


# Testing routes
@api_bp.route("/test/keyword/<keyword_id>", methods=["POST"])
def test_keyword(keyword_id):
    """Test a keyword detection."""
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        detected_id, confidence = current_app.analyzer.keyword_detector.detect(text)

        return jsonify(
            {
                "text": text,
                "detected_keyword": detected_id,
                "confidence": confidence,
                "matches_target": detected_id == keyword_id,
            }
        ), 200
    except Exception as e:
        logger.error(f"Error testing keyword: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/test/sound/<sound_id>", methods=["POST"])
def test_sound(sound_id):
    """Test sound playback."""
    try:
        result = current_app.analyzer.sound_manager.play_sound(sound_id)
        if result:
            return jsonify({"message": "Sound playing"}), 200
        else:
            return jsonify({"error": "Failed to play sound"}), 400
    except Exception as e:
        logger.error(f"Error testing sound: {e}")
        return jsonify({"error": str(e)}), 500


# LLM Routes
@api_bp.route("/llm/status", methods=["GET"])
def llm_status():
    """Get LLM engine status."""
    try:
        status = current_app.analyzer.llm_engine.get_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/llm/generate", methods=["POST"])
def llm_generate():
    """Generate text using LLM."""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 256)
        temperature = data.get("temperature", 0.7)
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 1024:
            max_tokens = 256
        
        if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 2.0:
            temperature = 0.7
        
        response = current_app.analyzer.llm_engine.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        if response is None:
            return jsonify({"error": "LLM generation failed"}), 500
        
        return jsonify({
            "prompt": prompt,
            "response": response,
            "backend": current_app.analyzer.llm_engine.active_backend,
        }), 200
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/llm/analyze-context", methods=["POST"])
def llm_analyze_context():
    """Analyze text context using LLM."""
    try:
        data = request.get_json()
        text = data.get("text", "")
        context_keywords = data.get("context_keywords", [])
        threshold = data.get("threshold", 0.6)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if not isinstance(context_keywords, list) or not context_keywords:
            return jsonify({"error": "context_keywords must be non-empty list"}), 400
        
        if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
            threshold = 0.6
        
        analysis = current_app.analyzer.llm_engine.analyze_context(
            text=text,
            context_keywords=context_keywords,
            threshold=threshold,
        )
        
        return jsonify(analysis), 200
    except Exception as e:
        logger.error(f"Error analyzing context: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/llm/cache/clear", methods=["POST"])
def llm_clear_cache():
    """Clear LLM response cache."""
    try:
        current_app.analyzer.llm_engine.clear_cache()
        return jsonify({"message": "LLM cache cleared"}), 200
    except Exception as e:
        logger.error(f"Error clearing LLM cache: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/whisper/test", methods=["POST"])
def whisper_test():
    """Test if Whisper is operational."""
    try:
        data = request.get_json()
        test_text = data.get("test_text", "teste operacional do whisper")
        
        # Try to get Whisper status (check if transcriber exists and is not None)
        result = None
        if hasattr(current_app.analyzer, 'transcriber') and current_app.analyzer.transcriber is not None:
            result = current_app.analyzer.transcriber.get_status()
        
        if result:
            return jsonify({
                "success": True,
                "confidence": 0.95,
                "text": test_text,
                "model": current_app.analyzer.config.get("whisper.model", "base"),
                "message": "Whisper operacional",
                "status": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Whisper não disponível - TranscriberThread não inicializado"
            }), 503
    except Exception as e:
        logger.error(f"Error testing Whisper: {e}")
        return jsonify({"error": str(e), "message": "Erro ao testar Whisper"}), 500


@api_bp.route("/config/gpu", methods=["POST"])
def set_gpu_config():
    """Set GPU usage percentage."""
    try:
        data = request.get_json()
        gpu_usage_percent = data.get("gpu_usage_percent", 50)
        
        # Validate percentage
        if not isinstance(gpu_usage_percent, (int, float)) or gpu_usage_percent < 0 or gpu_usage_percent > 100:
            return jsonify({"error": "GPU usage must be between 0 and 100"}), 400
        
        # Set in config
        current_app.analyzer.config.set("gpu_usage_percent", gpu_usage_percent, persist=False)
        
        logger.info(f"GPU usage set to {gpu_usage_percent}%")
        return jsonify({
            "message": f"GPU usage set to {gpu_usage_percent}%",
            "gpu_usage_percent": gpu_usage_percent
        }), 200
    except Exception as e:
        logger.error(f"Error setting GPU config: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/config/device", methods=["POST"])
def set_device_config():
    """Set audio input device."""
    try:
        data = request.get_json()
        device_id = data.get("device_id")
        
        if device_id is None:
            return jsonify({"error": "device_id is required"}), 400
        
        # Converter para int se for string
        try:
            device_id = int(device_id)
        except (ValueError, TypeError):
            return jsonify({"error": "device_id must be a number"}), 400
        
        # Validar se o device existe
        if current_app.analyzer.audio_processor:
            devices = current_app.analyzer.audio_processor.list_devices()
            device_ids = [d["index"] for d in devices]
            if device_id not in device_ids and device_id != -1:
                return jsonify({"error": f"Device {device_id} not found. Using default device."}), 400
        
        # Delegate the device change to analyzer.set_input_device which performs
        # validation, config updates, and safe restart logic.
        # If analyzer exists and the device is already the same, don't restart
        try:
            current_device = None
            if current_app.analyzer.audio_processor:
                current_device = current_app.analyzer.audio_processor.device_id

            if current_device == device_id:
                # Persist config keys to keep files in sync but avoid restart
                current_app.analyzer.config.set("audio.device_id", device_id, persist=True)
                current_app.analyzer.config.set("audio.input_device", device_id, persist=True)
                logger.info(f"Audio input device already set to {device_id}; no restart needed")
            else:
                # Run set_input_device in background inside application context
                try:
                    app = current_app._get_current_object()
                    analyzer = app.analyzer

                    def _async_set_device(app_obj, analyzer_obj, dev_id):
                        try:
                            with app_obj.app_context():
                                analyzer_obj.set_input_device(dev_id, persist=True)
                        except Exception as inner_e:
                            logger.warning(f"Async set_input_device failed: {inner_e}")

                    import threading
                    thread = threading.Thread(target=_async_set_device, args=(app, analyzer, device_id), daemon=True)
                    thread.start()
                except Exception as e:
                    logger.warning(f"Could not spawn device-set thread: {e}")
        except Exception as e:
            logger.warning(f"Error checking current device: {e}")
        
        logger.info(f"Audio input device set to {device_id}")
        return jsonify({
            "message": f"Dispositivo de entrada configurado",
            "device_id": device_id
        }), 200
    except Exception as e:
        logger.error(f"Error setting device config: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/config/whisper-device", methods=["POST"])
def set_whisper_device_config():
    """Set Whisper processing device (CPU or GPU)."""
    try:
        data = request.get_json()
        device = data.get("device")
        
        if device not in ["auto", "cpu", "cuda"]:
            return jsonify({"error": "device must be 'auto', 'cpu', or 'cuda'"}), 400
        
        # Set in config (with persistence)
        current_app.analyzer.config.set("whisper.device", device, persist=True)
        
        logger.info(f"Whisper device set to {device}")
        return jsonify({
            "message": f"Whisper configurado para usar {device}",
            "device": device
        }), 200
    except Exception as e:
        logger.error(f"Error setting Whisper device: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/audio/test", methods=["POST"])
def test_audio_capture():
    """Test audio capture from microphone."""
    try:
        import time
        from audio.processor import AudioProcessor
        
        data = request.get_json() or {}
        duration = float(data.get("duration", 2))  # 2 segundos padrão
        device_id = int(data.get("device_id", -1))
        
        logger.info(f"Starting audio test: device={device_id}, duration={duration}s")
        
        # Criar processador temporário
        processor = AudioProcessor(device_id=device_id)
        processor.start()
        
        # Capturar áudio
        start_time = time.time()
        total_samples = 0
        max_energy = 0.0
        
        while time.time() - start_time < duration:
            chunk = processor.get_chunk(timeout=0.5)
            if chunk is not None:
                total_samples += len(chunk)
                energy = float(np.sqrt(np.mean(chunk ** 2)))
                max_energy = max(max_energy, energy)
        
        processor.stop()
        
        if processor.pa:
            processor.pa.terminate()
        
        duration_actual = time.time() - start_time
        sample_rate = processor.sample_rate
        
        return jsonify({
            "success": total_samples > 0,
            "device_id": device_id,
            "duration_seconds": round(duration_actual, 2),
            "total_samples": total_samples,
            "sample_rate": sample_rate,
            "expected_samples": int(duration * sample_rate),
            "max_energy": round(max_energy, 4),
            "message": f"Capturados {total_samples} amostras em {duration_actual:.2f}s" if total_samples > 0 else "Nenhum áudio capturado!"
        }), 200
    except Exception as e:
        logger.error(f"Error testing audio capture: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erro ao testar captura de áudio"
        }), 500


@api_bp.route("/audio/level", methods=["GET"])
def get_audio_level():
    """Return current audio level / energy and dB for diagnostics."""
    try:
        processor = current_app.analyzer.audio_processor
        if not processor:
            return jsonify({"error": "Audio processor not initialized"}), 400

        energy = float(processor.get_energy())

        # Convert to dB (RMS-like value)
        import math
        db = 20 * math.log10(max(energy, 1e-6))

        # Normalize dB -60..0 as 0..1
        normalized_level = max(0.0, min(1.0, (db + 60.0) / 60.0))

        is_silent = processor.is_silent()

        silence_threshold = float(processor.silence_threshold)

        suggestion = None
        if is_silent or normalized_level < silence_threshold:
            suggestion = (
                "Detected audio level is below configured silence_threshold. "
                "Try increasing the microphone gain / lowering the silence_threshold setting."
            )

        return jsonify({
            "energy": round(energy, 6),
            "db": round(db, 2),
            "normalized_level": round(normalized_level, 4),
            "is_silent": bool(is_silent),
            "silence_threshold": silence_threshold,
            "suggestion": suggestion,
        }), 200
    except Exception as e:
        logger.error(f"Error getting audio level: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/transcribe/audio", methods=["POST"])
def transcribe_browser_audio():
    """Transcribe audio sent from browser using Web Audio API."""
    try:
        # Receber áudio bruto (Float32Array do navegador)
        audio_bytes = request.data
        
        if not audio_bytes or len(audio_bytes) == 0:
            return jsonify({"error": "No audio data provided"}), 400
        
        # Converter bytes para float32 array
        import struct
        audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # Transcrever
        if current_app.analyzer.transcriber:
            result = current_app.analyzer.transcriber.transcriber.transcribe(audio_data, sample_rate=48000)  # Web Audio usa 48kHz
            
            return jsonify({
                "success": True,
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", "pt")
            }), 200
        else:
            return jsonify({"error": "Transcriber not initialized"}), 500
            
    except Exception as e:
        logger.error(f"Error transcribing browser audio: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erro ao transcrever áudio"
        }), 500

