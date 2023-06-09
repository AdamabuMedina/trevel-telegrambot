import logging

from telebot.types import Message,CallbackQuery
import json

from keyboards.inline.bot_filters import for_start, for_history
from states.states import HistoryState
from keyboards.inline.clean_history import clean_button
from loader import bot, db_history
from utils.logger import logger


@bot.callback_query_handler(func=None, start_config=for_start.filter(action='history'))
def start_history(call:CallbackQuery)->None:
    logger.info(' ')
    bot.set_state(call.from_user.id, HistoryState.count, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Сколько последних запросов Вам показать?(Не более 10)',
                     reply_markup=clean_button())


@bot.callback_query_handler(func=None, history_config=for_history.filter(clean='Очистить'))
def clean_history(call:CallbackQuery)->None:
    """
    Коллбэк очистки истории
    """
    logger.info(' ')
    db_history.delete_data(call.from_user.id)
    bot.send_message(call.message.chat.id, 'История очищена')


@bot.message_handler(commands=['history'])
def start_history(message: Message) -> None:
    """
    Начало истории
    """
    logger.info(f'user_id: {message.from_user.id}')
    bot.send_message(message.chat.id, 'Сколько последних запросов Вам показать?(Не более 10)',
                     reply_markup=clean_button())
    bot.set_state(message.from_user.id, HistoryState.count, message.chat.id)


@bot.message_handler(state=HistoryState.count, is_digit=True, count_digit=True)
def get_history(message: Message) -> None:
    '''
    Вывод истории поиска
    '''
    logger.info(f'user_id: {message.from_user.id} {message.text}')
    data = db_history.get_data(message.from_user.id, message.text)
    rows = data.fetchall()
    if rows:
        logger.info(f'user id: {message.from_user.id}')
        for row in rows:
            data, command, hotels = row[0], row[1], json.loads(row[2])
            bot.send_message(message.chat.id, f'{data} выполнили команду {command} и нашли: ')
            for _ in range(len(hotels)):
                for id, description in hotels.items():
                    bot.send_message(message.chat.id, f'{description}')
    else:
        logger.error(f'user id: {message.from_user.id}')
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, 'Ваша история пуста. Можете начать её! /start')


@bot.message_handler(state=HistoryState.count, is_digit=False)
def bad_digit(message: Message) -> None:
    """
    :param message: не число
    """
    logger.error(f'user_id: {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число больше 0')


@bot.message_handler(state=HistoryState.count, is_digit=True, count_digit=False)
def many_count(message: Message) -> None:
    """
    не тот диапазон
    """
    logger.error(f'user_id: {message.from_user.id}')
    bot.send_message(message.chat.id, 'Введите число в диапазоне от 1 до 10')