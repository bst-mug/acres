"""
Root package.
"""
__all__ = ['constants']

import logging
import os
import shutil
from logging.config import fileConfig

# Automatically switch to the right working directory.
# This avoids lots of KeyError when it is set to something different than the root project folder.
# This is also needed for building docs, as they are initiated from the "docs" folder.
# Working directory must be the root project folder, which is the parent folder of this init file.
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Automatically create config.ini out of default if not present
if "config.ini" not in os.listdir(os.getcwd()):
    shutil.copyfile("config.ini.default", "config.ini")

# Setup logging
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
