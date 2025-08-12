from aiogram.fsm.state import State, StatesGroup

class PlaylistStates(StatesGroup):
    waiting_for_playlist_name = State()
    waiting_for_add_music = State()
    waiting_for_show_name = State()
    waiting_for_share_name = State()
    waiting_for_delete_track = State()
    waiting_for_rename = State()
    waiting_for_cover_image = State()
