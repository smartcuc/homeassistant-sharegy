# 📚 Architektur & Walkthrough: Task 5.4 & 5.5 – Kontextuelles Help-System & Wissensportal

**Datum**: 25. August 2026  
**Bereich**: In-App Support, Kontext-Hilfe, FAQ-Portal, Knowledge Base, Headless Content Management  
**Status**: 🚀 In Umsetzung

---

## 🎯 1. Zielsetzung & Kernfragen

1. **Wo stehen die Texte & Anleitungen?**
   * Vollständig strukturiert in der Datenbank (`helpcenter`-App) in einem **Headless-Modell** mit Markdown-Unterstützung (Texte, Code-Snippets, Tabellen, Warn-Boxen und Bilder).
   * Getrennte Felder für **Deutsch (`_de`)** und **Englisch (`_en`)**.
2. **Wie erfolgt die laufende Pflege?**
   * **Django Admin**: Voller Zugriff für Entwickler & Redaktion.
   * **In-App Quick-Editor**: Für angemeldete Mitarbeiter (`is_staff`) direkt im Drawer/Portal per Klick auf „✏️ Bearbeiten“ ohne Deployment.

---

## 🏛️ 2. Architektur & Systemüberblick

```mermaid
graph TD
    subgraph Backend: Django DB & REST API
        C["HelpCategory (Kategorie, Icon, SortOrder)"]
        A["HelpArticle (Titel DE/EN, Content DE/EN, Tags, Context-Key)"]
        API1["GET /api/help/context/?key=forecast"]
        API2["GET /api/help/categories/"]
        API3["GET /api/help/articles/?search=...&category=..."]
        API4["PATCH /api/help/articles/<slug>/ (Staff Only)"]
    end

    subgraph Content Management
        Adm1["1. Django Admin Backend (/admin/helpcenter/)"]
        Adm2["2. In-App Live Editor Modal (Frontend Quick-Edit)"]
    end

    subgraph Frontend User Experience
        Drawer["Task 5.4: HelpDrawer.jsx<br/>(Slide-Over rechts auf jeder Seite)"]
        Center["Task 5.5: HelpCenterPage.jsx<br/>(Vollwertiges Wissensportal & FAQ)"]
        Article["HelpArticleDetailPage.jsx<br/>(Schritt-für-Schritt Markdown Reader)"]
    end

    C --> API2
    A --> API1
    A --> API3
    A --> API4
    Adm1 --> A
    Adm2 --> API4
    API1 --> Drawer
    API2 --> Center
    API3 --> Center
    API3 --> Article
```

---

## 📋 3. Spezifikation der Komponenten

### A. Task 5.4: In-App Help Drawer (Slide-Over)
* Button **`? Hilfe & Tipps`** in der Sidebar und im Top-Header jeder Seite.
* Beim Klick gleitet von rechts ein eleganter Drawer ein (ohne Seitenwechsel):
  * **Kontexterkennung**: Erkennt die aktuelle URL/Route (z. B. `context_key = "forecast"` oder `"energy_dashboard"` oder `"devices"`).
  * **Top 3 Quick-Guides**: Zeigt sofort die relevantesten Erklärungen für die aktuelle Ansicht.
  * **Schnellsuche**: Live-Suche im gesamten Wissensportal.
  * **Direktlink**: Button *„Zum vollständigen Handbuch ↗“*.

### B. Task 5.5: Wissensportal & FAQ-Center (`/app/help`)
* **Kategorie-Übersicht**:
  * ☀️ **Erzeuger & Photovoltaik**: Wechselrichter-Anbindung (SMA, Sungrow, Fronius, Deye, Huawei).
  * ⚡ **Strompreise & Tarife**: Dynamische Tarife, Tibber, Börsenstrom-Formeln.
  * 🤖 **Smart Energy Optimizer**: Fahrpläne, Ladefenster, Wärmepumpen-Steuerung.
  * 🚨 **Alarmzentrale**: Notifikationen, Ertragsausfall-Erkennung, Schwellwerte.
  * 🧾 **Abrechnung & Mieterstrom**: Sub-Metering, Zählerallokation, PDF-Export.
* **Volltextsuche**: Schnelle Client- & Backend-Suche mit Treffer-Highlighting.
* **Artikel-Ansicht**: Responsiver Markdown-Reader mit Alert-Boxen (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`), Copy-to-Clipboard für Codeblöcke und "War dieser Artikel hilfreich?"-Feedback.

