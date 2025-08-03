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
import os

BOT_TOKEN = "8226474584:AAGcRUWTlDLACwMmHLnK8D-GREeUsoUXYPQ"
GROUP_ID = -1002845601347
BROKER_LINK = None
NAME, EMAIL, EXPERIENCE = range(3)

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Willkommen! Wie heisst du?")
    return NAME

def get_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text
    update.message.reply_text("Was ist deine E-Mail?")
    return EMAIL

def get_email(update: Update, context: CallbackContext):
    context.user_data["email"] = update.message.text
    update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

def get_experience(update: Update, context: CallbackContext):
    context.user_data["experience"] = update.message.text
    update.message.reply_text("Danke.")
    update.message.reply_text("https://t.me/SwissGoldsignal")
    return ConversationHandler.END
    try:
        bot.send_message(chat_id=user_id, text="✅ Danke! Du wirst gleich in die Gruppe aufgenommen.")
        bot.send_message(chat_id=GROUP_ID, text=f"🎉 {name} ist neu in der Gruppe!")

        if BROKER_LINK:
            bot.send_message(chat_id=GROUP_ID, text=f"📥 {name}, hier ist dein Broker-Link:\n{BROKER_LINK}")

        bot.invite_chat_member(chat_id=GROUP_ID, user_id=user_id)
    except Exception as e:
        print("Fehler beim Hinzufügen:", e)

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Abgebrochen.")
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
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        EMAIL: [MessageHandler(Filters.text & ~Filters.command, get_email)],
        EXPERIENCE: [MessageHandler(Filters.text & ~Filters.command, get_experience)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

dispatcher.add_handler(conv_handler)

def run_flask():
    app.run(host="0.0.0.0", port=5000)

def run_telegram():
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_telegram).start()
