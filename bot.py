import telebot
from telebot import types

# ---------------------------------------------------------
# CONFIGURATION (Keep your actual details here)
API_TOKEN = '9264444554:AAGo4NerLhRSdaoLFFf_vsMOwFnnOc5F02o'
MY_CHAT_ID = 9283320303 
# ---------------------------------------------------------

bot = telebot.TeleBot(API_TOKEN)

# A simple dictionary to keep track of users who are currently typing their ID
user_states = {}

# 1. Handle the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == MY_CHAT_ID:
        bot.send_message(MY_CHAT_ID, "🤖 Bot Online! Standing by for referral ID validations.")
    else:
        # Create the custom layout menu button
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        validation_button = types.KeyboardButton("🔐 Submit Referral ID Details")
        markup.add(validation_button)
        
        welcome_text = (
            "Hello! Welcome to our secure verification hub.\n\n"
            "⚠️ You must submit your referral ID details for validation before any business transaction can take place."
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# 2. Process all incoming messages and workflows
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # IF THE MESSAGE IS FROM YOU (THE ADMIN)
    if message.chat.id == MY_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.forward_from:
            original_user_id = message.reply_to_message.forward_from.id
            try:
                bot.send_message(original_user_id, message.text)
            except Exception:
                bot.send_message(MY_CHAT_ID, "❌ Failed to send response. The user may have blocked the bot.")
        else:
            bot.send_message(MY_CHAT_ID, "⚠️ Remember to use the 'Reply' feature on the forwarded alert to talk back to this user.")
    
    # IF A USER CLICKS THE SUBMIT BUTTON
    elif message.text == "🔐 Submit Referral ID Details":
        # Mark this specific user as "waiting for ID input"
        user_states[message.chat.id] = "waiting_for_id"
        
        instruction_text = (
            "📝 **Please type and send your Referral ID details below:**\n\n"
            "Once submitted, our administrator will validate your information before starting your business transaction."
        )
        bot.send_message(message.chat.id, instruction_text, parse_mode="Markdown")
        
    # IF THE USER SENDS THEIR REFERRAL ID
    elif user_states.get(message.chat.id) == "waiting_for_id":
        # Clear their waiting status since they provided it
        user_states[message.chat.id] = None
        
        # Confirm receipt to the user
        bot.send_message(message.chat.id, "✅ Thank you! Your Referral ID has been submitted for validation. Please wait while the administrator reviews it.")
        
        # Forward the Referral ID to you as an explicit alert
        alert_text = (
            f"🔔 **NEW VALIDATION REQUEST**\n"
            f"👤 User: @{message.from_user.username or 'No Username'}\n"
            f"🆔 Telegram ID: `{message.chat.id}`\n\n"
            f"🔑 **Submitted Referral ID:**\n{message.text}\n\n"
            f"👉 *To respond, simply reply directly to this forwarded message.*"
        )
        
        try:
            # We natively forward the message so you can reply to it directly,
            # but also send a text block summarizing what it is.
            bot.send_message(MY_CHAT_ID, alert_text, parse_mode="Markdown")
            bot.forward_message(MY_CHAT_ID, message.chat.id, message.message_id)
        except Exception:
            bot.send_message(MY_CHAT_ID, alert_text, parse_mode="Markdown")

    # GENERAL INCOMING CHAT TRAFFIC
    else:
        try:
            bot.forward_message(MY_CHAT_ID, message.chat.id, message.message_id)
        except Exception:
            bot.send_message(MY_CHAT_ID, f"📩 Message from User ID {message.chat.id}:\n\n{message.text}")

print("🔒 Secure verification bot is booting up...")
bot.infinity_polling()
