PERSISTENCE_DIR = 'ozanbot/config/'
CONFIG_DIR = 'ozanbot/config/config.json'
CONFIG_FOLDER = 'ozanbot/config/'

import os, logging
from telegram.ext.updater import Updater
from telegram.ext.defaults import Defaults
from telegram.utils.request import Request
from ozanbot.models.mq_bot import MQBot
import telegram
from telegram import ParseMode
from telegram.ext import messagequeue as mq

# Enable logging
# TODO REMOVE WHEN FINISHED DEBUGGING
debug = True
if debug:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
else:
    logging.basicConfig(filename="logs.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

applogger = logging.getLogger('applogger')
applogger.setLevel(logging.DEBUG)

instalogger = logging.getLogger('instaclient')
instalogger.setLevel(logging.DEBUG)

telelogger = logging.getLogger("telegram.bot")
telelogger.setLevel(logging.INFO)

def instaclient_error_callback(driver):
    from ozanbot import telegram_bot as bot
    driver.save_screenshot('error.png')
    bot.report_error('instaclient.__find_element() error.', send_screenshot=True, screenshot_name='error')
    os.remove('error.png')


LOCALHOST = True
queue = None
if os.environ.get('PORT') not in (None, ""):
    # Code running locally
    LOCALHOST = False    

# Initialize Bot
from ozanbot.config import config
BOT_TOKEN = config.get('BOT_TOKEN')
URL = config.get('SERVER_APP_DOMAIN')
PORT = int(os.environ.get('PORT', 5000))


request = Request(con_pool_size=8)
defaults = Defaults(parse_mode=ParseMode.HTML, run_async=True)
q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
telegram_bot = MQBot(BOT_TOKEN, request=request, mqueue=q, defaults=defaults)
updater = Updater(bot=telegram_bot, use_context=True)

# SET UP BOT COMMAND HANDLERS
applogger.debug(f'Initiate setup')
from ozanbot.bot import setup
setup.setup(updater)

        