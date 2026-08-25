######################
# helpcenter/tests.py
######################

from django.test import TestCase
from django.contrib.auth import get_user_model
from helpcenter.models import HelpCategory, HelpArticle

User = get_user_model()


class HelpCenterApiTests(TestCase):
    def setUp(self):
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
            content_type="application/json",
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
            content_type="application/json",
        )
        self.assertEqual(patch_fail.status_code, 403)

        # 2. Staff user can patch
        self.client.force_login(self.staff_user)
        patch_ok = self.client.patch(
            f"/api/help/articles/{self.article.slug}/",
            data={"title_de": "Aktualisierter Titel Durch Staff"},
            content_type="application/json",
        )
        self.assertEqual(patch_ok.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title_de, "Aktualisierter Titel Durch Staff")

