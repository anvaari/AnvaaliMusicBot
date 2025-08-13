from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import sys

import asyncio

from routers.private.start import start_router
from routers.private.show_playlists import show_playlist_router
from routers.private.add_track import add_track_router
from routers.private.add_playlist import add_playlist_router
from routers.private.share_playlist import share_playlist_router
from routers.private.show_musics import show_musics_router
from routers.private.rename_playlist import rename_playlist_router
from routers.private.set_cover import set_cover_router
from routers.private.remove_track import remove_track_router
from routers.private.remove_playlist import remove_playlist_router

from config import app_config

from utils.logging import get_logger

from database.db import init_db

logger = get_logger(__name__)



bot = Bot(
    token=app_config.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN
    )
)
dp = Dispatcher()

dp.include_routers(
    start_router,
    show_playlist_router,
    add_track_router,
    add_playlist_router,
    share_playlist_router,
    show_musics_router,
    rename_playlist_router,
    set_cover_router,
    remove_track_router,
    remove_playlist_router
)


async def main():
    """
    Start the Telegram bot: initialize the database, then begin polling for updates.
    
    This coroutine initializes the application's database by calling init_db(). If
    database initialization fails, the process exits with status code 1. On
    successful initialization it starts long-polling the Dispatcher for updates.
    """
    logger.info("Starting bot ...")
    try:
        init_db()
    except:
        logger.error("Database initialization failed, exiting.", exc_info=True)
        sys.exit(1)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
