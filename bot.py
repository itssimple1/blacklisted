import sys

from telethon import TelegramClient

from config import *


bot = TelegramClient(
    session="HellBot",
    api_id=API_ID,
    api_hash=API_HASH,
    auto_reconnect=True,
    connection_retries=None,
).start(bot_token=BOT_TOKEN)
