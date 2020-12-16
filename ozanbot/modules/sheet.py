from gspread.client import Client
from instaclient.classes.notification import Notification
from gspread.models import Spreadsheet, Worksheet
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os, re, json, jsonpickle 
from datetime import date, datetime
from .. import applogger
from ..config import config



def auth():
    creds_string = config.get('GSPREAD_CREDS')
    if creds_string == None:
        # use creds to create a client to interact with the Google Drive API
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive']
        # CREDENTIALS HAVE NOT BEEN INITIALIZED BEFORE
        client_secret = os.environ.get('GCLIENT_SECRET')
        if os.environ.get('PORT') in (None, ""):
            # CODE RUNNING LOCALLY
            applogger.debug('DATABASE: Resorted to local JSON file')
            with open('ffinstabot/config/client_secret.json') as json_file:
                client_secret_dict = json.load(json_file)
        else:
            # CODE RUNNING ON SERVER
            client_secret_dict = json.loads(client_secret)

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            client_secret_dict, scope)
        creds_string = jsonpickle.encode(creds)
        config.set('GSPREAD_CREDS', creds_string)
    creds = jsonpickle.decode(creds_string)
    client = gspread.authorize(creds)

    # IF NO SPREADSHEET ENV VARIABLE HAS BEEN SET, SET UP NEW SPREADSHEET
    if config.get('SPREADSHEET') == None:
        spreadsheet = set_sheet(client)
        return spreadsheet
    else:
        SPREADSHEET = config.get('SPREADSHEET')
        spreadsheet = client.open_by_key(SPREADSHEET)
        return spreadsheet


def log(timestamp:datetime, user_id:int or str, action:str):
    spreadsheet = auth()
    logs = spreadsheet.get_worksheet(4)                     
    logs.append_row([str(timestamp), user_id, action])


############################### GENERAL ################################
def find_by_username(user_id:int, sheet:Worksheet, col:int=1) -> None or int:
    """
    Finds the Row Index within the GSheet Database, matching the ``user_id`` argument.
    Returns None if no record is found.

    Args:
        user_id (int): Telegram ID of the user.
        sheet (Worksheet): Worksheet to check.
        col (int, optional): Column to check. Defaults to 1.

    Returns:
        None or list: None if no record is found, int if the record is found.
    """
    if not sheet:
        spreadsheet = auth()
        sheet = spreadsheet.get_worksheet(0)
    column = sheet.col_values(col)
    rows = list()
    for num, cell in enumerate(column):
        if str(cell) == str(user_id):
            rows.append(num + 1)
    if rows == []:
        return None
    return rows[0]


def get_rows(sheet:Worksheet):
    """
    Get a list of the rows' content from the Google Sheets database.

    :param sheet: GSheets worksheet to get data from
    :type sheet: Worksheet

    :return: List of lists, where each sub-list contains a row's contents.
    :rtype: list
    """
    rows:list = sheet.get_all_values()
    return rows


def get_sheet_url(index:int=0):
    """
    Returns the link of a worksheet

    Args:
        index (int, optional): Index of the sheet to get. Can be either 0, 1 or 2. Defaults to 0.

    Returns:
        str: Url of the selected worksheet
    """
    spreadsheet = auth()
    sheet:Worksheet = spreadsheet.get_worksheet(index)
    url = 'https://docs.google.com/spreadsheets/d/{}/edit#gid={}'.format(spreadsheet.id, sheet.id)
    return url


def set_sheet(client:Client):
    """
    Setup spreadsheet database if none exists yet.
    Will save the spreadsheet ID to Heroku Env Variables or to secrets.json file
    The service email you created throught the Google API will create the new spreadsheet and share it with the email you indicated in the GDRIVE_EMAIL enviroment variable. You will find the spreadsheet database in your google drive shared folder.
    Don't change the order of the worksheets or it will break the code.

    :param client: GSpread client to utilize
    :type client: Client
    :return: The newly created spreadsheet
    :rtype: Spreadsheet
    """
    # CREATE SPREADSHEET
    spreadsheet:Spreadsheet = client.create('FFInstaBot')
    config.set('SPREADSHEET', spreadsheet.id)

    settings = spreadsheet.add_worksheet(title='Settings', rows=6, cols=2)
    settings.append_row(['USER ID', 'SETTINGS'])

    follows = spreadsheet.add_worksheet(title='Follows', rows=50, cols=1)
    follows.append_row(['FOLLOWS'])

    notifications = spreadsheet.add_worksheet(title='Notifications', rows=50, cols=2)
    notifications.append_row(['USER ID', 'LAST NOTIFICATION'])

    messages = spreadsheet.add_worksheet(title='Messages', rows=10, cols=2)
    messages.append_row(['USER ID', 'MESSAGE ID'])

    # CREATE LOGS SHEET
    logs = spreadsheet.add_worksheet(title="Logs", rows="500", cols="3")
    logs.append_row(["TIMESTAMP", "USER ID", "ACTION"])

    # DELETE PRE-EXISTING SHEET
    sheet = spreadsheet.get_worksheet(0)
    spreadsheet.del_worksheet(sheet)

    # SHARE SPREADSHEET
    spreadsheet.share(value=config.get('GDRIVE_EMAIL'),
                      perm_type="user", role="owner")
    return spreadsheet