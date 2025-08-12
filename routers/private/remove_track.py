from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import services.playlist_service as ps
from states.user import PlaylistStates
from utils.logging import get_logger
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
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)
    edit_markup_message = get_edit_markup_message(callback_message)

    user_id = get_user_id(callback)
    playlist_name = callback_text.split(":")[1]

    user_db_id = ps.get_user_id(user_id)
    tracks = ps.get_tracks(playlist_name, user_db_id)
    
    if not tracks:
        logger.warning(f"User {user_id} tried to show non-existent or empty playlist '{playlist_name}'")
        await edit_text_message("Playlist is empty")
        return await callback.answer()
        
    music_remove_keyboard = get_music_remove_list_keyboard(list(range(len(tracks))))
    logger.info(f"User {user_id} is trying to remove track from playlist '{playlist_name}'")
    await state.set_state(PlaylistStates.waiting_for_delete_track)
    await state.set_data(data={"playlist_to_remove_track":playlist_name})
    await edit_text_message(
        "Please Choose track index from below list to remove.\n"
        "You can see index numbers by tap on *📋 Show Musics* button"
        )
    await edit_markup_message(reply_markup=music_remove_keyboard)

    await callback.answer()

@remove_track_router.callback_query(PlaylistStates.waiting_for_delete_track)
async def delete_track(callback: CallbackQuery, state: FSMContext):
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)

    state_data = await state.get_data()
    playlist_name = state_data["playlist_to_remove_track"]

    user_id = get_user_id(callback)
    track_index = int(callback_text.split(":")[1])

    user_db_id = ps.get_user_id(user_id)

    success = ps.remove_track_by_index(user_db_id, playlist_name, track_index)
    if success == True:
        logger.info(f"User {user_id} removed track #{track_index} from '{playlist_name}'")
        await edit_text_message(f"✅ Track #{track_index} removed from '{playlist_name}'.")
    else:
        logger.warning(f"Failed to remove track #{track_index} from '{playlist_name}' for user_id={user_id} ")
        await edit_text_message(f"❌ Can't remove #{track_index} from *{playlist_name}*")
    
    await state.clear()
    return await callback.answer()


            

    


