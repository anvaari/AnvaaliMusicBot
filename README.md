# 🎵 Anvaali Music Bot

A Telegram bot that allows users to create, manage, and share music playlists made from Telegram audio files. Built with long-term goals of playlist NFTs on TON blockchain.

---

## ✨ Features

- `/add <playlist_name>` – Start adding audio files to a playlist.
- `/cancel` – Cancel current adding session.
- `/show_playlists` – List your playlists.
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

### 2. Fill in your `config.py`

```python
BOT_TOKEN = "your_telegram_bot_token_here"
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
playlist-bot/
├── bot.py          # Main bot logic (aiogram)
├── db.py           # SQLite database functions
├── config.py       # Secrets (BOT_TOKEN)
├── README.md
└── requirements.txt
```

---

## 📌 To Do (Next Phase)

[] Add `/edit_title` to include playlist descriptions
[] Clone/copy playlists via `/copy <playlist_id>`
[] Add support for external streaming (Tidal, YouTube, etc.)
[] Integrate TON wallet login and minting via TonConnect
[] NFT Minting per playlist via TON smart contracts

---

## 📬 Contributing

Feel free to fork, extend, or raise PRs. Ideas welcome.


