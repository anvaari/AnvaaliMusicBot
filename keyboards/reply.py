from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.messages import EMOJIS

# Persistent reply keyboard (main menu)
def get_main_menu():
    kb_buttons = [
        [
            KeyboardButton(text=f"{EMOJIS.HEADPHONE.value} My Playlists"), 
            KeyboardButton(text=f"{EMOJIS.NEW.value} New Playlist")
        ]
    ]
    kb = ReplyKeyboardMarkup(keyboard=kb_buttons,resize_keyboard=True)
    
    return kb
