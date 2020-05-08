import sys
sys.path.append('../spotifython')

from user import *
from spotifython import Spotifython as sp
import os

USER_ID = os.environ['USER_ID']
NO_ACCESS_TOKEN = os.environ['NO_ACCESS_TOKEN']
ALL_ACCESS_TOKEN = os.environ['ALL_ACCESS_TOKEN']
INVALID_TOKEN = 'deadbeef'
