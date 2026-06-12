# ════════════════════════════════════════════════════════════
#   Clone Bot — Commands
#   FIXED:
#   - Start: 3-sec button removed, about mein server info
#   - Help: Updates+Support extra buttons removed
#   - /request: clone owner tak pahunchti hai
#   - /stats: sirf is clone ke files+users
#   - /settings: settings_cb.py ke callbacks use karta hai
#   - File caption: warning + main bot name
#   - Bekar commands removed: link/batch/backup/filter/viewfilter/delall/fsub
# ════════════════════════════════════════════════════════════

import asyncio, logging, re
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database.ia_filterdb import col, sec_col, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from AsFilterBot.database.clone_bot_userdb import clonedb
from info import ADMINS, SUPPORT_CHAT, LOG_CHANNEL
from Script import script
from utils import get_settings, get_size, temp, is_subscribed

logger = logging.getLogger(__name__)

# ── Main bot name — caption footer mein ─────────────────────
MAIN_BOT_NAME = "Create AutoFilter Bot"  # Main bot ka naam

# ── Auto delete helper ────────────────────────────────────────
async def _auto_delete_msg(msg, delay_secs: int):
    try:
        await asyncio.sleep(delay_secs)
        await msg.delete()
    except:
        pass

from clone_filter import clone_admin, clone_or_group_admin


async def _is_owner(client, user_id: int) -> bool:
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    return user_id == bd.get("user_id") or user_id in ADMINS


# ═══════════════════════════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message: Message):
    me = await client.get_me()
    cd = await db.get_bot(me.id)

    # Group mein start — sirf add button, koi 3-sec nonsense nahi
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[InlineKeyboardButton(
            '➕ Add Me To Your Group',
            url=f'http://t.me/{me.username}?startgroup=true'
        )]]
        if cd.get("update_channel_link"):
            buttons.append([InlineKeyboardButton(
                '📢 Join Update Channel',
                url=cd["update_channel_link"]
            )])
        await message.reply(
            f"<b>Namaste! 👋\n\n{me.first_name} aapki service mein hazir hai.\n"
            f"Group mein movie ka naam likho — main dhundh deta hoon! 🎬</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return

    # Register user
    if not await clonedb.is_user_exist(me.id, message.from_user.id):
        await clonedb.add_user(me.id, message.from_user.id)

    # Force Subscribe check
    fsub_channel = cd.get("fsub_channel")
    user_id = message.from_user.id
    if fsub_channel and user_id not in ADMINS and user_id != cd.get("user_id"):
        try:
            member = await client.get_chat_member(fsub_channel, user_id)
            if member.status in ["kicked", "left"]:
                raise Exception("Not member")
        except Exception:
            try:
                ch_link = cd.get("update_channel_link") or f"https://t.me/{str(fsub_channel).replace('-100', '')}"
                await message.reply(
                    "<b>⚠️ Pehle channel join karo, phir bot use karo!</b>",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("✅ Join Channel", url=ch_link),
                        InlineKeyboardButton("🔄 Verify", callback_data=f"fsub_check_{user_id}")
                    ]]),
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
            return

    # Deep link handling
    if len(message.command) == 2:
        data = message.command[1]
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""

        # File delivery
        if pre in ["file", "getfile", "media", "dl"] or not pre:
            await _deliver_file(client, message, file_id, cd)
            return

        if data.startswith("all"):
            files = temp.GETALL.get(file_id)
            if not files:
                return await message.reply('<b>File nahi mili.</b>', parse_mode=enums.ParseMode.HTML)
            await _deliver_multiple_files(client, message, files, cd)
            return

    # Normal start — buttons banao
    buttons = [
        [InlineKeyboardButton('➕ Add To Group', url=f'http://t.me/{me.username}?startgroup=true')],
        [
            InlineKeyboardButton('🕵️ Help', callback_data='help'),
            InlineKeyboardButton('🔍 About', callback_data='about')
        ],
    ]
    if cd.get("update_channel_link"):
        buttons.append([InlineKeyboardButton('📢 Update Channel', url=cd["update_channel_link"])])
    # Custom buttons from owner
    for btn in (cd.get("start_buttons") or []):
        try:
            buttons.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
        except:
            pass

    # Custom start message
    start_text = cd.get("start_message") or script.CLONE_START_TXT.format(
        message.from_user.mention, me.username, me.first_name
    )
    start_photo = cd.get("start_photo")

    if start_photo:
        await message.reply_photo(
            photo=start_photo,
            caption=start_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text(
            text=start_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )


# ── About callback — server info ─────────────────────────────
@Client.on_callback_query(filters.regex("^about$"))
async def about_cb(client, query: CallbackQuery):
    me = await client.get_me()
    await query.message.edit_text(
        f"<b>ℹ️ About @{me.username}</b>\n\n"
        f"🤖 <b>{me.first_name}</b>\n"
        f"🖥️ Running on: <b>{MAIN_BOT_NAME}</b> server\n\n"
        f"Ye bot automatically movies search karta hai.\n"
        f"Apna movie bot banane ke liye: @{MAIN_BOT_NAME.replace(' ', '_')}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ── Help — sirf 2 buttons, no Updates/Support extra ──────────
@Client.on_message(filters.command("help") & filters.incoming)
async def help_cmd(client, message: Message):
    me  = await client.get_me()
    bd  = await db.get_bot(me.id)
    uid = message.from_user.id
    is_owner = (uid == bd.get("user_id") or uid in ADMINS)
    await _send_help(client, message, is_owner, me)


@Client.on_callback_query(filters.regex("^help$"))
async def help_cb(client, query: CallbackQuery):
    me  = await client.get_me()
    bd  = await db.get_bot(me.id)
    uid = query.from_user.id
    is_owner = (uid == bd.get("user_id") or uid in ADMINS)
    btns = [
        [InlineKeyboardButton("👤 User Commands", callback_data="help_user")],
    ]
    if is_owner:
        btns.append([InlineKeyboardButton("👑 Admin Commands", callback_data="help_admin_panel")])

    tag = "\n\n👑 <b>Aap is bot ke Admin hain!</b>" if is_owner else ""
    await query.message.edit_text(
        f"<b>📖 Help — @{me.username}</b>\n\nNeeche se choose karo 👇{tag}",
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


async def _send_help(client, message, is_owner, me):
    btns = [
        [InlineKeyboardButton("👤 User Commands", callback_data="help_user")],
    ]
    if is_owner:
        btns.append([InlineKeyboardButton("👑 Admin Commands", callback_data="help_admin_panel")])

    tag = "\n\n👑 <b>Aap is bot ke Admin hain!</b>" if is_owner else ""
    await message.reply(
        f"<b>📖 Help — @{me.username}</b>\n\nNeeche se choose karo 👇{tag}",
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_user$"))
async def help_user_cb(client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>👤 User Commands</b>\n\n"
        "/start — Bot start karo\n"
        "/search [movie] — Movie search / IMDB info\n"
        "/request [movie] — Movie request karo\n"
        "/plan — Premium plans dekho\n"
        "/myplan — Apna active plan dekho\n"
        "/redeem [code] — Code redeem karo\n"
        "/id — Apna Telegram ID\n\n"
        "<i>💡 Group mein movie ka naam likho → auto search!</i>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_admin_panel$"))
async def help_admin_panel_cb(client, query: CallbackQuery):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    if query.from_user.id != bd.get("user_id") and query.from_user.id not in ADMINS:
        return await query.answer("❌ Sirf owner!", show_alert=True)

    await query.message.edit_text(
        "<b>👑 Admin Commands</b>\n\n"
        "/settings — Bot settings\n"
        "/index — Channel index karo\n"
        "/addnew — Nai file add karo library mein\n"
        "/stats — Files aur users count\n"
        "/ban [user_id] — User ban karo\n"
        "/unban [user_id] — User unban karo\n"
        "/broadcast [msg] — Sabko message bhejo\n"
        "/add_premium [id] [days] — Premium do\n"
        "/remove_premium [id] — Premium hatao\n"
        "/setplans — Premium plans set karo\n"
        "/cleanup — Blocked users hatao\n"
        "/restart — Bot restart karo",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
#  /settings — Clone bot settings (redirects to settings_cb.py)
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message: Message):
    if not await _is_owner(client, message.from_user.id):
        return await message.reply("<b>❌ Sirf owner!</b>", parse_mode=enums.ParseMode.HTML)

    me = await client.get_me()
    bd = await db.get_bot(me.id)

    pm    = "✅" if bd.get("pm_search", True)   else "❌"
    imdb  = "✅" if bd.get("imdb_on", True)      else "❌"
    strm  = "✅" if bd.get("stream_mode", False) else "❌"
    sl_t  = bd.get("shortlink_verify_time", 0)
    mb    = bd.get("max_results", 10)
    btn_mode = bd.get("button_mode", "button")
    btn_mode_label = "🔵 Button Mode" if btn_mode == "button" else "🔗 Link Mode"

    text = (
        f"<b>⚙️ Settings — @{me.username}</b>\n\n"
        f"🔍 PM Search: {pm}\n"
        f"🎬 IMDB: {imdb}\n"
        f"📺 Stream: {strm} (Premium only)\n"
        f"⏱️ Verify Time: {sl_t}h\n"
        f"🔢 Max Buttons: {mb}\n"
        f"📋 Result Mode: {btn_mode_label}\n"
    )
    btns = [
        [
            InlineKeyboardButton(f"{pm} PM Search", callback_data="tog_pm"),
            InlineKeyboardButton(f"{imdb} IMDB", callback_data="tog_imdb"),
        ],
        [
            InlineKeyboardButton(f"{strm} Stream", callback_data="tog_stream"),
            InlineKeyboardButton(f"⏱️ Verify ({sl_t}h)", callback_data="set_vt"),
        ],
        [
            InlineKeyboardButton(f"🔢 Max Btns ({mb})", callback_data="set_mb"),
            InlineKeyboardButton(f"📋 {btn_mode_label}", callback_data="tog_btn_mode"),
        ],
    ]
    await message.reply(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
#  /stats — Sirf is clone ke files + users
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client, message: Message):
    if not await _is_owner(client, message.from_user.id):
        return await message.reply("<b>❌ Sirf owner!</b>", parse_mode=enums.ParseMode.HTML)

    me = await client.get_me()
    bd = await db.get_bot(me.id)

    # Users — sirf is bot ke
    total_users = await clonedb.total_users_count(me.id)

    # Files — indexed files count
    indexed_ch = bd.get("indexed_channels") or []
    if indexed_ch:
        # Sirf is clone ke indexed channels ki files
        file_count = col.count_documents({"channel_id": {"$in": indexed_ch}})
        file_count += sec_col.count_documents({"channel_id": {"$in": indexed_ch}})
    else:
        # Shared database total
        file_count = col.count_documents({}) + sec_col.count_documents({})

    await message.reply(
        f"<b>📊 @{me.username} — Stats</b>\n\n"
        f"📁 Indexed Files: <b>{file_count:,}</b>\n"
        f"👥 Bot Users: <b>{total_users:,}</b>",
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
#  /request — Clone owner tak pahunchi!
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("request") & filters.incoming)
async def request_cmd(client, message: Message):
    movie_name = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not movie_name:
        return await message.reply(
            "<b>📬 Movie Request Karo</b>\n\n"
            "Usage: <code>/request Movie Name</code>\n\n"
            "Example: <code>/request Pushpa 2</code>",
            parse_mode=enums.ParseMode.HTML
        )

    user = message.from_user
    me   = await client.get_me()
    bd   = await db.get_bot(me.id)

    owner_id = bd.get("user_id")   # Clone owner ID

    req_text = (
        f"<b>🎬 #MovieRequest</b>\n\n"
        f"Movie: <b>{movie_name}</b>\n"
        f"By: {user.mention} (<code>{user.id}</code>)\n"
        f"Bot: @{me.username}\n"
        f"Chat: {message.chat.title or 'PM'} (<code>{message.chat.id}</code>)"
    )

    # Clone owner ko bhejo
    sent = False
    if owner_id:
        try:
            await client.send_message(
                owner_id,
                req_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        f"📩 Reply to {user.first_name}",
                        url=f"tg://user?id={user.id}"
                    )
                ]]),
                parse_mode=enums.ParseMode.HTML
            )
            sent = True
        except Exception as e:
            logger.warning(f"Request to owner failed: {e}")

    # LOG_CHANNEL mein bhi bhejo
    try:
        from info import REQST_CHANNEL
        rc = REQST_CHANNEL or LOG_CHANNEL
        if rc:
            await client.send_message(rc, req_text, parse_mode=enums.ParseMode.HTML)
    except:
        pass

    await message.reply(
        f"<b>✅ Request bhej di!</b>\n\n"
        f"🎬 <b>{movie_name}</b>\n\n"
        f"{'Bot owner ko notification aa gayi.' if sent else 'Request log mein save ho gayi.'}\n"
        f"Jald hi upload hogi. 🙏",
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
#  /id — User ID
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("id") & filters.incoming)
async def id_cmd(client, message: Message):
    user = message.from_user
    chat = message.chat
    text = f"<b>👤 Your ID: <code>{user.id}</code></b>"
    if chat.type != enums.ChatType.PRIVATE:
        text += f"\n<b>💬 Group ID: <code>{chat.id}</code></b>"
    if message.reply_to_message and message.reply_to_message.from_user:
        ru = message.reply_to_message.from_user
        text += f"\n<b>↩️ Reply User ID: <code>{ru.id}</code></b>"
    await message.reply(text, parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
#  /search — IMDB search
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command(["search", "imdb"]) & filters.incoming)
async def search_imdb_cmd(client, message: Message):
    query_text = " ".join(message.command[1:]).strip()
    if not query_text:
        return await message.reply(
            "<b>Usage:</b> <code>/search Movie Name</code>",
            parse_mode=enums.ParseMode.HTML
        )

    me = await client.get_me()
    bd = await db.get_bot(me.id)

    if not bd.get("imdb_on", True):
        return await message.reply("<b>❌ IMDB search abhi off hai.</b>", parse_mode=enums.ParseMode.HTML)

    wait = await message.reply("🔍 <b>Searching IMDB...</b>", parse_mode=enums.ParseMode.HTML)

    try:
        import aiohttp
        tmdb_api = bd.get("tmdb_api") or bd.get("omdb_api")
        if tmdb_api:
            # TMDB API
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query_text}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
            results = data.get("results", [])[:5]
            if not results:
                return await wait.edit_text(f"<b>❌ '{query_text}' nahi mili IMDB/TMDB par.</b>", parse_mode=enums.ParseMode.HTML)

            btns = []
            for r in results:
                title = r.get("title") or r.get("name", "Unknown")
                year  = (r.get("release_date") or r.get("first_air_date") or "")[:4]
                mid   = r.get("id")
                mtype = r.get("media_type", "movie")
                label = f"🎬 {title} ({year})" if year else f"🎬 {title}"
                btns.append([InlineKeyboardButton(label, callback_data=f"tmdb_{mtype}_{mid}")])

            await wait.edit_text(
                f"<b>🔍 Results for: {query_text}</b>\n\nEk select karo:",
                reply_markup=InlineKeyboardMarkup(btns),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await wait.edit_text(
                f"<b>❌ IMDB API set nahi hai.\n\n/settings → IMDB → API key dalo.</b>",
                parse_mode=enums.ParseMode.HTML
            )
    except Exception as e:
        await wait.edit_text(f"<b>❌ Search error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
#  /ban /unban
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("ban") & clone_admin)
async def ban_user(client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply("<b>Usage:</b> <code>/ban user_id reason</code>", parse_mode=enums.ParseMode.HTML)
    try:
        ban_id = int(args[1])
        reason = " ".join(args[2:]) or "No reason"
        me = await client.get_me()
        await clonedb.ban_user(me.id, ban_id, reason)
        await message.reply(
            f"<b>🚫 Banned!</b>\nUser: <code>{ban_id}</code>\nReason: {reason}",
            parse_mode=enums.ParseMode.HTML
        )
        try:
            await client.send_message(ban_id, f"<b>🚫 Aapko is bot mein ban kar diya gaya.\nReason: {reason}</b>", parse_mode=enums.ParseMode.HTML)
        except: pass
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("unban") & clone_admin)
async def unban_user(client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.reply("<b>Usage:</b> <code>/unban user_id</code>", parse_mode=enums.ParseMode.HTML)
    try:
        unban_id = int(args[1])
        me = await client.get_me()
        await clonedb.unban_user(me.id, unban_id)
        await message.reply(f"<b>✅ Unbanned!</b>\nUser: <code>{unban_id}</code>", parse_mode=enums.ParseMode.HTML)
        try:
            await client.send_message(unban_id, "<b>✅ Aapka ban hata diya gaya!</b>", parse_mode=enums.ParseMode.HTML)
        except: pass
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
#  /broadcast
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("broadcast") & clone_admin & filters.private)
async def broadcast_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply(
            "<b>Broadcast Message Forward Karo</b>\n\nKisi message ko reply karo /broadcast se.",
            parse_mode=enums.ParseMode.HTML
        )
    me = await client.get_me()
    all_users = await clonedb.get_all_users(me.id)
    sent = failed = 0
    status_msg = await message.reply(f"<b>📤 Broadcasting...</b>\n\nTotal: {len(all_users)}", parse_mode=enums.ParseMode.HTML)
    for uid in all_users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except:
            failed += 1
        if (sent + failed) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"<b>📤 Broadcasting...\nSent: {sent}\nFailed: {failed}</b>",
                    parse_mode=enums.ParseMode.HTML
                )
            except: pass
    await status_msg.edit_text(
        f"<b>✅ Broadcast Done!\nSent: {sent}\nFailed: {failed}</b>",
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
#  /cleanup — Blocked users delete karo
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("cleanup") & clone_admin)
async def cleanup_cmd(client, message: Message):
    me = await client.get_me()
    wait = await message.reply("<b>🧹 Cleanup shuru...</b>", parse_mode=enums.ParseMode.HTML)
    all_users = await clonedb.get_all_users(me.id)
    removed = 0
    for uid in all_users:
        try:
            await client.send_chat_action(uid, enums.ChatAction.TYPING)
        except Exception as e:
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower() or "not found" in str(e).lower():
                await clonedb.delete_user(me.id, uid)
                removed += 1
    await wait.edit_text(
        f"<b>✅ Cleanup Done!\nRemoved: {removed} blocked/deleted users</b>",
        parse_mode=enums.ParseMode.HTML
    )


# ═══════════════════════════════════════════════════════════════
#  /restart
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("restart") & clone_admin)
async def restart_cmd(client, message: Message):
    if not await _is_owner(client, message.from_user.id):
        return await message.reply("<b>❌ Sirf owner!</b>", parse_mode=enums.ParseMode.HTML)
    await message.reply("<b>🔄 Restarting...</b>", parse_mode=enums.ParseMode.HTML)
    import os, sys
    os.execl(sys.executable, sys.executable, *sys.argv)


# ═══════════════════════════════════════════════════════════════
#  /delete — File delete karo
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("delete") & clone_admin)
async def delete_file_cmd(client, message: Message):
    file_name = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not file_name:
        return await message.reply(
            "<b>Usage:</b> <code>/delete file name</code>",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        result = await col.delete_many({"$or": [
            {"file_name": {"$regex": file_name, "$options": "i"}},
            {"caption": {"$regex": file_name, "$options": "i"}}
        ]})
        r2 = await sec_col.delete_many({"$or": [
            {"file_name": {"$regex": file_name, "$options": "i"}},
            {"caption": {"$regex": file_name, "$options": "i"}}
        ]})
        total_del = result.deleted_count + r2.deleted_count
        await message.reply(
            f"<b>✅ {total_del} files delete ho gayi!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
#  /leave — Group se bot leave kare
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("leave") & clone_admin)
async def leave_chat(client, message: Message):
    if len(message.command) == 1:
        return await message.reply("<b>Usage:</b> <code>/leave chat_id</code>", parse_mode=enums.ParseMode.HTML)
    try:
        chat_id = int(message.command[1])
        await client.leave_chat(chat_id)
        await message.reply(f"<b>✅ Left chat: <code>{chat_id}</code></b>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ═══════════════════════════════════════════════════════════════
#  Banned word report — Clone owner ko bhejo only
# ═══════════════════════════════════════════════════════════════
async def report_to_clone_owner(client, user_id: int, reason: str, chat_id: int = None):
    """Bad word ya shortlink bypass report — sirf clone owner ko"""
    try:
        me = await client.get_me()
        bd = await db.get_bot(me.id)
        owner_id = bd.get("user_id")
        if owner_id:
            await client.send_message(
                owner_id,
                f"<b>⚠️ Report</b>\n\n"
                f"User: <code>{user_id}</code>\n"
                f"Reason: {reason}\n"
                f"Chat: <code>{chat_id or 'PM'}</code>",
                parse_mode=enums.ParseMode.HTML
            )
    except:
        pass


# ═══════════════════════════════════════════════════════════════
#  File delivery helpers
# ═══════════════════════════════════════════════════════════════
async def _build_caption(files: dict, me, bd: dict) -> str:
    """Clean caption + warning + main bot name footer"""
    raw_name = files.get("file_name", "Unknown")
    # Extra @links ya brackets hata dein
    clean_name = " ".join(
        w for w in raw_name.split()
        if not w.startswith("@") and not w.startswith("[") and not w.startswith("]")
    )

    auto_del = bd.get("auto_delete", 600)
    del_mins = auto_del // 60 if auto_del else 0

    caption_parts = [f"<b>🎬 {clean_name}</b>"]
    if del_mins > 0:
        caption_parts.append(
            f"\n⚠️ <i>Ye file {del_mins} minute baad delete hogi!\n"
            f"📥 Save Karo: File pe tap karein → ⬇ Download</i>"
        )
    caption_parts.append(f"\n\n🤖 Powered by <b>{MAIN_BOT_NAME}</b>")
    return "\n".join(caption_parts)


async def _deliver_file(client, message: Message, file_id: str, cd: dict):
    """Single file deliver with warning caption"""
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply("<b>❌ File nahi mili.</b>", parse_mode=enums.ParseMode.HTML)

    files  = files_
    me     = await client.get_me()
    me_data = await db.get_bot(me.id)
    protect  = me_data.get("protect_content", False)
    auto_del = me_data.get("auto_delete", 600)

    f_caption = await _build_caption(files, me, me_data)

    reply_markup = None
    if cd.get("update_channel_link"):
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("📢 Join Update Channel", url=cd["update_channel_link"])
        ]])

    msg = None
    from info import PUBLIC_FILE_CHANNEL, MAIN_MOVIE_CHANNEL

    try:
        pfc = PUBLIC_FILE_CHANNEL or MAIN_MOVIE_CHANNEL

        if pfc and temp.BOT:
            try:
                posted = await temp.BOT.send_cached_media(chat_id=pfc, file_id=file_id)
                msg = await client.copy_message(
                    chat_id=message.from_user.id,
                    from_chat_id=pfc,
                    message_id=posted.id,
                    caption=f_caption,
                    protect_content=protect,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                try: await posted.delete()
                except: pass
            except Exception as e1:
                logger.warning(f"pfc method failed: {e1}")

        if not msg:
            ch_id     = files.get("channel_id") or MAIN_MOVIE_CHANNEL
            ch_msg_id = files.get("channel_msg_id")
            if ch_id and ch_msg_id:
                try:
                    msg = await client.copy_message(
                        chat_id=message.from_user.id,
                        from_chat_id=ch_id,
                        message_id=ch_msg_id,
                        caption=f_caption,
                        protect_content=protect,
                        reply_markup=reply_markup,
                        parse_mode=enums.ParseMode.HTML
                    )
                except Exception as e2:
                    logger.warning(f"copy_message method failed: {e2}")

        if not msg:
            use_fid = files.get("og_file_id") or file_id
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=use_fid,
                caption=f_caption,
                protect_content=protect,
                reply_markup=reply_markup
            )

        if msg and auto_del and auto_del > 0:
            asyncio.create_task(_auto_delete_msg(msg, auto_del))

    except Exception as e:
        logger.error(f"File deliver error: {e}")
        await client.send_message(
            message.from_user.id,
            "<b>❌ File nahi aayi. Thodi der baad dobara try karo.</b>",
            parse_mode=enums.ParseMode.HTML
        )


async def _deliver_multiple_files(client, message: Message, files: list, cd: dict):
    """Multiple files deliver"""
    me      = await client.get_me()
    me_data = await db.get_bot(me.id)
    protect  = me_data.get("protect_content", False)
    auto_del = me_data.get("auto_delete", 600)

    reply_markup = None
    if cd.get("update_channel_link"):
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("📢 Join Update Channel", url=cd["update_channel_link"])
        ]])

    from info import PUBLIC_FILE_CHANNEL, MAIN_MOVIE_CHANNEL
    pfc = PUBLIC_FILE_CHANNEL or MAIN_MOVIE_CHANNEL

    sent_msgs = []
    for file in files:
        try:
            vj_file_id = file["file_id"]
            f_caption  = await _build_caption(file, me, me_data)
            msg = None

            if pfc and temp.BOT:
                try:
                    posted = await temp.BOT.send_cached_media(chat_id=pfc, file_id=vj_file_id)
                    msg = await client.copy_message(
                        chat_id=message.from_user.id,
                        from_chat_id=pfc,
                        message_id=posted.id,
                        caption=f_caption,
                        protect_content=protect,
                        reply_markup=reply_markup,
                        parse_mode=enums.ParseMode.HTML
                    )
                    try: await posted.delete()
                    except: pass
                except: pass

            if not msg:
                ch_id     = file.get("channel_id") or MAIN_MOVIE_CHANNEL
                ch_msg_id = file.get("channel_msg_id")
                if ch_id and ch_msg_id:
                    try:
                        msg = await client.copy_message(
                            chat_id=message.from_user.id,
                            from_chat_id=ch_id,
                            message_id=ch_msg_id,
                            caption=f_caption,
                            protect_content=protect,
                            reply_markup=reply_markup,
                            parse_mode=enums.ParseMode.HTML
                        )
                    except: pass

            if not msg:
                use_fid = file.get("og_file_id") or vj_file_id
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=use_fid,
                    caption=f_caption,
                    protect_content=protect,
                    reply_markup=reply_markup
                )

            if msg:
                sent_msgs.append(msg)
        except Exception as e:
            logger.error(f"Multi-file deliver error: {e}")
            continue

    if auto_del and auto_del > 0:
        for msg in sent_msgs:
            asyncio.create_task(_auto_delete_msg(msg, auto_del))


# ═══════════════════════════════════════════════════════════════
#  FSub verify button
# ═══════════════════════════════════════════════════════════════
@Client.on_callback_query(filters.regex(r"^fsub_check_(\d+)$"))
async def fsub_check_cb(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))
    if query.from_user.id != user_id:
        return await query.answer("Ye aapka nahi!", show_alert=True)

    me = await client.get_me()
    cd = await db.get_bot(me.id)
    fsub_channel = cd.get("fsub_channel")
    if not fsub_channel:
        return await query.answer("✅ Verify ho gaye!", show_alert=True)

    try:
        member = await client.get_chat_member(fsub_channel, user_id)
        if member.status not in ["kicked", "left"]:
            await query.answer("✅ Join verify ho gaya! Ab /start karo.", show_alert=True)
            await query.message.delete()
        else:
            await query.answer("❌ Abhi join nahi kiya!", show_alert=True)
    except:
        await query.answer("⚠️ Check nahi ho paya. Dobara try karo.", show_alert=True)
