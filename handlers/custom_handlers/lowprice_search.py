from datetime import date

from telebot.types import InputMediaPhoto, Message, CallbackQuery
from handlers.custom_handlers.search_utils.button_callback import button_callback
from handlers.custom_handlers.search_utils.get_cities_request import get_cities_request

from utils.logger import logger
from loader import bot
from states.states import LowPriceState
from keyboards.inline.bot_filters import for_search, for_button, for_photo, for_start
from keyboards.inline.calendar.inline_calendar import bot_get_keyboard_inline
from keyboards.inline.photo_keyboard import create_photo_keyboard
from utils.misc.hotel_search import get_properties_list
from utils.misc.hotel_photo_utils import get_photo_hotel
from handlers.custom_handlers.search_utils.start_search import start_search


@bot.callback_query_handler(func=None, start_config=for_start.filter(action='lowprice'))
def start_lowprice(call):
     start_search(call, LowPriceState.cities, call.message.chat.id, 'Отлично! Вы выбрали поиск недорогих отелей. Выберите город для поиска.')

@bot.message_handler(commands=['lowprice'])
def start_lowprice(message):
    start_search(message, LowPriceState.cities, message.chat.id, 'Отлично! Вы выбрали поиск недорогих отелей. Выберите город для поиска.')


@bot.message_handler(state=LowPriceState.cities)
def start_highprice(message):
    get_cities_request(message, 'PRICE', LowPriceState.cities)


@bot.callback_query_handler(func=None, button_config=for_button.filter(state='low_city'))
def lowprice_button_callback(call):
    button_callback(call, LowPriceState, 'lowprice')


@bot.callback_query_handler(func=None, search_config=for_search.filter(state='low_start_date'))
def callback_start_date(call: CallbackQuery) -> None:
    """
    :param call: Выбор пользователя начала поездки
    """
    logger.info(f'user_id {call.from_user.id}')
    bot.set_state(call.from_user.id, LowPriceState.end_date, call.message.chat.id)
    data = for_search.parse(callback_data=call.data)
    my_exit_date = date(year=int(data['year']), month=int(data['month']), day=int(data['day']))
    bot.send_message(call.message.chat.id, 'Выберите дату уезда',
                     reply_markup=bot_get_keyboard_inline(command='lowprice', state='low_end_date'))
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['startday'] = my_exit_date
        logger.info(f'user_id {call.from_user.id, my_exit_date}')
        bot.edit_message_text(f'Дата заезда: {my_exit_date}', call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, search_config=for_search.filter(state='low_end_date'))
def callback_end_date(call: CallbackQuery) -> None:
    """
    :param call: Окончание поездки
    """
    logger.info(f'user_id {call.from_user.id}')
    data = for_search.parse(callback_data=call.data)
    my_exit_date = date(year=int(data['year']), month=int(data['month']), day=int(data['day']))
    bot.set_state(call.from_user.id, LowPriceState.count_hotels, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Сколько отелей выводить? ( не более 10)')
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['endday'] = my_exit_date
        data['all_days'] = data['endday'] - data['startday']
        logger.info(f'user_id {call.from_user.id, my_exit_date}')
        if data['startday'] > data['endday']:
            logger.error(f'user_id {call.from_user.id}')
            data['startday'], data['endday'] = data['endday'], data['startday']
        bot.edit_message_text(f'Дата выезда: {my_exit_date}', call.message.chat.id, call.message.id)


@bot.message_handler(state=LowPriceState.count_hotels, is_digit=True, count_digit=True, )
def get_photo_info(message: Message) -> None:
    """
    Запрос фотографий отелей. Запись количества отелей
    """
    logger.info(f'user_id {message.from_user.id}')
    bot.set_state(message.from_user.id, LowPriceState.photo, message.chat.id)
    bot.send_message(message.chat.id, f'Буду выводить {message.text} отелей')
    bot.send_message(message.chat.id, f'Нужны фото отелей?',
                     reply_markup=create_photo_keyboard(state='low_photo'))
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_hotels'] = message.text


@bot.callback_query_handler(func=None, is_photo=for_photo.filter(photo='False', state='low_photo'))
def not_photo(call: CallbackQuery) -> None:
    logger.info(f'user_id {call.from_user.id}')
    bot.edit_message_text(f'Вывожу результаты', call.message.chat.id, call.message.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['photo'] = ''
    user_is_ready(call.message, call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(func=None, is_photo=for_photo.filter(photo='True', state='low_photo'))
def get_photo_count_info(call: CallbackQuery) -> None:
    """
    Запрос количества фотографий отелей. Запись необходимости фото
    """
    logger.info(f'user_id {call.from_user.id}')
    bot.edit_message_text('Сколько фото выводить?(Не более 10)', call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, LowPriceState.count_photo, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['photo'] = True


@bot.message_handler(state=LowPriceState.count_photo, is_digit=True, count_digit=True)
def get_photo_info(message: Message) -> None:
    """
    Запись количества фото отелей. Здесь нужно вызывать функцию обработки
     информации(в которой будет отправка сообщения в чат с результатами)
    """
    logger.info(f'user_id {message.from_user.id, message.text}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = message.text
        bot.send_message(message.chat.id, 'Вывожу отели...')
    user_is_ready(message)


@bot.message_handler(state=LowPriceState.count_hotels, is_digit=True, count_digit=False)
def dont_check_count(message: Message) -> None:
    """
    Ввели числа не в диапазоне
    :param message:
    :return:
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число в диапазоне от 1 до 10')


@bot.message_handler(state=LowPriceState.count_hotels, is_digit=False)
def count_incorrect(message: Message) -> None:
    """
    Ввел не цифру
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите количество в цифрах')


@bot.message_handler(state=LowPriceState.count_photo, is_digit=False)
def count_incorrect(message: Message) -> None:
    """
    Ввел не цифру
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите количество в цифрах')


@bot.message_handler(state=LowPriceState.count_photo, is_digit=True, count_digit=False)
def dont_check_count(message: Message) -> None:
    """
    Ввели числа не в диапазоне
    """
    logger.error(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число в диапазоне от 1 до 10')


def user_is_ready(message: Message, user_id=None, chat_id=None) -> None:
    """
    Отсюда вызывается метод для обнаружения всех отелей. Здесь же будет записи в БД, может Pickle.
    Всё будет в модуле utils
    :param message: Message
    :param user_id: На случай перехода с коллбека
    :param chat_id: На случай перехода с коллбека
    :return:
    """
    logger.info(f'user_id {message.from_user.id}')
    user_id = message.from_user.id if not user_id else user_id
    chat_id = message.chat.id if not chat_id else chat_id

    with bot.retrieve_data(user_id, chat_id) as data:
        ex_str = get_properties_list(data['destid'], data["startday"], data["endday"], data['SortOrder'],
                                     data['locale'],
                                     data['currency'], data['count_hotels'], user_id, command='lowprice',
                                     total_days=abs(data['all_days'].days))

        if isinstance(ex_str, dict):
            logger.info(f'user_id {message.from_user.id} {ex_str}')
            for key, value in ex_str.items():
                logger.info(f'user_id {message.from_user.id}')
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
