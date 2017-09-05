#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.tasks.twitch')

try:
   import requests
   import scctool.settings
   import scctool.tasks.webapp
except Exception as e:
    module_logger.exception("message")
    raise


def updateTitle(newTitle):

   #Updates the twitch title specified in the config file
   try:
      twitchChannel = scctool.settings.config.parser.get("Twitch", "Channel")
      clientID  = scctool.tasks.webapp.TWITCH_CLIENT_ID
      oauth = scctool.settings.config.parser.get("Twitch", "oauth")

      headers = {'Accept': 'application/vnd.twitchtv.v3+json',\
               'Authorization': 'OAuth ' + oauth,\
               'Client-ID': clientID}
      params = {'channel[status]': newTitle, 'channel[game]': 'StarCraft II'}

      r = requests.put('https://api.twitch.tv/kraken/channels/' + twitchChannel,\
                     headers = headers, params = params).raise_for_status()
      msg = "Updated stream title of "+twitchChannel+' to: "'\
            + newTitle.encode("ascii", "ignore").decode()+'"'

   except Exception as e:
      msg = str(e)
      module_logger.exception("message")

   return msg
