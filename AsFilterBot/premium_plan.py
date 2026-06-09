# ════════════════════════════════════════════════════════════
#   Clone Bot Premium Plans — Fully Customizable
#   Clone owner apne khud ke plans set kare + payment details
# ════════════════════════════════════════════════════════════
import asyncio, logging, datetime
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ListenerTimeout
from database.users_chats_db import db
from info import ADMINS
from clone_filter import clone_admin

logger = logging.getLogger(__name__)


async def _is_owner(client, user_id):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    return user_id == bd.get("user_id") or user_id in ADMINS


# ── /plan — Show current plans to users ──────────────────────
@Client.on_message(filters.command("plan") & filters.incoming)
async def plan_cmd(client, message: Message):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    plans = bd.get("premium_plans") or []
    payment = bd.get("payment_details") or {}

    if not plans:
        return await message.reply(
            "<b>💎 Premium Plans</b>\n\n"
            "Abhi koi plan set nahi hai.\n"
            "Bot owner se contact karo.",
            parse_mode=enums.ParseMode.HTML
        )

    text = "<b>💎 Premium Plans</b>\n\n"
    btns = []
    for i, plan in enumerate(plans):
        name = plan.get("name", f"Plan {i+1}")
        price = plan.get("price", "?")
        days = plan.get("days", 30)
        desc = plan.get("description", "")
        text += f"<b>{name}</b>\n💰 Price: ₹{price}\n📅 Duration: {days} days\n"
        if desc:
            text += f"📝 {desc}\n"
        text += "\n"
        btns.append([InlineKeyboardButton(f"💎 {name} - ₹{price}", callback_data=f"buy_plan_{i}")])

    if payment.get("upi_id") or payment.get("username"):
        btns.append([InlineKeyboardButton("💳 Payment Info", callback_data="show_payment")])

    await message.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^buy_plan_(\d+)$"))
async def buy_plan_cb(client, query):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    plans = bd.get("premium_plans") or []
    payment = bd.get("payment_details") or {}
    idx = int(query.matches[0].group(1))

    if idx >= len(plans):
        return await query.answer("Plan nahi mila!", show_alert=True)

    plan = plans[idx]
    name = plan.get("name", "Plan")
    price = plan.get("price", "?")
    days = plan.get("days", 30)
    upi = payment.get("upi_id", "")
    username = payment.get("username", "")
    note = payment.get("note", "Screenshot bhejne ke baad plan activate hoga.")

    text = (
        f"<b>💎 {name} Purchase</b>\n\n"
        f"💰 Amount: <b>₹{price}</b>\n"
        f"📅 Duration: {days} days\n\n"
        f"<b>Payment Details:</b>\n"
    )
    if upi:
        text += f"🏦 UPI: <code>{upi}</code>\n"
    if username:
        text += f"📱 Contact: {username}\n"
    text += f"\n📌 {note}"

    btns = []
    if username:
        btns.append([InlineKeyboardButton("📩 Screenshot Bhejo", url=f"https://t.me/{username.lstrip('@')}")])
    btns.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")])

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^show_payment$"))
async def show_payment_cb(client, query):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    payment = bd.get("payment_details") or {}
    upi = payment.get("upi_id", "")
    username = payment.get("username", "")
    note = payment.get("note", "")

    text = "<b>💳 Payment Details</b>\n\n"
    if upi:
        text += f"🏦 UPI ID: <code>{upi}</code>\n"
    if username:
        text += f"📱 Contact: {username}\n"
    if note:
        text += f"\n📌 {note}"

    btns = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")]]
    if username:
        btns.insert(0, [InlineKeyboardButton("📩 Contact Owner", url=f"https://t.me/{username.lstrip('@')}")])

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^back_to_plans$"))
async def back_to_plans_cb(client, query):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    plans = bd.get("premium_plans") or []
    payment = bd.get("payment_details") or {}

    text = "<b>💎 Premium Plans</b>\n\n"
    btns = []
    for i, plan in enumerate(plans):
        name = plan.get("name", f"Plan {i+1}")
        price = plan.get("price", "?")
        days = plan.get("days", 30)
        desc = plan.get("description", "")
        text += f"<b>{name}</b>\n💰 ₹{price} | 📅 {days} days\n"
        if desc: text += f"📝 {desc}\n"
        text += "\n"
        btns.append([InlineKeyboardButton(f"💎 {name} - ₹{price}", callback_data=f"buy_plan_{i}")])
    if payment.get("upi_id") or payment.get("username"):
        btns.append([InlineKeyboardButton("💳 Payment Info", callback_data="show_payment")])

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# ── /myplan — User apna plan dekhe ───────────────────────────
@Client.on_message(filters.command("myplan") & filters.incoming)
async def myplan_cmd(client, message: Message):
    user_id = message.from_user.id
    try:
        user_data = await db.get_user(user_id)
        is_premium = user_data.get("is_premium", False)
        expiry = user_data.get("expiry_time")
        if is_premium and expiry:
            days_left = max(0, (expiry - datetime.datetime.now()).days)
            exp_str = expiry.strftime("%d %b %Y")
            if days_left > 0:
                return await message.reply(
                    f"<b>💎 Aapka Premium Plan Active Hai!</b>\n\n"
                    f"📅 Expiry: {exp_str}\n"
                    f"⏳ Remaining: {days_left} days",
                    parse_mode=enums.ParseMode.HTML
                )
        await message.reply(
            "<b>❌ Aapke paas koi premium plan nahi hai.</b>\n\n"
            "/plan se plan dekho aur purchase karo.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Plans Dekho", callback_data="back_to_plans")]]),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ════════════════════════════════════════════════════════════
#   ADMIN: Premium Plans Setup
#   /setplans — Plans set karo (clone owner ke liye)
# ════════════════════════════════════════════════════════════
@Client.on_message(filters.command("setplans") & clone_admin & filters.private)
async def setplans_cmd(client, message: Message):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    plans = bd.get("premium_plans") or []

    current = "\n".join([
        f"{i+1}. {p.get('name')} — ₹{p.get('price')} — {p.get('days')} days"
        for i, p in enumerate(plans)
    ]) if plans else "Koi plan nahi hai abhi."

    await message.reply(
        f"<b>⚙️ Premium Plans Setup</b>\n\n"
        f"<b>Current Plans:</b>\n{current}\n\n"
        f"Kya karna hai?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Plan Add Karo", callback_data="admin_add_plan")],
            [InlineKeyboardButton("🗑️ Saare Plans Delete Karo", callback_data="admin_clear_plans")],
            [InlineKeyboardButton("💳 Payment Details Set Karo", callback_data="admin_set_payment")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_add_plan$"))
async def admin_add_plan_cb(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf Owner!", show_alert=True)
    user_id = query.from_user.id
    await query.message.edit_text(
        "<b>➕ Naya Plan Add Karo</b>\n\n"
        "Is format mein ek ek line mein bhejo:\n"
        "<code>Plan Name\nPrice (sirf number)\nDays\nDescription (optional)</code>\n\n"
        "Example:\n"
        "<code>Gold Plan\n99\n30\nHD movies access + fast download</code>\n\n"
        "👉 Bhejo ya /cancel karo:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_plans_back")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except (asyncio.TimeoutError, ListenerTimeout):
        return
    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("❌ Cancel.")

    lines = (reply.text or "").strip().split("\n")
    if len(lines) < 3:
        return await reply.reply("❌ Minimum 3 lines chahiye: Name, Price, Days")

    name = lines[0].strip()
    price = lines[1].strip()
    days = lines[2].strip()
    desc = lines[3].strip() if len(lines) > 3 else ""

    if not price.isdigit() or not days.isdigit():
        return await reply.reply("❌ Price aur Days sirf numbers hone chahiye.")

    me = await client.get_me()
    bd = await db.get_bot(me.id)
    plans = bd.get("premium_plans") or []
    plans.append({"name": name, "price": int(price), "days": int(days), "description": desc})
    await db.update_bot(me.id, {"premium_plans": plans})

    await reply.reply(
        f"<b>✅ Plan add ho gaya!</b>\n\n"
        f"Name: {name}\nPrice: ₹{price}\nDays: {days} days\n"
        f"Description: {desc or 'N/A'}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Manage Plans", callback_data="admin_plans_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_clear_plans$"))
async def admin_clear_plans_cb(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf Owner!", show_alert=True)
    me = await client.get_me()
    await db.update_bot(me.id, {"premium_plans": []})
    await query.answer("✅ Saare plans delete ho gaye!", show_alert=True)
    await setplans_from_cb(client, query)


@Client.on_callback_query(filters.regex("^admin_plans_back$"))
async def setplans_from_cb(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf Owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    plans = bd.get("premium_plans") or []
    current = "\n".join([
        f"{i+1}. {p.get('name')} — ₹{p.get('price')} — {p.get('days')} days"
        for i, p in enumerate(plans)
    ]) if plans else "Koi plan nahi hai abhi."
    await query.message.edit_text(
        f"<b>⚙️ Premium Plans Setup</b>\n\n<b>Current Plans:</b>\n{current}\n\nKya karna hai?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Plan Add Karo", callback_data="admin_add_plan")],
            [InlineKeyboardButton("🗑️ Saare Plans Delete Karo", callback_data="admin_clear_plans")],
            [InlineKeyboardButton("💳 Payment Details Set Karo", callback_data="admin_set_payment")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^admin_set_payment$"))
async def admin_set_payment_cb(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf Owner!", show_alert=True)
    user_id = query.from_user.id
    await query.message.edit_text(
        "<b>💳 Payment Details Set Karo</b>\n\n"
        "Is format mein bhejo:\n"
        "<code>UPI ID\nTelegram Username\nNote for users</code>\n\n"
        "Example:\n"
        "<code>1234567890@ybl\n@yourusername\nPayment ke baad screenshot bhejo</code>\n\n"
        "👉 Bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_plans_back")]]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except (asyncio.TimeoutError, ListenerTimeout):
        return
    if reply.text and reply.text.strip().lower() == "/cancel":
        return await reply.reply("❌ Cancel.")

    lines = (reply.text or "").strip().split("\n")
    upi = lines[0].strip() if len(lines) > 0 else ""
    username = lines[1].strip() if len(lines) > 1 else ""
    note = lines[2].strip() if len(lines) > 2 else "Screenshot bhejne ke baad activate hoga."

    me = await client.get_me()
    await db.update_bot(me.id, {"payment_details": {
        "upi_id": upi,
        "username": username,
        "note": note
    }})
    await reply.reply(
        f"<b>✅ Payment details set ho gayi!</b>\n\nUPI: {upi}\nUsername: {username}\nNote: {note}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Manage Plans", callback_data="admin_plans_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Admin: Manually give premium ─────────────────────────────
@Client.on_message(filters.command("add_premium") & clone_admin & filters.private)
async def add_premium_cmd(client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.reply(
            "<b>Usage:</b> <code>/add_premium user_id days</code>",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        user_id = int(args[1])
        days = int(args[2])
        expiry = datetime.datetime.now() + datetime.timedelta(days=days)
        await db.col.update_one(
            {"id": user_id},
            {"$set": {"is_premium": True, "expiry_time": expiry}},
            upsert=True
        )
        await message.reply(
            f"<b>✅ Premium diya!</b>\nUser: <code>{user_id}</code>\nDays: {days}\nExpiry: {expiry.strftime('%d %b %Y')}",
            parse_mode=enums.ParseMode.HTML
        )
        try:
            await client.send_message(
                user_id,
                f"<b>🎉 Aapko {days} din ka Premium mil gaya!\nExpiry: {expiry.strftime('%d %b %Y')}</b>",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("remove_premium") & clone_admin & filters.private)
async def remove_premium_cmd(client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply("<b>Usage:</b> <code>/remove_premium user_id</code>", parse_mode=enums.ParseMode.HTML)
    try:
        user_id = int(args[1])
        await db.col.update_one({"id": user_id}, {"$set": {"is_premium": False}})
        await message.reply(f"<b>✅ Premium hataya!</b>\nUser: <code>{user_id}</code>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command(["premiumusers", "pmusers"]) & clone_admin)
async def premiumusers_cmd(client, message: Message):
    try:
        premium_users = []
        async for u in db.col.find({"is_premium": True}):
            premium_users.append(u)
        if not premium_users:
            return await message.reply("<b>📭 Koi premium user nahi.</b>", parse_mode=enums.ParseMode.HTML)
        lines = [f"<b>💎 Premium Users ({len(premium_users)}):</b>\n"]
        for u in premium_users[:30]:
            uid = u.get("id", "?")
            exp = u.get("expiry_time")
            days_left = max(0, (exp - datetime.datetime.now()).days) if exp else 0
            lines.append(f"• <code>{uid}</code> — {days_left}d left")
        await message.reply("\n".join(lines), parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("genredeem") & clone_admin)
async def genredeem_cmd(client, message: Message):
    args = message.command
    count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
    days  = int(args[2]) if len(args) > 2 and args[2].isdigit() else 30
    import random, string
    codes = []
    for _ in range(min(count, 20)):
        code = "PREM-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        me = await client.get_me()
        bd = await db.get_bot(me.id)
        redeem_codes = bd.get("redeem_codes") or {}
        redeem_codes[code] = days
        await db.update_bot(me.id, {"redeem_codes": redeem_codes})
        codes.append(code)
    code_list = "\n".join([f"<code>{c}</code> ({days} days)" for c in codes])
    await message.reply(f"<b>🎁 {len(codes)} Codes:</b>\n\n{code_list}", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("redeem") & filters.incoming)
async def redeem_cmd(client, message: Message):
    code = message.command[1] if len(message.command) > 1 else ""
    if not code:
        return await message.reply("<b>Usage:</b> <code>/redeem CODE</code>", parse_mode=enums.ParseMode.HTML)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    redeem_codes = bd.get("redeem_codes") or {}
    if code not in redeem_codes:
        return await message.reply("<b>❌ Invalid ya already used code!</b>", parse_mode=enums.ParseMode.HTML)
    days = redeem_codes.pop(code)
    await db.update_bot(me.id, {"redeem_codes": redeem_codes})
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    user_id = message.from_user.id
    await db.col.update_one({"id": user_id}, {"$set": {"is_premium": True, "expiry_time": expiry}}, upsert=True)
    await message.reply(
        f"<b>🎉 Premium Activate!</b>\nDays: {days}\nExpiry: {expiry.strftime('%d %b %Y')}",
        parse_mode=enums.ParseMode.HTML
    )
