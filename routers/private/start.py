from aiogram import Router, F
from aiogram.types import Message, InputMediaAudio
import re
from keyboards.reply import get_main_menu
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import get_user_id, get_message_text_safe

logger = get_logger(__name__)

start_router = Router()


@start_router.message(F.text.startswith("/start"))
async def cmd_start(message: Message):
    user_id = get_user_id(message)
    ps.add_user(user_id)
    
    logger.info(f"User {user_id} started the bot")
    message_text = get_message_text_safe(message)


    if message_text.strip() == "/start":
        return await message.answer("Welcome to Playlist Bot! Choose an option:", reply_markup=get_main_menu())

    # Handle deep-link like: /start share__<playlist_id>
    args = message_text.split(" ")
    if len(args) != 2:
        logger.warning(f"User with '{user_id}' start bot with invalid link, args length more than 2.\nStart link: {message_text}")
        return await message.answer("Unknown start link, so ... Welcome to Playlist Bot! Choose an option:", reply_markup=get_main_menu())

    payload = args[1]
    if payload.startswith("share__"):
        playlist_id_raw = payload.split("__", 1)[1]
        try:
            playlist_id = int(playlist_id_raw)
        except ValueError:
            logger.warning(f"User with '{user_id}' start bot with invalid link, playlist_id was not int.\nStart link: {message_text}")
            return await message.answer("Thought it was playlist link but got invalid playlist link. Choose an option to interact with bot:", reply_markup=get_main_menu())

        playlist_name = ps.get_playlist_name_by_id(playlist_id)
        if playlist_name is None:
            logger.error(f"Can't get playlist name for playlist_id={playlist_id}")
            return await message.answer("❌ Can't retrieve playlist name from database, try again!")
        elif playlist_name is False:
            logger.error(f"User with user_id={user_id} tried to start bot with unknown playlist_id ({playlist_id}.)")
            return await message.answer("❌ Invalid share link, requested playlist does not exist.")
        
        tracks = ps.get_tracks_by_playlist_id(playlist_id)
        if not tracks:
            logger.warning(f"User with id {user_id} start bot with share link but playlist was empty.\nShare link: {message_text}")
            return await message.answer("Playlist is empty or not found.")

        escaped_name = re.sub(
            pattern=r'([*_`\[\]])',
            repl=r'\\\1', 
            string=playlist_name)
        await message.answer(f"🎧 **{escaped_name}** Playlist shared with you:")
        cover = ps.get_cover_image_by_playlist_id(playlist_id)
        if cover:
            await message.answer_photo(cover, caption="🎵 Playlist Cover")

        for i in range(0, len(tracks), 10):
            batch = tracks[i:i+10]
            media = [InputMediaAudio(media=file_id) for file_id in batch]
            await message.answer_media_group(media) # type: ignore
    else:
        logger.warning(f"User with '{user_id}' start bot with invalid link, not started with 'share__'.\nStart link: {message_text}")
        return await message.answer("Unknown start link, so ... Welcome to Playlist Bot! Choose an option:", reply_markup=get_main_menu())

