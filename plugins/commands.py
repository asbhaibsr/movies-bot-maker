# ════════════════════════════════════════════════════════════
#   MAIN BOT — BotFather Style
#   @createautofilterRobot
#   Support: @aschat_group | Updates: @asbhai_bsr
# ════════════════════════════════════════════════════════════

import re, asyncio, logging, datetime, aiohttp
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery, BotCommand
)
from database.users_chats_db import db
from database.subscription_db import (
    create_subscription, get_subscription, get_owner_bots
)
from info import ADMINS, LOG_CHANNEL
from utils import temp

logger = logging.getLogger(__name__)

UPDATE_CHANNEL = "https://t.me/asbhai_bsr"
SUPPORT_GROUP  = "https://t.me/aschat_group"


# ─── Bot API helper ─────────────────────────────────────────
async def bot_api(token: str, method: str, **params) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=params) as r:
            return await r.json()


# ─── Get running clone client ────────────────────────────────
async def get_clone_client(bot_id: int):
    for b in getattr(temp, "BOTS", []):
        try:
            me = await b.get_me()
            if me.id == bot_id:
                return b
        except:
            pass
    return None


# ════════════════════════════════════════════════════════════
#  /start
# ════════════════════════════════════════════════════════════
@Client.on_message(filters.command("start") & filters.private & filters.incoming)
async def start_cmd(client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"<b>👤 New User\n"
                f"ID: <code>{message.from_user.id}</code>\n"
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
        f"🤖 Main hoon <b>Create AutoFilter Bot</b>\n"
        f"Aapka apna <b>Movie Bot Factory!</b>\n\n"
        f"📌 <b>Main kya kar sakta hoon?</b>\n"
        f"  ✅ Apna Movie Bot banao\n"
        f"  ✅ Bot ka naam, photo, description change karo\n"
        f"  ✅ Welcome message + photo + buttons set karo\n"
        f"  ✅ Subscription manage karo\n\n"
        f"👇 Shuru karo:"
    )
    try:
        await message.reply_photo(
            photo="https://telegra.ph/file/your-banner.jpg",
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except:
        await message.reply(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
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
        f"<b>👋 {user.mention}! Wapas aa gaye 😊</b>\n\n"
        f"🤖 <b>Create AutoFilter Bot</b> — Movie Bot Factory\n\n"
        f"Kya karna hai?"
    )
    try:
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except:
        await query.answer()


@Client.on_callback_query(filters.regex("^main_help$"))
async def main_help_cb(client, query: CallbackQuery):
    text = (
        "<b>📖 Help — @createautofilterRobot</b>\n\n"
        "<b>User Commands:</b>\n"
        "/createbot — Naya movie bot banao\n"
        "/mybot — Apne bots dekho\n"
        "/delbot — Bot delete karo\n"
        "/manage — Bot ke saare settings manage karo\n\n"
        "<b>Manage Panel Features:</b>\n"
        "📝 Welcome message set karo\n"
        "🖼️ Welcome photo set karo\n"
        "🔘 Custom buttons add karo\n"
        "🤖 Bot naam change karo\n"
        "📄 Bot description change karo\n"
        "📸 Bot profile photo change karo\n"
        "📋 Bot commands set karo\n"
        "📢 Update channel set karo\n\n"
        f"Support: @aschat_group"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="go_home")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^create_bot_guide$"))
async def create_bot_guide_cb(client, query: CallbackQuery):
    text = (
        "<b>🤖 Apna Bot Kaise Banayein:</b>\n\n"
        "<b>Step 1:</b> @BotFather pe jao\n"
        "<b>Step 2:</b> /newbot bhejo\n"
        "<b>Step 3:</b> Bot ka naam do\n"
        "<b>Step 4:</b> Username do (must end in 'bot')\n"
        "<b>Step 5:</b> BotFather ka reply yahan forward karo\n\n"
        "📌 Ya seedha token paste karo\n\n"
        "👇 Tayaar ho? Start karo:"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Bot Banao", callback_data="start_create")],
            [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ════════════════════════════════════════════════════════════
#  /createbot
# ════════════════════════════════════════════════════════════
@Client.on_message(filters.command(["createbot", "clone"]) & filters.private)
async def createbot_cmd(client, message: Message):
    await _start_createbot(client, message.from_user.id)


@Client.on_callback_query(filters.regex("^start_create$"))
async def start_create_cb(client, query: CallbackQuery):
    await query.answer()
    await _start_createbot(client, query.from_user.id)


async def _start_createbot(client, user_id: int):
    if await db.is_clone_exist(user_id):
        clone = await db.get_clone(user_id)
        uname = clone.get("bot_username", "Unknown")
        await client.send_message(
            user_id,
            f"<b>⚠️ Aapka bot already hai: @{uname}</b>\n\n"
            f"Pehle /delbot karo, phir naya banao.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Delete Karo", callback_data="delbot_menu")],
                [InlineKeyboardButton("⚙️ Manage Karo", callback_data="manage_menu")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        return

    guide = await client.send_message(
        user_id,
        "<b>📋 Process:</b>\n\n"
        "1️⃣ @BotFather → /newbot\n"
        "2️⃣ Naam do → Username do\n"
        "3️⃣ BotFather ka confirmation <b>yahan forward karo</b>\n\n"
        "Ya seedha <code>TOKEN</code> paste karo\n\n"
        "⏰ 5 min mein jawab do | /cancel se cancel karo",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        reply = await client.listen(user_id, timeout=300)
    except asyncio.TimeoutError:
        return await guide.edit_text("⏰ <b>Timeout! /createbot dobara karo.</b>", parse_mode=enums.ParseMode.HTML)

    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("<b>❌ Cancel kar diya.</b>", parse_mode=enums.ParseMode.HTML)

    bot_token = None
    text_to_search = ""
    if reply.forward_from and reply.forward_from.id == 93372553:
        text_to_search = reply.text or ""
    elif reply.text:
        text_to_search = reply.text
    match = re.search(r"\b(\d+:[A-Za-z0-9_-]{35,})\b", text_to_search)
    if match:
        bot_token = match.group(1)

    if not bot_token:
        return await reply.reply(
            "<b>❌ Token nahi mila!</b>\n\nBotFather ka message forward karo ya token paste karo.",
            parse_mode=enums.ParseMode.HTML
        )

    wait = await reply.reply("⏳ <b>Bot start ho raha hai...</b>", parse_mode=enums.ParseMode.HTML)

    try:
        from info import API_ID, API_HASH
        new_bot = Client(
            f"clone_{bot_token[:8]}",
            API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "AsFilterBot"},
            sleep_threshold=60,
            max_concurrent_transmissions=2,
        )
        await new_bot.start()
        me = await new_bot.get_me()

        await db.add_clone_bot(
            bot_id=me.id,
            user_id=user_id,
            bot_token=bot_token,
            bot_username=me.username or ""
        )
        await create_subscription(me.id, user_id, me.username or "")

        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(new_bot)

        await wait.edit_text(
            f"<b>🎉 Bot Successfully Bana Diya!</b>\n\n"
            f"🤖 Bot: @{me.username}\n"
            f"🎁 Free Trial: <b>30 din</b>\n\n"
            f"Ab neeche se apna bot fully setup karo 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Bot Setup Karo", callback_data="manage_menu")],
                [InlineKeyboardButton("📋 Mere Bots", callback_data="my_bots")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"<b>🆕 Clone Bot Created!\n"
                f"Bot: @{me.username} (<code>{me.id}</code>)\n"
                f"Owner: <code>{user_id}</code></b>"
            )
        except:
            pass

    except Exception as e:
        await wait.edit_text(
            f"<b>❌ Error:</b>\n<code>{e}</code>\n\n"
            f"Token sahi hai? @aschat_group se help lo.",
            parse_mode=enums.ParseMode.HTML
        )


# ════════════════════════════════════════════════════════════
#  /mybot
# ════════════════════════════════════════════════════════════
@Client.on_message(filters.command("mybot") & filters.private)
@Client.on_callback_query(filters.regex("^my_bots$"))
async def mybot_cmd(client, update):
    user_id = update.from_user.id
    bots = await get_owner_bots(user_id)

    if not bots:
        text = "<b>📭 Koi bot nahi hai abhi.</b>\n\n/createbot se banao!"
        btns = [[InlineKeyboardButton("🤖 Bot Banao", callback_data="start_create")]]
        if isinstance(update, CallbackQuery):
            return await update.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
        return await update.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)

    lines = ["<b>📋 Aapke Bots:</b>\n"]
    buttons = []
    now = datetime.datetime.now()
    for i, sub in enumerate(bots, 1):
        uname     = sub.get("bot_username", "Unknown")
        expiry    = sub.get("expiry")
        days_left = max(0, (expiry - now).days) if expiry else 0
        active    = sub.get("is_active", False) and days_left > 0
        status    = "✅" if active else "❌"
        plan      = "🎁 Free" if sub.get("is_free") else "💎 Paid"
        lines.append(f"{status} @{uname} | {plan} | {days_left}d left")
        buttons.append([InlineKeyboardButton(f"⚙️ Manage @{uname}", callback_data=f"manage_bot_{uname}")])

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


# ════════════════════════════════════════════════════════════
#  /delbot
# ════════════════════════════════════════════════════════════
@Client.on_message(filters.command("delbot") & filters.private)
@Client.on_callback_query(filters.regex("^delbot_menu$"))
async def delbot_cmd(client, update):
    user_id = update.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        msg = "<b>❌ Koi bot nahi hai delete karne ke liye.</b>"
        if isinstance(update, CallbackQuery):
            return await update.answer(msg, show_alert=True)
        return await update.reply(msg, parse_mode=enums.ParseMode.HTML)

    uname = clone.get("bot_username", "Unknown")
    text  = (
        f"<b>🗑️ Bot Delete Confirm?</b>\n\n"
        f"Bot: @{uname}\n\n"
        f"⚠️ Ye action permanent hai!"
    )
    btns = [[
        InlineKeyboardButton("✅ Delete", callback_data=f"confirm_delbot_{user_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data="go_home"),
    ]]
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    else:
        await update.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^confirm_delbot_(\d+)$"))
async def confirm_delbot_cb(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))
    if query.from_user.id != user_id and query.from_user.id not in ADMINS:
        return await query.answer("❌ Ye aapka bot nahi!", show_alert=True)

    clone  = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Bot nahi mila.", show_alert=True)

    uname  = clone.get("bot_username", "Unknown")
    bot_id = clone.get("bot_id")

    for b in getattr(temp, "BOTS", []):
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
        f"<b>✅ @{uname} delete ho gaya!</b>\n\n/createbot se naya banao.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 Naya Bot", callback_data="start_create")]]),
        parse_mode=enums.ParseMode.HTML
    )


# ════════════════════════════════════════════════════════════
#  /manage — Full Settings Panel (BotFather + Clone Settings)
# ════════════════════════════════════════════════════════════
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

    uname     = clone.get("bot_username", "Unknown")
    has_photo = "✅" if clone.get("start_photo") else "❌"
    has_msg   = "✅" if clone.get("start_message") else "❌"
    btn_count = len(clone.get("start_buttons") or [])

    text = (
        f"<b>⚙️ Bot Settings — @{uname}</b>\n\n"
        f"📝 Welcome Msg: {has_msg}\n"
        f"🖼️ Welcome Photo: {has_photo}\n"
        f"🔘 Buttons: {btn_count}\n\n"
        f"👇 Kya change karna hai?"
    )
    btns = [
        [
            InlineKeyboardButton("📝 Welcome Msg", callback_data="set_start_msg"),
            InlineKeyboardButton("🖼️ Welcome Photo", callback_data="set_start_photo"),
        ],
        [
            InlineKeyboardButton("🔘 Buttons", callback_data="manage_buttons"),
            InlineKeyboardButton("📢 Update Channel", callback_data="set_update_ch"),
        ],
        [InlineKeyboardButton("🤖 Bot Settings (BotFather)", callback_data="botfather_menu")],
        [
            InlineKeyboardButton("📊 Subscription", callback_data="my_sub_status"),
            InlineKeyboardButton("🔙 Back", callback_data="go_home"),
        ],
    ]
    if query:
        try:
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
        except:
            await query.answer()
    else:
        await message.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# ══════════════════════════════════════════════
#  🤖 BOTFATHER FEATURES PANEL
# ══════════════════════════════════════════════
@Client.on_callback_query(filters.regex("^botfather_menu$"))
async def botfather_menu_cb(client, query: CallbackQuery):
    clone = await db.get_clone(query.from_user.id)
    uname = clone.get("bot_username", "Unknown") if clone else "Unknown"
    text = (
        f"<b>🤖 BotFather Settings — @{uname}</b>\n\n"
        f"Ye sab cheezein directly apne bot pe apply hongi.\n"
        f"BotFather pe jaane ki zarurat NAHI! 🎉\n\n"
        f"👇 Kya change karna hai?"
    )
    btns = [
        [
            InlineKeyboardButton("✏️ Bot Naam", callback_data="bf_change_name"),
            InlineKeyboardButton("📄 Description", callback_data="bf_change_desc"),
        ],
        [
            InlineKeyboardButton("ℹ️ About Text", callback_data="bf_change_about"),
            InlineKeyboardButton("📸 Profile Photo", callback_data="bf_change_photo"),
        ],
        [InlineKeyboardButton("📋 Bot Commands Set Karo", callback_data="bf_set_commands")],
        [InlineKeyboardButton("🗑️ Profile Photo Delete", callback_data="bf_del_photo")],
        [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# ─── Bot Name Change ─────────────────────────────────────────
@Client.on_callback_query(filters.regex("^bf_change_name$"))
async def bf_change_name_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>✏️ Bot ka naya naam bhejo:</b>\n\n"
        "Example: <code>My Movie Bot</code>\n\n"
        "👉 Naam bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    new_name = reply.text.strip() if reply.text else ""
    if not new_name or len(new_name) < 2:
        return await reply.reply("❌ Naam kam se kam 2 characters ka hona chahiye.")

    token = clone.get("bot_token")
    result = await bot_api(token, "setMyName", name=new_name)

    if result.get("ok"):
        await reply.reply(
            f"<b>✅ Bot naam change ho gaya!</b>\n\nNew name: <b>{new_name}</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="botfather_menu")]]),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await reply.reply(
            f"<b>❌ Error:</b> {result.get('description', 'Unknown error')}",
            parse_mode=enums.ParseMode.HTML
        )


# ─── Bot Description Change ──────────────────────────────────
@Client.on_callback_query(filters.regex("^bf_change_desc$"))
async def bf_change_desc_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📄 Bot Description Set Karo:</b>\n\n"
        "Ye tab dikhta hai jab koi pehli baar bot open kare.\n"
        "Max: 512 characters\n\n"
        "Example:\n"
        "<i>Ye bot aapko movies dhundhne mein help karta hai!</i>\n\n"
        "👉 Description bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    desc  = (reply.text or "").strip()[:512]
    token = clone.get("bot_token")
    result = await bot_api(token, "setMyDescription", description=desc)

    if result.get("ok"):
        await reply.reply(
            "<b>✅ Description set ho gayi!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await reply.reply(f"<b>❌ Error:</b> {result.get('description', 'Unknown')}", parse_mode=enums.ParseMode.HTML)


# ─── Bot About Text ───────────────────────────────────────────
@Client.on_callback_query(filters.regex("^bf_change_about$"))
async def bf_change_about_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>ℹ️ Bot About Text Set Karo:</b>\n\n"
        "Ye bot ke profile mein dikhta hai.\n"
        "Max: 120 characters\n\n"
        "Example: <code>Best Movie Bot 🎬</code>\n\n"
        "👉 About text bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    about  = (reply.text or "").strip()[:120]
    token  = clone.get("bot_token")
    result = await bot_api(token, "setMyShortDescription", short_description=about)

    if result.get("ok"):
        await reply.reply(
            "<b>✅ About text set ho gaya!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await reply.reply(f"<b>❌ Error:</b> {result.get('description', 'Unknown')}", parse_mode=enums.ParseMode.HTML)


# ─── Profile Photo Change ─────────────────────────────────────
@Client.on_callback_query(filters.regex("^bf_change_photo$"))
async def bf_change_photo_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📸 Bot Profile Photo Change Karo:</b>\n\n"
        "Photo direct bhejo (JPG/PNG)\n"
        "Ya <code>https://link.jpg</code> link bhejo\n\n"
        "👉 Photo bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    bot_id = clone.get("bot_id")
    token  = clone.get("bot_token")
    clone_client = await get_clone_client(bot_id)

    try:
        if reply.photo:
            # Photo download karke clone bot se set karo
            file_path = await client.download_media(reply.photo)
            if clone_client:
                await clone_client.set_profile_photo(photo=file_path)
                import os
                os.remove(file_path)
                await reply.reply(
                    "<b>✅ Profile photo set ho gaya!</b>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await reply.reply("❌ Clone bot running nahi hai. Bot restart karo.", parse_mode=enums.ParseMode.HTML)

        elif reply.text and reply.text.strip().startswith("http"):
            url = reply.text.strip()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    photo_bytes = await resp.read()
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(photo_bytes)
                tmp_path = tmp.name
            if clone_client:
                await clone_client.set_profile_photo(photo=tmp_path)
                os.remove(tmp_path)
                await reply.reply(
                    "<b>✅ Profile photo set ho gaya!</b>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await reply.reply("❌ Clone bot running nahi hai.", parse_mode=enums.ParseMode.HTML)
        else:
            await reply.reply("❌ Photo ya link bhejo.", parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        await reply.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ─── Delete Profile Photo ─────────────────────────────────────
@Client.on_callback_query(filters.regex("^bf_del_photo$"))
async def bf_del_photo_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    bot_id = clone.get("bot_id")
    clone_client = await get_clone_client(bot_id)
    if not clone_client:
        return await query.answer("❌ Bot running nahi. Restart karo.", show_alert=True)

    try:
        photos = []
        async for p in clone_client.get_chat_photos("me"):
            photos.append(p.file_id)
        if photos:
            await clone_client.delete_profile_photos(photos)
            await query.answer("✅ Profile photo delete ho gaya!", show_alert=True)
        else:
            await query.answer("Koi profile photo nahi hai.", show_alert=True)
    except Exception as e:
        await query.answer(f"❌ Error: {e}", show_alert=True)


# ─── Set Bot Commands ─────────────────────────────────────────
@Client.on_callback_query(filters.regex("^bf_set_commands$"))
async def bf_set_commands_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    default_cmds = (
        "start - Bot start karo\n"
        "help - Help menu\n"
        "settings - Settings manage karo\n"
        "search - Movie search karo\n"
        "request - Movie request karo\n"
        "plan - Premium plans dekho\n"
        "myplan - Apna plan dekho\n"
        "id - Apna ID dekho\n"
        "chat - AI se baat karo"
    )
    await query.message.edit_text(
        "<b>📋 Bot Commands Set Karo:</b>\n\n"
        "Format: <code>command - description</code>\n"
        "Har command ek nayi line mein\n\n"
        "<b>Default commands (copy kar sakte ho):</b>\n"
        f"<code>{default_cmds}</code>\n\n"
        "👉 Commands bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Default Commands Set Karo", callback_data="bf_set_default_cmds")],
            [InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=180)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    await _apply_commands(clone, reply, reply.text or "")


@Client.on_callback_query(filters.regex("^bf_set_default_cmds$"))
async def bf_set_default_cmds_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    default_text = (
        "start - Bot start karo\n"
        "help - Help menu\n"
        "settings - Settings manage karo\n"
        "search - Movie search karo\n"
        "request - Movie request karo\n"
        "plan - Premium plans dekho\n"
        "myplan - Apna plan dekho\n"
        "id - Apna ID dekho\n"
        "info - User info dekho\n"
        "chat - AI se baat karo\n"
        "topsearches - Trending movies\n"
        "broadcast - Broadcast karo"
    )
    await _apply_commands(clone, query, default_text, is_callback=True)


async def _apply_commands(clone, update, text: str, is_callback=False):
    commands = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if " - " in line:
            cmd, desc = line.split(" - ", 1)
        elif " — " in line:
            cmd, desc = line.split(" — ", 1)
        else:
            continue
        cmd = cmd.strip().lstrip("/").lower()
        desc = desc.strip()
        if cmd and desc and len(cmd) <= 32:
            commands.append({"command": cmd, "description": desc})

    if not commands:
        msg = "❌ Koi valid command nahi mila. Format: <code>command - description</code>"
        if is_callback:
            return await update.answer(msg, show_alert=True)
        return await update.reply(msg, parse_mode=enums.ParseMode.HTML)

    token  = clone.get("bot_token")
    result = await bot_api(token, "setMyCommands", commands=commands)

    success_msg = (
        f"<b>✅ {len(commands)} Commands Set Ho Gayi!</b>\n\n"
        + "\n".join([f"/{c['command']} — {c['description']}" for c in commands[:10]])
    )
    btns = [[InlineKeyboardButton("🔙 Back", callback_data="botfather_menu")]]

    if result.get("ok"):
        if is_callback:
            await update.answer("✅ Commands set ho gayi!", show_alert=True)
        else:
            await update.reply(success_msg, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    else:
        err = f"<b>❌ Error:</b> {result.get('description', 'Unknown')}"
        if is_callback:
            await update.answer("❌ Error!", show_alert=True)
        else:
            await update.reply(err, parse_mode=enums.ParseMode.HTML)


# ════════════════════════════════════════════════════════════
#  Welcome Message / Photo / Buttons
# ════════════════════════════════════════════════════════════
@Client.on_callback_query(filters.regex("^set_start_msg$"))
async def set_start_msg_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📝 Welcome Message Set Karo</b>\n\n"
        "Ye message tab dikhega jab koi /start karega.\n"
        "HTML tags use kar sakte ho: <b>bold</b>, <i>italic</i>, <code>code</code>\n\n"
        "Variables use kar sakte ho:\n"
        "<code>{first_name}</code> — User ka naam\n"
        "<code>{username}</code> — Username\n"
        "<code>{bot_name}</code> — Bot naam\n\n"
        "👉 Message bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    msg = reply.text or reply.caption or ""
    await db.update_clone(user_id, {"start_message": msg})
    await reply.reply(
        "<b>✅ Welcome message save ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^set_start_photo$"))
async def set_start_photo_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>🖼️ Welcome Photo Set Karo</b>\n\n"
        "Photo direct bhejo ya JPG link bhejo:\n"
        "<code>https://telegra.ph/file/abc.jpg</code>\n\n"
        "👉 Photo/Link bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    photo_url = None
    if reply.photo:
        photo_url = reply.photo.file_id
    elif reply.text:
        url = reply.text.strip()
        if url.startswith("http"):
            photo_url = url

    if not photo_url:
        return await reply.reply("❌ Photo ya valid link bhejo.")

    await db.update_clone(user_id, {"start_photo": photo_url})
    await reply.reply(
        "<b>✅ Welcome photo save ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^manage_buttons$"))
async def manage_buttons_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    btns_list = clone.get("start_buttons") or []
    lines = ["<b>🔘 Start Buttons</b>\n"]
    if btns_list:
        for i, b in enumerate(btns_list, 1):
            lines.append(f"{i}. {b.get('text','?')} → {b.get('url','?')}")
    else:
        lines.append("Koi button nahi hai abhi.")

    btns = [
        [InlineKeyboardButton("➕ Button Add Karo", callback_data="add_button")],
    ]
    if btns_list:
        btns.append([InlineKeyboardButton("🗑️ Saare Buttons Hatao", callback_data="clear_buttons")])
    btns.append([InlineKeyboardButton("🔙 Back", callback_data="manage_menu")])

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^add_button$"))
async def add_button_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    await query.message.edit_text(
        "<b>➕ Button Add Karo</b>\n\n"
        "Format: <code>Button Text | https://link.com</code>\n\n"
        "Example:\n"
        "<code>📢 Channel | https://t.me/asbhai_bsr</code>\n\n"
        "👉 Bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_buttons")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    text = reply.text or ""
    if "|" not in text:
        return await reply.reply("❌ Format: <code>Text | URL</code>", parse_mode=enums.ParseMode.HTML)

    parts    = text.split("|", 1)
    btn_text = parts[0].strip()
    btn_url  = parts[1].strip()

    if not btn_url.startswith("http"):
        return await reply.reply("❌ URL https:// se shuru hona chahiye.")

    clone      = await db.get_clone(user_id)
    btns_list  = clone.get("start_buttons") or []
    btns_list.append({"text": btn_text, "url": btn_url})
    await db.update_clone(user_id, {"start_buttons": btns_list})

    await reply.reply(
        f"<b>✅ Button add ho gaya!</b>\n{btn_text} → {btn_url}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_buttons")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^clear_buttons$"))
async def clear_buttons_cb(client, query: CallbackQuery):
    await db.update_clone(query.from_user.id, {"start_buttons": []})
    await query.answer("✅ Saare buttons hata diye!", show_alert=True)
    await manage_buttons_cb(client, query)


@Client.on_callback_query(filters.regex("^set_update_ch$"))
async def set_update_ch_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📢 Update Channel Set Karo</b>\n\n"
        "Example: <code>https://t.me/yourchannel</code>\n\n"
        "👉 Link bhejo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() in ["/cancel", "/manage"]:
        return await reply.reply("❌ Cancel.")

    url = (reply.text or "").strip()
    if not url.startswith("https://t.me/"):
        return await reply.reply("❌ t.me link hona chahiye.")

    await db.update_clone(user_id, {"update_channel_link": url})
    await reply.reply(
        "<b>✅ Update channel set ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )


# ════════════════════════════════════════════════════════════
#  Subscription Status
# ════════════════════════════════════════════════════════════
@Client.on_callback_query(filters.regex("^my_sub_status$"))
async def my_sub_status_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Koi bot nahi!", show_alert=True)

    bot_id = clone.get("bot_id")
    sub    = await get_subscription(bot_id)
    if not sub:
        return await query.message.edit_text(
            "<b>❌ Subscription data nahi mila.</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
            parse_mode=enums.ParseMode.HTML
        )

    now       = datetime.datetime.now()
    expiry    = sub.get("expiry")
    days_left = max(0, (expiry - now).days) if expiry else 0
    exp_str   = expiry.strftime("%d %b %Y") if expiry else "?"
    active    = sub.get("is_active", False) and days_left > 0
    is_free   = sub.get("is_free", True)
    uname     = sub.get("bot_username", "?")

    text = (
        f"<b>📊 Subscription</b>\n\n"
        f"🤖 Bot: @{uname}\n"
        f"💎 Plan: {'Free Trial' if is_free else 'Paid'}\n"
        f"📅 Expiry: {exp_str}\n"
        f"⏳ Remaining: {days_left} din\n"
        f"Status: {'✅ Active' if active else '❌ Expired'}\n\n"
        f"Renew ke liye contact karo:"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )
