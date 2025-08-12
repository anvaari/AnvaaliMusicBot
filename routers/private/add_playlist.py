from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates
from keyboards.inline import get_playlist_actions_keyboard
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import get_user_id,get_message_text_safe

logger = get_logger(__name__)

add_playlist_router = Router()

@add_playlist_router.message(F.text == "➕ New Playlist")
async def cmd_new_playlist(message: Message, state: FSMContext):
    await message.answer("Enter the name for your new playlist:")
    await state.set_state(PlaylistStates.waiting_for_playlist_name)

@add_playlist_router.message(PlaylistStates.waiting_for_playlist_name)
async def process_new_playlist(message: Message, state: FSMContext):
    name = get_message_text_safe(message)
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    ps.create_playlist(user_db_id,name)
    await message.answer(f"✅ Playlist '{name}' created!", reply_markup=get_playlist_actions_keyboard(name))
    await state.clear()