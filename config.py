import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8991881315
DB_PATH = os.getenv("DB_PATH", "users.db")

# ---------- Official Links ----------
WEBSITE_URL = "http://www.nollywoodspotlight.org"
BOT_USERNAME = "Nollywoodsspotlightbot"
BOT_LINK = f"https://t.me/{BOT_USERNAME}"

TELEGRAM_CHANNEL = "https://t.me/nollywoodspotlightblog1"
TELEGRAM_GROUP   = "http://t.me/nollywoodspotlightblog"

# ---------- Social links (disabled for now) ----------
INSTAGRAM        = ""
TWITTER          = ""
FACEBOOK         = ""
YOUTUBE          = ""
TIKTOK           = ""
WHATSAPP_CHANNEL = ""
