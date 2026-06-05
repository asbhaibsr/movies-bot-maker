# 🏭 Clone Factory — Main Bot Ka Naya Core
# Sirf ye kaam karta hai:
# 1. Clone bot banana
# 2. Subscription manage karna
# 3. /botbroadcast
# 4. My Bots dashboard

import re, asyncio, datetime, logging
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery
)
from database.users_chats_db import db
from database.subscription_db import (
    create_subscription, get_subscription, is_active,
    extend_subscription, deactivate_subscription,
    get_all_subscriptions, get_expiring_soon_subs,
    get_owner_bots, days_remaining, PLANS, FREE_TRIAL_DAYS
)
from info import (
    API_ID, API_HASH, ADMINS, LOG_CHANNEL,
    CLONE_MODE, SUPPORT_CHAT
)
from utils import temp

logger = logging.getLogger(__name__)

# Payment UPI (change as needed)
PAYMENT_UPI  = "your_upi@bank"
PAYMENT_NAME = "As Bhai BSR"

# Pending payment requests {owner_id: {bot_id, months, amount}}
_PENDING_PAY = {}

# ── Agreed users (legal disclaimer) ────────────────────────────
_AGREED = set()


# ═══════════════════════════════════════════════════════════════
#   MAIN START — Naya Simple UI
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("start") & filters.private, group=-2)
async def factory_start(client, message: Message):
    """Main bot ka naya start — sirf factory"""
    user_id = message.from_user.id
    args    = message.command

    # Handle deeplinks from other places
    if len(args) > 1:
        return  # Let other handlers (commands.py) handle deeplinks

    # Pehli baar legal disclaimer
    if user_id not in _AGREED:
        await _show_disclaimer(message)
        return

    await _show_main_menu(client, message)


async def _show_disclaimer(message: Message):
    text = (
        "⚠️ <b>Zaruri Notice — Pehle Padho!</b>\n\n"
        "Ye <b>Movie Bot Factory</b> hai — tumhara khud ka movie bot banao.\n\n"
        "<b>Kya allowed hai:</b>\n"
        "✅ Legal movies/series jinka tumhare paas rights ho\n"
        "✅ Public domain content\n"
        "✅ Apne banaye content\n\n"
        "<b>Kya ALLOWED NAHI:</b>\n"
        "❌ Pirated/copyright content\n"
        "❌ Illegal material\n"
        "❌ Rules todne pe bot BAND ho jayega\n\n"
        "Neeche <b>Agree</b> dabao continue karne ke liye:"
    )
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Agree & Continue", callback_data="factory_agree"),
        InlineKeyboardButton("❌ Cancel",            callback_data="factory_cancel"),
    ]])
    await message.reply_text(text, reply_markup=btn, parse_mode=enums.ParseMode.HTML)


async def _show_main_menu(client, message_or_query):
    """Main factory menu"""
    if isinstance(message_or_query, CallbackQuery):
        user = message_or_query.from_user
    else:
        user = message_or_query.from_user

    text = (
        f"👋 <b>Welcome, {user.first_name}!</b>\n\n"
        "🎬 <b>Movie Bot Factory</b>\n\n"
        "Apna khud ka Movie Bot banao — bilkul <b>FREE!</b>\n"
        f"• Pehle {FREE_TRIAL_DAYS} din free trial\n"
        "• Baad mein sirf ₹150/month\n\n"
        "Neeche se choose karo:"
    )
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Movie Bot Banao",      callback_data="factory_create")],
        [InlineKeyboardButton("📱 Mere Bots",             callback_data="factory_mybots")],
        [InlineKeyboardButton("❓ Help & Support",        url=f"https://t.me/{SUPPORT_CHAT}")],
    ])
    try:
        if isinstance(message_or_query, CallbackQuery):
            await message_or_query.message.edit_text(text, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
        else:
            await message_or_query.reply_text(text, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass


# ── Callbacks ───────────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^factory_agree$"))
async def factory_agree_cb(client, query: CallbackQuery):
    _AGREED.add(query.from_user.id)
    await query.answer("✅ Agree kar liya!")
    await _show_main_menu(client, query)


@Client.on_callback_query(filters.regex("^factory_cancel$"))
async def factory_cancel_cb(client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        "<b>Cancel kar diya. Jab ready ho /start karo.</b>",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^factory_create$"))
async def factory_create_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    _AGREED.add(user_id)

    # Already clone hai?
    if await db.is_clone_exist(user_id):
        clone_data = await db.get_clone(user_id)
        active = await is_active(clone_data.get("bot_id", 0))
        bot_username = clone_data.get("bot_username", "Unknown")
        days = await days_remaining(clone_data.get("bot_id", 0))
        status = f"✅ Active ({days} din bacha)" if active else "❌ Expired"
        await query.answer()
        await query.message.edit_text(
            f"<b>Tumhara bot already hai:</b> @{bot_username}\n"
            f"<b>Status:</b> {status}\n\n"
            "Pehle purana delete karo: /deleteclone",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🗑 Delete Clone",  callback_data="factory_delete"),
                InlineKeyboardButton("🏠 Menu",          callback_data="factory_menu"),
            ]]),
            parse_mode=enums.ParseMode.HTML
        )
        return

    await query.answer()
    await query.message.edit_text(
        "<b>🤖 Movie Bot Banane Ke Steps:</b>\n\n"
        "1️⃣ @BotFather pe jao\n"
        "2️⃣ <code>/newbot</code> send karo\n"
        "3️⃣ Bot ka naam likho\n"
        "4️⃣ Bot ka username likho\n"
        "5️⃣ Token milega — wo message <b>forward karo mujhe</b>\n\n"
        "⏱ <i>2 minute mein ho jayega!</i>\n\n"
        "/cancel — band karo",
        parse_mode=enums.ParseMode.HTML
    )
    # Wait for token
    try:
        resp = await client.listen(query.from_user.id, timeout=300)
        if resp.text and resp.text.strip() == "/cancel":
            return await resp.reply_text("<b>Cancel kar diya ✅</b>", parse_mode=enums.ParseMode.HTML)

        # Extract token
        bot_token = None
        if resp.forward_from and resp.forward_from.id == 93372553:
            matches = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", resp.text)
            if matches:
                bot_token = matches[0]
        else:
            matches = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", resp.text or "")
            if matches:
                bot_token = matches[0]

        if not bot_token:
            return await resp.reply_text(
                "<b>❌ Token nahi mila!</b>\nBotFather se forward karo ya directly paste karo.",
                parse_mode=enums.ParseMode.HTML
            )

        msg = await resp.reply_text("<b>⏳ Bot ban raha hai... thoda ruko!</b>", parse_mode=enums.ParseMode.HTML)

        # Start clone bot
        try:
            vj = Client(
                f"clone_{bot_token[:8]}",
                API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "AsBhai"},
                in_memory=True
            )
            await vj.start()
            bot_info = await vj.get_me()

            # Save to DB
            await db.add_clone_bot(bot_info.id, user_id, bot_token)
            await db.update_bot(bot_info.id, {"bot_username": bot_info.username})

            # Create subscription (1 month free)
            await create_subscription(bot_info.id, user_id, bot_info.username)

            expiry = datetime.datetime.now() + datetime.timedelta(days=FREE_TRIAL_DAYS)
            exp_str = expiry.strftime("%d %b %Y")

            await msg.edit_text(
                f"<b>🎉 Bot ban gaya!</b>\n\n"
                f"🤖 <b>Bot:</b> @{bot_info.username}\n"
                f"🆓 <b>Free Trial:</b> {FREE_TRIAL_DAYS} din\n"
                f"📅 <b>Expiry:</b> {exp_str}\n\n"
                "<b>Setup karo:</b>\n"
                "1. Apna file channel banao\n"
                "2. Bot ko us channel mein admin banao\n"
                "3. <code>/index channel_id</code> chala ke files add karo\n"
                "4. Bot ko group mein add karo\n\n"
                "<i>Settings ke liye apne bot mein /settings likho</i>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"🤖 @{bot_info.username} Open", url=f"https://t.me/{bot_info.username}"),
                    InlineKeyboardButton("📱 Mere Bots", callback_data="factory_mybots"),
                ]]),
                parse_mode=enums.ParseMode.HTML
            )

            # Log
            await client.send_message(
                LOG_CHANNEL,
                f"🤖 <b>#NewClone</b>\n"
                f"👤 Owner: {resp.from_user.mention} (<code>{user_id}</code>)\n"
                f"🤖 Bot: @{bot_info.username}\n"
                f"📅 Free till: {exp_str}",
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:
            await msg.edit_text(
                f"<b>❌ Error:</b>\n<code>{e}</code>\n\n"
                "Token galat hai ya bot already chal raha hai.\n"
                "Help ke liye: @aschat_group",
                parse_mode=enums.ParseMode.HTML
            )

    except asyncio.TimeoutError:
        await query.message.reply_text(
            "<b>⏰ Timeout! 5 minute mein token nahi aaya.</b>\nDobara try karo.",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Clone create error: {e}")


@Client.on_callback_query(filters.regex("^factory_mybots$"))
async def factory_mybots_cb(client, query: CallbackQuery):
    user_id  = query.from_user.id
    _AGREED.add(user_id)
    await query.answer()

    bots = await get_owner_bots(user_id)

    if not bots:
        return await query.message.edit_text(
            "<b>📱 Tumhara koi bot nahi hai abhi!</b>\n\n"
            "Pehla bot banao:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🤖 Bot Banao", callback_data="factory_create"),
                InlineKeyboardButton("🏠 Menu",      callback_data="factory_menu"),
            ]]),
            parse_mode=enums.ParseMode.HTML
        )

    lines = [f"<b>📱 Tere Bots ({len(bots)}):</b>\n"]
    btns  = []
    for b in bots:
        bot_id  = b.get("bot_id")
        uname   = b.get("bot_username", "Unknown")
        active  = await is_active(bot_id)
        days    = await days_remaining(bot_id)
        is_free = b.get("is_free", True)
        exp     = b.get("expiry")
        exp_str = exp.strftime("%d %b %Y") if exp else "?"

        if active:
            status = f"✅ {days}d remaining" + (" (Free)" if is_free else "")
        else:
            status = "❌ Expired — Renew karo"

        lines.append(f"🤖 @{uname}\n   {status} | Expiry: {exp_str}")
        btns.append([
            InlineKeyboardButton(f"@{uname} — Manage", callback_data=f"fmanage#{bot_id}"),
        ])

    btns.append([
        InlineKeyboardButton("🏠 Menu", callback_data="factory_menu"),
    ])

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^fmanage#"))
async def factory_manage_bot_cb(client, query: CallbackQuery):
    bot_id = int(query.data.split("#")[1])
    user_id = query.from_user.id

    sub = await get_subscription(bot_id)
    if not sub or sub.get("owner_id") != user_id:
        return await query.answer("Ye tumhara bot nahi hai!", show_alert=True)

    active  = await is_active(bot_id)
    days    = await days_remaining(bot_id)
    uname   = sub.get("bot_username", "Unknown")
    is_free = sub.get("is_free", True)
    exp     = sub.get("expiry")
    exp_str = exp.strftime("%d %b %Y %H:%M") if exp else "?"

    if active:
        status_txt = f"✅ Active — {days} din bacha\n"
        if is_free:
            status_txt += f"🆓 Free Trial ({FREE_TRIAL_DAYS} din)\n"
        status_txt += f"📅 Expiry: {exp_str}"
    else:
        status_txt = "❌ Subscription Expired!\nBot band ho gaya."

    text = (
        f"<b>🤖 @{uname}</b>\n\n"
        f"{status_txt}"
    )

    btns = []
    if not active or days <= 7:
        btns.append([InlineKeyboardButton("💳 Renew/Pay", callback_data=f"fpay#{bot_id}")])
    btns.append([
        InlineKeyboardButton(f"🤖 Open @{uname}", url=f"https://t.me/{uname}"),
    ])
    btns.append([
        InlineKeyboardButton("🗑 Delete Bot",   callback_data=f"fdelete#{bot_id}"),
        InlineKeyboardButton("◀️ Back",         callback_data="factory_mybots"),
    ])

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    await query.answer()


@Client.on_callback_query(filters.regex(r"^fpay#"))
async def factory_pay_cb(client, query: CallbackQuery):
    bot_id  = int(query.data.split("#")[1])
    user_id = query.from_user.id

    sub = await get_subscription(bot_id)
    if not sub or sub.get("owner_id") != user_id:
        return await query.answer("Ye tumhara bot nahi!", show_alert=True)

    uname = sub.get("bot_username", "Unknown")
    plan_btns = []
    for k, v in PLANS.items():
        plan_btns.append([
            InlineKeyboardButton(f"✅ {v['label']}", callback_data=f"fplan#{bot_id}#{k}")
        ])
    plan_btns.append([InlineKeyboardButton("◀️ Back", callback_data=f"fmanage#{bot_id}")])

    await query.message.edit_text(
        f"<b>💳 @{uname} ke liye plan choose karo:</b>",
        reply_markup=InlineKeyboardMarkup(plan_btns),
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^fplan#"))
async def factory_plan_cb(client, query: CallbackQuery):
    _, bot_id_s, plan_s = query.data.split("#")
    bot_id  = int(bot_id_s)
    plan_id = int(plan_s)
    user_id = query.from_user.id

    sub  = await get_subscription(bot_id)
    plan = PLANS.get(plan_id)
    if not sub or not plan:
        return await query.answer("Error!", show_alert=True)

    uname  = sub.get("bot_username", "Unknown")
    amount = plan["price"]
    months = plan["months"]

    # Save pending payment
    _PENDING_PAY[user_id] = {"bot_id": bot_id, "months": months, "amount": amount, "bot_username": uname}

    text = (
        f"<b>💸 Payment Details</b>\n\n"
        f"🤖 Bot: @{uname}\n"
        f"📦 Plan: {plan['label']}\n"
        f"💰 Amount: <b>₹{amount}</b>\n\n"
        f"<b>UPI:</b> <code>{PAYMENT_UPI}</code>\n"
        f"<b>Name:</b> {PAYMENT_NAME}\n\n"
        "Payment karne ke baad <b>screenshot bhejo is bot pe</b>.\n"
        "Admin 1-12 ghante mein activate kar dega.\n\n"
        "Screenshot bhejo 👇"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data=f"fmanage#{bot_id}")
        ]]),
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer()


@Client.on_message(filters.private & filters.photo & filters.incoming)
async def payment_screenshot_handler(client, message: Message):
    """User payment screenshot bheje"""
    user_id = message.from_user.id
    if user_id not in _PENDING_PAY:
        return
    pending = _PENDING_PAY[user_id]
    bot_id  = pending["bot_id"]
    months  = pending["months"]
    amount  = pending["amount"]
    uname   = pending["bot_username"]

    # Forward to admin/log channel
    caption = (
        f"💳 <b>#PaymentRequest</b>\n\n"
        f"👤 User: {message.from_user.mention} (<code>{user_id}</code>)\n"
        f"🤖 Bot: @{uname} (<code>{bot_id}</code>)\n"
        f"📦 Plan: {months} month(s)\n"
        f"💰 Amount: ₹{amount}\n\n"
        f"Activate karne ke liye:\n"
        f"<code>/activate {bot_id} {months}</code>"
    )
    try:
        await client.send_photo(LOG_CHANNEL, message.photo.file_id, caption=caption, parse_mode=enums.ParseMode.HTML)
    except Exception:
        await client.send_message(LOG_CHANNEL, caption, parse_mode=enums.ParseMode.HTML)

    await message.reply_text(
        "<b>✅ Screenshot mil gaya!</b>\n\n"
        "Admin 1-12 ghante mein activate kar dega.\n"
        "Koi problem ho to: @aschat_group",
        parse_mode=enums.ParseMode.HTML
    )
    del _PENDING_PAY[user_id]


@Client.on_callback_query(filters.regex(r"^fdelete#"))
async def factory_delete_cb(client, query: CallbackQuery):
    bot_id  = int(query.data.split("#")[1])
    user_id = query.from_user.id
    sub = await get_subscription(bot_id)
    if not sub or sub.get("owner_id") != user_id:
        return await query.answer("Ye tumhara bot nahi!", show_alert=True)

    await query.message.edit_text(
        "<b>⚠️ Confirm karo — Bot delete ho jayega!</b>\n\nYe action undo nahi ho sakta.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Haan Delete Karo", callback_data=f"fdelconfirm#{bot_id}"),
            InlineKeyboardButton("❌ Cancel",            callback_data=f"fmanage#{bot_id}"),
        ]]),
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^fdelconfirm#"))
async def factory_delete_confirm_cb(client, query: CallbackQuery):
    bot_id  = int(query.data.split("#")[1])
    user_id = query.from_user.id
    await db.delete_clone(user_id)
    await deactivate_subscription(bot_id)
    await query.message.edit_text(
        "<b>✅ Bot delete ho gaya!</b>\nNaya bot banao: /start",
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer("Deleted!")


@Client.on_callback_query(filters.regex("^factory_menu$"))
async def factory_menu_cb(client, query: CallbackQuery):
    _AGREED.add(query.from_user.id)
    await query.answer()
    await _show_main_menu(client, query)


@Client.on_callback_query(filters.regex("^factory_delete$"))
async def factory_delete_shortcut(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Koi bot nahi!", show_alert=True)
    bot_id = clone.get("bot_id", 0)
    await query.message.edit_text(
        "<b>⚠️ Confirm — Delete karo?</b>",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Delete",  callback_data=f"fdelconfirm#{bot_id}"),
            InlineKeyboardButton("❌ Cancel",  callback_data="factory_mybots"),
        ]]),
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
#   ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("activate") & filters.user(ADMINS))
async def activate_subscription(client, message: Message):
    """
    /activate bot_id months
    Example: /activate 123456789 3
    """
    args = message.command
    if len(args) != 3:
        return await message.reply_text(
            "<b>Usage:</b> <code>/activate bot_id months</code>",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        bot_id = int(args[1])
        months = int(args[2])
    except ValueError:
        return await message.reply_text("<b>❌ Galat format!</b>", parse_mode=enums.ParseMode.HTML)

    new_expiry = await extend_subscription(bot_id, months, message.from_user.id)
    if not new_expiry:
        return await message.reply_text(
            f"<b>❌ Bot {bot_id} not found in DB!</b>",
            parse_mode=enums.ParseMode.HTML
        )

    exp_str = new_expiry.strftime("%d %b %Y")
    sub = await get_subscription(bot_id)
    uname = sub.get("bot_username", "Unknown") if sub else "Unknown"
    owner_id = sub.get("owner_id") if sub else None

    await message.reply_text(
        f"<b>✅ Activated!</b>\n\n"
        f"🤖 @{uname}\n"
        f"📦 {months} month(s) added\n"
        f"📅 New expiry: {exp_str}",
        parse_mode=enums.ParseMode.HTML
    )

    # Notify owner
    if owner_id:
        try:
            await client.send_message(
                owner_id,
                f"<b>✅ Bot Activate Ho Gaya!</b>\n\n"
                f"🤖 @{uname}\n"
                f"📦 Plan: {months} month(s)\n"
                f"📅 Valid till: {exp_str}\n\n"
                "Enjoy karo! 🎬",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass


@Client.on_message(filters.command("sublist") & filters.user(ADMINS))
async def sub_list_cmd(client, message: Message):
    """All subscriptions dekho"""
    subs = await get_all_subscriptions()
    if not subs:
        return await message.reply_text("<b>Koi subscription nahi!</b>", parse_mode=enums.ParseMode.HTML)

    now = datetime.datetime.now()
    active_count   = sum(1 for s in subs if s.get("expiry", now) > now)
    expired_count  = len(subs) - active_count

    lines = [f"<b>📊 All Subscriptions ({len(subs)} total)</b>\n"
             f"✅ Active: {active_count} | ❌ Expired: {expired_count}\n\n"]

    for s in subs[:30]:
        uname  = s.get("bot_username", "?")
        exp    = s.get("expiry", now)
        active = exp > now
        days   = max(0, (exp - now).days)
        status = f"✅ {days}d" if active else "❌ Exp"
        lines.append(f"@{uname} — {status}")

    if len(subs) > 30:
        lines.append(f"\n<i>...aur {len(subs)-30} bots</i>")

    await message.reply_text("\n".join(lines), parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("expiringbots") & filters.user(ADMINS))
async def expiring_bots_cmd(client, message: Message):
    """Next 3 din mein expire hone wale bots"""
    subs = await get_expiring_soon_subs(days=3)
    if not subs:
        return await message.reply_text("<b>✅ Koi bot expire nahi hone wala 3 din mein!</b>", parse_mode=enums.ParseMode.HTML)

    now = datetime.datetime.now()
    lines = [f"<b>⚠️ {len(subs)} bots expire hone wale hain:</b>\n"]
    for s in subs:
        uname    = s.get("bot_username", "?")
        owner_id = s.get("owner_id", "?")
        exp      = s.get("expiry", now)
        days     = max(0, (exp - now).days)
        lines.append(f"@{uname} | Owner: <code>{owner_id}</code> | {days}d baca")

    await message.reply_text("\n".join(lines), parse_mode=enums.ParseMode.HTML)
