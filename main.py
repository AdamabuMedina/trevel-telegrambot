import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['hello-world'])
@bot.message_handler(func=lambda message: message.text == 'Привет'.lower())
def hello_message(message):
    bot.reply_to(message, 'Привет, мир!')

bot.polling()