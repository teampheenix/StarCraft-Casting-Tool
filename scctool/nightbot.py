#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.nightbot')

try:
    import requests, json
    import scctool.settings

except Exception as e:
    module_logger.exception("message") 
    raise  
    
def base_headers():
    return {"User-Agent": ""}
    
def updateCommand(message):
    
    cmd = scctool.settings.Config.get("NightBot","command")

    #Updates the twitch title specified in the config file 
    try:
        headers = base_headers()
        headers.update({"Authorization": "Bearer " + scctool.settings.Config.get("NightBot","token")})
        
        response = requests.get("https://api.nightbot.tv/1/commands", headers=headers).json()
        
        if(response['status']!=200):
            return "NightBot-API: "+str(response['status'])+" - "+response['message']
        
        cmdFound, skipUpdate, id = findCmd(response, cmd, message)
        
        if(skipUpdate):
            return "NightBot Command '"+cmd+"' was already set to '"+message+"'" 
            
        if(cmdFound):
            put_data = {"message": message}
            response = requests.put("https://api.nightbot.tv/1/commands/"+id,
                             headers=headers,
                             data=put_data)
            print(response.json())
            
        else:
            post_data = {"message": message,
                     "userLevel": "everyone",
                     "coolDown":"5",
                     "name": cmd}
        
            response = requests.post("https://api.nightbot.tv/1/commands",
                             headers=headers,
                             data=post_data)
            print(response.json())
     
        msg = "Updated NightBot Command '"+cmd+"' to '"+message+"'"        
            
    except Exception as e:
        msg = str(e)
        module_logger.exception("message") 

    return msg
    

def findCmd(response, cmd, msg):
    for i in range(0,response['_total']):
        if(response['commands'][i]['name'] == cmd):
            if(response['commands'][i]['message'] == msg):
                return True, True, response['commands'][i]['_id']
            else:
                return True, False, response['commands'][i]['_id']
            
            
    return False, False, ''