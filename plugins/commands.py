# ════════════════════════════════════════════════════════════
#   Main Bot — BotFather Style Bot Maker
#   Bot: @createautofilterRobot
#   Support: @aschat_group
#   Updates: @asbhai_bsr
# ════════════════════════════════════════════════════════════

import re, asyncio, logging, datetime
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
)
from database.users_chats_db import db
from database.subscription_db import (
    create_subscription, get_subscription, is_active, days_remaining,
    get_owner_bots
)
from info import ADMINS, SUPPORT_CHAT, CHNL_LNK, LOG_CHANNEL
from utils import temp

logger = logging.getLogger(__name__)

UPDATE_CHANNEL = "https://t.me/asbhai_bsr"
SUPPORT_GROUP  = "https://t.me/aschat_group"

# ═══════════════════════════════════════════════
#  /start  — Main welcome
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("start") & filters.private & filters.incoming)
async def start_cmd(client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"<b>👤 New User\nID: <code>{message.from_user.id}</code>\n"
                f"Name: {message.from_user.mention}</b>"
            )
        except:
            pass

    user = message.from_user
    buttons = [
        [InlineKeyboardButton("🤖 Apna Movie Bot Banao", callback_data="create_bot_guide")],
        [
            InlineKeyboardButton("📋 Mere Bots", callback_data="my_bots"),
            InlineKeyboardButton("❓ Help", callback_data="main_help"),
        ],
        [
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP),
            InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL),
        ],
    ]
    text = (
        f"<b>👋 Assalam o Alaikum, {user.mention}!</b>\n\n"
        f"🤖 Main hoon <b>Create AutoFilter Bot</b> — aapka personal\n"
        f"<b>Movie Bot Factory!</b>\n\n"
        f"📌 <b>Main kya kar sakta hoon?</b>\n"
        f"  ✅ Aapka apna Movie Bot banaunga\n"
        f"  ✅ Bot ka welcome message set karein\n"
        f"  ✅ Photo + Custom buttons lagayein\n"
        f"  ✅ Subscription manage karein\n\n"
        f"👇 Shuru karo neeche wale button se:"
    )
    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^create_bot_guide$"))
async def create_bot_guide_cb(client, query: CallbackQuery):
    text = (
        "<b>🤖 Apna Movie Bot Banane Ka Tarika:</b>\n\n"
        "<b>Step 1:</b> @BotFather pe jao\n"
        "<b>Step 2:</b> /newbot command bhejo\n"
        "<b>Step 3:</b> Bot ka naam do\n"
        "<b>Step 4:</b> Bot ka username do\n"
        "<b>Step 5:</b> BotFather wala message yahan forward karo\n\n"
        "👇 Shuru karo:"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Bot Banao (/createbot)", callback_data="start_create")],
            [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^main_help$"))
async def main_help_cb(client, query: CallbackQuery):
    text = (
        "<b>📖 Help Menu</b>\n\n"
        "<b>User Commands:</b>\n"
        "/createbot — Naya movie bot banao\n"
        "/mybot — Apne saare bots dekho\n"
        "/delbot — Koi bot delete karo\n"
        "/manage — Bot settings manage karo\n\n"
        "<b>Bot Features (clone mein):</b>\n"
        "✅ Auto Movie Search\n"
        "✅ IMDB Info\n"
        "✅ File Store\n"
        "✅ Premium Plans\n"
        "✅ Shortlink Verify\n"
        "✅ Group Filters\n"
        "✅ AI Chat\n"
        "✅ Force Subscribe\n\n"
        f"💬 Support: @aschat_group\n"
        f"📢 Updates: @asbhai_bsr"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="go_home")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^go_home$"))
async def go_home_cb(client, query: CallbackQuery):
    user = query.from_user
    buttons = [
        [InlineKeyboardButton("🤖 Apna Movie Bot Banao", callback_data="create_bot_guide")],
        [
            InlineKeyboardButton("📋 Mere Bots", callback_data="my_bots"),
            InlineKeyboardButton("❓ Help", callback_data="main_help"),
        ],
        [
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP),
            InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL),
        ],
    ]
    text = (
        f"<b>👋 Assalam o Alaikum, {user.mention}!</b>\n\n"
        f"🤖 Main hoon <b>Create AutoFilter Bot</b> — aapka personal\n"
        f"<b>Movie Bot Factory!</b>\n\n"
        f"📌 <b>Main kya kar sakta hoon?</b>\n"
        f"  ✅ Aapka apna Movie Bot banaunga\n"
        f"  ✅ Bot ka welcome message set karein\n"
        f"  ✅ Photo + Custom buttons lagayein\n"
        f"  ✅ Subscription manage karein\n\n"
        f"👇 Shuru karo neeche wale button se:"
    )
    try:
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except:
        try:
            await query.message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        except:
            await query.answer()


# ═══════════════════════════════════════════════
#  /createbot  — Bot banane ka process
# ═══════════════════════════════════════════════
@Client.on_message(filters.command(["createbot", "clone"]) & filters.private)
async def createbot_cmd(client, message: Message):
    await _start_createbot(client, message)


@Client.on_callback_query(filters.regex("^start_create$"))
async def start_create_cb(client, query: CallbackQuery):
    # Fake message object se process start karo
    await query.answer()
    await _start_createbot(client, query.message, user=query.from_user)


async def _start_createbot(client, message, user=None):
    if user is None:
        user = message.from_user

    if await db.is_clone_exist(user.id):
        clone = await db.get_clone(user.id)
        bot_uname = clone.get("bot_username", "Unknown")
        await client.send_message(
            user.id,
            f"<b>⚠️ Aapka ek bot already exist karta hai: @{bot_uname}</b>\n\n"
            f"Pehle /delbot se delete karo, phir naya banao.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Bot Delete Karo", callback_data="delbot_menu")],
                [InlineKeyboardButton("⚙️ Bot Manage Karo", callback_data="manage_menu")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        return

    guide_msg = await client.send_message(
        user.id,
        "<b>🤖 Bot Banane Ki Process:</b>\n\n"
        "<b>1️⃣</b> @BotFather pe jao\n"
        "<b>2️⃣</b> /newbot bhejo\n"
        "<b>3️⃣</b> Bot ka naam do (e.g. My Movie Bot)\n"
        "<b>4️⃣</b> Username do (e.g. mymovie_bot)\n"
        "<b>5️⃣</b> BotFather ka <b>confirmation message</b> yahan <b>forward</b> karo\n\n"
        "<i>ya seedha token paste karo</i>\n\n"
        "⏰ 5 minute mein jawab do, /cancel se cancel karo.",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        reply = await client.listen(user.id, timeout=300)
    except asyncio.TimeoutError:
        return await guide_msg.edit_text("<b>⏰ Timeout! Dobara /createbot karo.</b>")

    if reply.text and reply.text.strip() == "/cancel":
        return await reply.reply("<b>❌ Process cancel kar diya.</b>")

    # Token extract karo
    bot_token = None
    if reply.forward_from and reply.forward_from.id == 93372553:
        match = re.search(r"\b(\d+:[A-Za-z0-9_-]+)\b", reply.text or "")
        if match:
            bot_token = match.group(1)
    elif reply.text:
        match = re.search(r"\b(\d+:[A-Za-z0-9_-]+)\b", reply.text)
        if match:
            bot_token = match.group(1)

    if not bot_token:
        return await reply.reply(
            "<b>❌ Token nahi mila!</b>\n\n"
            "BotFather ka message forward karo ya token paste karo.\n"
            "Dobara /createbot karo.",
            parse_mode=enums.ParseMode.HTML
        )

    wait_msg = await reply.reply("⏳ <b>Bot start ho raha hai... 30 sec wait karo</b>", parse_mode=enums.ParseMode.HTML)

    try:
        from info import API_ID, API_HASH
        new_bot = Client(
            f"clone_{bot_token[:8]}",
            API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "AsFilterBot"},
        )
        await new_bot.start()
        bot_me = await new_bot.get_me()

        # DB mein save karo
        await db.add_clone_bot(
            bot_id=bot_me.id,
            user_id=user.id,
            bot_token=bot_token,
            bot_username=bot_me.username or ""
        )
        # Subscription create karo (30 day free trial)
        await create_subscription(bot_me.id, user.id, bot_me.username or "")

        # temp.BOTS mein add karo
        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(new_bot)

        await wait_msg.edit_text(
            f"<b>✅ Bot Successfully Bana Diya!</b>\n\n"
            f"🤖 Bot: @{bot_me.username}\n"
            f"🎁 Free Trial: <b>30 din</b>\n\n"
            f"Ab /manage se apna bot customize karo!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Bot Manage Karo", callback_data="manage_menu")],
                [InlineKeyboardButton("📋 Mere Bots", callback_data="my_bots")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        # Log channel
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"<b>🆕 Naya Clone Bot Bana!\n"
                f"Bot: @{bot_me.username} (<code>{bot_me.id}</code>)\n"
                f"Owner: {user.mention} (<code>{user.id}</code>)</b>"
            )
        except:
            pass

    except Exception as e:
        await wait_msg.edit_text(
            f"<b>❌ Error:</b>\n<code>{e}</code>\n\n"
            f"Token check karo ya @aschat_group mein support lo.",
            parse_mode=enums.ParseMode.HTML
        )


# ═══════════════════════════════════════════════
#  /mybot  — User ke saare bots
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("mybot") & filters.private)
@Client.on_callback_query(filters.regex("^my_bots$"))
async def mybot_cmd(client, update):
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
        send = update.message.edit_text
    else:
        user_id = update.from_user.id
        send = update.reply

    bots = await get_owner_bots(user_id)
    if not bots:
        text = "<b>📭 Aapka koi bot nahi hai.</b>\n\n/createbot se banao!"
        btns = [[InlineKeyboardButton("🤖 Bot Banao", callback_data="start_create")]]
        if isinstance(update, CallbackQuery):
            return await update.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(btns),
                parse_mode=enums.ParseMode.HTML
            )
        return await update.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)

    lines = ["<b>📋 Aapke Bots:</b>\n"]
    buttons = []
    for i, sub in enumerate(bots, 1):
        bot_uname = sub.get("bot_username", "Unknown")
        expiry = sub.get("expiry")
        active = sub.get("is_active", False)
        is_free = sub.get("is_free", True)
        days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
        status = "✅ Active" if active and days_left > 0 else "❌ Expired"
        plan_type = "🎁 Free Trial" if is_free else "💎 Paid"
        lines.append(
            f"<b>{i}.</b> @{bot_uname}\n"
            f"   Status: {status} | {plan_type}\n"
            f"   ⏳ {days_left} din bache\n"
        )
        buttons.append([
            InlineKeyboardButton(f"⚙️ @{bot_uname}", callback_data=f"manage_bot_{bot_uname}")
        ])

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="go_home")])

    kwargs = {
        "text": "\n".join(lines),
        "reply_markup": InlineKeyboardMarkup(buttons),
        "parse_mode": enums.ParseMode.HTML
    }
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(**kwargs)
    else:
        await update.reply(**kwargs)


# ═══════════════════════════════════════════════
#  /delbot  — Bot delete karo
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("delbot") & filters.private)
@Client.on_callback_query(filters.regex("^delbot_menu$"))
async def delbot_cmd(client, update):
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
    else:
        user_id = update.from_user.id

    clone = await db.get_clone(user_id)
    if not clone:
        txt = "<b>❌ Aapka koi bot nahi hai delete karne ke liye.</b>"
        if isinstance(update, CallbackQuery):
            return await update.answer(txt, show_alert=True)
        return await update.reply(txt, parse_mode=enums.ParseMode.HTML)

    bot_uname = clone.get("bot_username", "Unknown")
    text = (
        f"<b>🗑️ Bot Delete Confirmation</b>\n\n"
        f"Bot: @{bot_uname}\n\n"
        f"⚠️ Aap sure hain? Ye bot hamesha ke liye delete ho jayega!"
    )
    btns = [
        [
            InlineKeyboardButton("✅ Haan, Delete Karo", callback_data=f"confirm_delbot_{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="go_home"),
        ]
    ]
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    else:
        await update.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^confirm_delbot_(\d+)$"))
async def confirm_delbot_cb(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))
    if query.from_user.id != user_id and query.from_user.id not in ADMINS:
        return await query.answer("❌ Ye aapka bot nahi hai!", show_alert=True)

    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Bot nahi mila.", show_alert=True)

    bot_uname = clone.get("bot_username", "Unknown")
    bot_id = clone.get("bot_id")

    # Running BOTS se stop karo
    if hasattr(temp, "BOTS"):
        for b in temp.BOTS:
            try:
                me = await b.get_me()
                if me.id == bot_id:
                    await b.stop()
                    temp.BOTS.remove(b)
                    break
            except:
                pass

    await db.delete_clone(user_id)
    await query.message.edit_text(
        f"<b>✅ @{bot_uname} delete ho gaya!</b>\n\n"
        "/createbot se naya banao.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Naya Bot Banao", callback_data="start_create")],
            [InlineKeyboardButton("🏠 Home", callback_data="go_home")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        await client.send_message(
            LOG_CHANNEL,
            f"<b>🗑️ Clone Bot Deleted\nBot: @{bot_uname}\nOwner ID: {user_id}</b>"
        )
    except:
        pass


# ═══════════════════════════════════════════════
#  /manage  — Bot settings panel (BotFather style)
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("manage") & filters.private)
async def manage_cmd(client, message: Message):
    await _show_manage_menu(client, message.from_user.id, message=message)


@Client.on_callback_query(filters.regex("^manage_menu$"))
async def manage_menu_cb(client, query: CallbackQuery):
    await _show_manage_menu(client, query.from_user.id, query=query)


@Client.on_callback_query(filters.regex(r"^manage_bot_(.+)$"))
async def manage_bot_cb(client, query: CallbackQuery):
    await _show_manage_menu(client, query.from_user.id, query=query)


async def _show_manage_menu(client, user_id, message=None, query=None):
    clone = await db.get_clone(user_id)
    if not clone:
        txt = "<b>❌ Pehle /createbot se bot banao.</b>"
        if query:
            return await query.message.edit_text(txt, parse_mode=enums.ParseMode.HTML)
        return await message.reply(txt, parse_mode=enums.ParseMode.HTML)

    bot_uname = clone.get("bot_username", "Unknown")
    start_msg = clone.get("start_message") or "Default (set nahi hai)"
    start_photo = "✅ Set" if clone.get("start_photo") else "❌ Set Nahi"
    start_btns = len(clone.get("start_buttons") or [])
    update_ch = clone.get("update_channel_link") or "❌ Set Nahi"

    text = (
        f"<b>⚙️ Bot Settings — @{bot_uname}</b>\n\n"
        f"📝 Welcome Msg: {'✅ Custom' if clone.get('start_message') else '❌ Default'}\n"
        f"🖼️ Welcome Photo: {start_photo}\n"
        f"🔘 Custom Buttons: {start_btns} button\n"
        f"📢 Update Channel: {update_ch[:30] if update_ch != '❌ Set Nahi' else update_ch}\n\n"
        f"👇 Kya change karna hai?"
    )
    btns = [
        [InlineKeyboardButton("📝 Welcome Message", callback_data="set_start_msg")],
        [InlineKeyboardButton("🖼️ Welcome Photo", callback_data="set_start_photo")],
        [InlineKeyboardButton("🔘 Manage Buttons", callback_data="manage_buttons")],
        [InlineKeyboardButton("📢 Update Channel", callback_data="set_update_ch")],
        [InlineKeyboardButton("📊 Subscription", callback_data="my_sub_status")],
        [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
    ]
    if query:
        try:
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
        except:
            await query.answer()
    else:
        await message.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# — Set Welcome Message —
@Client.on_callback_query(filters.regex("^set_start_msg$"))
async def set_start_msg_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📝 Welcome Message Set Karo</b>\n\n"
        "Apna custom welcome message bhejo.\n"
        "<b>HTML tags use kar sakte ho</b> (bold, italic, code etc.)\n\n"
        "Ye message tab dikhega jab koi user aapke bot ko /start karega.\n\n"
        "👉 Message bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    new_msg = reply.text or reply.caption or ""
    await db.update_clone(user_id, {"start_message": new_msg})
    await reply.reply(
        "<b>✅ Welcome message set ho gaya!</b>\n\n"
        "Ab /start karte waqt ye message dikhega.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# — Set Welcome Photo —
@Client.on_callback_query(filters.regex("^set_start_photo$"))
async def set_start_photo_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>🖼️ Welcome Photo Set Karo</b>\n\n"
        "Koi bhi <b>JPG photo link</b> bhejo.\n"
        "Example: <code>https://telegra.ph/file/abc.jpg</code>\n\n"
        "Ya photo seedha send karo.\n\n"
        "👉 Photo/Link bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    photo_url = None
    if reply.photo:
        photo_url = reply.photo.file_id
    elif reply.text:
        url = reply.text.strip()
        if url.startswith("http") and (url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".png") or "telegra.ph" in url):
            photo_url = url
        else:
            return await reply.reply("❌ Sahi JPG link bhejo ya photo send karo.")

    await db.update_clone(user_id, {"start_photo": photo_url})
    await reply.reply(
        "<b>✅ Welcome photo set ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# — Manage Buttons —
@Client.on_callback_query(filters.regex("^manage_buttons$"))
async def manage_buttons_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    buttons_list = clone.get("start_buttons") or []
    lines = ["<b>🔘 Start Message Buttons</b>\n"]
    if buttons_list:
        for i, btn in enumerate(buttons_list, 1):
            lines.append(f"<b>{i}.</b> {btn.get('text','?')} → {btn.get('url','?')}")
    else:
        lines.append("Koi button nahi hai abhi.")

    lines.append("\n👇 Kya karna hai?")

    btns = [
        [InlineKeyboardButton("➕ Button Add Karo", callback_data="add_button")],
        [InlineKeyboardButton("🗑️ Saare Buttons Hatao", callback_data="clear_buttons")],
        [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
    ]
    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^add_button$"))
async def add_button_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    await query.message.edit_text(
        "<b>➕ Naya Button Add Karo</b>\n\n"
        "Is format mein bhejo:\n"
        "<code>Button Text | https://link.com</code>\n\n"
        "Example:\n"
        "<code>📢 Join Channel | https://t.me/asbhai_bsr</code>\n\n"
        "👉 Bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_buttons")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    text = reply.text or ""
    if "|" not in text:
        return await reply.reply("❌ Format galat hai! <code>Text | URL</code> format use karo.", parse_mode=enums.ParseMode.HTML)

    parts = text.split("|", 1)
    btn_text = parts[0].strip()
    btn_url  = parts[1].strip()

    if not btn_url.startswith("http"):
        return await reply.reply("❌ URL https:// se shuru hona chahiye.")

    clone = await db.get_clone(user_id)
    buttons_list = clone.get("start_buttons") or []
    buttons_list.append({"text": btn_text, "url": btn_url})
    await db.update_clone(user_id, {"start_buttons": buttons_list})

    await reply.reply(
        f"<b>✅ Button add ho gaya!</b>\n{btn_text} → {btn_url}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Buttons", callback_data="manage_buttons")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^clear_buttons$"))
async def clear_buttons_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    await db.update_clone(user_id, {"start_buttons": []})
    await query.answer("✅ Saare buttons hata diye!", show_alert=True)
    await manage_buttons_cb(client, query)


# — Set Update Channel —
@Client.on_callback_query(filters.regex("^set_update_ch$"))
async def set_update_ch_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📢 Update Channel Set Karo</b>\n\n"
        "Apne channel ka link bhejo:\n"
        "Example: <code>https://t.me/asbhai_bsr</code>\n\n"
        "👉 Link bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    url = reply.text.strip() if reply.text else ""
    if not url.startswith("https://t.me/"):
        return await reply.reply("❌ t.me link hona chahiye. Example: https://t.me/yourchannel")

    await db.update_clone(user_id, {"update_channel_link": url})
    await reply.reply(
        "<b>✅ Update channel set ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# — Subscription Status —
@Client.on_callback_query(filters.regex("^my_sub_status$"))
async def my_sub_status_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Koi bot nahi hai!", show_alert=True)

    bot_id = clone.get("bot_id")
    sub = await get_subscription(bot_id)
    if not sub:
        return await query.message.edit_text(
            "<b>❌ Subscription data nahi mila.</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
            parse_mode=enums.ParseMode.HTML
        )

    expiry  = sub.get("expiry")
    active  = sub.get("is_active", False)
    is_free = sub.get("is_free", True)
    days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
    exp_str = expiry.strftime("%d %b %Y") if expiry else "?"
    bot_uname = sub.get("bot_username", "?")

    text = (
        f"<b>📊 Subscription Status</b>\n\n"
        f"🤖 Bot: @{bot_uname}\n"
        f"📅 Expiry: {exp_str}\n"
        f"⏳ Bacha: {days_left} din\n"
        f"💎 Plan: {'Free Trial' if is_free else 'Paid'}\n"
        f"Status: {'✅ Active' if active and days_left > 0 else '❌ Expired'}\n\n"
        f"Renew ke liye admin se contact karo: @aschat_group"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^main_copyright$"))
async def main_copyright_cb(client, query):
    await query.answer(
        "🔒 Ye ek Auto Filter service hai.\n\n"
        "Files third-party sources se automatically index hoti hain.\n"
        "Hamara kisi bhi copyrighted content se seedha koi sambandh nahi.\n\n"
        "Kisi bhi issue ke liye @aschat_group contact karo.",
        show_alert=True
    )
