import json
import os


def get(key="", parent="", default="", value=""):
    """
    Retrieve configuration variables from the secrets.json file.
    :variable: String of the name of the variable you are retrieving (see secrets.json)
    """
    if os.environ.get('PORT') in (None, ""):
        # CODE RUNNING LOCALLY
        variables = {}
        with open('//config/secrets.json') as variables_file: # TODO
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
        with open('//config/config.json') as variables_file: # TODO
            variables = json.load(variables_file)

        if key in variables:
            del variables[key]
        variables[key] = value

        with open('//config/config.json', 'w') as output_file: # TODO
            json.dump(variables, output_file)
    else:
        os.environ[key] = value
