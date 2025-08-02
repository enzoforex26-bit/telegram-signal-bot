from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import requests
import threading

BOT_TOKEN = "8226474584:AAGcRUWTlDLACwMmHLnK8D-GREeUsoUXYPQ"
GROUP_ID = "-1002845601347"
BROKER_LINK = None

NAME, EMAIL, EXPERIENCE = range(3)

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen! Wie heisst du?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Was ist deine E-Mail?")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    name = context.user_data["name"]
    user_id = update.message.from_user.id
    bot = Bot(BOT_TOKEN)

    try:
        await bot.send_message(chat_id=user_id, text="✅ Danke! Du wirst gleich in die Gruppe aufgenommen.")
        await bot.send_message(chat_id=GROUP_ID, text=f"🎉 {name} ist neu in der Gruppe!")
        if BROKER_LINK:
            await bot.send_message(chat_id=GROUP_ID, text=f"📥 {name}, hier ist dein Broker-Link:\n{BROKER_LINK}")
    except Exception as e:
        print("Fehler beim Hinzufügen:", e)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Abgebrochen.")
    return ConversationHandler.END

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "⚠️ Kein Inhalt erhalten.")
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID,
        "text": message
    }
    requests.post(telegram_url, json=payload)
    return "OK", 200

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

telegram_app.add_handler(conv_handler)

def run_flask():
    app.run(host="0.0.0.0", port=5000)

def run_telegram():
    telegram_app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_telegram).start()
