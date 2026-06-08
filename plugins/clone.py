# ════════════════════════════════════════════════════════════
#  Clone Bot Manager — High Performance
#  Main bot NEVER slows down, clones start in background
# ════════════════════════════════════════════════════════════
import logging, asyncio
from info import API_ID, API_HASH, CLONE_MODE
from database.users_chats_db import db
from utils import temp

logger = logging.getLogger(__name__)

BATCH_SIZE  = 3    # Ek saath kitne start karo
BATCH_DELAY = 3    # Seconds between batches (memory relief)
START_DELAY = 5    # Main bot ready hone ke baad delay (seconds)


async def start_one_bot(bot_data: dict) -> bool:
    """Ek clone bot start karo. Returns True on success."""
    bot_token = bot_data.get("bot_token")
    if not bot_token:
        return False
    try:
        from pyrogram import Client
        clone = Client(
            f"clone_{bot_token[:8]}",
            API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "AsFilterBot"},
            sleep_threshold=60,          # Flood auto handle
            max_concurrent_transmissions=1,  # Min memory per clone
            workers=4,                   # Limited workers per clone
        )
        await clone.start()
        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(clone)
        me = await clone.get_me()
        logger.info(f"✅ @{me.username} started")
        return True
    except Exception as e:
        logger.error(f"❌ Clone start failed [{bot_token[:8]}]: {e}")
        return False


async def restart_bots():
    """
    Clones ko BACKGROUND mein start karo.
    Main bot immediately ready rahega — clones baad mein start honge.
    """
    if not CLONE_MODE:
        return
    if not hasattr(temp, "BOTS"):
        temp.BOTS = []

    cursor   = await db.get_all_bots()
    all_bots = await cursor.to_list(None)
    total    = len(all_bots)
    if total == 0:
        logger.info("No clone bots in DB.")
        return

    # Background task — main bot ko block nahi karta
    asyncio.create_task(_start_all_in_background(all_bots))
    logger.info(f"Queued {total} clone bots to start in background...")
    print(f"  ⏳ {total} clone bots queuing in background...")


async def _start_all_in_background(all_bots: list):
    """Background mein sab clones batches mein start karo"""
    total   = len(all_bots)
    success = 0
    failed  = 0

    # Thoda wait karo jisse main bot pehle settle ho
    await asyncio.sleep(START_DELAY)

    for i in range(0, total, BATCH_SIZE):
        batch   = all_bots[i: i + BATCH_SIZE]
        results = await asyncio.gather(
            *[start_one_bot(b) for b in batch],
            return_exceptions=True
        )
        for r in results:
            if r is True:
                success += 1
            else:
                failed += 1
        if i + BATCH_SIZE < total:
            await asyncio.sleep(BATCH_DELAY)

    logger.info(f"Clones done: {success} started, {failed} failed / {total} total")
    print(f"  ✅ {success}/{total} clone bots running now!")
