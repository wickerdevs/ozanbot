import json, os
from ozanbot.models.setting import Setting
from ozanbot import CONFIG_DIR
from typing import Optional, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from ozanbot.models.settings import Settings



############################### MESSAGE #################################
def set_message(user_id, message_id):
    messages = get('MESSAGES')
    if not messages:
        set('MESSAGES', {str(user_id): message_id})
    else:
        messages[str(user_id)] = message_id
        set('MESSAGES', messages)


def get_message(user_id):
    messages = get('MESSAGES')
    if not messages:
        return None
    else:
        return messages.get(str(user_id))


def set_settings(data:'Settings'):
    """
    set_settings Save settings to config.json

    Args:
        settings (Settings): Settings object
    """
    set(f'SETTINGS:{data.get("user_id")}', data)



def get_settings(user_id:int) -> Optional['Settings']:
    """
    Return `Setting` object corresponding to the user id.

    Args:
        user_id (int): Telegram user ID to check for

    Returns:
        Setting or None: Setting matching `user_id` attribute
    """
    from ozanbot.models.settings import Settings 
    data:Optional['Settings'] = get(f'SETTINGS:{user_id}')
    if data:
        return Settings.de_json(data)
    return None


def get(key="", parent="", default="", value=""):
    """
    Retrieve configuration variables from the config.json file.
    :variable: String of the name of the variable you are retrieving (see config.json)
    """
    if os.environ.get('PORT') in (None, ""):
        # CODE RUNNING LOCALLY
        variables = {}
        with open(CONFIG_DIR) as variables_file: # TODO
            variables = json.load(variables_file)
        if value != "":
            if value in variables.values():
                return True
            else:
                return False

        elif parent == "":
            requested = variables.get(str(key))
        else:
            requested = variables[parent][str(key)]
        if requested in ("", None, "insert_here", "insert_here_if_available"):
            if default == "":
                return None
            else:
                return default
        else:
            return requested
    else:
        # CODE RUNNING ON SERVER
        return os.environ.get(key)


def set(key, value):
    """
    Set a variable to the env_variables.json file.
    :key: String (all caps) with the dictionary name of the variable (type str)
    :value: the value of the variable (type str)
    """
    if os.environ.get('PORT') in (None, ""):
        with open(CONFIG_DIR) as variables_file: # TODO
            variables = json.load(variables_file)

        if key in variables:
            del variables[key]
        variables[key] = value

        with open(CONFIG_DIR, 'w') as output_file: # TODO
            json.dump(variables, output_file)
    else:
        os.environ[key] = value
