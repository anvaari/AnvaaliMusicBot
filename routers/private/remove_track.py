from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import services.playlist_service as ps
from states.user import PlaylistStates
from utils.logging import get_logger
from utils.messages import EMOJIS
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message,
    get_edit_markup_message,
    get_edit_text_message
)
from keyboards.inline import get_music_remove_list_keyboard

logger = get_logger(__name__)

remove_track_router = Router()

@remove_track_router.callback_query(F.data.startswith("delete_track:"))
async def delete_track_handler(callback: CallbackQuery,state: FSMContext):
    """
    Begin the "remove track" flow: validate the user and playlist, present a keyboard of track indices, and transition the FSM to await the user's index choice.
    
    The incoming CallbackQuery must contain callback data of the form "delete_track:<playlist_name>".
    Behavior:
    - Resolves the Telegram user to an internal DB user id. If resolution fails, edits the message with an internal error notice and returns.
    - Loads tracks for the given playlist. If the playlist is empty or missing, edits the message to indicate the playlist is empty and answers the callback.
    - If tracks exist, edits the message to prompt the user to choose a track index, replaces the message markup with a keyboard of indices, sets the FSM state to PlaylistStates.waiting_for_delete_track, and stores {"playlist_to_remove_track": <playlist_name>} in FSM data.
    - Always answers the callback at the end of a successful flow.
    
    Parameters:
    - callback: CallbackQuery containing the "delete_track:<playlist_name>" data.
    - state: FSMContext used to set the next state and persist the playlist name.
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)
    edit_markup_message = get_edit_markup_message(callback_message)

    user_id = get_user_id(callback)
    playlist_name = callback_text.split(":")[1]

    user_db_id = ps.get_user_id(user_id)
    tracks = ps.get_tracks(playlist_name, user_db_id)

    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        return await edit_text_message(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")
    
    if not tracks:
        logger.warning(f"User {user_id} tried to show non-existent or empty playlist '{playlist_name}'")
        await edit_text_message(f"{EMOJIS.FAIL.value} Playlist is empty")
        return await callback.answer()
        
    music_remove_keyboard = get_music_remove_list_keyboard(list(range(len(tracks))))
    logger.info(f"User {user_id} is trying to remove track from playlist '{playlist_name}'")
    await state.set_state(PlaylistStates.waiting_for_delete_track)
    await state.set_data(data={"playlist_to_remove_track":playlist_name})
    await edit_text_message(
        f"{EMOJIS.LIST_WITH_PEN.value} Please Choose track index from below list to remove.\n"
        "You can see index numbers by tap on *📋 Show Musics* button"
        )
    await edit_markup_message(reply_markup=music_remove_keyboard)

    await callback.answer()

@remove_track_router.callback_query(PlaylistStates.waiting_for_delete_track)
async def delete_track(callback: CallbackQuery, state: FSMContext):
    """
    Remove a track from the playlist chosen earlier in the FSM and notify the user.
    
    Reads the playlist name from FSM state key "playlist_to_remove_track", parses the selected track index from the callback data (expects a colon-separated value with the index after the colon), resolves the caller's DB user id, and calls the playlist service to remove the track by index. Updates the chat message with success, not-found, or error text, clears the FSM state, and answers the callback.
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)

    state_data = await state.get_data()
    playlist_name = state_data["playlist_to_remove_track"]

    user_id = get_user_id(callback)
    track_index = int(callback_text.split(":")[1])

    user_db_id = ps.get_user_id(user_id)
    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        return await edit_text_message(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")


    success = ps.remove_track_by_index(user_db_id, playlist_name, track_index)
    if success is True:
        logger.info(f"User {user_id} removed track #{track_index} from '{playlist_name}'")
        await edit_text_message(f"{EMOJIS.CHECK_MARK.value} Track #{track_index} removed from '{playlist_name}'.")
    elif success is None:
        logger.error(
            f"DB error removing track #{track_index} from '{playlist_name}' "
            f"for user_id={user_id} (db_id={user_db_id})"
        )
        await edit_text_message(f"{EMOJIS.WARN.value} Something went wrong. Please try again.")
    else:
        logger.warning(
            f"Track #{track_index} not found in '{playlist_name}' for user_id={user_id}"
        )
        await edit_text_message(f"{EMOJIS.FAIL.value} Can't remove track #{track_index} from '{playlist_name}'.")
    
    await state.clear()
    return await callback.answer()


            

    


