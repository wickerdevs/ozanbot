from datetime import timedelta
from typing import List


class Setting(object):
    def __init__(self, account:str=None, comment:str=None, interactions:int=None) -> None:
        self.account = account
        self.comment = comment
        self.interactions = interactions

    def __getitem__(self, item: str):
        return self.__dict__[item]

    def set_account(self, account:str):
        self.account = account

    def set_comment(self, text:str):
        self.comment = text

    def get_account(self):
        return self.account

    def get_comment(self):
        return self.comment

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

        return cls(**data)  # type: ignore[call-arg]