import threading
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

# Konfiguration
BOT_TOKEN = "8226474584:AAGcRUWTdLAcwMmHLnKBD-GREeUsoUXYPQ"
GROUP_ID = -1002845601347
GROUP_LINK = "https://t.me/swissgoldsingal"

# Flask App
app = Flask(__name__)
bot_instance = Bot(BOT_TOKEN)  # getrenntes Bot-Objekt nur für Webhook

# States
NAME, EMAIL, EXPERIENCE = range(3)

# Telegram Bot Logik
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen! Wie heisst du?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Wie ist deine E-Mail-Adresse?")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    await update.message.reply_text(f"📈 Danke! Hier ist der Link zur Signalgruppe:\n{GROUP_LINK}")
    return ConversationHandler.END

# Webhook für TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    msg = data.get("message", "⚠️ Kein Text enthalten")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_instance.send_message(chat_id=GROUP_ID, text=msg))
    loop.close()
    return "OK", 200

# Telegram-Bot starten
async def telegram_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
        },
        fallbacks=[],
    )

    app_bot.add_handler(conv_handler)
    print("✅ Telegram-Bot läuft...")
    await app_bot.run_polling()

# Flask + Telegram parallel starten
def start_all():
    threading.Thread(target=lambda: asyncio.run(telegram_bot())).start()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    start_all()
