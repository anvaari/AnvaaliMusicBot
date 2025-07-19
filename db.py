import sqlite3

conn = sqlite3.connect("playlist.db")
cur = conn.cursor()

def init_db():
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
    conn.commit()

def add_user(telegram_id):
    cur.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,))
    conn.commit()

def get_user_id(telegram_id):
    cur.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    res = cur.fetchone()
    return res[0] if res else None

def create_playlist(user_id, name):
    try:
        cur.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def add_track(playlist_name, user_id, file_id):
    cur.execute("SELECT id FROM playlists WHERE name=? AND user_id=?", (playlist_name, user_id))
    res = cur.fetchone()
    if not res:
        return False
    playlist_id = res[0]
    cur.execute("INSERT INTO tracks (playlist_id, file_id) VALUES (?, ?)", (playlist_id, file_id))
    conn.commit()
    return True

def get_playlists(user_id):
    cur.execute("SELECT name FROM playlists WHERE user_id=?", (user_id,))
    return [row[0] for row in cur.fetchall()]

def get_tracks(playlist_name, user_id):
    cur.execute("""
        SELECT t.file_id FROM tracks t
        JOIN playlists p ON p.id = t.playlist_id
        WHERE p.name=? AND p.user_id=?
    """, (playlist_name, user_id))
    return [row[0] for row in cur.fetchall()]

def get_playlist_id_by_name(user_id, name):
    cur.execute("SELECT id FROM playlists WHERE user_id=? AND name=?", (user_id, name))
    res = cur.fetchone()
    return res[0] if res else None

def get_tracks_by_playlist_id(playlist_id):
    cur.execute("SELECT file_id FROM tracks WHERE playlist_id=?", (playlist_id,))
    return [row[0] for row in cur.fetchall()]

def set_cover_image(user_id, playlist_name, file_id):
    cur.execute("UPDATE playlists SET cover_file_id=? WHERE user_id=? AND name=?", (file_id, user_id, playlist_name))
    conn.commit()

def get_cover_image_by_playlist_id(playlist_id):
    cur.execute("SELECT cover_file_id FROM playlists WHERE id=?", (playlist_id,))
    res = cur.fetchone()
    return res[0] if res else None


def remove_track_by_index(user_id, playlist_name, index):
    cur.execute("SELECT id FROM playlists WHERE user_id=? AND name=?", (user_id, playlist_name))
    res = cur.fetchone()
    if not res:
        return False
    playlist_id = res[0]
    cur.execute("SELECT id FROM tracks WHERE playlist_id=? ORDER BY id LIMIT 1 OFFSET ?", (playlist_id, index))
    track = cur.fetchone()
    if not track:
        return False
    track_id = track[0]
    cur.execute("DELETE FROM tracks WHERE id=?", (track_id,))
    conn.commit()
    return True

def delete_playlist(user_id, playlist_name):
    cur.execute("SELECT id FROM playlists WHERE user_id=? AND name=?", (user_id, playlist_name))
    res = cur.fetchone()
    if not res:
        return False
    playlist_id = res[0]
    cur.execute("DELETE FROM tracks WHERE playlist_id=?", (playlist_id,))
    cur.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
    conn.commit()
    return True

def rename_playlist(user_id, old_name, new_name):
    cur.execute("UPDATE playlists SET name=? WHERE user_id=? AND name=?", (new_name, user_id, old_name))
    conn.commit()
    return True
