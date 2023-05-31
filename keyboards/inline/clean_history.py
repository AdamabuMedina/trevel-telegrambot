from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.bot_filters import for_history


def clean_button() -> InlineKeyboardMarkup:
    """
    Кнопка очистки истории
    :return: Кнопка очистки
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Очистить историю', callback_data=for_history.new(clean='Очистить')))
    return keyboard