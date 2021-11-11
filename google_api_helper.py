"""
Handles all the API calls with google sheets. This is just to keep bot.py from being cluttered.
A lot of this is adapted from Google's quickstart.py and from https://denisluiz.medium.com/python-with-google-sheets-service-account-step-by-step-8f74c26ed28e.

@author Andrew Watson

"""
import os
import json
from apiclient import discovery
from google.oauth2 import service_account

class GoogleHelper:
    """
    Provides an easy interface for interacting with the Google spreadsheet
    """
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = None
    service = None
    spreadsheet_range = 'B2:C655366'

    __secrets = json.load(open('secrets.json'))
    spreadsheet_id = __secrets['spreadsheet_id']

    def _setupCreds(self):
        """
        Set up the credentials of the client.
        """
        google_client_secret = json.loads(os.environ["GROUPME_BOT_GOOGLE_CLIENT_SECRET"])
        if not self.credentials or not self.service or (self.credentials.expired and self.credentials.refresh_token):
            self.credentials = service_account.Credentials.from_service_account_info(google_client_secret, scopes=self.SCOPES)
            self.service = discovery.build('sheets', 'v4', credentials=self.credentials)

    def getSpreadsheet(self):
        """
        Gets the relevant data from the spreadsheet as an array of arrays.
        """
        self._setupCreds()
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.spreadsheet_range)
        response = request.execute()
        values = response['values']
        
        # filter out blank rows
        values = list(filter(lambda a: a != [], values))
        return values