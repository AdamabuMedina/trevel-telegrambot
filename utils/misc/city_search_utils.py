import re
from typing import Optional, Union
import requests
import json
from telebot.types import InlineKeyboardMarkup
from config_data.config import url_from_cities, headers
from keyboards.inline.city_keyboard import create_city_keyboard
from utils.logger import logger


def get_dest_id(city: str, locale: str, currency: str, state: str) -> Optional[Union[str, InlineKeyboardMarkup]]:
    """
    Получает идентификаторы городов по заданным параметрам.

    :param state: Состояние пользователя
    :param city: Город поиска
    :param locale: Локаль для выбранного языка
    :param currency: Валюта для выбранной локали
    :return: InlineKeyboardMarkup or None
    """
    logger.info(' ')
    querystring = {"query": city, "locale": locale, "currency": currency}
    try:
        response = requests.get(url_from_cities, headers=headers, params=querystring)
        if response:
            logger.info('response')
            data = json.loads(response.text)
            entries = list(filter(lambda i_data: i_data['group'] == 'CITY_GROUP', data['suggestions']))[0]['entities']
            if not entries:
                logger.error('Нет подходящих вариантов по вашему запросу')
                return 'Нет подходящих вариантов по вашему запросу'
            else:
                temp_dict_button_hotel = {}
                for i_hotel in entries:
                    if i_hotel['type'] == 'CITY':
                        current_city = re.sub(r'<[^.]*>\b', '', i_hotel['caption'])
                        current_city = re.sub(r'<[^.]*>', '', current_city)
                        call_dat = i_hotel["destinationId"]
                        temp_dict_button_hotel[current_city] = call_dat
                return create_city_keyboard(temp_dict_button_hotel, state)
    except Exception as e:
        logger.exception(e)
        return 'No response'
