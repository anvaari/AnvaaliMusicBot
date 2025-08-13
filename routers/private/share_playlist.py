from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import Bot
import services.playlist_service as ps
from utils.logging import get_logger
from utils.messages import EMOJIS
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message,
    get_edit_text_message
)

logger = get_logger(__name__)

share_playlist_router = Router()


@share_playlist_router.callback_query(F.data.startswith("share:"))
async def share_playlist(callback: CallbackQuery, bot: Bot):
    """
    Handle a "share:" callback: resolve the playlist and replace the original message with a shareable bot link.
    
    Given an aiogram CallbackQuery triggered by a "share:<playlist_name>" payload, this handler:
    - Resolves the internal DB user id for the Telegram user.
    - Looks up the playlist id by the resolved user and playlist name.
    - On success, builds a share link of the form `https://t.me/{bot_username}?start=share__{playlist_id}` and edits the originating message to present that link.
    - On failure, edits the message with an appropriate user-facing error and acknowledges the callback.
    
    Parameters:
        callback (CallbackQuery): The incoming callback query that contains the "share:<playlist_name>" data and original message.
        bot (Bot): Telegram Bot instance (used to fetch the bot username).
    
    Returns:
        None
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    
    edit_text_message = get_edit_text_message(callback_message)

    user_id = get_user_id(callback)
    playlist_name = callback_text.split(":")[1]

    user_db_id = ps.get_user_id(user_id)
    playlist_id = ps.get_playlist_id_by_name(user_db_id, playlist_name)

    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        await edit_text_message(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")
        return await callback.answer()

    if playlist_id is None:
        logger.error(f"DB error while resolving playlist_id for user={user_id}, name='{playlist_name}'")
        await edit_text_message(f"{EMOJIS.WARN.value} Something went wrong. Please try again later.")
        return await callback.answer()
    if playlist_id is False:
        logger.warning(f"User {user_id} tried to share non-existent playlist '{playlist_name}'")
        await edit_text_message(f"{EMOJIS.FAIL.value} Playlist not found.")
        return await callback.answer()

    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=share__{playlist_id}"
    logger.info(f"User {user_id} shared playlist {playlist_name}'")
    await edit_text_message(f"{EMOJIS.LINK.value} Share this link:\n`{link}`")

    await callback.answer()