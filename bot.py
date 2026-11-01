import os
import threading
import telebot
from telebot import types
from flask import Flask

# ---------------------------------------------------------
# 1. LIGHTWEIGHT WEB SERVER FOR CRON-JOB PINGS
# ---------------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and monitoring!"

def run_web_server():
    # Render automatically assigns an internal port via the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Start the web server on a separate thread so it doesn't block your Telegram bot polling loop
threading.Thread(target=run_web_server, daemon=True).start()

# ---------------------------------------------------------
# 2. CONFIGURATION (Direct Credentials - Safe for Private Repos)
# ---------------------------------------------------------
API_TOKEN = '9264444554:AAGgQ4Ja87XcpRWVKljjT-r1zwgB7R_wjQw'  # ⚠️ Replace this text with your real token inside the quotes
MY_CHAT_ID = 9283320303                        # Your private numerical Telegram ID

# ---------------------------------------------------------
# 3. TELEGRAM BOT CORE ENGINE
# ---------------------------------------------------------
bot = telebot.TeleBot(API_TOKEN)
user_states = {}

# Handle the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == MY_CHAT_ID:
        bot.send_message(MY_CHAT_ID, "🤖 Cloud Bot Active & Monitoring Validations.")
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        validation_button = types.KeyboardButton("🔐 Submit Referral ID Details")
        markup.add(validation_button)
        
        welcome_text = (
            "Hello! Welcome to our secure verification hub.\n\n"
            "⚠️ You must submit your referral ID details for validation before any business transaction can take place."
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Process workflows (Text layout bypassing privacy restrictions)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # IF THE MESSAGE IS FROM YOU (THE ADMIN)
    if message.chat.id == MY_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.text and "🆔 Telegram ID:" in message.reply_to_message.text:
            try:
                # Extract the sender's user ID directly out of the alert text block
                lines = message.reply_to_message.text.split("\n")
                target_user_id = int(lines.split(":`").replace("`", "").strip())
                bot.send_message(target_user_id, message.text)
                bot.send_message(MY_CHAT_ID, "✅ Reply sent successfully!")
            except Exception as e:
                bot.send_message(MY_CHAT_ID, f"❌ Failed to reply. Error: {str(e)}")
        else:
            bot.send_message(MY_CHAT_ID, "⚠️ To reply, right-click/long-press the text block alert and choose 'Reply'.")
    
    # IF A USER CLICKS THE SUBMIT BUTTON
    elif message.text == "🔐 Submit Referral ID Details":
        user_states[message.chat.id] = "waiting_for_id"
        instruction_text = (
            "📝 **Please type and send your Referral ID details below:**\n\n"
            "Once submitted, the administrator will validate your information."
        )
        bot.send_message(message.chat.id, instruction_text, parse_mode="Markdown")
        
    # IF THE USER SENDS THEIR REFERRAL ID
    elif user_states.get(message.chat.id) == "waiting_for_id":
        user_states[message.chat.id] = None
        bot.send_message(message.chat.id, "✅ Thank you! Your Referral ID has been submitted. Please wait while the admin reviews it.")
        
        # Hardcoded message text layout that bypasses native forward restrictions completely
        alert_text = (
            f"🔔 **NEW VALIDATION REQUEST**\n"
            f"👤 User: @{message.from_user.username or 'No Username'}\n"
            f"🆔 Telegram ID: `{message.chat.id}`\n\n"
            f"🔑 **Submitted Referral ID:**\n{message.text}"
        )
        bot.send_message(MY_CHAT_ID, alert_text, parse_mode="Markdown")

    # GENERAL TRAFFIC
    else:
        chat_text = (
            f"📩 **New Chat Message**\n"
            f"👤 From: @{message.from_user.username or 'No Username'}\n"
            f"🆔 Telegram ID: `{message.chat.id}`\n\n"
            f"💬 **Message:**\n{message.text}"
        )
        bot.send_message(MY_CHAT_ID, chat_text, parse_mode="Markdown")

print("🔒 Error-proof validation bot is booting up with background ping server...")
bot.infinity_polling()
