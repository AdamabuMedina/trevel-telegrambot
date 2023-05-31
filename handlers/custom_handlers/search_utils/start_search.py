from telebot.types import Message, CallbackQuery

from utils.logger import logger
from loader import bot

def start_search(call: CallbackQuery, state, chat_id, message: Message) -> None:
    logger.info(' ')
    bot.set_state(call.from_user.id, state, chat_id)
    bot.send_message(chat_id, message)