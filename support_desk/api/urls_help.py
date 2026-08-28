##############################
# support_desk/api/urls_help.py
##############################

from django.urls import path
from support_desk.api.views_help import (
    categories_list,
    articles_list,
    context_articles,
    article_detail,
    article_feedback,
)

urlpatterns = [
    path("categories/", categories_list, name="support-help-categories"),
    path("articles/", articles_list, name="support-help-articles"),
    path("context/", context_articles, name="support-help-context"),
    path("articles/<slug:slug>/", article_detail, name="support-help-article-detail"),
    path("articles/<slug:slug>/feedback/", article_feedback, name="support-help-article-feedback"),
]
