# 🎵 Anvaali Music Bot

A Telegram bot that allows users to create, manage, and share music playlists made from Telegram audio files. Built with long-term goals of playlist NFTs on TON blockchain.

---

## ✨ Features

- `/add <playlist_name>` – Start adding audio files to a playlist.
- `/finish` – Cancel current adding session.
- `/myplaylists` – List your playlists.
- `/show_playlist <playlist_name>` – View all tracks in a playlist (sent as a media group).
- `/share <playlist_name>` – Share a playlist link that previews it to others.
- `/remove_track <playlist_name> <index>` – Remove a track from a playlist by index.
- `/remove_playlist <playlist_name>` – Delete a playlist entirely.
- `/rename <old_name> <new_name>` – Rename a playlist.
- `/set_cover <playlist_name>` – Set cover image for playlist.
- Playlist state is session-based — no need for `/done` command.
- Works concurrently with multiple users without conflicts.

---

## 🧠 Vision

This bot is the first phase in a project that will:
- Allow users to mint their playlists as NFTs on the TON blockchain.
- Support artist tipping and token-based unlocks using a custom token (future).
- Create a music NFT ecosystem native to Telegram and TON.

---

## 🏁 Setup

### 1. Install Requirements

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

### 2. set BOT_TOKEN as environment. Use @BotFather to create one

```bash
echo "BOT_TOKEN = \"your_telegram_bot_token_here\" " > .env
```

### 3. Run the Bot

```bash
python bot.py
```

---

## 🗃 Database Schema (SQLite)

* `users`: `id`, `telegram_id`
* `playlists`: `id`, `user_id`, `name`, `cover_file_id`
* `tracks`: `id`, `playlist_id`, `file_id`

---

## 📂 Project Structure

```
AnvaaliMusicBot/
├── bot.py          # Main bot logic and commands (aiogram)
├── db.py           # SQLite database functions with error handling and logging
├── config.py       # Loads environment variables, bot token, and logging level
├── utils.py        # Utility functions (e.g., logger setup)
├── test_utils.py   # Unit tests for utils.py
├── README.md       # Project documentation
└── requirements.txt# Python dependencies
```

---

## 📬 Contributing

Feel free to fork, extend, or raise PRs. Ideas welcome.
