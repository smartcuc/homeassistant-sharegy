# 🏷️ Integrations Versioning & Release Standard (ioBroker & Home Assistant)

> **Gültig für:** `integrations/iobroker.sharegy` & `integrations/homeassistant/custom_components/sharegy`  
> **Standard:** Semantic Versioning (`MAJOR.MINOR.PATCH` gem. SemVer 2.0.0)  
> **Status:** Production Standard (SSOT Enforced)

---

## 🎯 1. Single Source of Truth (SSOT) Prinzip

Um Versionsdiskrepanzen zwischen Manifesten, WebSocket-Handshakes, RPC-Antworten und dem `moniy`-Monitoring-Hub auszuschließen, gilt:

### A. ioBroker Adapter (`iobroker.sharegy`)
- **Master-Datei:** [`package.json`](file:///c:/Users/Public/Dev/sharegy/integrations/iobroker.sharegy/package.json) $\rightarrow$ `"version": "x.y.z"`
- **Synchronisation:** [`io-package.json`](file:///c:/Users/Public/Dev/sharegy/integrations/iobroker.sharegy/io-package.json) $\rightarrow$ `"common.version": "x.y.z"`
- **Laufzeit-Auflösung in Code:**
  ```javascript
  const pkg = require("./package.json");
  const ADAPTER_VERSION = (pkg && pkg.version) || "unknown";
  ```
  *(Keine hardcodierten Versionsstrings in `main.js`, `lib/`, `sys.ping` oder WSS-URLs!)*
- **Automatischer Validierungs-Check:**
  ```bash
  cd integrations/iobroker.sharegy
  npm run check-version
  ```

### B. Home Assistant Integration (`homeassistant.sharegy`)
- **Master-Datei:** [`manifest.json`](file:///c:/Users/Public/Dev/sharegy/integrations/homeassistant/custom_components/sharegy/manifest.json) $\rightarrow$ `"version": "x.y.z"`
- **Laufzeit-Auflösung in Code (`const.py`):**
  ```python
  import json
  import os

  _MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
  try:
      with open(_MANIFEST_PATH, "r", encoding="utf-8") as _f:
          _manifest_data = json.load(_f)
          VERSION = _manifest_data.get("version", "2.2.0")
  except Exception:
      VERSION = "2.2.0"
  ```
  *(Alle Sensoren, Bridge-Klassen, Heartbeats und Watchdogs greifen automatisch auf `VERSION` zu.)*

---

## 🚀 2. Release-Checkliste bei neuen Versionen

Wenn eine neue Version (z. B. `2.2.1` oder `2.3.0`) veröffentlicht wird:

1. **ioBroker:**
   - In `package.json` die Version anheben.
   - In `io-package.json` `common.version` und den Changelog-Eintrag unter `common.news` ergänzen.
   - `npm run check-version` ausführen.
2. **Home Assistant:**
   - In `manifest.json` die Version anheben.
3. **Git Release:**
   - Release-Commit erstellen & Tag setzen (z. B. `git tag -a v2.2.0 -m "Release v2.2.0"`).
