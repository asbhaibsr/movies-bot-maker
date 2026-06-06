# ════════════════════════════════════════════════
#  Clone Bot Manager — Restart on startup
# ════════════════════════════════════════════════
import logging, asyncio
from info import API_ID, API_HASH, CLONE_MODE
from database.users_chats_db import db
from utils import temp

logger = logging.getLogger(__name__)


async def restart_bots():
    """Startup pe saare clone bots restart karo"""
    if not CLONE_MODE:
        return

    if not hasattr(temp, "BOTS"):
        temp.BOTS = []

    bots_cursor = await db.get_all_bots()
    bots = await bots_cursor.to_list(None)
    count = 0
    for bot_data in bots:
        bot_token = bot_data.get("bot_token")
        if not bot_token:
            continue
        try:
            from pyrogram import Client
            vj = Client(
                f"clone_{bot_token[:8]}",
                API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "AsFilterBot"},
            )
            await vj.start()
            temp.BOTS.append(vj)
            count += 1
            logger.info(f"Clone bot started: {bot_token[:10]}...")
        except Exception as e:
            logger.error(f"Clone restart error [{bot_token[:10]}]: {e}")

    logger.info(f"Total {count} clone bots restarted.")
