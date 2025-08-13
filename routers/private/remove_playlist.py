from aiogram import Router, F
from aiogram.types import CallbackQuery
import services.playlist_service as ps
from utils.messages import EMOJIS
from utils.logging import get_logger
from utils.typing import (
    get_user_id,
    get_callback_text_safe,
    get_callback_message,
    get_edit_markup_message,
    get_edit_text_message
)
from keyboards.inline import get_playlist_delete_confirmation_keyboard

logger = get_logger(__name__)

remove_playlist_router = Router()

@remove_playlist_router.callback_query(F.data.startswith("delete_playlist:"))
async def delete_playlist_handler(callback: CallbackQuery):
    """
    Prompt the user to confirm deletion of a playlist and replace the message markup with a confirmation keyboard.
    
    This handler expects callback.data in the form "delete_playlist:<playlist_name>". It extracts the playlist name, sends an alert-style callback answer asking the user to click again to confirm deletion, builds a confirmation inline keyboard for that playlist, and edits the original message to show the confirmation keyboard.
    
    Parameters:
        callback (CallbackQuery): CallbackQuery whose data follows "delete_playlist:<playlist_name>".
    
    Returns:
        The result of editing the original message (the edited Message object).
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)

    playlist_name = callback_text.split(":")[1]
    
    await callback.answer(
        text=f"{EMOJIS.QUESTION.value} Are you sure you want to delete '{playlist_name}'?\nClick again to confirm.",
        show_alert=True
    )
    kb = get_playlist_delete_confirmation_keyboard(playlist_name)

    edit_markup_message = get_edit_markup_message(callback_message)
    return await edit_markup_message(reply_markup=kb)


@remove_playlist_router.callback_query(F.data.startswith("confirm_delete:"))
async def delete_confirm_action(callback: CallbackQuery):
    """
    Handle the confirmation step for deleting a playlist triggered by a callback query.
    
    This handler expects a callback whose data starts with "confirm_delete:" followed by the playlist name.
    It resolves the Telegram user to a database user id, attempts to delete the named playlist via the playlist service,
    edits the original message to indicate success, not-found, or failure, and acknowledges the callback.
    
    Parameters:
        callback (CallbackQuery): The incoming callback query for the delete-confirm action.
    
    Notes:
        - If the user's database id cannot be resolved, the function edits the message to an internal-error notice.
        - The function does not return a value; it performs side effects (message edits and callback acknowledgement).
    """
    callback_text = get_callback_text_safe(callback)
    callback_message = get_callback_message(callback)
    
    playlist_name = callback_text.split(":")[1]

    user_id = get_user_id(callback)
    user_db_id = ps.get_user_id(user_id)

    edit_text_message = get_edit_text_message(callback_message)

    if user_db_id is None:
        logger.error(f"Cannot resolve DB user id for telegram_id={user_id}")
        await edit_text_message(f"{EMOJIS.FAIL.value} Internal error. Please try /start and retry.")
        return await callback.answer()

    success = ps.delete_playlist(user_db_id, playlist_name)
    if success is True:
        logger.info(f"User {user_id} deleted playlist '{playlist_name}'")
        await edit_text_message(f"{EMOJIS.TRASH.value} Playlist '{playlist_name}' deleted.")
        return await callback.answer()
    elif success is False:
        logger.warning(f"User {user_id} tried to delete non-existent playlist '{playlist_name}'")
        await edit_text_message(f"{EMOJIS.FAIL.value} Playlist *{playlist_name}* not found.")
        return await callback.answer()
    else:
        logger.warning(f"User {user_id} failed to delete playlist '{playlist_name}'")
        await edit_text_message(f"{EMOJIS.FAIL.value} Failed to delete *{playlist_name}*.")
        return await callback.answer()

@remove_playlist_router.callback_query(F.data == "cancel_delete")
async def delete_cancel_action(callback: CallbackQuery):
    """
    Handle a cancellation of a playlist deletion flow.
    
    Edits the originating callback message to indicate the deletion was canceled and acknowledges the callback to remove the loading state.
    
    Parameters:
        callback (CallbackQuery): Incoming callback query that triggered cancellation.
    """
    callback_message = get_callback_message(callback)
    edit_text_message = get_edit_text_message(callback_message)

    await edit_text_message(f"{EMOJIS.FAIL.value} Deletion canceled.")
    await callback.answer()


