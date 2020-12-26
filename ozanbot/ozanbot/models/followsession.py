from typing import Optional
from ozanbot.models.interaction import Interaction
from ozanbot.models.persistence import Persistence, persistence_decorator
from ozanbot.models.instasession import InstaSession
import time


class FollowSession(InstaSession):
    def __init__(self, user_id:int, target:str=None, message_id:int=None, comment_bool:bool=False, interaction:Optional[Interaction]=None) -> None:
        super(InstaSession, self).__init__(method=Persistence.FOLLOW, user_id=user_id, message_id=message_id)
        self.target = target
        self.count = 0
        self.comment_bool = comment_bool
        self.interaction = interaction

    def __repr__(self) -> str:
        return f'Follow<{self.target}>'

    def get_target(self):
        return self.target

    def get_count(self):
        return self.count

    def get_scraped(self):
        if not self.interaction.scraped:
            return list()
        return self.interaction.scraped.copy()

    def get_followed(self):
        if not self.interaction.followed:
            return list()
        return self.interaction.followed.copy()

    def get_failed(self):
        if not self.interaction.failed:
            return list()
        return self.interaction.failed.copy()

    @persistence_decorator
    def set_interaction(self, interaction):
        self.interaction = interaction

    @persistence_decorator
    def set_target(self, target):
        self.target = target

    @persistence_decorator
    def set_count(self, count):
        self.count = count

    @persistence_decorator
    def set_comment_bool(self, value):
        self.comment_bool = value

    @persistence_decorator
    def set_scraped(self, scraped):
        self.interaction.scraped = scraped

    @persistence_decorator
    def set_followed(self, followed):
        self.interaction.followed = followed

    @persistence_decorator
    def set_failed(self, failed):
        self.interaction.failed = failed

    @persistence_decorator
    def set_liked(self, liked):
        self.interaction.liked = liked

    @persistence_decorator
    def set_commented(self, commented):
        self.interaction.commented = commented

    @persistence_decorator
    def add_followed(self, username):
        if not self.interaction.followed:
            self.interaction.followed = list()
        self.interaction.followed.append(username)

    @persistence_decorator
    def add_failed(self, failed):
        if not self.interaction.failed:
            self.interaction.failed = list()
        self.interaction.failed.append(failed)

    @persistence_decorator
    def add_commented(self, commented):
        if not self.interaction.commented:
            self.interaction.commented = list()
        self.interaction.commented.append(commented)

    @persistence_decorator
    def add_liked(self, liked):
        if not self.interaction.liked:
            self.interaction.liked = list()
        self.interaction.liked.append(liked)
