# 🍞 [WIP] Globales Toast-Notification-System

**Dokument-Status:** In Konzeption / Spezifikation  
**Fortschritt:** 🟡 25 %  
**Priorität:** 🔴 Hoch (App-weites Micro-Feedback & UX)  
**Lead / Modul:** `frontend/src/components/ui/`, `frontend/src/context/`  

---

## 🎯 1. Problemstellung & Motivation

Bisher erfolgen Erfolgs- und Statusmeldungen (z. B. „Einstellungen gespeichert“, „Dimm-Signal gesendet“, „Zählerstand erfasst“) häufig über blockierende Alerts, Inline-Hinweise oder stille Updates.
Ein **globales Toast-System**:
* Informiert den Benutzer dezent und nicht-blockierend in der rechten unteren Bildschirmecke.
* Bietet eine **Undo-Funktion** (z. B. versehentliches Löschen rückgängig machen).
* Passt sich nahtlos an das Glassmorphic Dark/Light Theme der Plattform an.

---

## 🖥️ 2. Toast-Varianten & Design

```
+─────────────────────────────────────────────────────────────+
| 🟢  Erfolgreich gespeichert                                 |
|     Liegenschaft "Quartier Sonnenblick" wurde aktualisiert. |
+─────────────────────────────────────────────────────────────+

+─────────────────────────────────────────────────────────────+
| ⚡  § 14a EnWG Dimm-Befehl gesendet                         |
|     Sollwert 4,2 kW an 12 SteuVE übermittelt.               |
+─────────────────────────────────────────────────────────────+

+─────────────────────────────────────────────────────────────+
| 🗑️  Zählerzuordnung entfernt                 [ ↩ Rückgängig ] |
|     Zähler #DE00014521485 wurde gelöst.       (Noch 4s)     |
+─────────────────────────────────────────────────────────────+
```

---

## 📊 3. Spezifikation der Toast-Typen

| Typ | Icon / Farbkodierung | Auto-Dismiss | Typischer Anwendungsfall |
|---|:---:|:---:|---|
| **Success** | 🟢 Emerald | 4 Sekunden | Formular gespeichert, Export fertiggestellt, Gerät gekoppelt |
| **Info** | 🔵 Cyan / Blue | 5 Sekunden | Hintergrund-Berechnung gestartet, Synchronisation läuft |
| **Warning** | 🟠 Amber | 6 Sekunden | Batterie-Reserve erreicht, Offline-Pufferung aktiv |
| **Error** | 🔴 Rose | Bleibt bis Klick | API-Fehler, Validierungsfehler, Verbindungsabbruch |
| **Action / Undo** | 🟣 Indigo / Violet | 5 Sekunden | Gelöschte Zähler, deaktivierte Automatismen (mit `onUndo()` Callback) |

---

## 🛠️ 4. Technische Komponenten & Umsetzungsschritte

1. **`frontend/src/components/ui/ToastProvider.jsx`**:
   - Stack-Manager für bis zu 3 gleichzeitig sichtbare Toasts.
   - Smooth Slide-in / Fade-out Animationen via Framer Motion / CSS Transitions.
   - Swipe-to-Dismiss auf mobilen Touch-Geräten.
2. **Globaler Hook `frontend/src/hooks/useToast.js`**:
   ```javascript
   import { useToast } from '@/hooks/useToast';
   
   const { toast } = useToast();
   
   // Einfacher Toast:
   toast.success('Dimm-Befehl erfolgreich übermittelt');
   
   // Toast mit Undo-Aktion:
   toast.action('Zähler gelöscht', {
     actionLabel: 'Rückgängig',
     onAction: () => restoreMeter(meterId),
     durationMs: 5000,
   });
   ```
3. **Integration in `App.jsx`**:
   - Bereitstellung des Context-Providers um die gesamte Anwendungs-Hierarchie.
