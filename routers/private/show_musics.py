from aiogram import Router, F
from aiogram.types import Message,InputMediaAudio,CallbackQuery
import services.playlist_service as ps
from database import db
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message
)

logger = get_logger(__name__)

show_musics_router = Router()

@show_musics_router.callback_query(F.data.startswith("show:"))
async def show_playlist(callback: CallbackQuery):
    callback_text = get_callback_text_safe(callback)
    user_id = get_user_id(callback)
    playlist_name = callback_text.split(":")[1]
    callback_message = get_callback_message(callback)

    user_db_id = ps.get_user_id(user_id)
    tracks = ps.get_tracks(playlist_name, user_db_id)
    playlist_id = ps.get_playlist_id_by_name(user_db_id,playlist_name)
    
    if not tracks:
        logger.warning(f"User {user_id} tried to show non-existent or empty playlist '{playlist_name}'")
        await callback_message.answer(f"❌ Playlist '{playlist_name}' is empty.")
        await callback.answer("Playlist is empty", show_alert=True)
        return
    
    logger.info(f"User {user_id} is viewing playlist '{playlist_name}'")

    playlist_cover_file_id = ps.get_cover_image_by_playlist_id(playlist_id)
    if playlist_cover_file_id:
        await callback_message.answer_photo(playlist_cover_file_id,caption=f"🎧 Playlist '{playlist_name}' with {len(tracks)} tracks")
    else:
        await callback_message.answer(f"🎧 Playlist '{playlist_name}' with {len(tracks)} tracks")

    for i in range(0, len(tracks), 10):
        batch = tracks[i:i + 10]
        media = [InputMediaAudio(media=file_id,caption=f"Index: {i+index}") for index,file_id in enumerate(batch)]
        await callback_message.answer_media_group(media) # type: ignore
    
    await callback.answer()

