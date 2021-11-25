"""
GroupMe bot for prayer.

@author Andrew Watson

"""

import json
import os
import random
from urllib.parse import urlencode
import requests
from google_api_helper import GoogleHelper
import random

class Bot:
    # get the bot token from json
    __secrets = json.loads(os.environ["GROUPME_BOT_SECRETS"])
    BOT_ID = __secrets['bot_id']
    BASE_URL = "https://api.groupme.com/v3/"

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

    def getPersonToPrayFor(self, google_data: list, already_prayed_for):
        """
        Given the google data and the already_prayed_for object, figure out who to pray for next randomly.
        This function looks at the number of rows and which indexes have already been chosen (from the already prayed file)
        and chooses an index that has not been chosen yet.
        Returns an array where the index 0 is the name and index 1 is the request.
            Also returns the updated already_prayed_for object to be saved
        """

        # wrap google_data into a list of dictionaries that will maintain the index numbers of the people
        wrapped_data = []
        for i in range(len(google_data)):
            wrapped_data.append({
                "index": i,
                "data": google_data[i]
            })
        
        # remove already_prayed rows from wrapped data
        for index in already_prayed_for:
            for person in wrapped_data:
                if person["index"] == index:
                    wrapped_data.remove(person)
                    break

        # if data is now empty, do this again with new an empty already_prayed_for
        if len(wrapped_data) == 0:
            return self.getPersonToPrayFor(google_data, [])

        # randomly choose a person
        person = random.choice(wrapped_data)

        # add the index of that person to already_prayed_for
        already_prayed_for.append(person["index"])
        
        return person["data"], already_prayed_for


    def doBot(self):
        g = GoogleHelper()
        google_data = g.getSpreadsheet()
        already_prayed_for = g.getAlreadyPrayedFor()
        person_data, new_already_prayed_for = self.getPersonToPrayFor(google_data, already_prayed_for)
        self.sendMsg(self.BOT_ID, self.generateMessage(person_data[0], person_data[1]))
        g.updateAlreadyPrayedFor(new_already_prayed_for)

def main():
    b = Bot()
    b.doBot()

if __name__ == "__main__":
    main()