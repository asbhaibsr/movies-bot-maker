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
SUPPORT_CHAT_ID      = int(environ.get('SUPPORT_CHAT_ID', '-1002085088955'))
CHNL_LNK             = environ.get('CHNL_LNK', 'https://t.me/asbhai_bsr')
OWNER_LNK            = environ.get('OWNER_LNK', 'https://t.me/asbhai_bsr')
PUBLIC_FILE_CHANNEL  = environ.get('PUBLIC_FILE_CHANNEL', '-1002797023499')

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
