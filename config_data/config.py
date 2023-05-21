import os
from dotenv import load_dotenv, find_dotenv
from utils.logger import logger
from typing import Dict, List, Tuple

if not find_dotenv():
    logger.error("Переменные окружения не загружены, так как отсутствует файл .env")
    exit()
else:
    logger.info(logger.name)
    load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')
RAPID_API_KEY: str = os.getenv('RAPID_API_KEY')

DEFAULT_COMMANDS: List[Tuple[str, str]] = [
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', 'Поиск бюджетных отелей'),
    ('highprice', 'Поиск лучших отелей'),
    # ('bestdeal', 'Настройка поиска'),
    # ('history', 'История поиска')
]

url_from_cities: str = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_from_properties: str = "https://hotels4.p.rapidapi.com/properties/list"
url_from_photo: str = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

headers: Dict[str, str] = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": RAPID_API_KEY
}
