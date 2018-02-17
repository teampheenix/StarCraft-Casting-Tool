"""Update the twitch title to the title specified in the config file."""
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

previousTitle = None


def updateTitle(newTitle):
    """Update the twitch title to the title specified in the config file."""
    global previousTitle

    try:
        twitchChannel = scctool.settings.config.parser.get(
            "Twitch", "Channel").strip()
        clientID = scctool.tasks.webapp.TWITCH_CLIENT_ID
        oauth = scctool.settings.config.parser.get("Twitch", "oauth")

        headers = {'Accept': 'application/vnd.twitchtv.v3+json',
                   'Authorization': 'OAuth ' + oauth,
                   'Client-ID': clientID}
        params = {'channel[status]': newTitle, 'channel[game]': 'StarCraft II'}

        requests.put('https://api.twitch.tv/kraken/channels/' + twitchChannel,
                     headers=headers, params=params).raise_for_status()
        msg = _('Updated Twitch title of {} to: "{}"').format(twitchChannel, newTitle)
        success = True
        previousTitle = newTitle

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = "Twitch API-Error: {}"
        if(status_code == 404):
            msg = _("Not Found - Channel '{}' not found.").format(twitchChannel)
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
