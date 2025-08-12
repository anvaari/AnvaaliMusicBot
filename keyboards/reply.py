from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Persistent reply keyboard (main menu)
def get_main_menu():
    kb_buttons = [
        [
            KeyboardButton(text="🎧 My Playlists"), 
            KeyboardButton(text="➕ New Playlist")
        ]
    ]
    kb = ReplyKeyboardMarkup(keyboard=kb_buttons,resize_keyboard=True)
    
    return kb
