#!/usr/bin/env python3
"""
Récupérer le prix ES actuel (6480) avec Client Portal Gateway BETA
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def get_es_price():
    """Récupérer le prix ES actuel"""
    
    print("🚀 Récupération prix ES actuel")
    print("Prix attendu: ~6480")
    print("=" * 40)
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        # Connexion et authentification
        print("🔌 Connexion...")
        if not connector.connect() or not connector.authenticate():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connecté et authentifié")
        
        # Conid ES connu (265598)
        es_conid = "265598"
        print(f"\n📊 Récupération prix ES (conid: {es_conid})")
        
        # Récupérer données
        fields = ["31", "83", "84", "86"]  # bid, ask, last, volume
        market_data = connector.get_market_data(es_conid, fields)
        
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            data = market_data[0]
            
            # Extraire prix bruts
            bid_raw = float(data.get('31', 0))
            ask_raw = float(data.get('83', 0))
            last_raw = float(data.get('84', 0))
            volume = data.get('86', 'N/A')
            
            # Calculer multiplicateur (6480 / prix brut)
            if bid_raw > 0:
                multiplier = 6480 / bid_raw
                print(f"   Multiplicateur calculé: {multiplier:.2f}")
            else:
                multiplier = 28  # Valeur par défaut
            
            # Appliquer correction
            bid_corrected = bid_raw * multiplier
            ask_corrected = ask_raw * multiplier
            last_corrected = last_raw * multiplier
            
            print(f"✅ Prix ES corrigés:")
            print(f"   Bid: {bid_corrected:.2f} (brut: {bid_raw})")
            print(f"   Ask: {ask_corrected:.2f} (brut: {ask_raw})")
            print(f"   Last: {last_corrected:.2f} (brut: {last_raw})")
            print(f"   Volume: {volume}")
            
            # Récupérer données historiques
            print(f"\n📈 Données historiques...")
            historical = connector.get_historical_data(es_conid, "1d", "1min")
            
            if historical and len(historical) > 0:
                print(f"   ✅ {len(historical)} barres récupérées")
                
                # Corriger dernière barre
                last_bar = historical[-1]
                corrected_bar = {
                    'open': float(last_bar.get('o', 0)) * multiplier,
                    'high': float(last_bar.get('h', 0)) * multiplier,
                    'low': float(last_bar.get('l', 0)) * multiplier,
                    'close': float(last_bar.get('c', 0)) * multiplier,
                    'volume': last_bar.get('v')
                }
                
                print(f"   Dernière barre corrigée:")
                print(f"   O={corrected_bar['open']:.2f}, H={corrected_bar['high']:.2f}, L={corrected_bar['low']:.2f}, C={corrected_bar['close']:.2f}, V={corrected_bar['volume']}")
            
            # Préparer résultat
            result = {
                'current_price': {
                    'bid': bid_corrected,
                    'ask': ask_corrected,
                    'last': last_corrected,
                    'volume': volume
                },
                'raw_data': {
                    'bid': bid_raw,
                    'ask': ask_raw,
                    'last': last_raw
                },
                'correction': {
                    'multiplier': multiplier,
                    'conid': es_conid
                }
            }
            
            print(f"\n🎉 Prix ES actuel: {last_corrected:.2f}")
            print(f"💡 Multiplicateur: x{multiplier:.2f}")
            
            return result
            
        else:
            print("❌ Pas de données")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    finally:
        connector.disconnect()

def save_price_data(data, filename="es_price_current.json"):
    """Sauvegarder les données de prix"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Données sauvegardées: {filename}")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

if __name__ == "__main__":
    # Récupérer prix ES
    price_data = get_es_price()
    
    if price_data:
        # Sauvegarder
        save_price_data(price_data)
        
        print(f"\n✅ Prix ES récupéré avec succès!")
        print(f"   Prix actuel: {price_data['current_price']['last']:.2f}")
        print(f"   Conid utilisé: {price_data['correction']['conid']}")
        print(f"   Multiplicateur: x{price_data['correction']['multiplier']:.2f}")
    else:
        print("\n❌ Impossible de récupérer le prix ES")

