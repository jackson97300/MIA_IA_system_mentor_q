#!/usr/bin/env python3
"""
🔧 CRÉATION FICHIER CSV CORRECT - MIA_IA_SYSTEM
==============================================

Crée le fichier CSV avec le bon format que OptionsDataManager cherche.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

def create_correct_csv():
    """Crée le fichier CSV correct pour OptionsDataManager"""
    
    print("🔧 Création fichier CSV correct...")
    
    # Lire les données JSON existantes
    data_dir = Path("data/options_snapshots")
    json_file = data_dir / "spx_final_20250811.json"
    
    if not json_file.exists():
        print("❌ Fichier JSON non trouvé")
        return False
    
    # Lire les données JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"   📊 Données JSON: VIX {data['vix_level']:.1f}")
    
    # Créer le fichier CSV avec le bon format
    csv_file = data_dir / "spx_options_final_20250811.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # En-têtes selon le format attendu par OptionsDataManager
        headers = [
            'timestamp', 'session_type', 'vix_level', 'put_call_ratio',
            'put_call_volume_ratio', 'call_volume', 'put_volume', 'call_oi',
            'put_oi', 'gamma_exposure', 'dealer_position', 'gamma_flip_level',
            'pin_levels', 'unusual_activity'
        ]
        writer.writerow(headers)
        
        # Données
        row = [
            data.get('timestamp', datetime.now(timezone.utc).isoformat()),
            'asia_session',  # Session actuelle
            data.get('vix_level', 20.5),
            data.get('put_call_ratio', 0.85),
            data.get('put_call_volume_ratio', 0.80),
            data.get('call_volume', 25000),
            data.get('put_volume', 20000),
            data.get('call_oi', 1000000),
            data.get('put_oi', 800000),
            data.get('gamma_exposure', 75e9),
            data.get('dealer_position', 'neutral'),
            data.get('gamma_flip_level', 5400.0),
            ','.join(map(str, data.get('pin_levels', [5400, 5450, 5500]))),
            str(data.get('unusual_activity', False)).lower()
        ]
        writer.writerow(row)
    
    print(f"   ✅ Fichier CSV créé: {csv_file}")
    return True

if __name__ == "__main__":
    success = create_correct_csv()
    if success:
        print("🎉 Fichier CSV correct créé!")
        print("   OptionsDataManager peut maintenant le trouver")
    else:
        print("❌ Échec création fichier CSV")

