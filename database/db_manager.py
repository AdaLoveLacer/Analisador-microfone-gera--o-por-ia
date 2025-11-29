"""Database manager for persistence of events and detections."""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for storing events and detections."""

    DEFAULT_DB_FILE = "app_data.db"
    SCHEMA_VERSION = 1

    def __init__(self, db_dir: str = "."):
        """
        Initialize DatabaseManager.

        Args:
            db_dir: Directory to store database file
        """
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)

        self.db_path = self.db_dir / self.DEFAULT_DB_FILE
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Check schema version
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='config'"
                )
                exists = cursor.fetchone() is not None

                if not exists:
                    self._create_schema(conn)
                    logger.info("Database schema created successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseException(f"Failed to initialize database: {e}")

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create database schema."""
        cursor = conn.cursor()

        # Config table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                data_type TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Keywords table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pattern TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                sound_id TEXT,
                variations TEXT,
                context_keywords TEXT,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Sounds table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sounds (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                volume REAL DEFAULT 0.8,
                enabled BOOLEAN DEFAULT 1,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Detections table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                text_detected TEXT NOT NULL,
                keyword_matched TEXT,
                confidence REAL,
                context_score REAL,
                sound_played TEXT
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp)"
        )

        # Transcriptions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                text TEXT NOT NULL,
                confidence REAL,
                duration_seconds REAL
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_timestamp ON transcriptions(timestamp)"
        )

        # Events table (for logging)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                event_data TEXT,
                level TEXT DEFAULT 'INFO'
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)"
        )

        conn.commit()

    def add_detection(
        self,
        text: str,
        keyword_matched: str,
        confidence: float,
        context_score: float,
        sound_played: Optional[str] = None,
    ) -> int:
        """Add a detection record."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO detections
                    (text_detected, keyword_matched, confidence, context_score, sound_played)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (text, keyword_matched, confidence, context_score, sound_played),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add detection: {e}")
            raise DatabaseException(f"Failed to add detection: {e}")

    def add_transcription(
        self, text: str, confidence: float, duration_seconds: float
    ) -> int:
        """Add a transcription record."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO transcriptions (text, confidence, duration_seconds)
                    VALUES (?, ?, ?)
                    """,
                    (text, confidence, duration_seconds),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add transcription: {e}")
            raise DatabaseException(f"Failed to add transcription: {e}")

    def add_event(
        self, event_type: str, event_data: Optional[Dict] = None, level: str = "INFO"
    ) -> int:
        """Add an event record."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                event_data_json = json.dumps(event_data) if event_data else None
                cursor.execute(
                    """
                    INSERT INTO events (event_type, event_data, level)
                    VALUES (?, ?, ?)
                    """,
                    (event_type, event_data_json, level),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add event: {e}")
            raise DatabaseException(f"Failed to add event: {e}")

    def get_detections(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get detection records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, timestamp, text_detected, keyword_matched,
                           confidence, context_score, sound_played
                    FROM detections
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )
                return self._rows_to_dicts(cursor)
        except Exception as e:
            logger.error(f"Failed to get detections: {e}")
            raise DatabaseException(f"Failed to get detections: {e}")

    def get_transcriptions(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get transcription records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, timestamp, text, confidence, duration_seconds
                    FROM transcriptions
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )
                return self._rows_to_dicts(cursor)
        except Exception as e:
            logger.error(f"Failed to get transcriptions: {e}")
            raise DatabaseException(f"Failed to get transcriptions: {e}")

    def get_events(
        self, limit: int = 100, offset: int = 0, level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get event records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if level:
                    cursor.execute(
                        """
                        SELECT id, timestamp, event_type, event_data, level
                        FROM events
                        WHERE level = ?
                        ORDER BY timestamp DESC
                        LIMIT ? OFFSET ?
                        """,
                        (level, limit, offset),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, timestamp, event_type, event_data, level
                        FROM events
                        ORDER BY timestamp DESC
                        LIMIT ? OFFSET ?
                        """,
                        (limit, offset),
                    )
                return self._rows_to_dicts(cursor)
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            raise DatabaseException(f"Failed to get events: {e}")

    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Total detections
                cursor.execute("SELECT COUNT(*) FROM detections")
                total = cursor.fetchone()[0]

                # Detections by keyword
                cursor.execute(
                    """
                    SELECT keyword_matched, COUNT(*) as count
                    FROM detections
                    WHERE keyword_matched IS NOT NULL
                    GROUP BY keyword_matched
                    ORDER BY count DESC
                    """
                )
                by_keyword = {row[0]: row[1] for row in cursor.fetchall()}

                # Average confidence
                cursor.execute("SELECT AVG(confidence) FROM detections")
                avg_confidence = cursor.fetchone()[0] or 0

                # Average context score
                cursor.execute("SELECT AVG(context_score) FROM detections")
                avg_context = cursor.fetchone()[0] or 0

                return {
                    "total_detections": total,
                    "by_keyword": by_keyword,
                    "avg_confidence": avg_confidence,
                    "avg_context_score": avg_context,
                }
        except Exception as e:
            logger.error(f"Failed to get detection stats: {e}")
            raise DatabaseException(f"Failed to get detection stats: {e}")

    def clear_old_records(self, days: int = 30) -> None:
        """Clear records older than specified days."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now().replace(
                    day=datetime.now().day - days
                )

                cursor.execute(
                    "DELETE FROM detections WHERE timestamp < ?", (cutoff_date,)
                )
                cursor.execute(
                    "DELETE FROM transcriptions WHERE timestamp < ?",
                    (cutoff_date,),
                )
                cursor.execute(
                    "DELETE FROM events WHERE timestamp < ?", (cutoff_date,)
                )

                conn.commit()
                logger.info(f"Cleared records older than {days} days")
        except Exception as e:
            logger.error(f"Failed to clear old records: {e}")
            raise DatabaseException(f"Failed to clear old records: {e}")

    def export_detections_csv(self, file_path: str) -> None:
        """Export detections to CSV file."""
        try:
            detections = self.get_detections(limit=10000)
            if not detections:
                return

            import csv

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=detections[0].keys())
                writer.writeheader()
                writer.writerows(detections)

            logger.info(f"Exported {len(detections)} detections to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export detections: {e}")
            raise DatabaseException(f"Failed to export detections: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _rows_to_dicts(cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """Convert cursor rows to dictionaries."""
        return [dict(row) for row in cursor.fetchall()]
