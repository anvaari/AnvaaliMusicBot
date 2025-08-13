from aiogram import Router, F
from aiogram.types import Message,CallbackQuery
from keyboards.inline import get_playlist_list_keyboard,get_playlist_actions_keyboard
import services.playlist_service as ps
from utils.logging import get_logger
from utils.messages import EMOJIS
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message,
    get_edit_markup_message,
    get_edit_text_message
)

logger = get_logger(__name__)

show_playlist_router = Router()

@show_playlist_router.message(F.text == f"{EMOJIS.HEADPHONE.value} My Playlists")
async def show_all_playlists(message: Message):
    """
    Handle "🎧 My Playlists" user message: resolve the Telegram user to a DB user, fetch their playlists, and reply with an appropriate message or an inline keyboard listing playlists.
    
    The handler:
    - Resolves the Telegram user id to a database user id.
    - If the DB id cannot be resolved, replies with an internal error message.
    - Fetches playlists for the DB user; on failure replies with a generic error message.
    - If the user has no playlists, informs the user and suggests creating one.
    - If playlists are retrieved, sends a "Your playlists" message with a playlist-list inline keyboard.
    """
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    
    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        return await message.answer(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")

    playlists = ps.get_playlists(user_db_id)
    if playlists is None:
        logger.error(f"Failed to fetch playlists for user_id={user_id} (db_id={user_db_id})")
        return await message.answer(f"{EMOJIS.WARN.value} Something went wrong. Please try again.")
    if playlists is False:
        return await message.answer(f"{EMOJIS.FAIL.value} No playlists yet. Use `➕ New Playlist` button to add one.")
    await message.answer(f"{EMOJIS.HEADPHONE.value} Your playlists", reply_markup=get_playlist_list_keyboard(playlists))

@show_playlist_router.callback_query(F.data.startswith("use_playlist:"))
async def show_playlist_action_kb(callback: CallbackQuery):
    """
    Show available actions for a selected playlist by editing the originating callback message.
    
    Extracts the playlist name from the callback data (expected format "use_playlist:<playlist_name>"), updates the callback's message text to "✏️ Select action for playlist '<playlist_name>':" and replaces its inline keyboard with the keyboard returned by get_playlist_actions_keyboard(playlist_name). Finally, acknowledges the callback to clear the client's loading state.
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)


    playlist_name = callback_text.split(":")[1]

    edit_text_message = get_edit_text_message(callback_message)
    edit_markup_message = get_edit_markup_message(callback_message)

    await edit_text_message(f"{EMOJIS.PEN.value} Select action for playlist '{playlist_name}':")
    await edit_markup_message(reply_markup=get_playlist_actions_keyboard(playlist_name))

    await callback.answer()

