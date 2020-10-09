"""Provide match grabbers."""

from scctool.matchgrabber.alpha import MatchGrabber as MatchGrabberAlpha
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabber
from scctool.matchgrabber.rsl import MatchGrabber as MatchGrabberRSL
from scctool.matchgrabber.rstl import MatchGrabber as MatchGrabberRSTL
from scctool.matchgrabber.ctl import MatchGrabber as MatchGrabberCTL
from scctool.matchgrabber.spire import MatchGrabber as MatchGrabberSpire

__all__ = ["MatchGrabber", "MatchGrabberAlpha",
           "MatchGrabberRSTL", "MatchGrabberRSL", "MatchGrabberCTL",
           "MatchGrabberSpire"]
