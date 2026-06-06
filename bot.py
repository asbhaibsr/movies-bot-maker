# ════════════════════════════════════════════════════════════
#   Main Bot — @createautofilterRobot
#   Creates Movie Bots (BotFather Style)
# ════════════════════════════════════════════════════════════

import sys, glob, importlib, logging, logging.config, pytz, asyncio
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

from AsBhai.bot import AsBhaiBot
from AsBhai.util.keepalive import ping_server
from AsBhai.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
AsBhaiBot.start()
loop = asyncio.get_event_loop()


async def start():
    print('\n')
    print('🚀 Starting @createautofilterRobot...')

    bot_info = await AsBhaiBot.get_me()
    await initialize_clients()

    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Module Loaded => " + plugin_name)

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.BOTS = []

    me = await AsBhaiBot.get_me()
    temp.BOT = AsBhaiBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name

    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    try:
        await AsBhaiBot.send_message(
            chat_id=LOG_CHANNEL,
            text=f"<b>🤖 Bot Started!\nTime: {today} {time}</b>"
        )
    except:
        print("Make Your Bot Admin In Log Channel")

    # Start expiry background task
    try:
        from plugins.clone_expiry import start_expiry_check
        await start_expiry_check(AsBhaiBot)
    except Exception as e:
        print(f"Expiry task error: {e}")

    # Saare clone bots restart karo
    if CLONE_MODE:
        print("🔄 Restarting All Clone Bots...")
        await restart_bots()
        print(f"✅ {len(temp.BOTS)} Clone Bots Running.")

    # Web server
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    print(f"\n✅ @{me.username} is LIVE!\n")
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Bot Stopped!')
