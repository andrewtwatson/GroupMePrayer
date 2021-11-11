# GroupMePrayer
GroupMe bot for daily prayer for people in FG.

People will put their prayer requests in a Google Sheet. Then from a Heroku app, this bot will post to GroupMe once per day. It will continue until it is turned off.

Rows can be added to the end of the spreadsheet, modified, or deleted and everything will continue to work fine.
It would be good to setup your google form such that people can only submit one response, but can edit their response if they want to. You can delete and add rows without hurting anything.

### Set Up
- Create a copy of `secrets.template.json` named `secrets.json`.
- Register a bot with groupme. Add your bot_token to `secrets.json`.
- Register your sheet with Google Cloud Platform
  - Run `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib` to get the needed libraries
  - Use open Google's Cloud Console (console.cloud.google.com), open a project and enable the sheets API.
  - Create a service account.
    - Generate a key pair for it. Save the private key as `google_client_secret.json` in the root directory of the project.
    - Similar to this https://denisluiz.medium.com/python-with-google-sheets-service-account-step-by-step-8f74c26ed28e
- Create your Google Form. Share the sheet created by it with your Google Service Account's email.
  - It should have two questions: first the persons name and then their prayer request
  - Add the spreadsheet_id to `secrets.json`. The url for your sheet looks like "docs.google.com/spreadsheets/d/<spreadsheet_id>/edit"