##########################
# helpcenter/api/urls.py
##########################

from django.urls import path
from .views import (
    categories_list,
    articles_list,
    context_articles,
    article_detail,
    article_feedback,
)

urlpatterns = [
    path("categories/", categories_list, name="helpcenter-categories"),
    path("articles/", articles_list, name="helpcenter-articles"),
    path("context/", context_articles, name="helpcenter-context"),
    path("articles/<slug:slug>/", article_detail, name="helpcenter-article-detail"),
    path("articles/<slug:slug>/feedback/", article_feedback, name="helpcenter-article-feedback"),
]

