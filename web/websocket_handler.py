"""WebSocket handlers for real-time updates."""

import logging
import json
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_websocket_handlers(sio, analyzer):
    """
    Setup WebSocket event handlers.

    Args:
        sio: SocketIO server instance
        analyzer: MicrophoneAnalyzer instance
    """

    # Connected clients
    connected_clients = set()

    @sio.on("connect")
    def handle_connect(sid, environ):
        """Handle client connection."""
        logger.info(f"Client connected: {sid}")
        connected_clients.add(sid)
        sio.emit("connection_response", {"data": "Connected to server"}, to=sid)

    @sio.on("disconnect")
    def handle_disconnect(sid):
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {sid}")
        connected_clients.discard(sid)

    @sio.on("start_capture")
    def handle_start_capture(sid, data):
        """Handle start capture request."""
        try:
            analyzer.start()
            sio.emit(
                "capture_started",
                {"status": "started", "timestamp": datetime.now().isoformat()},
                to=sid,
            )
            logger.info("Capture started via WebSocket")
        except Exception as e:
            logger.error(f"Error starting capture: {e}")
            sio.emit("error", {"message": str(e)}, to=sid)

    @sio.on("stop_capture")
    def handle_stop_capture(sid, data):
        """Handle stop capture request."""
        try:
            analyzer.stop()
            sio.emit(
                "capture_stopped",
                {"status": "stopped", "timestamp": datetime.now().isoformat()},
                to=sid,
            )
            logger.info("Capture stopped via WebSocket")
        except Exception as e:
            logger.error(f"Error stopping capture: {e}")
            sio.emit("error", {"message": str(e)}, to=sid)

    @sio.on("update_config")
    def handle_update_config(sid, data):
        """Handle config update."""
        try:
            if not data:
                sio.emit("error", {"message": "No data provided"}, to=sid)
                return

            config = analyzer.config
            for key, value in data.items():
                config.set(key, value, persist=False)

            config.save_config()
            analyzer.reload_config()

            sio.emit(
                "config_updated",
                {
                    "status": "updated",
                    "timestamp": datetime.now().isoformat(),
                },
                to=sid,
            )
            logger.info("Config updated via WebSocket")
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            sio.emit("error", {"message": str(e)}, to=sid)

    @sio.on("test_sound")
    def handle_test_sound(sid, data):
        """Handle sound test request."""
        try:
            sound_id = data.get("sound_id")
            if not sound_id:
                sio.emit("error", {"message": "No sound_id provided"}, to=sid)
                return

            result = analyzer.sound_manager.play_sound(sound_id)
            if result:
                sio.emit(
                    "sound_played",
                    {
                        "sound_id": sound_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    to=sid,
                )
            else:
                sio.emit(
                    "error",
                    {"message": f"Failed to play sound: {sound_id}"},
                    to=sid,
                )
        except Exception as e:
            logger.error(f"Error testing sound: {e}")
            sio.emit("error", {"message": str(e)}, to=sid)

    @sio.on("get_status")
    def handle_get_status(sid, data):
        """Handle status request."""
        try:
            status = analyzer.get_status()
            sio.emit("status", status, to=sid)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            sio.emit("error", {"message": str(e)}, to=sid)

    # Register analyzer callbacks for broadcasting updates
    def on_transcription(text, confidence):
        """Broadcast transcription to all clients."""
        sio.emit(
            "transcription_update",
            {
                "text": text,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def on_detection(keyword_id, text, confidence, context_score):
        """Broadcast detection to all clients."""
        sio.emit(
            "keyword_detected",
            {
                "keyword_id": keyword_id,
                "text": text,
                "confidence": confidence,
                "context_score": context_score,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def on_status_change(status):
        """Broadcast status change to all clients."""
        sio.emit("status_update", status)

    # Register callbacks
    analyzer.register_transcription_callback(on_transcription)
    analyzer.register_detection_callback(on_detection)
    analyzer.register_status_callback(on_status_change)

    logger.info("WebSocket handlers configured")
