import os

src_dir = r"c:\Users\Public\Dev\eswes\frontend\src"

no_i18n = []
with_i18n = []

for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".jsx"):
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, src_dir)
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
            if "useTranslation" not in content and "t(" not in content:
                no_i18n.append((rel_path, len(content.splitlines())))
            else:
                with_i18n.append(rel_path)

print(f"Total with i18n: {len(with_i18n)}")
print(f"Total without i18n: {len(no_i18n)}\n")

print("Files without i18n (sorted by line count):")
for path, lines in sorted(no_i18n, key=lambda x: x[1], reverse=True):
    print(f"  {lines:4d} lines: {path}")
