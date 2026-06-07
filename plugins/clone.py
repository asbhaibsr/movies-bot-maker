# ════════════════════════════════════════════════════════════
#  Clone Bot Manager
#  - Startup pe saare clone bots restart karo
#  - Koyeb free tier ke liye optimized (no flood, small batches)
# ════════════════════════════════════════════════════════════

import logging, asyncio
from info import API_ID, API_HASH, CLONE_MODE
from database.users_chats_db import db
from utils import temp

logger = logging.getLogger(__name__)

# Ek saath kitne bots start karo (free tier ke liye 3 sahi hai)
BATCH_SIZE  = 3
BATCH_DELAY = 2   # seconds between batches


async def start_one_bot(bot_data: dict) -> bool:
    """Ek clone bot start karo. True = success, False = failed."""
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
            sleep_threshold=60,        # flood wait handle
            max_concurrent_transmissions=2,  # less memory
        )
        await vj.start()
        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(vj)
        me = await vj.get_me()
        logger.info(f"✅ Clone started: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Clone start failed [{bot_token[:10]}]: {e}")
        return False


async def restart_bots():
    """Startup pe saare clone bots restart karo — batch mein."""
    if not CLONE_MODE:
        logger.info("CLONE_MODE disabled — skipping clone restart")
        return

    if not hasattr(temp, "BOTS"):
        temp.BOTS = []

    bots_cursor = await db.get_all_bots()
    all_bots = await bots_cursor.to_list(None)
    total = len(all_bots)

    if total == 0:
        logger.info("No clone bots in DB.")
        return

    logger.info(f"Starting {total} clone bots in batches of {BATCH_SIZE}...")
    success = 0
    failed  = 0

    # Batch mein start karo — free tier flood se bachao
    for i in range(0, total, BATCH_SIZE):
        batch = all_bots[i : i + BATCH_SIZE]
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

    logger.info(f"Clone bots: {success} started, {failed} failed (Total: {total})")
    print(f"✅ {success}/{total} Clone Bots Running")
