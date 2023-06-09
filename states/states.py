from loader import bot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

state_storage = StateMemoryStorage()


class LowPriceState(StatesGroup):
    """
    State класс для команды LowPrice
    """
    city = State()
    cities = State()
    count_hotels = State()
    photo = State()
    count_photo = State()
    start_date = State()
    end_date = State()
    name = "low"

class HighPriceState(StatesGroup):
    """
    State класс для команды HighPrice
    """
    city = State()
    cities = State()
    count_hotels = State()
    photo = State()
    count_photo = State()
    start_date = State()
    end_date = State()
    name = "high"


class BestDealState(StatesGroup):
    """
    State класс для команды BestDeal
    """
    city = State()
    cities = State()
    count_hotels = State()
    photo = State()
    count_photo = State()
    start_date = State()
    end_date = State()
    min_price = State()
    max_price = State()
    distance = State()
    name = "dest"


class HistoryState(StatesGroup):
    """
    State класс для команды history
    """
    count = State()

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
