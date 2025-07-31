import logging
from config import app_config

class EmojiFormatter(logging.Formatter):
    level_emojis = {
        logging.DEBUG: "🐛",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🔥",
    }

    def format(self, record):
        emoji = self.level_emojis.get(record.levelno, "")
        original_msg = record.getMessage()
        record.msg = f"{emoji} {original_msg}"
        formatted = super().format(record)
        record.msg = original_msg  # Restore original message
        return formatted

def setup_logging():
    logger = logging.getLogger("anvaali")
    logger.setLevel(app_config.LOG_LEVEL)

    handler = logging.StreamHandler()
    formatter = EmojiFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logging()
