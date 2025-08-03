from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackContext
from flask import Flask, request
import requests
import json

BOT_TOKEN = "8226474584:AAGcRUWTlDLACwMmHLnK8D-GREeUsoUXYPQ"
ADMIN_ID = 1785174843
GROUP_ID = -1002845601347
BROKER_LINK = None

NAME, EMAIL, EXPERIENCE = range(3)

app = Flask(__name__)
bot = Bot(BOT_TOKEN)

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
    await update.message.reply_text("Danke.")

    name = context.user_data["name"]
    user_id = update.message.from_user.id

    await bot.send_message(chat_id=user_id, text="Hier ist der Gruppenlink:\nhttps://t.me/Swissgoldsingal")
    await bot.send_message(chat_id=user_id, text="✅ Danke! Du wirst gleich in die Gruppe aufgenommen.")
    await bot.send_message(chat_id=GROUP_ID, text=f"🎉 {name} ist neu in der Gruppe!")

    if BROKER_LINK:
        await bot.send_message(chat_id=GROUP_ID, text=f"📈 {name}, hier ist dein Broker-Link:\n{BROKER_LINK}")

    try:
        await bot.add_chat_members(chat_id=GROUP_ID, user_ids=[user_id])
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
