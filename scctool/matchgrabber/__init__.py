"""Provide match grabbers."""
from scctool.matchgrabber.ctl import MatchGrabber as MatchGrabberCTL
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabber

__all__ = ["MatchGrabber",  "MatchGrabberCTL"]
