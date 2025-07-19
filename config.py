
# config.py - Configuration file for AnvaaliMusicBot
#
# This file loads environment variables and provides configuration options for the bot.
#
# Example .env file:
# BOT_TOKEN=your_discord_bot_token_here
# LOG_LEVEL=INFO
#
# BOT_TOKEN: Discord bot token. Required to run the bot.
# LOG_LEVEL: Logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is INFO.

from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class appConfigs:
    BOT_TOKEN: str = getenv("BOT_TOKEN", "")
    LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO")

    def __post_init__(self):
        if not self.BOT_TOKEN:
            raise ValueError("Please set BOT_TOKEN value as environment variable. Example: BOT_TOKEN=your_token")

app_config = appConfigs()
