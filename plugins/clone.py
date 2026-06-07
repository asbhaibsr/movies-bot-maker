# ════════════════════════════════════════════════════════════
#  Clone Bot Manager — High Performance
#  Koyeb Free Tier Optimized
# ════════════════════════════════════════════════════════════
import logging, asyncio
from info import API_ID, API_HASH, CLONE_MODE
from database.users_chats_db import db
from utils import temp

logger = logging.getLogger(__name__)

BATCH_SIZE  = 3   # Ek saath kitne start karo
BATCH_DELAY = 2   # Seconds between batches


async def start_one_bot(bot_data: dict) -> bool:
    bot_token = bot_data.get("bot_token")
    if not bot_token:
        return False
    try:
        from pyrogram import Client
        vj = Client(
            f"clone_{bot_token[:8]}",
            API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "AsFilterBot"},
            sleep_threshold=60,
            max_concurrent_transmissions=2,
        )
        await vj.start()
        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(vj)
        me = await vj.get_me()
        logger.info(f"✅ @{me.username} started")
        return True
    except Exception as e:
        logger.error(f"❌ Clone start failed: {e}")
        return False


async def restart_bots():
    if not CLONE_MODE:
        return
    if not hasattr(temp, "BOTS"):
        temp.BOTS = []

    cursor    = await db.get_all_bots()
    all_bots  = await cursor.to_list(None)
    total     = len(all_bots)
    if total == 0:
        logger.info("No clone bots in DB.")
        return

    logger.info(f"Starting {total} clone bots...")
    success = failed = 0

    for i in range(0, total, BATCH_SIZE):
        batch   = all_bots[i: i + BATCH_SIZE]
        results = await asyncio.gather(
            *[start_one_bot(b) for b in batch],
            return_exceptions=True
        )
        for r in results:
            if r is True: success += 1
            else: failed += 1
        if i + BATCH_SIZE < total:
            await asyncio.sleep(BATCH_DELAY)

    logger.info(f"Done: {success} started, {failed} failed")
    print(f"✅ {success}/{total} Clone Bots Running")
