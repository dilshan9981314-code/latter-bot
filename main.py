import os
import telebot
from flask import Flask, request

TOKEN = '8835467489:AAGPrrerDGEoz-V3fB-Qksnh8a9Pc4iccr4'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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
