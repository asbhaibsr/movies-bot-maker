# ════════════════════════════════════════════════════════════
#  Admin Commands for Main Bot
#  /activate /sublist /expiringbots /expirycheck /logs
# ════════════════════════════════════════════════════════════

import logging, datetime, asyncio, os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.users_chats_db import db
from database.subscription_db import (
    extend_subscription, get_all_subscriptions, get_expiring_soon_subs,
    deactivate_subscription, sub_col
)
from info import ADMINS, LOG_CHANNEL
from utils import temp

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
#  /activate bot_id months
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("activate") & filters.user(ADMINS))
async def activate_cmd(client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.reply(
            "<b>Usage:</b> <code>/activate bot_id months</code>\n\n"
            "Example: <code>/activate 123456789 3</code>",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        bot_id = int(args[1])
        months = int(args[2])
    except ValueError:
        return await message.reply("❌ bot_id aur months numbers hone chahiye.")

    new_expiry = await extend_subscription(bot_id, months, message.from_user.id)
    if not new_expiry:
        return await message.reply(f"❌ Bot <code>{bot_id}</code> ka subscription record nahi mila.", parse_mode=enums.ParseMode.HTML)

    exp_str = new_expiry.strftime("%d %b %Y")
    await message.reply(
        f"<b>✅ Subscription Activate!</b>\n\n"
        f"🤖 Bot ID: <code>{bot_id}</code>\n"
        f"📅 New Expiry: <b>{exp_str}</b>\n"
        f"📦 Extended by: {months} month(s)",
        parse_mode=enums.ParseMode.HTML
    )
    # Bot owner ko notify karo
    try:
        bot_data = await db.get_bot(bot_id)
        owner_id = bot_data.get("user_id") if bot_data else None
        if owner_id:
            await client.send_message(
                owner_id,
                f"<b>🎉 Aapka bot subscription activate ho gaya!</b>\n\n"
                f"🤖 Bot ID: <code>{bot_id}</code>\n"
                f"📅 Expiry: <b>{exp_str}</b>\n"
                f"📦 {months} month(s) ke liye",
                parse_mode=enums.ParseMode.HTML
            )
    except:
        pass


# ═══════════════════════════════════════════════
#  /sublist — Saare active subscriptions
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("sublist") & filters.user(ADMINS))
async def sublist_cmd(client, message: Message):
    subs = await get_all_subscriptions()
    if not subs:
        return await message.reply("<b>📭 Koi subscription nahi hai abhi.</b>", parse_mode=enums.ParseMode.HTML)

    lines = [f"<b>📋 Total Subscriptions: {len(subs)}</b>\n"]
    now = datetime.datetime.now()
    active_count = 0
    for sub in subs:
        bot_uname = sub.get("bot_username", "?")
        expiry    = sub.get("expiry")
        is_active = sub.get("is_active", False)
        is_free   = sub.get("is_free", True)
        days_left = max(0, (expiry - now).days) if expiry else 0
        exp_str   = expiry.strftime("%d %b %Y") if expiry else "?"
        status    = "✅" if is_active and days_left > 0 else "❌"
        plan      = "Free" if is_free else "Paid"
        active_count += 1 if (is_active and days_left > 0) else 0
        lines.append(f"{status} @{bot_uname} | {plan} | {days_left}d | {exp_str}")

    lines.append(f"\n<b>Active: {active_count}/{len(subs)}</b>")
    # Long message — split if needed
    full_text = "\n".join(lines)
    if len(full_text) > 4000:
        # Send in chunks
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) > 4000:
                await message.reply(chunk, parse_mode=enums.ParseMode.HTML)
                chunk = ""
            chunk += line + "\n"
        if chunk:
            await message.reply(chunk, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply(full_text, parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════
#  /expiringbots — Jaldi expire hone wale bots
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("expiringbots") & filters.user(ADMINS))
async def expiringbots_cmd(client, message: Message):
    expiring = await get_expiring_soon_subs(days=7)
    if not expiring:
        return await message.reply(
            "<b>✅ Koi bot agle 7 din mein expire nahi ho raha!</b>",
            parse_mode=enums.ParseMode.HTML
        )

    lines = [f"<b>⚠️ {len(expiring)} bots agle 7 din mein expire honge:</b>\n"]
    now = datetime.datetime.now()
    for sub in expiring:
        bot_uname = sub.get("bot_username", "?")
        bot_id    = sub.get("bot_id", "?")
        expiry    = sub.get("expiry")
        days_left = max(0, (expiry - now).days) if expiry else 0
        exp_str   = expiry.strftime("%d %b %Y") if expiry else "?"
        notified  = "✅" if sub.get("expiry_notified") else "❌"
        lines.append(
            f"• @{bot_uname} (<code>{bot_id}</code>)\n"
            f"  Expire: {exp_str} | {days_left}d left | Notified: {notified}"
        )

    await message.reply(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📨 Notify Karo", callback_data="admin_notify_expiring")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_notify_expiring$"))
async def admin_notify_cb(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("Sirf Admin!", show_alert=True)
    await query.answer("📨 Notifications bhej rahe hain...", show_alert=True)

    expiring = await get_expiring_soon_subs(days=7)
    sent = 0
    now = datetime.datetime.now()
    for sub in expiring:
        if sub.get("expiry_notified"):
            continue
        owner_id  = sub.get("owner_id")
        bot_uname = sub.get("bot_username", "?")
        expiry    = sub.get("expiry", now)
        days_left = max(0, (expiry - now).days)
        exp_str   = expiry.strftime("%d %b %Y")
        try:
            await client.send_message(
                owner_id,
                f"⚠️ <b>@{bot_uname} ka plan expire hone wala hai!</b>\n\n"
                f"⏰ Sirf <b>{days_left} din</b> bache hain\n"
                f"📅 Expiry: {exp_str}\n\n"
                f"Renew karo: @aschat_group",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 Support", url="https://t.me/aschat_group")]
                ]),
                parse_mode=enums.ParseMode.HTML
            )
            await sub_col.update_one(
                {"bot_id": sub["bot_id"]},
                {"$set": {"expiry_notified": True}}
            )
            sent += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.error(f"Notify error {owner_id}: {e}")

    try:
        await query.message.edit_text(
            f"<b>✅ {sent} owners ko notify kar diya!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except:
        pass


# ═══════════════════════════════════════════════
#  /expirycheck — Sab subscriptions ka status
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("expirycheck") & filters.user(ADMINS))
async def expirycheck_cmd(client, message: Message):
    subs = await get_all_subscriptions()
    now = datetime.datetime.now()
    active = expired = expiring = 0

    for sub in subs:
        expiry = sub.get("expiry")
        if not expiry or not sub.get("is_active"):
            expired += 1
            continue
        days_left = (expiry - now).days
        if days_left <= 0:
            expired += 1
        elif days_left <= 3:
            expiring += 1
        else:
            active += 1

    text = (
        f"<b>📊 Subscription Status Report</b>\n\n"
        f"Total Bots: {len(subs)}\n"
        f"✅ Active: {active}\n"
        f"⚠️ Expiring (3 din): {expiring}\n"
        f"❌ Expired: {expired}\n\n"
        f"<i>Check time: {now.strftime('%d %b %Y %H:%M')}</i>"
    )
    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚠️ Expiring Bots Dekho", callback_data="admin_show_expiring_7")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════
#  /logs — Platform logs
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def logs_cmd(client, message: Message):
    log_file = "logs.txt"  # logging.conf mein jo file set hai
    if os.path.exists(log_file):
        try:
            await client.send_document(
                message.chat.id,
                log_file,
                caption="<b>📋 Bot Logs</b>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            await message.reply(f"❌ Log file bhej nahi saka: {e}")
    else:
        # Aiohttp / console se recent lines try karo
        lines = []
        try:
            import logging
            # Get all handlers and read from file handler if available
            root = logging.getLogger()
            for handler in root.handlers:
                if hasattr(handler, 'baseFilename'):
                    with open(handler.baseFilename, 'r') as f:
                        lines = f.readlines()[-100:]
                    break
        except:
            pass

        if lines:
            log_text = "".join(lines[-80:])
            if len(log_text) > 3900:
                log_text = log_text[-3900:]
            await message.reply(
                f"<b>📋 Recent Logs:</b>\n<pre>{log_text}</pre>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            total_bots = await db.count_all_bots()
            running = len(getattr(temp, "BOTS", []))
            await message.reply(
                f"<b>📊 Bot Status:</b>\n\n"
                f"🤖 Total Clone Bots (DB): {total_bots}\n"
                f"▶️ Currently Running: {running}\n\n"
                f"<i>Log file nahi mili. Console logs dekhne ke liye hosting platform use karo.</i>",
                parse_mode=enums.ParseMode.HTML
            )


# ═══════════════════════════════════════════════
#  Admin Management Commands (Dynamic Admins)
# ═══════════════════════════════════════════════

@Client.on_message(filters.command("adminslist") & filters.user(ADMINS))
async def adminslist_cmd(client, message: Message):
    """Saare admins ki list — env + dynamic"""
    env_admins = ADMINS
    dyn_docs = await db.get_all_dynamic_admins_info()

    lines = ["<b>👑 Admins List</b>\n"]
    lines.append(f"<b>🔒 Env Admins ({len(env_admins)}):</b>")
    for aid in env_admins:
        try:
            u = await client.get_users(aid)
            uname = f"@{u.username}" if u.username else u.first_name
        except:
            uname = "Unknown"
        lines.append(f"  • <code>{aid}</code> — {uname}")

    if dyn_docs:
        lines.append(f"\n<b>➕ Dynamic Admins ({len(dyn_docs)}):</b>")
        for doc in dyn_docs:
            uname = f"@{doc['username']}" if doc.get("username") else "No username"
            lines.append(f"  • <code>{doc['user_id']}</code> — {uname}")
    else:
        lines.append("\n<i>Koi dynamic admin nahi.</i>")

    await message.reply(
        "\n".join(lines),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("addadmin") & filters.user(ADMINS))
async def addadmin_cmd(client, message: Message):
    """Dynamic admin add karo — /addadmin user_id"""
    args = message.command
    if len(args) < 2:
        return await message.reply(
            "<b>Usage:</b> <code>/addadmin user_id</code>\n\n"
            "Example: <code>/addadmin 123456789</code>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        new_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Sirf numeric ID bhejo.")

    if new_id in ADMINS:
        return await message.reply(
            f"<b>ℹ️ {new_id} pehle se Env Admin hai!</b>",
            parse_mode=enums.ParseMode.HTML
        )

    username = ""
    name_str = f"<code>{new_id}</code>"
    try:
        u = await client.get_users(new_id)
        username = u.username or ""
        name_str = u.mention
    except:
        pass

    await db.add_dynamic_admin(new_id, username)

    await message.reply(
        f"<b>✅ Admin Add Ho Gaya!</b>\n\n"
        f"👤 User: {name_str}\n"
        f"🆔 ID: <code>{new_id}</code>\n\n"
        f"Ab ye user Admin Panel access kar sakta hai.",
        parse_mode=enums.ParseMode.HTML
    )
    try:
        await client.send_message(
            LOG_CHANNEL,
            f"<b>➕ Admin Added\nID: <code>{new_id}</code>\nBy: {message.from_user.mention}</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except:
        pass


@Client.on_message(filters.command("removeadmin") & filters.user(ADMINS))
async def removeadmin_cmd(client, message: Message):
    """Dynamic admin remove karo — /removeadmin user_id"""
    args = message.command
    if len(args) < 2:
        return await message.reply(
            "<b>Usage:</b> <code>/removeadmin user_id</code>\n\n"
            "Example: <code>/removeadmin 123456789</code>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        rem_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Sirf numeric ID bhejo.")

    if rem_id in ADMINS:
        return await message.reply(
            "<b>❌ Env Admin ko yahan se remove nahi kar sakte!</b>\n\n"
            "Env var (ADMINS) se directly ID hatao.",
            parse_mode=enums.ParseMode.HTML
        )

    removed = await db.remove_dynamic_admin(rem_id)
    if removed:
        await message.reply(
            f"<b>✅ Admin Remove Ho Gaya!</b>\n🆔 <code>{rem_id}</code>",
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply(
            f"<b>❌ ID <code>{rem_id}</code> dynamic admins mein nahi mila.</b>",
            parse_mode=enums.ParseMode.HTML
        )
