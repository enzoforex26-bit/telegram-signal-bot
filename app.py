from telegram import Update, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
import requests

BOT_TOKEN = "8226474584:AAGcRUWTdLACwMmHLnK8D-GREeUsoUXYPQ"
ADMIN_ID = 1785174843
GROUP_ID = -1002845601347
BROKER_LINK = None

NAME, EMAIL, EXPERIENCE = range(3)

bot = Bot(BOT_TOKEN)

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

    name = context.user_data["name"]
    user_id = update.effective_user.id

    try:
        bot.send_message(chat_id=user_id, text="Hier ist der Gruppenlink:\nhttps://t.me/Swissgoldsingal")
        bot.send_message(chat_id=user_id, text="✅ Danke! Du wirst gleich in die Gruppe aufgenommen.")
        bot.send_message(chat_id=GROUP_ID, text=f"🎉 {name} ist neu in der Gruppe!")

        if BROKER_LINK:
            bot.send_message(chat_id=GROUP_ID, text=f"{name}, hier ist dein Broker-Link:\n{BROKER_LINK}")

        bot.invite_chat_member(chat_id=GROUP_ID, user_id=user_id)

    except Exception as e:
        print("Fehler beim Senden oder Einladen:", e)

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Abgebrochen.")
    return ConversationHandler.END

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
    run_telegram()
