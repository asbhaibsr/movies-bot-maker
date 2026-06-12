# ════════════════════════════════════════════════════════════
#   Clone Bot Settings — /settings command
#   UPDATED: Removed Protect, Set URL+API, Shortlink toggle, Auto Delete
#   KEPT: PM Search, IMDB (asks API), Stream (premium only), Verify Time, Max Buttons
# ════════════════════════════════════════════════════════════
import asyncio, logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ListenerTimeout
from database.users_chats_db import db
from info import ADMINS

logger = logging.getLogger(__name__)


async def _is_owner(client, user_id: int) -> bool:
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    return user_id == bd.get("user_id") or user_id in ADMINS


async def _save(client, key, value):
    me = await client.get_me()
    await db.update_bot(me.id, {key: value})


async def _refresh(client, query):
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    pm    = "✅" if bd.get("pm_search", True)   else "❌"
    imdb  = "✅" if bd.get("imdb_on", True)      else "❌"
    strm  = "✅" if bd.get("stream_mode", False) else "❌"
    sl_t  = bd.get("shortlink_verify_time", 0)
    mb    = bd.get("max_results", 10)

    # Button mode: inline buttons ya hyperlinks
    btn_mode = bd.get("button_mode", "button")
    btn_mode_label = "🔵 Button Mode" if btn_mode == "button" else "🔗 Link Mode"

    text = (
        f"<b>⚙️ Settings — @{me.username}</b>\n\n"
        f"🔍 PM Search: {pm}\n"
        f"🎬 IMDB: {imdb}\n"
        f"📺 Stream: {strm} (Premium users only)\n"
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
    try:
        await query.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(btns),
            parse_mode=enums.ParseMode.HTML
        )
    except:
        await query.answer("✅ Updated!")


from clone_filter import clone_admin, clone_or_group_admin

@Client.on_callback_query(filters.regex("^tog_pm$"))
async def tog_pm(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    v = not bd.get("pm_search", True)
    await _save(client, "pm_search", v)
    await query.answer(f"PM Search {'ON' if v else 'OFF'} ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^tog_imdb$"))
async def tog_imdb(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    currently_on = bd.get("imdb_on", True)

    if not currently_on:
        # Turning ON — ask for API key if not set
        current_api = bd.get("tmdb_api") or bd.get("omdb_api")
        if not current_api:
            user_id = query.from_user.id
            await query.message.edit_text(
                "<b>🎬 IMDB On Karne Ke Liye API Key Chahiye</b>\n\n"
                "TMDB ya OMDB ki free API key enter karo:\n\n"
                "TMDB: https://www.themoviedb.org/settings/api\n"
                "OMDB: https://www.omdbapi.com/apikey.aspx\n\n"
                "API key bhejo ya /skip (IMDB bina API ke bhi kaam karega):",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_settings")]]),
                parse_mode=enums.ParseMode.HTML
            )
            try:
                reply = await client.listen(user_id, timeout=120)
            except (asyncio.TimeoutError, ListenerTimeout):
                return
            if reply.text and reply.text.strip().lower() not in ["/skip", "skip"]:
                api_key = reply.text.strip()
                await _save(client, "tmdb_api", api_key)
            # Now turn on
            await _save(client, "imdb_on", True)
            await reply.reply(
                "<b>✅ IMDB ON kar diya!</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Settings", callback_data="back_settings")]]),
                parse_mode=enums.ParseMode.HTML
            )
            return
    # Toggle
    v = not currently_on
    await _save(client, "imdb_on", v)
    await query.answer(f"IMDB {'ON' if v else 'OFF'} ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^tog_stream$"))
async def tog_stream(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    v = not bd.get("stream_mode", False)
    await _save(client, "stream_mode", v)
    await query.answer(f"Stream {'ON' if v else 'OFF'} — Premium users only ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^tog_btn_mode$"))
async def tog_btn_mode(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    current = bd.get("button_mode", "button")
    new_mode = "link" if current == "button" else "button"
    await _save(client, "button_mode", new_mode)
    label = "Link Mode" if new_mode == "link" else "Button Mode"
    await query.answer(f"{label} set! ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^set_vt$"))
async def set_vt(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    await query.message.edit_text(
        "<b>⏱️ Shortlink Verify Time</b>\n\nKitne ghante baad dobara verify karna padega?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("6h",  callback_data="vt_6"),
                InlineKeyboardButton("12h", callback_data="vt_12"),
            ],
            [
                InlineKeyboardButton("24h", callback_data="vt_24"),
                InlineKeyboardButton("48h", callback_data="vt_48"),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_settings")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^vt_(\d+)$"))
async def vt_val(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    hours = int(query.matches[0].group(1))
    await _save(client, "shortlink_verify_time", hours)
    await query.answer(f"✅ Verify time: {hours}h set!", show_alert=True)
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^set_mb$"))
async def set_mb(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    await query.message.edit_text(
        "<b>🔢 Max Result Buttons</b>\n\nKitne buttons dikhane hain?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5",  callback_data="mb_5"),
                InlineKeyboardButton("8",  callback_data="mb_8"),
                InlineKeyboardButton("10", callback_data="mb_10"),
            ],
            [
                InlineKeyboardButton("15", callback_data="mb_15"),
                InlineKeyboardButton("20", callback_data="mb_20"),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_settings")],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^mb_(\d+)$"))
async def mb_val(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    val = int(query.matches[0].group(1))
    await _save(client, "max_results", val)
    await query.answer(f"✅ Max buttons: {val} set!", show_alert=True)
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^back_settings$"))
async def back_settings(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    await _refresh(client, query)
