"""Update the twitch title to the title specified in the config file."""
import logging

import requests

import scctool.settings

# create logger
module_logger = logging.getLogger(__name__)

previousTitle = None


def updateTitle(newTitle):
    """Update the twitch title to the title specified in the config file."""
    global previousTitle

    try:
        twitchChannel = scctool.settings.config.parser.get(
            "Twitch", "Channel").strip()
        userID = getUserID(twitchChannel)

        clientID = scctool.settings.safe.get('twitch-client-id')
        oauth = scctool.settings.config.parser.get("Twitch", "oauth")

        headers = {'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': 'OAuth ' + oauth,
                   'Client-ID': clientID}

        params = {'channel[status]': newTitle}

        if scctool.settings.config.parser.getboolean("Twitch", "set_game"):
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

    clientID = scctool.settings.safe.get('twitch-client-id')
    headers = {'Accept': 'application/vnd.twitchtv.v5+json',
               'Client-ID': clientID}
    params = {'login': user}

    response = requests.get('https://api.twitch.tv/kraken/users',
                            headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data['users'][0]['_id']


# def addCommunity(channelID):
#     scctCommunity = 'a021033c-a1d3-4be4-866b-56b9a5f9980c'
#     clientID = scctool.settings.safe.get('twitch-client-id')
#     oauth = scctool.settings.config.parser.get("Twitch", "oauth")
#     headers = {'Accept': 'application/vnd.twitchtv.v5+json',
#                'Authorization': 'OAuth ' + oauth,
#                'Content-Type': 'application/json',
#                'Client-ID': clientID}
#
#     url = 'https://api.twitch.tv/kraken/channels/{}/communities'.format(
#         channelID)
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     communities = list()
#     for community in data.get('communities', list()):
#         communities.append(community['_id'])
#     if scctCommunity not in communities:
#         if len(communities) >= 3:
#             communities.pop()
#         communities.append(scctCommunity)
#         data = {'community_ids': communities}
#         response = requests.put(url, headers=headers, json=data)
#         response.raise_for_status()
