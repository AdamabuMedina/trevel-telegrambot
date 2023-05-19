from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.bot_filters import for_photo
from utils.logger import logger


def create_photo_keyboard(state: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с двумя кнопками для выбора необходимости фото.
    :param state: состояние
    :return: клавиатура
    """
    keyboard = InlineKeyboardMarkup()
    try:
        keyboard.add(
            InlineKeyboardButton('Фото нужны', callback_data=for_photo.new(photo='True', state=state)),
            InlineKeyboardButton('Фото не нужны', callback_data=for_photo.new(photo='False', state=state))
        )
        logger.info(' ')
    except ValueError:
        logger.exception()
    return keyboard
