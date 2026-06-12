# ════════════════════════════════════════════════════════════
#   Clone Bot Manager — Queue System for Free Tier
#   MAX_CONCURRENT_BOTS: kitne bots ek saath chalein
#   Inactive bots automatically stop → queue se naya start
# ════════════════════════════════════════════════════════════
import asyncio, logging, time
from pyrogram import Client as PyroClient
from database.users_chats_db import db
from info import API_ID, API_HASH, CLONE_MODE, LOG_CHANNEL, ADMINS
from AsFilterBot.database.clone_bot_userdb import clonedb
from utils import temp

logger = logging.getLogger(__name__)

# ── Free tier limits ─────────────────────────────────────────
# Koyeb free: ~512MB RAM, ~0.1 vCPU
# Each Pyrogram idle client ~8-12MB
# Free tier safe: 35-40 concurrent
# Paid small plan: 150-200
MAX_CONCURRENT_BOTS = 40       # Change to 200+ after upgrading plan
BOT_INACTIVE_TIMEOUT = 1800    # 30 min inactive → stop karo
START_DELAY = 3                # Main bot settle time before queue starts
BATCH_SIZE  = 5                # Ek saath kitne start karein
BATCH_DELAY = 2.0              # Seconds between batches

# ── Runtime tracking ─────────────────────────────────────────
_bot_last_activity: dict = {}  # bot_id → last activity timestamp
_bot_clients: dict = {}        # bot_id → PyroClient
_queue_lock = asyncio.Lock()

# ─────────────────────────────────────────────────────────────


def touch_bot(bot_id: int):
    """Bot activity record karo"""
    _bot_last_activity[bot_id] = time.time()


def get_running_count() -> int:
    return len(_bot_clients)


async def start_one_bot(bot_data: dict) -> bool:
    """Single clone bot start karo, runtime dict mein register karo"""
    token    = bot_data.get("bot_token")
    bot_id   = bot_data.get("bot_id")
    bot_uname = bot_data.get("bot_username", "?")

    if not token or not bot_id:
        return False

    # Already running check
    if bot_id in _bot_clients:
        touch_bot(bot_id)
        return True

    try:
        c = PyroClient(
            f"clone_{bot_id}",
            API_ID, API_HASH,
            bot_token=token,
            plugins={"root": "AsFilterBot"},
        )
        await c.start()
        _bot_clients[bot_id] = c
        touch_bot(bot_id)

        # temp.BOTS mein bhi rakho (existing code compatibility)
        if not hasattr(temp, "BOTS"):
            temp.BOTS = []
        temp.BOTS.append(c)

        logger.info(f"✅ Bot started: @{bot_uname}")
        return True
    except Exception as e:
        logger.warning(f"❌ Bot start failed @{bot_uname}: {e}")
        return False


async def stop_one_bot(bot_id: int) -> bool:
    """Bot gracefully stop karo"""
    c = _bot_clients.pop(bot_id, None)
    _bot_last_activity.pop(bot_id, None)
    if c:
        try:
            await c.stop()
            # temp.BOTS se bhi hatao
            if hasattr(temp, "BOTS") and c in temp.BOTS:
                temp.BOTS.remove(c)
            return True
        except Exception as e:
            logger.warning(f"Stop error bot {bot_id}: {e}")
    return False


async def _evict_oldest_inactive() -> bool:
    """Sabse zyada inactive bot hatao slot ke liye"""
    if not _bot_last_activity:
        return False
    oldest_id = min(_bot_last_activity, key=_bot_last_activity.get)
    logger.info(f"Evicting inactive bot {oldest_id} to free slot")
    return await stop_one_bot(oldest_id)


async def get_or_wake_bot(bot_id: int):
    """
    Bot ka client return karo.
    Agar queue mein hai, queue se nikaalo aur start karo.
    """
    async with _queue_lock:
        # Already running
        if bot_id in _bot_clients:
            touch_bot(bot_id)
            return _bot_clients[bot_id]

        # Queue mein hai — start karo
        bot_data = await db.get_bot(bot_id)
        if not bot_data or not bot_data.get("bot_token"):
            return None

        # Agar limit hit ho gayi → oldest inactive evict karo
        if get_running_count() >= MAX_CONCURRENT_BOTS:
            evicted = await _evict_oldest_inactive()
            if not evicted:
                logger.warning(f"Queue full ({MAX_CONCURRENT_BOTS}), could not evict for bot {bot_id}")
                return None

        ok = await start_one_bot(bot_data)
        return _bot_clients.get(bot_id) if ok else None


async def _inactive_monitor():
    """
    Background task: har 10 min check karo
    Agar bot BOT_INACTIVE_TIMEOUT se zyada idle → stop
    Ye slot free karta hai doosre bots ke liye
    """
    while True:
        await asyncio.sleep(600)
        now = time.time()
        to_stop = []
        for bot_id, last_t in list(_bot_last_activity.items()):
            if (now - last_t) > BOT_INACTIVE_TIMEOUT:
                to_stop.append(bot_id)
        for bid in to_stop:
            logger.info(f"Stopping inactive bot {bid} (idle {BOT_INACTIVE_TIMEOUT//60}m)")
            await stop_one_bot(bid)
        if to_stop:
            logger.info(f"Inactive monitor: stopped {len(to_stop)}, running: {get_running_count()}/{MAX_CONCURRENT_BOTS}")


async def restart_bots():
    """
    Server restart par: queue mein rakhke pehle MAX_CONCURRENT_BOTS start karo.
    Baaki bots on-demand wake hote hain.
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

    # Active cap tak hi start karo
    to_start = all_bots[:MAX_CONCURRENT_BOTS]
    queued   = total - len(to_start)

    print(f"  📊 Total bots: {total} | Starting: {len(to_start)} | Queued: {queued}")
    print(f"  ℹ️  Queue limit: {MAX_CONCURRENT_BOTS} (change in plugins/clone.py)")

    asyncio.create_task(_start_batch_background(to_start))
    asyncio.create_task(_inactive_monitor())

    logger.info(f"Started queue for {len(to_start)}/{total} bots, {queued} on-demand")


async def _start_batch_background(bots: list):
    await asyncio.sleep(START_DELAY)
    success = failed = 0
    for i in range(0, len(bots), BATCH_SIZE):
        batch = bots[i: i + BATCH_SIZE]
        results = await asyncio.gather(
            *[start_one_bot(b) for b in batch],
            return_exceptions=True
        )
        for r in results:
            if r is True:
                success += 1
            else:
                failed += 1
        if i + BATCH_SIZE < len(bots):
            await asyncio.sleep(BATCH_DELAY)

    print(f"  ✅ {success} bots running | {failed} failed | {get_running_count()} active / {MAX_CONCURRENT_BOTS} max")
