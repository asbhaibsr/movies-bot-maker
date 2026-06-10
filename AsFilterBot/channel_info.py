# ════════════════════════════════════════════════════════════
#  Clone Bot — Channel Info + Stats
#  /channel  — Admin: Connected channels aur file DB info
#  /cstats   — Users + Admin: Detailed stats
# ════════════════════════════════════════════════════════════

import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.ia_filterdb import col, sec_col
from database.users_chats_db import db
from AsFilterBot.database.clone_bot_userdb import clonedb
from clone_filter import clone_admin, clone_or_group_admin
from info import ADMINS
import asyncio

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  /channel — Clone bot ka channel info (Admin only)
# ═══════════════════════════════════════════════════════════
@Client.on_message(filters.command("channel") & clone_admin)
async def channel_info_cmd(client, message: Message):
    """
    Konsa channel set hai:
    - FSub channels (force subscribe)
    - Update channel
    - File DB ka indexed channel list
    - Access check
    """
    me       = await client.get_me()
    bot_data = await db.get_bot(me.id)
    wait_msg = await message.reply("⏳ Channel info collect ho rahi hai...")

    # ── FSub channel ─────────────────────────────────────────────────
    fsub_raw = bot_data.get("fsub_channel")
    fsub_lines = []
    if fsub_raw:
        try:
            # Multiple fsub channels (comma-separated IDs bhi ho sakte hain)
            fsub_ids = [f.strip() for f in str(fsub_raw).split(",") if f.strip()]
            for fid in fsub_ids:
                try:
                    chat = await client.get_chat(int(fid) if fid.lstrip("-").isdigit() else fid)
                    cname = f"@{chat.username}" if chat.username else chat.title
                    fsub_lines.append(f"  ✅ {cname} (<code>{chat.id}</code>) — Accessible")
                except Exception:
                    fsub_lines.append(f"  ❌ <code>{fid}</code> — Bot ka access nahi / nahi mila!")
        except Exception as ex:
            fsub_lines.append(f"  ⚠️ Parse error: {ex}")
    else:
        fsub_lines.append("  ❌ Koi FSub channel set nahi")

    # ── Update channel ────────────────────────────────────────────────
    update_ch_raw = bot_data.get("update_channel_link") or "Not Set"

    # ── File DB — Indexed channels ────────────────────────────────────
    try:
        # col aur sec_col dono se unique channel IDs
        primary_channels = col.distinct("channel_id")
        sec_channels     = sec_col.distinct("channel_id")
        all_channel_ids  = set(c for c in (primary_channels + sec_channels) if c)
    except Exception:
        all_channel_ids = set()

    indexed_channel_lines = []
    if all_channel_ids:
        for ch_id in list(all_channel_ids)[:10]:   # max 10 dikhao
            try:
                ch    = await client.get_chat(ch_id)
                cname = f"@{ch.username}" if ch.username else ch.title
                count = col.count_documents({"channel_id": ch_id}) + sec_col.count_documents({"channel_id": ch_id})
                indexed_channel_lines.append(
                    f"  📁 {cname} — <b>{count:,}</b> files"
                )
            except Exception:
                count = col.count_documents({"channel_id": ch_id}) + sec_col.count_documents({"channel_id": ch_id})
                indexed_channel_lines.append(
                    f"  📁 <code>{ch_id}</code> — <b>{count:,}</b> files (access nahi)"
                )
        if len(all_channel_ids) > 10:
            indexed_channel_lines.append(f"  … aur {len(all_channel_ids)-10} channels")
    else:
        indexed_channel_lines.append("  ❌ Koi channel indexed nahi — /index se channel add karo")

    # ── File counts ───────────────────────────────────────────────────
    try:
        primary_count = col.count_documents({})
        sec_count     = sec_col.count_documents({})
        total_files   = primary_count + sec_count
    except Exception:
        primary_count = sec_count = total_files = 0

    # ── Users & Groups ────────────────────────────────────────────────
    try:
        total_users  = await clonedb.total_users_count(me.id)
        total_groups = await db.total_chat_count()
    except Exception:
        total_users = total_groups = 0

    # ── Build message ─────────────────────────────────────────────────
    fsub_text           = "\n".join(fsub_lines)
    indexed_ch_text     = "\n".join(indexed_channel_lines)

    text = (
        f"<b>📡 Channel & File Info — @{me.username}</b>\n\n"

        f"<b>🔒 Force Subscribe Channels:</b>\n"
        f"{fsub_text}\n\n"

        f"<b>📢 Update Channel:</b>\n"
        f"  {update_ch_raw}\n\n"

        f"<b>📁 Indexed File Channels:</b>\n"
        f"{indexed_ch_text}\n\n"

        f"<b>📊 Database Stats:</b>\n"
        f"  📦 Primary DB: <b>{primary_count:,}</b> files\n"
        f"  📦 Secondary DB: <b>{sec_count:,}</b> files\n"
        f"  📦 Total Files: <b>{total_files:,}</b>\n\n"

        f"<b>👥 Bot Usage:</b>\n"
        f"  👤 Users: <b>{total_users:,}</b>\n"
        f"  👥 Groups: <b>{total_groups:,}</b>"
    )

    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="channel_info_refresh")],
        [
            InlineKeyboardButton("🔒 FSub Manage", callback_data="fsub_manage"),
            InlineKeyboardButton("📥 Index Now", callback_data="index_now_hint"),
        ]
    ])

    await wait_msg.edit_text(text, reply_markup=btns, parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^channel_info_refresh$"))
async def channel_info_refresh_cb(client, query):
    """Refresh button — /channel wala data dobara load karo"""
    await query.answer("🔄 Refreshing...")
    await channel_info_cmd(client, query.message)


@Client.on_callback_query(filters.regex("^index_now_hint$"))
async def index_now_hint_cb(client, query):
    await query.answer(
        "Index karne ke liye:\n/index -100CHANNEL_ID\nChannel ID nahi pata? /id command use karo.",
        show_alert=True
    )


# ═══════════════════════════════════════════════════════════
#  /cstats — Detailed stats (Users + Admin dono ke liye)
# ═══════════════════════════════════════════════════════════
@Client.on_message(filters.command("cstats") & filters.incoming)
async def cstats_cmd(client, message: Message):
    """
    Detailed bot stats:
    - Admin ke liye: files, users, groups, DB size, channels
    - User ke liye: basic stats
    """
    me       = await client.get_me()
    bot_data = await db.get_bot(me.id)
    uid      = message.from_user.id
    is_admin = (uid == bot_data.get("user_id") or uid in ADMINS)

    # ── File counts ───────────────────────────────────────────────────
    try:
        primary_count = col.count_documents({})
        sec_count     = sec_col.count_documents({})
        total_files   = primary_count + sec_count
    except Exception:
        primary_count = sec_count = total_files = 0

    # ── Users & Groups ────────────────────────────────────────────────
    try:
        total_users  = await clonedb.total_users_count(me.id)
        total_groups = await db.total_chat_count()
    except Exception:
        total_users = total_groups = 0

    if is_admin:
        # Admin: detailed stats
        try:
            from database.ia_filterdb import db as file_db
            db_stats  = file_db.command("dbstats")
            db_size_mb = round(db_stats.get("dataSize", 0) / (1024*1024), 2)
        except Exception:
            db_size_mb = "N/A"

        # Indexed channels count
        try:
            ch_count = len(set(col.distinct("channel_id") + sec_col.distinct("channel_id")))
        except Exception:
            ch_count = 0

        # Subscription info
        try:
            from database.subscription_db import get_subscription
            import datetime
            sub = await get_subscription(me.id)
            if sub:
                expiry    = sub.get("expiry")
                days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
                sub_text  = f"✅ Active — {days_left} din bache"
            else:
                sub_text = "❌ No subscription"
        except Exception:
            sub_text = "N/A"

        text = (
            f"<b>📊 Bot Stats — @{me.username}</b>\n\n"
            f"<b>📁 Files:</b>\n"
            f"  Primary DB: {primary_count:,}\n"
            f"  Secondary DB: {sec_count:,}\n"
            f"  Total: <b>{total_files:,}</b>\n"
            f"  Indexed Channels: {ch_count}\n"
            f"  DB Size: {db_size_mb} MB\n\n"
            f"<b>👥 Users & Groups:</b>\n"
            f"  Users: <b>{total_users:,}</b>\n"
            f"  Groups: <b>{total_groups:,}</b>\n\n"
            f"<b>💎 Subscription:</b> {sub_text}\n\n"
            f"<b>🔧 Quick Links:</b>\n"
            f"  /channel — Channel details\n"
            f"  /settings — Bot settings\n"
            f"  /index — Index files"
        )
    else:
        # User: basic stats sirf
        text = (
            f"<b>📊 @{me.username} Stats</b>\n\n"
            f"📁 Total Files: <b>{total_files:,}</b>\n"
            f"👥 Groups: <b>{total_groups:,}</b>\n\n"
            f"<i>Koi movie chahiye? Bas naam type karo!</i>"
        )

    await message.reply(text, parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════
#  /checkbot — Bot health check (Admin only)
# ═══════════════════════════════════════════════════════════
@Client.on_message(filters.command("checkbot") & clone_admin)
async def checkbot_cmd(client, message: Message):
    """
    Bot ka health check — sab sahi hai ya nahi:
    ✅ FSub channel accessible
    ✅ Files indexed
    ✅ Shortlink set
    ✅ Subscription active
    """
    me       = await client.get_me()
    bot_data = await db.get_bot(me.id)
    wait_msg = await message.reply("🔍 Health check chal rahi hai...")

    checks = []

    # ── 1. Files indexed? ────────────────────────────────────────────
    try:
        file_count = col.count_documents({}) + sec_col.count_documents({})
        if file_count > 0:
            checks.append(f"✅ Files: {file_count:,} indexed")
        else:
            checks.append("❌ Files: Koi file indexed nahi! /index se channel add karo")
    except Exception:
        checks.append("⚠️ Files: DB check nahi hua")

    # ── 2. FSub channel accessible? ──────────────────────────────────
    fsub = bot_data.get("fsub_channel")
    if fsub:
        try:
            chat = await client.get_chat(fsub)
            cname = f"@{chat.username}" if chat.username else chat.title
            # Check if bot is admin
            member = await client.get_chat_member(chat.id, (await client.get_me()).id)
            is_admin_in_ch = member.status.value in ["administrator", "creator"]
            if is_admin_in_ch:
                checks.append(f"✅ FSub: {cname} — Bot admin hai ✓")
            else:
                checks.append(f"⚠️ FSub: {cname} — Bot admin NAHI hai! Promote karo")
        except Exception as ex:
            checks.append(f"❌ FSub: Channel access nahi — {ex}")
    else:
        checks.append("ℹ️ FSub: Set nahi (optional)")

    # ── 3. Shortlink set? ────────────────────────────────────────────
    grp_settings = {}
    try:
        from utils import get_settings
        grp_settings = await get_settings(message.chat.id)
    except Exception:
        pass

    shortlink_url = grp_settings.get("shortlink") or bot_data.get("url")
    shortlink_api = grp_settings.get("shortlink_api") or bot_data.get("api")

    if shortlink_url and shortlink_api:
        checks.append(f"✅ Shortlink: {shortlink_url} — Set hai")
    else:
        checks.append("⚠️ Shortlink: Set nahi — /shortlink command use karo")

    # ── 4. Subscription active? ──────────────────────────────────────
    try:
        from database.subscription_db import get_subscription, is_active as sub_is_active
        import datetime
        sub = await get_subscription(me.id)
        if sub and sub.get("is_active"):
            expiry    = sub.get("expiry")
            days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
            if days_left > 7:
                checks.append(f"✅ Subscription: {days_left} din bache")
            elif days_left > 0:
                checks.append(f"⚠️ Subscription: Sirf {days_left} din bache! Renew karo")
            else:
                checks.append("❌ Subscription: Expire ho gaya! @aschat_group pe contact karo")
        else:
            checks.append("❌ Subscription: Active nahi!")
    except Exception:
        checks.append("⚠️ Subscription: Check nahi hua")

    # ── 5. Update channel set? ───────────────────────────────────────
    update_ch = bot_data.get("update_channel_link")
    if update_ch:
        checks.append(f"✅ Update Channel: {update_ch[:40]}")
    else:
        checks.append("ℹ️ Update Channel: Set nahi (optional)")

    # ── 6. Welcome message custom? ───────────────────────────────────
    if bot_data.get("start_message"):
        checks.append("✅ Welcome Message: Custom set hai")
    else:
        checks.append("ℹ️ Welcome Message: Default use ho raha hai")

    # ── Result ───────────────────────────────────────────────────────
    fail_count = sum(1 for c in checks if c.startswith("❌"))
    warn_count = sum(1 for c in checks if c.startswith("⚠️"))

    if fail_count == 0 and warn_count == 0:
        overall = "✅ Bot bilkul theek hai!"
    elif fail_count == 0:
        overall = f"⚠️ {warn_count} warnings hain — thoda improve karo"
    else:
        overall = f"❌ {fail_count} issues hain — fix karo!"

    check_text = "\n".join(checks)
    await wait_msg.edit_text(
        f"<b>🔍 Bot Health Check — @{me.username}</b>\n\n"
        f"{check_text}\n\n"
        f"<b>━━━ Overall: {overall} ━━━</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Re-check", callback_data="recheck_health")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="open_settings")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^recheck_health$"))
async def recheck_health_cb(client, query):
    await query.answer("🔄 Re-checking...")
    await checkbot_cmd(client, query.message)


@Client.on_callback_query(filters.regex("^open_settings$"))
async def open_settings_cb(client, query):
    await query.answer()
    from AsFilterBot.commands import settings
    await settings(client, query.message)
