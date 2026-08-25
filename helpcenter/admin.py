######################
# helpcenter/admin.py
######################

from django.contrib import admin
from .models import HelpCategory, HelpArticle


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ("icon", "title_de", "title_en", "key", "sort_order", "article_count")
    search_fields = ("title_de", "title_en", "key")
    list_editable = ("sort_order",)
    prepopulated_fields = {"key": ("title_de",)}

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = "Artikel"


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title_de",
        "category",
        "context_key",
        "is_published",
        "is_featured",
        "views_count",
        "helpful_ratio",
        "sort_order",
    )
    list_filter = ("category", "context_key", "is_published", "is_featured")
    search_fields = ("title_de", "title_en", "content_de", "slug", "context_key", "tags")
    list_editable = ("is_published", "is_featured", "sort_order")
    prepopulated_fields = {"slug": ("title_de",)}
    fieldsets = (
        ("Allgemein", {
            "fields": ("category", "slug", "context_key", "is_published", "is_featured", "sort_order", "tags"),
        }),
        ("Deutsch (DE)", {
            "fields": ("title_de", "summary_de", "content_de"),
        }),
        ("Englisch (EN)", {
            "fields": ("title_en", "summary_en", "content_en"),
        }),
        ("Statistiken & Feedback", {
            "fields": ("views_count", "helpful_yes", "helpful_no"),
            "classes": ("collapse",),
        }),
    )

    def helpful_ratio(self, obj):
        total = obj.helpful_yes + obj.helpful_no
        if total == 0:
            return "-"
        pct = round(obj.helpful_yes / total * 100)
        return f"{pct}% 👍 ({total})"
    helpful_ratio.short_description = "Feedback"

