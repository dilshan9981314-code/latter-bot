import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, jsonify

TOKEN = '8835467489:AAGPrrerDGEoz-V3fB-Qksnh8a9Pc4iccr4'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 🔗 ඔබගේ Digital Products වල Download Links මෙතැනට ලබාදෙන්න
PRODUCTS = {
    "3500": "https://your-digital-product-link.com/kala",
    "5500": "https://your-digital-product-link.com/bhaga",
    "10000": "https://your-digital-product-link.com/gram"
}

# Pending Orders මතක තබාගැනීමට
pending_users = {}

BANK_DETAILS = (
    "🏦 **ගෙවීම් සිදුකිරීම සඳහා බැංකු විස්තර:**\n\n"
    "• Bank: **HNB Bank**\n"
    "• Acc No: **082020197245**\n"
    "• Name: **MR Dilsh**\n\n"
    "⚠️ මුදල් ගෙවූ සැනින් පද්ධතිය මගින් එය Auto Verify වී ඔබගේ Digital Product එක මෙතැනට ලැබෙනු ඇත."
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🍁 කාල - Rs. 3,500", callback_data="pkg_3500"),
        InlineKeyboardButton("⚡ භාග - Rs. 5,500", callback_data="pkg_5500"),
        InlineKeyboardButton("🔥 ග්‍රෑම් - Rs. 10,000", callback_data="pkg_10000")
    )
    bot.send_message(
        message.chat.id, 
        "👋 සාදරයෙන් පිළිගන්නවා!\n\nකරුණාකර ඔබට අවශ්‍ය Package එක තෝරන්න:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "pkg_3500":
        pending_users[chat_id] = "3500"
        bot.send_message(chat_id, f"✅ **තෝරාගත් Package එක: කාල (Rs. 3,500)**\n\n{BANK_DETAILS}", parse_mode="Markdown")
    elif call.data == "pkg_5500":
        pending_users[chat_id] = "5500"
        bot.send_message(chat_id, f"✅ **තෝරාගත් Package එක: භාග (Rs. 5,500)**\n\n{BANK_DETAILS}", parse_mode="Markdown")
    elif call.data == "pkg_10000":
        pending_users[chat_id] = "10000"
        bot.send_message(chat_id, f"✅ **තෝරාගත් Package එක: ග්‍රෑම් (Rs. 10,000)**\n\n{BANK_DETAILS}", parse_mode="Markdown")

# -------------------------------------------------------------
# 🤖 MacroDroid Webhook (SMS එක ආපු ගමන් Auto Product එක යවන කොටස)
# -------------------------------------------------------------
@app.route('/sms-webhook', methods=['POST'])
def sms_webhook():
    data = request.json or {}
    sms_text = data.get('sms', '')

    for chat_id, amount in list(pending_users.items()):
        if amount in sms_text or f"{int(amount):,}" in sms_text:
            product_link = PRODUCTS.get(amount)
            bot.send_message(
                chat_id, 
                f"🎉 **ගෙවීම සාර්ථකව තහවුරු විය!**\n\nඔබගේ Digital Product එක ලබාගැනීමට පහත Link එක ක්ලික් කරන්න:\n{product_link}"
            )
            del pending_users[chat_id]
            return jsonify({"status": "success", "message": "Product Delivered"}), 200

    return jsonify({"status": "ignored", "message": "No matching user"}), 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is running successfully!"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
