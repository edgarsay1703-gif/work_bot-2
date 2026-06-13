import logging
import sqlite3
from contextlib import closing
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import config
import utils

logger = logging.getLogger(__name__)

def db_connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(db_connect()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                timezone TEXT NOT NULL DEFAULT 'Europe/Moscow',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_start "
            "ON work_sessions(user_id, started_at)"
        )
        conn.commit()
    logger.info("Database initialized: %s", config.DB_PATH)

def ensure_user(user_id: int):
    with closing(db_connect()) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(user_id, timezone, created_at) VALUES(?, ?, ?)",
            (user_id, config.DEFAULT_TZ, utils.now_utc().isoformat()),
        )
        conn.commit()

def get_user_tz(user_id: int) -> ZoneInfo:
    ensure_user(user_id)
    with closing(db_connect()) as conn:
        row = conn.execute(
            "SELECT timezone FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    tz_name = row["timezone"] if row else config.DEFAULT_TZ
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        logger.warning("Unknown timezone %r for user %s, falling back to default", tz_name, user_id)
        return ZoneInfo(config.DEFAULT_TZ)

def start_session(user_id: int, started_utc_iso: str):
    with closing(db_connect()) as conn:
        conn.execute(
            "INSERT INTO work_sessions(user_id, started_at) VALUES(?, ?)",
            (user_id, started_utc_iso),
        )
        conn.commit()
    logger.info("Session started for user %s at %s", user_id, started_utc_iso)

def get_active_session(user_id: int):
    with closing(db_connect()) as conn:
        return conn.execute(
            "SELECT id, started_at FROM work_sessions "
            "WHERE user_id = ? AND ended_at IS NULL "
            "ORDER BY started_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()

def close_session(session_id: int, ended_utc_iso: str):
    with closing(db_connect()) as conn:
        conn.execute(
            "UPDATE work_sessions SET ended_at = ? WHERE id = ?",
            (ended_utc_iso, session_id),
        )
        conn.commit()
    logger.info("Session %s closed at %s", session_id, ended_utc_iso)

def close_all_active_sessions(user_id: int, ended_utc_iso: str):
    """Закрывает все зависшие открытые сессии пользователя (на случай перезапуска бота)."""
    with closing(db_connect()) as conn:
        count = conn.execute(
            "UPDATE work_sessions SET ended_at = ? "
            "WHERE user_id = ? AND ended_at IS NULL",
            (ended_utc_iso, user_id),
        ).rowcount
        conn.commit()
    if count:
        logger.warning("Force-closed %d stale session(s) for user %s", count, user_id)
    return count

def get_sessions_in_range(user_id: int, start_utc_iso: str, end_utc_iso: str):
    now_iso = utils.now_utc().isoformat()
    with closing(db_connect()) as conn:
        rows = conn.execute(
            """
            SELECT started_at, ended_at
            FROM work_sessions
            WHERE user_id = ?
              AND started_at < ?
              AND COALESCE(ended_at, ?) > ?
            ORDER BY started_at
            """,
            (user_id, end_utc_iso, now_iso, start_utc_iso),
        ).fetchall()
    return [(row["started_at"], row["ended_at"]) for row in rows]

def set_user_timezone(user_id: int, tz_name: str):
    with closing(db_connect()) as conn:
        conn.execute(
            "UPDATE users SET timezone = ? WHERE user_id = ?",
            (tz_name, user_id),
        )
        conn.commit()
    logger.info("Timezone for user %s set to %s", user_id, tz_name)

def get_all_users():
    with closing(db_connect()) as conn:
        return conn.execute("SELECT user_id FROM users").fetchall()
