from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline keyboard for playlist actions after creation or show
def get_playlist_actions_keyboard(playlist_name: str):
    inline_keyboard = [
        [
            InlineKeyboardButton(text="➕ Add Music", callback_data=f"add_music:{playlist_name}"),
            InlineKeyboardButton(text="📋 Show Musics", callback_data=f"show:{playlist_name}")
        ],
        [
            InlineKeyboardButton(text="☠️ Delete Track", callback_data=f"delete_track:{playlist_name}"),
            InlineKeyboardButton(text="☠️ Delete Playlist", callback_data=f"delete_playlist:{playlist_name}"),
            InlineKeyboardButton(text="⌨ Rename Playlist", callback_data=f"rename:{playlist_name}")

        ],
        [
            InlineKeyboardButton(text="🖼️ Set Cover", callback_data=f"set_cover:{playlist_name}"),
            InlineKeyboardButton(text="🔗 Share Playlist", callback_data=f"share:{playlist_name}")
        ],
        [
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,row_width=2)
    
    return kb

def get_playlist_list_keyboard(playlists_name:list[str]):
    inline_keyboard = []

    for i in range(len(playlists_name),0,-4):
        for j in range(max(i-4,0),i):
            sub_inline_keyboard = [
                InlineKeyboardButton(text=playlists_name[j],callback_data=f"use_playlist:{playlists_name[j]}")
            ] 
            inline_keyboard.append(sub_inline_keyboard)
    
    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,row_width=2)
    return kb

def get_music_remove_list_keyboard(music_ids:list[int]):
    inline_keyboard = []

    for i in range(0,len(music_ids),6):

        sub_inline_keyboard = [
            InlineKeyboardButton(text=f"{j}",callback_data=f"track_to_remove:{j}")
            for j in range(i,min(i+6,len(music_ids)))
        ] 
        inline_keyboard.append(sub_inline_keyboard)
    
    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,row_width=2)
    return kb

def get_playlist_delete_confirmation_keyboard(playlist_name: str):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm Delete", callback_data=f"confirm_delete:{playlist_name}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_delete")
            ],
            

        ],
        row_width=2)
    
    return kb