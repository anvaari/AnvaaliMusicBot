from aiogram import Router, F
from aiogram.types import Message,InputMediaAudio,CallbackQuery
from keyboards.inline import get_playlist_list_keyboard,get_playlist_actions_keyboard
import services.playlist_service as ps
from database import db
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message
)

logger = get_logger(__name__)

show_playlist_router = Router()

@show_playlist_router.message(F.text == "🎧 My Playlists")
async def show_all_playlists(message: Message):
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    playlists = ps.get_playlists(user_db_id)
    if not playlists:
        await message.answer("No playlists yet. Use `➕ New Playlist` button to add one.")
    else:
        await message.answer("🎧 Your playlists",reply_markup=get_playlist_list_keyboard(playlists))

@show_playlist_router.callback_query(F.data.startswith("use_playlist:"))
async def show_playlist_action_kb(callback: CallbackQuery):
    callback_text = get_callback_text_safe(callback)
    playlist_name = callback_text.split(":")[1]

    callback_message = get_callback_message(callback)
    await callback_message.answer(
        f"Select action for playlist '{playlist_name}':",
        reply_markup=get_playlist_actions_keyboard(playlist_name)
    )

    await callback.answer()

