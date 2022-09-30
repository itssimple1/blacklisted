import io
import re
import sys

from pyrogram import Client, filters
from pyrogram.types import Message

import asyncio
from config import *
from db import get_chat_blacklist, rm_from_blacklist, add_to_blacklist


bot = Client(
    session="HellBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)




async def start_bot():
    try:
        await bot.start()
        print("Bot Started !!")
    except Exception as e:
        print(str(e))

@bot.on_message((filters.bot | filters.text) &  filters.incoming)
async def on_new_message(event: Message):
    if event.from_user.id in USERS:
        return
    name = event.text
    snips = get_chat_blacklist(event.chat.id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception:
                to_del = await event.reply_text("I do not have DELETE permission in this chat")
                rm_from_blacklist(event.chat.id, snip.lower())
                await asyncio.sleep(10)
                await to_del.delete()
            break



@bot.on_message(filters.command(["add"],["$", "!", "/", "?", "."]))
async def on_add_black_list(m: Message):
    if m.from_user.id not in USERS:
        return
    text = m.text.pattern_match.group(1)
    to_blacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})
    for trigger in to_blacklist:
        add_to_blacklist(m.chat.id, trigger.lower())
    await m.reply_text(f"__Added__ `{to_blacklist}` __triggers to the blacklist in the current chat.__")


@bot.on_message(filters.command(["remove"],["$", "!", "/", "?", "."]))
async def on_delete_blacklist(m: Message):
    if m.from_user.id not in USERS:
        return
    text = m.text.pattern_match.group(1)
    to_unblacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})
    successful = sum(
        1
        for trigger in to_unblacklist
        if rm_from_blacklist(m.chat.id_id, trigger.lower())
    )
    await m.reply_text(f"__Removed__ `{successful} / {len(to_unblacklist)}` __from the blacklist.__")



@bot.on_message(filters.command(["listblack", "blacklists", "listblacklist"],["$", "!", "/", "?", "."]))
async def on_view_blacklist(c: bot, m: Message):
    all_blacklisted = get_chat_blacklist(m.chat.id)
    if len(all_blacklisted) > 0:
        OUT_STR = "**Blacklists in the Current Chat:**\n"
        for trigger in all_blacklisted:
            OUT_STR += f"👉 `{trigger}` \n"
    else:
        OUT_STR = f"__No Blacklists found. Start saving using__`/add blacklist_word`"
    if len(OUT_STR) > 4095:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "blacklist.text"
            await m.reply_document(
                out_file,
                force_document=True,
                caption="Blacklists in the Current Chat",
            )
    else:
        await m.reply_text(OUT_STR)


bot.loop.run_until_complete(start_bot())

if len(sys.argv) not in (1, 3, 4):
    bot.disconnect()
else:
    try:
        bot.run_until_disconnected()
    except ConnectionError:
        pass
