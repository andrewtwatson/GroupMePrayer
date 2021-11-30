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

    def generateMessage(self, name: str, prayerRequest: str, next_person_name: str):
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
                " This is one way we do that!", "", "", "", "", "", "", "", "", ""),
            
            ("Also, " + next_person_name + " will be up tomorrow! If you want to update your prayer requests, go to the Google Form now.",
             "And just so you know, " + next_person_name + " is up next. Go update your requests if you want.",
             next_person_name + " will be up tomorrow. Go update your prayer requests if anything has changed.",
             next_person_name + ", you're up next. Last chance to update your prayer requests!")
        ]
        params = []
        for p in param_options:
            params.append(random.choice(p))

        template = "%s %s! %s for " + name + ". %s: \n" + prayerRequest + "\n\n%s%s\n" + name + ", if you have any prayer requests, you can post them below.\n\n%s"
        message = template % tuple(params)

        return message

    def sendMsg(self, bot_id, msg):
        """
        Use the bot to send a message to the groupme
        """
        url = self.BASE_URL + "bots/post?"
        payload = {"bot_id": bot_id, "text": msg}
        r = requests.post(url, params=payload)

    def getPersonToPrayFor(self, google_data: list, already_prayed_for: dict):
        """
        google_data is the list of data that comes out of the google sheet.
        already_prayed_for is a dict that looks like this:
            {
                'past': [list of indicies of people who have already been prayed for],
                'next': a single int with the index of the next person to pray for.
            }
        
        The way this is works is it wraps each row from google data so that we can remove objects and preserve
        the original indicies. Then remove each 'past' index. If that removed all the people in the list, get a fresh list and start over.
        Then find the next person to pray for, move them from 'next' to 'past', and find a new person to be next.

        Returns the data of the person we are now praying for, data of the next person to pray for, and the already_prayed_for object to save.
        """
        if google_data is None or len(google_data) == 0:
            return None, None

        # wrap google_data into a list of dictionaries that will maintain the index numbers of the people
        wrapped_data = []
        for i in range(len(google_data)):
            wrapped_data.append({
                "index": i,
                "data": google_data[i]
            })
        
        # remove already_prayed_for past rows from wrapped data
        for index in already_prayed_for['past']:
            for person in wrapped_data:
                if person["index"] == index:
                    wrapped_data.remove(person)
                    break

        # if data is now empty, do this again with new an empty already_prayed_for
        if len(wrapped_data) == 0:
            return self.getPersonToPrayFor(google_data, {'past': [], 'next': already_prayed_for['next']})

        # get the next person to pray for and save it for later
        person_to_pray_for = None
        for person in wrapped_data:
            if person['index'] == already_prayed_for['next']:
                person_to_pray_for = person
                break
        # if you couldn't find the next person, choose randomly.
        if person_to_pray_for is None:
            person_to_pray_for = random.choice(wrapped_data)

        # add the person to the already_prayed_for['past'] list, remove from wrapped_data
        already_prayed_for['past'].append(person_to_pray_for['index'])
        wrapped_data.remove(person_to_pray_for)

        # randomly choose a person to pray for next.
        if len(wrapped_data) > 0:
            next_person = random.choice(wrapped_data)
        else:
            # if we just removed the last person, pick randomly from the entire list again.
            # we have to wrap this in the same way we wrapped the google_data at the beginning.
            next_person_index = random.randrange(0, len(google_data))
            next_person_data = google_data[next_person_index]
            next_person = {'index': next_person_index, 'data': next_person_data}
        
        already_prayed_for['next'] = next_person['index']
        
        return person_to_pray_for['data'], next_person['data'], already_prayed_for


    def doBot(self):
        g = GoogleHelper()
        google_data = g.getSpreadsheet()
        already_prayed_for = g.getAlreadyPrayedFor()
        person_data, next_person_data, new_already_prayed_for = self.getPersonToPrayFor(google_data, already_prayed_for)

        if person_data is not None and new_already_prayed_for is not None:
            self.sendMsg(self.BOT_ID, self.generateMessage(person_data[0], person_data[1], next_person_data[0]))
            g.updateAlreadyPrayedFor(new_already_prayed_for)

def main():
    b = Bot()
    b.doBot()

if __name__ == "__main__":
    main()