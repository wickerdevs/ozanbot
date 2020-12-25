from instaclient.errors.common import InstaClientError, InvaildPasswordError, InvalidSecurityCodeError, InvalidUserError, NotLoggedInError, PrivateAccountError, InvalidVerificationCodeError, VerificationCodeNecessary, SuspisciousLoginAttemptError
from instaclient.client.instaclient import InstaClient
from instaclient.instagram.profile import Profile
from ozanbot.bot.commands import *
from ozanbot import applogger

client:InstaClient


@send_typing_action
def ig_login(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END

    # Check IG status    
    instasession:InstaSession = InstaSession(update.effective_chat.id, update.effective_user.id)
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    message = send_message(update, context, checking_ig_status)
    instasession.set_message(message.message_id)

    send_message(update, context, input_ig_username_text, markup)
    return InstaStates.INPUT_USERNAME

    

@send_typing_action
def instagram_username(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSTASESSION, update)
    if not instasession:
        return InstaStates.INPUT_USERNAME
    
    username = update.message.text 
    message = send_message(update, context, checking_user_vadility_text)
    instasession.set_message(message.message_id)
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    # Verify User
    try:
        instaclient = instagram.init_client()
        profile = instaclient.get_profile(username, context=False)
        if isinstance(profile, Profile):
            applogger.debug('USER {} IS VALID'.format(username))
        else:
            send_message(update, context, invalid_user_text.format(username), markup)
            instasession.set_message(message.message_id)
            return InstaStates.INPUT_USERNAME
    except InvalidUserError as error:
        send_message(update, context, invalid_user_text.format(error.username), markup)
        instasession.set_message(message.message_id)
        return InstaStates.INPUT_USERNAME
    except (PrivateAccountError, NotLoggedInError) as error:
        pass
    instasession.set_username(username)
    # Request Password
    send_message(update, context, input_password_text, markup)
    return InstaStates.INPUT_PASSWORD



@send_typing_action
def instagram_password(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSTASESSION, update)
    if not instasession:
        return InstaStates.INPUT_PASSWORD

    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    password = update.message.text
    instasession.set_password(password)
    message = send_message(update, context, attempting_login_text)
    instasession.set_message(message.message_id)

    if len(password) < 6:
        send_message(update, context, invalid_password_text.format(instasession.password), markup)
        return InstaStates.INPUT_PASSWORD
        
    # Attempt login
    instaclient = instagram.init_client()
    try:
        instaclient.login(instasession.username, instasession.password)
    except InvalidUserError as error:
        send_message(update, context, invalid_user_text.format(error.username), markup)
        instasession.set_message(message.message_id)
        instaclient.disconnect()
        return InstaStates.INPUT_USERNAME

    except InvaildPasswordError:
        send_message(update, context, invalid_password_text.format(instasession.password), markup)
        instaclient.disconnect()
        return InstaStates.INPUT_PASSWORD
        
    except VerificationCodeNecessary:
        send_message(update, context, verification_code_necessary, markup)
        instaclient.disconnect()
        return ConversationHandler.END

    except SuspisciousLoginAttemptError as error:
        # Creds are correct
        instaclient.driver.save_screenshot('suspicious_login_attempt.png')
        context.bot.report_error(error, send_screenshot=True, screenshot_name='suspicious_login_attempt')
        if os.path.exists("suspicious_login_attempt.png"):
            os.remove("suspicious_login_attempt.png")
        instasession.increment_code_request()
        if error.mode == SuspisciousLoginAttemptError.PHONE:
            text = input_security_code_text
        else:
            text = input_security_code_text_email
        markup = CreateMarkup({Callbacks.RESEND_CODE: 'Resend Code', Callbacks.CANCEL: 'Cancel'}).create_markup()
        send_message(update, context, text, markup)
        global client
        client = instaclient
        return InstaStates.INPUT_SECURITY_CODE

    # Login Successful
    instasession.save_creds()
    instasession.set_session()
    instaclient.disconnect()

    # Check Settings
    settings = config.get_settings(update.effective_user.id)
    if not settings:
        settings:Settings = Settings(user_id=update.effective_user.id)

    settings.set_setting(instasession.username)
    settings.set_message(config.get_message(update.effective_chat.id))

    # Ask to input default message
    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    send_message(update, context, login_successful_text, markup)
    return StartStates.TEXT


@send_typing_action
def input_default_text(update, context):
    settings:Settings = Settings.deserialize(Persistence.SETTINGS, update)
    if not settings:
        return

    instasession:InstaSession = InstaSession.deserialize(Persistence.INSTASESSION, update)
    if not instasession:
        return

    settings.set_comment(instasession.username, update.message.text)

    # TODO Change this part when implementing schedule queue --------------------|
    settings.save()
    
    markup = CreateMarkup({Callbacks.HELP: 'What can I do?'}).create_markup()
    send_message(update, context, end.format(instasession.username), markup)

    settings.discard()
    instasession.discard()
    return ConversationHandler.END


@send_typing_action
def instagram_resend_scode(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSTASESSION, update)
    if not instasession:
        return InstaStates.INPUT_SECURITY_CODE

    try:
        global client
        client.resend_security_code()
        text = 'phone number'
    except SuspisciousLoginAttemptError as error:
        if error.mode == SuspisciousLoginAttemptError.EMAIL:
            # Code to sent via email
            text = 'email'
        else:
            text = 'phone number'
    instasession.increment_code_request()
    update.callback_query.answer()
    markup = CreateMarkup({Callbacks.RESEND_CODE: 'Resend Code', Callbacks.CANCEL: 'Cancel'}).create_markup()
    send_message(update, context, security_code_resent.format(text, instasession.code_request), markup)
    return InstaStates.INPUT_SECURITY_CODE
    

""" 
@send_typing_action
def instagram_verification_code(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSTASESSION, update)
    if not instasession:
        return InstaStates.INPUT_VERIFICATION_CODE

    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    code = update.message.text
    message = update.effective_chat.send_message(text=validating_code_text, reply_markup=markup)
    instasession.set_scode(code)
    instasession.set_message(message.message_id)

    try:
        instaclient.input_verification_code(code)
    except InvalidVerificationCodeError:
        context.bot.edit_message_text(text=invalid_security_code_text.format(code), chat_id=instasession.user_id, message_id=instasession.message_id, reply_markup=markup)
        return InstaStates.INPUT_VERIFICATION_CODE

    # Login Successful
    instasession.save_creds()
    context.bot.edit_message_text(text=login_successful_text, chat_id=instasession.user_id, message_id=instasession.message_id)
    instasession.discard()
    return ConversationHandler.END """



@send_typing_action
def instagram_security_code(update, context):
    instasession:InstaSession = InstaSession.deserialize(Persistence.INSTASESSION, update)
    if not instasession:
        return InstaStates.INPUT_SECURITY_CODE

    markup = CreateMarkup({Callbacks.CANCEL: 'Cancel'}).create_markup()
    code = update.message.text
    message = send_message(update, context, validating_code_text, markup)
    instasession.set_scode(code)
    instasession.set_message(message.message_id)

    try:
        global client
        client.input_security_code(code)
    except InvalidSecurityCodeError:
        send_message(update, context, invalid_security_code_text.format(code), markup)
        return InstaStates.INPUT_SECURITY_CODE

    # Login Successful # TODO
    instasession.save_creds()
    instasession.set_session()
    client.disconnect()

    # Check Settings
    settings:Settings = config.get_settings(instasession.user_id)
    setting = settings.get_setting(instasession.username)
    if not setting:
        settings.set_setting(instasession.username)

    # Ask to input default message
    send_message(update, context, login_successful_text)
    return StartStates.TEXT



@send_typing_action
def cancel_instagram(update, context, instasession:InstaSession=None):
    if not instasession:
        instasession = InstaSession.deserialize(Persistence.INSTASESSION, update)
        if not instasession:
            return
    try:
        update.callback_query.edit_message_text(text=cancelled_instagram_text)
    except:
        try:
            context.bot.edit_message_text(chat_id=instasession.user_id, message_id=instasession.message_id, text=cancelled_instagram_text)
        except:
            message = send_message(update, context, cancelled_instagram_text)
    instasession.discard()
    try: client.disconnect()
    except: pass
    return ConversationHandler.END

    
    






