from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from database.user_db import UserDatabase
from database.user_history_db import UserHistoryDatabase

# Инициализация хранилища состояний
storage: StateMemoryStorage = StateMemoryStorage()

# Создание экземпляра бота с использованием токена из конфигурации и хранилища состояний
bot: TeleBot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

# Создание объектов базы данных пользователей и истории пользователей
db_user = UserDatabase('user.db')
db_history = UserHistoryDatabase('history_user.db')
