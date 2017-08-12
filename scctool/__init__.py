__all__ = ['settings','matchdata','twitch','view','controller','apithread']
# deprecated to keep older scripts who import this from breaking
import scctool.settings
import scctool.twitch
import scctool.nightbot
import scctool.matchdata
import scctool.view
import scctool.apithread

from scctool.matchdata import *
from scctool.view import *
from scctool.controller import *
from scctool.apithread import *
from scctool.nightbot import *