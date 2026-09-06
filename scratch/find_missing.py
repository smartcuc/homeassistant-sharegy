import os

phrases = [
    'Dein Energiechart kommt',
    'Einfach',
    'Autarkie (Heute)',
    'deines Strombedarfs stammten',
    'Systemstatus & Live-Infrastruktur',
    'Erzeuger- & Speicheranlagen',
    'Finanzvorteil (Heute)',
    'Eingespart',
    'Vermiedene Stromkosten durch Eigenverbrauch',
    'CO₂ vermieden',
    'Eigenverbrauch:',
    'Noch keine Einzelgeräte erfasst',
    'Noch keine Messdaten für diesen Zeitraum',
    'Möchtest du detaillierte Phasenströme',
    'Zu den Experten-Tools',
    'Omi-check',
    'Omi',
    'Willkommen bei Sharegy'
]

results = []
for root, dirs, files in os.walk('frontend/src'):
    if 'node_modules' in root:
        continue
    for file in files:
        if file.endswith(('.jsx', '.js')):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for p in phrases:
                        if p.lower() in line.lower():
                            results.append(f"{fp}:{i}: [{p}] -> {line.strip()}")

with open('scratch/missing_findings.txt', 'w', encoding='utf-8') as out:
    for r in results:
        out.write(r + '\n')

print(f"Found {len(results)} matches. Wrote to scratch/missing_findings.txt")
