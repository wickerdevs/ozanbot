from ozanbot.bot.commands import *


@send_typing_action
def check_account(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END
    instasession = InstaSession(update.effective_chat.id, update.effective_user.id)
    #message = send_message(update, context, message=checking_accounts_connection)
    try:
        if instasession.get_creds():
            # User logged into instagram
            text = connection_found_text.format(instasession.username, instasession.username)
            markup = CreateMarkup({Callbacks.LOGOUT: 'Log Out', Callbacks.SWITCH: 'Switch Account', Callbacks.EDIT_SETTINGS: 'Settings'}, cols=2).create_markup()
            instasession.discard()
            message = send_message(update, context, text, markup)
        else:
            # User is not logged in
            markup = CreateMarkup({Callbacks.LOGIN: 'Log In'}).create_markup()
            instasession.discard()
            message = send_message(update, context, no_connection, markup)
    except:
        # Error
        instasession.discard()
        message = send_message(update, context, problem_connecting)
        context.bot.report_error('Error in Checking Instagram Connection')
        

def switch_account(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END
        
    instasession = InstaSession(update.effective_chat.id, update.effective_user.id)
    creds = instasession.get_all_creds()
    session = instasession.get_session()
    markupk = dict()
    for cred in creds:
        if cred != session:
            markupk[f'{Callbacks.SELECTSWITCH}:{cred}'] = cred

    if len(markupk) < 1:
        markup = CreateMarkup({Callbacks.LOGIN: 'Add Another Account'}).create_markup()
        send_message(update, context, no_accounts_available_text, markup)
        return

    markupk[Callbacks.LOGIN] = 'Add Another'
    markupk[Callbacks.ACCOUNT] = 'Cancel'
    markup = CreateMarkup(markupk, cols=2).create_markup()

    send_message(update, context, switch_account_text, markup)
    instasession.discard()
    return


def select_switched_account(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END
    
    data = update.callback_query.data
    selection = data.split(':')[1]
    instasession = InstaSession(update.effective_chat.id, update.effective_user.id)
    instasession.set_session(selection)
    markup = CreateMarkup({Callbacks.ACCOUNT: 'Account Info'}).create_markup()
    send_message(update, context, switched_account_text.format(selection, selection), markup)
    instasession.discard()
    return