#######################
# helpcenter/models.py
#######################

import uuid
from django.db import models


class HelpCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.SlugField(max_length=80, unique=True, help_text="Technischer Key (z. B. inverters, optimizer)")
    icon = models.CharField(max_length=20, default="📖", help_text="Emoji oder Icon-Name")
    title_de = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_de = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hilfe-Kategorie"
        verbose_name_plural = "Hilfe-Kategorien"
        ordering = ["sort_order", "title_de"]

    def __str__(self):
        return f"{self.icon} {self.title_de} ({self.key})"


class HelpArticle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        HelpCategory,
        related_name="articles",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-Slug (z. B. solar-prognose-verstaendnis)")
    context_key = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Kontext-Schlüssel für Drawer-Matching (z. B. 'forecast', 'energy', 'tariffs', 'alerts', 'devices', 'optimizer')",
    )

    title_de = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    summary_de = models.TextField(blank=True, help_text="Kurzbeschreibung für Suchergebnisse und Drawer")
    summary_en = models.TextField(blank=True)

    content_de = models.TextField(help_text="Ausführlicher Artikelinhalt in Markdown (Deutsch)")
    content_en = models.TextField(blank=True, help_text="Ausführlicher Artikelinhalt in Markdown (Englisch)")

    tags = models.JSONField(default=list, blank=True, help_text="Liste von Schlagworten für Volltextsuche")
    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, help_text="Hervorheben auf der Wissensportal-Startseite")
    sort_order = models.IntegerField(default=0)

    views_count = models.PositiveIntegerField(default=0)
    helpful_yes = models.PositiveIntegerField(default=0)
    helpful_no = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hilfe-Artikel"
        verbose_name_plural = "Hilfe-Artikel"
        ordering = ["sort_order", "-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.title_de} [{self.slug}]"

