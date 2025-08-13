from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user import PlaylistStates

class IgnoreIfInPlaylistState(BaseFilter):
    def __init__(self, exclude_state: str|None = None):
        """
        Initialize the filter.
        
        Parameters:
            exclude_state (str | None): Optional name of a PlaylistStates state that should be allowed (i.e., the filter will pass when the current state equals `PlaylistStates:<exclude_state>`). If None, no PlaylistStates value is specially excluded.
        """
        self.exclude_state = exclude_state

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        """
        Return True when the filter should pass for the incoming message based on the user's FSM state.
        
        Checks the current FSM state (via the provided FSM context) and:
        - If the state belongs to PlaylistStates (state string starts with "PlaylistStates:"), returns True only when it exactly matches the configured excluded state (`PlaylistStates:<exclude_state>`); otherwise returns False.
        - If the current state is None or not a PlaylistStates state, returns True.
        
        Returns:
            bool: True if the message should be allowed by the filter, False to ignore it.
        """
        current_state = await state.get_state()
        # If the user is in a PlaylistState, and it's not the excluded one → ignore
        prefix = f"{PlaylistStates.__name__}:"
        if current_state is not None and current_state.startswith(prefix):
            return current_state == f'{prefix}{self.exclude_state}'
        return True 