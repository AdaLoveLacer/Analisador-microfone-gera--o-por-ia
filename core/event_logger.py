"""Event logger for application logging."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from database.db_manager import DatabaseManager

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class DatabaseHandler(logging.Handler):
    """Logging handler that writes to database."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the database."""
        try:
            self.db_manager.add_event(
                event_type=record.name,
                event_data={
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                },
                level=record.levelname,
            )
        except Exception:
            self.handleError(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    db_manager: Optional[DatabaseManager] = None,
) -> None:
    """
    Setup application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        db_manager: DatabaseManager instance for DB logging (optional)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (max 5MB, keep 3 files)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,  # Keep only 3 backup files
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Database handler
    if db_manager:
        db_handler = DatabaseHandler(db_manager)
        db_handler.setLevel(logging.INFO)  # Only INFO and above to DB
        root_logger.addHandler(db_handler)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
