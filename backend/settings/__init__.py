import os
import sys

if os.path.exists("/var/www/sharegy"):
    from .prod import *
else:
    from .base import *

if "test" in sys.argv or any("test" in arg for arg in sys.argv):
    SECURE_SSL_REDIRECT = False
