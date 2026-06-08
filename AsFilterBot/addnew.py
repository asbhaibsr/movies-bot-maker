# ════════════════════════════════════════════════════════════
#   /addnew — Clone Bot Owner Movie Add Command
#   Clone owner file bhejta hai → Main channel mein save
# ════════════════════════════════════════════════════════════
import asyncio, logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ListenerTimeout
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL
from utils import temp, get_size
from userbot import add_to_channel

logger = logging.getLogger(__name__)


async def _is_owner(client, user_id: int) -> bool:
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    return user_id == bd.get("user_id") or user_id in ADMINS


# ── /addnew command ──────────────────────────────────────────
from clone_filter import clone_admin, clone_or_group_admin
@Client.on_message(filters.command("addnew") & filters.incoming)
async def addnew_cmd(client, message: Message):
    if not await _is_owner(client, message.from_user.id):
        return await message.reply(
            "<b>❌ Ye command sirf bot owner ke liye hai!</b>",
            parse_mode=enums.ParseMode.HTML
        )

    me = await client.get_me()
    from info import MAIN_MOVIE_CHANNEL
    if not MAIN_MOVIE_CHANNEL:
        return await message.reply(
            "<b>❌ MAIN_MOVIE_CHANNEL set nahi hai.</b>\n"
            "Main bot admin se contact karo.",
            parse_mode=enums.ParseMode.HTML
        )

    prompt = await message.reply(
        "<b>📁 Movie File Bhejo</b>\n\n"
        "Abhi apni movie file bhejdo (video/document).\n"
        "File hamari main library mein add ho jayegi.\n\n"
        "⏰ 2 min mein bhejo ya /cancel karo:",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        reply = await client.listen(message.from_user.id, timeout=120)
    except (asyncio.TimeoutError, ListenerTimeout):
        return await prompt.edit_text(
            "<b>⏰ Timeout! Dobara /addnew karo.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("<b>❌ Cancel kar diya.</b>", parse_mode=enums.ParseMode.HTML)

    media = reply.video or reply.document or reply.audio
    if not media:
        return await reply.reply(
            "<b>❌ Sirf video/document/audio files accept hain.</b>",
            parse_mode=enums.ParseMode.HTML
        )

    wait = await reply.reply(
        "⏳ <b>File main library mein add ho rahi hai...</b>",
        parse_mode=enums.ParseMode.HTML
    )

    caption = reply.caption or f"📁 {getattr(media, 'file_name', 'Unknown')}"
    saved = await add_to_channel(media.file_id, caption)

    if saved:
        fname = saved.get('file_name', 'Unknown')
        fsize = get_size(saved.get('file_size', 0))
        await wait.edit_text(
            f"<b>✅ File Add Ho Gayi!</b>\n\n"
            f"📁 Name: <code>{fname}</code>\n"
            f"📦 Size: {fsize}\n\n"
            f"Ab sabhi users is movie ko search se dhundh sakte hain!",
            parse_mode=enums.ParseMode.HTML
        )
        # Log channel notify
        try:
            owner_id = message.from_user.id
            bot_uname = me.username
            await temp.BOT.send_message(
                LOG_CHANNEL,
                f"<b>📁 New File Added via Clone</b>\n\n"
                f"Clone: @{bot_uname}\n"
                f"Owner: <code>{owner_id}</code>\n"
                f"File: {fname}"
            )
        except:
            pass
    else:
        await wait.edit_text(
            "<b>❌ File add nahi hui.</b>\n\n"
            "MAIN_MOVIE_CHANNEL check karo ya main bot admin se contact karo.",
            parse_mode=enums.ParseMode.HTML
        )


# ── /myfiles — Clone owner ki added files dekho ─────────────
@Client.on_message(filters.command("myfiles") & filters.incoming)
async def myfiles_cmd(client, message: Message):
    if not await _is_owner(client, message.from_user.id):
        return await message.reply(
            "<b>❌ Sirf bot owner!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    await message.reply(
        "<b>📚 Library ke baare mein:</b>\n\n"
        "Saari movies ek shared library mein hain.\n"
        "Aapke /addnew se dali files bhi wahan hain.\n\n"
        "Movie search karo group mein ya PM mein.",
        parse_mode=enums.ParseMode.HTML
    )
