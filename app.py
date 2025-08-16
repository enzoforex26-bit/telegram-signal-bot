import threading
import logging
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

BOT_TOKEN = "8226474584:AAHoTLwWAiLiLsBNnNX_CuUukzMTNWdsc-o"
GROUP_ID = -1002845601347
GROUP_LINK = "https://t.me/swissgoldsingal"
BROKER_LINK = "https://go.ironfx.com/visit/?bta=57545&brand=ironfx"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("telegram-bot")

app = Flask(__name__)
bot = Bot(BOT_TOKEN)

NAME, EMAIL, EXPERIENCE = range(3)

WELCOME_TEXT = "Willkommen! Wie heisst du?"
ASK_EMAIL = "Danke! Wie ist deine E-Mail?"
ASK_EXP = "Wie viel Trading-Erfahrung hast du?"

JOIN_MSG = (
    "📈 Danke, {name}!\n\n"
    f"👉 Signalgruppe: {GROUP_LINK}\n"
    f"👉 Broker-Link: {BROKER_LINK}\n\n"
    "🎁 *Gewinnspiel:* Bei einer Einzahlung von *300 CHF/EUR+* nimmst du automatisch am Trip nach *Dubai* teil.\n\n"
    "Schreibe /broker, um den Link jederzeit erneut zu bekommen."
)

BROKER_MSG = (
    f"👉 Broker-Link: {BROKER_LINK}\n\n"
    "🎁 Gewinnspiel: Ab *300 CHF/EUR* Einzahlung nimmst du automatisch am Dubai-Trip teil."
)

def start(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        return ConversationHandler.END
    update.message.reply_text(WELCOME_TEXT)
    return NAME

def get_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text.strip()
    update.message.reply_text(ASK_EMAIL)
    return EMAIL

def get_email(update: Update, context: CallbackContext):
    context.user_data["email"] = update.message.text.strip()
    update.message.reply_text(ASK_EXP)
    return EXPERIENCE

def get_experience(update: Update, context: CallbackContext):
    name = context.user_data.get("name", "Neues Mitglied")
    context.user_data["experience"] = update.message.text.strip()
    user_id = update.effective_user.id
    try:
        bot.send_message(chat_id=user_id, text=JOIN_MSG.format(name=name), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        bot.send_message(chat_id=GROUP_ID, text=f"🎉 {name} ist neu in der Gruppe!")
    except Exception as e:
        logger.error(f"Senden fehlgeschlagen: {e}")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    if update.effective_chat.type == "private":
        update.message.reply_text("Abgebrochen.")
    return ConversationHandler.END

def cmd_broker(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        return
    update.message.reply_text(BROKER_MSG, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def unknown(update: Update, context: CallbackContext):
    return

def error_handler(update: object, context: CallbackContext):
    logger.exception("Fehler im Update-Handler", exc_info=context.error)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True) or {}
        message = data.get("message", "⚠️ Kein Inhalt erhalten.")
        bot.send_message(chat_id=GROUP_ID, text=message)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook-Fehler: {e}")
        return "Fehler", 500

def run_flask():
    app.run(host="0.0.0.0", port=5000)

def run_telegram():
    updater = Updater(BOT_TOKEN, use_context=True)
    try:
        updater.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"delete_webhook warn: {e}")

    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start, filters=Filters.chat_type.private)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, get_name)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, get_email)],
            EXPERIENCE: [MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, get_experience)],
        },
        fallbacks=[CommandHandler("cancel", cancel, filters=Filters.chat_type.private)],
        allow_reentry=False,
    )

    dp.add_handler(conv)
    dp.add_handler(CommandHandler("broker", cmd_broker, filters=Filters.chat_type.private))
    dp.add_handler(MessageHandler(Filters.all, unknown))
    dp.add_error_handler(error_handler)

    updater.start_polling(clean=True, allowed_updates=["message", "edited_message", "channel_post", "edited_channel_post"])
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_telegram()
