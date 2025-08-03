from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from flask import Flask, request
import asyncio
import threading

# Bot-Konfiguration
BOT_TOKEN = "8226474584:AAGcRUWTdLACwMmHLnK8D-GREeUsoUXYPQ"
GROUP_LINK = "https://t.me/Swissgoldsingal"
GROUP_ID = -1002845601347

# States für die Konversation
NAME, EMAIL, EXPERIENCE = range(3)

# Flask App
app = Flask(__name__)
bot = Bot(BOT_TOKEN)

# Telegram: Start-Befehl
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen! Wie heisst du?")
    return NAME

# Telegram: Name speichern
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Wie ist deine E-Mail-Adresse?")
    return EMAIL

# Telegram: E-Mail speichern
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

# Telegram: Erfahrung speichern und Link senden
async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    await update.message.reply_text(f"✅ Danke! Hier ist der Link zur Signalgruppe:\n{GROUP_LINK}")
    return ConversationHandler.END

# Telegram-Bot starten
def telegram_bot():
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
    asyncio.run(app_bot.run_polling())

# Webhook Endpoint für TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "⚠️ Kein Inhalt erhalten.")
    bot.send_message(chat_id=GROUP_ID, text=message)
    return "OK", 200

# Start Flask + Telegram parallel
if __name__ == "__main__":
    threading.Thread(target=telegram_bot).start()
    app.run(host="0.0.0.0", port=5000)
