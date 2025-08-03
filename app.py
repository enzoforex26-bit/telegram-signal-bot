import threading
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Konfiguration
BOT_TOKEN = "8226474584:AAGcRUWTdLAcwMmHLnKBD-GREeUsoUXYPQ"
GROUP_ID = -1002845601347
GROUP_LINK = "https://t.me/swissgoldsingal"

# Flask App
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
updater = None

# States
NAME, EMAIL, EXPERIENCE = range(3)

# Telegram Bot Logik
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Willkommen! Wie heisst du?")
    return NAME

def get_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text
    update.message.reply_text("Wie ist deine E-Mail-Adresse?")
    return EMAIL

def get_email(update: Update, context: CallbackContext):
    context.user_data["email"] = update.message.text
    update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

def get_experience(update: Update, context: CallbackContext):
    context.user_data["experience"] = update.message.text
    update.message.reply_text(f"📈 Danke! Hier ist der Link zur Signalgruppe:\n{GROUP_LINK}")
    return ConversationHandler.END

# Webhook-Endpunkt für TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    msg = data.get("message", "⚠️ Kein Text enthalten")
    bot.send_message(chat_id=GROUP_ID, text=msg)
    return "OK", 200

# Telegram-Bot starten
def run_telegram_bot():
    global updater
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
            EXPERIENCE: [MessageHandler(Filters.text & ~Filters.command, get_experience)],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)
    print("✅ Telegram-Bot läuft...")
    updater.start_polling()
    updater.idle()

# Telegram und Flask parallel starten
def start_all():
    threading.Thread(target=run_telegram_bot).start()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    start_all()
