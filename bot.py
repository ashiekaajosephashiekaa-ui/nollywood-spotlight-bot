import logging
import random
import threading
import os
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

# ============================================================
# CONTENT
# ============================================================

# ---- Recent Nollywood movies (2025-2026) — used 80% of the time ----
RECENT_MOVIES = [
    # ===== 2025 BOX OFFICE HITS =====
    {"title": "Behind The Scenes", "year": 2025, "genre": "Drama", "star": "Funke Akindele"},
    {"title": "Gingerrr", "year": 2025, "genre": "Comedy / Drama", "star": "Toyin Abraham"},
    {"title": "Oversabi Aunty", "year": 2025, "genre": "Family / Comedy", "star": "Toyin Abraham"},
    {"title": "Ori: The Rebirth", "year": 2025, "genre": "Epic / Fantasy", "star": "Muyiwa Ademola"},
    {"title": "Reel Love", "year": 2025, "genre": "Romance / Drama", "star": "Timini Egbuson"},
    {"title": "Labake Olododo", "year": 2025, "genre": "Period Drama", "star": "Iyabo Ojo"},
    {"title": "Owambe Thieves", "year": 2025, "genre": "Comedy / Crime", "star": "Odunlade Adekola"},
    {"title": "The Herd", "year": 2025, "genre": "Thriller / Drama", "star": "Daniel Etim Effiong"},
    {"title": "A Lagos Love Story", "year": 2025, "genre": "Romance / Drama", "star": "Jemima Osunde"},
    {"title": "Unclaimed", "year": 2025, "genre": "Psychological Thriller", "star": "Kunle Remi"},
    {"title": "Níní", "year": 2025, "genre": "Emotional Thriller", "star": "Mariah Ugbashi"},
    {"title": "To Kill a Monkey", "year": 2025, "genre": "Crime / Thriller", "star": "Kemi Adetiba"},
    {"title": "A Very Dirty December", "year": 2025, "genre": "Comedy / Drama", "star": "Ini Edo"},
    {"title": "Lisabi: A Legend Is Born", "year": 2025, "genre": "Historical Epic", "star": "Lateef Adedimeji"},
    {"title": "Warlord: Olori Ogun", "year": 2025, "genre": "Historical Epic", "star": "Odunlade Adekola"},

    # ===== 2026 RELEASES =====
    {"title": "The Four: No One Fights Alone", "year": 2026, "genre": "Drama", "star": "Funke Akindele"},
    {"title": "Black Market", "year": 2026, "genre": "Crime / Thriller", "star": "Fatimah Binta Gimsay"},
    {"title": "IYALOJA", "year": 2026, "genre": "Thriller", "star": "Kehinde Bankole"},
    {"title": "Remi & Nneoma", "year": 2026, "genre": "Drama", "star": "Liz Benson"},
    {"title": "EVI", "year": 2026, "genre": "Musical / Drama", "star": "Osas Okonyon"},
]

# ---- Classic Nollywood — used 20% of the time ----
CLASSIC_MOVIES = [
    {"title": "Living in Bondage", "year": 1992, "genre": "Drama", "star": "Kenneth Okonkwo"},
    {"title": "Glamour Girls", "year": 1994, "genre": "Drama", "star": "Eucharia Anunobi"},
    {"title": "The Figurine", "year": 2009, "genre": "Thriller", "star": "Ramsey Nouah"},
    {"title": "October 1", "year": 2014, "genre": "Thriller", "star": "Sadiq Daba"},
    {"title": "King of Boys", "year": 2018, "genre": "Crime / Drama", "star": "Sola Sobowale"},
    {"title": "Lionheart", "year": 2018, "genre": "Drama", "star": "Genevieve Nnaji"},
]

def pick_movie():
    """Returns a recent movie 80% of the time, classic 20%."""
    if random.random() < 0.8:
        return random.choice(RECENT_MOVIES), "🆕 *Recent Release*"
    return random.choice(CLASSIC_MOVIES), "🏆 *Nollywood Classic*"

# ---- Trivia — fun & varied ----
TRIVIA = [
    {"question": "Which Nollywood legend is famously called 'The King of Nollywood'? 👑",
     "options": ["Ramsey Nouah", "Pete Edochie", "Chiwetalu Agu", "Richard Mofe-Damijo"],
     "answer": "Pete Edochie"},

    {"question": "What year was the Nigerian film industry nicknamed 'Nollywood'? 🎬",
     "options": ["1992", "1998", "2000", "2005"],
     "answer": "1992"},

    {"question": "Which 2023 movie broke Nollywood box office records with over ₦1 billion? 💰",
     "options": ["The Black Book", "A Tribe Called Judah", "Gangs of Lagos", "Jagun Jagun"],
     "answer": "A Tribe Called Judah"},

    {"question": "Which Nollywood actress starred in and directed 'Lionheart'? 🦁",
     "options": ["Genevieve Nnaji", "Omotola Jalade", "Rita Dominic", "Ini Edo"],
     "answer": "Genevieve Nnaji"},

    {"question": "Which 2023 epic made waves for its powerful Yoruba cultural storytelling? ⚔️",
     "options": ["Anikulapo", "Jagun Jagun", "House of Ga'a", "Lisabi"],
     "answer": "Jagun Jagun"},

    {"question": "Who directed the thriller 'October 1' and 'Ijogbon'? 🎥",
     "options": ["Kunle Afolayan", "Tunde Kelani", "Niyi Akinmolayan", "Izu Ojukwu"],
     "answer": "Kunle Afolayan"},

    {"question": "Which 2022 Nollywood film is set in the oil-rich Niger Delta and tackles crude oil theft? 🛢️",
     "options": ["Brotherhood", "Shanty Town", "Anikulapo", "Adire"],
     "answer": "Brotherhood"},

    {"question": "Which Nollywood actress is nicknamed 'Toyin Tomato' for her iconic role? 🍅",
     "options": ["Funke Akindele", "Toyin Abraham", "Mercy Johnson", "Iyabo Ojo"],
     "answer": "Toyin Abraham"},

    {"question": "Which 2024 historical epic tells the story of a legendary Yoruba warrior? 🛡️",
     "options": ["Lisabi: The Uprising", "House of Ga'a", "Beast of Two Worlds", "Kaka"],
     "answer": "Lisabi: The Uprising"},

    {"question": "Which Nollywood comedy queen produced 'Battle on Buka Street' and 'A Tribe Called Judah'? 🎭",
     "options": ["Funke Akindele", "Toyin Abraham", "Mercy Johnson", "Nkem Owoh"],
     "answer": "Funke Akindele"},

    {"question": "Which actor is famous for the catchphrase 'I go wound o!'? 🤕",
     "options": ["Chiwetalu Agu", "Nkem Owoh", "John Okafor (Mr Ibu)", "Charles Inojie"],
     "answer": "Chiwetalu Agu"},

    {"question": "Which late Nollywood comedian was beloved as 'Mr Ibu'? 🎤",
     "options": ["John Okafor", "Baba Suwe", "Sam Loco Efe", "Sanyeri"],
     "answer": "John Okafor"},

    {"question": "The 2023 film 'Mami Wata' is shot in which language? 🌊",
     "options": ["Yoruba", "Igbo", "Pidgin English", "Hausa"],
     "answer": "Pidgin English"},

    {"question": "Which streaming giant produced the 2023 Nigerian action film 'The Black Book'? 🎞️",
     "options": ["Netflix", "Amazon Prime", "Disney+", "Apple TV+"],
     "answer": "Netflix"},
]

# ============================================================
# MENUS — Gold/yellow emoji accents throughout
# ============================================================

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌟 Visit Nollywood Spotlight Website", url=WEBSITE_URL)],
        [
            InlineKeyboardButton("📺 Join Channel", url=TELEGRAM_CHANNEL),
            InlineKeyboardButton("👥 Join Group", url=TELEGRAM_GROUP),
        ],
        [
            InlineKeyboardButton("🎬 Random Movie", callback_data="movie"),
            InlineKeyboardButton("🎯 Play Trivia", callback_data="trivia"),
        ],
        [
            InlineKeyboardButton("📊 Live Stats", callback_data="stats"),
            InlineKeyboardButton("✨ Follow Us", callback_data="follow"),
        ],
        [
            InlineKeyboardButton("🔗 My Referral Link", callback_data="referral"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
        [
            InlineKeyboardButton(
                "📢 Share This Bot",
                url=f"https://t.me/share/url?url={BOT_LINK}&text=🎬 Check out Nollywood Spotlight Bot!"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def follow_menu():
    rows = []
    if WEBSITE_URL:
        rows.append([InlineKeyboardButton("🌟 Official Website", url=WEBSITE_URL)])
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
    rows.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)

def back_only():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")]]
    )

# ============================================================
# WELCOME TEXT
# ============================================================

def welcome_text(total_users):
    return (
        "╔══════════════════════════╗\n"
        "   🎬 *NOLLYWOOD SPOTLIGHT* 🎬\n"
        "╚══════════════════════════╝\n\n"
        "🌟 *Your #1 gateway to Nollywood!*\n\n"
        "✨ *What you get:*\n"
        "📰 Newest News Updates\n"
        "📸 Celebrity Paparazzi\n"
        "🎧 Music News\n"
        "🏷️ Promotions\n"
        "💰 Giveaways\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Total Users:* `{total_users}`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 *Tap a button below to begin!*"
    )

# ============================================================
# HANDLERS
# ============================================================

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

    await update.message.reply_text(
        welcome_text(total_users),
        reply_markup=main_menu(),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    total = await db.get_total_users()
    text = (
        "📊 *LIVE BOT STATISTICS*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 *Total Users:* `{total}`\n"
        f"🕐 *Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        "Invite friends to grow our community! 🌟"
    )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_only())

async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    text = (
        "🎬 *NOLLYWOOD SPOTLIGHT BOT*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Your ultimate gateway to the Nigerian film industry. Get the latest news, "
        "celebrity updates, trivia, and more.\n\n"
        "🌟 *Stay Connected:*\n"
        f"🌐 Website: {WEBSITE_URL}\n"
        f"📺 Channel: {TELEGRAM_CHANNEL}\n"
        f"👥 Group: {TELEGRAM_GROUP}\n\n"
        "📋 *Commands:*\n"
        "/start — Main menu\n"
        "/help — Show help\n"
        "/trivia — Play Nollywood trivia\n"
        "/movie — Random movie suggestion\n"
        "/stats — Bot statistics\n"
        "/about — About this bot"
    )
    await q.edit_message_text(
        text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=back_only(),
    )

async def follow_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "✨ *FOLLOW NOLLYWOOD SPOTLIGHT*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Stay connected across all our platforms 👇",
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
        "🔗 *YOUR REFERRAL LINK*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"`{ref_link}`\n\n"
        f"👥 *Users referred:* `{ref_count}`\n\n"
        "🌟 Share this link and grow the community!"
    )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_only())

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    total = await db.get_total_users()
    await q.edit_message_text(
        welcome_text(total),
        parse_mode="Markdown",
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )

async def movie_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("🎬 Picking a movie for you...")
    m, tag = pick_movie()
    text = (
        f"{tag}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎥 *{m['title']}* ({m['year']})\n\n"
        f"🎭 *Genre:* {m['genre']}\n"
        f"⭐ *Starring:* {m['star']}\n\n"
        "🌟 Want more? Visit our website!"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌟 Visit Website", url=WEBSITE_URL)],
        [
            InlineKeyboardButton("🎲 Another Movie", callback_data="movie"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_main"),
        ],
    ])
    await q.edit_message_text(
        text, parse_mode="Markdown", reply_markup=kb, disable_web_page_preview=True
    )

async def trivia_callback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await send_trivia(q.message, context, edit=True, query=q)

async def send_trivia(message, context, edit=False, query=None):
    q_data = random.choice(TRIVIA)
    context.user_data['trivia_answer'] = q_data["answer"]
    keyboard = [
        [InlineKeyboardButton(f"⭐ {o}", callback_data=f"trivia_{o}")]
        for o in q_data["options"]
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")])
    text = (
        "🎯 *NOLLYWOOD TRIVIA*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{q_data['question']}\n\n"
        "👇 *Pick your answer:*"
    )
    if edit and query:
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await message.reply_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def trivia_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    selected = q.data.split("_", 1)[1]
    correct = context.user_data.get('trivia_answer')
    if not correct:
        await q.edit_message_text(
            "❌ This trivia has expired. Use /trivia to start a new one.",
            reply_markup=back_only(),
        )
        return

    if selected == correct:
        result = (
            "🎉 *CORRECT!* 🌟\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ The answer is *{correct}*\n\n"
            "🏆 You're a true Nollywood fan!"
        )
    else:
        result = (
            "❌ *Oops — Wrong!*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✔️ Correct answer: *{correct}*\n"
            f"❌ You picked: *{selected}*\n\n"
            "💡 Better luck next time!"
        )
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎯 Play Again", callback_data="trivia"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_main"),
        ],
    ])
    await q.edit_message_text(result, parse_mode="Markdown", reply_markup=kb)
    context.user_data.pop('trivia_answer', None)

# ---- Slash commands ----
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *NOLLYWOOD SPOTLIGHT — COMMANDS*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "/start — Main menu\n"
        "/help — This help message\n"
        "/trivia — Play Nollywood trivia\n"
        "/movie — Random Nollywood movie\n"
        "/stats — Bot statistics\n"
        "/about — About this bot\n\n"
        "🌟 Explore the menu for more!",
        parse_mode="Markdown",
    )

async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_trivia(update.message, context)

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m, tag = pick_movie()
    await update.message.reply_text(
        f"{tag}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎥 *{m['title']}* ({m['year']})\n\n"
        f"🎭 *Genre:* {m['genre']}\n"
        f"⭐ *Starring:* {m['star']}\n\n"
        "🌟 Want more? Visit our website!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🌟 Visit Website", url=WEBSITE_URL)]]
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = await db.get_total_users()
    await update.message.reply_text(
        f"👥 *Total Users:* `{total}`", parse_mode="Markdown"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *NOLLYWOOD SPOTLIGHT BOT*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Your gateway to the Nigerian film industry.\n\n"
        f"🌐 {WEBSITE_URL}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

# ---- Admin ----
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
    await update.message.reply_text(
        f"📊 *Admin Stats*\n\nTotal Users: `{total}`", parse_mode="Markdown"
    )

# ---- Post Init ----
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

# ---- Dashboard thread ----
def run_dashboar:* `{total}`", parse_mode="Markdown")

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
