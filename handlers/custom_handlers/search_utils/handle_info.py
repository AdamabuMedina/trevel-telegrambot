from telebot.types import Message, CallbackQuery

from utils.logger import logger
from loader import bot
from keyboards.inline.photo_keyboard import create_photo_keyboard


def handle_photo_info(message: Message, state, state_name) -> None:
    """
    Обработка запроса для получения информации и фотографий отелей
    :param message: Количество отелей
    :return: None
    """
    logger.info(f'user_id {message.from_user.id}')
    bot.send_message(message.chat.id, f'Буду выводить {message.text} отелей')
    bot.send_message(message.chat.id, 'Нужны фото отелей?',
                     reply_markup=create_photo_keyboard(state=state_name))
    bot.set_state(message.from_user.id, state.photo, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'user_id {message.from_user.id} {message.text}')
        data['count_hotels'] = message.text


def not_photo(call: CallbackQuery, state=None, func=None) -> None:
    logger.info(f'user_id {call.from_user.id}')
    if state != None:
        bot.edit_message_text(f'Введите минимальную цену за ночь', call.message.chat.id, call.message.id)
        bot.set_state(call.from_user.id, state.min_price, call.message.chat.id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            logger.info(f'user_id {call.from_user.id}')
            data['photo'] = ''
    else:
        bot.edit_message_text('Вывожу результаты', call.message.chat.id, call.message.id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['photo'] = ''
        func(call.message, call.from_user.id, call.message.chat.id)


def get_count_info(call: CallbackQuery, state) -> None:
    """
    Запрос количества фотографий отелей. Запись необходимости фото
    """
    logger.info(f'user_id {call.from_user.id}')
    bot.edit_message_text('Сколько фото выводить?(Не более 10)', call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, state.count_photo, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['photo'] = True