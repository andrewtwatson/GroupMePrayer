"""
Sets up the environmental variables from secrets.json and google_client_secret.json, then runs bot.py.
This is just for the convienence of testing on a local machine instead of on heroku.

@author Andrew Watson

"""
import os

if __name__ == "__main__":
    # get contents of secrets.json
    f = open("secrets.json", "r")
    os.environ["GROUPME_BOT_SECRETS"] = f.read()
    f.close()

    # get contents of google_client_secret.json
    f = open("google_client_secret.json", "r")
    os.environ["GROUPME_BOT_GOOGLE_CLIENT_SECRET"] = f.read()
    f.close()

    import bot
    bot.main()