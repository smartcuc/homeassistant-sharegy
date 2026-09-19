############################
# support_desk/api/urls.py
############################

from django.urls import path
from support_desk.api.views import (
    tickets_list_create,
    ticket_detail,
    ticket_add_message,
    deflection_suggest,
    agent_ticket_management,
    agent_ticket_escalate_to_smartevo,
    canned_responses_list,
)

urlpatterns = [
    # Customer / User endpoints (Sharegy session or Factofy JWT)
    path("tickets/", tickets_list_create, name="support-tickets-list-create"),
    path("tickets/<uuid:ticket_id>/", ticket_detail, name="support-ticket-detail"),
    path("tickets/<uuid:ticket_id>/messages/", ticket_add_message, name="support-ticket-messages"),
    
    # Knowledge-base deflection before submission
    path("deflection/suggest/", deflection_suggest, name="support-deflection-suggest"),
    
    # Staff / Agent management
    path("agent/tickets/", agent_ticket_management, name="support-agent-tickets"),
    path("agent/tickets/<uuid:ticket_id>/", agent_ticket_management, name="support-agent-ticket-detail"),
    path("agent/tickets/<uuid:ticket_id>/escalate/", agent_ticket_escalate_to_smartevo, name="support-agent-ticket-escalate"),
    path("canned-responses/", canned_responses_list, name="support-canned-responses"),
]

