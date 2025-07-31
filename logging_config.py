import logging
from config import app_config
import sys

class EmojiFormatter(logging.Formatter):
    level_emojis = {
        logging.DEBUG: "🐛",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🔥",
    }

    def format(self, record):
        """
        Format a log record by prepending an emoji corresponding to its log level.
        
        The emoji is added to the beginning of the log message, and the original message is restored after formatting to prevent side effects.
        
        Returns:
            str: The formatted log message with an emoji prefix.
        """
        emoji = self.level_emojis.get(record.levelno, "")
        original_msg = record.getMessage()
        record.msg = f"{emoji} {original_msg}"
        formatted = super().format(record)
        record.msg = original_msg  # Restore original message
        return formatted

def get_logger(logger_name:str):
    """
    Create and configure a logger with emoji-enhanced log messages.
    
    The logger uses the log level specified in the application configuration, outputs to standard output, and formats messages with timestamps, log level, filename, line number, and an emoji corresponding to the log level.
    
    Parameters:
        logger_name (str): The name of the logger to retrieve or create.
    
    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(app_config.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    formatter = EmojiFormatter(
        "%(asctime)s - %(levelname)s "
        "in %(filename)s at line %(lineno)d: "
        "%(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
