from aiogram import Router, F
from aiogram.types import CallbackQuery,Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates
import services.playlist_service as ps
from utils.logging import get_logger
from utils.messages import EMOJIS
from utils.typing import (
    get_user_id,
    get_message_text_safe,
    get_callback_message,
    get_callback_text_safe,
    get_edit_text_message
)

logger = get_logger(__name__)

rename_playlist_router = Router()

@rename_playlist_router.callback_query(F.data.startswith("rename:"))
async def handle_rename_callback(callback: CallbackQuery, state: FSMContext):
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)

    playlist_name = callback_text.split(":")[1]

    await state.set_data(data={"playlist_name_to_rename":playlist_name})
    await state.set_state(PlaylistStates.waiting_for_rename)

    await edit_text_message(f"{EMOJIS.NEW.value} Enter new name for {playlist_name}")
    return await callback.answer()

@rename_playlist_router.message(PlaylistStates.waiting_for_rename)
async def process_rename_playlist(message: Message, state: FSMContext):
    user_id = get_user_id(message)

    user_db_id = ps.get_user_id(user_id)
    
    state_data = await state.get_data()
    old_name = state_data["playlist_name_to_rename"]
    new_name = get_message_text_safe(message)

    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        return await message.answer(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")

    new_playlist_exists = ps.get_playlist_id_by_name(user_db_id, new_name)
    if new_playlist_exists:
        logger.warning(f"User {user_id} tried to rename to existing playlist '{new_name}'")
        await state.clear()
        return await message.answer(f"{EMOJIS.FAIL.value} `{new_name}` already exists, can't rename.")
    
    ps.rename_playlist(user_db_id, old_name, new_name)
    await state.clear()
    logger.info(f"User {user_id} renamed playlist '{old_name}' to '{new_name}'")
    return await message.answer(f"{EMOJIS.CHECK_MARK.value} Playlist renamed from '{old_name}' to '{new_name}'.")