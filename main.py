

from flask import Flask, request
import telebot

TOKEN = "8835467489:AAGPrrerDGEoz-V3fB-Qksnh8a9Pc4iccr4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Bank Details
BANK_DETAILS = (
    "🏦 *HNB Bank Details*\n"
    "Acc No: `082020197245`\n"
    "Name: MR Dilsh\n\n"
    "මුදල් තැන්පත් කළ පසු SMS එක මගින් ස්වයංක්‍රීයව Product එක ලැබෙනු ඇත."
)

# Product Catalog
PRODUCTS = {
    "kala": {"name": "🍁 කාල", "price": "3,500", "link": "https://your-product-link.com/kala"},
    "bhaga": {"name": "⚡ භාග", "price": "5,500", "link": "https://your-product-link.com/bhaga"},
    "gram": {"name": "🔥 ග්‍රෑම්", "price": "10,000", "link": "https://your-product-link.com/gram"}
}

@app.route('/')
def home():
    return "Bot is running successfully!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("🍁 කාල - Rs. 3,500", callback_data="buy_kala")
    btn2 = telebot.types.InlineKeyboardButton("⚡ භාග - Rs. 5,500", callback_data="buy_bhaga")
    btn3 = telebot.types.InlineKeyboardButton("🔥 ග්‍රෑම් - Rs. 10,000", callback_data="buy_gram")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)

    bot.send_message(
        message.chat.id,
        "👋 *සාදරයෙන් පිළිගනිමු!*\n\nකරුණාකර ඔබට අවශ්‍ය Package එක පහතින් තෝරන්න:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    pkg_key = call.data.split("_")[1]
    pkg = PRODUCTS.get(pkg_key)
    if pkg:
        msg = f"✅ *ඔබ තෝරාගත් Package එක:* {pkg['name']}\n💵 *මිල:* Rs. {pkg['price']}\n\n{BANK_DETAILS}"
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

@app.route('/sms-webhook', methods=['POST'])
def sms_webhook():
    data = request.json or {}
    return "SMS Received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))
