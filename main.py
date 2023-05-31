from loader import bot
import handlers  # noqa
from keyboards.inline.bot_filters import bind_filters
from utils.set_bot_commands import set_default_commands
from utils.logger import logger

if __name__ == '__main__':
    set_default_commands(bot)
    bind_filters(bot)
    try:
        bot.delete_webhook()
    except Exception as e:
        logger.exception(e)
    bot.polling(none_stop=True)
