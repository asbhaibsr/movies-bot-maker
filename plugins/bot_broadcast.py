# Broadcast System
# /broadcast — Sirf is bot ke users
# /botbroadcast — Saare clone bots + unke groups

import asyncio, logging
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database.users_chats_db import db
from info import ADMINS

logger = logging.getLogger(__name__)

DELAY      = 0.05
BATCH      = 20
BATCH_WAIT = 1.0


def _get_data(msg: Message) -> dict:
    d = {"parse_mode": enums.ParseMode.HTML}
    if msg.photo:
        d["photo"] = msg.photo.file_id
        d["text"]  = msg.caption.html if msg.caption else ""
    elif msg.video:
        d["video"] = msg.video.file_id
        d["text"]  = msg.caption.html if msg.caption else ""
    elif msg.document:
        d["document"] = msg.document.file_id
        d["text"]     = msg.caption.html if msg.caption else ""
    else:
        d["text"] = msg.text.html if msg.text else ""
    return d


async def _send(bot, cid, data):
    try:
        if "photo" in data:
            await bot.send_photo(cid, data["photo"], caption=data.get("text"), parse_mode=data["parse_mode"])
        elif "video" in data:
            await bot.send_video(cid, data["video"], caption=data.get("text"), parse_mode=data["parse_mode"])
        elif "document" in data:
            await bot.send_document(cid, data["document"], caption=data.get("text"), parse_mode=data["parse_mode"])
        else:
            await bot.send_message(cid, data["text"], parse_mode=data["parse_mode"], disable_web_page_preview=True)
        return True
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        return False
    except (UserIsBlocked, InputUserDeactivated):
        return False
    except Exception:
        return False


async def _run_broadcast(bot, ids, data, sts, label):
    ok = fail = 0
    for i, cid in enumerate(ids):
        if i and i % BATCH == 0:
            try:
                await sts.edit_text(
                    f"<b>📡 {label}</b>\n{i}/{len(ids)}\n✅{ok} ❌{fail}",
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
            await asyncio.sleep(BATCH_WAIT)
        if await _send(bot, cid, data):
            ok += 1
        else:
            fail += 1
        await asyncio.sleep(DELAY)
    return ok, fail


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>Kisi message ko reply karo + /broadcast</b>", parse_mode=enums.ParseMode.HTML)

    data = _get_data(message.reply_to_message)
    sts  = await message.reply_text("<b>📡 Broadcast shuru...</b>", parse_mode=enums.ParseMode.HTML)

    users = []
    async for u in await db.get_all_users():
        users.append(u.get("id"))

    ok, fail = await _run_broadcast(client, users, data, sts, "Broadcast")
    await sts.edit_text(
        f"<b>✅ Done!</b>\n👥 {len(users)} total\n✅ {ok} sent\n❌ {fail} failed",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("botbroadcast") & filters.user(ADMINS))
async def botbroadcast_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("<b>Kisi message ko reply karo + /botbroadcast</b>", parse_mode=enums.ParseMode.HTML)

    data = _get_data(message.reply_to_message)
    sts  = await message.reply_text("<b>📡 Bot Broadcast shuru...</b>", parse_mode=enums.ParseMode.HTML)

    total_ok = total_fail = bots_done = 0
    all_bots = []
    async for b in db.bot.find({}):
        all_bots.append(b)

    from utils import temp
    for bot_data in all_bots:
        try:
            for clone_client in getattr(temp, 'BOTS', []):
                me = await clone_client.get_me()
                if str(me.id) == str(bot_data.get("bot_id","")):
                    # Users
                    users = []
                    async for u in await db.get_all_users():
                        users.append(u.get("id"))
                    ok, fail = await _run_broadcast(clone_client, users, data, sts, f"Bot {bots_done+1}")
                    total_ok   += ok
                    total_fail += fail
                    bots_done  += 1
                    await asyncio.sleep(0.3)
                    break
        except Exception as e:
            logger.error(f"Botbroadcast error: {e}")

    await sts.edit_text(
        f"<b>✅ Bot Broadcast Done!</b>\n🤖 {bots_done} bots\n✅ {total_ok} sent\n❌ {total_fail} failed",
        parse_mode=enums.ParseMode.HTML
    )
