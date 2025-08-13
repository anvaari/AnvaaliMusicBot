import sqlite3
from utils.logging import get_logger
from database.db import sqlite_db_path
from os.path import join as path_join

logger = get_logger(__name__)

def add_user(telegram_id:int) -> None :
    """
    Add a user record for the given Telegram ID.
    
    If a user with the same Telegram ID already exists, the operation is a no-op (uses INSERT OR IGNORE).
    Errors are logged and not propagated.
    
    Parameters:
        telegram_id (int): Telegram user's numeric ID.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
    except sqlite3.Error:
        logger.error(f"Failed to add {telegram_id} to users table",exc_info=True)
    else:
        logger.debug(f"{telegram_id} user added successfully")

def get_user_id(telegram_id):
    """
    Return the internal database user ID for a given Telegram ID.
    
    Queries the users table for a row with the provided Telegram ID and returns its database id.
    
    Parameters:
        telegram_id (int): Telegram user identifier to look up.
    
    Returns:
        int | None: The user's database id if found; None if no matching user exists or a database error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
            res = cur.fetchone()
    except sqlite3.Error:
        logger.error(f"Failed to get id of user with Telegram ID = {telegram_id}")
        return None
    else:
        logger.debug(f"Successfully get id of user with Telegram ID = {telegram_id}")
        return res[0] if res else None

def create_playlist(user_id, name):
    """
    Create a new playlist for the given user.
    
    Parameters:
        user_id (int): Internal user ID owning the playlist.
        name (str): Playlist name to create.
    
    Returns:
        True if the playlist was created.
        False if a playlist with the same name already exists for that user.
        None if a database error occurred while creating the playlist.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (user_id, name))
    except sqlite3.IntegrityError:
        logger.debug(f"{name} playlist already exists for user_id = {user_id}")
        return False
    except sqlite3.Error:
        logger.error(f"Failed to create a {name} playlist for user_id = {user_id}",exc_info=True)
        return None
    else:
        return True

def add_track(playlist_name, user_id, file_id):
    """
    Add a track (by file_id) to the named playlist for a specific user.
    
    Looks up the playlist ID for the given user and playlist name, then inserts a new track record.
    Parameters:
        playlist_name (str): Playlist name scoped to the provided user_id.
        user_id (int): Internal user identifier.
        file_id (str): File identifier for the track (e.g., Telegram file_id).
    
    Returns:
        bool | None: True if the track was added, False if the track already exists (integrity constraint),
                     or None if a database error occurred.
    """
    playlist_id = get_playlist_id_by_name(user_id,playlist_name)
    if playlist_id is None:
        logger.error(f"DB error resolving playlist_id for user_id={user_id}, name='{playlist_name}'")
        return None
    if playlist_id is False:
        logger.warning(f"Playlist '{playlist_name}' not found for user_id={user_id}")
        return False
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("INSERT INTO tracks (playlist_id, file_id) VALUES (?, ?)", (playlist_id, file_id))
    except sqlite3.IntegrityError:
        logger.info(f"Track with file_id={file_id} already exists for {playlist_name} playlist for user_id={user_id}")
        return False
    except sqlite3.Error:
        logger.error(f"Failed to add track with file_id = {file_id} to playlist {playlist_name} for user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully add track with file_id = {file_id} to playlist {playlist_name} for user_id = {user_id}")
        return True

def get_playlists(user_id):
    """
    Return the list of playlist names for the given internal user ID.
    
    Parameters:
        user_id (int): Internal database ID of the user whose playlists should be retrieved.
    
    Returns:
        list[str] | None: List of playlist names on success, or None if a database error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT name FROM playlists WHERE user_id=?", (user_id,))
    except sqlite3.Error:
        logger.error(f"Failed to get playlists for user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlists for user_id = {user_id}")
        return [row[0] for row in cur.fetchall()]

def get_tracks(playlist_name, user_id):
    """
    Return the list of track file IDs for a user's playlist.
    
    Retrieves all `file_id` values for tracks in the playlist with the exact name `playlist_name`
    that belongs to the user identified by `user_id`. Returns None if a database error occurs.
    
    Parameters:
        playlist_name (str): Exact name of the playlist to query.
        user_id (int): Internal user ID owning the playlist.
    
    Returns:
        list[str] | None: List of track `file_id` strings on success, or None on error.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("""
                SELECT t.file_id FROM tracks t
                JOIN playlists p ON p.id = t.playlist_id
                WHERE p.name=? AND p.user_id=?
            """, (playlist_name, user_id))
    except sqlite3.Error:
        logger.error(f"Failed to get tracks from {playlist_name} playlist for user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get tracks from {playlist_name} playlist for user_id = {user_id}")
        return [row[0] for row in cur.fetchall()]

def get_playlist_id_by_name(user_id, name):
    """
    Return the playlist ID for a given user and playlist name.
    
    Parameters:
        user_id (int): Internal user ID.
        name (str): Playlist name.
    
    Returns:
        int: The playlist ID if found.
        False: If no playlist with the given name exists for the user.
        None: If a database error occurs.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT id FROM playlists WHERE user_id=? AND name=?", (user_id, name))
            res = cur.fetchone()
    except sqlite3.Error:
        logger.error(f"Failed to get playlist ID for {name} playlist from user_id = {user_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlist ID for {name} playlist from user_id = {user_id}")
        return res[0] if res else False
    
def get_playlist_name_by_id(playlist_id:int):
    """
    Return the playlist's name for a given playlist primary key id.
    
    Parameters:
        playlist_id (int): The playlist primary key (playlists.id).
    
    Returns:
        str: The playlist name if found.
        False: If no playlist exists with the given id.
        None: If a database error occurs while querying.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT name FROM playlists WHERE id=?", (playlist_id,))
            res = cur.fetchone()
    except sqlite3.Error:
        logger.error(f"Failed to get playlist Name for id={playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get playlist Name for id={playlist_id}")
        return res[0] if res else False

def get_tracks_by_playlist_id(playlist_id):
    """
    Return a list of track file IDs for the given playlist ID.
    
    Retrieves all `file_id` values from the `tracks` table for the playlist with the provided `playlist_id`.
    Returns an empty list when the playlist has no tracks. Returns `None` if a database error occurs.
    Parameters:
        playlist_id (int): The playlists.id value identifying the playlist.
    
    Returns:
        list[str] | None: List of track file IDs, or None on database error.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT file_id FROM tracks WHERE playlist_id=?", (playlist_id,))
    except sqlite3.Error:
        logger.error(f"Failed to get tracks from playlist_id = {playlist_id}",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully get tracks from playlist_id = {playlist_id}")
        return [row[0] for row in cur.fetchall()]

def set_cover_image(user_id, playlist_name, file_id):
    """
    Set the cover image for a user's playlist.
    
    Updates the playlist row matching the given user_id and playlist_name by setting its cover_file_id to file_id.
    
    Parameters:
        user_id (int): Internal user ID owning the playlist.
        playlist_name (str): Name of the playlist to update.
        file_id (str): File ID to store as the playlist's cover image.
    
    Returns:
        bool: True if the update completed successfully, False if a database error occurred.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("UPDATE playlists SET cover_file_id=? WHERE user_id=? AND name=?", (file_id, user_id, playlist_name))
    except sqlite3.Error:
        logger.error(f"Failed to set cover with file_id = {file_id} in {playlist_name} for user_id = {user_id}",exc_info=True)
        return False
    else:
        logger.debug(f"Successfully set cover with file_id = {file_id} in {playlist_name} for user_id = {user_id}")
        return True

def get_cover_image_by_playlist_id(playlist_id):
    """
    Return the cover image file_id for a playlist.
    
    Looks up the playlist's `cover_file_id` by playlist `id`. Returns the file_id string if a row exists; returns None if the playlist has no cover, the playlist is not found, or a database error occurs.
    
    Parameters:
        playlist_id (int): Playlist primary key.
    
    Returns:
        str | None: Cover image file_id or None when not found or on error.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("SELECT cover_file_id FROM playlists WHERE id=?", (playlist_id,))
            res = cur.fetchone()
    except sqlite3.Error:
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
    except sqlite3.Error:
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
    except sqlite3.Error:
        logger.error(f"Failed to delete track_id = {track_id} from tracks table",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully delete track_id = {track_id} from tracks table")
        
    return True

def delete_playlist(user_id, playlist_name):
    """
    Delete a user's playlist and all tracks contained in it.
    
    Given a user_id and playlist_name, removes all tracks referencing the playlist and then deletes the playlist row.
    
    Parameters:
        user_id (int): Internal user ID owning the playlist.
        playlist_name (str): Name of the playlist to delete.
    
    Returns:
        True if the playlist and its tracks were deleted.
        False if the playlist was not found for the given user.
        None if a database error occurred during deletion.
    """
    playlist_id = get_playlist_id_by_name(user_id, playlist_name)
    if playlist_id is None:
        return None
    if playlist_id is False:
        return False
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("DELETE FROM tracks WHERE playlist_id=?", (playlist_id,))
            cur.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
    except sqlite3.Error:
        logger.error(f"Failed to remove tracks from {playlist_name} playlist.",exc_info=True)
        return None
    else:
        logger.debug(f"Successfully remove tracks from {playlist_name} playlist.")
        return True

def rename_playlist(user_id, old_name, new_name):
    """
    Rename a user's playlist.
    
    Attempts to set a playlist's name from `old_name` to `new_name` for the given internal `user_id`.
    
    Parameters:
        user_id (int): Internal user ID owning the playlist.
        old_name (str): Current playlist name.
        new_name (str): Desired new playlist name.
    
    Returns:
        bool | None: True if the update succeeded; None if a database error occurred.
    """
    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            cur= conn.cursor()
            cur.execute("UPDATE playlists SET name=? WHERE user_id=? AND name=?", (new_name, user_id, old_name))
    except sqlite3.Error:
        logger.error(f"Failed to rename {old_name} playlist to {new_name} for user_id = {user_id}",exc_info=True)
    else:
        logger.debug(f"Successfully rename {old_name} playlist to {new_name} for user_id = {user_id}") 
        return True
