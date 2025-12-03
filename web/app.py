"""Flask web application and API with Flask-SocketIO."""

import os
import logging
from flask import Flask, render_template, jsonify, request, send_file, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

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
    # Use absolute path for static folder
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    
    app = Flask(__name__, static_folder=static_folder, static_url_path="/static")
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

    # Setup Flask-SocketIO (com gevent async_mode)
    sio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="gevent",
        ping_timeout=60,
        ping_interval=25
    )
    app.sio = sio

    # Register blueprints
    from web.api_routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # Register WebSocket handlers
    from web.websocket_handler import setup_websocket_handlers

    setup_websocket_handlers(sio, analyzer)

    # Routes
    @app.route("/")
    def index():
        """Serve main HTML page."""
        index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return Response(f.read(), mimetype='text/html')
        return jsonify({"error": "index.html not found"}), 404

    @app.route("/static/<path:path>")
    def send_static(path):
        """Serve static files."""
        return send_from_directory(os.path.join(os.path.dirname(__file__), "static"), path)

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
    Run Flask application with Flask-SocketIO.

    Args:
        analyzer: MicrophoneAnalyzer instance
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    try:
        app = create_app(analyzer)
        
        logger.info(f"Starting Flask app with Flask-SocketIO on {host}:{port}")
        logger.info("Using gevent async mode for better compatibility")
        
        # Run with Flask-SocketIO (handles both HTTP and WebSocket)
        # Flask-SocketIO with gevent async_mode handles everything automatically
        app.sio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Desabilitar para evitar duplicação
            log_output=True
        )
        
    except Exception as e:
        logger.error(f"Failed to run Flask app: {e}")
        raise
