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

        current_app.analyzer.start()
        return jsonify({"message": "Capture started"}), 200
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

        # Update each key
        for key, value in data.items():
            current_app.config_manager.set(key, value, persist=False)

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
