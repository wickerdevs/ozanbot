from ..commands import *


def help_def(update, context):
    message = send_message(update, context, help_text)