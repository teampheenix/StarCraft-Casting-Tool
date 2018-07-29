"""Update the twitch title to the title specified in the config file."""
import logging

import requests

import scctool.settings
from scctool.tasks.auth import TWITCH_CLIENT_ID

# create logger
module_logger = logging.getLogger('scctool.tasks.twitch')

previousTitle = None


def updateTitle(newTitle):
    """Update the twitch title to the title specified in the config file."""
    global previousTitle

    try:
        twitchChannel = scctool.settings.config.parser.get(
            "Twitch", "Channel").strip()
        userID = getUserID(twitchChannel)

        clientID = TWITCH_CLIENT_ID
        oauth = scctool.settings.config.parser.get("Twitch", "oauth")

        headers = {'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': 'OAuth ' + oauth,
                   'Client-ID': clientID}

        params = {'channel[status]': newTitle}
        params['channel[game]'] = 'StarCraft II'

        requests.put('https://api.twitch.tv/kraken/channels/' + userID,
                     headers=headers, params=params).raise_for_status()
        msg = _('Updated Twitch title of {} to: "{}"').format(
            twitchChannel, newTitle)
        success = True
        previousTitle = newTitle

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = "Twitch API-Error: {}"
        if(status_code == 404):
            msg = _("Not Found - Channel '{}'"
                    " not found.").format(twitchChannel)
            msg = error_msg.format(msg)
        elif(status_code == 403):
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

    return msg, success


def getUserID(user):

    clientID = TWITCH_CLIENT_ID
    headers = {'Accept': 'application/vnd.twitchtv.v5+json',
               'Client-ID': clientID}
    params = {'login': user}

    response = requests.get('https://api.twitch.tv/kraken/users',
                            headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data['users'][0]['_id']
