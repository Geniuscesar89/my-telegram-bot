import os
import threading
import telebot
from telebot import types
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot status: Active"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web_server, daemon=True).start()

API_TOKEN = '9040439270:AAHgaj0UjMNHEFPlltwkhDSvQHGxLRvCMZc'
MY_CHAT_ID = 9283320303
bot = telebot.TeleBot(API_TOKEN)
user_states = {}
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == MY_CHAT_ID:
        bot.send_message(MY_CHAT_ID, "🤖 Cloud Bot Active.")
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        validation_button = types.KeyboardButton("🔐 Submit Referral ID Details")
        markup.add(validation_button)
        bot.send_message(message.chat.id, "Hello! Welcome.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.id == MY_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.text and "🆔 Telegram ID:" in message.reply_to_message.text:
            try:
                lines = message.reply_to_message.text.split("\n")
                for line in lines:
                    if "🆔 Telegram ID:" in line:
                        target_user_id = int(line.split("🆔 Telegram ID:")[1].replace("`", "").strip())
                        bot.send_message(target_user_id, message.text)
                        bot.send_message(MY_CHAT_ID, "✅ Reply sent!")
                        break
            except Exception as e:
                bot.send_message(MY_CHAT_ID, f"❌ Error: {str(e)}")
    elif message.text == "🔐 Submit Referral ID Details":
        user_states[message.chat.id] = "waiting_for_id"
        bot.send_message(message.chat.id, "📝 Send Referral ID details:")
    elif user_states.get(message.chat.id) == "waiting_for_id":
        user_states[message.chat.id] = None
        bot.send_message(message.chat.id, "✅ Submitted!")
        alert = f"🔔 **NEW REQUEST**\n👤 User: @{message.from_user.username or 'None'}\n🆔 Telegram ID: `{message.chat.id}`\n\n🔑 ID:\n{message.text}"
        bot.send_message(MY_CHAT_ID, alert, parse_mode="Markdown")
    else:
        chat_text = f"📩 **New Message**\n👤 From: @{message.from_user.username or 'None'}\n🆔 Telegram ID: `{message.chat.id}`\n\n💬 Message:\n{message.text}"
        bot.send_message(MY_CHAT_ID, chat_text, parse_mode="Markdown")

print("🔒 Booting up...")
bot.infinity_polling()
