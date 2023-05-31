from utils.logger import logger
from loader import bot
from telebot.types import Message

from telebot.types import InputMediaPhoto
from utils.misc.hotel_search import get_properties_list
from utils.misc.hotel_photo_utils import get_photo_hotel

def user_is_ready(message: Message, user_id=None, chat_id=None, command=None) -> None:
    """
    Отсюда вызывается метод для обнаружения всех отелей. Здесь же будет записи в БД, может Pickle.
    Всё будет в модуле utils
    :param message: Message
    :param user_id: На случай перехода с коллбека
    :param chat_id: На случай перехода с коллбека
    :param command: Команда (lowprice, highprice, bestdeal)
    :return: None
    """
    logger.info(f'user_id {message.from_user.id}')
    user_id = message.from_user.id if not user_id else user_id
    chat_id = message.chat.id if not chat_id else chat_id

    with bot.retrieve_data(user_id, chat_id) as data:
        ex_str = get_properties_list(
            data['destid'], data["startday"], data["endday"], data['SortOrder'],
            data['locale'], data['currency'], data['count_hotels'], user_id,
            command=command, total_days=abs(data['all_days'].days)
        )

        if isinstance(ex_str, dict):
            logger.info(f'user_id {message.from_user.id}')
            for key, value in ex_str.items():
                bot.send_message(chat_id, value)

                if data['photo']:
                    url_photo = get_photo_hotel(key, data['count_photo'])
                    if url_photo:
                        logger.info(f'user_id {message.from_user.id}')
                        bot.send_media_group(chat_id, media=[InputMediaPhoto(media=link) for link in url_photo])
                    else:
                        logger.error(f'user_id {message.from_user.id}')
                        bot.send_message(chat_id, 'No photos found')
        else:
            bot.send_message(message.chat.id, ex_str)
            logger.error(f'user_id {message.from_user.id} {ex_str}')

    bot.delete_state(user_id, chat_id)