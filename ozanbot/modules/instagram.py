from functools import wraps
import logging
from ozanbot.models.interaction import Interaction
from sys import exc_info
from ozanbot.models.settings import Settings
from ozanbot.models.setting import Setting
from ozanbot.models.followsession import FollowSession
from ozanbot.config import config
from typing import List, Optional, Tuple
from ozanbot import CONFIG_DIR, CONFIG_FOLDER
from instaclient.client.instaclient import InstaClient
from instaclient.errors.common import FollowRequestSentError, InvaildPasswordError, InvalidUserError, SuspisciousLoginAttemptError, VerificationCodeNecessary
from instaclient.instagram.post import Post
from ..models.instasession import InstaSession
from ozanbot import applogger
import os, multiprocessing

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
        client = InstaClient(driver_path=f'{CONFIG_FOLDER}chromedriver.exe', debug=True, error_callback=insta_error_callback, logger=instalogger, localhost_headless=False)
    else:
        client = InstaClient(host_type=InstaClient.WEB_SERVER, debug=True, error_callback=insta_error_callback, logger=instalogger, localhost_headless=True)
    return client


def error_proof(func):
    @wraps(func)
    def wrapper(session:FollowSession):
        result:Tuple[bool, FollowSession] = func(session)
        if result[1]:
            settings:Settings = config.get_settings(session.user_id)
            settings.add_interaction(result[1].interaction)
        return result
    return wrapper


@error_proof
def enqueue_interaction(session:FollowSession) -> Tuple[bool, Optional[FollowSession]]:
    applogger.debug(session)
    settings:Settings = config.get_settings(session.user_id)
    applogger.debug(settings)
    setting:Setting = settings.get_setting(session.username)
    applogger.debug(setting)
    client = init_client()
    target = client.get_profile(session.target)
    applogger.debug(target)
    interaction = Interaction(target)
    applogger.debug(interaction)
    session.set_interaction(interaction)

    try:
        client.login(session.username, session.password)
    except (InvalidUserError, InvaildPasswordError):
        client.disconnect()
        return (False, None)
    except VerificationCodeNecessary:
        client.disconnect()
        return (False, None)

    # TODO: Scrape Users
    try:
        followers = client.get_followers(session.target, session.count)
        session.set_scraped(followers)
    except Exception as error:
        applogger.error(f'Error in scraping <{session.target}>\'s followers: ', exc_info=error)
        client.disconnect()
        return (False, None)

    # FOR EACH USER
    for index, follower in enumerate(followers):
        # TODO: Follow User
        try:
            client.follow(follower)
            session.add_followed(client.get_profile(follower))
        except FollowRequestSentError as error:
            pass
        except Exception as error:
            applogger.error(f'Error in following <{follower}>\'s followers: ', exc_info=error)
            client.disconnect()
            return (False, session)

        # TODO: Get first 2 posts
        try:
            posts:List[Post] = client.get_user_posts(follower, 2)
            for post in posts:
                try:
                    post.like()
                    session.add_liked(post)
                    post.add_comment(setting.comment)
                    session.add_commented(post)
                except Exception as error:
                    applogger.error(f'Error in sending like/comment to <{follower}>: ', exc_info=error)
                    pass
        except Exception as error:
            applogger.error(f'Error in interacting: ', exc_info=error)
            client.disconnect()
            return (False, session)
        
        client.disconnect()
        return (True, session)

        