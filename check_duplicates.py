import json
from collections import defaultdict

# Lire le fichier unifié
with open('DATA_SIERRA_CHART/DATA_2025/SEPTEMBRE/20250919/unified_20250919.jsonl', 'r') as f:
    lines = f.readlines()

print("=== VÉRIFICATION DES DOUBLONS DANS L'UNIFIER ===")

# Analyser les timestamps
timestamps = []
duplicate_timestamps = defaultdict(list)
duplicate_buckets = defaultdict(list)

for i, line in enumerate(lines):
    try:
        data = json.loads(line)
        t = data.get('t')
        if t is not None:
            timestamps.append(t)
            duplicate_timestamps[t].append(i)
            
            # Vérifier les buckets (basé sur basedata)
            basedata = data.get('basedata', {})
            if basedata:
                bucket_key = f"{basedata.get('sym', 'unknown')}_{basedata.get('i', 'unknown')}"
                duplicate_buckets[bucket_key].append(i)
    except json.JSONDecodeError:
        print(f"❌ Erreur JSON ligne {i+1}")

print(f"📊 STATISTIQUES GLOBALES:")
print(f"   - Lignes totales: {len(lines)}")
print(f"   - Timestamps uniques: {len(set(timestamps))}")
print(f"   - Timestamps dupliqués: {len(timestamps) - len(set(timestamps))}")

# Vérifier les timestamps dupliqués
print(f"\n🔍 TIMESTAMPS DUPLIQUÉS:")
timestamp_duplicates = {k: v for k, v in duplicate_timestamps.items() if len(v) > 1}
if timestamp_duplicates:
    for timestamp, line_indices in timestamp_duplicates.items():
        print(f"   - Timestamp {timestamp}: lignes {line_indices}")
else:
    print("   ✅ Aucun timestamp dupliqué")

# Vérifier les buckets dupliqués
print(f"\n🔍 BUCKETS DUPLIQUÉS:")
bucket_duplicates = {k: v for k, v in duplicate_buckets.items() if len(v) > 1}
if bucket_duplicates:
    for bucket, line_indices in bucket_duplicates.items():
        print(f"   - Bucket {bucket}: lignes {line_indices}")
else:
    print("   ✅ Aucun bucket dupliqué")

# Vérifier les lignes identiques
print(f"\n🔍 LIGNES IDENTIQUES:")
line_hashes = defaultdict(list)
for i, line in enumerate(lines):
    line_hash = hash(line.strip())
    line_hashes[line_hash].append(i)

identical_lines = {k: v for k, v in line_hashes.items() if len(v) > 1}
if identical_lines:
    for line_hash, line_indices in identical_lines.items():
        print(f"   - Lignes identiques: {line_indices}")
else:
    print("   ✅ Aucune ligne identique")

# Vérifier la progression temporelle
print(f"\n🔍 PROGRESSION TEMPORELLE:")
timestamps_sorted = sorted(timestamps)
for i in range(1, len(timestamps_sorted)):
    if timestamps_sorted[i] < timestamps_sorted[i-1]:
        print(f"   ❌ Rétrogradation temporelle: {timestamps_sorted[i-1]} → {timestamps_sorted[i]}")
        break
else:
    print("   ✅ Progression temporelle correcte")

# Vérifier les champs manquants
print(f"\n🔍 CHAMPS MANQUANTS:")
required_fields = ['t', 'basedata', 'vwap', 'vva', 'pvwap', 'depth', 'nbcv', 'menthorq', 'atr', 'cumulative_delta']
field_presence = {field: 0 for field in required_fields}

for line in lines:
    try:
        data = json.loads(line)
        for field in required_fields:
            if field in data and data[field] is not None:
                field_presence[field] += 1
    except json.JSONDecodeError:
        continue

print(f"   Présence des champs:")
for field, count in field_presence.items():
    percentage = (count / len(lines)) * 100
    status = "✅" if percentage > 70 else "⚠️" if percentage > 30 else "❌"
    print(f"     {field}: {count}/{len(lines)} ({percentage:.1f}%) {status}")

print(f"\n🎯 RÉSUMÉ:")
if not timestamp_duplicates and not bucket_duplicates and not identical_lines:
    print("   ✅ AUCUN DOUBLON DÉTECTÉ - FICHIER PROPRE")
else:
    print("   ⚠️ DOUBLONS DÉTECTÉS - NÉCESSITE NETTOYAGE")




