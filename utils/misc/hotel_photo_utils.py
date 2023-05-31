from typing import Union, List
import requests
import json
from config_data.config import url_from_photo, headers
from utils.logger import logger


def get_photo_hotel(city_id: int, count_photo: int) -> Union[List[str], bool]:
    """
    Получает фотографии отеля по идентификатору города.

    :param city_id: Идентификатор города
    :param count_photo: Количество фотографий
    :return: Список URL-адресов фотографий
    """
    media = []
    querystring = {
        'id': city_id
    }
    try:
        response = requests.request("GET", url_from_photo, headers=headers, params=querystring)
        if response:
            logger.info('response')
            data = json.loads(response.text)['hotelImages']
            if data:
                for photo in data:
                    media.append(photo['baseUrl'].replace('{size}', 'b'))
                    if len(media) >= count_photo:
                        break
                return media
    except BaseException as e:
        logger.exception(e)
        return False
