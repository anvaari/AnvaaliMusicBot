from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.messages import EMOJIS

# Persistent reply keyboard (main menu)
def get_main_menu():
    """
    Create and return the persistent main menu as an aiogram ReplyKeyboardMarkup.
    
    The keyboard contains a single row with two buttons:
    - "🎧 My Playlists" (EMOJIS.HEADPHONE)
    - "➕ New Playlist" (EMOJIS.NEW)
    
    Returns:
        ReplyKeyboardMarkup: A reply keyboard markup with resize_keyboard=True ready to be sent to users.
    """
    kb_buttons = [
        [
            KeyboardButton(text=f"{EMOJIS.HEADPHONE.value} My Playlists"), 
            KeyboardButton(text=f"{EMOJIS.NEW.value} New Playlist")
        ]
    ]
    kb = ReplyKeyboardMarkup(keyboard=kb_buttons,resize_keyboard=True)
    
    return kb
