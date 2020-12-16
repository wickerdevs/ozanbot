import os, logging
import telegram
from instaclient import InstaClient
from telegram.ext.updater import Updater
from telegram.ext.defaults import Defaults
from telegram.utils.request import Request
from .models.mq_bot import MQBot
from telegram import ParseMode
from telegram.ext import messagequeue as mq

# Enable logging
# TODO REMOVE WHEN FINISHED DEBUGGING
debug = False
if debug:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
else:
    logging.basicConfig(filename="logs.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

applogger = logging.getLogger('applogger')
applogger.setLevel(logging.DEBUG)

instalogger = logging.getLogger('instaclient')
instalogger.setLevel(logging.DEBUG)

telelogger = logging.getLogger("telegram.bot")
telelogger.setLevel(logging.DEBUG)


def instaclient_error_callback(driver):
    from . import telegram_bot as bot
    driver.save_screenshot('error.png')
    bot.report_error('instaclient.__find_element() error.', send_screenshot=True, screenshot_name='error')
    os.remove('error.png')


LOCALHOST = True
queue = None
if os.environ.get('PORT') not in (None, ""):
    # Code running locally
    LOCALHOST = False    

# Initialize Bot
from .config import config
BOT_TOKEN = config.get_var('BOT_TOKEN')
URL = config.get_var('SERVER_APP_DOMAIN')
PORT = int(os.environ.get('PORT', 5000))
from .bot import setup

# set connection pool size for bot 
request = Request(con_pool_size=8)
defaults = Defaults(parse_mode=ParseMode.HTML, run_async=True)
q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
telegram_bot = MQBot(BOT_TOKEN, request=request, mqueue=q, defaults=defaults)
updater = Updater(bot=telegram_bot, use_context=True)
applogger.debug(f'Started bot of id: {telegram_bot.id}')

# SET UP BOT COMMAND HANDLERS
setup.setup(updater)
        