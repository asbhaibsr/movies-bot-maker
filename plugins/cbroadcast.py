# ════════════════════════════════════════════════════════════
#  /cbroadcast — Main Bot se ALL Clone Bots ke Users ko Broadcast
#  Sirf ADMINS use kar sakte hain
# ════════════════════════════════════════════════════════════

import asyncio, logging
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
)
from info import ADMINS, LOG_CHANNEL
from database.users_chats_db import db
from utils import temp

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("cbroadcast") & filters.user(ADMINS))
async def cbroadcast_cmd(client, message: Message):
    """
    /cbroadcast — Sabhi running clone bots ke through users ko broadcast karo.
    Har clone bot apne registered users ko message bhejta hai.
    """
    clone_bots = getattr(temp, "BOTS", [])
    if not clone_bots:
        return await message.reply(
            "<b>❌ Abhi koi clone bot running nahi hai.</b>\n\n"
            "Clone bots start hone ke baad dobara try karo.",
            parse_mode=enums.ParseMode.HTML
        )

    await message.reply(
        f"<b>📢 Clone Broadcast Setup</b>\n\n"
        f"🤖 Running Clone Bots: <b>{len(clone_bots)}</b>\n\n"
        f"Woh message bhejo jise broadcast karna hai.\n"
        f"<i>(Text, Photo, Video, Document — kuch bhi chalega)</i>\n\n"
        f"👉 Message bhejo ya /cancel karo:",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        bcast_msg = await client.listen(message.from_user.id, timeout=120)
    except asyncio.TimeoutError:
        return await message.reply("⏰ Timeout! Dobara /cbroadcast karo.")

    if bcast_msg.text and bcast_msg.text.strip() in ["/cancel", "/stop"]:
        return await bcast_msg.reply("❌ Broadcast cancel kar diya.")

    # ── Broadcast shuru ──────────────────────────────────────────────
    status_msg = await bcast_msg.reply(
        "<b>📢 Broadcast shuru ho raha hai...</b>\n\n⏳ Please wait...",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        from AsFilterBot.database.clone_bot_userdb import clonedb
        USERDB_OK = True
    except ImportError:
        USERDB_OK = False
        await status_msg.edit_text(
            "❌ clone_bot_userdb import nahi hua. Bot restart karo.",
            parse_mode=enums.ParseMode.HTML
        )
        return

    grand_sent   = 0
    grand_failed = 0
    grand_total  = 0
    bot_lines    = []
    done_bots    = 0

    for clone_client in clone_bots:
        done_bots += 1
        try:
            me        = await clone_client.get_me()
            bot_id    = me.id
            bot_uname = f"@{me.username}" if me.username else str(bot_id)

            user_cursor = await clonedb.get_all_users(bot_id)
            sent = failed = 0

            async for user_doc in user_cursor:
                uid = user_doc.get("user_id")
                if not uid:
                    continue
                try:
                    await bcast_msg.copy(uid)
                    sent += 1
                    await asyncio.sleep(0.05)   # flood avoid
                except Exception:
                    failed += 1

            grand_sent   += sent
            grand_failed += failed
            grand_total  += sent + failed
            bot_lines.append(
                f"✅ {bot_uname}: <b>{sent}</b> sent, <b>{failed}</b> failed"
            )

        except Exception as ex:
            bot_lines.append(f"❌ Bot #{done_bots} error: {ex}")
            logger.error(f"cbroadcast bot error: {ex}")

        # Progress update har 5 bots ke baad
        if done_bots % 5 == 0 or done_bots == len(clone_bots):
            try:
                await status_msg.edit_text(
                    f"<b>📢 Broadcasting... {done_bots}/{len(clone_bots)} bots done</b>\n\n"
                    f"✅ Sent so far: {grand_sent} | ❌ Failed: {grand_failed}",
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                pass

    # ── Final Report ─────────────────────────────────────────────────
    bot_report = "\n".join(bot_lines)
    if len(bot_report) > 3000:
        bot_report = bot_report[:3000] + "\n… [truncated]"

    final_text = (
        f"<b>✅ Clone Broadcast Complete!</b>\n\n"
        f"🤖 Clone Bots: <b>{len(clone_bots)}</b>\n"
        f"👥 Total Users: <b>{grand_total}</b>\n"
        f"📨 Sent: <b>{grand_sent}</b>\n"
        f"❌ Failed: <b>{grand_failed}</b>\n\n"
        f"<b>━━━ Per Bot ━━━</b>\n{bot_report}"
    )
    await status_msg.edit_text(final_text, parse_mode=enums.ParseMode.HTML)

    # Log channel
    try:
        await client.send_message(
            LOG_CHANNEL,
            f"<b>📢 cBroadcast Done\n"
            f"By: {message.from_user.mention}\n"
            f"Bots: {len(clone_bots)} | Sent: {grand_sent} | Failed: {grand_failed}</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        pass


# ── /broadcast_stats — Kitne users hain har clone bot mein ──────────
@Client.on_message(filters.command("bcaststats") & filters.user(ADMINS))
async def bcaststats_cmd(client, message: Message):
    """Har clone bot ke user count dikhao"""
    clone_bots = getattr(temp, "BOTS", [])
    if not clone_bots:
        return await message.reply("❌ Koi clone bot running nahi.")

    try:
        from AsFilterBot.database.clone_bot_userdb import clonedb
    except ImportError:
        return await message.reply("❌ clonedb import error.")

    wait = await message.reply("⏳ Counting users per bot...")
    lines = [f"<b>👥 Clone Bot User Stats</b>\n<i>Total Bots: {len(clone_bots)}</i>\n"]
    grand_total = 0

    for bot_client in clone_bots:
        try:
            me    = await bot_client.get_me()
            count = await clonedb.total_users_count(me.id)
            uname = f"@{me.username}" if me.username else str(me.id)
            grand_total += count
            lines.append(f"🤖 {uname}: <b>{count:,}</b> users")
        except Exception as ex:
            lines.append(f"❌ Error: {ex}")

    lines.append(f"\n<b>Total Users (All Bots): {grand_total:,}</b>")
    await wait.edit_text(
        "\n".join(lines),
        parse_mode=enums.ParseMode.HTML
    )
