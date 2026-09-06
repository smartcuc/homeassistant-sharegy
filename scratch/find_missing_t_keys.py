import os
import re
import json

src_dir = r"c:\Users\Public\Dev\eswes\frontend\src"
de_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\de.json"
en_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\en.json"

with open(de_path, "r", encoding="utf-8") as f:
    de = json.load(f)

with open(en_path, "r", encoding="utf-8") as f:
    en = json.load(f)

def get_keys(d, prefix=""):
    res = {}
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            res.update(get_keys(v, full))
        else:
            res[full] = v
    return res

de_keys = get_keys(de)

# Regex to find t("key", "fallback") or t('key', 'fallback') or t("key")
t_call_regex = re.compile(r't\(\s*["\']([^"\']+)["\'](?:\s*,\s*["\']((?:[^"\\]|\\.)*)["\'])?')

used_keys = {}
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".jsx") or f.endswith(".js"):
            full_path = os.path.join(root, f)
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
            for match in t_call_regex.finditer(content):
                key = match.group(1)
                fallback = match.group(2)
                used_keys[key] = fallback

missing_in_de_dict = {}
for k, fb in used_keys.items():
    if k not in de_keys:
        missing_in_de_dict[k] = fb

print(f"Total unique t(...) keys in JSX: {len(used_keys)}")
print(f"Keys used in JSX but missing in de.json: {len(missing_in_de_dict)}")
for k, fb in list(missing_in_de_dict.items())[:30]:
    print(f"  {k} -> fallback: '{fb}'")
