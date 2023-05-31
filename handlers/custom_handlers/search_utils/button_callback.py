from datetime import date
from utils.logger import logger
from loader import bot
from keyboards.inline.bot_filters import  for_button, for_search
from keyboards.inline.calendar.inline_calendar import bot_get_keyboard_inline
from telebot.types import CallbackQuery


def button_callback(call: CallbackQuery, state, command)  -> None:
    logger.info(f'user_id {call.from_user.id}')
    callback_data = for_button.parse(callback_data=call.data)
    name, destid = callback_data['name'], int(callback_data['destid'])
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['destid'] = destid
        data['city'] = name
        logger.info(f'user_id {call.from_user.id}{destid, name}')
        bot.edit_message_text(f'Отличный выбор {name}', call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, state.start_date, call.message.chat.id)
    bot.send_message(call.message.chat.id, f'Выберите даты заезда',
                     reply_markup=bot_get_keyboard_inline(command=command, state=f'{state.name}_start_date'))


def callback_start_date(call: CallbackQuery, state, command) -> None:
    """
    :param call: Выбор пользователя начала поездки
    """
    logger.info(f'user_id {call.from_user.id}')
    bot.set_state(call.from_user.id, state.end_date, call.message.chat.id)
    data = for_search.parse(callback_data=call.data)
    my_exit_date = date(year=int(data['year']), month=int(data['month']), day=int(data['day']))
    bot.send_message(call.message.chat.id, 'Выберите дату уезда',
                     reply_markup=bot_get_keyboard_inline(command=command, state=f'{state.name}_end_date'))
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['startday'] = my_exit_date
        logger.info(f'user_id {call.from_user.id, my_exit_date}')
        bot.edit_message_text(f'Дата заезда: {my_exit_date}', call.message.chat.id, call.message.id)


def callback_end_date(call: CallbackQuery, state) -> None:
    logger.info(f'user_id {call.from_user.id}')
    data = for_search.parse(callback_data=call.data)
    my_exit_date = date(year=int(data['year']), month=int(data['month']), day=int(data['day']))
    bot.set_state(call.from_user.id, state.count_hotels, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Сколько отелей выводить? (не более 10)')
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        logger.info(f'user_id {call.from_user.id} {my_exit_date}')
        data['endday'] = my_exit_date
        data['all_days'] = data['endday'] - data['startday']
        if data['startday'] > data['endday']:
            logger.error(f'user_id {call.from_user.id}')
            data['startday'], data['endday'] = data['endday'], data['startday']
        bot.edit_message_text(f'Дата выезда: {my_exit_date}', call.message.chat.id, call.message.id)