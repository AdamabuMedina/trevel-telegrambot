from telebot.types import InputMediaPhoto, Message, CallbackQuery
from handlers.custom_handlers.search_utils.button_callback import button_callback, callback_end_date, callback_start_date
from handlers.custom_handlers.search_utils.get_cities_request import get_cities_request
from handlers.custom_handlers.search_utils.handle_info import get_count_info, handle_invalid_input, process_photo_info, handle_photo_info, not_photo

from loader import bot
from utils.logger import logger
from states.states import HighPriceState
from keyboards.inline.bot_filters import for_search, for_button, for_photo, for_start
from utils.misc.hotel_search import get_properties_list
from utils.misc.hotel_photo_utils import get_photo_hotel
from handlers.custom_handlers.search_utils.start_search import start_search


@bot.callback_query_handler(func=None, start_config=for_start.filter(action='highprice'))
def start_highprice(call: CallbackQuery):
    start_search(call, HighPriceState.cities, call.message.chat.id, 'Отлично! Вы выбрали поиск топовых отелей. Выберите город для поиска.')

@bot.message_handler(commands=['highprice'])
def start_highprice(message: Message):
    start_search(message, HighPriceState.cities, message.chat.id, 'Отлично! Вы выбрали поиск топовых отелей. Выберите город для поиска.')


@bot.message_handler(state=HighPriceState.cities)
def start_highprice(message: Message):
    get_cities_request(message, 'PRICE_HIGHEST_FIRST', HighPriceState.cities, "High_state")


@bot.callback_query_handler(func=None, button_config=for_button.filter(state='High_state'))
def highprice_button_callback(call: CallbackQuery):
    button_callback(call, HighPriceState, 'highprice')


@bot.callback_query_handler(func=None, search_config=for_search.filter(state='high_start_date'))
def highprice_callback_start_date(call):
    callback_start_date(call, HighPriceState, 'highprice')


@bot.callback_query_handler(func=None, search_config=for_search.filter(state='high_end_date'))
def highprice_callback_end_date(call):
    callback_end_date(call, HighPriceState)


@bot.message_handler(state=HighPriceState.count_hotels, is_digit=True, count_digit=True)
def highprice_get_info(message: Message) -> None:
    handle_photo_info(message, HighPriceState, "High_state")


@bot.callback_query_handler(func=None, is_photo=for_photo.filter(photo='False', state='High_state'))
def highprice_not_photo(call: CallbackQuery) -> None:
    not_photo(call, func=user_is_ready)


@bot.callback_query_handler(func=None, is_photo=for_photo.filter(photo='True', state='High_state'))
def highprice_get_count_info(call: CallbackQuery) -> None:
    get_count_info(call, HighPriceState)


@bot.message_handler(state=HighPriceState.count_photo, is_digit=True, count_digit=True)
def highprice_get_photo_info(message: Message) -> None:
    process_photo_info(message, user_is_ready)


@bot.message_handler(state=HighPriceState.count_hotels)
def handle_high_price_count_hotels(message: Message) -> None:
    handle_invalid_input(message, is_digit=True, is_count=False)

@bot.message_handler(state=HighPriceState.count_photo)
def handle_high_price_count_photo(message: Message) -> None:
    handle_invalid_input(message, is_digit=True, is_count=False)

@bot.message_handler(state=HighPriceState.count_hotels, is_digit=False)
def handle_high_price_count_hotels_format(message: Message) -> None:
    handle_invalid_input(message, is_digit=False, is_count=True)

@bot.message_handler(state=HighPriceState.count_photo, is_digit=False)
def handle_high_price_count_photo_format(message: Message) -> None:
    handle_invalid_input(message, is_digit=False, is_count=True)


def user_is_ready(message: Message, user_id=None, chat_id=None) -> None:
    logger.info(f'user_id {message.from_user.id}')
    user_id = message.from_user.id if not user_id else user_id
    chat_id = message.chat.id if not chat_id else chat_id
    with bot.retrieve_data(user_id, chat_id) as data:
        ex_str = get_properties_list(
            data['destid'], data["startday"], data["endday"], data['SortOrder'],
            data['locale'], data['currency'], data['count_hotels'], user_id, command='higiprice',
            total_days=abs(data['all_days'].days)
        )
        if isinstance(ex_str, dict):
            logger.info(f'user_id {message.from_user.id, ex_str}')
            for key, value in ex_str.items():
                bot.send_message(chat_id, f'{value}')
                if data['photo']:
                    url_photo = get_photo_hotel(key, data['count_photo'])
                    if url_photo:
                        logger.info(f'user_id {message.from_user.id}')
                        bot.send_media_group(
                            chat_id, media=[InputMediaPhoto(media=link) for link in url_photo]
                        )
                    else:
                        logger.error(f'user_id {message.from_user.id}')
                        bot.send_message(chat_id, 'Фото не нашлось')
        else:
            bot.send_message(message.chat.id, f'{ex_str}')
            logger.error(f'user_id {message.from_user.id, ex_str}')
    bot.delete_state(user_id, chat_id)
