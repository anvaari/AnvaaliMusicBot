from aiogram import Router, F
from aiogram.types import CallbackQuery,Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates
import services.playlist_service as ps
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_message,
    get_callback_text_safe
)

logger = get_logger(__name__)

set_cover_router = Router()

@set_cover_router.callback_query(F.data.startswith("set_cover:"))
async def handle_set_cover_callback(callback: CallbackQuery, state: FSMContext):
    callback_text = get_callback_text_safe(callback)
    playlist_name = callback_text.split(":")[1]
    user_id = get_user_id(callback)
    callback_message = get_callback_message(callback)
    
    logger.info(f"User {user_id} is setting a cover for '{playlist_name}'")

    await state.set_data(data={"playlist_name_to_set_cover":playlist_name})
    await state.set_state(PlaylistStates.waiting_for_cover_image)
    await callback_message.answer(
        f"📸 Send photo to set as cover image for **{playlist_name}**.\n"
        "Attention, send photo not file. If you send album, first one will be used."
    )
    await callback.answer()

@set_cover_router.message(PlaylistStates.waiting_for_cover_image)
async def process_add_cover_to_playlist(message: Message, state: FSMContext):
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    
    state_data = await state.get_data()
    playlist_name = state_data["playlist_name_to_set_cover"]

    if message.photo is None:
        logger.warning(f"User:{user_id} tried to add cover image with message other than photo.")
        await state.clear()
        return await message.answer("❌ Please send photo, Can't set this message as cover photo")

    file_id = message.photo[-1].file_id
    cover_set = ps.set_cover_image(user_db_id, playlist_name, file_id)
    if cover_set:
        logger.debug(f"User:{user_id} set file with id={file_id} as cover image for {playlist_name} playlist")
        await message.answer(f"✅ Cover image set for '{playlist_name}'")
    else:
        logger.error(f"Can't set cover image with file_id={file_id} for {playlist_name} for user_id={user_id}")
        await message.answer(f"❌ Failed to set image for '{playlist_name}'")
    await state.clear()

    
    