from datetime import timedelta
from ozanbot.models import interaction
from ozanbot.models.interaction import Interaction
from typing import Dict, List, TYPE_CHECKING
from ..models.setting import Setting
import jsonpickle, json
from ..models.persistence import Persistence, persistence_decorator
from ..config import config
import datetime
    

class Settings(Persistence):
    def __init__(self, 
    method:str=Persistence.SETTINGS,
    user_id:int=None, 
    message_id:int=None,
    settings:dict=None, 
    interactions:List[Interaction]=None) -> None:
        super().__init__(method, user_id, message_id)
        self.settings=settings # username: setting
        self.interactions = interactions

    def __repr__(self) -> str:
        return jsonpickle.encode(self)

    def __str__(self) -> str:
        return f'Settings<{self.user_id}>'

    def to_dict(self) -> str:
        data = dict()
        for key in iter(self.__dict__):
            value = self.__dict__[key]
            if value is not None:
                if key == 'settings':
                    for id in value.keys():
                        value[id] = Setting.to_dict(value[id])
                elif key == 'interactions':
                    for index, item in enumerate(value):
                        value[index] = Interaction.to_dict(value[index])
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
        if hasattr(obj, 'settings'):
            settings:dict = obj.settings
            if settings:
                for key in settings:
                    settings[key] = Setting.de_json(settings.get(key))
                obj.settings = settings
        if hasattr(obj, 'interactions'):
            interactions:list = obj.interactions
            if interactions:
                for key in interactions:
                    interactions[key] = Interaction.de_json(interactions.get(key))
                obj.interactions = interactions
        return obj
        
    def from_string(string:str):
        return jsonpickle.decode(string)

    def get_setting(self, account:str):
        try:
            setting:Setting = self.settings.get(account)
            if setting:
                return setting
            return None
        except:
            return None

    def add_interaction(self, interaction:Interaction):
        if not self.interactions:
            self.interactions = list()
        self.interactions.append(interaction)

    @persistence_decorator
    def set_setting(self, account:str, setting:Setting=None):
        if setting:
            self.settings[account] = setting
            return setting
        else:
            setting = Setting(account)
            if not self.settings:
                self.settings = dict()
            self.settings[account] = setting
            return setting

    @persistence_decorator
    def set_comment(self, account:str, text:str):
        setting = self.settings.get(account)
        if not setting:
            return False
        setting.set_comment(text)
        self.settings[account] = setting
        return True

    def save(self):
        config.set_settings(self.to_dict())