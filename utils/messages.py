from enum import Enum

class EMOJIS(str, Enum):
    HEADPHONE = '🎧'
    ADD = '➕'
    MIC = '🎤'
    TRASH = '🗑'
    CHECK_MARK = '✅'
    FAIL = '❌'
    LIST = '📋'
    MUSIC = '🎵'
    CAMERA = '📸'
    LINK = '🔗'
    FILE = '📂'
    LIST_WITH_PEN = '📝'
    PHOTO = '🖼️'
    NEW = '🆕'
    DANGER = '☠'
    PEN = '✍🏻'
    WARN = '⚠️'
    CLOCK = '⏰'
    QUESTION = '?'
    HUG = '🫂'


def is_text_starts_with_emoji(text: str) -> bool:
    """Check if text starts with a UI command emoji."""
    text = text.strip()
    if not text:
        return False
    return text[0] in EMOJIS._value2member_map_