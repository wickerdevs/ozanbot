from functools import wraps
import logging

from telegram.parsemode import ParseMode
from ozanbot.models.interaction import Interaction
from sys import exc_info
from ozanbot.models.settings import Settings
from ozanbot.models.setting import Setting
from ozanbot.models.followsession import FollowSession
from ozanbot.config import config
from ozanbot.texts import *
from typing import List, Optional, Tuple
from ozanbot import CONFIG_DIR, CONFIG_FOLDER
from instaclient.client.instaclient import InstaClient
from instaclient.errors.common import FollowRequestSentError, InvaildPasswordError, InvalidUserError, PrivateAccountError, SuspisciousLoginAttemptError, VerificationCodeNecessary
from instaclient.instagram.post import Post
from instaclient.instagram.profile import Profile
from ozanbot.models.instasession import InstaSession
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

    
def update_message(obj: FollowSession, text:str):
    """
    process_update_callback sends an update message to the user, to inform of the status of the current process. This method can be used as a callback in another method.

    Args:
        obj (ScraperorForwarder): Object to get the `chat_id` and `message_id` from.
        message (str): The text to send via message
        message_id (int, optional): If this argument is defined, then the method will try to edit the message matching the `message_id` of the `obj`. Defaults to None.
    """
    from ozanbot import telegram_bot as bot
    message_id = config.get_message(obj.get_user_id())
    try:
        bot.delete_message(chat_id=obj.user_id, message_id=message_id)
    except Exception as error:
        applogger.error(f'Unable to delete message of id {message_id}', exc_info=error)
        pass         

    message_obj = bot.send_message(chat_id=obj.user_id, text=text, parse_mode=ParseMode.HTML)
    obj.set_message(message_obj.message_id)
    config.set_message(obj.user_id, message_obj.message_id)
    applogger.debug(f'Sent message of id {message_obj.message_id}')
    return   



def init_client():
    if os.environ.get('PORT') in (None, ""):
        client = InstaClient(driver_path=f'{CONFIG_FOLDER}chromedriver.exe', debug=True, error_callback=insta_error_callback, logger=instalogger, localhost_headless=True)
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

    update_message(session, logging_in_text)
    try:
        client.login(session.username, session.password)
    except (InvalidUserError, InvaildPasswordError):
        client.disconnect()
        return (False, None)
    except VerificationCodeNecessary:
        client.disconnect()
        return (False, None)
    
    target = client.get_profile(session.target)
    applogger.debug(target)
    interaction = Interaction(target)
    applogger.debug(interaction)
    session.set_interaction(interaction)

    # TODO: Scrape Users
    update_message(session, waiting_scrape_text)
    try:
        followers = client.get_followers(session.target, session.count)
        session.set_scraped(followers)
    except Exception as error:
        applogger.error(f'Error in scraping <{session.target}>\'s followers: ', exc_info=error)
        client.disconnect()
        update_message(session, operation_error_text.format(len(session.get_followed())))
        return (False, None)

    # FOR EACH USER
    for index, follower in enumerate(followers):
        # TODO: Follow User
        if follower == session.username:
            continue

        update_message(session, followed_user_text.format(index, len(followers)))
        profile:Profile = client.get_profile(follower)
        if not profile:
            continue

        try:
            profile.follow()
            session.add_followed(profile)
        except FollowRequestSentError as error:
            pass
        except Exception as error:
            applogger.error(f'Error in following <{follower}>\'s followers: ', exc_info=error)
            client.disconnect()
            update_message(session, operation_error_text.format(len(session.get_followed())))
            return (False, session)

        # TODO: Get first 2 posts
        if profile.post_count > 0:
            comments = 0
            try:
                try:
                    posts:List[Post] = profile.get_posts(session.count)
                    for post in posts:
                        try:
                            post.like()
                            session.add_liked(post)
                            if comments < 1:
                                post.add_comment(setting.comment)
                                session.add_commented(post)
                                comments += 1
                        except Exception as error:
                            applogger.error(f'Error in sending like/comment to <{follower}>: ', exc_info=error)
                            pass
                except (PrivateAccountError, InvalidUserError):
                    pass
            except Exception as error:
                applogger.error(f'Error in interacting: ', exc_info=error)
                client.disconnect()
                update_message(session, operation_error_text.format(len(session.get_followed())))
                return (False, session)
        
    update_message(session, follow_successful_text.format(len(session.get_followed()), session.count))
    client.disconnect()
    return (True, session)

        