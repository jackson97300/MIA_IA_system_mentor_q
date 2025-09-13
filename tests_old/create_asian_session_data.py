#!/usr/bin/env python3
"""
Création de données de test pour la session Asie
MIA_IA_SYSTEM - Session Asie Data Generator
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import json
import csv
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

def create_asian_session_data():
    """Crée des données de test pour la session Asie"""
    
    # Créer le dossier de données
    data_dir = Path("data/options_snapshots/final")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Données SPX simulées pour session Asie
    spx_data = {
        "timestamp": datetime.now().isoformat(),
        "session": "asia_session",
        "spx_options": {
            "total_volume": 15000,
            "put_volume": 8500,
            "call_volume": 6500,
            "put_call_ratio": 1.31,
            "gamma_exposure": -0.25,
            "dealer_position": 0.15,
            "pin_levels": [4500, 4525, 4550],
            "unusual_activity": {
                "large_blocks": 3,
                "sweeps": 7,
                "gamma_hedging": True
            }
        },
        "market_data": {
            "es_price": 4532.50,
            "es_volume": 12500,
            "es_delta": 850,
            "vix": 18.5,
            "session_volatility": "moderate"
        }
    }
    
    # Sauvegarder en CSV
    filename = f"spx_final_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = data_dir / filename
    
    df = pd.DataFrame([{
        'timestamp': spx_data["timestamp"],
        'data_source': 'saved_data',
        'spx_data': json.dumps(spx_data)
    }])
    
    df.to_csv(filepath, index=False)
    
    print(f"✅ Données session Asie créées: {filename}")
    print(f"   📊 Volume total: {spx_data['spx_options']['total_volume']}")
    print(f"   📈 Put/Call Ratio: {spx_data['spx_options']['put_call_ratio']}")
    print(f"   🎯 Gamma Exposure: {spx_data['spx_options']['gamma_exposure']}")
    print(f"   💰 ES Price: {spx_data['market_data']['es_price']}")
    
    return filepath

if __name__ == "__main__":
    create_asian_session_data()
