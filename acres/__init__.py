__all__ = ['rater', 'text_cleanser']

import logging
import os
import sys
from logging.config import fileConfig

# Check for the right working directory
# This avoids lots of KeyError when it is set to something different than the root project folder.
# We check for the existence of "setup.py" as a signal of the right directory.
if "setup.py" not in os.listdir(os.getcwd()):
    print("Wrong working directory: " + os.getcwd())
    print("Edit your 'Run Configuration' to point it to the root project folder.")
    sys.exit(1)

# Check if config.ini exists
if "config.ini" not in os.listdir(os.getcwd()):
    print("config.ini not found!")
    sys.exit(2)

# Setup logging
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
