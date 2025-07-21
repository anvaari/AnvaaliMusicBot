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
        record.msg = f"{emoji} {record.msg}"
        return super().format(record)

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
