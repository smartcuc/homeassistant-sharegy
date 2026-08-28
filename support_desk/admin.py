#############################
# support_desk/admin.py
#############################

from django.contrib import admin
from support_desk.models import (
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    CannedResponse,
    TicketActivityLog,
)


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

