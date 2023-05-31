from typing import Optional, Union
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.bot_filters import for_button
from utils.logger import logger

def create_city_keyboard(dict_buttons: dict, state: str) -> Optional[Union[str, InlineKeyboardMarkup]]:
    """
    Создает InlineKeyboardMarkup с кнопками городов.

    :param dict_buttons: словарь. Ключ - название города, значение - Destid
    :param state: состояние пользователя
    :return: InlineKeyboardMarkup или None, если не найдены подходящие города
    """
    logger.info('Creating city keyboard')
    if not dict_buttons:
        logger.error('No suitable cities found')
        return 'Не нашел подходящего города'

    keyboard = InlineKeyboardMarkup(row_width=1)
    try:
        keyboard.add(*[
            InlineKeyboardButton(
                name,
                callback_data=for_button.new(name=name[:10], destid=int(data), state=state)
            )
            for name, data in dict_buttons.items() if len(data) <= 10
        ])
    except (ValueError, KeyError):
        logger.exception('Unknown error occurred while determining cities')
        return 'Неизвестная ошибка при определении городов. /start'

    return keyboard
