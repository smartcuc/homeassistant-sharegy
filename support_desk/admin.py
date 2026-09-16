#############################
# support_desk/admin.py
#############################

from django.contrib import admin
from support_desk.models import (
    HelpCategory,
    HelpArticle,
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    CannedResponse,
    TicketActivityLog,
)


# =========================================================================
# 1. WISSENSPORTAL & FAQ ADMIN (KNOWLEDGE BASE)
# =========================================================================

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


# =========================================================================
# 2. SUPPORT DESK & TICKET ADMIN
# =========================================================================

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    fields = ["created_at", "sender", "external_sender_name", "is_staff_reply", "is_internal_note", "body"]
    readonly_fields = ["created_at"]


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    fields = ["filename", "file", "file_size", "mime_type", "created_at"]
    readonly_fields = ["created_at"]


class TicketActivityLogInline(admin.TabularInline):
    model = TicketActivityLog
    extra = 0
    fields = ["created_at", "actor_name", "action", "details"]
    readonly_fields = ["created_at", "actor_name", "action", "details"]


@admin.register(SupportProjectConfig)
class SupportProjectConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "project_key", "ticket_prefix", "is_active", "created_at"]
    search_fields = ["name", "project_key"]
    list_filter = ["is_active"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "ticket_number",
        "project_key",
        "subject",
        "category",
        "priority",
        "status",
        "contact_name",
        "contact_email",
        "assigned_agent",
        "created_at",
    ]
    list_filter = ["project_key", "status", "priority", "category", "created_at"]
    search_fields = ["ticket_number", "subject", "contact_name", "contact_email", "external_user_id"]
    readonly_fields = ["id", "ticket_number", "created_at", "updated_at"]
    inlines = [TicketMessageInline, TicketAttachmentInline, TicketActivityLogInline]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ["ticket", "sender", "external_sender_name", "is_staff_reply", "is_internal_note", "created_at"]
    list_filter = ["is_staff_reply", "is_internal_note", "created_at"]
    search_fields = ["ticket__ticket_number", "body", "external_sender_name", "external_sender_email"]


@admin.register(CannedResponse)
class CannedResponseAdmin(admin.ModelAdmin):
    list_display = ["shortcut", "title", "project_key", "category", "created_at"]
    list_filter = ["project_key", "category"]
    search_fields = ["shortcut", "title", "body_de", "body_en"]


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ["filename", "ticket", "file_size", "mime_type", "created_at"]
    list_filter = ["mime_type", "created_at"]
    search_fields = ["filename", "ticket__ticket_number"]
    raw_id_fields = ["ticket", "message", "uploaded_by"]
    readonly_fields = ["created_at"]


@admin.register(TicketActivityLog)
class TicketActivityLogAdmin(admin.ModelAdmin):
    list_display = ["ticket", "action", "actor_name", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["ticket__ticket_number", "actor_name", "details"]
    raw_id_fields = ["ticket", "user"]
    readonly_fields = ["created_at"]

