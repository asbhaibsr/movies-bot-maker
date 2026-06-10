# ════════════════════════════════════════════════════════════
#   @createautofilterRobot — Main Bot
#   BotFather Style Movie Bot Maker
# ════════════════════════════════════════════════════════════

import asyncio, sys, glob, importlib, logging, logging.config
import pytz

# Python 3.10+ fix: loop pehle banao — Motor/Pyrogram isi loop se judenge
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)
from pathlib import Path

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

from pyrogram import idle
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from datetime import date, datetime
from aiohttp import web
from plugins import web_server
from plugins.clone import restart_bots

# ── AsBhai streaming (optional — sirf IS_STREAM=True pe use hota hai) ────────
try:
    from AsBhai.bot import AsBhaiBot
    from AsBhai.util.keepalive import ping_server
    from AsBhai.bot.clients import initialize_clients
    STREAM_OK = True
except ImportError:
    STREAM_OK = False
    print("⚠️  AsBhai streaming module nahi mila — stream features disabled")

# ── Userbot (optional — sirf USER_SESSION_STRING set hone pe) ────────────────
try:
    from userbot import init_userbot, stop_userbot
    USERBOT_OK = True
except ImportError:
    USERBOT_OK = False

# ── Plugins glob ─────────────────────────────────────────────────────────────
ppath = "plugins/*.py"
files = glob.glob(ppath)


async def start():
    print('\n')
    print('━' * 40)
    print('🤖 @createautofilterRobot starting...')
    print('━' * 40)

    # ── Main bot start (AsBhaiBot) ────────────────────────────────────────────
    if STREAM_OK:
        await AsBhaiBot.start()
        await initialize_clients()
    else:
        # Streaming nahi hai toh direct pyrogram client use karo
        print("ℹ️  Stream mode OFF — direct bot client use ho raha hai")

    # ── Dynamic admins load karo (DB se) ─────────────────────────────────────
    try:
        dyn_ids = await db.get_dynamic_admins()
        for aid in dyn_ids:
            if aid not in ADMINS:
                ADMINS.append(aid)
        print(f"👑 {len(dyn_ids)} dynamic admins loaded (total: {len(ADMINS)})")
    except Exception as e:
        print(f"⚠️  Dynamic admins load error: {e}")

    # ── Banned users/chats cache ─────────────────────────────────────────────
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.BOTS = []

    # ── Bot info ─────────────────────────────────────────────────────────────
    if STREAM_OK:
        me = await AsBhaiBot.get_me()
        bot_client = AsBhaiBot
    else:
        # Fallback: koi bhi available bot client use karo
        me = None
        bot_client = None

    if me:
        temp.BOT    = bot_client
        temp.ME     = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name

    # ── Plugins load karo ────────────────────────────────────────────────────
    loaded = 0
    for name in files:
        with open(name) as a:
            patt        = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = f"plugins.{plugin_name}"
            try:
                spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules[import_path] = load
                loaded += 1
                print(f"  ✅ {plugin_name}")
            except Exception as e:
                print(f"  ❌ {plugin_name}: {e}")

    print(f"\n📦 {loaded} plugins loaded\n")

    # ── Startup log ──────────────────────────────────────────────────────────
    if me and bot_client:
        tz    = pytz.timezone('Asia/Kolkata')
        now   = datetime.now(tz)
        today = date.today()
        time_str = now.strftime("%H:%M:%S")
        try:
            await bot_client.send_message(
                LOG_CHANNEL,
                f"<b>✅ Bot Started!\n"
                f"🤖 @{me.username}\n"
                f"📅 {today} {time_str} IST\n"
                f"👑 Admins loaded: {len(ADMINS)}</b>"
            )
        except Exception as e:
            print(f"LOG_CHANNEL error: {e}")

    # ── Keepalive ping (Heroku/Koyeb) ────────────────────────────────────────
    if ON_HEROKU and STREAM_OK:
        asyncio.create_task(ping_server())

    # ── Expiry background check ──────────────────────────────────────────────
    try:
        from plugins.clone_expiry import start_expiry_check
        asyncio.create_task(start_expiry_check(bot_client))
        print("⏰ Expiry check task started")
    except Exception as e:
        print(f"⚠️  Expiry task error: {e}")

    # ── Userbot start ────────────────────────────────────────────────────────
    if USERBOT_OK:
        try:
            await init_userbot()
            print("👤 Userbot started")
        except Exception as e:
            print(f"⚠️  Userbot: {e}")

    # ── Clone bots restart ──────────────────────────────────────────────────
    if CLONE_MODE:
        print("\n🔄 Restarting clone bots...")
        await restart_bots()

    # ── Web server ───────────────────────────────────────────────────────────
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    if me:
        print(f"\n{'━'*40}")
        print(f"✅ @{me.username} is LIVE on port {PORT}!")
        print(f"{'━'*40}\n")
    else:
        print(f"\n✅ Bot LIVE on port {PORT}!\n")

    await idle()


if __name__ == '__main__':
    try:
        _loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Bot Stopped!')
    finally:
        if USERBOT_OK:
            try:
                _loop.run_until_complete(stop_userbot())
            except:
                pass
