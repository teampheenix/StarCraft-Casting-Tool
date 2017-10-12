"""Update Nightbot commands."""
import logging

# create logger
module_logger = logging.getLogger('scctool.tasks.nightbot')

try:
    import requests
    import scctool.settings

except Exception as e:
    module_logger.exception("message")
    raise


def base_headers():
    """Define header."""
    return {"User-Agent": ""}


previousMsg = None


def updateCommand(message):
    """Update command to message."""
    cmd = scctool.settings.config.parser.get("Nightbot", "command")
    global previousMsg

    # Updates the twitch title specified in the config file
    try:
        headers = base_headers()
        headers.update({"Authorization": "Bearer " +
                        scctool.settings.config.parser.get("Nightbot", "token")})

        response = requests.get(
            "https://api.nightbot.tv/1/commands",
            headers=headers)

        response.raise_for_status()

        cmdFound, skipUpdate, id = findCmd(response.json(), cmd, message)

        if(skipUpdate):
            previousMsg = message
            msg = _("Nightbot Command '{}' was already set to '{}'").format(
                cmd, message)
            success = True
            return msg, success

        if(cmdFound):
            put_data = {"message": message}
            requests.put("https://api.nightbot.tv/1/commands/" + id,
                         headers=headers,
                         data=put_data).raise_for_status()
        else:
            post_data = {"message": message,
                         "userLevel": "everyone",
                         "coolDown": "5",
                         "name": cmd}

            requests.post("https://api.nightbot.tv/1/commands",
                          headers=headers,
                          data=post_data).raise_for_status()

        previousMsg = message

        msg = _("Updated Nightbot Command '{}' to '{}'").format(cmd, message)
        success = True

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = "Nightbot API-Error: {}"
        if(status_code == 403):
            msg = error_msg.format(_("Forbidden - Do you have permission?"))
        elif(status_code == 401):
            msg = error_msg.format(_("Unauthorized - Refresh your token!"))
        elif(status_code == 429):
            msg = error_msg.format(_("Too Many Requests."))
        else:
            msg = str(e)
        success = False
        module_logger.exception("message")
    except Exception as e:
        msg = str(e)
        success = False
        module_logger.exception("message")
    finally:
        return msg, success


def findCmd(response, cmd, msg):
    """Find command in API data."""
    for i in range(0, response['_total']):
        if(response['commands'][i]['name'] == cmd):
            if(response['commands'][i]['message'] == msg):
                return True, True, response['commands'][i]['_id']
            else:
                return True, False, response['commands'][i]['_id']

    return False, False, ''
