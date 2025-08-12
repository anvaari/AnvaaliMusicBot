import sqlite3
from utils.logging import get_logger
from config import app_config
from os.path import join as path_join

logger = get_logger(__name__)


sqlite_db_path = path_join(app_config.PROJECT_ROOT_DIR,app_config.DATABASE_NAME)

def init_db():
    """
    Initialize the SQLite database by creating tables for users, playlists, and tracks if they do not already exist.
    
    This function ensures the required schema is present for the playlist application. Rolls back the transaction on failure and commits on success.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                cover_file_id TEXT,
                UNIQUE(user_id, name),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER,
                file_id TEXT,
                UNIQUE(playlist_id,file_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE
            )""")
    except Exception as e:
        logger.error("Failed to execute table creation queries",exc_info=True)
        raise e
    else:
        logger.debug("Tables created successfully (If not exists).")
