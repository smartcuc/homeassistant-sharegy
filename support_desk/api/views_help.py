#################################
# support_desk/api/views_help.py
#################################

from django.db.models import Q, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from support_desk.models import HelpCategory, HelpArticle
from support_desk.api.serializers import (
    HelpCategorySerializer,
    HelpArticleListSerializer,
    HelpArticleDetailSerializer,
    HelpArticleUpdateSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def categories_list(request):
    """Liefert alle aktiven Hilfe-Kategorien."""
    categories = HelpCategory.objects.all().order_by("sort_order", "title_de")
    serializer = HelpCategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def articles_list(request):
    """
    Liefert eine gefilterte Liste von Hilfe-Artikeln.
    Filter: search, category (key), featured (true/false), context_key
    """
    qs = HelpArticle.objects.filter(is_published=True).select_related("category")

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(title_de__icontains=search)
            | Q(title_en__icontains=search)
            | Q(summary_de__icontains=search)
            | Q(summary_en__icontains=search)
            | Q(content_de__icontains=search)
            | Q(content_en__icontains=search)
            | Q(tags__icontains=search)
        )

    category_key = request.GET.get("category", "").strip()
    if category_key:
        qs = qs.filter(category__key=category_key)

    featured = request.GET.get("featured", "").strip().lower()
    if featured in ["1", "true", "yes"]:
        qs = qs.filter(is_featured=True)

    context_key = request.GET.get("context_key", "").strip()
    if context_key:
        qs = qs.filter(context_key=context_key)

    serializer = HelpArticleListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def context_articles(request):
    """
    Liefert kontextspezifische Artikel für den In-App Help-Drawer
    basierend auf dem aktuellen Seiten-Kontext-Key (z. B. 'forecast', 'energy_dashboard').
    """
    key = request.GET.get("key", "").strip()
    if not key:
        # Fallback auf Featured Articles
        qs = HelpArticle.objects.filter(is_published=True, is_featured=True).select_related("category")[:5]
    else:
        qs = HelpArticle.objects.filter(is_published=True, context_key=key).select_related("category")
        if not qs.exists():
            # Fallback auf allgemeine / hervorgehobene Artikel
            qs = HelpArticle.objects.filter(is_published=True, is_featured=True).select_related("category")[:5]

    serializer = HelpArticleListSerializer(qs[:5], many=True)
    return Response({
        "context_key": key,
        "count": len(serializer.data),
        "articles": serializer.data,
    })


@api_view(["GET", "PATCH"])
@permission_classes([AllowAny])
def article_detail(request, slug):
    """
    GET: Lädt Artikel anhand des Slugs und erhöht Views.
    PATCH: Ermöglicht Staff-Mitgliedern das Bearbeiten im Frontend.
    """
    try:
        article = HelpArticle.objects.select_related("category").get(slug=slug)
    except HelpArticle.DoesNotExist:
        return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({"error": "Admin privileges required for editing."}, status=status.HTTP_403_FORBIDDEN)

        serializer = HelpArticleUpdateSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(HelpArticleDetailSerializer(article).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET: View Count inkrementieren
    HelpArticle.objects.filter(id=article.id).update(views_count=F("views_count") + 1)
    article.refresh_from_db()

    serializer = HelpArticleDetailSerializer(article)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def article_feedback(request, slug):
    """Nimmt Feedback ('helpful': true/false) entgegen."""
    try:
        article = HelpArticle.objects.get(slug=slug)
    except HelpArticle.DoesNotExist:
        return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

    helpful = request.data.get("helpful")
    if helpful is True or helpful == "true" or helpful == 1:
        HelpArticle.objects.filter(id=article.id).update(helpful_yes=F("helpful_yes") + 1)
    elif helpful is False or helpful == "false" or helpful == 0:
        HelpArticle.objects.filter(id=article.id).update(helpful_no=F("helpful_no") + 1)

    article.refresh_from_db()
    return Response({
        "status": "ok",
        "helpful_yes": article.helpful_yes,
        "helpful_no": article.helpful_no,
    })
