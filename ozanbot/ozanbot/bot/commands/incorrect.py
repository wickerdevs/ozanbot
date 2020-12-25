from ozanbot.bot.commands import *

@send_typing_action
def incorrect_command(update, context):
    send_message(update, context, incorrect_command_text)