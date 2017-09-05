__all__ = ["custom", "alpha", "rstl", "MatchGrabber"]

from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent

class MatchGrabber(MatchGrabberParent):

    def __init__(self, *args):
        """Init match grabber."""
        super(MatchGrabber, self).__init__(*args)
