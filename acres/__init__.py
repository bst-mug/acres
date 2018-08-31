__all__ = ['rater', 'text_cleanser']

import logging
import os
from logging.config import fileConfig

# Automatically switch to the right working directory.
# This avoids lots of KeyError when it is set to something different than the root project folder.
# This is also needed for building docs, as they are initiated from the "docs" folder.
# Working directory must be the root project folder, which is the parent folder of this init file.
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Check if config.ini exists
if "config.ini" not in os.listdir(os.getcwd()):
    raise ValueError("config.ini not found!")

# Setup logging
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
