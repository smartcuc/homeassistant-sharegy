##########################################
# support_desk/services/knowledge_engine.py
##########################################

from typing import List, Dict, Any
from django.db.models import Q
from support_desk.models import HelpCategory, HelpArticle


def search_deflection_articles(query_str: str, limit: int = 4) -> List[Dict[str, Any]]:
    """
    Searches published HelpArticles for deflection suggestions based on a search term.
    """
    if not query_str or len(query_str.strip()) < 3:
        return []

    tokens = [t.strip() for t in query_str.strip().split() if len(t.strip()) > 2]
    q_filter = Q()
    for t in tokens:
        q_filter |= (
            Q(title_de__icontains=t)
            | Q(title_en__icontains=t)
            | Q(summary_de__icontains=t)
            | Q(tags__icontains=t)
        )

    qs = HelpArticle.objects.filter(is_published=True).filter(q_filter).select_related("category").distinct()[:limit]

    results = []
    for art in qs:
        results.append({
            "id": str(art.id),
            "slug": art.slug,
            "title_de": art.title_de,
            "title_en": art.title_en or art.title_de,
            "summary_de": art.summary_de,
            "summary_en": art.summary_en,
            "category_name": art.category.title_de if art.category else "",
            "views_count": art.views_count,
        })
    return results
