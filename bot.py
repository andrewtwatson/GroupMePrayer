"""
GroupMe bot for prayer.

@author Andrew Watson

"""

import json
import random
from urllib.parse import urlencode
import requests
from google_api_helper import GoogleHelper

# get the bot token from json
__secrets = json.load(open('secrets.json'))
BOT_ID = __secrets['bot_id']
BASE_URL = "https://api.groupme.com/v3/"

def generateMessage(name, prayerRequest):
    """
    Generate a message to send to the groupme. The goal is to make a 
    unique-seeming message that includes the name and what to pray for.
    """
    # make a list of params with one of each param_option
    param_options = [
        ("Hey", "Howdy", "Hi", "Good morning"),
        ("y'all", "family", "everyone", "guys"),
        ("Today, we are gonna be praying", "The person of the day to be praying", "Today, we're praying", "Today, please pray"),
        ("They wrote", name + " wrote", "They are asking for prayer for this"),
        ("Please join in praying for " + name + " today!", "Pray boldly! God hears your prayers! He is not far off.", \
            "God is good! O how beautiful he is! Seek him today.", 
            "Psalm 27 -> I believe that I shall look upon the goodness of the LORD in the land of the living!\n" \
                "Wait for the LORD; be strong, and let your heart take courage;wait for the LORD!\""),
        
        # The vision should only come up maybe once a week on average
        ("\n\nJust as a reminder, the reason we do this everyday is to live what it means to be a Family Member" \
            " towards each other and bear each others burdens. Galatians 6:2 says \"Bear one another's burdens, and so fulfill the law of Christ.\"" \
            " The law of Chist is to love above all else! To love the Lord your God and to love your brothers and sisters!" \
            " This is one way we do that!", "", "", "", "", "", "")
    ]
    params = []
    for p in param_options:
        params.append(random.choice(p))

    template = "%s %s! %s for " + name + ". %s: \n" + prayerRequest + "\n\n%s%s"
    message = template % tuple(params)
    print(message)
    return message


def sendMsg(bot_id, msg):
    """
    Use the bot to send a message to the groupme
    """
    url = BASE_URL + "bots/post?"
    payload = {"bot_id": bot_id, "text": msg}
    r = requests.post(url, params=payload)


# generateMessage("Andrew", "Pray for my back")
# sendMsg(BOT_ID, "hi mikato")

g = GoogleHelper()
google_data = g.getSpreadsheet()
# sendMsg(BOT_ID, generateMessage(google_data[0][0], google_data[0][1]))
# sendMsg(BOT_ID, generateMessage(google_data[1][0], google_data[1][1]))

from pprint import pprint
pprint(google_data)