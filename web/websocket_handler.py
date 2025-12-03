"""WebSocket handlers for real-time updates using Flask-SocketIO."""

import logging
import json
from typing import Any, Dict
from datetime import datetime
from flask_socketio import emit

logger = logging.getLogger(__name__)


def setup_websocket_handlers(sio, analyzer):
    """
    Setup Flask-SocketIO event handlers.

    Args:
        sio: Flask-SocketIO instance
        analyzer: MicrophoneAnalyzer instance
    """

    # Connected clients
    connected_clients = set()

    @sio.on("connect")
    def handle_connect():
        """Handle client connection."""
        from flask import request
        client_id = request.sid
        logger.info(f"✓ Client connected: {client_id}")
        connected_clients.add(client_id)
        emit("connection_response", {"data": "Connected to server", "client_id": client_id})

    @sio.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection."""
        from flask import request
        client_id = request.sid
        logger.info(f"✗ Client disconnected: {client_id}")
        connected_clients.discard(client_id)

    @sio.on("start_capture")
    def handle_start_capture(data=None):
        """Handle start capture request."""
        try:
            analyzer.start()
            emit(
                "capture_started",
                {"status": "started", "timestamp": datetime.now().isoformat()},
                broadcast=True
            )
            logger.info("✓ Capture started via WebSocket")
        except Exception as e:
            logger.error(f"✗ Error starting capture: {e}")
            emit("error", {"message": str(e)})

    @sio.on("stop_capture")
    def handle_stop_capture(data=None):
        """Handle stop capture request."""
        try:
            analyzer.stop()
            emit(
                "capture_stopped",
                {"status": "stopped", "timestamp": datetime.now().isoformat()},
                broadcast=True
            )
            logger.info("✓ Capture stopped via WebSocket")
        except Exception as e:
            logger.error(f"✗ Error stopping capture: {e}")
            emit("error", {"message": str(e)})

    @sio.on("get_status")
    def handle_get_status(data=None):
        """Handle status request."""
        try:
            status = analyzer.get_status()
            emit("status_update", status)
            logger.debug("✓ Status sent via WebSocket")
        except Exception as e:
            logger.error(f"✗ Error getting status: {e}")
            emit("error", {"message": str(e)})

    @sio.on("test_keyword")
    def handle_test_keyword(data):
        """Handle test keyword detection."""
        try:
            text = data.get("text", "")
            keyword_id = data.get("keyword_id")
            
            if not text or not keyword_id:
                emit("error", {"message": "text and keyword_id required"})
                return
            
            result = analyzer.keyword_detector.detect(text, keyword_id)
            emit("test_keyword_result", {
                "keyword_id": keyword_id,
                "text": text,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            logger.debug(f"✓ Keyword test: {keyword_id}")
        except Exception as e:
            logger.error(f"✗ Error in test_keyword: {e}")
            emit("error", {"message": str(e)})

    @sio.on("test_sound")
    def handle_test_sound(data):
        """Handle sound test request."""
        try:
            sound_id = data.get("sound_id")
            if not sound_id:
                emit("error", {"message": "No sound_id provided"})
                return

            result = analyzer.sound_manager.play_sound(sound_id)
            emit(
                "sound_played",
                {
                    "sound_id": sound_id,
                    "success": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.debug(f"✓ Sound played: {sound_id}")
        except Exception as e:
            logger.error(f"✗ Error testing sound: {e}")
            emit("error", {"message": str(e)})

    @sio.on("update_config")
    def handle_update_config(data):
        """Handle config update."""
        try:
            if not data:
                emit("error", {"message": "No data provided"})
                return

            config = analyzer.config
            for key, value in data.items():
                config.set(key, value, persist=False)

            config.save_config()
            analyzer.reload_config()

            emit(
                "config_updated",
                {
                    "status": "updated",
                    "timestamp": datetime.now().isoformat(),
                },
                broadcast=True
            )
            logger.info("✓ Config updated via WebSocket")
        except Exception as e:
            logger.error(f"✗ Error updating config: {e}")
            emit("error", {"message": str(e)})

    # Callbacks do analyzer para emitir eventos em tempo real
    def on_transcription(text: str, confidence: float):
        """Emit transcription update to all clients."""
        sio.emit(
            "transcription_update",
            {
                "text": text,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            },
            broadcast=True
        )
        logger.debug(f"📝 Transcription broadcast: {text[:40]}...")

    def on_keyword_detected(keyword_id: str, text: str, confidence: float, context_score: float):
        """Emit keyword detection to all clients."""
        sio.emit(
            "keyword_detected",
            {
                "keyword_id": keyword_id,
                "text": text,
                "confidence": confidence,
                "context_score": context_score,
                "timestamp": datetime.now().isoformat()
            },
            broadcast=True
        )
        logger.info(f"🎯 Keyword detected broadcast: {keyword_id}")

    def on_status_change(status: Dict[str, Any]):
        """Emit status change to all clients."""
        sio.emit(
            "status_update",
            {
                **status,
                "timestamp": datetime.now().isoformat()
            },
            broadcast=True
        )
        logger.debug("🔄 Status update broadcast")

    def on_audio_level(data: Dict[str, Any]):
        """Emit audio level update to all clients."""
        sio.emit(
            "audio_level",
            {
                "level": data.get("level", 0),
                "energy": data.get("energy", 0),
                "timestamp": datetime.now().isoformat()
            },
            broadcast=True
        )

    # Register callbacks
    analyzer.register_transcription_callback(on_transcription)
    analyzer.register_detection_callback(on_keyword_detected)
    analyzer.register_status_callback(on_status_change)
    analyzer.register_audio_level_callback(on_audio_level)

    logger.info("✓ WebSocket handlers configured")
