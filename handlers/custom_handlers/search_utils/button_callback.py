from utils.logger import logger
from loader import bot
from keyboards.inline.bot_filters import  for_button
from keyboards.inline.calendar.inline_calendar import bot_get_keyboard_inline


def button_callback(call, state, command):
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
