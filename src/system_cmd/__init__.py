__version__ = '1.1.8'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .meat import *
from .interface import *
from .structures import *


