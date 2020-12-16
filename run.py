import os, logging
import telegram
from template import updater, telelogger


if __name__ == '__main__':
    telelogger.info('Polling Telegram bot...')
    updater.start_polling()