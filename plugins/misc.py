# Misc commands — /id /stats /cancel
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS
from utils import temp

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("id") & filters.private)
async def id_cmd(client, message: Message):
    user = message.from_user
    await message.reply(
        f"<b>👤 Your ID:</b> <code>{user.id}</code>\n"
        f"<b>Name:</b> {user.first_name}\n"
        f"<b>Username:</b> @{user.username or 'N/A'}",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_cmd(client, message: Message):
    total_users = await db.total_users_count()
    total_bots  = await db.count_all_bots()
    running     = len(getattr(temp, "BOTS", []))
    await message.reply(
        f"<b>📊 Bot Stats</b>\n\n"
        f"👥 Total Users: {total_users}\n"
        f"🤖 Total Clone Bots: {total_bots}\n"
        f"▶️ Currently Running: {running}",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client, message: Message):
    await message.reply("<b>❌ Process cancel kar diya.</b>", parse_mode=enums.ParseMode.HTML)
