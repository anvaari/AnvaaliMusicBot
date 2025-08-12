from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import Bot
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message
)

logger = get_logger(__name__)

share_playlist_router = Router()


@share_playlist_router.callback_query(F.data.startswith("share:"))
async def share_playlist(callback: CallbackQuery, bot: Bot):
    callback_text = get_callback_text_safe(callback)
    playlist_name = callback_text.split(":")[1]
    callback_message = get_callback_message(callback)
    
    user_id = get_user_id(callback)
    user_db_id = ps.get_user_id(user_id)
    playlist_id = ps.get_playlist_id_by_name(user_db_id, playlist_name)

    if not playlist_id:
        logger.warning(f"User {user_id} tried to share non-existent playlist '{playlist_name}'")
        return await callback_message.answer("❌ Playlist not found.")

    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=share__{playlist_id}"
    logger.info(f"User {user_id} shared playlist {playlist_name}'")
    await callback_message.answer(f"🔗 Share this link:\n`{link}`")

    await callback.answer()