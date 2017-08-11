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
      headers = {'Accept': 'application/vnd.twitchtv.v3+json',\
               'Authorization': 'OAuth ' + alphasc2tool.settings.oauth,\
               'Client-ID': alphasc2tool.settings.clientID}
      params = {'channel[status]': newTitle, 'channel[game]': 'StarCraft II'}
      
      r = requests.put('https://api.twitch.tv/kraken/channels/' + alphasc2tool.settings.twitchChannel,\
                     headers = headers, params = params).raise_for_status()
      msg = "Updated stream title of "+alphasc2tool.settings.twitchChannel+' to: "'\
            + newTitle.encode("ascii", "ignore").decode()+'"'
            
   except Exception as e:
      msg = str(e)
      module_logger.exception("message") 

   return msg