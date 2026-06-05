# Clone Subscription Expiry Reminder
# 2 din pehle notify karta hai - "Plan Lo" button ke saath main bot link
import asyncio, datetime, logging
from pyrogram import Client
from database.subscription_db import get_expiring_soon_subs, sub_col
from database.users_chats_db import db
from info import LOG_CHANNEL
from utils import temp

logger = logging.getLogger(__name__)

MAIN_BOT_USERNAME = "AsFilterBot"  # Change this to your main factory bot username

async def notify_expiring_clones(client):
    """2 din mein expire hone wale clone bots ke owners ko notify karo"""
    try:
        expiring = await get_expiring_soon_subs(days=2)
        for sub in expiring:
            owner_id  = sub.get("owner_id")
            bot_uname = sub.get("bot_username","?")
            expiry    = sub.get("expiry", datetime.datetime.now())
            days_left = max(0, (expiry - datetime.datetime.now()).days)

            # Already notified check
            if sub.get("expiry_notified"):
                continue

            try:
                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                from pyrogram import enums
                msg = (
                    f"⚠️ <b>@{bot_uname} ka time khatam hone wala hai!</b>\n\n"
                    f"⏰ Sirf <b>{days_left} din</b> bache hain\n"
                    f"📅 Expiry: {expiry.strftime('%d %b %Y')}\n\n"
                    "Bot band hone se pehle plan lo — service jaari rahegi!"
                )
                btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("💎 Plan Lo", url=f"https://t.me/{MAIN_BOT_USERNAME}?start=mybots")
                ]])
                await client.send_message(owner_id, msg, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
                # Mark notified
                await sub_col.update_one(
                    {"bot_id": sub["bot_id"]},
                    {"$set": {"expiry_notified": True}}
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Expiry notify error {owner_id}: {e}")
    except Exception as e:
        logger.error(f"notify_expiring_clones error: {e}")


_RUNNING = False

async def clone_expiry_loop(client):
    global _RUNNING
    if _RUNNING:
        return
    _RUNNING = True
    logger.info("Clone expiry reminder loop started ✓")
    while True:
        await notify_expiring_clones(client)
        await asyncio.sleep(3600 * 12)  # Har 12 ghante


_STARTED = False
async def start_expiry_check(client):
    global _STARTED
    if not _STARTED:
        _STARTED = True
        asyncio.create_task(clone_expiry_loop(client))
