from aiogram import Router, F
from aiogram.types import Message,CallbackQuery
from keyboards.inline import get_playlist_list_keyboard,get_playlist_actions_keyboard
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message,
    get_edit_markup_message,
    get_edit_text_message
)

logger = get_logger(__name__)

show_playlist_router = Router()

@show_playlist_router.message(F.text == "🎧 My Playlists")
async def show_all_playlists(message: Message):
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    
    playlists = ps.get_playlists(user_db_id)
    playlists = ps.get_playlists(user_db_id)
    if playlists is None:
        logger.error(f"Failed to fetch playlists for user_id={user_id} (db_id={user_db_id})")
        return await message.answer("⚠️ Something went wrong. Please try again.")
    if playlists is False:
        return await message.answer("No playlists yet. Use `➕ New Playlist` button to add one.")
    await message.answer("🎧 Your playlists", reply_markup=get_playlist_list_keyboard(playlists))

@show_playlist_router.callback_query(F.data.startswith("use_playlist:"))
async def show_playlist_action_kb(callback: CallbackQuery):
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)


    playlist_name = callback_text.split(":")[1]

    edit_text_message = get_edit_text_message(callback_message)
    edit_markup_message = get_edit_markup_message(callback_message)

    await edit_text_message(f"Select action for playlist '{playlist_name}':")
    await edit_markup_message(reply_markup=get_playlist_actions_keyboard(playlist_name))

    await callback.answer()

