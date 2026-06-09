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

from pyrogram import Client, idle
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from datetime import date, datetime
from aiohttp import web
from plugins import web_server
from plugins.clone import restart_bots
from userbot import init_userbot, stop_userbot

from AsBhai.bot import AsBhaiBot
from AsBhai.util.keepalive import ping_server
from AsBhai.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
AsBhaiBot.start()  # same loop use karega jo upar set ki hai

async def start():
    print('\n')
    print('━' * 40)
    print('🤖 @createautofilterRobot starting...')
    print('━' * 40)

    await initialize_clients()

    # Plugins load karo
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

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Banned users/chats cache
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.BOTS = []

    # Bot info set karo
    me        = await AsBhaiBot.get_me()
    temp.BOT  = AsBhaiBot
    temp.ME   = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name

    tz   = pytz.timezone('Asia/Kolkata')
    now  = datetime.now(tz)
    today = date.today()
    time  = now.strftime("%H:%M:%S")

    try:
        await AsBhaiBot.send_message(
            LOG_CHANNEL,
            f"<b>✅ Bot Started!\n"
            f"🤖 @{me.username}\n"
            f"📅 {today} {time} IST</b>"
        )
    except Exception as e:
        print(f"LOG_CHANNEL error: {e}")

    # Expiry background task
    try:
        from plugins.clone_expiry import start_expiry_check
        asyncio.create_task(start_expiry_check(AsBhaiBot))
        print("⏰ Expiry check task started")
    except Exception as e:
        print(f"Expiry task error: {e}")

    # Userbot start karo (session string)
    try:
        await init_userbot()
    except Exception as e:
        print(f'Userbot: {e}')

    # Clone bots restart
    if CLONE_MODE:
        print("\n🔄 Restarting clone bots...")
        await restart_bots()

    # Web server start
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    print(f"\n{'━'*40}")
    print(f"✅ @{me.username} is LIVE on port {PORT}!")
    print(f"{'━'*40}\n")

    await idle()


if __name__ == '__main__':
    try:
        _loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Bot Stopped!')
