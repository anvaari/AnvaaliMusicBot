import sqlite3
from logging_config import get_logger

logger = get_logger(__name__)

conn = sqlite3.connect("playlist.db")
cur = conn.cursor()

def init_db():
    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            cover_file_id TEXT,
            UNIQUE(user_id, name)
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            file_id TEXT
        )""")
    except:
        logger.error("Failed to execute table creation queries",exc_info=True)
        conn.rollback()
    else:
        logger.debug("Tables created successfully (If not exists).")
        conn.commit()

def add_user(telegram_id):
    try:
        cur.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
    except:
        logger.error(f"Failed to add {telegram_id} to users table",exc_info=True)
        conn.rollback()
    else:
        logger.debug(f"{telegram_id} user added successfully")
        conn.commit()

def get_user_id(telegram_id):
    try:
        cur.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
        res = cur.fetchone()
    except:
        logger.error(f"Failed to get id of user with Telegram ID = {telegram_id}")
        return None
    else:
        logger.debug(f"Successfully get id of user with Telegram ID = {telegram_id}")
        return res[0] if res else None

def create_playlist(user_id, name):
    try:
        cur.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (user_id, name))
    except sqlite3.IntegrityError:
        logger.debug(f"{name} playlist already exists for user_id = {user_id}")
        return False
    except:
        logger.error(f"Failed to create a {name} playlist for user_id = {user_id}",exc_info=True)
        return None
    else:
        conn.commit()
        return True

def add_track(playlist_name, user_id, file_id):
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if not playlist_id:
        return False
    try:
        cur.execute("INSERT INTO tracks (playlist_id, file_id) VALUES (?, ?)", (playlist_id, file_id))
    except:
        logger.error(f"Failed to add track with file_id = {file_id} to playlist {playlist_name} for user_id = {user_id}",exc_info=True)
        conn.rollback()
    else:
        logger.debug(f"Successfully add track with file_id = {file_id} to playlist {playlist_name} for user_id = {user_id}")
        conn.commit()
        return True
    return None

def get_playlists(user_id):
    try:
        cur.execute("SELECT name FROM playlists WHERE user_id=?", (user_id,))
    except:
        logger.error(f"Failed to get playlists for user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlists for user_id = {user_id}")
        return [row[0] for row in cur.fetchall()]

def get_tracks(playlist_name, user_id):
    try:
        cur.execute("""
            SELECT t.file_id FROM tracks t
            JOIN playlists p ON p.id = t.playlist_id
            WHERE p.name=? AND p.user_id=?
        """, (playlist_name, user_id))
    except:
        logger.error(f"Failed to get tracks from {playlist_name} playlist for user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get tracks from {playlist_name} playlist for user_id = {user_id}")
        return [row[0] for row in cur.fetchall()]

def get_playlist_id_by_name(user_id, name):
    try:
        cur.execute("SELECT id FROM playlists WHERE user_id=? AND name=?", (user_id, name))
        res = cur.fetchone()
    except:
        logger.error(f"Failed to get playlist ID for {name} playlist from user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlist ID for {name} playlist from user_id = {user_id}")
        return res[0] if res else False

def get_tracks_by_playlist_id(playlist_id):
    try:
        cur.execute("SELECT file_id FROM tracks WHERE playlist_id=?", (playlist_id,))
    except:
        logger.error(f"Failed to get tracks from playlist_id = {playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get tracks from playlist_id = {playlist_id}")
        return [row[0] for row in cur.fetchall()]

def set_cover_image(user_id, playlist_name, file_id):
    try:
        cur.execute("UPDATE playlists SET cover_file_id=? WHERE user_id=? AND name=?", (file_id, user_id, playlist_name))
    except:
        logger.error(f"Failed to set cover with file_id = {file_id} in {playlist_name} for user_id = {user_id}",exc_info=True)
        conn.rollback()
        return False
    else:
        logger.debug(f"Successfully set cover with file_id = {file_id} in {playlist_name} for user_id = {user_id}")
        conn.commit()
        return True

def get_cover_image_by_playlist_id(playlist_id):
    try:
        cur.execute("SELECT cover_file_id FROM playlists WHERE id=?", (playlist_id,))
        res = cur.fetchone()
    except:
        logger.error(f"Failed to get cover image file_id for playlist_id = {playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get cover image file_id for playlist_id = {playlist_id}")
        return res[0] if res else None


def remove_track_by_index(user_id, playlist_name, index):
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if not playlist_id:
        return False
    try:
        cur.execute("SELECT id FROM tracks WHERE playlist_id=? ORDER BY id LIMIT 1 OFFSET ?", (playlist_id, index))
        track = cur.fetchone()
    except:
        logger.error(f"Failed to get track_id from tracks table for playlist_id = {playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get track_id from tracks table for playlist_id = {playlist_id}")
    if not track:
        return False
    track_id = track[0]
    try:
        cur.execute("DELETE FROM tracks WHERE id=?", (track_id,))
    except:
        logger.error(f"Failed to delete track_id = {track_id} from tracks table",exc_info=True)
        conn.rollback()
        return None
    else:
        logger.debug(f"Successfully delete track_id = {track_id} from tracks table")
        conn.commit()
    return True

def delete_playlist(user_id, playlist_name):
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if not playlist_id:
        return False
    try:
        cur.execute("DELETE FROM tracks WHERE playlist_id=?", (playlist_id,))
        cur.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
    except:
        logger.error(f"Failed to remove tracks from {playlist_name} playlist.",exc_info=True)
        conn.rollback()
        return None
    else:
        logger.debug(f"Successfully remove tracks from {playlist_name} playlist.")
        conn.commit()
        return True

def rename_playlist(user_id, old_name, new_name):
    try:
        cur.execute("UPDATE playlists SET name=? WHERE user_id=? AND name=?", (new_name, user_id, old_name))
    except:
        logger.error(f"Failed to rename {old_name} playlist to {new_name} for user_id = {user_id}",exc_info=True)
        conn.rollback()
    else:
        logger.debug(f"Successfully rename {old_name} playlist to {new_name} for user_id = {user_id}")
        conn.commit()
        return True
