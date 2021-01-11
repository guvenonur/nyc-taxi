import os
import sys
from util.config.config import ConfigParser

path = sys.argv[-1:][0] if sys.argv[-1:][0].endswith('.ini') else os.environ['CONFIG']

if not os.path.exists(path):
    path = './default.ini'

config = ConfigParser.load(path)
