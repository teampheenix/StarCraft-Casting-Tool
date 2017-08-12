#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('alphasc2tool.twitch')

try:
   import requests
   import alphasc2tool.settings
except Exception as e:
    module_logger.exception("message") 
    raise  


def updateTitle(newTitle):
    
   #Updates the twitch title specified in the config file 
   try:
      twitchChannel = alphasc2tool.settings.Config.get("Twitch", "Channel")
      clientID  = alphasc2tool.settings.Config.get("Twitch", "clientID")
      oauth = alphasc2tool.settings.Config.get("Twitch", "oauth")

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