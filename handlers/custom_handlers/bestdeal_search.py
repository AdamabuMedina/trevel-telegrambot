from datetime import date
from telebot.types import InputMediaPhoto, Message, CallbackQuery
from handlers.custom_handlers.search_utils.button_callback import button_callback, callback_end_date, callback_start_date
from handlers.custom_handlers.search_utils.get_cities_request import get_cities_request

from utils.logger import logger
from loader import bot
from states.states import BestDealState
from keyboards.inline.bot_filters import for_search, for_button, for_photo, for_start
from keyboards.inline.calendar.inline_calendar import bot_get_keyboard_inline
from keyboards.inline.photo_keyboard import create_photo_keyboard
from utils.misc.hotel_search import get_properties_list
from utils.misc.hotel_photo_utils import get_photo_hotel
from handlers.custom_handlers.search_utils.start_search import start_search


@bot.callback_query_handler(func=None, start_config=for_start.filter(action='bestdeal'))
def start_bestdeal(call):
    start_search(call, BestDealState.cities, call.message.chat.id, 'Отлично! Выбран дополнительный критерий поиска. Выберите город для поиска.')

@bot.message_handler(commands=['bestdeal'])
def start_bestdeal(message):
    start_search(message, BestDealState.cities, message.chat.id, 'Отлично! Выбран дополнительный критерий поиска. Выберите город для поиска.')


@bot.message_handler(state=BestDealState.cities)
def start_highprice(message):
    get_cities_request(message, 'STAR_RATING_HIGHEST_FIRST', BestDealState.cities, 'best_state')

@bot.callback_query_handler(func=None, button_config=for_button.filter(state='best_state'))
def bestdeal_button_callback(call):
    button_callback(call, BestDealState, 'lowprice')


@bot.callback_query_handler(func=None, search_config=for_search.filter(state='dest_start_date'))
def bestdeal_callback_start_date(call):
    callback_start_date(call, BestDealState, 'lowprice')


@bot.callback_query_handler(func=None, search_config=for_search.filter(state='dest_end_date'))
def bestdeal_callback_end_date(call):
    callback_end_date(call, BestDealState)



@bot.message_handler(state=BestDealState.count_hotels, is_digit=True, count_digit=True, )
def get_photo_info(message: Message) -> None:
    """
    Запрос фотографий отелей. Запись количества отелей
    :param message: Количество отелей
    :return:None
    """
    logger.info(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, f'Буду выводить {message.text} отелей')
    bot.send_message(message.chat.id, f'Нужны фото отелей?',
                     reply_markup=create_photo_keyboard(state='best_state'))
    bot.set_state(message.from_user.id, BestDealState.photo, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'user_id {message.from_user.id} {message.text}')
        data['count_hotels'] = message.text


@bot.callback_query_handler(func=None, is_photo=for_photo.filter(photo='False', state='best_state'))
def not_photo(call: CallbackQuery) -> None:
    """
    :param call: Обработчик кнопки "фото не нужно"
    :return: None
    """
    logger.info(f'user_id {call.from_user.id}')
    bot.edit_message_text(f'Введите минимальную цену за ночь', call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, BestDealState.min_price, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        logger.info(f'user_id {call.from_user.id}')
        data['photo'] = ''


@bot.callback_query_handler(func=None, is_photo=for_photo.filter(photo='True', state='best_state'))
def get_photo_count_info(call: CallbackQuery) -> None:
    """
    Запрос количества фотографий отелей. Запись необходимости фото
    :return: None
    """
    logger.info(f'user_id {call.from_user.id}')
    bot.edit_message_text('Сколько фото выводить?(Не более 10)', call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, BestDealState.count_photo, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        logger.info(f'user_id {call.from_user.id}')
        data['photo'] = True


@bot.message_handler(state=BestDealState.count_photo, is_digit=True, count_digit=True)
def get_photo_info(message: Message) -> None:
    """
    Запись количества фото отелей. Здесь нужно вызывать функцию обработки
     информации(в которой будет отправка сообщения в чат с результатами)
    :param message:количества фото отелей
    :return: None
    """
    logger.info(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, f'Введите минимальную цену за ночь')
    bot.set_state(message.from_user.id, BestDealState.min_price, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'user_id {message.from_user.id} {message.text}')
        data['count_photo'] = message.text


@bot.message_handler(state=BestDealState.min_price, is_digit=True)
def get_min_price(message: Message) -> None:
    """
    Запись минимальной цены за ночь
    :param message: min_price
    :return: None
    """
    logger.info(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, f'Введите максимальную цену за ночь')
    bot.set_state(message.from_user.id, BestDealState.max_price, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'user_id {message.from_user.id} {message.text}')
        data['min_price'] = int(message.text)


@bot.message_handler(state=BestDealState.max_price, is_digit=True)
def get_max_price(message: Message) -> None:
    """
    Запись максимальной цены за ночь
    :param message: max_price
    :return: None
    """
    bot.send_message(message.chat.id, f'Введите расстояние до центра')
    bot.set_state(message.from_user.id, BestDealState.distance, message.chat.id)
    logger.info(f'user_id {message.from_user.id}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'user_id {message.from_user.id} {message.text}')
        data['max_price'] = int(message.text)
        if data['max_price'] < data['min_price']:
            logger.error(f'user_id {message.from_user.id} ввел цены наоборот')
            data['max_price'], data['min_price'] = data['min_price'], data['max_price']


@bot.message_handler(state=BestDealState.distance, is_digit=True)
def get_distance_to_centre(message: Message) -> None:
    """
    Запись дистанции до центра
    :param message: distance
    :return: None
    """
    logger.info(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Вывожу результаты')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'user_id {message.from_user.id} {message.text}')
        data['distance'] = float(message.text)
    user_is_ready(message)


@bot.message_handler(state=[BestDealState.distance, BestDealState.max_price, BestDealState.min_price],
                     is_digit=False)
def not_digit_message(message: Message) -> None:
    """
    Обработчик ошибки при вводе не int
    :return: None
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число больше 0!')


@bot.message_handler(state=BestDealState.count_hotels, is_digit=True, count_digit=False)
def dont_check_count(message: Message) -> None:
    """
    Ввели числа не в диапазоне
    :return:None
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число в диапазоне от 1 до 10')


def user_is_ready(message: Message) -> None:
    """
    Отсюда вызывается метод для обнаружения всех отелей. Здесь же будет записи в БД, может Pickle.
    Всё будет в модуле utils
    :return: None
    """
    logger.info(f'user_id {message.from_user.id}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        addition_str = {
            'priceMin': data['min_price'],
            'priceMax': data['max_price'],
            'landmarkIds': data['distance']
        }
        ex_str = get_properties_list(data['destid'], data["startday"], data["endday"], data['SortOrder'],
                                     data['locale'],
                                     data['currency'], data['count_hotels'], message.from_user.id,
                                     best_string=addition_str, command='bestdeal',
                                     total_days=abs(data['all_days'].days))
        if isinstance(ex_str, dict):
            logger.info(f'user_id {message.from_user.id}')
            for key, value in ex_str.items():
                bot.send_message(message.chat.id, f'{value}')
                if data['photo']:
                    logger.info(f'user_id {message.from_user.id}')
                    url_photo = get_photo_hotel(key, data['count_photo'])
                    if url_photo:
                        logger.info(f'user_id {message.from_user.id}')
                        bot.send_media_group(message.chat.id, media=[InputMediaPhoto(media=link) for link in url_photo])
                    else:
                        logger.error(f'user_id {message.from_user.id}')
                        bot.send_message(message.chat.id, 'Фото не нашлось')
        else:
            logger.error(f'user_id {message.from_user.id} {ex_str}')
            bot.send_message(message.chat.id, f'{ex_str}')
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=BestDealState.count_hotels, is_digit=False)
def count_incorrect(message: Message) -> None:
    """
    Ввел не цифру
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите количество в цифрах')


@bot.message_handler(state=BestDealState.count_photo, is_digit=False)
def count_incorrect(message: Message) -> None:
    """
    Ввел не цифру
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите количество в цифрах')


@bot.message_handler(state=BestDealState.count_photo, is_digit=True, count_digit=False)
def dont_check_count(message: Message) -> None:
    """
    Ввели числа не в диапазоне
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число в диапазоне от 1 до 10')
