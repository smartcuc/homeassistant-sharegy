#############################
# support_desk/tests.py
#############################

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from support_desk.models import (
    HelpCategory,
    HelpArticle,
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    CannedResponse,
)
from support_desk.services.auth_jwt import generate_support_jwt, verify_support_jwt
from support_desk.services.ticket_engine import (
    generate_ticket_number,
    create_ticket,
    add_message,
    update_ticket_status,
    assign_ticket,
)

User = get_user_model()


class SupportDeskEngineTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.customer = User.objects.create_user(
            username="kunde1",
            email="kunde@sharegy.de",
            password="testpassword123",
            first_name="Max",
            last_name="Mustermann",
        )
        self.staff_agent = User.objects.create_user(
            username="support_agent",
            email="agent@sharegy.de",
            password="testpassword123",
            is_staff=True,
            first_name="Anna",
            last_name="Support",
        )

        # Projects Config
        self.proj_sharegy = SupportProjectConfig.objects.create(
            project_key="sharegy",
            name="Sharegy HEMS",
            ticket_prefix="SHAR",
            secret_key="sharegy-super-secret-key",
            allowed_categories=["hardware", "tariff", "forecast", "billing", "general"],
        )
        self.proj_factofy = SupportProjectConfig.objects.create(
            project_key="factofy",
            name="Factofy Digital Twin",
            ticket_prefix="FACT",
            secret_key="factofy-shared-secret-key-2026",
            allowed_categories=["3d_mesh", "sensors", "lorawan", "gis_map", "general"],
        )

        # HelpCenter Article for Deflection Test
        self.category = HelpCategory.objects.create(
            key="devices",
            title_de="Geräte & Zähler",
            title_en="Devices & Meters",
        )
        self.article = HelpArticle.objects.create(
            category=self.category,
            slug="wechselrichter-offline-beheben",
            title_de="Wechselrichter offline - Erste Hilfe & Reboot",
            title_en="Inverter offline troubleshooting",
            summary_de="Schritt für Schritt Anleitung bei Verbindungsabbruch des Wechselrichters",
            content_de="1. Prüfe die WLAN-Verbindung...",
            tags=["wechselrichter", "offline", "inverter", "wifi"],
            is_published=True,
        )

    def test_ticket_number_generation_multi_project(self):
        num_shar = generate_ticket_number("sharegy")
        self.assertTrue(num_shar.startswith("SHAR-"))

        num_fact = generate_ticket_number("factofy")
        self.assertTrue(num_fact.startswith("FACT-"))

        # Sequential uniqueness
        t1 = create_ticket(project_key="sharegy", subject="Test 1", user=self.customer)
        t2 = create_ticket(project_key="sharegy", subject="Test 2", user=self.customer)
        self.assertNotEqual(t1.ticket_number, t2.ticket_number)

    def test_jwt_auth_for_external_factofy_client(self):
        # 1. Generate JWT as Factofy backend would
        token = generate_support_jwt(
            project_key="factofy",
            user_id="fact_user_8821",
            email="operator@stadtwerke-nord.de",
            name="Klaus Operator",
            extra_claims={"tenant": "stadtwerke_nord"},
        )
        self.assertIsInstance(token, str)

        # 2. Verify token
        is_valid, payload, err = verify_support_jwt(token)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertEqual(payload["project"], "factofy")
        self.assertEqual(payload["sub"], "fact_user_8821")
        self.assertEqual(payload["email"], "operator@stadtwerke-nord.de")

        # 3. Create Ticket via API using external JWT
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.post(
            "/api/support/tickets/",
            data={
                "subject": "LoRaWAN Sensor Node 4B sendet keine Pegeldaten",
                "category": "sensors",
                "priority": "high",
                "initial_message": "Seit 02:00 Uhr keine Telemetrie vom Hochwasser-Sensor.",
                "context_payload": {
                    "building_id": "BLD-99",
                    "sensor_eui": "0004A30B001F1234",
                    "coordinates": [50.9375, 6.9603],
                    "layer": "water_level",
                },
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertTrue(data["ticket_number"].startswith("FACT-"))
        self.assertEqual(data["project_key"], "factofy")
        self.assertEqual(data["contact_email"], "operator@stadtwerke-nord.de")
        self.assertEqual(data["context_payload"]["sensor_eui"], "0004A30B001F1234")

        # 4. List user's tickets as Factofy user
        list_resp = self.client.get("/api/support/tickets/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.json()), 1)
        self.assertEqual(list_resp.json()[0]["ticket_number"], data["ticket_number"])

    def test_sharegy_ticket_lifecycle_and_internal_notes(self):
        # 1. Customer creates ticket with attachment
        self.client.force_login(self.customer)
        test_file = SimpleUploadedFile("inverter_log.txt", b"ERROR 403: MQTT connection timeout", content_type="text/plain")

        resp = self.client.post(
            "/api/support/tickets/",
            data={
                "subject": "Deye Wechselrichter zeigt keine Solarleistung",
                "category": "hardware",
                "priority": "urgent",
                "initial_message": "Inverter ist rot und speist nicht ein.",
                "context_payload": json.dumps({"device_id": 1239, "model": "Deye-SUN-12K"}),
                "attachments": [test_file],
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 201)
        ticket_id = resp.json()["id"]

        # 2. Staff views and writes an internal note (yellow note)
        self.client.force_login(self.staff_agent)
        note_resp = self.client.post(
            f"/api/support/agent/tickets/{ticket_id}/",
            data={"body": "Intern: Prüfen ob Firmware-Update v2.1 bereitsteht."},
            format="json",
        )
        self.assertEqual(note_resp.status_code, 201)

        # 3. Staff replies to customer
        reply_resp = self.client.post(
            f"/api/support/tickets/{ticket_id}/messages/",
            data={"body": "Hallo Herr Mustermann, bitte schalten Sie den DC-Schalter einmal für 30s aus."},
            format="json",
        )
        self.assertEqual(reply_resp.status_code, 201)

        # 4. Verify Customer CANNOT see internal notes
        self.client.force_login(self.customer)
        detail_resp = self.client.get(f"/api/support/tickets/{ticket_id}/")
        self.assertEqual(detail_resp.status_code, 200)
        messages = detail_resp.json()["messages"]
        # Should have initial message + staff reply, but NOT the internal note!
        self.assertEqual(len(messages), 2)
        for msg in messages:
            self.assertFalse(msg["is_internal_note"])

        # 5. Staff CAN see internal notes
        self.client.force_login(self.staff_agent)
        staff_detail_resp = self.client.get(f"/api/support/tickets/{ticket_id}/")
        self.assertEqual(len(staff_detail_resp.json()["messages"]), 3)

    def test_deflection_suggestions_endpoint(self):
        resp = self.client.get("/api/support/deflection/suggest/?q=Wechselrichter")
        self.assertEqual(resp.status_code, 200)
        suggestions = resp.json()["suggestions"]
        self.assertTrue(len(suggestions) >= 1)
        self.assertEqual(suggestions[0]["slug"], "wechselrichter-offline-beheben")

    def test_agent_hub_management_and_kpis(self):
        # Create 1 Sharegy ticket and 1 Factofy ticket
        create_ticket(project_key="sharegy", subject="Sharegy Issue", user=self.customer)
        create_ticket(project_key="factofy", subject="Factofy Issue", contact_email="fact@city.de")

        self.client.force_login(self.staff_agent)
        resp = self.client.get("/api/support/agent/tickets/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertIn("kpis", data)
        self.assertIn("tickets", data)
        self.assertEqual(data["kpis"]["sharegy_count"], 1)
        self.assertEqual(data["kpis"]["factofy_count"], 1)
        self.assertEqual(len(data["tickets"]), 2)

        # Filter by project_key=factofy
        fact_resp = self.client.get("/api/support/agent/tickets/?project_key=factofy")
        self.assertEqual(len(fact_resp.json()["tickets"]), 1)
        self.assertEqual(fact_resp.json()["tickets"][0]["project_key"], "factofy")

    def test_anonymous_user_cannot_create_ticket(self):
        # Anonymous users without session or JWT token are rejected
        resp = self.client.post(
            "/api/support/tickets/",
            data={
                "subject": "Gast Ticket",
                "message": "Ich bin nicht angemeldet",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("error", resp.json())

    def test_free_ems_user_priority_forced_to_low(self):
        # Free-EMS user attempts to create ticket with priority='high' -> backend forces 'low'
        self.client.force_login(self.customer)
        resp = self.client.post(
            "/api/support/tickets/",
            data={
                "subject": "Free User Issue",
                "priority": "high",
                "message": "Dringende Frage von Free User",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["priority"], "low")

    def test_pro_and_admin_user_can_set_priority(self):
        # 1. Staff Agent creates ticket with 'urgent'
        self.client.force_login(self.staff_agent)
        resp = self.client.post(
            "/api/support/tickets/",
            data={
                "subject": "Admin Critical Incident",
                "priority": "urgent",
                "message": "Netzausfall am Gateway",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["priority"], "urgent")

        # 2. Pro User creates ticket with 'high'
        from billing.models import EMSSubscription
        EMSSubscription.objects.update_or_create(
            user=self.customer,
            defaults={
                "plan": EMSSubscription.PLAN_PRO_MONTHLY,
                "status": EMSSubscription.STATUS_ACTIVE,
            }
        )
        self.client.force_login(self.customer)
        pro_resp = self.client.post(
            "/api/support/tickets/",
            data={
                "subject": "EMS Pro High Priority Request",
                "priority": "high",
                "message": "Optimierungs-Algorithmus prüfen",
            },
            format="json",
        )
        self.assertEqual(pro_resp.status_code, 201)
        self.assertEqual(pro_resp.json()["priority"], "high")




class KnowledgeBaseApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="helpuser",
            email="help@example.com",
            password="testpassword123",
        )
        self.staff_user = User.objects.create_user(
            username="helpstaff",
            email="staff@example.com",
            password="testpassword123",
            is_staff=True,
        )

        self.category = HelpCategory.objects.create(
            key="test-cat",
            icon="📖",
            title_de="Test Kategorie",
            title_en="Test Category",
        )

        self.article = HelpArticle.objects.create(
            category=self.category,
            slug="test-article",
            context_key="forecast",
            title_de="Test Artikel Titel",
            title_en="Test Article Title",
            summary_de="Kurzbeschreibung",
            content_de="# Markdown Inhalt",
            content_en="# Markdown Content",
            tags=["solar", "test"],
            is_published=True,
            is_featured=True,
        )

    def test_categories_list_api(self):
        response = self.client.get("/api/help/categories/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["key"], "test-cat")
        self.assertEqual(data[0]["article_count"], 1)

    def test_articles_list_and_search_api(self):
        # 1. Normal list
        response = self.client.get("/api/help/articles/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)

        # 2. Search match
        search_resp = self.client.get("/api/help/articles/?search=Titel")
        self.assertEqual(search_resp.status_code, 200)
        self.assertEqual(len(search_resp.json()), 1)

        # 3. Search no match
        no_resp = self.client.get("/api/help/articles/?search=nonexistenttermxyz")
        self.assertEqual(no_resp.status_code, 200)
        self.assertEqual(len(no_resp.json()), 0)

    def test_context_articles_api(self):
        response = self.client.get("/api/help/context/?key=forecast")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["context_key"], "forecast")
        self.assertGreaterEqual(len(data["articles"]), 1)
        self.assertEqual(data["articles"][0]["slug"], "test-article")

    def test_article_detail_and_views_increment(self):
        initial_views = self.article.views_count
        response = self.client.get(f"/api/help/articles/{self.article.slug}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title_de"], "Test Artikel Titel")
        self.assertEqual(data["views_count"], initial_views + 1)

    def test_article_feedback_api(self):
        response = self.client.post(
            f"/api/help/articles/{self.article.slug}/feedback/",
            data={"helpful": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.helpful_yes, 1)

    def test_staff_article_patch_api(self):
        # 1. Anonymous / Normal user cannot patch
        self.client.force_login(self.user)
        patch_fail = self.client.patch(
            f"/api/help/articles/{self.article.slug}/",
            data={"title_de": "Neuer Titel Von User"},
            format="json",
        )
        self.assertEqual(patch_fail.status_code, 403)

        # 2. Staff user can patch
        self.client.force_login(self.staff_user)
        patch_ok = self.client.patch(
            f"/api/help/articles/{self.article.slug}/",
            data={"title_de": "Aktualisierter Titel Durch Staff"},
            format="json",
        )
        self.assertEqual(patch_ok.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title_de, "Aktualisierter Titel Durch Staff")
