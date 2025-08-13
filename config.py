from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass
import os
import pathlib

load_dotenv()

@dataclass
class appConfigs:
    BOT_TOKEN: str = getenv("BOT_TOKEN","")
    LOG_LEVEL: str = getenv("LOG_LEVEL","INFO")
    DATABASE_NAME: str = getenv("DATABASE_NAME","playlist.db")
    PROJECT_ROOT_DIR: str = str(pathlib.Path(os.path.dirname(os.path.abspath(__file__))).absolute())
    # Max delay between text and audio forwards (in seconds)
    ADD_TRACK_TIME_WINDOW: int = int(getenv("ADD_TRACK_TIME_WINDOW","60"))

    def __post_init__(self):
        """
        Validate required configuration after initialization.
        
        Raises:
            ValueError: If the BOT_TOKEN configuration is empty or not provided.
        """
        if not self.BOT_TOKEN:
            raise ValueError("Please set BOT_TOKEN value as environment variable")


app_config = appConfigs()   
