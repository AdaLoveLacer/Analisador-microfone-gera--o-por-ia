"""Flask web application and API."""

import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from python_socketio import Server, ASGIApp
import socketio

from core.analyzer import MicrophoneAnalyzer
from core.config_manager import ConfigManager
from core.event_logger import setup_logging, get_logger
from database.db_manager import DatabaseManager

logger = get_logger(__name__)


def create_app(analyzer: MicrophoneAnalyzer) -> Flask:
    """
    Create and configure Flask application.

    Args:
        analyzer: MicrophoneAnalyzer instance

    Returns:
        Configured Flask application
    """
    app = Flask(__name__, static_folder="web/static", static_url_path="/static")
    app.config["JSON_AS_ASCII"] = False

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Store analyzer reference
    app.analyzer = analyzer
    app.config_manager = analyzer.config
    app.db_manager = analyzer.database

    # Setup logging
    setup_logging(
        log_level=analyzer.config.get("app.log_level", "INFO"),
        log_file="logs/app.log",
        db_manager=analyzer.database,
    )

    # Register blueprints
    from web.api_routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # Setup WebSocket
    sio = socketio.Server(
        async_mode="threading",
        cors_allowed_origins="*",
    )
    app.wsgi = socketio.WSGIApp(sio, app)

    # Store sio reference
    app.sio = sio

    # Register WebSocket handlers
    from web.websocket_handler import setup_websocket_handlers

    setup_websocket_handlers(sio, analyzer)

    # Routes
    @app.route("/")
    def index():
        """Serve main HTML page."""
        return app.send_static_file("index.html")

    @app.route("/static/<path:path>")
    def send_static(path):
        """Serve static files."""
        return app.send_from_directory("web/static", path)

    @app.route("/health")
    def health():
        """Health check endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    logger.info("Flask app created successfully")
    return app


def run_app(
    analyzer: MicrophoneAnalyzer,
    host: str = "0.0.0.0",
    port: int = 5000,
    debug: bool = False,
) -> None:
    """
    Run Flask application.

    Args:
        analyzer: MicrophoneAnalyzer instance
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    try:
        app = create_app(analyzer)
        logger.info(f"Starting Flask app on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"Failed to run Flask app: {e}")
        raise
