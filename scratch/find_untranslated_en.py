import json
import re
import os
import glob

# 1. Check en.json for suspicious German words (e.g. 'der', 'die', 'das', 'und', 'für', 'nicht', 'übersicht', 'einstellungen', 'geräte', 'speicher', 'strom', 'erzeugung', 'hausverbrauch')
german_markers = [
    r"\bder\b", r"\bdie\b", r"\bdas\b", r"\bund\b", r"\bfür\b", r"\bnicht\b", r"\büber\b",
    r"\bGeräte\b", r"\bSpeicher\b", r"\bStrom\b", r"\bErzeugung\b", r"\bHausverbrauch\b",
    r"\bNetz\b", r"\bLaden\b", r"\bEntladen\b", r"\bHeute\b", r"\bMonat\b", r"\bJahr\b",
    r"\bKopieren\b", r"\bAbbrechen\b", r"\bSpeichern\b", r"\bBearbeiten\b", r"\bLöschen\b",
    r"\bSchließen\b", r"\bErfolgreich\b", r"\bFehler\b", r"\bBitte\b", r"\bAuswahl\b",
    r"\bÜbersicht\b", r"\bEinstellungen\b", r"\bSchnittstellen\b", r"\bSteuerung\b"
]

en_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\en.json"
with open(en_path, "r", encoding="utf-8") as f:
    en = json.load(f)

def flatten(d, prefix=""):
    res = {}
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            res.update(flatten(v, full))
        else:
            res[full] = str(v)
    return res

en_flat = flatten(en)
untranslated = {}
for k, val in en_flat.items():
    for gm in german_markers:
        if re.search(gm, val, re.IGNORECASE):
            untranslated[k] = val
            break

print(f"Potentially untranslated keys in en.json: {len(untranslated)}")
for k, v in list(untranslated.items())[:30]:
    print(f"  {k}: {v}")
