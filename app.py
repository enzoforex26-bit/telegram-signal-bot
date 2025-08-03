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

# Konfiguration
BOT_TOKEN = "8226474584:AAGcRUWTdLACwMmHLnK8D-GREeUsoUXYPQ"
GROUP_ID = -1002845601347
GROUP_LINK = "https://t.me/Swissgoldsingal"

# States
NAME, EMAIL, EXPERIENCE = range(3)

# Flask App
app = Flask(__name__)
bot = Bot(BOT_TOKEN)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen! Wie heisst du?")
    return NAME

# Name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Wie ist deine E-Mail-Adresse?")
    return EMAIL

# E-Mail
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

# Erfahrung + Link senden
async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    await update.message.reply_text(f"✅ Danke! Hier ist der Link zur Signalgruppe:\n{GROUP_LINK}")
    return ConversationHandler.END

# Bot starten
def start_bot():
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

# Webhook für TradingView
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    msg = data.get("message", "⚠️ Kein Text enthalten")
    bot.send_message(chat_id=GROUP_ID, text=msg)
    return "OK", 200

# Flask + Telegram parallel
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=5000)
