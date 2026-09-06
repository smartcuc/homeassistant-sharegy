import json
import os

de_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\de.json"
en_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\en.json"

with open(de_path, "r", encoding="utf-8") as f:
    de = json.load(f)

with open(en_path, "r", encoding="utf-8") as f:
    en = json.load(f)

def get_all_keys(d, prefix=""):
    keys = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(get_all_keys(v, full_key))
        else:
            keys[full_key] = v
    return keys

de_keys = get_all_keys(de)
en_keys = get_all_keys(en)

missing_in_en = [k for k in de_keys if k not in en_keys]
missing_in_de = [k for k in en_keys if k not in de_keys]

print(f"Total keys in DE: {len(de_keys)}")
print(f"Total keys in EN: {len(en_keys)}")
print(f"Missing in EN: {len(missing_in_en)}")
print(f"Missing in DE: {len(missing_in_de)}")

if missing_in_en:
    print("\nSample missing in EN:")
    for k in missing_in_en[:50]:
        print(f"  {k} -> DE: '{de_keys[k]}'")
