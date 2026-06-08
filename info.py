# ════════════════════════════════════════════════
#   AsBhai Auto Filter Bot — Configuration
#   Developer: @asbhaibsr
#   Support: @aschat_group
# ════════════════════════════════════════════════

import re
from os import environ

# Pattern for ID validation
id_pattern = re.compile(r'^\d+$')

def _bool(val, default=False):
    if val is None: return default
    return val.lower() in ('true', '1', 'yes')

# ── Core Telegram ───────────────────────────────
API_ID    = int(environ.get('API_ID', '0'))
API_HASH  = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')

# ── Admins ──────────────────────────────────────
ADMINS = [int(a) for a in environ.get('ADMINS', '7315805581').split() if id_pattern.search(a)]

AUTH_USERS = [int(a) for a in environ.get('AUTH_USERS', '').split() if id_pattern.search(a)]
AUTH_USERS = list(set(AUTH_USERS + ADMINS))

# ── Database — Sirf 1 MongoDB ───────────────────
DATABASE_URI  = environ.get('DATABASE_URI', '')
DATABASE_NAME = environ.get('DATABASE_NAME', 'asbhaibot')

# Sab ek hi DB use karte hain
FILE_DB_URI     = DATABASE_URI
SEC_FILE_DB_URI = DATABASE_URI
USER_DB_URI     = DATABASE_URI
OTHER_DB_URI    = DATABASE_URI
MULTIPLE_DATABASE = False

# ── Channels ────────────────────────────────────
LOG_CHANNEL          = int(environ.get('LOG_CHANNEL', '0'))
SUPPORT_CHAT         = environ.get('SUPPORT_CHAT', 'aschat_group')
SUPPORT_CHAT_ID      = int(environ.get('SUPPORT_CHAT_ID', '0'))
CHNL_LNK             = environ.get('CHNL_LNK', 'https://t.me/asbhai_bsr')
OWNER_LNK            = environ.get('OWNER_LNK', 'https://t.me/asbhai_bsr')
PUBLIC_FILE_CHANNEL  = environ.get('PUBLIC_FILE_CHANNEL', '')

# ── Clone System ────────────────────────────────
CLONE_MODE            = _bool(environ.get('CLONE_MODE'), default=True)
CLONE_DATABASE_URI    = environ.get('CLONE_DATABASE_URI', DATABASE_URI)

# ── Search & Filter ─────────────────────────────
MAX_B_TN          = int(environ.get('MAX_B_TN', '9'))
MAX_BTN           = int(environ.get('MAX_BTN', '4'))
COLLECTION_NAME   = environ.get('COLLECTION_NAME', 'Telegram_files')
USE_CAPTION_FILTER = _bool(environ.get('USE_CAPTION_FILTER'), default=True)

# ── Verify / Shortlink ──────────────────────────
VERIFY                  = _bool(environ.get('VERIFY'), default=False)
VERIFY_SHORTLINK_URL    = environ.get('VERIFY_SHORTLINK_URL', '')
VERIFY_SHORTLINK_API    = environ.get('VERIFY_SHORTLINK_API', '')
VERIFY_SECOND_SHORTNER  = _bool(environ.get('VERIFY_SECOND_SHORTNER'), default=False)
VERIFY_SND_SHORTLINK_URL = environ.get('VERIFY_SND_SHORTLINK_URL', '')
VERIFY_SND_SHORTLINK_API = environ.get('VERIFY_SND_SHORTLINK_API', '')
VERIFY_TUTORIAL          = environ.get('VERIFY_TUTORIAL', 'https://t.me/asbhai_bsr/671')
IS_TUTORIAL              = _bool(environ.get('IS_TUTORIAL'), default=False)
BLOGGER_VERIFY           = False  # Not supported

# ── Premium ─────────────────────────────────────
PREMIUM_AND_REFERAL_MODE = _bool(environ.get('PREMIUM_AND_REFERAL_MODE'), default=True)
PAYMENT_QR               = environ.get('PAYMENT_QR', '')

# ── Auto Delete ─────────────────────────────────
AUTO_DELETE       = _bool(environ.get('AUTO_DELETE'), default=False)
AUTO_DELETE_TIME  = int(environ.get('AUTO_DELETE_TIME', '300'))

# ── Bot Settings ────────────────────────────────
PM_SEARCH             = _bool(environ.get('PM_SEARCH'), default=True)
INDEX_EXTENSIONS      = environ.get('INDEX_EXTENSIONS', '').split()
SHORTLINK_URL         = environ.get('SHORTLINK_URL', '')
SHORTLINK_API         = environ.get('SHORTLINK_API', '')
TUTORIAL              = environ.get('TUTORIAL', 'https://t.me/asbhai_bsr/671')

# ── Subscription Pricing ────────────────────────
FREE_TRIAL_DAYS = int(environ.get('FREE_TRIAL_DAYS', '30'))

# ── Search years ────────────────────────────────
YEARS = [
    "1990","1991","1992","1993","1994","1995","1996","1997","1998","1999",
    "2000","2001","2002","2003","2004","2005","2006","2007","2008","2009",
    "2010","2011","2012","2013","2014","2015","2016","2017","2018","2019",
    "2020","2021","2022","2023","2024","2025","2026",
]

# ── Anti Spam ────────────────────────────────────
PM_SEARCH_DAILY_LIMIT = int(environ.get('PM_SEARCH_DAILY_LIMIT', '15'))
SPAM_MSG_LIMIT        = int(environ.get('SPAM_MSG_LIMIT', '5'))
SPAM_TIME_WINDOW      = int(environ.get('SPAM_TIME_WINDOW', '5'))
SPAM_BLOCK_TIME       = int(environ.get('SPAM_BLOCK_TIME', '60'))

# ── Maintenance ──────────────────────────────────
MAINTENANCE_MODE = _bool(environ.get('MAINTENANCE_MODE'), default=False)

# ── Ads ──────────────────────────────────────────
IS_STREAM      = _bool(environ.get('IS_STREAM'), default=False)
ON_HEROKU      = True if 'DYNO' in environ else False

# ── Privacy ──────────────────────────────────────
BOT_NAME     = environ.get('BOT_NAME', 'AsBhai Filter Bot')
BOT_USERNAME = environ.get('BOT_USERNAME', '')

# ── Filter Bot Settings (Missing vars added) ────
CUSTOM_FILE_CAPTION = environ.get('CUSTOM_FILE_CAPTION', '')
BATCH_FILE_CAPTION  = environ.get('BATCH_FILE_CAPTION', '')
IMDB                = _bool(environ.get('IMDB'), default=True)
IMDB_TEMPLATE       = environ.get('IMDB_TEMPLATE', '<b>{title}</b>\n\n⭐ Rating: {rating}\n📅 Year: {year}\n🎭 Genres: {genres}')
MELCOW_NEW_USERS    = _bool(environ.get('MELCOW_NEW_USERS'), default=True)
BUTTON_MODE         = _bool(environ.get('BUTTON_MODE'), default=False)
SPELL_CHECK_REPLY   = _bool(environ.get('SPELL_CHECK_REPLY'), default=True)
PROTECT_CONTENT     = _bool(environ.get('PROTECT_CONTENT'), default=False)
AUTO_FFILTER        = _bool(environ.get('AUTO_FFILTER'), default=True)
SHORTLINK_MODE      = _bool(environ.get('SHORTLINK_MODE'), default=False)

# ── Channels & Groups ────────────────────────────
AUTH_CHANNEL   = environ.get('AUTH_CHANNEL', '')
AUTH_CHANNEL   = int(AUTH_CHANNEL) if AUTH_CHANNEL and id_pattern.search(AUTH_CHANNEL) else ''
CHANNELS       = [int(c) for c in environ.get('CHANNELS', '').split() if id_pattern.search(c)]
REQST_CHANNEL  = environ.get('REQST_CHANNEL', '')
REQST_CHANNEL  = int(REQST_CHANNEL) if REQST_CHANNEL and id_pattern.search(REQST_CHANNEL) else ''
GRP_LNK        = environ.get('GRP_LNK', 'https://t.me/aschat_group')

# ── Streaming ────────────────────────────────────
STREAM_MODE    = _bool(environ.get('STREAM_MODE'), default=False)
URL            = environ.get('URL', '')  # Base URL for stream links e.g. https://yourserver.com/

# ── Cache ────────────────────────────────────────
CACHE_TIME     = int(environ.get('CACHE_TIME', '300'))

# ── Reactions ────────────────────────────────────
REACTIONS      = environ.get('REACTIONS', '❤️ 🔥 🎉 👍 😍').split()

# ── Pics (welcome/force-sub images) ─────────────
_pics_raw = environ.get('PICS', '')
PICS           = [p.strip() for p in _pics_raw.split(',') if p.strip()]

# ── Join Request / Force Sub ─────────────────────
REQUEST_TO_JOIN_MODE = _bool(environ.get('REQUEST_TO_JOIN_MODE'), default=False)
TRY_AGAIN_BTN        = _bool(environ.get('TRY_AGAIN_BTN'), default=True)

# ── Referral & Premium ───────────────────────────
REFERAL_COUNT         = int(environ.get('REFERAL_COUNT', '5'))
REFERAL_PREMEIUM_TIME = int(environ.get('REFERAL_PREMEIUM_TIME', '30'))
PAYMENT_TEXT          = environ.get('PAYMENT_TEXT', 'Contact admin for premium access.')

# ── File Store / Gen Link ────────────────────────
FILE_STORE_CHANNEL = [int(c) for c in environ.get('FILE_STORE_CHANNEL', '').split() if id_pattern.search(c)]
PUBLIC_FILE_STORE  = _bool(environ.get('PUBLIC_FILE_STORE'), default=False)

# ── Auto Delete Channels ─────────────────────────
DELETE_CHANNELS    = [int(c) for c in environ.get('DELETE_CHANNELS', '').split() if id_pattern.search(c)]

# ── Index Channel ────────────────────────────────
INDEX_REQ_CHANNEL  = environ.get('INDEX_REQ_CHANNEL', '')
INDEX_REQ_CHANNEL  = int(INDEX_REQ_CHANNEL) if INDEX_REQ_CHANNEL and id_pattern.search(INDEX_REQ_CHANNEL) else LOG_CHANNEL

# ── Blogger / Google Sheet (optional) ───────────
GOOGLE_SHEET_CSV_URL = environ.get('GOOGLE_SHEET_CSV_URL', '')
BLOGGER_BASE_URL     = environ.get('BLOGGER_BASE_URL', '')

# ── Web Server ──────────────────────────────────
PORT = int(environ.get('PORT', '8080'))

# ── Bot Session & Client Settings ──────────────
SESSION         = environ.get('SESSION', 'AsBhaiBot')
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL   = int(environ.get('PING_INTERVAL', '800'))

# ── Auto Approve ─────────────────────────────── 
AUTO_APPROVE_MODE = _bool(environ.get('AUTO_APPROVE_MODE'), default=False)

# ── AI Spell Check & No Results Message ─────────
AI_SPELL_CHECK = _bool(environ.get('AI_SPELL_CHECK'), default=False)
NO_RESULTS_MSG = environ.get('NO_RESULTS_MSG', '')

# ── Alert Messages ───────────────────────────────
MSG_ALRT = environ.get('MSG_ALRT', '⚠️ This button is not for you!')

# ══════════════════════════════════════════════════
#   SESSION STRING — Userbot for channel search
# ══════════════════════════════════════════════════
USER_SESSION_STRING = environ.get('USER_SESSION_STRING', '')   # User account session
MAIN_MOVIE_CHANNEL  = environ.get('MAIN_MOVIE_CHANNEL', '')    # Main movie channel ID
MAIN_MOVIE_CHANNEL  = int(MAIN_MOVIE_CHANNEL) if MAIN_MOVIE_CHANNEL and id_pattern.search(MAIN_MOVIE_CHANNEL) else 0
SEARCH_CACHE_TTL    = int(environ.get('SEARCH_CACHE_TTL', '300'))   # 5 min cache (seconds)
COPYRIGHT_TEXT      = environ.get('COPYRIGHT_TEXT', '🔒 Ye service sirf educational purpose ke liye hai. Hamara kisi copyrighted content se koi sambandh nahi hai.')
