import os
import sys

# Ensure UTF-8 output on Windows / charmap consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.dev")

import django
django.setup()

from support_desk.models import HelpArticle

articles = HelpArticle.objects.select_related("category").order_by("category__sort_order", "sort_order", "slug")
print(f"Total Help Articles: {articles.count()}")
for a in articles:
    print(f"- {a.slug} (Category: {a.category.key if a.category else None}, Title DE: {a.title_de})")
