# ════════════════════════════════════════════════════════════
#   Clone Bot Custom Filters
#   clone_admin → Is user admin of THIS specific clone bot?
#   Replaces filters.user(ADMINS) in ALL clone bot files
# ════════════════════════════════════════════════════════════
from pyrogram import filters
from database.users_chats_db import db
from info import ADMINS
import logging

logger = logging.getLogger(__name__)


async def _clone_admin_check(flt, client, update):
    """
    User admin hai agar:
    1. Main bot ke ADMINS list mein hai
    2. Ya is clone bot ka registered owner hai
    """
    # Message ya callback query dono support karo
    if hasattr(update, 'from_user') and update.from_user:
        user_id = update.from_user.id
    else:
        return False

    # Main bot admin?
    if user_id in ADMINS:
        return True

    # Clone bot owner?
    try:
        me = await client.get_me()
        bd = await db.get_bot(me.id)
        return user_id == bd.get("user_id")
    except Exception as e:
        logger.warning(f"clone_admin_check error: {e}")
        return False


async def _clone_group_admin_check(flt, client, message):
    """Group mein admin check - Telegram group admin ya clone owner"""
    if not message.from_user:
        return False
    user_id = message.from_user.id

    # Main admin always pass
    if user_id in ADMINS:
        return True

    # Clone owner always pass
    try:
        me = await client.get_me()
        bd = await db.get_bot(me.id)
        if user_id == bd.get("user_id"):
            return True
    except:
        pass

    # Group admin?
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False


# ─── Filters to use in @Client.on_message decorators ────────
# Use: filters.command("cmd") & clone_admin
clone_admin = filters.create(_clone_admin_check)

# Use in group management: filters.command("cmd") & clone_or_group_admin
clone_or_group_admin = filters.create(_clone_group_admin_check)
