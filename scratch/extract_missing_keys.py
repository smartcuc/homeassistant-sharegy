import os
import re
import json

src_dir = r"c:\Users\Public\Dev\eswes\frontend\src"
de_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\de.json"
en_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\en.json"
pl_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\pl.json"

with open(de_path, "r", encoding="utf-8") as f:
    de_data = json.load(f)

with open(en_path, "r", encoding="utf-8") as f:
    en_data = json.load(f)

with open(pl_path, "r", encoding="utf-8") as f:
    pl_data = json.load(f)

def get_flat_keys(d, prefix=""):
    res = {}
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            res.update(get_flat_keys(v, full))
        else:
            res[full] = v
    return res

de_flat = get_flat_keys(de_data)
en_flat = get_flat_keys(en_data)

# Regex to find t("...", "...")
t_regex = re.compile(r't\(\s*["\']([a-zA-Z0-9_\.\-]+)["\'](?:\s*,\s*["\']((?:[^"\\]|\\.)*)["\'])?')

extracted_keys = {}
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".jsx") or f.endswith(".js"):
            full_path = os.path.join(root, f)
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
            for m in t_regex.finditer(content):
                key = m.group(1)
                fallback = m.group(2)
                # Ignore dynamic paths / tracking event keys if they look like file paths
                if key.startswith(".") or "/" in key:
                    continue
                extracted_keys[key] = fallback or key

missing_in_en = {k: v for k, v in extracted_keys.items() if k not in en_flat}

print(f"Extracted valid keys from codebase: {len(extracted_keys)}")
print(f"Missing in en.json: {len(missing_in_en)}")

# Save to inspect
with open(r"c:\Users\Public\Dev\eswes\scratch\missing_keys.json", "w", encoding="utf-8") as f:
    json.dump(missing_in_en, f, indent=2, ensure_ascii=False)

print("Saved missing keys to scratch/missing_keys.json")
