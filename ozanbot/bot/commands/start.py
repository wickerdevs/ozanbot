from ..commands import *

def start_def(update, context):
    if not check_auth(update, context):
        return ConversationHandler.END

        