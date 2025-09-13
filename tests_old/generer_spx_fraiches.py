
#!/usr/bin/env python3
"""
Générateur de données SPX fraîches pour MIA_IA_SYSTEM
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generer_donnees_spx_fraiches():
    """Générer des données SPX fraîches"""
    
    print("🔄 Génération données SPX fraîches...")
    
    # Créer le répertoire si nécessaire
    os.makedirs("data/options_snapshots/final", exist_ok=True)
    
    # Données SPX simulées mais réalistes
    current_time = datetime.now()
    
    # Prix ES actuel (corrigé)
    es_price = 6489.0
    
    # Générer strikes autour du prix actuel
    strikes = np.arange(es_price - 200, es_price + 200, 25)
    
    # Données options réalistes
    data = []
    for strike in strikes:
        # Calculer des valeurs réalistes
        moneyness = es_price / strike
        days_to_expiry = 30  # 30 jours
        
        # Volatilité implicite basée sur moneyness
        if moneyness > 1.02:  # ITM
            iv = 0.15 + np.random.normal(0, 0.02)
        elif moneyness < 0.98:  # OTM
            iv = 0.25 + np.random.normal(0, 0.03)
        else:  # ATM
            iv = 0.20 + np.random.normal(0, 0.02)
        
        # Open Interest réaliste
        oi = int(np.random.uniform(100, 5000))
        
        # Volume
        volume = int(np.random.uniform(10, 500))
        
        # Bid/Ask
        bid = max(0.05, np.random.uniform(0.05, 50))
        ask = bid * (1 + np.random.uniform(0.01, 0.1))
        
        # Données pour calls et puts
        for option_type in ['C', 'P']:
            data.append({
                'symbol': 'SPX',
                'expiry': (current_time + timedelta(days=days_to_expiry)).strftime('%Y-%m-%d'),
                'strike': strike,
                'option_type': option_type,
                'bid': bid,
                'ask': ask,
                'last': (bid + ask) / 2,
                'volume': volume,
                'open_interest': oi,
                'implied_volatility': iv,
                'delta': np.random.uniform(-1, 1),
                'gamma': np.random.uniform(0, 0.01),
                'theta': np.random.uniform(-0.1, 0),
                'vega': np.random.uniform(0, 100),
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Créer DataFrame
    df = pd.DataFrame(data)
    
    # Sauvegarder avec timestamp frais
    filename = f"spx_fresh_{current_time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = f"data/options_snapshots/final/{filename}"
    
    df.to_csv(filepath, index=False)
    
    print(f"✅ Données SPX fraîches générées: {filename}")
    print(f"   📊 {len(df)} options générées")
    print(f"   💰 Prix ES: {es_price}")
    print(f"   ⏰ Timestamp: {current_time.strftime('%H:%M:%S')}")
    
    return filepath

if __name__ == "__main__":
    generer_donnees_spx_fraiches()
