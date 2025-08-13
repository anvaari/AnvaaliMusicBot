from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.messages import EMOJIS

# Inline keyboard for playlist actions after creation or show
def get_playlist_actions_keyboard(playlist_name: str):
    """
    Build an InlineKeyboardMarkup with playlist-specific action buttons.
    
    Creates a multi-row inline keyboard for managing the given playlist. Buttons and their callback_data patterns:
    - "Add Music" (callback_data: "add_music:{playlist_name}"), "Show Musics" ("show:{playlist_name}")
    - "Delete Track" ("delete_track:{playlist_name}"), "Delete Playlist" ("delete_playlist:{playlist_name}")
    - "Rename Playlist" ("rename:{playlist_name}")
    - "Set Cover" ("set_cover:{playlist_name}"), "Share Playlist" ("share:{playlist_name}")
    
    Button labels include emoji symbols from the EMOJIS enum. The returned keyboard uses row_width=2 and contains an intentionally empty final row.
    Parameters:
        playlist_name (str): Name of the playlist used to build callback_data values.
    
    Returns:
        InlineKeyboardMarkup: Inline keyboard ready to be sent with a Telegram message.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(text=f"{EMOJIS.ADD.value} Add Music", callback_data=f"add_music:{playlist_name}"),
            InlineKeyboardButton(text=f"{EMOJIS.LIST.value} Show Musics", callback_data=f"show:{playlist_name}")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJIS.DANGER.value} Delete Track", callback_data=f"delete_track:{playlist_name}"),
            InlineKeyboardButton(text=f"{EMOJIS.DANGER.value} Delete Playlist", callback_data=f"delete_playlist:{playlist_name}"),
        ],
        [
            InlineKeyboardButton(text=f"{EMOJIS.PEN.value} Rename Playlist", callback_data=f"rename:{playlist_name}")

        ],
        [
            InlineKeyboardButton(text=f"{EMOJIS.PHOTO.value} Set Cover", callback_data=f"set_cover:{playlist_name}"),
            InlineKeyboardButton(text=f"{EMOJIS.LINK.value} Share Playlist", callback_data=f"share:{playlist_name}")
        ],
        [
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard,row_width=2)
    
    return kb

def get_playlist_list_keyboard(playlists_name:list[str]):
    """
    Build an InlineKeyboardMarkup listing playlists in blocks.
    
    Creates one-button rows for each playlist using callback data `use_playlist:{playlist_name}`.
    Playlists are iterated in reverse order in groups of up to four (processing the list from end toward start),
    so the most recently appended names (end of the list) appear first.
    
    Parameters:
        playlists_name (list[str]): Playlist names to include in the keyboard.
    
    Returns:
        InlineKeyboardMarkup: Inline keyboard with one-button rows for each playlist and row_width set to 2.
    """
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
    """
    Builds an InlineKeyboardMarkup that lets the user select tracks to remove.
    
    Creates rows containing up to six inline buttons each. Buttons are labeled with the zero-based track index and use callback data in the form `track_to_remove:{index}`. Only the length of `music_ids` is used; the values in the list are not included in button text.
    
    Parameters:
        music_ids (list[int]): List of music identifiers; only its length determines how many indexed buttons are generated.
    
    Returns:
        InlineKeyboardMarkup: Inline keyboard with rows of up to six track-selection buttons (row_width=2).
    """
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

    """
    Return an InlineKeyboardMarkup prompting the user to confirm or cancel deletion of a playlist.
    
    Parameters:
        playlist_name (str): Playlist name used in the confirm button's callback_data as `confirm_delete:{playlist_name}`.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with two buttons — "✅ Confirm Delete" (confirm_delete:{playlist_name}) and "❌ Cancel" (cancel_delete).
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{EMOJIS.CHECK_MARK.value} Confirm Delete", callback_data=f"confirm_delete:{playlist_name}"),
                InlineKeyboardButton(text=f"{EMOJIS.FAIL.value} Cancel", callback_data="cancel_delete")
            ],
            

        ],
        row_width=2)
    
    return kb