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
import threading
import requests

# Konfiguration
BOT_TOKEN = "8226474584:AAGcRUWTlDLACwMmHLnK8D-GREeUsoUXYPQ"
GROUP_ID = -1002845601347
GROUP_LINK = "https://t.me/swissgoldsingal"

# Flask App
app = Flask(__name__)
bot = Bot(BOT_TOKEN)

# States
NAME, EMAIL, EXPERIENCE = range(3)

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
    name = context.user_data["name"]
    context.user_data["experience"] = update.message.text
    user_id = update.message.from_user.id

    try:
        bot.send_message(chat_id=user_id, text=f"📈 Danke! Hier ist der Link zur Signalgruppe:\n{GROUP_LINK}")
        bot.send_message(chat_id=GROUP_ID, text=f"🎉 {name} ist neu in der Gruppe!")
    except Exception as e:
        print("Fehler beim Senden:", e)

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Abgebrochen.")
    return ConversationHandler.END

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "⚠️ Kein Inhalt erhalten.")
    try:
        bot.send_message(chat_id=GROUP_ID, text=message)
        return "OK", 200
    except Exception as e:
        print("Webhook-Fehler:", e)
        return "Fehler", 500

def run_flask():
    app.run(host="0.0.0.0", port=5000)

def run_telegram():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
            EXPERIENCE: [MessageHandler(Filters.text & ~Filters.command, get_experience)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_telegram()
