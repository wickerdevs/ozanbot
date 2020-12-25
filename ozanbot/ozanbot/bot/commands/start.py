from ozanbot.bot.commands import *

@send_typing_action
def start_def(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END

    settings = config.get_settings(update.effective_chat.id)
    if settings and hasattr(settings, 'settings') and settings.settings is not None:
        markup = CreateMarkup({Callbacks.EDIT_SETTINGS: 'Edit Settings', Callbacks.ACCOUNT: 'Account Info'}, cols=2).create_markup()
        send_message(update, context, startup_done, markup)
        settings.discard()
        return ConversationHandler.END
    
    # Initialize Settings
    settings = Settings(user_id=update.effective_chat.id)

    markup = CreateMarkup({Callbacks.LOGIN: 'Next'}).create_markup()
    message = send_message(update, context, welcome, markup)
    settings.set_message(message.message_id)
    settings.save()
    settings.discard()


        