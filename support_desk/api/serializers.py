#################################
# support_desk/api/serializers.py
#################################

from rest_framework import serializers
from django.contrib.auth import get_user_model
from support_desk.models import (
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    TicketActivityLog,
    CannedResponse,
)

User = get_user_model()


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
    message_count = serializers.SerializerMethodField()
    assigned_agent_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "project_key",
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
        is_staff = request.user.is_staff if request and request.user and request.user.is_authenticated else False
        
        # Non-staff users do not see internal notes
        if is_staff:
            qs = obj.messages.all().order_by("created_at")
        else:
            qs = obj.messages.filter(is_internal_note=False).order_by("created_at")
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

