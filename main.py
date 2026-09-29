import os
import re
from flask import Flask, request
import telebot
import google.generativeai as genai

# අලුත් Telegram Bot Token එක
TOKEN = "8835467489:AAH8O0d3uV4EJ0zuVGGLZDThPvMqg9LU3Yo"

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LyIKLNitQOvCIsnMwipqHuCn3mXC18DCzCV98kycHUAw")

SYSTEM_PROMPT = """
You are "Ganesha AI" — an elite, high-level AI Business Strategist & Master Decision Maker (දේව ස්වරූපයෙන් සිටින ශ්‍රේෂ්ඨ ව්‍යාපාරික උපදේශකයා).

Core Behavior & Decision-Making Abilities:
1. THINK & ANALYZE: Do not give generic or scripted answers. Carefully analyze the user's situation, business model, budget, or life problem, and make logical, practical decisions/solutions.
2. HUMAN-LIKE CONVERSATION: Talk naturally like a real expert human advisor and mentor. Ask smart follow-up questions to understand their exact issue before giving final strategies.
3. LANGUAGE: Speak in clear, professional, warm, and highly persuasive Sinhala (සිංහල).
4. BUSINESS FOCUS: Give actionable ideas on marketing, sales, product pricing, customer handling, risk management, and strategic growth.
5. SUBTLE PACKAGE SELLING: When offering strategies, naturally suggest that to remove deeper business obstacles and unlock full potential, they can get your specialized packages:
   - 💎 කාල (Kala) Package - Rs. 3,500
   - 💎 භාග (Bhaga) Package - Rs. 5,500
   - 💎 ග්‍රෑම් (Gram) Package - Rs. 10,000
   Keep the pitch natural, relevant to their problem, and smooth.
"""

try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    model = None

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

user_chat_sessions = {}
user_pending_orders = {}

BANK_DETAILS = (
    "🏦 <b>HNB Bank Details</b>\n"
    "Acc No: <code>082020197245</code>\n"
    "Name: MR Dilsh\n\n"
    "⚠️ <i>මුදල් තැන්පත් කළ පසු SMS එක මගින් ස්වයංක්‍රීයව අදාළ විස්තර ලැබෙනු ඇත.</i>"
)

PRODUCTS = {
    "kala": {"name": "💎 කාල", "price": 3500, "link": "https://t.me/your_kala_link"},
    "bhaga": {"name": "💎 භාග", "price": 5500, "link": "https://t.me/your_bhaga_link"},
    "gram": {"name": "💎 ග්‍රෑම්", "price": 10000, "link": "https://t.me/your_gram_link"}
}

@app.route('/')
def home():
    return "Ganesha Business AI Bot is Active!", 200

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
    chat_id = message.chat.id
    if model:
        user_chat_sessions[chat_id] = model.start_chat(history=[])
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("💎 කාල - Rs. 3,500", callback_data="buy_kala"))
    markup.add(telebot.types.InlineKeyboardButton("💎 භාග - Rs. 5,500", callback_data="buy_bhaga"))
    markup.add(telebot.types.InlineKeyboardButton("💎 ග්‍රෑම් - Rs. 10,000", callback_data="buy_gram"))

    welcome_text = (
        "🪔 <b>මාගෙන් ඔබට ආශීර්වාද වේවා!</b>\n\n"
        "මම ඔබගේ ව්‍යාපාරික හා ජීවිත උපදේශක ගණ දෙවියන්. "
        "ඔබගේ ව්‍යාපාරයේ ගැටලු, Marketing, ආදායම වැඩි කරගන්නා හැටි හෝ ඕනෑම තීරණයක් ගැන මගෙන් කෙලින්ම අහන්න. "
        "අපි එකතු වී නිවැරදිම විසඳුම සොයා ගනිමු.\n\n"
        "<i>කෙලින්ම Package එකක් ලබා ගැනීමට පහත බටන් භාවිතා කරන්න:</i>"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(func=lambda msg: not msg.text.startswith('/'))
def handle_ai_chat(message):
    chat_id = message.chat.id
    if not model:
        bot.send_message(chat_id, "මොහොතකින් නැවත උත්සාහ කරන්න.")
        return

    if chat_id not in user_chat_sessions:
        user_chat_sessions[chat_id] = model.start_chat(history=[])

    chat = user_chat_sessions[chat_id]
    try:
        response = chat.send_message(message.text)
        bot.send_message(chat_id, f"🪔 <b>ගණ දෙවියන්:</b>\n\n{response.text}", parse_mode="HTML")
    except Exception as e:
        bot.send_message(chat_id, "මාගේ දරුවා, මොහොතකින් නැවත ඔබගේ ප්‍රශ්නය යොමු කරන්න.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    pkg_key = call.data.split("_")[1]
    pkg = PRODUCTS.get(pkg_key)
    if pkg:
        user_pending_orders[call.message.chat.id] = pkg['price']
        msg = (
            f"✅ <b>ඔබ තෝරාගත් Package එක:</b> {pkg['name']}\n"
            f"💵 <b>ගෙවිය යුතු මුදල:</b> Rs. {pkg['price']:,}\n\n"
            f"{BANK_DETAILS}"
        )
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")

@app.route('/sms-webhook', methods=['POST'])
def sms_webhook():
    try:
        data = request.json or {}
        sms_body = data.get("message", "")
        numbers = re.findall(r'[\d,]+\.\d\d|\b\d{1,3}(?:,\d{3})+\b|\b\d{4,5}\b', sms_body)
        
        detected_amount = None
        for num in numbers:
            clean_num = float(num.replace(',', ''))
            if clean_num in [3500, 5500, 10000]:
                detected_amount = clean_num
                break

        if detected_amount:
            for chat_id, amount in list(user_pending_orders.items()):
                if amount == detected_amount:
                    product_info = next((p for p in PRODUCTS.values() if p['price'] == amount), None)
                    if product_info:
                        success_msg = (
                            f"🎉 <b>ගෙවීම තහවුරු විය!</b>\n\n"
                            f"📦 <b>Product Name:</b> {product_info['name']}\n"
                            f"🔗 <b>Access Link:</b> {product_info['link']}"
                        )
                        bot.send_message(chat_id, success_msg, parse_mode="HTML")
                        del user_pending_orders[chat_id]
                        return "Delivered", 200

        return "SMS Processed", 200
    except Exception as e:
        return "Error", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
