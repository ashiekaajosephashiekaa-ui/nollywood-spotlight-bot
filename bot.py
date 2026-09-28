import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import (
    BOT_TOKEN, ADMIN_ID, WEBSITE_URL, BOT_USERNAME, BOT_LINK,
    TELEGRAM_CHANNEL, TELEGRAM_GROUP, INSTAGRAM, TWITTER,
    FACEBOOK, YOUTUBE, TIKTOK, WHATSAPP_CHANNEL,
)
import database as db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- Content ----------
TRIVIA = [
    {"question": "Which Nollywood actor is known as 'The King of Nollywood'?",
     "options": ["Ramsey Nouah", "Genevieve Nnaji", "Pete Edochie", "Omotola Jalade"],
     "answer": "Pete Edochie"},
    {"question": "What year was the Nigerian film industry dubbed 'Nollywood'?",
     "options": ["1992", "1998", "2000", "2005"],
     "answer": "1992"},
    {"question": "Which Nollywood movie was the first to be shot on a digital camera?",
     "options": ["Living in Bondage", "Glamour Girls", "Domitilla", "Rattlesnake"],
     "answer": "Living in Bondage"},
    {"question": "Who directed the 2014 thriller 'October 1'?",
     "options": ["Kunle Afolayan", "Tunde Kelani", "Izu Ojukwu", "Niyi Akinmolayan"],
     "answer": "Kunle Afolayan"},
    {"question": "Which Nollywood actress starred in 'Lionheart'?",
     "options": ["Genevieve Nnaji", "Omotola Jalade", "Rita Dominic", "Ini Edo"],
     "answer": "Genevieve Nnaji"},
]

MOVIES = [
    {"title": "Living in Bondage", "year": 1992, "genre": "Drama"},
    {"title": "Glamour Girls", "year": 1994, "genre": "Drama"},
    {"title": "Domitilla", "year": 1996, "genre": "Drama"},
    {"title": "The Figurine", "year": 2009, "genre": "Thriller"},
    {"title": "October 1", "year": 2014, "genre": "Thriller"},
    {"title": "The Wedding Party", "year": 2016, "genre": "Comedy"},
    {"title": "King of Boys", "year": 2018, "genre": "Crime"},
    {"title": "Lionheart", "year": 2018, "genre": "Drama"},
    {"title": "Living in Bondage: Breaking Free", "year": 2019, "genre": "Thriller"},
    {"title": "Citation", "year": 2020, "genre": "Drama"},
]

# ---------- Menu Builders ----------
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌐 Visit Nollywood Spotlight", url=WEBSITE_URL)],
        [
            InlineKeyboardButton("📊 User Stats", callback_data="stats"),
            InlineKeyboardButton("🌍 Follow Us", callback_data="follow"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
        [
            InlineKeyboardButton("🔗 My Referral Link", callback_data="referral"),
            InlineKeyboardButton(
                "📢 Share Bot",
                url=f"https://t.me/share/url?url={BOT_LINK}&text=Check out Nollywood Spotlight Bot!"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def follow_menu():
    rows = []
    if WEBSITE_URL:
        rows.append([InlineKeyboardButton("🌐 Website", url=WEBSITE_URL)])
    tg_row = []
    if TELEGRAM_CHANNEL:
        tg_row.append(InlineKeyboardButton("📺 Telegram Channel", url=TELEGRAM_CHANNEL))
    if TELEGRAM_GROUP:
        tg_row.append(InlineKeyboardButton("👥 Community Group", url=TELEGRAM_GROUP))
    if tg_row:
        rows.append(tg_row)
    social = []
    if INSTAGRAM: social.append(InlineKeyboardButton("📸 Instagram", url=INSTAGRAM))
    if TWITTER:   social.append(InlineKeyboardButton("🐦 X (Twitter)", url=TWITTER))
    if FACEBOOK:  social.append(InlineKeyboardButton("📘 Facebook", url=FACEBOOK))
    if social:
        rows.append(social)
    media = []
    if YOUTUBE:  media.append(InlineKeyboardButton("▶️ YouTube", url=YOUTUBE))
    if TIKTOK:   media.append(InlineKeyboardButton("🎵 TikTok", url=TIKTOK))
    if WHATSAPP_CHANNEL: media.append(InlineKeyboardButton("💬 WhatsApp", url=WHATSAPP_CHANNEL))
    if media:
        rows.append(media)
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    referrer_id = None
    if args and args[0].startswith("ref_"):
        try:
            referrer_id = int(args[0][4:])
        except ValueError:
            pass

    await db.add_user(user.id, user.username, user.first_name, referrer_id)
    total_users = await db.get_total_users()

    welcome_text = (
        f"🎬 *Welcome to Nollywood Spotlight Bot!*\n\n"
        f"Discover the latest Nollywood movies, trivia, and updates.\n\n"
        f"👥 *Total Users:* `{total_users}`\n\n"
        f"Use the buttons below to explore 👇"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu(),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    total = await db.get_total_users()
    text = (
        f"📈 *Bot Statistics*\n\n"
        f"👥 Total Users: `{total}`\n"
        f"🕐 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    await q.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        )
    )

async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lines = [
        "🎬 *Nollywood Spotlight Bot*",
        "",
        "Your gateway to the Nigerian film industry.",
        "",
        f"🌐 Website: {WEBSITE_URL}",
        "",
        "*Commands:*",
        "/start — Main menu",
        "/help — Show help",
        "/trivia — Play Nollywood trivia",
        "/movie — Random movie suggestion",
        "/stats — Bot statistics",
        "/about — About this bot",
    ]
    await q.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        )
    )

async def follow_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "🌍 *Follow Nollywood Spotlight*\n\n"
        "Stay connected across all our platforms:",
        parse_mode="Markdown",
        reply_markup=follow_menu(),
        disable_web_page_preview=True,
    )

async def referral_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    ref_count = await db.get_referral_count(uid)
    ref_link = f"{BOT_LINK}?start=ref_{uid}"
    text = (
        f"🔗 *Your Referral Link*\n\n"
        f"`{ref_link}`\n\n"
        f"👥 Users referred: `{ref_count}`\n\n"
        f"Share this link and grow the community!"
    )
    await q.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        )
    )

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    total = await db.get_total_users()
    await q.edit_message_text(
        f"🎬 *Welcome back!*\n\n👥 *Total Users:* `{total}`",
        parse_mode="Markdown",
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Available Commands*\n\n"
        "/start — Main menu\n"
        "/help — This help message\n"
        "/trivia — Play Nollywood trivia\n"
        "/movie — Random Nollywood movie\n"
        "/stats — Bot statistics\n"
        "/about — About this bot",
        parse_mode="Markdown"
    )

async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_data = random.choice(TRIVIA)
    keyboard = [[InlineKeyboardButton(o, callback_data=f"trivia_{o}")] for o in q_data["options"]]
    await update.message.reply_text(
        f"🎬 *Nollywood Trivia*\n\n{q_data['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    context.user_data['trivia_answer'] = q_data["answer"]

async def trivia_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    selected = q.data.split("_", 1)[1]
    correct = context.user_data.get('trivia_answer')
    if not correct:
        await q.edit_message_text("❌ This trivia has expired. Use /trivia to start a new one.")
        return
    if selected == correct:
        result = "✅ *Correct!*"
    else:
        result = f"❌ *Wrong!* The correct answer was: *{correct}*"
    await q.edit_message_text(f"{result}\n\nUse /trivia for another question!", parse_mode="Markdown")
    context.user_data.pop('trivia_answer', None)

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = random.choice(MOVIES)
    await update.message.reply_text(
        f"🎥 *Random Nollywood Movie*\n\n"
        f"*Title:* {m['title']}\n"
        f"*Year:* {m['year']}\n"
        f"*Genre:* {m['genre']}\n\n"
        f"Want to know more? Visit our website!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🌐 Visit Nollywood Spotlight", url=WEBSITE_URL)]]
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = await db.get_total_users()
    await update.message.reply_text(f"👥 *Total Users:* `{total}`", parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎬 *Nollywood Spotlight Bot*\n\n"
        f"Your gateway to the Nigerian film industry.\n\n"
        f"🌐 Website: {WEBSITE_URL}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

# ---------- Admin ----------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    users = await db.get_all_users()
    success = failed = 0
    await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=message, parse_mode="Markdown")
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Failed to send to {uid}: {e}")
    await update.message.reply_text(f"✅ Done.\nSuccess: {success}\nFailed: {failed}")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    total = await db.get_total_users()
    await update.message.reply_text(f"📊 *Admin Stats*\n\nTotal Users: `{total}`", parse_mode="Markdown")

# ---------- Post Init ----------
async def post_init(application: Application):
    await db.init_db()
    await application.bot.set_my_commands([
        BotCommand("start", "Main menu"),
        BotCommand("help", "Show help"),
        BotCommand("trivia", "Play Nollywood trivia"),
        BotCommand("movie", "Random movie suggestion"),
        BotCommand("stats", "Bot statistics"),
        BotCommand("about", "About this bot"),
    ])

# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("trivia", trivia_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("adminstats", admin_stats))

    app.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(about_callback, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(follow_callback, pattern="^follow$"))
    app.add_handler(CallbackQueryHandler(referral_callback, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(trivia_callback, pattern="^trivia_"))

    app.run_polling()

if __name__ == "__main__":
    main()
