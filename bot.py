import io
import re
import sys

from telethon import TelegramClient, events

from config import *
from db import get_chat_blacklist, rm_from_blacklist, add_to_blacklist


bot = TelegramClient(
    session="HellBot",
    api_id=API_ID,
    api_hash=API_HASH,
    auto_reconnect=True,
    connection_retries=None,
).start(bot_token=BOT_TOKEN)


def in_handler(**args):
    def decorator(func):
        bot.add_event_handler(func, events.NewMessage(**args))
        return func
    return decorator


def hell_cmd(pattern: str = None, **args):
    args["func"] = lambda e: e.via_bot_id is None

    if pattern is not None:
        global hell_reg
        if (
            pattern.startswith(r"\#")
            or not pattern.startswith(r"\#")
            and pattern.startswith(r"^")
        ):
            hell_reg = re.compile(pattern)
        else:
            hell_ = "\\" + "/"
            hell_reg = re.compile(hell_ + pattern)

    def decorator(func):
        bot.add_event_handler(
            func, events.NewMessage(**args, incoming=True, pattern=hell_reg)
        )
        return func

    return decorator

async def start_bot():
    try:
        await bot.start()
        print("Bot Started !!")
    except Exception as e:
        print(str(e))

USERS = sudo_users(user)


@in_handler(incoming=True)
async def on_new_message(event):
    if event.sender_id in USERS:
        return
    name = event.raw_text
    snips = get_chat_blacklist(event.chat_id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception:
                to_del = await event.client.send_message(event.chat_id, "I do not have DELETE permission in this chat")
                rm_from_blacklist(event.chat_id, snip.lower())
                await asyncio.sleep(10)
                await to_del.delete()
            break


@hell_cmd(pattern="add(?:\s|$)([\s\S]*)")
async def on_add_black_list(event):
    if event.sender_id not in USERS:
        return
    text = event.pattern_match.group(1)
    to_blacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})
    for trigger in to_blacklist:
        add_to_blacklist(event.chat_id, trigger.lower())
    await event.client.send_message(event.chat_id, f"__Added__ `{to_blacklist}` __triggers to the blacklist in the current chat.__")


@hell_cmd(pattern="remove(?:\s|$)([\s\S]*)")
async def on_delete_blacklist(event):
    if event.sender_id not in USERS:
        return
    text = event.pattern_match.group(1)
    to_unblacklist = list({trigger.strip() for trigger in text.split("\n") if trigger.strip()})
    successful = sum(
        1
        for trigger in to_unblacklist
        if rm_from_blacklist(event.chat_id, trigger.lower())
    )
    await event.client.send_message(event.chat_id, f"__Removed__ `{successful} / {len(to_unblacklist)}` __from the blacklist.__")


@hell_cmd(pattern="listblacklist$")
async def on_view_blacklist(event):
    all_blacklisted = get_chat_blacklist(event.chat_id)
    if len(all_blacklisted) > 0:
        OUT_STR = "**Blacklists in the Current Chat:**\n"
        for trigger in all_blacklisted:
            OUT_STR += f"👉 `{trigger}` \n"
    else:
        OUT_STR = f"__No Blacklists found. Start saving using__`/addblacklist`"
    if len(OUT_STR) > 4095:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "blacklist.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Blacklists in the Current Chat",
                reply_to=event,
            )
    else:
        await event.client.send_message(event.chat_id, OUT_STR)


bot.loop.run_until_complete(start_bot())

if len(sys.argv) not in (1, 3, 4):
    bot.disconnect()
else:
    try:
        bot.run_until_disconnected()
    except ConnectionError:
        pass
