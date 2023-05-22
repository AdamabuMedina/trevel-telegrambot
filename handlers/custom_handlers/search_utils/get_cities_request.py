from utils.logger import logger
from loader import bot
from utils.misc.city_search_utils import get_dest_id
from telebot.types import  Message


def get_cities_request(message: Message, sort_order, state) -> None:
    logger.info(f'user_id {message.from_user.id}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['id'] = message.from_user.id
        data['SortOrder'] = sort_order
        data['locale'] = 'ru_RU'
        data['currency'] = 'USD'
        data['city'] = message.text
        logger.info(f'user_id {message.from_user.id}')
        keyboard = get_dest_id(
            message.text, data['locale'], data['currency'], state='High_state')
        if keyboard:
            logger.info(f'user_id {message.from_user.id} {message.text}')
            bot.send_message(
                message.chat.id, 'Выберите подходящий город:', reply_markup=keyboard)
        else:
            logger.error(f'user_id {message.from_user.id}')
            bot.send_message(
                message.chat.id, 'Нет подходящего варианта. Попробуйте еще раз.')
            bot.set_state(message.from_user.id, state)
