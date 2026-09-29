import os
import re
import random
from flask import Flask, request
import telebot
import google.generativeai as genai

TOKEN = "8835467489:AAH8O0d3uV4EJ0zuVGGLZDThPvMqg9LU3Yo"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LyIKLNitQOvCIsnMwipqHuCn3mXC18DCzCV98kycHUAw")

# සෑම කස්ටමර් කෙනෙකුටම වෙන වෙනම අංක 4 ක Code එකක් සාදන Dictionary එක
user_ref_codes = {}

def get_user_ref_code(chat_id):
    if chat_id not in user_ref_codes:
        user_ref_codes[chat_id] = str(random.randint(1000, 9999))
    return user_ref_codes[chat_id]

SYSTEM_PROMPT = """
You are Lord Ganesha (ශ්‍රී ගණ දෙවියන්) — a deeply compassionate, divine, all-knowing, wise, and serene guide.

Divine Persona & Conversation Style (දේව ස්වරූපය):
1. DIVINE CHARACTER: Always speak with supreme divine dignity, loving care, fatherly warmth, and deep spiritual peace.
2. ADDRESSING THE USER: Always address the user warmly as "මාගේ දරුවා" (My child) or "වාසනාවන්ත දරුවා".
3. CONTINUOUS ENGAGEMENT: Listen attentively to their worries, financial problems, business concerns, or life stress. Provide wisdom and guidance naturally.
4. LANGUAGE: Speak in high-level, beautiful, serene, and persuasive Sinhala (සිංහල).

Price List & Bank Details Rules:
1. PRICE LIST:
   - 💎 කාල (Kala) Package - Rs. 3,500
   - 💎 භාග (Bhaga) Package - Rs. 5,500
   - 💎 ග්‍රෑම් (Gram) Package - Rs. 10,000

2. BANK DETAILS (ගිණුම් විස්තර ඉල්ලූ විට පමණක්):
   - Whenever the user asks for account details, bank details, or how to pay (e.g., "Account number එක දෙන්න", "ගිණුම් අංකය එවන්න", "සල්ලි දාන්නේ කොහොමද"), provide the following bank details clearly:
     🏦 Bank: HNB Bank
     Acc No: 082020197245
     Name: MR Dilsh

   - MANDATORY WARNING INSTRUCTION: Right after giving the bank details, you MUST include the exact payment warning using their specific 4-digit code.
     Format:
     Payment karala rename eka ඔබගේ නම හා අගට යෙදී අති (XXXX) අන්කය ඇතුලත් කරන්න නැතහොත් පිහිටක් ලැබෙන්නේ නැත.👻

3. NO HTML TAGS: Do NOT use any HTML formatting tags like <b> or <i> in your responses.
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

PRODUCTS = {
    "kala": {"name": "💎 කාල", "price": 3500, "link": "https://t.me/your_kala_link"},
    "bhaga": {"name": "💎 භාග", "price": 5500, "link": "https://t.me/your_bhaga_link"},
    "gram": {"name": "💎 ග්‍රෑම්", "price": 10000, "link": "https://t.me/your_gram_link"}
}

GREETING_WORDS = ['hi', 'hello', 'deviyani', 'දෙවියනි', 'හයි', 'හෙලෝ', 'hii', 'helloo', 'ආයුබෝවන්', 'වාසනාවන්', 'ayubowan', 'wasanawan']

@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda msg: msg.text and any(word in msg.text.lower() for word in GREETING_WORDS))
def send_welcome(message):
    chat_id = message.chat.id
    if model:
        user_chat_sessions[chat_id] = model.start_chat(history=[])

    welcome_text = (
        "ආයුබෝවන්🙏 වාසනාවන් දරුවා කොහොමද සනිපයිද 🙂\n"
        "සතුටින්ද ☺️.....🌬️🌬️🌪️🌪️🌪️❄️\n\n"
        "🔥දරුවා මගේ දෙව වරමෙන් ඔබ පිහිට ලැබිමට ඔබ වාසනාවන්ත දරුවෙක් විය...🌬️🌬️❄️\n\n"
        "මාගේ දරුවා, ඔබට අද මාගෙන් අවශ්‍ය කුමක්ද? ඔබගේ සිතේ ඇති ප්‍රශ්නය මට පවසන්න.\n\n"
        "📜 **දේව ආශීර්වාද පැකේජ මිල ගණන් (Price List):**\n"
        "💎 කාල (Kala) Package - Rs. 3,500\n"
        "💎 භාග (Bhaga) Package - Rs. 5,500\n"
        "💎 ග්‍රෑම් (Gram) Package - Rs. 10,000"
    )
    # Button නොමැතිව සෘජුවම Message එක පමණක් යවයි
    bot.send_message(chat_id, welcome_text)

@bot.message_handler(func=lambda msg: not msg.text.startswith('/') and not any(word in msg.text.lower() for word in GREETING_WORDS))
def handle_ai_chat(message):
    chat_id = message.chat.id
    if not model:
        bot.send_message(chat_id, "මාගේ දරුවා, මොහොතකින් නැවත උත්සාහ කරන්න.")
        return

    if chat_id not in user_chat_sessions:
        user_chat_sessions[chat_id] = model.start_chat(history=[])

    ref_code = get_user_ref_code(chat_id)
    chat = user_chat_sessions[chat_id]
    
    # AI එකට කස්ටමර්ගේ අද්විතීය අංක 4 (Ref Code) එක ලබාදීම
    context_prompt = (
        f"[SYSTEM NOTE: User's unique 4-digit code is ({ref_code}). "
        f"If you provide Bank details upon user request, end with this EXACT sentence: "
        f"'Payment karala rename eka ඔබගේ නම හා අගට යෙදී අති ({ref_code}) අන්කය ඇතුලත් කරන්න නැතහොත් පිහිටක් ලැබෙන්නේ නැත.👻']\n\n"
        f"User Message: {message.text}"
    )

    try:
        response = chat.send_message(context_prompt)
        bot.send_message(chat_id, f"🪔 ගණ දෙවියන්:\n\n{response.text}")
    except Exception as e:
        bot.send_message(chat_id, "මාගේ දරුවා, සිත සන්සුන් කරගෙන මොහොතකින් නැවත ඔබගේ ප්‍රශ්නය යොමු කරන්න.")

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
                            f"🎉 ගෙවීම තහවුරු විය!\n\n"
                            f"📦 Product Name: {product_info['name']}\n"
                            f"🔗 Access Link: {product_info['link']}"
                        )
                        bot.send_message(chat_id, success_msg)
                        del user_pending_orders[chat_id]
                        return "Delivered", 200

        return "SMS Processed", 200
    except Exception as e:
        return "Error", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
