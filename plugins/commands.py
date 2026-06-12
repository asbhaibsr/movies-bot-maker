# ════════════════════════════════════════════════════════════
#   Main Bot — BotFather Style Bot Maker
#   UPDATED: Files DB button, Manage menu, Moderators, Plans
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

SUPPORT_GROUP  = "https://t.me/aschat_group"
UPDATE_CHANNEL = "https://t.me/asbhai_bsr"
MAIN_BOT_NAME  = "Create AutoFilter Bot"

# UPI details for Files Database payment
PAYMENT_UPI_ID  = "yourupi@ybl"          # Change this to your UPI ID
PAYMENT_AMOUNT  = 200                    # Amount in rupees


async def is_main_admin(user_id: int) -> bool:
    if user_id in ADMINS:
        return True
    return await db.is_dynamic_admin(user_id)


# ═══════════════════════════════════════════════
#  /start
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
    if await is_main_admin(user.id):
        buttons.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel_main")])

    text = (
        f"<b>👋 Assalam o Alaikum, {user.mention}!</b>\n\n"
        f"🤖 Main hoon <b>{MAIN_BOT_NAME}</b> — aapka personal\n"
        f"<b>Movie Bot Factory!</b>\n\n"
        f"📌 <b>Main kya kar sakta hoon?</b>\n"
        f"  ✅ Aapka apna Movie Bot banaunga\n"
        f"  ✅ Files database manage karein\n"
        f"  ✅ Premium plans set karein\n"
        f"  ✅ Subscription manage karein\n\n"
        f"👇 Shuru karo neeche wale button se:"
    )
    await message.reply_text(
        text=text,
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
    if await is_main_admin(user.id):
        buttons.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel_main")])

    text = (
        f"<b>👋 Assalam o Alaikum, {user.mention}!</b>\n\n"
        f"🤖 Main hoon <b>{MAIN_BOT_NAME}</b>\n\n"
        f"👇 Kya karna hai?"
    )
    try:
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except:
        await query.answer()


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
        "/mybot — Apne bots dekho\n"
        "/manage — Bot settings manage karo\n\n"
        "<b>Bot Features (Clone mein):</b>\n"
        "✅ Auto Movie Search\n"
        "✅ IMDB Info\n"
        "✅ Premium Plans\n"
        "✅ Shortlink Verify\n"
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


# ═══════════════════════════════════════════════
#  🔧 ADMIN PANEL
# ═══════════════════════════════════════════════
@Client.on_callback_query(filters.regex("^admin_panel_main$"))
async def admin_panel_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)

    total_users = await db.total_users_count()
    total_bots  = await db.count_all_bots()
    running     = len(getattr(temp, "BOTS", []))
    dyn_admins  = await db.get_dynamic_admins()

    text = (
        "<b>🔧 Admin Panel</b>\n\n"
        f"👥 Total Users: <code>{total_users}</code>\n"
        f"🤖 Clone Bots: <code>{total_bots}</code>\n"
        f"▶️ Running: <code>{running}</code>\n"
        f"👑 Admins: <code>{len(ADMINS) + len(dyn_admins)}</code>\n\n"
        "👇 Kya karna hai?"
    )
    btns = [
        [InlineKeyboardButton("👑 Admin Management", callback_data="admin_mgmt_panel")],
        [
            InlineKeyboardButton("📋 Sub List", callback_data="admin_sublist_quick"),
            InlineKeyboardButton("⚠️ Expiring", callback_data="admin_expiring_quick"),
        ],
        [InlineKeyboardButton("📩 Pending Requests", callback_data="admin_pending_db_reqs")],
        [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
    ]
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_mgmt_panel$"))
async def admin_mgmt_panel_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)

    env_admins = ADMINS
    dyn_docs   = await db.get_all_dynamic_admins_info()

    lines = ["<b>👑 Admin Management</b>\n"]
    lines.append(f"<b>🔒 Env Admins ({len(env_admins)}):</b>")
    for aid in env_admins:
        lines.append(f"  • <code>{aid}</code>")

    if dyn_docs:
        lines.append(f"\n<b>➕ Dynamic Admins ({len(dyn_docs)}):</b>")
        for doc in dyn_docs:
            uname = f"@{doc['username']}" if doc.get("username") else "No username"
            lines.append(f"  • <code>{doc['user_id']}</code> — {uname}")
    else:
        lines.append("\n<i>Koi dynamic admin nahi abhi.</i>")

    btns = [
        [InlineKeyboardButton("➕ Admin Add Karo", callback_data="admin_add_new")],
        [InlineKeyboardButton("➖ Admin Remove Karo", callback_data="admin_remove_one")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel_main")],
    ]
    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_add_new$"))
async def admin_add_new_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)
    if query.from_user.id not in ADMINS:
        return await query.answer("❌ Sirf main Env Admin kar sakta hai!", show_alert=True)

    await query.message.edit_text(
        "<b>➕ Naya Admin Add Karo</b>\n\nUser ka Telegram ID bhejo (sirf numbers):",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="admin_mgmt_panel")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(query.from_user.id, timeout=60)
    except asyncio.TimeoutError:
        return

    if not reply.text or not reply.text.strip().isdigit():
        return await reply.reply("❌ Sirf numeric ID bhejo.")

    new_id = int(reply.text.strip())
    if new_id in ADMINS:
        return await reply.reply(f"<b>ℹ️ {new_id} pehle se Env Admin hai!</b>", parse_mode=enums.ParseMode.HTML)

    username = ""
    try:
        u = await client.get_users(new_id)
        username = u.username or ""
    except:
        pass

    await db.add_dynamic_admin(new_id, username)
    await reply.reply(
        f"<b>✅ Admin Add Ho Gaya!</b>\n🆔 <code>{new_id}</code>\n👤 @{username or 'N/A'}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 Admin List", callback_data="admin_mgmt_panel")],
            [InlineKeyboardButton("🏠 Home", callback_data="go_home")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_remove_one$"))
async def admin_remove_cb(client, query: CallbackQuery):
    if query.from_user.id not in ADMINS:
        return await query.answer("❌ Sirf main Env Admin remove kar sakta hai!", show_alert=True)

    dyn_docs = await db.get_all_dynamic_admins_info()
    if not dyn_docs:
        return await query.answer("Koi dynamic admin nahi.", show_alert=True)

    lines = ["<b>➖ Admin Remove Karo</b>\n\nJis ka ID bhejo:"]
    for doc in dyn_docs:
        uname = f"@{doc['username']}" if doc.get("username") else ""
        lines.append(f"• <code>{doc['user_id']}</code> {uname}")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="admin_mgmt_panel")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(query.from_user.id, timeout=60)
    except asyncio.TimeoutError:
        return

    if not reply.text or not reply.text.strip().isdigit():
        return await reply.reply("❌ Sirf numeric ID bhejo.")

    remove_id = int(reply.text.strip())
    if remove_id in ADMINS:
        return await reply.reply("<b>❌ Env Admin ko yahan se remove nahi kar sakte!</b>", parse_mode=enums.ParseMode.HTML)

    removed = await db.remove_dynamic_admin(remove_id)
    if removed:
        await reply.reply(
            f"<b>✅ Admin Remove Ho Gaya!</b>\n🆔 <code>{remove_id}</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 Admin List", callback_data="admin_mgmt_panel")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await reply.reply(f"<b>❌ ID <code>{remove_id}</code> nahi mila.</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^admin_sublist_quick$"))
async def admin_sublist_quick_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)
    from database.subscription_db import get_all_subscriptions
    subs = await get_all_subscriptions()
    if not subs:
        return await query.answer("Koi subscription nahi.", show_alert=True)
    now = datetime.datetime.now()
    active_c = sum(1 for s in subs if s.get("is_active") and s.get("expiry") and now < s["expiry"])
    await query.message.edit_text(
        f"<b>📋 Subscriptions Summary</b>\n\n"
        f"Total: <code>{len(subs)}</code>\n"
        f"Active: <code>{active_c}</code>\n"
        f"Expired: <code>{len(subs)-active_c}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel_main")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_expiring_quick$"))
async def admin_expiring_quick_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)
    from database.subscription_db import get_expiring_soon_subs
    expiring = await get_expiring_soon_subs(days=7)
    await query.message.edit_text(
        f"<b>⚠️ Agle 7 din mein expire: {len(expiring)} bots</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel_main")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════
#  📂 FILES DATABASE BUTTON — 200 Rs UPI Flow
# ═══════════════════════════════════════════════
@Client.on_callback_query(filters.regex("^files_database_btn$"))
async def files_database_btn_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("❌ Pehle /createbot se bot banao!", show_alert=True)

    bot_uname = clone.get("bot_username", "?")
    text = (
        f"<b>📂 Free Files Database — ₹{PAYMENT_AMOUNT}</b>\n\n"
        f"🎯 Aapko apna channel nahi banana padega!\n"
        f"Hamare main channel ki saari movies automatically aapke bot <b>@{bot_uname}</b> mein search hongi.\n\n"
        f"<b>💳 Payment kaise karein:</b>\n"
        f"1️⃣ UPI par ₹{PAYMENT_AMOUNT} bhejein\n"
        f"2️⃣ UTR/Transaction ID note karein\n"
        f"3️⃣ Neeche wale button se form bharein\n\n"
        f"<b>UPI ID:</b> <code>{PAYMENT_UPI_ID}</code>"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 ₹{PAYMENT_AMOUNT} Pay Karo", callback_data="start_db_payment_form")],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^start_db_payment_form$"))
async def start_db_payment_form_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("❌ Pehle bot banao!", show_alert=True)

    bot_uname = clone.get("bot_username", "?")

    await query.message.edit_text(
        f"<b>📝 Step 1 of 2 — UTR Number Bhejo</b>\n\n"
        f"₹{PAYMENT_AMOUNT} ka payment UPI ID <code>{PAYMENT_UPI_ID}</code> par karein\n\n"
        f"Payment ke baad <b>UTR/Transaction ID</b> bhejein:\n"
        f"<i>(12-digit number jo payment confirmation mein milta hai)</i>\n\n"
        f"⏱️ 5 minute mein bhejein ya /cancel karein:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )

    try:
        utr_msg = await client.listen(user_id, timeout=300)
    except asyncio.TimeoutError:
        return

    if utr_msg.text and utr_msg.text.strip().lower() in ["/cancel", "cancel"]:
        return await utr_msg.reply("❌ Cancel kar diya.")

    utr_number = (utr_msg.text or "").strip()
    if len(utr_number) < 6:
        return await utr_msg.reply("❌ Valid UTR number bhejein (minimum 6 characters).")

    # Step 2 — confirm bot username
    await utr_msg.reply(
        f"<b>📝 Step 2 of 2 — Bot Username Confirm</b>\n\n"
        f"UTR save ho gaya: <code>{utr_number}</code>\n\n"
        f"Ab aapka bot username send karo jiske liye database chahiye.\n"
        f"Current bot: <b>@{bot_uname}</b>\n\n"
        f"<b>@{bot_uname}</b> ke liye database chahiye? Reply karo:\n"
        f"✅ Haan — <code>CONFIRM</code> likho\n"
        f"Ya alag username bhejo: <code>@username</code>\n\n"
        f"⏱️ 3 minute mein bhejein:",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        confirm_msg = await client.listen(user_id, timeout=180)
    except asyncio.TimeoutError:
        return

    confirm_text = (confirm_msg.text or "").strip()
    if confirm_text.upper() == "CONFIRM":
        final_bot_username = bot_uname
    elif confirm_text.startswith("@"):
        final_bot_username = confirm_text.lstrip("@")
    else:
        final_bot_username = confirm_text.lstrip("@") or bot_uname

    # Save pending request
    pending_req = {
        "user_id": user_id,
        "bot_username": final_bot_username,
        "utr": utr_number,
        "amount": PAYMENT_AMOUNT,
        "status": "pending",
        "created_at": datetime.datetime.now()
    }
    try:
        await db.db.db_requests.insert_one(pending_req)
    except Exception as e:
        logger.error(f"DB request save error: {e}")

    # Owner ko notify karo
    user_mention = confirm_msg.from_user.mention
    owner_text = (
        f"<b>📥 Naya Files Database Request</b>\n\n"
        f"👤 User: {user_mention} (<code>{user_id}</code>)\n"
        f"🤖 Bot: @{final_bot_username}\n"
        f"💰 Amount: ₹{PAYMENT_AMOUNT}\n"
        f"🔖 UTR: <code>{utr_number}</code>\n\n"
        f"Request approve/reject karein:"
    )
    for admin_id in ADMINS:
        try:
            await client.send_message(
                admin_id,
                owner_text,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Approve", callback_data=f"db_approve_{user_id}_{final_bot_username}"),
                        InlineKeyboardButton("❌ Reject", callback_data=f"db_reject_{user_id}"),
                    ]
                ]),
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass

    await confirm_msg.reply(
        f"<b>✅ Request Submit Ho Gayi!</b>\n\n"
        f"🤖 Bot: @{final_bot_username}\n"
        f"💰 Amount: ₹{PAYMENT_AMOUNT}\n"
        f"🔖 UTR: <code>{utr_number}</code>\n\n"
        f"Admin verification ke baad aapko notification milega.\n"
        f"⏱️ Usually 1-24 ghante mein process hota hai.",
        parse_mode=enums.ParseMode.HTML
    )


# ── Admin: Approve/Reject DB request ───────────────────────
@Client.on_callback_query(filters.regex(r"^db_approve_(\d+)_(.+)$"))
async def db_approve_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)

    user_id = int(query.matches[0].group(1))
    bot_username = query.matches[0].group(2)

    await query.message.edit_text(
        f"<b>✅ Approved!</b>\n\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Bot: @{bot_username}\n\n"
        f"<b>Ab karo:</b>\n"
        f"1. Bot @{bot_username} ko apne main movies channel mein Admin banao\n"
        f"2. Phir main bot pe: <code>/index CHANNEL_ID @{bot_username}</code>",
        parse_mode=enums.ParseMode.HTML
    )

    # Update DB status
    try:
        await db.db.db_requests.update_one(
            {"user_id": user_id, "status": "pending"},
            {"$set": {"status": "approved", "approved_at": datetime.datetime.now()}}
        )
    except:
        pass

    # User ko notify karo
    try:
        await client.send_message(
            user_id,
            f"<b>🎉 Aapki Files Database Request Approve Ho Gayi!</b>\n\n"
            f"🤖 Bot: @{bot_username}\n\n"
            f"<b>Ab kya hoga:</b>\n"
            f"✅ Admin aapke bot ko main channel ka admin banega\n"
            f"✅ Saari existing movies automatically aapke bot mein index hongi\n"
            f"✅ Naya content aane par bhi automatically aayega\n\n"
            f"<b>Extra file add karne ke liye:</b>\n"
            f"Apne bot mein <code>/addnew</code> command use karein",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"User notify error: {e}")


@Client.on_callback_query(filters.regex(r"^db_reject_(\d+)$"))
async def db_reject_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)

    user_id = int(query.matches[0].group(1))

    await query.message.edit_text(
        f"<b>❌ Rejected</b>\n\nUser ID: <code>{user_id}</code>",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        await db.db.db_requests.update_one(
            {"user_id": user_id, "status": "pending"},
            {"$set": {"status": "rejected"}}
        )
    except:
        pass

    try:
        await client.send_message(
            user_id,
            "<b>❌ Aapki Files Database Request Reject Ho Gayi.</b>\n\n"
            "Agar aapne payment ki thi, to support se contact karein: @aschat_group",
            parse_mode=enums.ParseMode.HTML
        )
    except:
        pass


@Client.on_callback_query(filters.regex("^admin_pending_db_reqs$"))
async def admin_pending_db_reqs_cb(client, query: CallbackQuery):
    if not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Sirf Admin!", show_alert=True)

    try:
        pending = await db.db.db_requests.find({"status": "pending"}).to_list(20)
        if not pending:
            return await query.answer("Koi pending request nahi.", show_alert=True)
        lines = [f"<b>📩 Pending DB Requests ({len(pending)})</b>\n"]
        for req in pending:
            lines.append(
                f"• <code>{req.get('user_id')}</code> → @{req.get('bot_username')} | UTR: {req.get('utr')}"
            )
        await query.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_panel_main")]
            ]),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


# ═══════════════════════════════════════════════
#  /createbot
# ═══════════════════════════════════════════════
@Client.on_message(filters.command(["createbot", "clone"]) & filters.private)
async def createbot_cmd(client, message: Message):
    await _start_createbot(client, message)


@Client.on_callback_query(filters.regex("^start_create$"))
async def start_create_cb(client, query: CallbackQuery):
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
        "<b>3️⃣</b> Bot ka naam do\n"
        "<b>4️⃣</b> Username do\n"
        "<b>5️⃣</b> BotFather ka confirmation message yahan <b>forward</b> karo\n\n"
        "⏱️ 5 minute ka time. /cancel se rokein.\n\n"
        "👇 BotFather ka message forward karo ya token paste karo:",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        reply = await client.listen(user.id, timeout=300)
    except asyncio.TimeoutError:
        return await guide_msg.edit_text("<b>⏰ Timeout! Dobara /createbot karo.</b>")

    if reply.text and reply.text.strip() == "/cancel":
        return await reply.reply("<b>❌ Process cancel kar diya.</b>")

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
            "<b>❌ Token nahi mila!</b>\n\nBotFather ka message forward karo ya token paste karo.\nDobara /createbot karo.",
            parse_mode=enums.ParseMode.HTML
        )

    wait_msg = await reply.reply("⏳ <b>Bot start ho raha hai... 30 sec wait karo</b>", parse_mode=enums.ParseMode.HTML)

    try:
        from info import API_ID, API_HASH
        from pyrogram import Client as PyroClient
        new_bot = PyroClient(
            f"clone_{bot_token[:8]}",
            API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "AsFilterBot"},
        )
        await new_bot.start()
        bot_me = await new_bot.get_me()

        await db.add_clone_bot(
            bot_id=bot_me.id,
            user_id=user.id,
            bot_token=bot_token,
            bot_username=bot_me.username or ""
        )
        await create_subscription(bot_me.id, user.id, bot_me.username or "")

        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(new_bot)

        await wait_msg.edit_text(
            f"<b>🎉 Bot Successfully Bana!</b>\n\n"
            f"🤖 Bot: @{bot_me.username}\n"
            f"🆔 Bot ID: <code>{bot_me.id}</code>\n\n"
            f"✅ 30 din ka free trial shuru!\n\n"
            f"<b>Ab kya karo:</b>\n"
            f"1. Apne group mein @{bot_me.username} add karo\n"
            f"2. /manage se settings set karo\n"
            f"3. Files Database ke liye /manage → Files Database button dabao",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Bot Settings", callback_data="manage_menu")],
                [InlineKeyboardButton("🏠 Home", callback_data="go_home")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"<b>🤖 New Clone Bot Created!\n"
                f"Bot: @{bot_me.username} (<code>{bot_me.id}</code>)\n"
                f"Owner: {user.mention} (<code>{user.id}</code>)</b>"
            )
        except:
            pass

    except Exception as e:
        logger.error(f"Clone bot start error: {e}")
        await wait_msg.edit_text(
            f"<b>❌ Bot start nahi hua!</b>\n\n"
            f"Error: <code>{e}</code>\n\n"
            f"Possible reasons:\n"
            f"• Token galat hai\n"
            f"• Bot already kisi aur ne use kar liya\n\n"
            f"Dobara try karo: /createbot",
            parse_mode=enums.ParseMode.HTML
        )


# ═══════════════════════════════════════════════
#  /mybot
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("mybot") & filters.private)
@Client.on_callback_query(filters.regex("^my_bots$"))
async def mybot_cmd(client, update):
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
    else:
        user_id = update.from_user.id

    clone = await db.get_clone(user_id)
    if not clone:
        txt = "<b>❌ Aapka koi bot nahi hai.\n\n/createbot se naya banao!</b>"
        if isinstance(update, CallbackQuery):
            return await update.message.edit_text(
                txt,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 Bot Banao", callback_data="start_create")],
                    [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
                ]),
                parse_mode=enums.ParseMode.HTML
            )
        return await update.reply(txt, parse_mode=enums.ParseMode.HTML)

    from database.subscription_db import get_subscription
    bot_id    = clone.get("bot_id")
    bot_uname = clone.get("bot_username", "Unknown")
    sub = await get_subscription(bot_id)

    if sub:
        expiry    = sub.get("expiry")
        is_active_sub = sub.get("is_active", False)
        days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
        exp_str   = expiry.strftime("%d %b %Y") if expiry else "?"
        plan      = "Free Trial" if sub.get("is_free") else "Paid"
        status    = "✅ Active" if is_active_sub and days_left > 0 else "❌ Expired"
        sub_text  = f"📅 Expiry: {exp_str}\n⏳ {days_left} din bache\n💎 {plan} | {status}"
    else:
        sub_text = "⚠️ Subscription data nahi mila"

    text = (
        f"<b>📋 Aapka Bot</b>\n\n"
        f"🤖 @{bot_uname}\n"
        f"🆔 Bot ID: <code>{bot_id}</code>\n\n"
        f"{sub_text}"
    )
    btns = [
        [InlineKeyboardButton("⚙️ Settings", callback_data="manage_menu")],
        [
            InlineKeyboardButton("🗑️ Delete", callback_data="delbot_menu"),
            InlineKeyboardButton("📊 Sub Status", callback_data="my_sub_status"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
    ]
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    else:
        await update.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════
#  /delbot
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
        f"⚠️ Sure ho? Ye bot hamesha ke liye delete ho jayega!"
    )
    btns = [[
        InlineKeyboardButton("✅ Haan, Delete Karo", callback_data=f"confirm_delbot_{user_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data="go_home"),
    ]]
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    else:
        await update.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^confirm_delbot_(\d+)$"))
async def confirm_delbot_cb(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))
    if query.from_user.id != user_id and not await is_main_admin(query.from_user.id):
        return await query.answer("❌ Ye aapka bot nahi hai!", show_alert=True)

    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Bot nahi mila.", show_alert=True)

    bot_uname = clone.get("bot_username", "Unknown")
    bot_id = clone.get("bot_id")

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
        f"<b>✅ @{bot_uname} delete ho gaya!</b>\n\n/createbot se naya banao.",
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
#  /manage — Bot settings panel (UPDATED)
# ═══════════════════════════════════════════════
@Client.on_message(filters.command("manage") & filters.private)
async def manage_cmd(client, message: Message):
    await _show_manage_menu(client, message.from_user.id, message=message)


@Client.on_callback_query(filters.regex("^manage_menu$"))
async def manage_menu_cb(client, query: CallbackQuery):
    await _show_manage_menu(client, query.from_user.id, query=query)


async def _show_manage_menu(client, user_id, message=None, query=None):
    clone = await db.get_clone(user_id)
    if not clone:
        txt = "<b>❌ Pehle /createbot se bot banao.</b>"
        if query:
            return await query.message.edit_text(txt, parse_mode=enums.ParseMode.HTML)
        return await message.reply(txt, parse_mode=enums.ParseMode.HTML)

    bot_uname  = clone.get("bot_username", "Unknown")
    bot_id     = clone.get("bot_id")

    try:
        from database.ia_filterdb import col as _col, sec_col as _sec_col
        _file_cnt = _col.count_documents({}) + _sec_col.count_documents({})
    except Exception:
        _file_cnt = 0
    try:
        from AsFilterBot.database.clone_bot_userdb import clonedb as _cdb
        _user_cnt = await _cdb.total_users_count(bot_id)
    except Exception:
        _user_cnt = 0

    text = (
        f"<b>⚙️ Bot Settings — @{bot_uname}</b>\n\n"
        f"📁 Total Files: <b>{_file_cnt:,}</b>\n"
        f"👤 Bot Users: <b>{_user_cnt:,}</b>\n\n"
        f"👇 Kya change karna hai?"
    )
    btns = [
        [InlineKeyboardButton("📝 Welcome Message", callback_data="set_start_msg")],
        [InlineKeyboardButton("🔘 Custom Buttons", callback_data="manage_buttons")],
        [InlineKeyboardButton("📢 Update Channel", callback_data="set_update_ch")],
        [InlineKeyboardButton("🤖 My Clone Bot", callback_data="my_clone_bot_info")],
        [InlineKeyboardButton("🔗 Link Shortener", callback_data="set_shortlink_main")],
        [InlineKeyboardButton("👮 Moderators", callback_data="manage_mods")],
        [InlineKeyboardButton("💎 Plan Setup", callback_data="setup_clone_plan")],
        [InlineKeyboardButton("📂 Files Database", callback_data="files_database_btn")],
        [
            InlineKeyboardButton("📊 Stats", callback_data="manage_channel_stats"),
            InlineKeyboardButton("🔍 Health Check", callback_data="manage_health_check"),
        ],
        [InlineKeyboardButton("💳 Subscription", callback_data="my_sub_status")],
        [InlineKeyboardButton("🗑️ Delete Bot", callback_data="delbot_menu")],
        [InlineKeyboardButton("🔙 Back", callback_data="go_home")],
    ]
    if query:
        try:
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
        except:
            await query.answer()
    else:
        await message.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# ── My Clone Bot info ─────────────────────────────────────
@Client.on_callback_query(filters.regex("^my_clone_bot_info$"))
async def my_clone_bot_info_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)
    bot_uname = clone.get("bot_username", "?")
    bot_id = clone.get("bot_id")
    running = any(True for b in getattr(temp, "BOTS", []) if True)
    await query.message.edit_text(
        f"<b>🤖 Your Clone Bot</b>\n\n"
        f"Username: @{bot_uname}\n"
        f"Bot ID: <code>{bot_id}</code>\n"
        f"Server: {MAIN_BOT_NAME}\n\n"
        f"Ye bot hamare server par chal raha hai.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Set Shortlink (main bot level) ────────────────────────
@Client.on_callback_query(filters.regex("^set_shortlink_main$"))
async def set_shortlink_main_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    bot_id = clone.get("bot_id")
    bot_data = await db.get_bot(bot_id)
    current_url = bot_data.get("shortlink_url") or "Set nahi hai"

    await query.message.edit_text(
        f"<b>🔗 Link Shortener Set Karo</b>\n\n"
        f"Current: <code>{current_url}</code>\n\n"
        f"2 lines mein bhejo:\n"
        f"<code>shortlink.com\nabc123apikey</code>\n\n"
        f"👉 Bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return
    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("❌ Cancel.")

    lines = (reply.text or "").strip().split("\n")
    if len(lines) < 2:
        return await reply.reply("❌ 2 lines chahiye: URL aur API key")

    sl_url = lines[0].strip().replace("https://", "").replace("http://", "")
    sl_api = lines[1].strip()
    await db.update_bot(bot_id, {"shortlink_url": sl_url, "shortlink_api": sl_api, "is_shortlink": True})
    await reply.reply(
        f"<b>✅ Shortlink set!</b>\nURL: {sl_url}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Settings", callback_data="manage_menu")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Moderators ────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^manage_mods$"))
async def manage_mods_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    bot_id = clone.get("bot_id")
    bot_data = await db.get_bot(bot_id)
    mods = bot_data.get("moderators") or []

    lines = ["<b>👮 Moderators</b>\n"]
    if mods:
        for m in mods:
            lines.append(f"• <code>{m.get('user_id')}</code> — @{m.get('username','N/A')}")
    else:
        lines.append("<i>Koi moderator nahi abhi.</i>")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Mod", callback_data="mod_add")],
            [InlineKeyboardButton("➖ Remove Mod", callback_data="mod_remove")],
            [InlineKeyboardButton("🔄 Transfer Bot", callback_data="mod_transfer")],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^mod_add$"))
async def mod_add_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>➕ Moderator Add Karo</b>\n\nJis user ko mod banana hai uska Telegram ID bhejo:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_mods")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=60)
    except asyncio.TimeoutError:
        return

    if not reply.text or not reply.text.strip().isdigit():
        return await reply.reply("❌ Sirf numeric ID bhejo.")

    new_mod_id = int(reply.text.strip())
    username = ""
    try:
        u = await client.get_users(new_mod_id)
        username = u.username or ""
    except:
        pass

    bot_id = clone.get("bot_id")
    bot_data = await db.get_bot(bot_id)
    mods = bot_data.get("moderators") or []
    if any(m.get("user_id") == new_mod_id for m in mods):
        return await reply.reply("❌ Ye user pehle se moderator hai!")
    mods.append({"user_id": new_mod_id, "username": username})
    await db.update_bot(bot_id, {"moderators": mods})
    await reply.reply(
        f"<b>✅ Moderator add ho gaya!</b>\nID: <code>{new_mod_id}</code>\n@{username or 'N/A'}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👮 Moderators", callback_data="manage_mods")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^mod_remove$"))
async def mod_remove_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    bot_id = clone.get("bot_id")
    bot_data = await db.get_bot(bot_id)
    mods = bot_data.get("moderators") or []
    if not mods:
        return await query.answer("Koi moderator nahi hai.", show_alert=True)

    lines = ["<b>➖ Moderator Remove Karo</b>\n\nJis ka ID bhejo:"]
    for m in mods:
        lines.append(f"• <code>{m.get('user_id')}</code> @{m.get('username','N/A')}")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_mods")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=60)
    except asyncio.TimeoutError:
        return

    if not reply.text or not reply.text.strip().isdigit():
        return await reply.reply("❌ Sirf numeric ID bhejo.")

    remove_id = int(reply.text.strip())
    new_mods = [m for m in mods if m.get("user_id") != remove_id]
    if len(new_mods) == len(mods):
        return await reply.reply("❌ Ye ID moderators mein nahi mila.")
    await db.update_bot(bot_id, {"moderators": new_mods})
    await reply.reply(
        f"<b>✅ Moderator remove ho gaya!</b>\nID: <code>{remove_id}</code>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👮 Moderators", callback_data="manage_mods")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^mod_transfer$"))
async def mod_transfer_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>🔄 Bot Transfer Karo</b>\n\n"
        "Jis user ko bot transfer karna hai uska <b>Telegram ID</b> bhejo.\n\n"
        "⚠️ Ye action permanent hai! Aapka ownership chala jayega.\n\n"
        "ID bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="manage_mods")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=60)
    except asyncio.TimeoutError:
        return

    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("❌ Cancel.")
    if not reply.text or not reply.text.strip().isdigit():
        return await reply.reply("❌ Sirf numeric ID bhejo.")

    new_owner_id = int(reply.text.strip())
    bot_id = clone.get("bot_id")
    bot_uname = clone.get("bot_username", "?")

    # Update bot ownership
    await db.update_bot(bot_id, {"user_id": new_owner_id})
    await db.db.clone_bots.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": new_owner_id}}
    )
    await reply.reply(
        f"<b>✅ Bot Transfer Ho Gaya!</b>\n\n"
        f"Bot @{bot_uname} ab user <code>{new_owner_id}</code> ke paas hai.",
        parse_mode=enums.ParseMode.HTML
    )
    try:
        await client.send_message(
            new_owner_id,
            f"<b>🎉 Aapko bot @{bot_uname} transfer kiya gaya hai!</b>\n\n"
            f"Ab aap is bot ke owner hain. /manage se settings manage karein.",
            parse_mode=enums.ParseMode.HTML
        )
    except:
        pass


# ── Plan Setup from main bot ──────────────────────────────
@Client.on_callback_query(filters.regex("^setup_clone_plan$"))
async def setup_clone_plan_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    bot_id = clone.get("bot_id")
    bot_data = await db.get_bot(bot_id)
    plans = bot_data.get("premium_plans") or []

    current = "\n".join([
        f"{i+1}. {p.get('name')} — ₹{p.get('price')} — {p.get('days')} days"
        for i, p in enumerate(plans)
    ]) if plans else "Koi plan set nahi abhi."

    await query.message.edit_text(
        f"<b>💎 Plan Setup — Apne Clone Bot Ke Liye</b>\n\n"
        f"<b>Current Plans:</b>\n{current}\n\n"
        f"Ye plans aapke clone bot mein /plan command par dikhenge.\n"
        f"Users in plans se aapko pay karenge.\n\n"
        f"Kya karna hai?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Plan Add Karo", callback_data="plan_setup_add")],
            [InlineKeyboardButton("🗑️ Saare Plans Delete", callback_data="plan_setup_clear")],
            [InlineKeyboardButton("💳 Payment Details Set", callback_data="plan_setup_payment")],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^plan_setup_add$"))
async def plan_setup_add_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>➕ Naya Plan Add Karo</b>\n\n"
        "4 lines mein bhejo:\n"
        "<code>Plan Name\nPrice (number)\nDays\nDescription</code>\n\n"
        "Example:\n"
        "<code>Gold Plan\n99\n30\nHD movies + fast download</code>\n\n"
        "👉 Bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="setup_clone_plan")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return
    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("❌ Cancel.")

    lines = (reply.text or "").strip().split("\n")
    if len(lines) < 3:
        return await reply.reply("❌ Minimum 3 lines: Name, Price, Days")

    name = lines[0].strip()
    price = lines[1].strip()
    days = lines[2].strip()
    desc = lines[3].strip() if len(lines) > 3 else ""

    if not price.isdigit() or not days.isdigit():
        return await reply.reply("❌ Price aur Days sirf numbers hone chahiye.")

    bot_id = clone.get("bot_id")
    bot_data = await db.get_bot(bot_id)
    plans = bot_data.get("premium_plans") or []
    plans.append({"name": name, "price": int(price), "days": int(days), "description": desc})
    await db.update_bot(bot_id, {"premium_plans": plans})
    await reply.reply(
        f"<b>✅ Plan add ho gaya!</b>\n{name} — ₹{price} — {days} days",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Plans Dekho", callback_data="setup_clone_plan")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^plan_setup_clear$"))
async def plan_setup_clear_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)
    await db.update_bot(clone.get("bot_id"), {"premium_plans": []})
    await query.answer("✅ Saare plans delete ho gaye!", show_alert=True)
    await setup_clone_plan_cb(client, query)


@Client.on_callback_query(filters.regex("^plan_setup_payment$"))
async def plan_setup_payment_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>💳 Payment Details Set Karo</b>\n\n"
        "3 lines mein bhejo:\n"
        "<code>UPI ID\n@TelegramUsername\nNote for users</code>\n\n"
        "Example:\n"
        "<code>1234567890@ybl\n@yourname\nPayment ke baad screenshot bhejo</code>\n\n"
        "👉 Bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="setup_clone_plan")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return
    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("❌ Cancel.")

    lines = (reply.text or "").strip().split("\n")
    upi = lines[0].strip() if len(lines) > 0 else ""
    username = lines[1].strip() if len(lines) > 1 else ""
    note = lines[2].strip() if len(lines) > 2 else "Screenshot bhejne ke baad activate hoga."

    await db.update_bot(clone.get("bot_id"), {"payment_details": {
        "upi_id": upi, "username": username, "note": note
    }})
    await reply.reply(
        f"<b>✅ Payment details set ho gayi!</b>\nUPI: {upi}\nContact: {username}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Plans Dekho", callback_data="setup_clone_plan")]]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Welcome Message / Buttons / Update Channel ────────────
@Client.on_callback_query(filters.regex("^set_start_msg$"))
async def set_start_msg_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📝 Welcome Message Set Karo</b>\n\nApna custom welcome message bhejo.\nHTML tags allowed.\n\n👉 Message bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
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
        "<b>✅ Welcome message set ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Settings", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )


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
        lines.append("Koi button nahi hai.")
    lines.append("\n👇 Kya karna hai?")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Button Add Karo", callback_data="add_button")],
            [InlineKeyboardButton("🗑️ Saare Buttons Hatao", callback_data="clear_buttons")],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^add_button$"))
async def add_button_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    await query.message.edit_text(
        "<b>➕ Naya Button Add Karo</b>\n\n"
        "Format:\n<code>Button Text | https://link.com</code>\n\n"
        "Example:\n<code>📢 Join Channel | https://t.me/asbhai_bsr</code>\n\n"
        "👉 Bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_buttons")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return
    if reply.text and reply.text.strip() in ["/cancel"]:
        return await reply.reply("❌ Cancel.")

    text = reply.text or ""
    if "|" not in text:
        return await reply.reply("❌ Format galat! <code>Text | URL</code> use karo.", parse_mode=enums.ParseMode.HTML)

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
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Buttons", callback_data="manage_buttons")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^clear_buttons$"))
async def clear_buttons_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    await db.update_clone(user_id, {"start_buttons": []})
    await query.answer("✅ Saare buttons hata diye!", show_alert=True)
    await manage_buttons_cb(client, query)


@Client.on_callback_query(filters.regex("^set_update_ch$"))
async def set_update_ch_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.message.edit_text(
        "<b>📢 Update Channel Set Karo</b>\n\nChannel link bhejo:\n<code>https://t.me/yourchannel</code>\n\n👉 Link bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except asyncio.TimeoutError:
        return
    if reply.text and reply.text.strip() in ["/cancel"]:
        return await reply.reply("❌ Cancel.")

    url = reply.text.strip() if reply.text else ""
    if not url.startswith("https://t.me/"):
        return await reply.reply("❌ t.me link hona chahiye.")

    await db.update_clone(user_id, {"update_channel_link": url})
    await reply.reply(
        "<b>✅ Update channel set ho gaya!</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Settings", callback_data="manage_menu")]]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Subscription Status ────────────────────────────────────
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

    expiry    = sub.get("expiry")
    active    = sub.get("is_active", False)
    is_free   = sub.get("is_free", True)
    days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
    exp_str   = expiry.strftime("%d %b %Y") if expiry else "?"
    bot_uname = sub.get("bot_username", "?")

    text = (
        f"<b>📊 Subscription Status</b>\n\n"
        f"🤖 Bot: @{bot_uname}\n"
        f"📅 Expiry: {exp_str}\n"
        f"⏳ Bacha: {days_left} din\n"
        f"💎 Plan: {'Free Trial (30 days)' if is_free else 'Paid'}\n"
        f"Status: {'✅ Active' if active and days_left > 0 else '❌ Expired'}\n\n"
        f"<b>Available Plans:</b>\n"
        f"📦 1 Month — Contact support\n"
        f"📦 2 Month — Contact support\n\n"
        f"Renew ke liye: @aschat_group"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)],
            [InlineKeyboardButton("🔙 Back", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Channel Stats & Health Check ──────────────────────────
@Client.on_callback_query(filters.regex("^manage_channel_stats$"))
async def manage_channel_stats_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.answer("📁 Fetching...")

    bot_id    = clone.get("bot_id")
    bot_uname = clone.get("bot_username", "?")
    bot_data  = await db.get_bot(bot_id)

    try:
        from database.ia_filterdb import col as _col, sec_col as _sec_col
        primary_cnt = _col.count_documents({})
        sec_cnt     = _sec_col.count_documents({})
        total_files = primary_cnt + sec_cnt
        ch_ids = set(c for c in (_col.distinct("channel_id") + _sec_col.distinct("channel_id")) if c)
    except Exception:
        primary_cnt = sec_cnt = total_files = 0
        ch_ids = set()

    try:
        from AsFilterBot.database.clone_bot_userdb import clonedb as _cdb
        user_cnt  = await _cdb.total_users_count(bot_id)
    except Exception:
        user_cnt = 0

    fsub = bot_data.get("fsub_channel")
    fsub_str = f"<code>{fsub}</code>" if fsub else "❌ Set Nahi"
    update_ch = bot_data.get("update_channel_link") or "❌ Set Nahi"

    ch_lines = []
    for ch_id in list(ch_ids)[:5]:
        cnt = _col.count_documents({"channel_id": ch_id}) + _sec_col.count_documents({"channel_id": ch_id})
        ch_lines.append(f"  📁 <code>{ch_id}</code> — {cnt:,} files")
    if len(ch_ids) > 5:
        ch_lines.append(f"  … aur {len(ch_ids)-5} channels")
    indexed_text = "\n".join(ch_lines) if ch_lines else "  ❌ Koi channel indexed nahi"

    text = (
        f"<b>📊 @{bot_uname} — Stats</b>\n\n"
        f"📦 Files: {total_files:,}\n"
        f"📡 Indexed Channels: {len(ch_ids)}\n"
        f"{indexed_text}\n\n"
        f"👥 Users: {user_cnt:,}\n"
        f"🔒 FSub: {fsub_str}"
    )

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Health Check", callback_data="manage_health_check")],
            [InlineKeyboardButton("🔙 Settings", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^manage_health_check$"))
async def manage_health_check_cb(client, query: CallbackQuery):
    user_id = query.from_user.id
    clone   = await db.get_clone(user_id)
    if not clone:
        return await query.answer("Pehle bot banao!", show_alert=True)

    await query.answer("🔍 Checking...")
    bot_id    = clone.get("bot_id")
    bot_uname = clone.get("bot_username", "?")
    bot_data  = await db.get_bot(bot_id)
    checks = []

    running = False
    for b in getattr(temp, "BOTS", []):
        try:
            me = await b.get_me()
            if me.id == bot_id:
                running = True
                break
        except:
            pass
    checks.append("✅ Bot Running" if running else "❌ Bot Not Running")

    try:
        from database.ia_filterdb import col as _col, sec_col as _sec_col
        fc = _col.count_documents({}) + _sec_col.count_documents({})
        checks.append(f"✅ Files: {fc:,} indexed" if fc > 0 else "❌ Files: 0 — /index karo")
    except:
        checks.append("⚠️ Files: Check nahi hua")

    try:
        sub = await get_subscription(bot_id)
        if sub and sub.get("is_active"):
            expiry = sub.get("expiry")
            days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
            if days_left > 7:
                checks.append(f"✅ Subscription: {days_left} din bache")
            elif days_left > 0:
                checks.append(f"⚠️ Subscription: Sirf {days_left} din! Renew karo")
            else:
                checks.append("❌ Subscription: Expire!")
        else:
            checks.append("❌ Subscription: Active nahi!")
    except:
        checks.append("⚠️ Subscription: Check nahi hua")

    sl_url = bot_data.get("shortlink_url")
    sl_api = bot_data.get("shortlink_api")
    checks.append(f"✅ Shortlink: {sl_url}" if sl_url and sl_api else "⚠️ Shortlink: Set nahi")

    fails = sum(1 for c in checks if c.startswith("❌"))
    warns = sum(1 for c in checks if c.startswith("⚠️"))
    overall = "✅ Sab theek!" if fails == 0 and warns == 0 else (f"⚠️ {warns} warning(s)" if fails == 0 else f"❌ {fails} issue(s)")

    text = (
        f"<b>🔍 Health Check — @{bot_uname}</b>\n\n"
        + "\n".join(checks) +
        f"\n\n<b>Overall: {overall}</b>"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Re-check", callback_data="manage_health_check")],
            [InlineKeyboardButton("📊 Stats", callback_data="manage_channel_stats")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="manage_menu")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^main_copyright$"))
async def main_copyright_cb(client, query):
    await query.answer(
        "🔒 Auto Filter service.\nFiles third-party sources se automatically index hoti hain.",
        show_alert=True
    )


# ════════════════════════════════════════════════════════════
#  FREE TRIAL ABUSE FIX — createbot mein check
#  Ek user = ek baar free trial
#  Delete karke dobara nahi bana sakta
# ════════════════════════════════════════════════════════════
# Ye function commands.py ke _start_createbot ke start par call hota hai
# Already upar likhe _start_createbot mein ye check add karein:
# Patch: neeche wala override karta hai upar ka _start_createbot

async def _start_createbot(client, message, user=None):
    """Overridden: includes free trial abuse check"""
    if user is None:
        user = message.from_user

    user_id = user.id

    # ── Free trial abuse check ─────────────────────────────
    try:
        trial_doc = await db.db.used_free_trials.find_one({"user_id": user_id})
        if trial_doc:
            # User pehle free trial use kar chuka hai
            await client.send_message(
                user_id,
                "<b>⚠️ Aapka Free Trial Pehle Se Use Ho Chuka Hai!</b>\n\n"
                "Aap ek baar bot bana chuke ho. Delete karke dobara free mein nahi bana sakte.\n\n"
                "<b>Options:</b>\n"
                "💳 Subscription kharido aur naya bot banao\n"
                "🔄 Ya apna purana bot reactivate karo\n\n"
                "Support ke liye: @aschat_group",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 Support", url="https://t.me/aschat_group")],
                    [InlineKeyboardButton("🏠 Home", callback_data="go_home")],
                ]),
                parse_mode=enums.ParseMode.HTML
            )
            return
    except Exception as e:
        logger.warning(f"Trial check error: {e}")

    # ── Existing bot check ─────────────────────────────────
    if await db.is_clone_exist(user_id):
        clone = await db.get_clone(user_id)
        bot_uname = clone.get("bot_username", "Unknown")
        await client.send_message(
            user_id,
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
        user_id,
        "<b>🤖 Bot Banane Ki Process:</b>\n\n"
        "<b>1️⃣</b> @BotFather pe jao\n"
        "<b>2️⃣</b> /newbot bhejo\n"
        "<b>3️⃣</b> Bot ka naam do\n"
        "<b>4️⃣</b> Username do\n"
        "<b>5️⃣</b> BotFather ka confirmation message yahan <b>forward</b> karo\n\n"
        "⏱️ 5 minute ka time. /cancel se rokein.\n\n"
        "👇 BotFather ka message forward karo ya token paste karo:",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        reply = await client.listen(user_id, timeout=300)
    except asyncio.TimeoutError:
        return await guide_msg.edit_text("<b>⏰ Timeout! Dobara /createbot karo.</b>")

    if reply.text and reply.text.strip() == "/cancel":
        return await reply.reply("<b>❌ Process cancel kar diya.</b>")

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
            "<b>❌ Token nahi mila!</b>\n\nBotFather ka message forward karo ya token paste karo.\nDobara /createbot karo.",
            parse_mode=enums.ParseMode.HTML
        )

    wait_msg = await reply.reply("⏳ <b>Bot start ho raha hai... 30 sec wait karo</b>", parse_mode=enums.ParseMode.HTML)

    try:
        from info import API_ID, API_HASH
        from pyrogram import Client as PyroClient
        new_bot = PyroClient(
            f"clone_{bot_token[:8]}",
            API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "AsFilterBot"},
        )
        await new_bot.start()
        bot_me = await new_bot.get_me()

        await db.add_clone_bot(
            bot_id=bot_me.id,
            user_id=user_id,
            bot_token=bot_token,
            bot_username=bot_me.username or ""
        )
        from database.subscription_db import create_subscription
        await create_subscription(bot_me.id, user_id, bot_me.username or "")

        # ── Free trial record save karo ──────────────────────
        try:
            await db.db.used_free_trials.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id,
                    "bot_id": bot_me.id,
                    "bot_username": bot_me.username,
                    "created_at": datetime.datetime.now()
                }},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Trial record save error: {e}")

        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(new_bot)

        # Queue tracking mein add karo
        try:
            from plugins.clone import _bot_clients, touch_bot
            _bot_clients[bot_me.id] = new_bot
            touch_bot(bot_me.id)
        except: pass

        await wait_msg.edit_text(
            f"<b>🎉 Bot Successfully Bana!</b>\n\n"
            f"🤖 Bot: @{bot_me.username}\n"
            f"🆔 Bot ID: <code>{bot_me.id}</code>\n\n"
            f"✅ 30 din ka free trial shuru!\n\n"
            f"<b>Ab kya karo:</b>\n"
            f"1. Apne group mein @{bot_me.username} add karo\n"
            f"2. /manage se settings set karo\n"
            f"3. Files ke liye /manage → Files Database",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Bot Settings", callback_data="manage_menu")],
                [InlineKeyboardButton("🏠 Home", callback_data="go_home")],
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"<b>🤖 New Clone Bot Created!\n"
                f"Bot: @{bot_me.username} (<code>{bot_me.id}</code>)\n"
                f"Owner: {user.mention} (<code>{user_id}</code>)</b>"
            )
        except: pass

    except Exception as e:
        logger.error(f"Clone bot start error: {e}")
        await wait_msg.edit_text(
            f"<b>❌ Bot start nahi hua!</b>\n\n"
            f"Error: <code>{e}</code>\n\n"
            f"Possible reasons:\n"
            f"• Token galat hai\n"
            f"• Bot already kisi aur ne use kar liya\n\n"
            f"Dobara try karo: /createbot",
            parse_mode=enums.ParseMode.HTML
        )
