import telebot
from flask import Flask, request
import os

API_TOKEN = os.getenv('API_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
user_state = {}

LANGS = {
    'fa': {
        'start': 'زبان را انتخاب کن:',
        'choose_pair': 'جفت ارز را انتخاب کن:',
        'signal': '📈 سیگنال برای {pair}:\n📊 خرید در {price}'
    },
    'en': {
        'start': 'Choose your language:',
        'choose_pair': 'Choose a currency pair:',
        'signal': '📈 Signal for {pair}:\n📊 Buy at {price}'
    }
}

PAIRS = ['EURUSD', 'GBPUSD', 'XAUUSD']

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('فارسی', 'English')
    bot.send_message(message.chat.id, LANGS['en']['start'], reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ['فارسی', 'English'])
def set_lang(msg):
    lang = 'fa' if msg.text == 'فارسی' else 'en'
    user_state[msg.chat.id] = {'lang': lang}
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in PAIRS:
        markup.add(p)
    bot.send_message(msg.chat.id, LANGS[lang]['choose_pair'], reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in PAIRS)
def send_signal(msg):
    state = user_state.get(msg.chat.id)
    if not state:
        return bot.send_message(
            msg.chat.id,
            "Please /start first" if not state or state.get('lang') == 'en' else "لطفاً ابتدا /start را بزن"
        )
    lang = state['lang']
    price = round(1.0000 + os.urandom(1)[0] / 100, 4)
    bot.send_message(msg.chat.id, LANGS[lang]['signal'].format(pair=msg.text, price=price))

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return 'ok'
    return 'running'

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
