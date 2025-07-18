from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class appConfigs:
    BOT_TOKEN: str = getenv("BOT_TOKEN","")
    LOG_LEVEL: str = getenv("LOG_LEVEL","INFO")

    def __post_init__(self):
        if not self.BOT_TOKEN:
            raise ValueError("Please set BOT_TOKEN value as environment variable")


app_config = appConfigs()   
