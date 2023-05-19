from loader import bot
from utils.logger import logger
from telebot.types import CallbackQuery
from keyboards.inline.bot_filters import calendar_factory
from keyboards.inline.calendar.inline_calendar import get_next_or_prev_month


@bot.callback_query_handler(func=None, calendar_config=calendar_factory.filter())
def callback_inline_action_prev_next(call: CallbackQuery):
    """
    Обрабатывает выбор пользователя с календаря, если было выбрано перелистывание месяца.
    :param call: Выбор пользователя
    """
    logger.info(' ')
    callback_data = calendar_factory.parse(callback_data=call.data)
    action, year, month, command, state = (
        callback_data['action'], int(callback_data['year']), int(callback_data['month']), callback_data['command'],
        callback_data['state'])
    bot.edit_message_text('Месяц', call.message.chat.id, call.message.id,
                          reply_markup=get_next_or_prev_month(action=action,
                                                              year=year,
                                                              month=month,
                                                              command=command,
                                                              state=state))


@bot.callback_query_handler(func=lambda call: call.data.startswith('EMPTY'))
def if_empty_callback(call: CallbackQuery):
    """
    Обрабатывает выбор пользователя, если было выбрано некорректное место на календаре.
    :param call: Выбор пользователя
    """
    logger.error()
    bot.answer_callback_query(callback_query_id=call.id,
                              text='Выберите число!')  # Применить, когда тыкает в ненужное место
