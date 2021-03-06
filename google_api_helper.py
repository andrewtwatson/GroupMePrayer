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
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = None
    service = None
    SPREADSHEET_RANGE = 'B2:C655366'
    ALREADY_PRAYED_FOR_CELL = 'I1'

    __secrets = json.loads(os.environ["GROUPME_BOT_SECRETS"])
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
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.SPREADSHEET_RANGE)
        response = request.execute()
        values = response['values']
        
        # filter out blank rows
        values = list(filter(lambda a: a != [], values))
        return values
    
    def getAlreadyPrayedFor(self):
        """
        The cell I1 is used to store a JSON object for the people who have already been prayed for and who's next.
        Get the cell and return it as a JSON object. If it is empty, give a blank json object back
        """
        self._setupCreds()
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.ALREADY_PRAYED_FOR_CELL)
        response = request.execute()
        try:
            json_string = response['values'][0][0]
        except KeyError:
            return {'past': [], 'next': -1}
        return json.loads(json_string)
    
    def updateAlreadyPrayedFor(self, json_object):
        """
        The cell I1 is used to store a JSON object for the people who have already been prayed for and who's next.
        Update the cell with a new JSON object.
        """
        self._setupCreds()
        value_range_body = {
            "range": self.ALREADY_PRAYED_FOR_CELL,
            "majorDimension": "ROWS",
            "values": [
                [json.dumps(json_object)]
            ]
        }
        request = self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=self.ALREADY_PRAYED_FOR_CELL, valueInputOption='RAW', body=value_range_body)
        request.execute()