from aiogram.types import Message,CallbackQuery,InaccessibleMessage

def get_user_id(message: Message | CallbackQuery) -> int:
    assert message.from_user is not None, "Expected message.from_user not null"
    return message.from_user.id

def get_message_text_safe(message: Message) -> str:
    assert message.text is not None, "Expected message.text not null"
    return message.text

def get_audio_file_id(message: Message) -> str:
    assert message.audio is not None, "Expected audio message"
    return message.audio.file_id

def get_audio_title(message: Message) -> str:
    assert message.audio is not None, "Expected audio message"
    return message.audio.title or "No Title"

def get_callback_text_safe(callback: CallbackQuery):
    assert callback.data is not None, "Expected callback data"
    return callback.data

def get_callback_message(callback: CallbackQuery):
    assert callback.message is not None, "Expected callback message"
    return callback.message

def get_edit_markup_message(message: Message|InaccessibleMessage):
    assert isinstance(message,Message), "Expected message"
    return message.edit_reply_markup

def get_edit_text_message(message: Message|InaccessibleMessage):
    assert isinstance(message,Message), "Expected Message"
    return message.edit_text