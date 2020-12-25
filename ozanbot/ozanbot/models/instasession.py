from ozanbot.models.persistence import persistence_decorator
from ozanbot.config import config
from ozanbot.bot.commands import *
from ozanbot import *
import os

class InstaSession(Persistence):
    def __init__(self, user_id, message_id=None, method=Persistence.INSTASESSION):
        super().__init__(method, user_id, message_id=None)
        self.username = None
        self.password = None
        self.security_code = None
        self.code_request = 0

    @persistence_decorator
    def set_username(self, username):
        self.username = username

    @persistence_decorator
    def set_password(self, password):
        self.password = password

    @persistence_decorator
    def set_scode(self, scode):
        self.security_code = scode

    @persistence_decorator
    def increment_code_request(self):
        self.code_request += 1

    def set_session(self, session:str=None):
        # Localhost
        config.set(f'instasession:{self.user_id}', self.username if session is None else session)

    def get_session(self):
        # Localhost
        session:str = config.get(f'instasession:{self.user_id}')

        if not session:
            return None
        self.username = str(session)
        return str(session)

    def save_creds(self):
        """
        Store working instagram credentials (username and password)
        """
        creds = config.get('instacreds:{}'.format(self.user_id))
        # Localhost
        if not creds:
            creds = dict()
        creds[self.username] = self.password
        config.set('instacreds:{}'.format(self.user_id), creds)

    def get_creds(self):
        session = self.get_session()

        creds = config.get('instacreds:{}'.format(self.user_id))
        if not creds:
            return False
        else:
            self.set_username(session if isinstance(session, str) else list(creds.keys())[0])

            if creds.get(self.username):
                self.set_password(creds.get(self.username))
                return True
            else:
                return False

    def delete_creds(self):
        session = self.get_session()
        self.username = None
        self.password = None

        creds = config.get(f'instacreds:{self.user_id}')
        try: del creds[session]
        except: pass
        config.set('instacreds:{}'.format(self.user_id), creds)

        newsession = None
        for key in list(creds.keys()):
            if key != session:
                
                newsession = key
                self.set_session(key)
                self.set_username(key)
                break
        applogger.debug(f'Set session: {newsession}')

        if not newsession:
            self.set_session(None)            

    def get_all_creds(self):
        creds = config.get('instacreds:{}'.format(self.user_id))
        if not creds:
            return None
        
        hascreds = False
        for cred in creds:
            if creds.get(cred):
                hascreds = True
                break
        if not hascreds: return None
        return creds



            