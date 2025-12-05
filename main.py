"""Main entry point for the application."""

import os
import sys
import signal
import logging
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configure logging early
from core.event_logger import setup_logging

# Setup basic logging
setup_logging(log_level="INFO", log_file="logs/app.log")
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handle graceful shutdown."""
    logger.info("Shutdown signal received")
    print("\nShutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    try:
        logger.info("Starting Analisador de Microfone")
        logger.info(f"Working directory: {os.getcwd()}")

        # Initialize analyzer
        from core.analyzer import MicrophoneAnalyzer
        from web.app_fastapi import run_app

        analyzer = MicrophoneAnalyzer(config_dir=".", database_dir=".")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start FastAPI app
        logger.info("Starting FastAPI application...")
        run_app(
            analyzer,
            host="0.0.0.0",
            port=5000,
            reload=False,
        )

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
