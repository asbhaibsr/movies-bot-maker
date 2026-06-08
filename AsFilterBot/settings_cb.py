# ════════════════════════════════════════════════════════════
#   Clone Bot Settings Callbacks
#   PM Search / IMDB / Protect / Stream / Shortlink / Auto Delete
# ════════════════════════════════════════════════════════════
import asyncio, logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ListenerTimeout
from database.users_chats_db import db
from info import ADMINS
from shortzy import Shortzy

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
    pm    = "✅" if bd.get("pm_search", True)       else "❌"
    imdb  = "✅" if bd.get("imdb_on", True)          else "❌"
    prot  = "✅" if bd.get("protect_content", False) else "❌"
    strm  = "✅" if bd.get("stream_mode", False)     else "❌"
    sl    = "✅" if bd.get("is_shortlink", False)    else "❌"
    sl_url= (bd.get("shortlink_url") or "Not set")[:25]
    sl_t  = bd.get("shortlink_verify_time", 0)
    ad    = bd.get("auto_delete", 600)
    mb    = bd.get("max_results", 10)
    ad_t  = f"{ad//60} min" if ad else "Off"

    text = (
        f"<b>⚙️ Settings — @{me.username}</b>\n\n"
        f"🔍 PM Search: {pm}\n"
        f"🎬 IMDB: {imdb}\n"
        f"🔒 Protect: {prot}\n"
        f"📺 Stream: {strm}\n"
        f"🗑️ Auto Del: {ad_t}\n"
        f"🔢 Max Btns: {mb}\n"
        f"🔗 Shortlink: {sl} | {sl_url}\n"
        f"⏱️ Verify: {sl_t}h\n"
    )
    btns = [
        [
            InlineKeyboardButton(f"{pm} PM Search", callback_data="tog_pm"),
            InlineKeyboardButton(f"{imdb} IMDB", callback_data="tog_imdb"),
        ],
        [
            InlineKeyboardButton(f"{prot} Protect", callback_data="tog_protect"),
            InlineKeyboardButton(f"{strm} Stream", callback_data="tog_stream"),
        ],
        [
            InlineKeyboardButton(f"{sl} Shortlink", callback_data="tog_sl"),
            InlineKeyboardButton("🔗 Set URL+API", callback_data="set_sl_api"),
        ],
        [
            InlineKeyboardButton(f"⏱️ Verify ({sl_t}h)", callback_data="set_vt"),
            InlineKeyboardButton(f"🔢 Max ({mb})", callback_data="set_mb"),
        ],
        [InlineKeyboardButton(f"🗑️ Auto Del ({ad_t})", callback_data="set_ad")],
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
    v = not bd.get("imdb_on", True)
    await _save(client, "imdb_on", v)
    await query.answer(f"IMDB {'ON' if v else 'OFF'} ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^tog_protect$"))
async def tog_protect(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    v = not bd.get("protect_content", False)
    await _save(client, "protect_content", v)
    await query.answer(f"Protect {'ON' if v else 'OFF'} ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^tog_stream$"))
async def tog_stream(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    v = not bd.get("stream_mode", False)
    await _save(client, "stream_mode", v)
    await query.answer(f"Stream {'ON' if v else 'OFF'} ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^tog_sl$"))
async def tog_sl(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    me = await client.get_me()
    bd = await db.get_bot(me.id)
    if not bd.get("shortlink_url"):
        return await query.answer("❌ Pehle URL+API set karo!", show_alert=True)
    v = not bd.get("is_shortlink", False)
    await _save(client, "is_shortlink", v)
    await query.answer(f"Shortlink {'ON' if v else 'OFF'} ✅")
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^set_sl_api$"))
async def set_sl_api(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    user_id = query.from_user.id
    await query.message.edit_text(
        "<b>🔗 Shortlink URL + API Set Karo</b>\n\n"
        "2 line mein bhejo:\n"
        "<code>modijiurl.com\nabc123apikey</code>\n\n"
        "👉 Bhejo ya /cancel:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_settings")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )
    try:
        reply = await client.listen(user_id, timeout=120)
    except (asyncio.TimeoutError, ListenerTimeout):
        return
    if reply.text and reply.text.strip().lower() in ["/cancel"]:
        return await reply.reply("❌ Cancel.")
    lines = (reply.text or "").strip().split("\n")
    if len(lines) < 2:
        return await reply.reply(
            "❌ 2 lines chahiye:\n<code>URL\nAPI</code>",
            parse_mode=enums.ParseMode.HTML
        )
    sl_url = lines[0].strip().replace("https://", "").replace("http://", "")
    sl_api = lines[1].strip()
    try:
        shortzy = Shortzy(api_key=sl_api, base_site=sl_url)
        await shortzy.convert("https://t.me/asbhai_bsr")
        await _save(client, "shortlink_url", sl_url)
        await _save(client, "shortlink_api", sl_api)
        await reply.reply(
            f"<b>✅ Shortlink set!</b>\nURL: {sl_url}\nAPI: ***...{sl_api[-4:]}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Settings", callback_data="back_settings")]
            ]),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await reply.reply(
            f"<b>❌ Invalid shortlink:</b>\n<code>{e}</code>",
            parse_mode=enums.ParseMode.HTML
        )


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


@Client.on_callback_query(filters.regex("^set_ad$"))
async def set_ad(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    await query.message.edit_text(
        "<b>🗑️ Auto Delete Time</b>\n\nKitne minute baad file delete ho?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5 min",  callback_data="ad_300"),
                InlineKeyboardButton("10 min", callback_data="ad_600"),
            ],
            [
                InlineKeyboardButton("30 min", callback_data="ad_1800"),
                InlineKeyboardButton("1 Hour", callback_data="ad_3600"),
            ],
            [
                InlineKeyboardButton("❌ Off", callback_data="ad_0"),
                InlineKeyboardButton("🔙 Back", callback_data="back_settings"),
            ],
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^ad_(\d+)$"))
async def ad_val(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    secs = int(query.matches[0].group(1))
    await _save(client, "auto_delete", secs)
    txt = f"{secs//60} min" if secs > 0 else "Off"
    await query.answer(f"✅ Auto delete: {txt}", show_alert=True)
    await _refresh(client, query)


@Client.on_callback_query(filters.regex("^back_settings$"))
async def back_settings(client, query):
    if not await _is_owner(client, query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)
    await _refresh(client, query)
