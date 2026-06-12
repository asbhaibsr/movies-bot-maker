# ════════════════════════════════════════════════════════════
#   Clone Bot — /index command
#   FIXED: No permission prompt, 3-file batch limit, smooth indexing
# ════════════════════════════════════════════════════════════
import logging, re, asyncio
from utils import temp
from info import ADMINS
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

# Batch size — max 3 files at a time to prevent hang
INDEX_BATCH_SIZE = 3
INDEX_BATCH_DELAY = 1.5  # seconds between batches

from clone_filter import clone_admin, clone_or_group_admin


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)

    msg = query.message
    await query.answer('Processing...⏳', show_alert=True)

    await msg.edit(
        "Starting Indexing...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message(filters.private & filters.command('index'))
async def send_for_index(bot, message):
    """
    Clone owner /index use karke apna channel index kar sakta hai.
    No permission prompt — seedha karo.
    """
    me = await bot.get_me()
    bot_data = await db.get_bot(me.id)
    owner_id = bot_data.get("user_id")

    # Owner ya main admin check
    if message.from_user.id not in ADMINS and message.from_user.id != owner_id:
        return await message.reply(
            "<b>❌ Ye command sirf bot owner ke liye hai!</b>",
            parse_mode=enums.ParseMode.HTML
        )

    vj = await bot.ask(
        message.chat.id,
        "<b>📁 Channel Index Karo</b>\n\n"
        "Apne channel ki <b>last post ka link</b> ya message <b>forward</b> karo:\n\n"
        "Skip number set karne ke liye: <code>/setskip NUMBER</code>\n\n"
        "⏱️ 5 min ka time:",
        parse_mode=enums.ParseMode.HTML
    )

    if vj.forward_from_chat and vj.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = vj.forward_from_message_id
        chat_id = vj.forward_from_chat.username or vj.forward_from_chat.id
    elif vj.text:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(vj.text)
        if not match:
            return await vj.reply('<b>❌ Invalid link! Dobara /index karo.</b>', parse_mode=enums.ParseMode.HTML)
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    else:
        return

    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await vj.reply(
            '<b>❌ Private channel hai. Pehle mujhe us channel ka admin banao.</b>',
            parse_mode=enums.ParseMode.HTML
        )
    except (UsernameInvalid, UsernameNotModified):
        return await vj.reply('<b>❌ Invalid link.</b>', parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        return await vj.reply(f'<b>❌ Error: {e}</b>', parse_mode=enums.ParseMode.HTML)

    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply(
            '<b>❌ Message nahi mila. Bot ko channel ka admin banao.</b>',
            parse_mode=enums.ParseMode.HTML
        )
    if k.empty:
        return await message.reply('<b>❌ Empty message. Check karo.</b>', parse_mode=enums.ParseMode.HTML)

    # Direct index — no approval needed for clone owner
    confirm_msg = await message.reply(
        f'<b>📁 Index Confirm Karo</b>\n\n'
        f'Channel: <code>{chat_id}</code>\n'
        f'Last Msg ID: <code>{last_msg_id}</code>\n\n'
        f'<b>Dhyan rakhein:</b> 3 files ek saath index hoti hain — bot hang nahi hoga.',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton('✅ Index Karo', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}'),
            InlineKeyboardButton('❌ Cancel', callback_data='close_data')
        ]]),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command('setskip') & filters.incoming)
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Skip number number hona chahiye.")
        await message.reply(f"✅ Skip number: {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Usage: <code>/setskip 100</code>", parse_mode=enums.ParseMode.HTML)


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    """
    Index with 3-file batch limit to prevent bot hang.
    """
    total_files = 0
    duplicate   = 0
    errors      = 0
    deleted     = 0
    no_media    = 0
    unsupported = 0

    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            batch_count = 0

            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    await msg.edit(
                        f"<b>Cancelled!</b>\n\n"
                        f"Saved: <code>{total_files}</code>\n"
                        f"Duplicate: <code>{duplicate}</code>\n"
                        f"Errors: <code>{errors}</code>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    break

                current += 1
                batch_count += 1

                # Progress update every 30 messages
                if current % 30 == 0:
                    can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    try:
                        await msg.edit_text(
                            f"<b>Indexing...</b>\n\n"
                            f"Fetched: <code>{current}</code>\n"
                            f"Saved: <code>{total_files}</code>\n"
                            f"Duplicate: <code>{duplicate}</code>\n"
                            f"Errors: <code>{errors}</code>",
                            reply_markup=reply,
                            parse_mode=enums.ParseMode.HTML
                        )
                    except MessageNotModified:
                        pass

                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue

                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue

                media.caption = message.caption
                aynav, vnay = await save_file(media, channel_id=message.chat.id, msg_id=message.id)
                if aynav:
                    total_files += 1
                elif vnay == 0:
                    duplicate += 1
                elif vnay == 2:
                    errors += 1

                # Batch delay — 3 files ke baad 1.5 sec wait
                if batch_count >= INDEX_BATCH_SIZE:
                    batch_count = 0
                    await asyncio.sleep(INDEX_BATCH_DELAY)

        except Exception as e:
            logger.exception(e)
            await msg.edit(
                f'<b>❌ Error: {e}</b>\n\n'
                f'Saved: <code>{total_files}</code>',
                parse_mode=enums.ParseMode.HTML
            )
            return
        else:
            await msg.edit(
                f'<b>✅ Index Complete!</b>\n\n'
                f'Total Saved: <code>{total_files}</code>\n'
                f'Duplicate Skipped: <code>{duplicate}</code>\n'
                f'Deleted Messages: <code>{deleted}</code>\n'
                f'Non-Media Skipped: <code>{no_media + unsupported}</code>\n'
                f'Errors: <code>{errors}</code>',
                parse_mode=enums.ParseMode.HTML
            )
