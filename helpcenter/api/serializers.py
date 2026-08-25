#################################
# helpcenter/api/serializers.py
#################################

from rest_framework import serializers
from helpcenter.models import HelpCategory, HelpArticle


class HelpCategorySerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = HelpCategory
        fields = [
            "id",
            "key",
            "icon",
            "title_de",
            "title_en",
            "description_de",
            "description_en",
            "sort_order",
            "article_count",
        ]

    def get_article_count(self, obj):
        return obj.articles.filter(is_published=True).count()


class HelpArticleListSerializer(serializers.ModelSerializer):
    category_key = serializers.CharField(source="category.key", read_only=True)
    category_title_de = serializers.CharField(source="category.title_de", read_only=True)
    category_title_en = serializers.CharField(source="category.title_en", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)

    class Meta:
        model = HelpArticle
        fields = [
            "id",
            "slug",
            "category_key",
            "category_title_de",
            "category_title_en",
            "category_icon",
            "context_key",
            "title_de",
            "title_en",
            "summary_de",
            "summary_en",
            "tags",
            "is_featured",
            "views_count",
            "created_at",
            "updated_at",
        ]


class HelpArticleDetailSerializer(serializers.ModelSerializer):
    category_key = serializers.CharField(source="category.key", read_only=True)
    category_title_de = serializers.CharField(source="category.title_de", read_only=True)
    category_title_en = serializers.CharField(source="category.title_en", read_only=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True)

    class Meta:
        model = HelpArticle
        fields = [
            "id",
            "slug",
            "category_key",
            "category_title_de",
            "category_title_en",
            "category_icon",
            "context_key",
            "title_de",
            "title_en",
            "summary_de",
            "summary_en",
            "content_de",
            "content_en",
            "tags",
            "is_published",
            "is_featured",
            "views_count",
            "helpful_yes",
            "helpful_no",
            "created_at",
            "updated_at",
        ]


class HelpArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpArticle
        fields = [
            "title_de",
            "title_en",
            "summary_de",
            "summary_en",
            "content_de",
            "content_en",
            "context_key",
            "tags",
            "is_published",
            "is_featured",
        ]

