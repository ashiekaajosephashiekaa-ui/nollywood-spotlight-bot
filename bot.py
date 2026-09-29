import logging
import random
import threading
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import (
    BOT_TOKEN, ADMIN_ID, WEBSITE_URL, BOT_USERNAME, BOT_LINK,
    TELEGRAM_CHANNEL, TELEGRAM_GROUP, INSTAGRAM, TWITTER,
    FACEBOOK, YOUTUBE, TIKTOK, WHATSAPP_CHANNEL,
)
import database as db

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


RECENT_MOVIES = [
    {"title": "Behind The Scenes", "year": 2025, "genre": "Drama", "star": "Funke Akindele"},
    {"title": "Gingerrr", "year": 2025, "genre": "Comedy", "star": "Toyin Abraham"},
    {"title": "Oversabi Aunty", "year": 2025, "genre": "Family Comedy", "star": "Toyin Abraham"},
    {"title": "Ori: The Rebirth", "year": 2025, "genre": "Epic Fantasy", "star": "Muyiwa Ademola"},
    {"title": "Reel Love", "year": 2025, "genre": "Romance", "star": "Timini Egbuson"},
    {"title": "Labake Olododo", "year": 2025, "genre": "Period Drama", "star": "Iyabo Ojo"},
    {"title": "Owambe Thieves", "year": 2025, "genre": "Comedy Crime", "star": "Odunlade Adekola"},
    {"title": "The Herd", "year": 2025, "genre": "Thriller", "star": "Daniel Etim Effiong"},
    {"title": "A Lagos Love Story", "year": 2025, "genre": "Romance", "star": "Jemima Osunde"},
    {"title": "Unclaimed", "year": 2025, "genre": "Psychological Thriller", "star": "Kunle Remi"},
    {"title": "Nini", "year": 2025, "genre": "Emotional Thriller", "star": "Mariah Ugbashi"},
    {"title": "To Kill a Monkey", "year": 2025, "genre": "Crime Thriller", "star": "Kemi Adetiba"},
    {"title": "A Very Dirty December", "year": 2025, "genre": "Comedy Drama", "star": "Ini Edo"},
    {"title": "Lisabi: A Legend Is Born", "year": 2025, "genre": "Historical Epic", "star": "Lateef Adedimeji"},
    {"title": "Warlord: Olori Ogun", "year": 2025, "genre": "Historical Epic", "star": "Odunlade Adekola"},
    {"title": "The Four", "year": 2026, "genre": "Drama", "star": "Funke Akindele"},
    {"title": "Black Market", "year": 2026, "genre": "Crime Thriller", "star": "Fatimah Binta Gimsay"},
    {"title": "IYALOJA", "year": 2026, "genre": "Thriller", "star": "Kehinde Bankole"},
    {"title": "Remi and Nneoma", "year": 2026, "genre": "Drama", "star": "Liz Benson"},
    {"title": "EVI", "year": 2026, "genre": "Musical Drama", "star": "Osas Okonyon"},
]

CLASSIC_MOVIES = [
    {"title": "Living in Bondage", "year": 1992, "genre": "Drama", "star": "Kenneth Okonkwo"},
    {"title": "Glamour Girls", "year": 1994, "genre": "Drama", "star": "Eucharia Anunobi"},
    {"title": "The Figurine", "year": 2009, "genre": "Thriller", "star": "Ramsey Nouah"},
    {"title": "October 1", "year": 2014, "genre": "Thriller", "star": "Sadiq Daba"},
    {"title": "King of Boys", "year": 2018, "genre": "Crime Drama", "star": "Sola Sobowale"},
    {"title": "Lionheart", "year": 2018, "genre": "Drama", "star": "Genevieve Nnaji"},
]

TRIVIA = [
    {"question": "Which Nollywood legend is called The King of Nollywood?",
     "options": ["Ramsey Nouah", "Pete Edochie", "Chiwetalu Agu", "RMD"],
     "answer": "Pete Edochie"},
    {"question": "What year was the Nigerian film industry nicknamed Nollywood?",
     "options": ["1992", "1998", "2000", "2005"],
     "answer": "1992"},
    {"question": "Which 2023 movie broke Nollywood box office records with over 1 billion Naira?",
     "options": ["The Black Book", "A Tribe Called Judah", "Gangs of Lagos", "Jagun Jagun"],
     "answer": "A Tribe Called Judah"},
    {"question": "Which actress starred in and directed Lionheart?",
     "options": ["Genevieve Nnaji", "Omotola Jalade", "Rita Dominic", "Ini Edo"],
     "answer": "Genevieve Nnaji"},
    {"question": "Which 2023 epic showcased Yoruba cultural storytelling?",
     "options": ["Anikulapo", "Jagun Jagun", "House of Gaa", "Lisabi"],
     "answer": "Jagun Jagun"},
    {"question": "Who directed October 1 and Ijogbon?",
     "options": ["Kunle Afolayan", "Tunde Kelani", "Niyi Akinmolayan", "Izu Ojukwu"],
     "answer": "Kunle Afolayan"},
    {"question": "Which 2022 film is set in the Niger Delta?",
     "options": ["Brotherhood", "Shanty Town", "Anikulapo", "Adire"],
     "answer": "Brotherhood"},
    {"question": "Which actress is nicknamed Toyin Tomato?",
     "options": ["Funke Akindele", "Toyin Abraham", "Mercy Johnson", "Iyabo Ojo"],
     "answer": "Toyin Abraham"},
    {"question": "Which 2024 epic tells the story of a Yoruba warrior?",
     "options": ["Lisabi: The Uprising", "House of Gaa", "Beast of Two Worlds", "Kaka"],
     "answer": "Lisabi: The Uprising"},
    {"question": "Who produced Battle on Buka Street and A Tribe Called Judah?",
     "options": ["Funke Akindele", "Toyin Abraham", "Mercy Johnson", "Nkem Owoh"],
     "answer": "Funke Akindele"},
    {"question": "Which actor is famous for the catchphrase I go wound o?",
     "options": ["Chiwetalu Agu", "Nkem Owoh", "John Okafor", "Charles Inojie"],
     "answer": "Chiwetalu Agu"},
    {"question": "Which late comedian was beloved as Mr Ibu?",
     "options": ["John Okafor", "Baba Suwe", "Sam Loco Efe", "Sanyeri"],
     "answer": "John Okafor"},
    {"question": "The 2023 film Mami Wata is shot in which language?",
     "options": ["Yoruba", "Igbo", "Pidgin English", "Hausa"],
     "answer": "Pidgin English"},
    {"question": "Which streaming giant produced The Black Book?",
     "options": ["Netflix", "Amazon Prime", "Disney+", "Apple TV+"],
     "answer": "Netflix"},
]


def pick_movie():
    if random.random() < 0.8:
        return random.choice(RECENT_MOVIES), "NEW RELEASE"
    return random.choice(CLASSIC_MOVIES), "NOLLYWOOD CLASSIC"


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Visit Nollywood Spotlight Website", url=WEBSITE_URL)],
        [
            InlineKeyboardButton("Join Channel", url=TELEGRAM_CHANNEL),
            InlineKeyboardButton("Join Group", url=TELEGRAM_GROUP),
        ],
        [
            InlineKeyboardButton("Random Movie", callback_data="movie"),
            InlineKeyboardButton("Play Trivia", callback_data="trivia"),
        ],
        [
            InlineKeyboardButton("Live Stats", callback_data="stats"),
            InlineKeyboardButton("Follow Us", callback_data="follow"),
        ],
        [
            InlineKeyboardButton("My Referral Link", callback_data="referral"),
            InlineKeyboardButton("About", callback_data="about"),
        ],
        [InlineKeyboardButton(
            "Share This Bot",
            url="https://t.me/share/url?url=" + BOT_LINK + "&text=Check out Nollywood Spotlight Bot"
        )],
    ])


def follow_menu():
    rows = []
    if WEBSITE_URL:
        rows.append([InlineKeyboardButton("Official Website", url=WEBSITE_URL)])
    tg = []
    if TELEGRAM_CHANNEL:
        tg.append(InlineKeyboardButton("Telegram Channel", url=TELEGRAM_CHANNEL))
    if TELEGRAM_GROUP:
        tg.append(InlineKeyboardButton("Community Group", url=TELEGRAM_GROUP))
    if tg:
        rows.append(tg)
    social = []
    if INSTAGRAM: social.append(InlineKeyboardButton("Instagram", url=INSTAGRAM))
    if TWITTER:   social.append(InlineKeyboardButton("X Twitter", url=TWITTER))
    if FACEBOOK:  social.append(InlineKeyboardButton("Facebook", url=FACEBOOK))
    if social:
        rows.append(social)
    media = []
    if YOUTUBE:  media.append(InlineKeyboardButton("YouTube", url=YOUTUBE))
    if TIKTOK:   media.append(InlineKeyboardButton("TikTok", url=TIKTOK))
    if WHATSAPP_CHANNEL: media.append(InlineKeyboardButton("WhatsApp", url=WHATSAPP_CHANNEL))
    if media:
        rows.append(media)
    rows.append([InlineKeyboardButton("Back to Menu", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def back_only():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back to Menu", callback_data="back_main")]]
    )


def welcome_text(total):
    return (
        "NOLLYWOOD SPOTLIGHT\n"
        "========================\n\n"
        "Your #1 gateway to Nollywood!\n\n"
        "What you get:\n"
        "- Newest News Updates\n"
        "- Celebrity Paparazzi\n"
        "- Music News\n"
        "- Promotions\n"
        "- Giveaways\n\n"
        "========================\n"
        "Total Users: " + str(total) + "\n"
        "========================\n\n"
        "Tap a button below to begin!"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    ref = None
    if args and args[0].startswith("ref_"):
        try:
            ref = int(args[0][4:])
        except ValueError:
            pass
    await db.add_user(user.id, user.username, user.first_name, ref)
    total = await db.get_total_users()
    await update.message.reply_text(
        welcome_text(total),
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    total = await db.get_total_users()
    text = (
        "LIVE BOT STATISTICS\n"
        "========================\n\n"
        "Total Users: " + str(total) + "\n"
        "Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n\n"
        "Invite friends to grow our community!"
    )
    await q.edit_message_text(text, reply_markup=back_only())


async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    text = (
        "NOLLYWOOD SPOTLIGHT BOT\n"
        "========================\n\n"
        "Your ultimate gateway to the Nigerian film industry. Get the latest news, "
        "celebrity updates, trivia, and more.\n\n"
        "Stay Connected:\n"
        "Website: " + WEBSITE_URL + "\n"
        "Channel: " + TELEGRAM_CHANNEL + "\n"
        "Group: " + TELEGRAM_GROUP + "\n\n"
        "Commands:\n"
        "/start - Main menu\n"
        "/help - Show help\n"
        "/trivia - Play trivia\n"
        "/movie - Random movie\n"
        "/stats - Bot statistics\n"
        "/about - About this bot"
    )
    await q.edit_message_text(text, reply_markup=back_only(), disable_web_page_preview=True)


async def follow_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "FOLLOW NOLLYWOOD SPOTLIGHT\n"
        "========================\n\n"
        "Stay connected across all our platforms:",
        reply_markup=follow_menu(),
        disable_web_page_preview=True,
    )


async def referral_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    count = await db.get_referral_count(uid)
    link = BOT_LINK + "?start=ref_" + str(uid)
    text = (
        "YOUR REFERRAL LINK\n"
        "========================\n\n"
        + link + "\n\n"
        "Users referred: " + str(count) + "\n\n"
        "Share this link and grow the community!"
    )
    await q.edit_message_text(text, reply_markup=back_only())


async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    total = await db.get_total_users()
    await q.edit_message_text(
        welcome_text(total),
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )


async def movie_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Picking a movie...")
    m, tag = pick_movie()
    text = (
        tag + "\n"
        "========================\n"
        "Title: " + m["title"] + " (" + str(m["year"]) + ")\n\n"
        "Genre: " + m["genre"] + "\n"
        "Starring: " + m["star"] + "\n\n"
        "Want more? Visit our website!"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Visit Website", url=WEBSITE_URL)],
        [
            InlineKeyboardButton("Another Movie", callback_data="movie"),
            InlineKeyboardButton("Back", callback_data="back_main"),
        ],
    ])
    await q.edit_message_text(text, reply_markup=kb, disable_web_page_preview=True)


async def trivia_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await send_trivia(q.message, context, edit=True, query=q)


async def send_trivia(message, context, edit=False, query=None):
    data = random.choice(TRIVIA)
    context.user_data["trivia_answer"] = data["answer"]
    keyboard = [[InlineKeyboardButton(o, callback_data="trivia_" + o)] for o in data["options"]]
    keyboard.append([InlineKeyboardButton("Back to Menu", callback_data="back_main")])
    text = (
        "NOLLYWOOD TRIVIA\n"
        "========================\n\n"
        + data["question"] + "\n\n"
        "Pick your answer:"
    )
    if edit and query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def trivia_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    picked = q.data.split("_", 1)[1]
    correct = context.user_data.get("trivia_answer")
    if not correct:
        await q.edit_message_text("This trivia has expired. Use /trivia to start a new one.",
                                  reply_markup=back_only())
        return
    if picked == correct:
        result = (
            "CORRECT!\n"
            "========================\n\n"
            "The answer is " + correct + "\n\n"
            "You are a true Nollywood fan!"
        )
    else:
        result = (
            "WRONG!\n"
            "========================\n\n"
            "Correct answer: " + correct + "\n"
            "You picked: " + picked + "\n\n"
            "Better luck next time!"
        )
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Play Again", callback_data="trivia"),
            InlineKeyboardButton("Back", callback_data="back_main"),
        ],
    ])
    await q.edit_message_text(result, reply_markup=kb)
    context.user_data.pop("trivia_answer", None)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "NOLLYWOOD SPOTLIGHT COMMANDS\n"
        "========================\n\n"
        "/start - Main menu\n"
        "/help - This help message\n"
        "/trivia - Play Nollywood trivia\n"
        "/movie - Random Nollywood movie\n"
        "/stats - Bot statistics\n"
        "/about - About this bot"
    )


async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_trivia(update.message, context)


async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m, tag = pick_movie()
    await update.message.reply_text(
        tag + "\n"
        "========================\n"
        "Title: " + m["title"] + " (" + str(m["year"]) + ")\n\n"
        "Genre: " + m["genre"] + "\n"
        "Starring: " + m["star"] + "\n\n"
        "Want more? Visit our website!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Visit Website", url=WEBSITE_URL)]]
        ),
        disable_web_page_preview=True,
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = await db.get_total_users()
    await update.message.reply_text("Total Users: " + str(total))


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "NOLLYWOOD SPOTLIGHT BOT\n"
        "========================\n\n"
        "Your gateway to the Nigerian film industry.\n\n"
        "Website: " + WEBSITE_URL,
        disable_web_page_preview=True,
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    users = await db.get_all_users()
    ok = 0
    fail = 0
    await update.message.reply_text("Broadcasting to " + str(len(users)) + " users...")
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=msg)
            ok += 1
        except Exception as e:
            fail += 1
            logger.error("Send fail " + str(uid) + ": " + str(e))
    await update.message.reply_text("Done.\nSuccess: " + str(ok) + "\nFailed: " + str(fail))


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized.")
        return
    total = await db.get_total_users()
    await update.message.reply_text("Admin Stats\n\nTotal Users: " + str(total))


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


def run_dashboard():
    from dashboard import app
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    threading.Thread(target=run_dashboard, daemon=True).start()
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
    app.add_handler(CallbackQueryHandler(movie_callback, pattern="^movie$"))
    app.add_handler(CallbackQueryHandler(trivia_start, pattern="^trivia$"))
    app.add_handler(CallbackQueryHandler(trivia_answer, pattern="^trivia_"))

    app.run_polling()


if __name__ == "__main__":
    main()
