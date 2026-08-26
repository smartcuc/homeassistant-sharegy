###################
# tenants/models.py
###################

import uuid
from django.db import models
from django.utils.text import slugify


# Konsolidiert: Das zentrale Tenant-Modell befindet sich in core.models
from core.models import Tenant

__all__ = ["Tenant"]
