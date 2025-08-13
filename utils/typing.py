from aiogram.types import Message,CallbackQuery,InaccessibleMessage

def get_user_id(message: Message | CallbackQuery) -> int:
    """
    Return the Telegram user ID from a Message or CallbackQuery.
    
    Parameters:
        message (Message | CallbackQuery): Incoming aiogram Message or CallbackQuery whose `from_user` must be present.
    
    Returns:
        int: The user's Telegram ID.
    
    Raises:
        AssertionError: If `message.from_user` is None.
    """
    assert message.from_user is not None, "Expected message.from_user not null"
    return message.from_user.id

def get_message_text_safe(message: Message) -> str:
    """
    Return the text content of a Telegram Message.
    
    Raises:
        AssertionError: If the message has no text (i.e., message.text is None).
    
    Returns:
        str: The message text.
    """
    assert message.text is not None, "Expected message.text not null"
    return message.text

def get_audio_file_id(message: Message) -> str:
    """
    Return the Telegram file_id for the audio attached to a Message.
    
    Parameters:
        message (Message): A aiogram Message that must include an audio attachment.
    
    Returns:
        str: The audio's file_id.
    
    Raises:
        AssertionError: If the message has no audio (message.audio is None).
    """
    assert message.audio is not None, "Expected audio message"
    return message.audio.file_id

def get_audio_title(message: Message) -> str:
    """
    Return the audio title from a Telegram Message, defaulting to "No Title" if the title is absent.
    
    Parameters:
        message (Message): aiogram Message expected to contain an audio payload.
    
    Returns:
        str: The audio's title, or "No Title" when the audio has no title.
    
    Raises:
        AssertionError: If the provided message has no audio (i.e., message.audio is None).
    """
    assert message.audio is not None, "Expected audio message"
    return message.audio.title or "No Title"

def get_callback_text_safe(callback: CallbackQuery):
    """
    Return the callback query's data string.
    
    Raises:
        AssertionError: If `callback.data` is None.
    
    Returns:
        str: The callback data.
    """
    assert callback.data is not None, "Expected callback data"
    return callback.data

def get_callback_message(callback: CallbackQuery):
    """
    Return the Message object associated with a CallbackQuery.
    
    Parameters:
        callback (CallbackQuery): CallbackQuery expected to have an associated message.
    
    Returns:
        Message: The message attached to the callback.
    
    Raises:
        AssertionError: If `callback.message` is None.
    """
    assert callback.message is not None, "Expected callback message"
    return callback.message

def get_edit_markup_message(message: Message|InaccessibleMessage):
    """
    Return the Message.edit_reply_markup value.
    
    Parameters:
        message (Message | InaccessibleMessage): The object expected to be a Message.
    
    Returns:
        The message.edit_reply_markup value (may be None).
    
    Raises:
        AssertionError: If `message` is not an instance of Message.
    """
    assert isinstance(message,Message), "Expected message"
    return message.edit_reply_markup

def get_edit_text_message(message: Message|InaccessibleMessage):
    """
    Return the `edit_text` attribute from a Message.
    
    If the provided object is not an instance of aiogram.types.Message an AssertionError is raised.
    The returned value may be None if the message has no edit_text.
    """
    assert isinstance(message,Message), "Expected Message"
    return message.edit_text

def get_edit_media_message(message: Message|InaccessibleMessage):
    """
    Return the `edit_media` field from a Message.
    
    Raises:
        AssertionError: If `message` is not an instance of `Message`.
    
    Returns:
        The `edit_media` value from the provided `Message` (may be None).
    """
    assert isinstance(message,Message), "Expected Message"
    return message.edit_media

def get_edit_caption_message(message: Message|InaccessibleMessage):
    """
    Return the `edit_caption` value from a Telegram Message.
    
    This function asserts that the provided object is an aiogram.types.Message and then returns its `edit_caption` attribute. Use this when you need the caption text intended for edited messages.
    
    Parameters:
        message: The object expected to be an aiogram.types.Message (not InaccessibleMessage).
    
    Returns:
        The `edit_caption` value (may be None).
    
    Raises:
        AssertionError: If `message` is not an instance of `Message`.
    """
    assert isinstance(message,Message), "Expected Message"
    return message.edit_caption