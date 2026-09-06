import os
import re
import glob

src_dir = r"c:\Users\Public\Dev\eswes\frontend\src"

# German words regex
german_patterns = [
    r"\b(und|oder|für|nicht|über|mit|ohne|von|bis|nach|vor|beim|beim|durch|aus|ins|im|zur|zum)\b",
    r"\b(Erzeugung|Verbrauch|Einspeisung|Netzbezug|Haushalt|Batterie|Speicher|Zähler|Gerät|Geräte|Steuerung|Übersicht|Einstellungen|Schnittstellen|Prognose|Tarife|Abrechnung|Gemeinschaften|Hilfe)\b",
    r"\b(Laden|Entladen|Abbrechen|Speichern|Kopieren|Schließen|Bearbeiten|Löschen|Hinzufügen|Aktualisieren|Zurück|Weiter|Erfolgreich|Fehler|Warnung|Aktiv|Inaktiv)\b",
    r"\b(Heute|Gestern|Monat|Woche|Jahr|Tage|Stunden|Minuten|Sekunden|Echtzeit|Autarkie|Eigenverbrauch)\b",
    r"[äöüßÄÖÜ]"
]

combined_regex = re.compile("|".join(german_patterns), re.IGNORECASE)

jsx_files = []
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".jsx"):
            jsx_files.append(os.path.join(root, f))

results = {}

for file_path in jsx_files:
    rel_path = os.path.relpath(file_path, src_dir)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    file_matches = []
    has_use_translation = False
    for idx, line in enumerate(lines, 1):
        if "useTranslation" in line:
            has_use_translation = True
        
        # Check if line contains german text not inside t("...") or comments or console.log
        # Strip comments
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue
        if "console.log" in stripped or "console.error" in stripped or "console.warn" in stripped:
            continue
            
        # Check if there are matches
        matches = combined_regex.findall(line)
        if matches:
            # Check if it's already inside t("...")
            # If line has t(..., "...") and the match is ONLY the fallback, that's fine, but let's check if the key exists in locale!
            file_matches.append((idx, line.strip()))
            
    if file_matches:
        results[rel_path] = {
            "has_i18n": has_use_translation,
            "match_count": len(file_matches),
            "samples": file_matches[:10]
        }

print(f"Total JSX files: {len(jsx_files)}")
print(f"Files with potential German text: {len(results)}\n")

# Sort by match count
for f, data in sorted(results.items(), key=lambda x: x[1]["match_count"], reverse=True):
    print(f"{f} (has useTranslation: {data['has_i18n']}, {data['match_count']} lines):")
    for lnum, ltext in data["samples"][:3]:
        print(f"   L{lnum}: {ltext[:100]}")
    print()
