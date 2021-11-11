"""
GroupMe bot for prayer.

@author Andrew Watson

"""

import json
import random
from urllib.parse import urlencode
import requests
from google_api_helper import GoogleHelper
import random

class Bot:
    # get the bot token from json
    __secrets = json.load(open('secrets.json'))
    BOT_ID = __secrets['bot_id']
    BASE_URL = "https://api.groupme.com/v3/"
    # json file of the indexes of the people already prayed for.
    ALREADY_PRAYED_FOR = "already_prayed_for.json"

    def generateMessage(self, name: str, prayerRequest: str):
        """
        Generate a message to send to the groupme. The goal is to make a 
        unique-seeming message that includes the name and what to pray for.
        """
        # clean any percent signs form the name, prayerRequest
        name = name.replace("%", "")
        prayerRequest = prayerRequest.replace("%", "")

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
            
            # The vision should only come up maybe once every 10 days on average
            ("\n\nJust as a reminder, the reason we do this every day is to live what it means to be a Family Member" \
                " towards each other and bear each others burdens. Galatians 6:2 says \"Bear one another's burdens, and so fulfill the law of Christ.\"" \
                " The law of Chist is to love above all else! To love the Lord your God and to love your brothers and sisters!" \
                " This is one way we do that!", "", "", "", "", "", "", "", "", "")
        ]
        params = []
        for p in param_options:
            params.append(random.choice(p))

        template = "%s %s! %s for " + name + ". %s: \n" + prayerRequest + "\n\n%s%s\n" + name + ""
        message = template % tuple(params)

        return message

    def sendMsg(self, bot_id, msg):
        """
        Use the bot to send a message to the groupme
        """
        url = self.BASE_URL + "bots/post?"
        payload = {"bot_id": bot_id, "text": msg}
        r = requests.post(url, params=payload)

    def getPersonToPrayFor(self, google_data: list):
        """
        Given the google data and the already_prayed_for file, figure out who to pray for next randomly.
        This function looks at the number of rows and which indexes have already been chosen (from the already prayed file)
        and chooses an index that has not been chosen yet.
        Returns an array where the index 0 is the name and index 1 is the request.
        """
        try:
            file = open(self.ALREADY_PRAYED_FOR, "r")
            already_prayed = json.load(file)
            file.close()
        except OSError:
            already_prayed = []

        # wrap google_data into a list of dictionaries that will maintain the index numbers of the people
        wrapped_data = []
        for i in range(len(google_data)):
            wrapped_data.append({
                "index": i,
                "data": google_data[i]
            })
        
        # remove already_prayed rows from wrapped data
        for index in already_prayed:
            for person in wrapped_data:
                if person["index"] == index:
                    wrapped_data.remove(person)
                    break

        # if data is now empty, wipe the json and run this again. Reset.
        if len(wrapped_data) == 0:
            file = open(self.ALREADY_PRAYED_FOR, "w")
            json.dump([], file)
            file.close()
            return self.getPersonToPrayFor(google_data)

        # randomly choose a person
        person = random.choice(wrapped_data)

        # add the index of that person to already_prayed_for.json
        already_prayed.append(person["index"])
        file = open(self.ALREADY_PRAYED_FOR, "w")
        json.dump(already_prayed, file)
        file.close()

        return person["data"]


    def doBot(self):
        g = GoogleHelper()
        google_data = g.getSpreadsheet()
        person_data = self.getPersonToPrayFor(google_data)
        # self.sendMsg(self.BOT_ID, self.generateMessage(person_data[0], person_data[1]))

if __name__ == "__main__":
    b = Bot()
    b.doBot()