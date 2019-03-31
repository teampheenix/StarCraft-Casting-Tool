"""Provide gettext translations."""
import gettext as gt
import logging
import sys

import scctool.settings
import scctool.settings.config

module_logger = logging.getLogger(__name__)

this = sys.modules[__name__]
this.translation = gt.NullTranslations()


def gettext(msg):
    """Return gettext translation."""
    return this.translation.gettext(msg)


def set_language():
    """Set language in PyQt5 and gettext."""
    global this
    lang = scctool.settings.config.parser.get("SCT", "language")
    localesDir = scctool.settings.getLocalesDir()

    try:
        this.translation = gt.translation(
            'messages',
            localedir=localesDir,
            languages=[lang])
    except Exception:
        this.translation = gt.NullTranslations()
        module_logger.exception(f"Lang '{lang}', dir '{dir}':")
