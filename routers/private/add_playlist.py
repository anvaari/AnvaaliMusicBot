from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates
from keyboards.inline import get_playlist_actions_keyboard
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import get_user_id,get_message_text_safe
from utils.messages import EMOJIS

logger = get_logger(__name__)

add_playlist_router = Router()

@add_playlist_router.message(F.text == f"{EMOJIS.ADD.value} New Playlist")
async def cmd_new_playlist(message: Message, state: FSMContext):
    await message.answer(f"{EMOJIS.PEN.value} Enter the name for your new playlist:")
    await state.set_state(PlaylistStates.waiting_for_playlist_name)

@add_playlist_router.message(PlaylistStates.waiting_for_playlist_name)
async def process_new_playlist(message: Message, state: FSMContext):
    playlist_name = get_message_text_safe(message).strip()
    if not playlist_name:
        return await message.answer(f"{EMOJIS.FAIL.value} Playlist name cannot be empty. Please enter a valid name.")
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    result = ps.create_playlist(user_db_id,playlist_name)
    if result is True:
        logger.info(f"User {user_id} created playlist '{playlist_name}'")
        await message.answer(f"{EMOJIS.CHECK_MARK.value} Playlist '{playlist_name}' created!", reply_markup=get_playlist_actions_keyboard(playlist_name))
        return await state.clear()
    elif result is False:
        logger.warning(f"User {user_id} attempted to create duplicate playlist '{playlist_name}'")
        return await message.answer(f"{EMOJIS.FAIL.value} Playlist '{playlist_name}' already exists.")
    else:
        logger.error(f"DB error while creating playlist '{playlist_name}' for user_id={user_id}")
        return await message.answer(f"{EMOJIS.WARN.value} Something went wrong. Please try again.")