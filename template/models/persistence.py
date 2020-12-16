import json, jsonpickle
from . import *
import os

def persistence_decorator(func):
    def wrapper(self, *args, **kw):
        # Call function
        output = func(self, *args, **kw)
        # Post Processing
        self.serialize()
        return output
    return wrapper

class Persistence(object):
    """Class to save objects in pickle files for bot Conversation Persistance"""
    SIGNIN = 'signin'
    FOLLOW = 'follow'
    SIGNOUT = 'signout'
    ACCOUNT = 'account'
    INSTASESSION = 'instasession'
    START = 'start'
    SETTINGS = 'settings'
    
    
    def __init__(self, method, user_id, message_id=None):
        self.method = method
        self.user_id = user_id
        self.message_id = message_id


    @persistence_decorator
    def set_message(self, message_id):
        self.message_id = message_id
        return self.message_id


    def get_user_id(self):
        return self.user_id


    def get_message_id(self):
        return self.message_id


    def discard(self):
        # CODE RUNNING LOCALLY
        try:
            os.remove(
            "ffinstabot/bot/persistence/{}{}.json".format(self.method, self.user_id))
        except FileNotFoundError:
            return self

    def serialize(self):
        # CODE RUNNING LOCALLY
        if not os.path.isdir('ffinstabot/bot/persistence/'):
            os.mkdir('ffinstabot/bot/persistence/')
        with open("ffinstabot/bot/persistence/{}{}.json".format(self.method, self.user_id), "w") as write_file:
            encoded = jsonpickle.encode(self)
            json.dump(encoded, write_file, indent=4)
        return self

    def deserialize(method, update):
        # CODE RUNNING LOCALLY
        try:
            with open("ffinstabot/bot/persistence/{}{}.json".format(method, update.effective_chat.id)) as file:
                json_string = json.load(file)
                obj = jsonpickle.decode(json_string)
                return obj
        except:
            return None