from aiogram import Router, F
from aiogram.types import CallbackQuery,Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates
import services.playlist_service as ps
from utils.logging import get_logger
from utils.messages import EMOJIS
from utils.typing import (
    get_user_id,
    get_callback_message,
    get_callback_text_safe,
    get_edit_text_message
)

logger = get_logger(__name__)

set_cover_router = Router()

@set_cover_router.callback_query(F.data.startswith("set_cover:"))
async def handle_set_cover_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle a "set_cover:<playlist>" callback: prompt the user to send a photo to set the playlist cover.
    
    Stores the target playlist name in the FSM under the key "playlist_name_to_set_cover", transitions the FSM to PlaylistStates.waiting_for_cover_image, edits the originating callback message to instruct the user to send a photo (not a file; if an album is sent the first photo will be used), and answers the callback to acknowledge it.
    
    Parameters:
        callback (CallbackQuery): Incoming callback query whose data starts with "set_cover:".
        state (FSMContext): FSM context used to store the playlist name and set the next state.
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)

    playlist_name = callback_text.split(":")[1]
    user_id = get_user_id(callback)
    
    logger.info(f"User {user_id} is setting a cover for '{playlist_name}'")

    await state.set_data(data={"playlist_name_to_set_cover":playlist_name})
    await state.set_state(PlaylistStates.waiting_for_cover_image)
    await edit_text_message(
        f"{EMOJIS.CAMERA.value} Send photo to set as cover image for **{playlist_name}**.\n"
        "Attention, send photo not file. If you send album, first one will be used."
    )
    return await callback.answer()

@set_cover_router.message(PlaylistStates.waiting_for_cover_image)
async def process_add_cover_to_playlist(message: Message, state: FSMContext):
    """
    Handle a photo message to set a playlist cover image.
    
    When the FSM is in PlaylistStates.waiting_for_cover_image, this retrieves the target
    playlist name from the FSM state, verifies the incoming message contains a photo,
    resolves the calling user's database ID, and attempts to set the playlist's cover
    image using the photo's file_id. Clears the FSM state before returning.
    
    Parameters:
        message (Message): Incoming Telegram message that should contain a photo. If the
            message contains an album, the last photo (highest resolution) is used.
        state (FSMContext): FSM context containing "playlist_name_to_set_cover" with the
            target playlist name. The state is cleared by this handler in all outcomes.
    """
    user_id = get_user_id(message)
    user_db_id = ps.get_user_id(user_id)
    
    state_data = await state.get_data()
    playlist_name = state_data["playlist_name_to_set_cover"]

    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        return await message.answer(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")

    if message.photo is None:
        logger.warning(f"User:{user_id} tried to add cover image with message other than photo.")
        await state.clear()
        return await message.answer("{EMOJIS.FAIL.value} Please send photo, Can't set this message as cover photo")

    file_id = message.photo[-1].file_id
    cover_set = ps.set_cover_image(user_db_id, playlist_name, file_id)
    if cover_set is True:
        logger.debug(f"User:{user_id} set file with id={file_id} as cover image for {playlist_name} playlist")
        await message.answer(f"{EMOJIS.CHECK_MARK.value} Cover image set for '{playlist_name}'")
    elif cover_set is False:
        logger.error(f"Failed to set cover image with file_id={file_id} for {playlist_name} for user_id={user_id}")
        await message.answer(f"{EMOJIS.FAIL.value} Failed to set image for '{playlist_name}'")
    else:
        logger.error(f"Database error while setting cover for playlist '{playlist_name}' for user {user_id}")
        await message.answer(f"{EMOJIS.FAIL.value} Database error. Please try again.")
    return await state.clear()

    
    