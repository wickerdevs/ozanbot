import logging
from instaclient import InstaClient
import os

instalogger = logging.getLogger('instaclient')


def insta_error_callback(driver):
    driver.save_screenshot('error.png')
    from ozanbot import telegram_bot as bot, config # TODO
    users_str = config.get('DEVS')
    if isinstance(users_str, str):
        users_str = users_str.replace('[', '')
        users_str = users_str.replace(']', '')
        users_str = users_str.replace(' ', '')
        users = users_str.split(',')
        for index, user in enumerate(users):
            users[index] = int(user)
    else:
        users = users_str

    for dev in users:
        bot.send_photo(chat_id=dev, photo=open('{}.png'.format('error'), 'rb'), caption='There was an error with the bot. Check logs')



def init_client():
    if os.environ.get('PORT') in (None, ""):
        client = InstaClient(driver_path='ffinstabot/config/driver/chromedriver.exe', debug=True, error_callback=insta_error_callback, logger=instalogger, localhost_headless=True)
    else:
        client = InstaClient(host_type=InstaClient.WEB_SERVER, debug=True, error_callback=insta_error_callback, logger=instalogger)
    return client