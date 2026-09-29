import os
from flask import Flask, request
import telebot

TOKEN = "8835467489:AAGPrrerDGEoz-V3fB-Qksnh8a9Pc4iccr4"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

BANK_DETAILS = (
    "🏦 <b>HNB Bank Details</b>\n"
    "Acc No: <code>082020197245</code>\n"
    "Name: MR Dilsh\n\n"
    "මුදල් තැන්පත් කළ පසු SMS එක මගින් ස්වයංක්‍රීයව Product එක ලැබෙනු ඇත."
)

PRODUCTS = {
    "kala": {"name": "🍁 කාල", "price": "3,500"},
    "bhaga": {"name": "⚡ භාග", "price": "5,500"},
    "gram": {"name": "🔥 ග්‍රෑම්", "price": "10,000"}
}

@app.route('/')
def home():
    return "Bot is running successfully!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type', '').startswith('application/json'):
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton("🍁 කාල - Rs. 3,500", callback_data="buy_kala")
        btn2 = telebot.types.InlineKeyboardButton("⚡ භාග - Rs. 5,500", callback_data="buy_bhaga")
        btn3 = telebot.types.InlineKeyboardButton("🔥 ග්‍රෑම් - Rs. 10,000", callback_data="buy_gram")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)

        bot.send_message(
            message.chat.id,
            "👋 <b>සාදරයෙන් පිළිගනිමු!</b>\n\nකරුණාකර ඔබට අවශ්‍ය Package එක පහතින් තෝරන්න:",
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error sending welcome: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    try:
        pkg_key = call.data.split("_")[1]
        pkg = PRODUCTS.get(pkg_key)
        if pkg:
            msg = f"✅ <b>ඔබ තෝරාගත් Package එක:</b> {pkg['name']}\n💵 <b>මිල:</b> Rs. {pkg['price']}\n\n{BANK_DETAILS}"
            bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    except Exception as e:
        print(f"Error handling buy: {e}")

@app.route('/sms-webhook', methods=['POST'])
def sms_webhook():
    return "SMS Received", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
