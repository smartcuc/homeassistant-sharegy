import os

search_terms = [
    'Noch keine Messdaten',
    'Electricity Tariffs',
    'Autarkie (Heute)',
    'Autarkie (',
    'Finanzvorteil (',
    'Omi',
    'Basis',
    'Eingespart',
    'Experten'
]

results = []
for root, dirs, files in os.walk('frontend/src'):
    if 'node_modules' in root or 'locales' in root:
        continue
    for file in files:
        if file.endswith(('.jsx', '.js')):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    for st in search_terms:
                        if st.lower() in line.lower():
                            results.append(f"{fp}:{i}: [{st}] -> {line.strip()}")

with open('scratch/missing_findings_2.txt', 'w', encoding='utf-8') as out:
    for r in results:
        out.write(r + '\n')

print(f"Found {len(results)} matches.")
