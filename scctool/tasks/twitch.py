"""Update the twitch title to the title specified in the config file."""
import logging

import requests
from requests.api import request

import scctool.settings
import scctool.settings.translation


# create logger
module_logger = logging.getLogger(__name__)

previousTitle = None
_ = scctool.settings.translation.gettext


def updateTitle(newTitle):
    """Update the twitch title to the title specified in the config file."""
    global previousTitle
    twitchChannel = scctool.settings.config.parser.get(
        "Twitch", "Channel").strip()

    try:
        userID = getUserID(twitchChannel)

        clientID = scctool.settings.safe.get('twitch-client-id')
        oauth = scctool.settings.config.parser.get("Twitch", "oauth")

        headers = {'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': f'Bearer {oauth}',
                   'Client-Id': clientID}

        data = {'title': newTitle}

        if scctool.settings.config.parser.getboolean("Twitch", "set_game"):
            data['game_id'] = '490422'

        requests.patch(
            url=f'https://api.twitch.tv/helix/channels?broadcaster_id={userID}', headers=headers, json=data).raise_for_status()
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


def getUserID(login):
    """Get a user's ID from twitch API."""
    client_id = scctool.settings.safe.get('twitch-client-id')
    url = 'https://api.twitch.tv/helix/users'
    oauth = scctool.settings.config.parser.get("Twitch", "oauth")
    headers = {'Client-Id': client_id, 'Authorization': f'Bearer {oauth}'}
    params = {'login': login}

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    try:
        return r.json().get('data')[0]['id']
    except IndexError:
        raise ValueError(
            f'Twitch channel "{login}" not found - please check your settings.')


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
