from aiogram import Router, F
from aiogram.types import InputMediaAudio,CallbackQuery,InputMediaPhoto
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message,
    get_edit_text_message,
    get_edit_caption_message,
    get_edit_media_message
)

logger = get_logger(__name__)

show_musics_router = Router()

@show_musics_router.callback_query(F.data.startswith("show:"))
async def show_playlist(callback: CallbackQuery):
    callback_text = get_callback_text_safe(callback)
    user_id = get_user_id(callback)
    callback_message = get_callback_message(callback)

    edit_text_message = get_edit_text_message(callback_message)
    edit_caption_message = get_edit_caption_message(callback_message)
    edit_photo_message = get_edit_media_message(callback_message)

    playlist_name = callback_text.split(":")[1]

    user_db_id = ps.get_user_id(user_id)
    tracks = ps.get_tracks(playlist_name, user_db_id)
    playlist_id = ps.get_playlist_id_by_name(user_db_id,playlist_name)
    
    if not tracks:
        logger.warning(f"User {user_id} tried to show non-existent or empty playlist '{playlist_name}'")
        await edit_text_message(f"❌ Playlist '{playlist_name}' is empty.")
        return await callback.answer()
    
    logger.info(f"User {user_id} is viewing playlist '{playlist_name}'")

    playlist_cover_file_id = ps.get_cover_image_by_playlist_id(playlist_id)
    if playlist_cover_file_id:
        await edit_photo_message(media=InputMediaPhoto(media=playlist_cover_file_id))
        await edit_caption_message(caption=f"🎧 Playlist '{playlist_name}' with {len(tracks)} tracks")
    else:
        await edit_text_message(f"🎧 Playlist '{playlist_name}' with {len(tracks)} tracks")

    for i in range(0, len(tracks), 10):
        batch = tracks[i:i + 10]
        media = [InputMediaAudio(media=file_id,caption=f"Index: {i+index}") for index,file_id in enumerate(batch)]
        await callback_message.answer_media_group(media) # type: ignore
    
    await callback.answer()

