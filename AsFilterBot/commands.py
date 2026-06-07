# # # 
# 
import os, string, logging, random, asyncio, time, datetime, re, sys, json, base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import col, sec_col, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from AsFilterBot.database.clone_bot_userdb import clonedb
from info import *
from shortzy import Shortzy
from utils import get_size, temp, get_seconds, get_clone_shortlink
from database.subscription_db import is_active, days_remaining, PLANS
import asyncio
logger = logging.getLogger(__name__)


# ── 3 Second Update Channel Button (Auto Delete) ────────────
async def _send_update_btn_3sec(client, chat_id):
    """Start pe sirf 3 second ke liye @asbhai_bsr channel button dikhao, phir delete karo"""
    try:
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("📢 Updates: @asbhai_bsr", url="https://t.me/asbhai_bsr")
        ]])
        m = await client.send_message(
            chat_id,
            "<b>📢 Hamara update channel join karo!</b>",
            reply_markup=btn,
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(3)
        try:
            await m.delete()
        except Exception:
            pass
    except Exception:
        pass


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    me = await client.get_me()
    cd = await db.get_bot(me.id)
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        # 3 second update channel button
        asyncio.create_task(_send_update_btn_3sec(client, message.chat.id))
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{me.username}?startgroup=true')
        ]]
        if cd.get("update_channel_link"):
            buttons.append([InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🍿', url=cd["update_channel_link"])])
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.CLONE_START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, me.username, me.first_name), reply_markup=reply_markup)
        return 
    if not await clonedb.is_user_exist(me.id, message.from_user.id):
        await clonedb.add_user(me.id, message.from_user.id)
    if len(message.command) != 2:
        # 3 second update channel button (background task)
        asyncio.create_task(_send_update_btn_3sec(client, message.chat.id))

        # Buttons build karo
        buttons = [[
            InlineKeyboardButton('⤬ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⤬', url=f'http://t.me/{me.username}?startgroup=true')
        ],[
            InlineKeyboardButton('🕵️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('🔍 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if cd.get("update_channel_link"):
            buttons.append([InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🍿', url=cd["update_channel_link"])])
        # Custom buttons from manage panel
        for btn in (cd.get("start_buttons") or []):
            try:
                buttons.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
            except:
                pass
        reply_markup = InlineKeyboardMarkup(buttons)

        # Custom start message
        start_text = cd.get("start_message") or script.CLONE_START_TXT.format(
            message.from_user.mention, me.username, me.first_name
        )
        # Custom photo
        start_photo = cd.get("start_photo")
        if start_photo:
            await message.reply_photo(
                photo=start_photo,
                caption=start_text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                text=start_text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.startswith("sendfiles"):
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        g = await get_clone_shortlink(f"https://telegram.me/{me.username}?start=allfiles_{file_id}", cd["url"], cd["api"])
        t = cd["tutorial"]
        btn = [[
            InlineKeyboardButton('📂 Dᴏᴡɴʟᴏᴀᴅ Nᴏᴡ 📂', url=g)
        ],[
            InlineKeyboardButton('⁉️ Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ ⁉️', url=t)
        ]]
        k = await client.send_message(chat_id=message.from_user.id,text=f"<b>Get All Files in a Single Click!!!\n\n📂 ʟɪɴᴋ ➠ : {g}\n\n<i>Note: This message is deleted in 5 mins to avoid copyrights. Save the link to Somewhere else</i></b>", reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(300)
        await k.edit("<b>Your message is successfully deleted!!!</b>")
        return
        
    
    elif data.startswith("short"):
        user = message.from_user.id
        files_ = await get_file_details(file_id)
        files = files_
        g = await get_clone_shortlink(f"https://telegram.me/{me.username}?start=file_{file_id}", cd["url"], cd["api"]) 
        t = cd["tutorial"]
        btn = [[
            InlineKeyboardButton('📂 Dᴏᴡɴʟᴏᴀᴅ Nᴏᴡ 📂', url=g)
        ],[
            InlineKeyboardButton('⁉️ Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ ⁉️', url=t)
        ]]
        k = await client.send_message(chat_id=user,text=f"<b>📕Nᴀᴍᴇ ➠ : <code>{files['file_name']}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files['file_size'])}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}\n\n<i>Note: This message is deleted in 20 mins to avoid copyrights. Save the link to Somewhere else</i></b>", reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(1200)
        await k.edit("<b>Your message is successfully deleted!!!</b>")
        return
        
    elif data.startswith("all"):
        files = temp.GETALL.get(file_id)
        if not files:
            return await message.reply('<b><i>No such file exist.</b></i>')
        filesarr = []
        for file in files:
            vj_file_id = file['file_id']
            k = await temp.BOT.send_cached_media(chat_id=PUBLIC_FILE_CHANNEL, file_id=vj_file_id)
            vj = await client.get_messages(PUBLIC_FILE_CHANNEL, k.id)
            mg = getattr(vj, vj.media.value)
            file_id = mg.file_id
            files_ = await get_file_details(vj_file_id)
            files1 = files_
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1['file_name'].split()))
            size=get_size(files1['file_size'])
            f_caption=files1['caption']
            if f_caption is None:
                f_caption = f"@asbhaibsr {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1['file_name'].split()))}"
            if cd["update_channel_link"] != None:
                up = cd["update_channel_link"]
                button = [[
                    InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🍿', url=up)
                ]]
                reply_markup=InlineKeyboardMarkup(button)
            else:
                reply_markup=None
       
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=False,
                reply_markup=reply_markup
            )
            filesarr.append(msg)
        k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie Files/Videos will be deleted in <b><u>10 mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this ALL Files/Videos to your Saved Messages and Start Download there</i></b>")
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
        return    
    elif data.startswith("files"):
        if cd['url']:
            files_ = await get_file_details(file_id)
            files = files_
            g = await get_clone_shortlink(f"https://telegram.me/{me.username}?start=file_{file_id}", cd["url"], cd["api"])
            t = cd["tutorial"]
            btn = [[
                InlineKeyboardButton('📂 Dᴏᴡɴʟᴏᴀᴅ Nᴏᴡ 📂', url=g)
            ],[
                InlineKeyboardButton('⁉️ Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ ⁉️', url=t)
            ]]
            k = await client.send_message(chat_id=message.from_user.id,text=f"<b>📕Nᴀᴍᴇ ➠ : <code>{files['file_name']}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files['file_size'])}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}\n\n<i>Note: This message is deleted in 20 mins to avoid copyrights. Save the link to Somewhere else</i></b>", reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(1200)
            await k.edit("<b>Your message is successfully deleted!!!</b>")
            return
    user = message.from_user.id
    files_ = await get_file_details(file_id)           
    if not files_:
        return await message.reply('**No such file exist.**')
    files = files_
    title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files['file_name'].split()))
    size=get_size(files['file_size'])
    f_caption=files['caption']
    if f_caption is None:
        f_caption = f"@asbhaibsr {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files['file_name'].split()))}"
    if cd["update_channel_link"] != None:
        up = cd["update_channel_link"]
        button = [[
            InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🍿', url=up)
        ]]
        reply_markup=InlineKeyboardMarkup(button)
    else:
        reply_markup=None
    k = await temp.BOT.send_cached_media(chat_id=PUBLIC_FILE_CHANNEL, file_id=file_id)
    vj = await client.get_messages(PUBLIC_FILE_CHANNEL, k.id)
    m = getattr(vj, vj.media.value)
    file_id = m.file_id
    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=False,
        reply_markup=reply_markup
    )
    k = await msg.reply("<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>10 mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>",quote=True)
    await asyncio.sleep(600)
    await msg.delete()
    await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
    return   
  
@Client.on_message(filters.command("settings") & filters.private)
async def settings(client, message):
    me = await client.get_me()
    owner = await db.get_bot(me.id)
    if owner["user_id"] != message.from_user.id:
        return
    url = await client.ask(message.chat.id, "<b>Now Send Me Your Shortlink Site Domain Or Url Without https://</b>")
    api = await client.ask(message.chat.id, "<b>Now Send Your Api</b>")
    try:
        shortzy = Shortzy(api_key=api.text, base_site=url.text)
        link = 'https://t.me/asbhaibsr'
        await shortzy.convert(link)
    except Exception as e:
        await message.reply(f"**Error In Converting Link**\n\n<code>{e}</code>\n\n**Start The Process Again By - /settings**", reply_markup=InlineKeyboardMarkup(btn))
        return
    tutorial = await client.ask(message.chat.id, "<b>Now Send Me Your How To Open Link means Tutorial Link.</b>")
    if not tutorial.text.startswith(('https://', 'http://')):
        await message.reply("**Invalid Link. Start The Process Again By - /settings**")
        return 
    link = await client.ask(message.chat.id, "<b>Now Send Me Your Update Channel Link Which Is Shown In Your Start Button And Below File Button.</b>")
    if not link.text.startswith(('https://', 'http://')):
        await message.reply("**Invalid Link. Start The Process Again By - /settings**")
        return 
    data = {
        'url': url.text,
        'api': api.text,
        'tutorial': tutorial.text,
        'update_channel_link': link.text
    }
    await db.update_bot(me.id, data)
    await message.reply("**Successfully Added All Settings**")

@Client.on_message(filters.command("reset") & filters.private)
async def reset_settings(client, message):
    me = await client.get_me()
    owner = await db.get_bot(me.id)
    if owner["user_id"] != message.from_user.id:
        return
    if owner["url"] == None:
        await message.reply("**No Settings Found.**")
    else:
        data = {
            'url': None,
            'api': None,
            'tutorial': None,
            'update_channel_link': None
        }
        await db.update_bot(me.id, data)
        await message.reply("**Successfully Reset All Settings To Default.**")

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client, message):
    me = await client.get_me()
    total_users = await clonedb.total_users_count(me.id)
    filesp = col.count_documents({})
    totalsec = sec_col.count_documents({})
    total = int(filesp) + int(totalsec)
    await message.reply(f"**Total Files : {total}\n\nTotal Users : {total_users}**")


# ══════════════════════════════════════════════════════════
#  MISSING COMMANDS — Added
# ══════════════════════════════════════════════════════════

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.users_chats_db import db
from info import ADMINS
import asyncio, logging
logger = logging.getLogger(__name__)


# ── /help ──────────────────────────────────────────────
@Client.on_message(filters.command("help") & filters.incoming)
async def help_cmd(client, message: Message):
    me = await client.get_me()
    buttons = [
        [InlineKeyboardButton("🔍 Movie Search", callback_data="help_search"),
         InlineKeyboardButton("📁 File Store", callback_data="help_files")],
        [InlineKeyboardButton("🔧 Filters", callback_data="help_filters"),
         InlineKeyboardButton("⚙️ Settings", callback_data="help_settings")],
        [InlineKeyboardButton("💎 Premium", callback_data="help_premium"),
         InlineKeyboardButton("🤖 AI Chat", callback_data="help_ai")],
        [InlineKeyboardButton("👑 Admin", callback_data="help_admin")],
    ]
    await message.reply(
        f"<b>📖 Help Menu — @{me.username}</b>\n\n"
        "Neeche se apni category choose karo 👇",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_search$"))
async def help_search_cb(client, query):
    await query.message.edit_text(
        "<b>🔍 Movie Search Commands:</b>\n\n"
        "• Group mein movie name likho → auto search\n"
        "/search [name] — IMDB search\n"
        "/imdb [name] — IMDB info\n"
        "/topsearches — Top searched movies\n"
        "/trending — Trending movies\n"
        "/request [name] — Movie request karo\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_files$"))
async def help_files_cb(client, query):
    await query.message.edit_text(
        "<b>📁 File Commands (Admin):</b>\n\n"
        "/index — Channel index karo\n"
        "/delete [name] — File delete karo\n"
        "/deleteall — Saari files delete karo\n"
        "/link /plink — File link banao\n"
        "/batch /pbatch — Bulk links\n"
        "/backup — DB backup\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_filters$"))
async def help_filters_cb(client, query):
    await query.message.edit_text(
        "<b>🔧 Filter Commands:</b>\n\n"
        "/filter [word] [reply] — Filter add karo\n"
        "/viewfilters — Filters dekho\n"
        "/del [word] — Filter hatao\n"
        "/delall — Saare filters hatao\n"
        "/connect [group_id] — Group connect karo\n"
        "/disconnect — Disconnect karo\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_settings$"))
async def help_settings_cb(client, query):
    await query.message.edit_text(
        "<b>⚙️ Settings Commands:</b>\n\n"
        "/settings — Bot settings manage karo\n"
        "/enable [feature] — Feature on karo\n"
        "/disable [feature] — Feature off karo\n"
        "/fsub [channel] — Force subscribe set karo\n"
        "/nofsub — Force subscribe hatao\n"
        "/shortlink [url] [api] — Shortlink set karo\n"
        "/set_tutorial [url] — Tutorial link set karo\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_premium$"))
async def help_premium_cb(client, query):
    await query.message.edit_text(
        "<b>💎 Premium Commands:</b>\n\n"
        "/plan — Premium plans dekho\n"
        "/myplan — Apna plan dekho\n"
        "/redeem [code] — Redeem code use karo\n\n"
        "<b>Admin:</b>\n"
        "/add_premium [user_id] [days] — Premium do\n"
        "/remove_premium [user_id] — Premium hatao\n"
        "/premiumusers — Premium users list\n"
        "/genredeem [count] [days] — Codes banao\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_ai$"))
async def help_ai_cb(client, query):
    await query.message.edit_text(
        "<b>🤖 AI Commands:</b>\n\n"
        "/chat [question] — AI se baat karo\n"
        "/ai [question] — Same as /chat\n"
        "/ask [question] — Same as /chat\n\n"
        "<i>Hindi, English, Hinglish — sab chal ta hai!</i>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_admin$"))
async def help_admin_cb(client, query):
    await query.message.edit_text(
        "<b>👑 Admin Commands:</b>\n\n"
        "/stats — Bot stats\n"
        "/users — User count\n"
        "/broadcast [reply] — Sab users ko message\n"
        "/send [user_id] [msg] — Kisi ko message\n"
        "/ban [user_id] — Ban karo\n"
        "/unban [user_id] — Unban karo\n"
        "/restart — Bot restart karo\n"
        "/leave [chat_id] — Group se leave karo\n"
        "/maintenance on|off — Maintenance mode\n"
        "/channel — Connected channels\n"
        "/backup — DB backup\n"
        "/cleanup — Dead users clean karo\n"
        "/totalrequests — Movie requests count\n"
        "/purgerequests — Pending requests delete karo\n",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_back")]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^help_back$"))
async def help_back_cb(client, query):
    me = await client.get_me()
    buttons = [
        [InlineKeyboardButton("🔍 Movie Search", callback_data="help_search"),
         InlineKeyboardButton("📁 File Store", callback_data="help_files")],
        [InlineKeyboardButton("🔧 Filters", callback_data="help_filters"),
         InlineKeyboardButton("⚙️ Settings", callback_data="help_settings")],
        [InlineKeyboardButton("💎 Premium", callback_data="help_premium"),
         InlineKeyboardButton("🤖 AI Chat", callback_data="help_ai")],
        [InlineKeyboardButton("👑 Admin", callback_data="help_admin")],
    ]
    await query.message.edit_text(
        f"<b>📖 Help Menu — @{me.username}</b>\n\nNeeche se apni category choose karo 👇",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


# ── /id ──────────────────────────────────────────────
@Client.on_message(filters.command("id") & filters.incoming)
async def id_cmd(client, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        chat = message.chat
    else:
        user = message.from_user
        chat = message.chat
    text = f"<b>👤 User ID:</b> <code>{user.id if user else 'N/A'}</code>\n"
    if user:
        text += f"<b>Name:</b> {user.first_name}\n"
        text += f"<b>Username:</b> @{user.username or 'N/A'}\n\n"
    text += f"<b>💬 Chat ID:</b> <code>{chat.id}</code>\n"
    text += f"<b>Chat Title:</b> {chat.title or chat.first_name or 'N/A'}"
    await message.reply(text, parse_mode=enums.ParseMode.HTML)


# ── /info ─────────────────────────────────────────────
@Client.on_message(filters.command("info") & filters.incoming)
async def info_cmd(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user
    try:
        full = await client.get_users(user.id)
        mention = full.mention
        username = f"@{full.username}" if full.username else "N/A"
        premium = "✅ Yes" if getattr(full, 'is_premium', False) else "❌ No"
        text = (
            f"<b>ℹ️ User Info</b>\n\n"
            f"👤 Name: {full.first_name} {full.last_name or ''}\n"
            f"🆔 ID: <code>{full.id}</code>\n"
            f"📛 Username: {username}\n"
            f"💎 Premium: {premium}\n"
            f"🤖 Bot: {'Yes' if full.is_bot else 'No'}\n"
        )
    except Exception as e:
        text = f"<b>❌ Info nahi mili: {e}</b>"
    await message.reply(text, parse_mode=enums.ParseMode.HTML)


# ── /search /imdb ─────────────────────────────────────
@Client.on_message(filters.command(["search", "imdb"]) & filters.incoming)
async def search_imdb_cmd(client, message: Message):
    query_text = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not query_text:
        return await message.reply("<b>Usage:</b> <code>/search Movie Name</code>", parse_mode=enums.ParseMode.HTML)
    
    wait = await message.reply(f"<i>🔍 Searching IMDB for: {query_text}...</i>", parse_mode=enums.ParseMode.HTML)
    try:
        from utils import get_poster
        movie = await get_poster(query_text, bulk=False, id=False, file=None)
        if not movie:
            return await wait.edit_text(f"<b>❌ '{query_text}' IMDB par nahi mili.</b>", parse_mode=enums.ParseMode.HTML)
        
        title    = movie.get('title', 'N/A')
        year     = movie.get('year', 'N/A')
        rating   = movie.get('rating', 'N/A')
        genres   = ", ".join(movie.get('genres', []))
        overview = (movie.get('plot', '') or '')[:300]
        poster   = movie.get('poster', None)
        
        text = (
            f"<b>🎬 {title} ({year})</b>\n\n"
            f"⭐ Rating: {rating}/10\n"
            f"🎭 Genres: {genres}\n\n"
            f"📖 {overview}..."
        )
        btns = [[InlineKeyboardButton("🔍 Search This Movie", 
                 switch_inline_query_current_chat=title)]]
        if poster:
            await wait.delete()
            await message.reply_photo(poster, caption=text, 
                  reply_markup=InlineKeyboardMarkup(btns),
                  parse_mode=enums.ParseMode.HTML)
        else:
            await wait.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await wait.edit_text(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /request ─────────────────────────────────────────
@Client.on_message(filters.command("request") & filters.incoming)
async def request_cmd(client, message: Message):
    movie_name = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not movie_name:
        return await message.reply(
            "<b>Usage:</b> <code>/request Movie Name</code>\n\n"
            "Ya group mein <code>#request Movie Name</code> likho",
            parse_mode=enums.ParseMode.HTML
        )
    user = message.from_user
    from info import REQST_CHANNEL, LOG_CHANNEL
    req_channel = REQST_CHANNEL or LOG_CHANNEL
    text = (
        f"<b>🎬 #MovieRequest</b>\n\n"
        f"Movie: <b>{movie_name}</b>\n"
        f"By: {user.mention} (<code>{user.id}</code>)\n"
        f"Chat: {message.chat.title or 'PM'} (<code>{message.chat.id}</code>)"
    )
    try:
        await client.send_message(req_channel, text, parse_mode=enums.ParseMode.HTML)
        await message.reply(
            f"<b>✅ Request bhej di!</b>\n\n"
            f"🎬 <b>{movie_name}</b>\n\n"
            f"Admin jald se jald upload karega. 🙏",
            parse_mode=enums.ParseMode.HTML
        )
    except:
        await message.reply(f"<b>✅ Request note kar li: {movie_name}</b>", parse_mode=enums.ParseMode.HTML)


# ── /totalrequests ───────────────────────────────────
@Client.on_message(filters.command("totalrequests") & filters.incoming)
async def totalrequests_cmd(client, message: Message):
    me = await client.get_me()
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    await message.reply(
        "<b>📊 Movie Requests:</b>\n\n"
        "Requests REQST_CHANNEL mein jati hain.\n"
        "Wahan jaake count karo.",
        parse_mode=enums.ParseMode.HTML
    )


# ── /purgerequests ────────────────────────────────────
@Client.on_message(filters.command("purgerequests") & filters.incoming)
async def purgerequests_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    await message.reply(
        "<b>🗑️ Requests channel mein jao aur manually delete karo.</b>\n\n"
        "Ya REQST_CHANNEL var set karo.",
        parse_mode=enums.ParseMode.HTML
    )


# ── /delete /deleteall /deletefiles ──────────────────
@Client.on_message(filters.command("delete") & filters.incoming)
async def delete_file_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    file_name = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not file_name:
        return await message.reply(
            "<b>Usage:</b> <code>/delete file name</code>\n\nFile ka naam likho jo delete karni hai.",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        from database.ia_filterdb import col
        result = await col.delete_many({"$or": [
            {"file_name": {"$regex": file_name, "$options": "i"}},
            {"caption": {"$regex": file_name, "$options": "i"}}
        ]})
        await message.reply(
            f"<b>✅ {result.deleted_count} files delete ho gayi!</b>\n\nQuery: <code>{file_name}</code>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("deleteall") & filters.incoming)
async def deleteall_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    await message.reply(
        "<b>⚠️ SAARI files delete karni hain?</b>\n\nYe action UNDO nahi hoga!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Haan Delete Karo", callback_data="confirm_deleteall"),
             InlineKeyboardButton("❌ Cancel", callback_data="cancel_deleteall")]
        ]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^confirm_deleteall$"))
async def confirm_deleteall_cb(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("Sirf Admin!", show_alert=True)
    try:
        from database.ia_filterdb import col
        result = await col.delete_many({})
        await query.message.edit_text(
            f"<b>✅ {result.deleted_count} saari files delete ho gayi!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await query.message.edit_text(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex("^cancel_deleteall$"))
async def cancel_deleteall_cb(client, query):
    await query.message.edit_text("<b>❌ Cancel kar diya.</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("deletefiles") & filters.incoming)
async def deletefiles_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    file_names = message.text.split("\n")[1:]
    if not file_names:
        return await message.reply(
            "<b>Usage:</b>\n<code>/deletefiles\nFile Name 1\nFile Name 2\nFile Name 3</code>",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        from database.ia_filterdb import col
        deleted = 0
        for fn in file_names:
            fn = fn.strip()
            if fn:
                r = await col.delete_many({"file_name": {"$regex": fn, "$options": "i"}})
                deleted += r.deleted_count
        await message.reply(f"<b>✅ {deleted} files delete ho gayi!</b>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /set_template ─────────────────────────────────────
@Client.on_message(filters.command("set_template") & filters.incoming)
async def set_template_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    template = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not template:
        return await message.reply(
            "<b>Usage:</b> <code>/set_template your template here</code>\n\n"
            "Variables: {title} {year} {rating} {genres}",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        from utils import save_group_settings
        await save_group_settings(message.chat.id, "template", template)
        await message.reply(f"<b>✅ Template set ho gaya!</b>\n<code>{template}</code>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /myplan ───────────────────────────────────────────
@Client.on_message(filters.command("myplan") & filters.incoming)
async def myplan_cmd(client, message: Message):
    user_id = message.from_user.id
    try:
        user_data = await db.get_user(user_id)
        has_premium = await db.has_premium_access(user_id)
        if has_premium:
            expiry = user_data.get("expiry_time")
            import datetime
            days_left = max(0, (expiry - datetime.datetime.now()).days) if expiry else 0
            exp_str = expiry.strftime("%d %b %Y") if expiry else "N/A"
            await message.reply(
                f"<b>💎 Your Premium Plan</b>\n\n"
                f"✅ Status: <b>Active</b>\n"
                f"📅 Expiry: <b>{exp_str}</b>\n"
                f"⏳ Remaining: <b>{days_left} days</b>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply(
                "<b>❌ Aapke paas koi premium plan nahi hai.</b>\n\n"
                "/plan se plan dekho.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Plans Dekho", callback_data="vj_plan_pg#0")]]),
                parse_mode=enums.ParseMode.HTML
            )
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /add_premium /remove_premium ─────────────────────
@Client.on_message(filters.command("add_premium") & filters.incoming)
async def add_premium_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    args = message.command
    if len(args) < 3:
        return await message.reply("<b>Usage:</b> <code>/add_premium user_id days</code>", parse_mode=enums.ParseMode.HTML)
    try:
        user_id = int(args[1])
        days = int(args[2])
        import datetime
        expiry = datetime.datetime.now() + datetime.timedelta(days=days)
        await db.col.update_one(
            {"id": user_id},
            {"$set": {"is_premium": True, "expiry_time": expiry}},
            upsert=True
        )
        await message.reply(
            f"<b>✅ Premium diya!</b>\n\nUser: <code>{user_id}</code>\nDays: {days}\nExpiry: {expiry.strftime('%d %b %Y')}",
            parse_mode=enums.ParseMode.HTML
        )
        try:
            await client.send_message(user_id, f"<b>🎉 Aapko {days} din ka Premium mil gaya!\n\nExpiry: {expiry.strftime('%d %b %Y')}</b>", parse_mode=enums.ParseMode.HTML)
        except:
            pass
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("remove_premium") & filters.incoming)
async def remove_premium_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    args = message.command
    if len(args) < 2:
        return await message.reply("<b>Usage:</b> <code>/remove_premium user_id</code>", parse_mode=enums.ParseMode.HTML)
    try:
        user_id = int(args[1])
        await db.col.update_one({"id": user_id}, {"$set": {"is_premium": False}})
        await message.reply(f"<b>✅ Premium hataya!</b>\n\nUser: <code>{user_id}</code>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /premiumusers /pmusers ────────────────────────────
@Client.on_message(filters.command(["premiumusers", "pmusers"]) & filters.incoming)
async def premiumusers_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    try:
        premium_users = []
        async for u in db.col.find({"is_premium": True}):
            premium_users.append(u)
        if not premium_users:
            return await message.reply("<b>📭 Koi premium user nahi hai.</b>", parse_mode=enums.ParseMode.HTML)
        import datetime
        lines = [f"<b>💎 Premium Users ({len(premium_users)}):</b>\n"]
        for u in premium_users[:30]:
            uid = u.get("id", "?")
            exp = u.get("expiry_time")
            days_left = max(0, (exp - datetime.datetime.now()).days) if exp else 0
            exp_str = exp.strftime("%d %b %Y") if exp else "N/A"
            lines.append(f"• <code>{uid}</code> — {exp_str} ({days_left}d left)")
        await message.reply("\n".join(lines), parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /bulk_premium ─────────────────────────────────────
@Client.on_message(filters.command("bulk_premium") & filters.incoming)
async def bulk_premium_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    args = message.text.split("\n")
    days_line = args[0].split()
    if len(days_line) < 2:
        return await message.reply(
            "<b>Usage:</b>\n<code>/bulk_premium days\nuser_id1\nuser_id2\nuser_id3</code>",
            parse_mode=enums.ParseMode.HTML
        )
    try:
        days = int(days_line[1])
        user_ids = [int(x.strip()) for x in args[1:] if x.strip().isdigit()]
        import datetime
        expiry = datetime.datetime.now() + datetime.timedelta(days=days)
        count = 0
        for uid in user_ids:
            await db.col.update_one({"id": uid}, {"$set": {"is_premium": True, "expiry_time": expiry}}, upsert=True)
            count += 1
        await message.reply(f"<b>✅ {count} users ko {days} din ka premium diya!</b>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /genredeem /redeem ────────────────────────────────
REDEEM_CODES = {}

@Client.on_message(filters.command("genredeem") & filters.incoming)
async def genredeem_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    args = message.command
    count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
    days  = int(args[2]) if len(args) > 2 and args[2].isdigit() else 30
    import random, string
    codes = []
    for _ in range(min(count, 20)):
        code = "PREM-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        REDEEM_CODES[code] = days
        codes.append(code)
    code_list = "\n".join([f"<code>{c}</code> ({days} days)" for c in codes])
    await message.reply(f"<b>🎁 {len(codes)} Redeem Codes:</b>\n\n{code_list}", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("redeem") & filters.incoming)
async def redeem_cmd(client, message: Message):
    code = message.command[1] if len(message.command) > 1 else ""
    if not code:
        return await message.reply("<b>Usage:</b> <code>/redeem CODE</code>", parse_mode=enums.ParseMode.HTML)
    if code not in REDEEM_CODES:
        return await message.reply("<b>❌ Invalid ya already used code!</b>", parse_mode=enums.ParseMode.HTML)
    days = REDEEM_CODES.pop(code)
    import datetime
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    user_id = message.from_user.id
    await db.col.update_one({"id": user_id}, {"$set": {"is_premium": True, "expiry_time": expiry}}, upsert=True)
    await message.reply(
        f"<b>🎉 Premium Activate!</b>\n\nDays: {days}\nExpiry: {expiry.strftime('%d %b %Y')}",
        parse_mode=enums.ParseMode.HTML
    )


# ── /shortlink commands ───────────────────────────────
@Client.on_message(filters.command("shortlink") & filters.incoming)
async def shortlink_set_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    args = message.command
    if len(args) < 3:
        return await message.reply(
            "<b>Usage:</b> <code>/shortlink url api</code>\n\n"
            "Example: <code>/shortlink modijiurl.com abc123api</code>",
            parse_mode=enums.ParseMode.HTML
        )
    url, api = args[1], args[2]
    try:
        from utils import save_group_settings
        await save_group_settings(message.chat.id, "shortlink_url", url)
        await save_group_settings(message.chat.id, "shortlink_api", api)
    except Exception as e:
        pass
    await message.reply(f"<b>✅ Shortlink set!\nURL: {url}\nAPI: {api}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("setshortlinkon") & filters.incoming)
async def shortlink_on_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    from utils import save_group_settings
    await save_group_settings(message.chat.id, "is_shortlink", True)
    return await message.reply("<b>✅ Shortlink ON kar diya!</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("setshortlinkoff") & filters.incoming)
async def shortlink_off_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    from utils import save_group_settings
    await save_group_settings(message.chat.id, "is_shortlink", False)
    return await message.reply("<b>✅ Shortlink OFF kar diya!</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("shortlink_info") & filters.incoming)
async def shortlink_info_cmd(client, message: Message):
    settings = await db.get_settings(message.chat.id)
    url = settings.get("shortlink_url", "Set nahi hai")
    api = settings.get("shortlink_api", "Set nahi hai")
    on  = "✅ ON" if settings.get("is_shortlink") else "❌ OFF"
    await message.reply(
        f"<b>🔗 Shortlink Info</b>\n\nStatus: {on}\nURL: {url}\nAPI: {api}",
        parse_mode=enums.ParseMode.HTML
    )


# ── /set_tutorial /remove_tutorial ───────────────────
@Client.on_message(filters.command("set_tutorial") & filters.incoming)
async def set_tutorial_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    url = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not url:
        return await message.reply("<b>Usage:</b> <code>/set_tutorial URL</code>", parse_mode=enums.ParseMode.HTML)
    from utils import save_group_settings
    await save_group_settings(message.chat.id, "tutorial", url)
    return await message.reply(f"<b>✅ Tutorial link set!\n{url}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("remove_tutorial") & filters.incoming)
async def remove_tutorial_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    from utils import save_group_settings
    await save_group_settings(message.chat.id, "tutorial", None)
    return await message.reply("<b>✅ Tutorial link hata diya!</b>", parse_mode=enums.ParseMode.HTML)


# ── /fsub /nofsub ─────────────────────────────────────
@Client.on_message(filters.command("fsub") & filters.incoming)
async def fsub_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    channel = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not channel:
        return await message.reply(
            "<b>Usage:</b> <code>/fsub @channel</code> ya channel ID\n\nBot ko channel ka admin banana mat bhoolna!",
            parse_mode=enums.ParseMode.HTML
        )
    me = await client.get_me()
    bot_data = await db.get_bot(me.id)
    await db.update_bot(me.id, {"fsub_channel": channel})
    await message.reply(f"<b>✅ Force Subscribe set!\nChannel: {channel}</b>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("nofsub") & filters.incoming)
async def nofsub_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    me = await client.get_me()
    await db.update_bot(me.id, {"fsub_channel": None})
    await message.reply("<b>✅ Force Subscribe OFF kar diya!</b>", parse_mode=enums.ParseMode.HTML)


# ── /send ──────────────────────────────────────────────
@Client.on_message(filters.command("send") & filters.incoming)
async def send_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    if not message.reply_to_message:
        return await message.reply(
            "<b>Usage:</b> Kisi message ko reply karo + <code>/send user_id</code>",
            parse_mode=enums.ParseMode.HTML
        )
    args = message.command
    if len(args) < 2:
        return await message.reply("<b>Usage:</b> <code>/send user_id</code> (reply mein)", parse_mode=enums.ParseMode.HTML)
    try:
        user_id = int(args[1])
        await message.reply_to_message.copy(user_id)
        await message.reply(f"<b>✅ Message bheja user <code>{user_id}</code> ko!</b>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply(f"<b>❌ Error: {e}</b>", parse_mode=enums.ParseMode.HTML)


# ── /restart ──────────────────────────────────────────
@Client.on_message(filters.command("restart") & filters.incoming)
async def restart_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    await message.reply("<b>🔄 Bot restart ho raha hai...</b>", parse_mode=enums.ParseMode.HTML)
    import os, sys
    os.execl(sys.executable, sys.executable, *sys.argv)


# ── /channel ──────────────────────────────────────────
@Client.on_message(filters.command("channel") & filters.incoming)
async def channel_cmd(client, message: Message):
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Sirf Admin!</b>", parse_mode=enums.ParseMode.HTML)
    me = await client.get_me()
    bot_data = await db.get_bot(me.id)
    update_ch  = bot_data.get("update_channel_link") or "Set nahi hai"
    fsub_ch    = bot_data.get("fsub_channel") or "Set nahi hai"
    await message.reply(
        f"<b>📢 Bot Channels</b>\n\n"
        f"Update Channel: {update_ch}\n"
        f"Force Sub: {fsub_ch}",
        parse_mode=enums.ParseMode.HTML
    )


# ── /cancel ───────────────────────────────────────────
@Client.on_message(filters.command("cancel") & filters.incoming)
async def cancel_cmd(client, message: Message):
    await message.reply("<b>❌ Process cancel kar diya.</b>", parse_mode=enums.ParseMode.HTML)
