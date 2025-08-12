from aiogram.types import Message,CallbackQuery

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

