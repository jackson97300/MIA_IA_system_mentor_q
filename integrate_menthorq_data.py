#!/usr/bin/env python3
"""
Script pour intégrer les données MenthorQ du fichier chart_10_20250909.jsonl
dans le fichier unifié mia_unified_20250907.jsonl
"""

import json
import os
from datetime import datetime
from pathlib import Path

def integrate_menthorq_data():
    """Intègre les données MenthorQ dans le fichier unifié"""
    
    # Chemins des fichiers
    chart_10_file = "chart_10_20250909.jsonl"
    unified_file = "mia_unified_20250907.jsonl"
    
    if not os.path.exists(chart_10_file):
        print(f"❌ Fichier {chart_10_file} non trouvé")
        return False
    
    if not os.path.exists(unified_file):
        print(f"❌ Fichier {unified_file} non trouvé")
        return False
    
    print(f"🔄 Intégration des données MenthorQ...")
    print(f"   Source: {chart_10_file}")
    print(f"   Cible: {unified_file}")
    
    # Lire les données MenthorQ
    menthorq_events = []
    with open(chart_10_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                if data.get('type') == 'menthorq':
                    # Convertir au format unifié
                    unified_event = {
                        "type": "menthorq_level",
                        "graph": data.get('chart', 10),
                        "sym": data.get('sym', 'ESU25_FUT_CME'),
                        "price": data.get('px', 0.0),
                        "level_type": data.get('name', 'unknown'),
                        "strength": data.get('sg', 1),
                        "t": data.get('t', 0),
                        "ingest_ts": datetime.now().isoformat(),
                        "file_path": chart_10_file
                    }
                    menthorq_events.append(unified_event)
            except json.JSONDecodeError as e:
                print(f"⚠️ Erreur ligne {line_num}: {e}")
                continue
    
    print(f"✅ {len(menthorq_events)} événements MenthorQ extraits")
    
    # Ajouter au fichier unifié
    with open(unified_file, 'a') as f:
        for event in menthorq_events:
            f.write(json.dumps(event) + '\n')
    
    print(f"✅ Données MenthorQ intégrées dans {unified_file}")
    return True

if __name__ == "__main__":
    success = integrate_menthorq_data()
    if success:
        print("🎉 Intégration terminée avec succès !")
    else:
        print("❌ Échec de l'intégration")



