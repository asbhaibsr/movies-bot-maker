# Clone Bot Subscription Database
# Handles free trial + paid subscription per clone bot

import datetime
import motor.motor_asyncio
from info import DATABASE_URI, DATABASE_NAME

_client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
_db     = _client[DATABASE_NAME]
sub_col = _db["clone_subscriptions"]

# Pricing
PLANS = {
    1: {"months": 1, "price": 150,  "label": "1 Month  — ₹150"},
    2: {"months": 2, "price": 300,  "label": "2 Months — ₹300"},
    3: {"months": 3, "price": 450,  "label": "3 Months — ₹450"},
    4: {"months": 4, "price": 600,  "label": "4 Months — ₹600"},
    5: {"months": 5, "price": 700,  "label": "5 Months — ₹700"},
}

FREE_TRIAL_DAYS = 30   # 1 month free


async def create_subscription(bot_id: int, owner_id: int, bot_username: str):
    """Naya clone banane pe free trial start karo"""
    now    = datetime.datetime.now()
    expiry = now + datetime.timedelta(days=FREE_TRIAL_DAYS)
    doc = {
        "bot_id":       int(bot_id),
        "owner_id":     int(owner_id),
        "bot_username": bot_username,
        "created_at":   now,
        "expiry":       expiry,
        "is_free":      True,
        "is_active":    True,
        "plan_history": [],
    }
    await sub_col.update_one({"bot_id": int(bot_id)}, {"$set": doc}, upsert=True)
    return doc


async def get_subscription(bot_id: int):
    """Bot ki subscription details lo"""
    return await sub_col.find_one({"bot_id": int(bot_id)})


async def is_active(bot_id: int) -> bool:
    """Check karo bot ka subscription active hai ya nahi"""
    doc = await sub_col.find_one({"bot_id": int(bot_id)})
    if not doc:
        return False
    if not doc.get("is_active"):
        return False
    expiry = doc.get("expiry")
    if not expiry:
        return False
    return datetime.datetime.now() < expiry


async def extend_subscription(bot_id: int, months: int, admin_id: int):
    """Subscription extend karo (admin confirm karne ke baad)"""
    doc = await sub_col.find_one({"bot_id": int(bot_id)})
    if not doc:
        return False
    now    = datetime.datetime.now()
    expiry = doc.get("expiry", now)
    # Agar expired hai to aaj se shuru karo
    if expiry < now:
        expiry = now
    new_expiry = expiry + datetime.timedelta(days=30 * months)
    plan_record = {
        "extended_at":  now,
        "months":       months,
        "new_expiry":   new_expiry,
        "confirmed_by": admin_id,
    }
    await sub_col.update_one(
        {"bot_id": int(bot_id)},
        {
            "$set":  {"expiry": new_expiry, "is_active": True, "is_free": False},
            "$push": {"plan_history": plan_record},
        }
    )
    return new_expiry


async def deactivate_subscription(bot_id: int):
    await sub_col.update_one({"bot_id": int(bot_id)}, {"$set": {"is_active": False}})


async def get_all_subscriptions():
    """Saare subscriptions list"""
    result = []
    async for doc in sub_col.find({}):
        result.append(doc)
    return result


async def get_expiring_soon_subs(days: int = 3):
    """Next N din mein expire hone wale bots"""
    now  = datetime.datetime.now()
    soon = now + datetime.timedelta(days=days)
    result = []
    async for doc in sub_col.find({
        "is_active": True,
        "expiry":    {"$gt": now, "$lte": soon}
    }):
        result.append(doc)
    return result


async def get_owner_bots(owner_id: int):
    """Ek user ke saare clone bots"""
    result = []
    async for doc in sub_col.find({"owner_id": int(owner_id)}):
        result.append(doc)
    return result


async def days_remaining(bot_id: int) -> int:
    doc = await sub_col.find_one({"bot_id": int(bot_id)})
    if not doc:
        return 0
    expiry = doc.get("expiry")
    if not expiry:
        return 0
    remaining = (expiry - datetime.datetime.now()).days
    return max(0, remaining)
