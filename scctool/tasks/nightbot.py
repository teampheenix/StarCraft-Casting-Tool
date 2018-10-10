"""Update Nightbot commands."""
import logging

import requests

import scctool.settings

# create logger
module_logger = logging.getLogger(__name__)


def base_headers():
    """Define header."""
    return {"User-Agent": ""}


previousMsg = dict()


def updateCommand(data):
    """Update command to message."""
    global previousMsg

    # Updates the twitch title specified in the config file
    try:
        headers = base_headers()
        headers.update({"Authorization": "Bearer " +
                        scctool.settings.config.parser.get("Nightbot",
                                                           "token")})

        response = requests.get(
            "https://api.nightbot.tv/1/commands",
            headers=headers)

        response.raise_for_status()
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
        yield '', msg, success, False
    except Exception as e:
        msg = str(e)
        success = False
        module_logger.exception("message")
        yield '', msg, success, False

    for cmdFound, skipUpdate, id, cmd, message in \
            findCommands(response.json(), data):
        try:
            deleted = False
            if(skipUpdate):
                previousMsg[cmd] = message
                msg = _("Nightbot command '{}' " +
                        "was already set to '{}'").format(
                    cmd, message)
                success = True
                yield cmd, msg, success, False
                continue
            elif(cmdFound):
                if message != "__DELETE__":
                    put_data = {"message": message}
                    requests.put("https://api.nightbot.tv/1/commands/" + id,
                                 headers=headers,
                                 data=put_data).raise_for_status()
                else:
                    requests.delete("https://api.nightbot.tv/1/commands/" + id,
                                    headers=headers).raise_for_status()
                    deleted = True
            elif(message != "__DELETE__"):
                post_data = {"message": message,
                             "userLevel": "everyone",
                             "coolDown": "5",
                             "name": cmd}

                requests.post("https://api.nightbot.tv/1/commands",
                              headers=headers,
                              data=post_data).raise_for_status()
            else:
                deleted = True

            previousMsg[cmd] = message

            if deleted:
                msg = _("Deleted command '{}'").format(cmd)
            else:
                msg = _("Updated Nightbot command '{}' to '{}'").format(
                    cmd, message)
            success = True

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_msg = "Nightbot API-Error: {}"
            if(status_code == 403):
                msg = error_msg.format(
                    _("Forbidden - Do you have permission?"))
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
            yield cmd, msg, success, deleted

    return


def findCommands(response, data):
    commands_found = dict()
    for i in range(0, response['_total']):
        commands_found[response['commands'][i]['name']] = i
    for cmd, msg in data.items():
        if cmd in commands_found:
            idx = commands_found[cmd]
            if (response['commands'][idx]['message'] == msg and
                    msg != "__DELETE__"):
                yield True, True, response['commands'][idx]['_id'], cmd, msg
            else:
                yield True, False, response['commands'][idx]['_id'], cmd, msg
        else:
            yield False, False, '', cmd, msg
