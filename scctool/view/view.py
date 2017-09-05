#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.view')

try:
    import platform
    import base64
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtQml import *

    import scctool.settings
    import scctool.obs
    import time
    import shutil
    import os
    import re

except Exception as e:
    module_logger.exception("message")
    raise
