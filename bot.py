import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InputMediaAudio
from config import app_config
import db

db.init_db()

bot = Bot(token=app_config.BOT_TOKEN)
dp = Dispatcher()

user_active_playlists: dict[str,str] = {}  # user_id → playlist_name
pending_cover_uploads: dict[str,str] = {}  # user_id → playlist_name



@dp.message(F.text.startswith("/start"))
async def start_cmd(message: types.Message):
    db.add_user(message.from_user.id)

    if message.text.strip() == "/start":
        return await message.answer("Welcome to Playlist Bot! Use /newplaylist to create your first playlist.")

    # Handle deep-link like: /start share__<playlist_id>
    args = message.text.split(" ")
    if len(args) != 2:
        return

    payload = args[1]
    if payload.startswith("share__"):
        playlist_id = payload.split("__", 1)[1]
        try:
            playlist_id = int(playlist_id)
        except ValueError:
            return await message.answer("Invalid playlist link.")

        tracks = db.get_tracks_by_playlist_id(playlist_id)
        if not tracks:
            return await message.answer("Playlist is empty or not found.")

        await message.answer("🎧 Playlist shared with you:")
        cover = db.get_cover_image_by_playlist_id(playlist_id)
        if cover:
            await message.answer_photo(cover, caption="🎵 Playlist Cover")

        for i in range(0, len(tracks), 10):
            batch = tracks[i:i+10]
            media = [InputMediaAudio(media=file_id) for file_id in batch]
            await message.answer_media_group(media)

@dp.message(F.text.startswith("/newplaylist"))
async def new_playlist_cmd(message: Message):
    db.add_user(message.from_user.id)
    parts = message.text.split(" ")
    if len(parts) != 2:
        return await message.answer("Usage: /newplaylist <name>. <name> should be one word splitted with '-' or '_'")
    name = parts[1]
    user_id = db.get_user_id(message.from_user.id)
    success = db.create_playlist(user_id, name)
    if success:
        await message.answer(f"✅ Playlist '{name}' created!")
    else:
        await message.answer(f"⚠️ Playlist '{name}' already exists.")

@dp.message(F.text.startswith("/add"))
async def add_usage(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 2:
        return await message.answer("Usage: /add <playlist_name>")
    playlist_name = parts[1]
    user_id = db.get_user_id(message.from_user.id)
    playlists = db.get_playlists(user_id)
    if playlist_name not in playlists:
        return await message.answer("❌ Playlist not found.")
    
    user_active_playlists[message.from_user.id] = playlist_name
    await message.answer(f"🎵 You're now adding music to '{playlist_name}'. Send audio files. Type /finish to finish.")

@dp.message(F.audio)
async def add_audio(message: types.Message):
    user_id = db.get_user_id(message.from_user.id)
    playlist_name = user_active_playlists.get(message.from_user.id)

    if not playlist_name:
        return await message.answer("❗ First, use /add <playlist_name> to start adding tracks.")

    success = db.add_track(playlist_name, user_id, message.audio.file_id)
    if success:
        await message.answer(f"✅ Added to '{playlist_name}'")
    else:
        await message.answer("❌ Failed to add track.")

@dp.message(F.text.startswith("/myplaylists"))
async def my_playlists(message: Message):
    parts = message.text.split(" ")
    if len(parts) != 1:
        return await message.answer("Usage: /myplaylists")
    user_id = db.get_user_id(message.from_user.id)
    playlists = db.get_playlists(user_id)
    if not playlists:
        await message.answer("No playlists yet.")
    else:
        await message.answer("🎧 Your playlists:\n" + "\n".join(playlists))

@dp.message(F.text.startswith("/show_playlist"))
async def show_playlist(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 2:
        return await message.answer("Usage: /show_playlist <playlist_name>")
    
    playlist_name = parts[1]
    user_id = db.get_user_id(message.from_user.id)
    tracks = db.get_tracks(playlist_name, user_id)

    if not tracks:
        return await message.answer("❌ Playlist not found or empty.")

    await message.answer(f"🎧 Showing playlist '{playlist_name}' with {len(tracks)} track(s):")

    # Telegram limit: max 10 media per group
    BATCH_SIZE = 10
    for i in range(0, len(tracks), BATCH_SIZE):
        batch = tracks[i:i + BATCH_SIZE]
        media = [InputMediaAudio(media=file_id,caption=f"{index+i}") for index,file_id in enumerate(batch)]
        await message.answer_media_group(media)

@dp.message(F.text.startswith("/share"))
async def share_cmd(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 2:
        return await message.answer("Usage: /share <playlist_name>")
    
    playlist_name = parts[1]
    user_id = db.get_user_id(message.from_user.id)
    playlist_id = db.get_playlist_id_by_name(user_id, playlist_name)
    
    if not playlist_id:
        return await message.answer("❌ Playlist not found.")

    bot_username = (await bot.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start=share__{playlist_id}"
    await message.answer(f"🔗 Share this playlist:\n{deep_link}")

@dp.message(F.text.startswith("/setcover"))
async def set_cover_cmd(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 2:
        return await message.answer("Usage: /setcover <playlist_name>")
    
    playlist_name = parts[1]
    user_id = db.get_user_id(message.from_user.id)
    playlists = db.get_playlists(user_id)
    if playlist_name not in playlists:
        return await message.answer("❌ Playlist not found.")
    
    pending_cover_uploads[message.from_user.id] = playlist_name
    await message.answer("📸 Now send a photo to set as cover image.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id not in pending_cover_uploads:
        return await message.answer("ℹ️ No playlist selected. Use /setcover <playlist_name> first.")

    playlist_name = pending_cover_uploads.pop(user_id)
    file_id = message.photo[-1].file_id  # highest resolution

    db.set_cover_image(user_id, playlist_name, file_id)
    await message.answer(f"✅ Cover image set for playlist '{playlist_name}'")

@dp.message(F.text.startswith("/remove_track"))
async def remove_track_cmd(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 3:
        return await message.answer("Usage: /remove_track <playlist_name> <track_index>")

    playlist_name = parts[1]
    try:
        index = int(parts[2])
    except ValueError:
        return await message.answer("❌ Invalid track index.")

    user_id = db.get_user_id(message.from_user.id)
    success = db.remove_track_by_index(user_id, playlist_name, index)

    if success:
        await message.answer(f"✅ Track #{index} removed from '{playlist_name}'.")
    else:
        await message.answer("❌ Track or playlist not found.")

@dp.message(F.text.startswith("/remove_playlist"))
async def remove_playlist_cmd(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 2:
        return await message.answer("Usage: /remove_playlist <playlist_name>")
    
    playlist_name = parts[1]
    user_id = db.get_user_id(message.from_user.id)
    success = db.delete_playlist(user_id, playlist_name)
    if success:
        await message.answer(f"🗑 Playlist '{playlist_name}' deleted.")
    else:
        await message.answer("❌ Playlist not found.")

@dp.message(F.text.startswith("/rename"))
async def rename_cmd(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) != 3:
        return await message.answer("Usage: /rename <old_name> <new_name>")
    
    old_name, new_name = parts[1], parts[2]
    user_id = db.get_user_id(message.from_user.id)
    success = db.rename_playlist(user_id, old_name, new_name)

    if success:
        await message.answer(f"✅ Playlist renamed from '{old_name}' to '{new_name}'.")
    else:
        await message.answer("❌ Rename failed. Maybe the new name exists or playlist not found.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
