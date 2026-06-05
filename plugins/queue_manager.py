# Smart Queue — Bot ko crash hone se bachata hai
# Ek ek request handle karta hai — kitne bhi bots hon

import asyncio, logging, os, time
from collections import deque

logger = logging.getLogger(__name__)

MAX_CONCURRENT = 30
RAM_PAUSE_MB   = 400
RAM_OK_MB      = 320
CHECK_SEC      = 5
MAX_QUEUE      = 3000

_q       = deque()
_sem     = asyncio.Semaphore(MAX_CONCURRENT)
_paused  = False
_stats   = {"done": 0, "dropped": 0, "errors": 0}


def _ram():
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    except:
        return 0.0


async def _ram_watch():
    global _paused
    while True:
        r = _ram()
        if r > RAM_PAUSE_MB and not _paused:
            _paused = True
            logger.warning(f"Queue PAUSED — RAM {r:.0f}MB")
        elif r < RAM_OK_MB and _paused:
            _paused = False
            logger.info(f"Queue RESUMED — RAM {r:.0f}MB")
        await asyncio.sleep(CHECK_SEC)


async def _worker():
    while True:
        if _paused or not _q:
            await asyncio.sleep(0.1)
            continue
        try:
            coro = _q.popleft()
            async with _sem:
                try:
                    await coro
                    _stats["done"] += 1
                except Exception as e:
                    _stats["errors"] += 1
        except IndexError:
            await asyncio.sleep(0.05)


async def start_queue(workers=3):
    asyncio.create_task(_ram_watch())
    for _ in range(workers):
        asyncio.create_task(_worker())
    logger.info(f"Queue ready — {workers} workers, RAM limit {RAM_PAUSE_MB}MB")


def enqueue(coro) -> bool:
    if len(_q) >= MAX_QUEUE:
        _stats["dropped"] += 1
        return False
    _q.append(coro)
    return True


def status():
    return {"queue": len(_q), "paused": _paused, "ram_mb": round(_ram(),1), **_stats}
