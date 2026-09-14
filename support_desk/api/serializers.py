#################################
# support_desk/api/serializers.py
#################################

from rest_framework import serializers
from django.contrib.auth import get_user_model
from support_desk.models import (
    HelpCategory,
    HelpArticle,
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    TicketActivityLog,
    CannedResponse,
)

User = get_user_model()


# =========================================================================
# 1. WISSENSPORTAL / KNOWLEDGE BASE SERIALIZERS
# =========================================================================

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


# =========================================================================
# 2. SUPPORT DESK & TICKET SERIALIZERS
# =========================================================================

class TicketAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = ["id", "filename", "file_size", "mime_type", "file_url", "created_at"]

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.SerializerMethodField()
    attachments = TicketAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "ticket_id",
            "sender_id",
            "sender_name",
            "sender_email",
            "is_staff_reply",
            "is_internal_note",
            "body",
            "attachments",
            "created_at",
        ]

    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.username
        return obj.external_sender_name or "Kunde"

    def get_sender_email(self, obj):
        if obj.sender:
            return obj.sender.email
        return obj.external_sender_email or ""


class TicketActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketActivityLog
        fields = ["id", "actor_name", "action", "details", "created_at"]


class TicketListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True, default=None)
    message_count = serializers.SerializerMethodField()
    assigned_agent_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "project_key",
            "tenant_id",
            "tenant_name",
            "subject",
            "category",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "contact_name",
            "contact_email",
            "assigned_agent_name",
            "message_count",
            "created_at",
            "updated_at",
        ]

    def get_message_count(self, obj):
        return obj.messages.filter(is_internal_note=False).count()

    def get_assigned_agent_name(self, obj):
        if obj.assigned_agent:
            return f"{obj.assigned_agent.first_name} {obj.assigned_agent.last_name}".strip() or obj.assigned_agent.username
        return None


class TicketDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True, default=None)
    messages = serializers.SerializerMethodField()
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    activity_logs = TicketActivityLogSerializer(many=True, read_only=True)
    assigned_agent_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "project_key",
            "tenant_id",
            "tenant_name",
            "subject",
            "category",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "contact_name",
            "contact_email",
            "assigned_agent_name",
            "context_payload",
            "messages",
            "attachments",
            "activity_logs",
            "first_response_due",
            "first_responded_at",
            "resolved_at",
            "closed_at",
            "created_at",
            "updated_at",
        ]

    def get_messages(self, obj):
        request = self.context.get("request")
        user = request.user if request and request.user and request.user.is_authenticated else None
        
        is_global_staff = bool(
            user and (
                user.is_staff or 
                user.is_superuser or 
                getattr(user, "is_platform_admin", False) or 
                getattr(user, "is_platform_helpdesk", False)
            )
        )
        is_tenant_agent = False
        if user and obj.tenant_id and hasattr(user, "memberships"):
            is_tenant_agent = user.memberships.filter(
                tenant_id=obj.tenant_id,
                is_active=True,
                role__in=["admin", "helpdesk", "installer", "user_admin"]
            ).exists()
        
        can_view_internal = is_global_staff or is_tenant_agent

        # Non-agent users do not see internal notes
        if can_view_internal:
            qs = obj.messages.all()
        else:
            qs = obj.messages.filter(is_internal_note=False)

        return TicketMessageSerializer(qs, many=True).data

    def get_assigned_agent_name(self, obj):
        if obj.assigned_agent:
            return f"{obj.assigned_agent.first_name} {obj.assigned_agent.last_name}".strip() or obj.assigned_agent.username
        return None


class CannedResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CannedResponse
        fields = ["id", "project_key", "shortcut", "title", "category", "body_de", "body_en", "created_at"]


class SupportProjectConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportProjectConfig
        fields = ["id", "project_key", "name", "ticket_prefix", "allowed_categories", "is_active", "created_at"]
