import json, jsonpickle
from ozanbot import PERSISTENCE_DIR
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

    
    def __getitem__(self, item: str):
        return self.__dict__[item]


    @persistence_decorator
    def set_message(self, message_id):
        self.message_id = message_id
        return self.message_id


    def get_user_id(self):
        return self.user_id


    def get_message_id(self):
        return self.message_id

    
    def to_dict(self) -> str:
        data = dict()

        for key in iter(self.__dict__):
            value = self.__dict__[key]
            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value
        return data

    @classmethod
    def de_json(cls, data: dict):

        if not data:
            return None

        obj = cls(**data)  # type: ignore[call-arg]
        return obj

    def discard(self):
        # CODE RUNNING LOCALLY
        try:
            os.remove(
            "{}{}{}.json".format(PERSISTENCE_DIR, self.method, self.user_id))
        except FileNotFoundError:
            return self

    def serialize(self):
        # CODE RUNNING LOCALLY
        if not os.path.isdir(PERSISTENCE_DIR):
            os.mkdir(PERSISTENCE_DIR)
        with open("{}{}{}.json".format(PERSISTENCE_DIR, self.method, self.user_id), "w") as write_file:
            encoded = jsonpickle.encode(self)
            json.dump(encoded, write_file, indent=4)
        return self

    def deserialize(method, update):
        # CODE RUNNING LOCALLY
        try:
            with open("{}{}{}.json".format(PERSISTENCE_DIR, method, update.effective_chat.id)) as file:
                json_string = json.load(file)
                obj = jsonpickle.decode(json_string)
                return obj
        except:
            return None