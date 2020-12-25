from ozanbot.bot.commands import *


@send_typing_action
def instagram_log_out(update, context):
    if check_auth(update, context):
        instasession = InstaSession(update.effective_chat.id, update.effective_user.id)
        # User is authorised
        message = send_message(update, context, logging_out)
        instasession.delete_creds()
        instasession.discard()
        markup = CreateMarkup({Callbacks.ACCOUNT: 'Account Info'}).create_markup()
        message.edit_text(text=instagram_loggedout_text, reply_markup=markup)

