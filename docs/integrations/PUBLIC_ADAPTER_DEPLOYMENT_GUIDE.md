# 🚀 Public Deployment Guide: ioBroker & Home Assistant Integrationen

Diese Anleitung beschreibt, wie du die Integrations-Adapter (**ioBroker** und **Home Assistant**) aus dem geschützten (privaten) Sharegy-Haupt-Repository (`smartcuc/eswes`) in eigenständige, **öffentliche GitHub-Repositories** veröffentlichst und synchronisierst.

---

## 🏗️ Warum dieser Ansatz (Git Subtree)?

1. **Sicherheit**: Der Core-Code von Sharegy (Backend, Frontend, ML, Datenbankmodelle) bleibt zu 100 % in deinem geschützten/privaten Repository.
2. **Community & Ökosystem**: ioBroker- und Home Assistant-Nutzer können die Adapter über öffentliche GitHub-URLs, HACS oder npm installieren.
3. **Single Source of Truth**: Du entwickelst und pflegst alle Adapter direkt im Hauptprojekt. Die Veröffentlichung geschieht mit einem einzigen Git-Befehl.

---

## 📦 1. ioBroker Adapter (`ioBroker.sharegy`)

### Schritt 1: Leeres Public-Repo auf GitHub erstellen
1. Auf GitHub ein neues Repository anlegen:
   - **Repository Name**: `ioBroker.sharegy` *(wichtig: exakt so mit großem B)*
   - **Sichtbarkeit**: `Public`
   - ⚠️ **Wichtig**: *Add a README*, *.gitignore* oder *license* **nicht** anhaken (Repo muss komplett leer sein).

### Schritt 2: Initialer Push via Git Subtree
Führe im Terminal deines lokalen Projekts (`c:\Users\Public\Dev\eswes`) folgenden Befehl aus:

```bash
git subtree push --prefix integrations/iobroker.sharegy https://github.com/smartcuc/ioBroker.sharegy.git main
```

### Schritt 3: Spätere Updates synchronisieren
Jedes Mal, wenn du Änderungen im Ordner `integrations/iobroker.sharegy/` committest, synchronisierst du das öffentliche Repo wieder mit demselben Befehl:

```bash
git subtree push --prefix integrations/iobroker.sharegy https://github.com/smartcuc/ioBroker.sharegy.git main
```

### 📥 Installation durch ioBroker-Nutzer:
- **Über die ioBroker-Admin UI**: *Adapter -> GitHub-Icon (Installieren aus eigener URL) -> Benutzerdefiniert*:
  ```
  https://github.com/smartcuc/ioBroker.sharegy
  ```
- **Oder per CLI auf dem ioBroker-Server**:
  ```bash
  cd /opt/iobroker
  npm install https://github.com/smartcuc/ioBroker.sharegy.git
  iobroker add sharegy
  iobroker upload sharegy
  ```

---

## 🏡 2. Home Assistant Integration (`homeassistant-sharegy` / HACS)

### Schritt 1: Leeres Public-Repo auf GitHub erstellen
1. Auf GitHub ein neues Repository anlegen:
   - **Repository Name**: `homeassistant-sharegy`
   - **Sichtbarkeit**: `Public`
   - ⚠️ **Wichtig**: *Add a README*, *.gitignore* oder *license* **nicht** anhaken.

### Schritt 2: Initialer Push via Git Subtree
Führe im Projekt-Terminal folgenden Befehl aus:

```bash
git subtree push --prefix integrations/homeassistant https://github.com/smartcuc/homeassistant-sharegy.git main
```

### Schritt 3: Spätere Updates synchronisieren
```bash
git subtree push --prefix integrations/homeassistant https://github.com/smartcuc/homeassistant-sharegy.git main
```

### 📥 Installation durch Home Assistant-Nutzer (HACS):
1. In Home Assistant zu **HACS** $\rightarrow$ **Integrationen** navigieren.
2. Oben rechts auf das Drei-Punkte-Menü $\rightarrow$ **Benutzerdefinierte Repositories** klicken.
3. Repository: `https://github.com/smartcuc/homeassistant-sharegy` | Typ: `Integration`.
4. Auf **Herunterladen** klicken und Home Assistant neu starten.

---

## 🛠️ Nützliche Git-Aliase (Optional zur Vereinfachung)

Du kannst dir in deiner lokalen Git-Konfiguration kurze Aliase anlegen:

```bash
git config alias.push-iob "subtree push --prefix integrations/iobroker.sharegy https://github.com/smartcuc/ioBroker.sharegy.git main"
git config alias.push-ha "subtree push --prefix integrations/homeassistant https://github.com/smartcuc/homeassistant-sharegy.git main"
```

Danach reicht zukünftig einfach:
```bash
git push-iob
git push-ha
```
