from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates

class IgnoreIfInPlaylistState(BaseFilter):
    def __init__(self, exclude_state: str|None = None):
        self.exclude_state = exclude_state

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        # If the user is in a PlaylistState, and it's not the excluded one → ignore
        if current_state is not None and current_state.startswith('PlaylistStates:'):
            return current_state == f'PlaylistStates:{self.exclude_state}'
        return True 