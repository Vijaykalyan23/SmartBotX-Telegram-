import logging
import openai
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

# 🔹 Replace these with your actual tokens
TELEGRAM_TOKEN = "7753070354:AAEAhllIlAfHWGJFP9enm0H0vWZF2ufdFIk"
OPENAI_API_KEY = "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"
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
CHAT_ID = "YOUR_CHAT_ID"  # Your Telegram chat ID for scheduled messages

# 🔹 Initialize APIs
openai.api_key = OPENAI_API_KEY

# 🔹 Logging (for debugging)
logging.basicConfig(level=logging.INFO)

# ✅ Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! 🤖 I'm your bot. Type /help to see my features!")

# ✅ Help Command
async def help_command(update: Update, context: CallbackContext):
    help_text = """
🛠 Available Commands:
/start - Welcome Message
/help - Show this menu
/about - Info about me
/weather <city> - Get live weather
/menu - Open interactive menu
(Chat with me for AI responses!)
    """
    await update.message.reply_text(help_text)

# ✅ About Command
async def about(update: Update, context: CallbackContext):
    await update.message.reply_text("I'm a smart Telegram bot powered by Python and AI! 🤖")

# ✅ Weather Command
async def weather(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Usage: /weather <city>")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        await update.message.reply_text("❌ City not found. Try again.")
    else:
        weather_info = f"🌡 Temperature: {response['main']['temp']}°C\n☁ Condition: {response['weather'][0]['description']}"
        await update.message.reply_text(f"Weather in {city}:\n{weather_info}")

# ✅ AI Chatbot (ChatGPT)
async def chatgpt_response(update: Update, context: CallbackContext):
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    await update.message.reply_text(response["choices"][0]["message"]["content"])

# ✅ Inline Keyboard (Menu)
async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Google 🌍", url="https://www.google.com")],
        [InlineKeyboardButton("Weather ☁", callback_data="weather"), InlineKeyboardButton("About ℹ", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# ✅ Scheduled Daily Message
async def daily_message(context: CallbackContext):
    await context.bot.send_message(CHAT_ID, "Good morning! ☀️ Here's your daily update.")

def schedule_jobs():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.bot.loop.create_task(daily_message()), 'cron', hour=9, minute=0)
    scheduler.start()

# ✅ Main Function
def main():
    global app
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("weather", weather, pass_args=True))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_response))

    # Start Scheduled Jobs
    schedule_jobs()

    print("Bot is running... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
