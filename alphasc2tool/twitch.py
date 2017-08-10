#!/usr/bin/env python
import requests
import alphasc2tool.settings

def updateTitle(newTitle):
    
   #Updates the twitch title specified in the config file 
   
   headers = {'Accept': 'application/vnd.twitchtv.v3+json',\
              'Authorization': 'OAuth ' + alphasc2tool.settings.oauth,\
              'Client-ID': alphasc2tool.settings.clientID}
   params = {'channel[status]': newTitle, 'channel[game]': 'StarCraft II'}
   
   r = requests.put('https://api.twitch.tv/kraken/channels/' + alphasc2tool.settings.twitchChannel,\
                    headers = headers, params = params).raise_for_status()
   msg = "Updated stream title of "+alphasc2tool.settings.twitchChannel+' to: "'\
          + newTitle.encode("ascii", "ignore").decode()+'"'
   
   return msg