import json
from typing import List, Optional, Union

import requests
from config_data.config import url_from_properties, headers
from loader import db_history
from utils.logger import logger


def get_distance_to_centre(landmarks: List[dict], user_id: int) -> Optional[str]:
    """
    Проверяет наличие в словаре дистанции до центра
    :param user_id: Идентификатор пользователя
    :param landmarks: Список со словарём, где могут быть расстояния до центра города/достопримечательности
    :return: Расстояние в виде строки или None
    """
    logger.info(f'{user_id} Вызвана функция get_distance_to_centre(propert)')
    for i in landmarks:
        if i['label'] == 'Центр города' or i['label'] == 'City center':
            return i['distance']
    logger.error(KeyError)
    return None


def get_address(address: dict, user_id: int) -> str:
    """
    Проверяет наличие адреса отеля
    :param user_id: Идентификатор пользователя
    :param address: Словарь с адресом
    :return: Адрес в виде строки
    """
    logger.info(f'{user_id} Вызвана функция get_address(propert)')
    if 'streetAddress' in address:
        return address['streetAddress']
    return address['locality']


def get_rating(hotel: dict, user_id: int) -> Optional[int]:
    """
    Проверяет наличие рейтинга отеля
    :param user_id: Идентификатор пользователя
    :param hotel: Словарь с информацией об отеле
    :return: Рейтинг в виде целого числа или None
    """
    logger.info(f'{user_id} Вызвана функция get_rating(propert)')
    if 'starRating' in hotel:
        return hotel['starRating']
    logger.error(KeyError)
    return None


def get_properties_list(destination_id: int, checkin: str, checkout: str, sort_order: str, locale: str, currency: str,
                        pagesize: str, user_id: int, command: str, total_days: int,
                        best_string: dict = None) -> Optional[Union[str, dict]]:
    """
    Получает список отелей
    :param total_days: Всего дней путешествия
    :param command: Введенная команда
    :param destination_id: Идентификатор города
    :param checkin: Дата заезда
    :param checkout: Дата выезда
    :param sort_order: Порядок сортировки
    :param locale: Локаль
    :param currency: Валюта
    :param pagesize: Количество отелей
    :param user_id: Идентификатор пользователя
    :param best_string: Дополнительные параметры запроса
    :return: Строка или словарь с информацией об отелях, либо None
    """
    logger.info(' ')
    querystring = {
        "destinationId": destination_id,
        "pageSize": pagesize,
        "checkIn": checkin,
        "checkOut": checkout,
        "sortOrder": sort_order,
        "locale": locale,
        "currency": currency
    }
    if best_string:
        logger.info('BestDeal')
        querystring.update(best_string)
    try:
        response = requests.request("GET", url_from_properties, headers=headers, params=querystring)
        if response:
            logger.info('response')
            try:
                data = json.loads(response.text)['data']['body']['searchResults']['results']
                if data:
                    return get_normalized_data(data, user_id, command, total_days)
                logger.error('Not response')
                return 'По вашему запросу ничего не найдено. Попробуйте снова /start'
            except (KeyError, json.JSONDecodeError) as e:
                logger.error(f'Error decoding JSON response: {e}')
                return 'Ошибка ответа сервера, попробуйте еще раз. /start'
    except requests.RequestException as e:
        logger.error(f'Error sending the request: {e}')
    except Exception as e:
        logger.exception(e)


def get_normalized_data(hotels: dict, user_id: int, command: str, total_days: int) -> Optional[Union[dict, str]]:
    """
    Генерирует нормализованную строку для бота
    :param total_days: Всего дней путешествия
    :param command: Введенная команда
    :param hotels: Список отелей
    :param user_id: Идентификатор пользователя
    :return: Нормализованная строка или словарь с информацией об отелях, либо None
    """
    logger.info(' ')
    if hotels:
        normalized_data = {}
        for num, hotel in enumerate(hotels):
            description = f'Отель - {hotel["name"]}\n' \
                          f'Адрес - {get_address(hotel["address"], user_id)}\n' \
                          f'Цена за ночь - {hotel["ratePlan"]["price"]["current"]} \n' \
                          f'Сайт отеля: https://ru.hotels.com/ho{hotel["id"]}\n' \
                          f'Всего стоимость за {total_days} ночи: {int(hotel["ratePlan"]["price"]["exactCurrent"]) * total_days}$\n'
            distance = get_distance_to_centre(hotel['landmarks'], user_id)
            rating = get_rating(hotel, user_id)
            if distance:
                description += f'Расстояние до центра  - {distance}\n'
            if rating:
                description += f'Рейтинг отеля: {rating}\n'

            normalized_data[hotel['id']] = description
        db_history.set_data(user_id, command, normalized_data)
        logger.info(' ')
        return normalized_data
    logger.error('Not hotels')
    return "По вашему запросу ничего не найдено. Попробуйте снова /start"
