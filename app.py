from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8226474584:AAGcRUWTlDLACwMmHLnK8D-GREeUsoUXYPQ"
ADMIN_ID = 1785174843
GROUP_ID = -1002845601347

NAME, EMAIL, EXPERIENCE = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Willkommen bei Swiss Gold Trades 🪙\nWie ist dein Name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Danke! Wie ist deine E-Mail-Adresse?")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Wie viel Trading-Erfahrung hast du?")
    return EXPERIENCE

async def get_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text

    user_info = f"""
📥 Neuer Benutzer:
👤 Name: {context.user_data['name']}
📧 E-Mail: {context.user_data['email']}
📊 Erfahrung: {context.user_data['experience']}
    """
    await context.bot.send_message(chat_id=GROUP_ID, text=user_info)
    await update.message.reply_text("Danke! Du wirst bald freigeschaltet. 📈")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
    },
    fallbacks=[],
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    app.run_polling()
