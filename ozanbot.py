from ozanbot import applogger, telelogger, BOT_TOKEN
from telegram.ext.updater import Updater
from telegram.ext.defaults import Defaults
from telegram.utils.request import Request
from ozanbot.models.mq_bot import MQBot
import telegram
from telegram import ParseMode
from telegram.ext import messagequeue as mq


if __name__ == '__main__':
    # set connection pool size for bot 
    request = Request(con_pool_size=8)
    defaults = Defaults(parse_mode=ParseMode.HTML, run_async=True)
    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    telegram_bot = MQBot(BOT_TOKEN, request=request, mqueue=q, defaults=defaults)
    updater = Updater(bot=telegram_bot, use_context=True)
    
    # SET UP BOT COMMAND HANDLERS
    applogger.debug(f'Initiate setup')
    from ozanbot.bot import setup
    setup.setup(updater)

    # Start
    applogger.debug(f'Started bot of id: {telegram_bot.id}')
    telelogger.info('Polling Telegram bot...')
    updater.start_polling()