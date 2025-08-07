import sqlite3
from utils import get_logger
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
                UNIQUE(user_id, name)
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER,
                file_id TEXT
            )""")
    except:
        logger.error("Failed to execute table creation queries",exc_info=True)
    else:
        logger.debug("Tables created successfully (If not exists).")

def add_user(telegram_id):
    """
    Add a new user to the database with the specified Telegram ID.
    
    If the user already exists, the operation is ignored. Rolls back the transaction on failure and commits on success.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
    except:
        logger.error(f"Failed to add {telegram_id} to users table",exc_info=True)
    else:
        logger.debug(f"{telegram_id} user added successfully")

def get_user_id(telegram_id):
    """
    Retrieve the internal user ID associated with a given Telegram ID.
    
    Returns:
        int or None: The user ID if found, or None if the user does not exist or an error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
            res = cur.fetchone()
    except:
        logger.error(f"Failed to get id of user with Telegram ID = {telegram_id}")
        return None
    else:
        logger.debug(f"Successfully get id of user with Telegram ID = {telegram_id}")
        return res[0] if res else None

def create_playlist(user_id, name):
    """
    Create a new playlist for a user with the specified name.
    
    Returns:
        True if the playlist was created successfully.
        False if a playlist with the same name already exists for the user.
        None if an unexpected error occurred during creation.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (user_id, name))
    except sqlite3.IntegrityError:
        logger.debug(f"{name} playlist already exists for user_id = {user_id}")
        return False
    except:
        logger.error(f"Failed to create a {name} playlist for user_id = {user_id}",exc_info=True)
        return None
    else:
        return True

def add_track(playlist_name, user_id, file_id):
    """
    Adds a track to a user's playlist by playlist name.
    
    Parameters:
        playlist_name (str): The name of the playlist to add the track to.
        user_id (int): The internal user ID.
        file_id (str): The file ID of the track to add.
    
    Returns:
        bool or None: Returns True if the track was added successfully, False if the playlist does not exist, or None on database error.
    """
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if not playlist_id:
        return False
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("INSERT INTO tracks (playlist_id, file_id) VALUES (?, ?)", (playlist_id, file_id))
    except:
        logger.error(f"Failed to add track with file_id = {file_id} to playlist {playlist_name} for user_id = {user_id}",exc_info=True)
    else:
        logger.debug(f"Successfully add track with file_id = {file_id} to playlist {playlist_name} for user_id = {user_id}")
        return True
    return None

def get_playlists(user_id):
    """
    Retrieve the list of playlist names associated with a given user ID.
    
    Parameters:
        user_id (int): The internal ID of the user whose playlists are to be retrieved.
    
    Returns:
        list[str] or None: A list of playlist names if successful, or None if an error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT name FROM playlists WHERE user_id=?", (user_id,))
    except:
        logger.error(f"Failed to get playlists for user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlists for user_id = {user_id}")
        return [row[0] for row in cur.fetchall()]

def get_tracks(playlist_name, user_id):
    """
    Retrieve a list of track file IDs from a specified playlist for a given user.
    
    Parameters:
        playlist_name (str): The name of the playlist.
        user_id (int): The internal user ID.
    
    Returns:
        list[str] or None: A list of track file IDs if successful, or None if an error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
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
    """
    Retrieve the playlist ID for a given user and playlist name.
    
    Returns:
        int: The playlist ID if found.
        False: If the playlist does not exist for the user.
        None: If a database error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT id FROM playlists WHERE user_id=? AND name=?", (user_id, name))
            res = cur.fetchone()
    except:
        logger.error(f"Failed to get playlist ID for {name} playlist from user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlist ID for {name} playlist from user_id = {user_id}")
        return res[0] if res else False

def get_tracks_by_playlist_id(playlist_id):
    """
    Retrieve a list of track file IDs associated with a given playlist ID.
    
    Parameters:
        playlist_id (int): The unique identifier of the playlist.
    
    Returns:
        list[str] or None: A list of file IDs if successful, or None if an error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT file_id FROM tracks WHERE playlist_id=?", (playlist_id,))
    except:
        logger.error(f"Failed to get tracks from playlist_id = {playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get tracks from playlist_id = {playlist_id}")
        return [row[0] for row in cur.fetchall()]

def set_cover_image(user_id, playlist_name, file_id):
    """
    Set the cover image for a user's playlist.
    
    Updates the cover image file ID for the specified playlist belonging to the given user.
    
    Returns:
        True if the cover image was successfully updated, or False if the operation failed.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("UPDATE playlists SET cover_file_id=? WHERE user_id=? AND name=?", (file_id, user_id, playlist_name))
    except:
        logger.error(f"Failed to set cover with file_id = {file_id} in {playlist_name} for user_id = {user_id}",exc_info=True)
        return False
    else:
        logger.debug(f"Successfully set cover with file_id = {file_id} in {playlist_name} for user_id = {user_id}")
        return True

def get_cover_image_by_playlist_id(playlist_id):
    """
    Retrieve the cover image file ID for a playlist by its playlist ID.
    
    Parameters:
        playlist_id (int): The unique identifier of the playlist.
    
    Returns:
        str or None: The file ID of the cover image if found, or None if not found or on error.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT cover_file_id FROM playlists WHERE id=?", (playlist_id,))
            res = cur.fetchone()
    except:
        logger.error(f"Failed to get cover image file_id for playlist_id = {playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get cover image file_id for playlist_id = {playlist_id}")
        return res[0] if res else None


def remove_track_by_index(user_id, playlist_name, index):
    """
    Remove a track from a user's playlist by its zero-based index.
    
    Parameters:
        user_id (int): The internal user ID.
        playlist_name (str): The name of the playlist.
        index (int): The zero-based index of the track to remove.
    
    Returns:
        bool or None: True if the track was successfully removed, False if the playlist or track does not exist, or None on database error.
    """
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if not playlist_id:
        return False
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
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
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("DELETE FROM tracks WHERE id=?", (track_id,))
    except:
        logger.error(f"Failed to delete track_id = {track_id} from tracks table",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully delete track_id = {track_id} from tracks table")
        
    return True

def delete_playlist(user_id, playlist_name):
    """
    Deletes a playlist and all its tracks for a given user and playlist name.
    
    Returns:
        True if the playlist and its tracks were successfully deleted.
        False if the playlist does not exist.
        None if an unexpected error occurs during deletion.
    """
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if not playlist_id:
        return False
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("DELETE FROM tracks WHERE playlist_id=?", (playlist_id,))
            cur.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
    except:
        logger.error(f"Failed to remove tracks from {playlist_name} playlist.",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully remove tracks from {playlist_name} playlist.")
        return True

def rename_playlist(user_id, old_name, new_name):
    """
    Rename a user's playlist to a new name.
    
    Parameters:
        user_id (int): The internal ID of the user.
        old_name (str): The current name of the playlist.
        new_name (str): The new name for the playlist.
    
    Returns:
        bool: True if the playlist was successfully renamed; None if an error occurred.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("UPDATE playlists SET name=? WHERE user_id=? AND name=?", (new_name, user_id, old_name))
    except:
        logger.error(f"Failed to rename {old_name} playlist to {new_name} for user_id = {user_id}",exc_info=True)
    else:
        logger.debug(f"Successfully rename {old_name} playlist to {new_name} for user_id = {user_id}") 
        return True
