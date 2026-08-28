#######################
# helpcenter/models.py
#######################
# Backwards compatibility alias: models now reside in support_desk.models
from support_desk.models import HelpCategory, HelpArticle

__all__ = ["HelpCategory", "HelpArticle"]
