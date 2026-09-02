import os

if os.path.exists("/var/www/sharegy"):
    from .prod import *
else:
    from .base import *
