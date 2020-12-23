from typing import Dict, List, Union, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from instaclient.instagram import *
    from instaclient.client.instaclient import InstaClient


class Interaction:
    def __init__(self,
    target:Union['Profile', str],
    scraped:List[str]=None,
    failed:List[str]=None,
    followed:List['Profile']=None,
    liked:List['Post']=None,
    commented:List['Post']=None) -> None:
        self.target = target
        self.scraped = scraped
        self.failed = failed
        self.followed = followed
        self.liked = liked
        self.commented = commented

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Interaction):
            if self.target == o.target:
                for item in o.followed:
                    if item not in self.followed:
                        return False
                for item in o.liked:
                    if item not in self.liked:
                        return False
                for item in o.commented:
                    if item not in self.liked:
                        return False
                return True
        return False

    def __getitem__(self, item: str):
        return self.__dict__[item]

    def to_dict(self):
        data = dict()

        for key in iter(self.__dict__):
            value = self.__dict__[key]
            if isinstance(value, list):
                for index, item in enumerate(value):
                    if hasattr(item, 'to_dict'):
                        value[index] = value[index].to_dict()
            else:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value
        return data

    @classmethod
    def de_json(cls, data: dict, client:Optional['InstaClient']=None):

        if not data:
            return None

        for key in data:
            if hasattr(data[key], 'de_json'):
                data[key] = Profile.de_json(data[key], client)
            if isinstance(data[key], List[Dict]):
                if key == 'followed':
                    data[key] = Profile.de_json(data[key], client)
                elif key in ('liked', 'commented'):
                    data[key] = Post.de_json(data[key], client)

        obj = cls(**data)  # type: ignore[call-arg]
        return obj

    

    def set_scraped(self, scraped:List[str]):
        self.scraped = scraped

    def add_followed(self, profile:'Profile'):
        if profile not in self.followed:
            self.followed.append(profile)

    def add_liked(self, post:'Post'):
        if post not in self.liked:
            self.liked.append(post)

    def add_commented(self, post:'Post'):
        if post not in self.liked:
            self.liked.append(post)
