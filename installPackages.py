#!/usr/bin/env python3
import pip
import sys
import platform

system = platform.system()

pip.main(['install', 'PyQt5'])
pip.main(['install', 'requests'])
pip.main(['install', 'configparser'])


if(system=="Windows"):
    pip.main(['install', 'pypiwin32'])
