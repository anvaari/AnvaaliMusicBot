import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InputMediaAudio
from config import app_config
import db

# List of available commands and their descriptions
HELP_COMMANDS = {
    "/start": "Start the bot or open a shared playlist.",
    "/newplaylist": "Create a new playlist.",
    "/add": "Add music to a playlist.",
    "/finish": "Finish adding music to a playlist.",
    "/myplaylists": "List your playlists.",
    "/show_playlist": "Show tracks in a playlist.",
    "/share": "Share a playlist with others.",
    "/remove_track": "Remove a track from a playlist.",
    "/remove_playlist": "Delete a playlist.",
    "/rename": "Rename a playlist.",
    "/setcover": "Set a cover image for a playlist.",
    "/help": "Show this help message."
}

@dp.message(F.text == "/help")
async def help_cmd(message: Message):
    help_text = "\u2139\ufe0f **Available Commands:**\n\n"
    for cmd, desc in HELP_COMMANDS.items():
        help_text += f"{cmd} - {desc}\n"
    await message.answer(help_text, parse_mode="Markdown")

db.init_db()

bot = Bot(token=app_config.BOT_TOKEN)
dp = Dispatcher()

# Session state tracking
user_states = {}  # user_id → {'state': str, 'data': any}
user_active_playlists: dict[int, str] = {}
pending_cover_uploads: dict[int, str] = {}

# Utilities
def set_user_state(user_id, state, data=None):
    user_states[user_id] = {'state': state, 'data': data}

def clear_user_state(user_id):
    user_states.pop(user_id, None)

def get_user_state(user_id):
    return user_states.get(user_id)


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


# ==== Handle wrong command ====

@dp.message(lambda message: message.reply_to_message is None and  message.text.startswith('/') and not message.text.split()[0] in [
    "/start", "/add", "/finish", "/myplaylists", "/show_playlist",
    "/share", "/remove_track", "/remove_playlist", "/rename", "/set_cover", "/newplaylist"
])
async def unknown_command(message: types.Message):
    await message.reply("❌ Unknown command. Type `/` to get hint :)")

@dp.message(lambda message: message.reply_to_message is None and not message.text.startswith('/'))
async def bad_message(message: types.Message):
    if get_user_state(message.from_user.id):
        await message.reply("❌ You should interact with reply, don't send orphan message :D ")
    else:
        await message.reply("❌ You have no active command. type / to get hint :)")


# ===== New Playlist =====

@dp.message(F.text == "/newplaylist")
async def newplaylist_cmd(message: Message):
    await message.answer("🎼 Please reply this message with the name of the new playlist:")
    set_user_state(message.from_user.id, "waiting_playlist_name")
        
# ===== Add Session =====

@dp.message(F.text == "/add")
async def add_prompt(message: Message):
    await message.answer("📝 Which playlist would you like to add music to? Reply the name to this message.")
    set_user_state(message.from_user.id, "waiting_add_playlist")

@dp.message(F.audio)
async def add_audio(message: types.Message):
    playlist_name = user_active_playlists.get(message.from_user.id)
    if not playlist_name:
        return await message.answer("❗ First, use /add and select a playlist.")

    user_id = db.get_user_id(message.from_user.id)
    success = db.add_track(playlist_name, user_id, message.audio.file_id)
    if success:
        await message.answer(f"✅ Added to `{playlist_name}`")
    else:
        await message.answer("❌ Failed to add track.")

@dp.message(F.text == "/finish")
async def finish_add(message: Message):
    if message.from_user.id in user_active_playlists:
        del user_active_playlists[message.from_user.id]
        await message.answer("✅ Finished adding music.")
    else:
        await message.answer("ℹ️ No active playlist session.")


# ===== Cover Upload =====

@dp.message(F.text == "/setcover")
async def set_cover_prompt(message: Message):
    await message.answer("📛 Which playlist do you want to set a cover for? Reply the name to this message.")
    set_user_state(message.from_user.id, "waiting_set_cover")

@dp.message(F.photo)
async def handle_cover_upload(message: types.Message):
    user_id = message.from_user.id
    if user_id not in pending_cover_uploads:
        return await message.answer("ℹ️ Use /setcover to choose a playlist first.")
    
    playlist_name = pending_cover_uploads.pop(user_id)
    file_id = message.photo[-1].file_id
    db.set_cover_image(db.get_user_id(user_id), playlist_name, file_id)
    await message.answer(f"✅ Cover image set for '{playlist_name}'")


# ===== Playlist Info =====

@dp.message(F.text == "/myplaylists")
async def my_playlists(message: Message):
    user_id = db.get_user_id(message.from_user.id)
    playlists = db.get_playlists(user_id)
    if not playlists:
        await message.answer("No playlists yet. Use /newplaylist to add one.")
    else:
        await message.answer("🎧 Your playlists:\n" + "\n".join(playlists))

@dp.message(F.text == "/show_playlist")
async def show_playlist_prompt(message: Message):
    await message.answer("📂 Reply the name of the playlist to view:")
    set_user_state(message.from_user.id, "waiting_show_playlist")

# ===== Share, Delete, Rename =====

@dp.message(F.text == "/share")
async def share_prompt(message: Message):
    await message.answer("🔗 Reply the name of the playlist to share:")
    set_user_state(message.from_user.id, "waiting_share")
    
@dp.message(F.text == "/remove_track")
async def remove_track_prompt(message: Message):
    await message.answer("🗑 Reply with <playlist_name> <track_index> to remove:")
    set_user_state(message.from_user.id, "waiting_remove_track")

@dp.message(F.text == "/remove_playlist")
async def remove_playlist_prompt(message: Message):
    await message.answer("🗑 Reply with the name of the playlist to delete:")
    set_user_state(message.from_user.id, "waiting_remove_playlist")

@dp.message(F.text == "/rename")
async def rename_prompt(message: Message):
    await message.answer("✏️ Reply with: <old_name> <new_name>")
    set_user_state(message.from_user.id, "waiting_rename")

# ==== Handle Replies ====
@dp.message(F.text, F.reply_to_message)
async def handle_replies(message: Message):
    state = get_user_state(message.from_user.id)
    if not state:
        return await message.answer(f"You have no active command. type / to get hint :)")

    user_id = db.get_user_id(message.from_user.id)
    text = message.text.strip()

    if state["state"] == "waiting_playlist_name":
        name = text
        success = db.create_playlist(user_id, name)
        clear_user_state(message.from_user.id)
        if success:
            return await message.answer(f"✅ Playlist `{name}` created!")
        else:
            return await message.answer(f"⚠️ Playlist `{name}` already exists.")

    elif state["state"] == "waiting_add_playlist":
        playlist_name = text
        playlists = db.get_playlists(user_id)
        if playlist_name not in playlists:
            clear_user_state(message.from_user.id)
            return await message.answer(f"❌ `{playlist_name}` playlist not found.")
        user_active_playlists[message.from_user.id] = playlist_name
        clear_user_state(message.from_user.id)
        return await message.answer(f"🎵 You're now adding music to `{playlist_name}`. Send audio files. Use /finish when done.")

    elif state["state"] == "waiting_set_cover":
        playlist_name = text
        playlists = db.get_playlists(user_id)
        if playlist_name not in playlists:
            clear_user_state(message.from_user.id)
            return await message.answer(f"❌ `{playlist_name}` playlist not found.")
        pending_cover_uploads[message.from_user.id] = playlist_name
        clear_user_state(message.from_user.id)
        return await message.answer(f"📸 Now send a photo to set as cover image for `{playlist_name}` playlist.")

    elif state["state"] == "waiting_remove_track":
        text_list = text.split(" ")
        if len(text_list) != 2:
            clear_user_state(message.from_user.id)
            return await message.answer("❌ Invalid input. Usage: <playlist_name> <index>. Fetch Indices using /show_playlist command.")
        
        playlist_name, index = text_list

        if not index.isdecimal():
            clear_user_state(message.from_user.id)
            return await message.answer(f"❌ Invalid index. Index should be number but `{index}` given.")

        index = int(index)
        success = db.remove_track_by_index(user_id, playlist_name, index)
        clear_user_state(message.from_user.id)
        if success:
            return await message.answer(f"✅ Track #{index} removed from '{playlist_name}'.")
        else:
            return await message.answer("❌ Track or playlist not found.")
            
    elif state["state"] == "waiting_remove_playlist":
        playlist_name = text
        success = db.delete_playlist(user_id, playlist_name)
        clear_user_state(message.from_user.id)
        if success:
            return await message.answer(f"🗑 Playlist '{playlist_name}' deleted.")
        else:
            return await message.answer("❌ Playlist not found.")

    elif state["state"] == "waiting_rename":
        text_list = text.split(" ")
        if len(text_list) != 2:
            clear_user_state(message.from_user.id)
            return await message.answer("❌ Invalid input. Usage: <old_name> <new_name>")

        old_name , new_name = text_list

        old_playlist_exists = db.get_playlist_id_by_name(message.from_user.id,old_name)
        if not old_playlist_exists:
            clear_user_state(message.from_user.id)
            return await message.answer(f"❌ Invalid Playlist. Playlist `{old_name}` not exists")

        new_playlist_exists = db.get_playlist_id_by_name(message.from_user.id,new_name)
        if not new_playlist_exists:
            clear_user_state(message.from_user.id)
            return await message.answer(f"❌ `{new_name}` already exists, can't rename.")

        db.rename_playlist(user_id, old_name, new_name)
        clear_user_state(message.from_user.id)
        return await message.answer(f"✅ Playlist renamed from '{old_name}' to '{new_name}'.")
    
    elif state["state"] == "waiting_show_playlist":
        playlist_name = message.text.strip()
        user_id = db.get_user_id(message.from_user.id)
        tracks = db.get_tracks(playlist_name, user_id)
        clear_user_state(message.from_user.id)

        if not tracks:
            return await message.answer("❌ Playlist not found or empty.")
        await message.answer(f"🎧 Playlist '{playlist_name}' with {len(tracks)} tracks:")

        for i in range(0, len(tracks), 10):
            batch = tracks[i:i + 10]
            media = [InputMediaAudio(media=file_id,caption=f"Index: {i+index}") for index,file_id in enumerate(batch)]
            await message.answer_media_group(media)
    
    elif state["state"] == "waiting_share":
        playlist_name = message.text.strip()
        user_id = db.get_user_id(message.from_user.id)
        playlist_id = db.get_playlist_id_by_name(user_id, playlist_name)
        clear_user_state(message.from_user.id)

        if not playlist_id:
            return await message.answer("❌ Playlist not found.")

        bot_username = (await bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=share__{playlist_id}"
        await message.answer(f"🔗 Share this link:\n{link}")

# ===== Main Runner =====

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
