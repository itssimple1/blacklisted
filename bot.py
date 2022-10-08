import io
import re
# import sys

from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus as cms, ChatType as CT
from pyrogram.types import Message
from pyrogram.errors import RPCError, UserNotParticipant, MessageDeleteForbidden

import asyncio
from config import *
from db import get_chat_blacklist, rm_from_blacklist, add_to_blacklist


bot = Client(
    "HellBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

def startup():
    bot.start()
    idle()


@bot.on_message(filters.bot | filters.text)
async def on_new_message(c: bot, m: Message):
    if USERS:
        if m.from_user.id in USERS:
            return
    name = m.text
    snips = get_chat_blacklist(m.chat.id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await m.delete()
            except Exception:
                to_del = await m.reply_text("I do not have DELETE permission in this chat")
                rm_from_blacklist(m.chat.id, snip.lower())
                await asyncio.sleep(10)
                await to_del.delete()
            break


@bot.on_message(filters.command(["start"],["$", "!", "/", "?", "."]))
async def start(c: bot, m: Message):
    if m.chat.type is CT.BOT:
        pass
    if m.chat.type is CT.PRIVATE:
        await bot.send_message(
            m.chat.id,
            f"Hi {m.from_user.mention}, I am a simple bot to create black list. Do `/help` to see what I can do"
        )
    await m.reply_text("I am alive ;)")

@bot.on_message(filters.command(["help"],["$", "!", "/", "?", "."]))
async def help(_, m: Message):
    txt = """
`/add` - to add word in black list
`/remove` - to remove word from black list
`/blacklists` - to show the list of current blacklist words

***PREFIXES ARE `$`, `!`, `/`, `?`, `.`***
You can also use all the prefixes in place of `/`
"""
    to_del = await m.reply_text(txt, quote=True)
    try:
        if m.chat.type not in [CT.PRIVATE, CT.BOT]:
            asyncio.sleep(20)
            await to_del.delete()
    except MessageDeleteForbidden:
        pass

@bot.on_message(filters.command(["add"],["$", "!", "/", "?", "."]))
async def on_add_black_list(_, m: Message):
    user = m.from_user.id
    try:
        member = await m.chat.get_member(user)
    except UserNotParticipant:
        await m.reply_text("***HUH? user is not participan, then who activated the cmd?***")
    except RPCError as e:
        await m.reply_text(f"Got error {e}")

    if user not in USERS and member.status not in [cms.OWNER, cms.ADMINISTRATOR]:
        m.reply_text("Sorry! You can't do that.")
        return
    text = m.text.pattern_match.group(1)
    to_blacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})
    for trigger in to_blacklist:
        add_to_blacklist(m.chat.id, trigger.lower())
    await m.reply_text(f"__Added__ `{to_blacklist}` __triggers to the blacklist in the current chat.__")


@bot.on_message(filters.command(["remove"],["$", "!", "/", "?", "."]))
async def on_delete_blacklist(_, m: Message):
    user = m.from_user.id
    try:
        member = await m.chat.get_member(user)
    except UserNotParticipant:
        await m.reply_text("***HUH? user is not participan, then who activated the cmd?***")
    except RPCError as e:
        await m.reply_text(f"Got error {e}")

    if user not in USERS and member.status not in [cms.OWNER, cms.ADMINISTRATOR]:
        m.reply_text("Sorry! You can't do that.")
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


startup()
