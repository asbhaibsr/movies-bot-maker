# ════════════════════════════════════════════════════════════
#   UserBot — Session String Search + Cache
#   Main channel search karo bina MongoDB ke
#   Cache: 5 minute (300 sec)
# ════════════════════════════════════════════════════════════
import time, logging, asyncio
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# In-memory cache: {query_lower: {results:[...], ts: timestamp}}
_cache: Dict[str, dict] = {}
userbot = None   # Pyrogram Client (user account)


async def init_userbot():
    """Bot startup pe userbot initialize karo"""
    global userbot
    try:
        from info import USER_SESSION_STRING, API_ID, API_HASH
        if not USER_SESSION_STRING:
            logger.info("USER_SESSION_STRING not set — userbot disabled, using MongoDB")
            return
        from pyrogram import Client
        userbot = Client(
            "userbot_session",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=USER_SESSION_STRING,
            no_updates=True,    # We only SEARCH, don't handle updates
        )
        await userbot.start()
        me = await userbot.get_me()
        logger.info(f"✅ Userbot started: {me.first_name} (@{me.username})")
    except Exception as e:
        logger.error(f"❌ Userbot init failed: {e}")
        userbot = None


async def stop_userbot():
    global userbot
    if userbot:
        try:
            await userbot.stop()
        except:
            pass


def _cache_get(query: str) -> Optional[List[dict]]:
    """Cache se result lo agar fresh hai"""
    from info import SEARCH_CACHE_TTL
    key = query.lower().strip()
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry['ts'] < SEARCH_CACHE_TTL:
            logger.debug(f"Cache hit: {query}")
            return entry['results']
        else:
            del _cache[key]
    return None


def _cache_set(query: str, results: List[dict]):
    """Result cache mein save karo"""
    key = query.lower().strip()
    _cache[key] = {'results': results, 'ts': time.time()}
    # Cache size limit (max 500 entries)
    if len(_cache) > 500:
        oldest = sorted(_cache.items(), key=lambda x: x[1]['ts'])[:100]
        for k, _ in oldest:
            del _cache[k]


def cache_invalidate(query: str = None):
    """Cache clear karo (specific query ya sabhi)"""
    if query:
        _cache.pop(query.lower().strip(), None)
    else:
        _cache.clear()


async def search_in_channel(query: str, limit: int = 20) -> List[dict]:
    """
    Main movie channel mein movie search karo userbot se.
    Returns: list of {file_id, file_name, file_size, file_type, caption}
    """
    global userbot

    # 1. Cache check
    cached = _cache_get(query)
    if cached is not None:
        return cached[:limit]

    # 2. Userbot available nahi? Empty return (MongoDB fallback hoga)
    if not userbot:
        return []

    from info import MAIN_MOVIE_CHANNEL
    if not MAIN_MOVIE_CHANNEL:
        return []

    results = []
    try:
        # Channel messages search karo
        async for msg in userbot.search_messages(
            chat_id=MAIN_MOVIE_CHANNEL,
            query=query,
            limit=limit * 2    # Extra fetch for filtering
        ):
            media = msg.document or msg.video or msg.audio
            if not media:
                continue

            file_name = (
                getattr(media, 'file_name', None)
                or (msg.caption or '')[:100]
                or f"File_{msg.id}"
            )

            results.append({
                'file_id':   media.file_id,
                'file_name': file_name,
                'file_size': getattr(media, 'file_size', 0) or 0,
                'file_type': 'video' if msg.video else ('audio' if msg.audio else 'document'),
                'caption':   msg.caption or '',
                'message_id': msg.id,
            })

            if len(results) >= limit:
                break

        # Cache mein save karo
        _cache_set(query, results)
        logger.info(f"Userbot search '{query}': {len(results)} results")

    except Exception as e:
        logger.error(f"Userbot search error: {e}")

    return results


async def add_to_channel(file_id: str, caption: str = "") -> Optional[dict]:
    """
    File ko main movie channel mein add karo (main bot ke through).
    Returns: saved file info or None
    """
    global userbot
    try:
        from info import MAIN_MOVIE_CHANNEL
        from utils import temp
        if not MAIN_MOVIE_CHANNEL or not temp.BOT:
            return None

        # Main bot use karke channel mein send karo
        msg = await temp.BOT.send_cached_media(
            chat_id=MAIN_MOVIE_CHANNEL,
            file_id=file_id,
            caption=caption or "📁 Added via Clone Bot"
        )
        media = msg.document or msg.video or msg.audio
        if not media:
            return None

        # Cache invalidate karo (nayi file add hui)
        _cache.clear()

        return {
            'file_id':    media.file_id,
            'file_name':  getattr(media, 'file_name', '') or caption,
            'file_size':  media.file_size or 0,
            'message_id': msg.id,
        }
    except Exception as e:
        logger.error(f"add_to_channel error: {e}")
        return None


def is_userbot_active() -> bool:
    return userbot is not None
