from ozanbot import applogger, telelogger, telegram_bot, updater



if __name__ == '__main__':
    # Start
    applogger.debug(f'Started bot of id: {telegram_bot.id}')
    telelogger.info('Polling Telegram bot...')
    updater.start_polling()