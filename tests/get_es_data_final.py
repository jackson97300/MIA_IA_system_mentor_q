#!/usr/bin/env python3
"""
Script final pour récupérer les données ES futures
Conid validé: 265598
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

class ESDataRetriever:
    """Récupérateur de données ES futures"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.es_conid = "265598"  # Conid validé
        
    def connect(self):
        """Se connecter au gateway"""
        if not self.connector.connect():
            print("❌ Impossible de se connecter au gateway")
            return False
            
        if not self.connector.config.authenticated:
            if not self.connector.authenticate():
                print("❌ Authentification échouée")
                return False
        
        print("✅ Connecté et authentifié")
        return True
    
    def get_current_price(self):
        """Récupérer le prix actuel ES"""
        try:
            fields = ["31", "83", "84"]  # bid, ask, last
            market_data = self.connector.get_market_data(self.es_conid, fields)
            
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                data = market_data[0]
                return {
                    'bid': data.get('31'),
                    'ask': data.get('83'),
                    'last': data.get('84'),
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"❌ Erreur prix actuel: {e}")
            return None
    
    def get_ohlc_data(self, period="1d", bar="1min", limit=100):
        """Récupérer données OHLC ES"""
        try:
            historical = self.connector.get_historical_data(self.es_conid, period, bar)
            
            if historical:
                # Convertir en format OHLC standard
                ohlc_data = []
                for bar_data in historical[-limit:]:  # Dernières barres
                    ohlc_data.append({
                        'timestamp': bar_data.get('t'),
                        'open': bar_data.get('o'),
                        'high': bar_data.get('h'),
                        'low': bar_data.get('l'),
                        'close': bar_data.get('c'),
                        'volume': bar_data.get('v')
                    })
                return ohlc_data
            return None
        except Exception as e:
            print(f"❌ Erreur OHLC: {e}")
            return None
    
    def get_es_summary(self):
        """Récupérer un résumé complet ES"""
        print("📊 Récupération données ES futures...")
        print("=" * 50)
        
        # 1. Prix actuel
        print("1️⃣ Prix actuel...")
        current_price = self.get_current_price()
        if current_price:
            print(f"   Bid: {current_price['bid']}")
            print(f"   Ask: {current_price['ask']}")
            print(f"   Last: {current_price['last']}")
        else:
            print("   ❌ Prix non disponible")
        
        # 2. Données 1 minute
        print("\n2️⃣ Données 1 minute (dernières 10 barres)...")
        ohlc_1min = self.get_ohlc_data("1d", "1min", 10)
        if ohlc_1min:
            print(f"   ✅ {len(ohlc_1min)} barres récupérées")
            print("   Dernières 3 barres:")
            for i, bar in enumerate(ohlc_1min[-3:]):
                print(f"      Barre {i+1}: O={bar['open']}, H={bar['high']}, L={bar['low']}, C={bar['close']}, V={bar['volume']}")
        else:
            print("   ❌ Données 1min non disponibles")
        
        # 3. Données 5 minutes
        print("\n3️⃣ Données 5 minutes (dernières 10 barres)...")
        ohlc_5min = self.get_ohlc_data("5d", "5min", 10)
        if ohlc_5min:
            print(f"   ✅ {len(ohlc_5min)} barres récupérées")
            print("   Dernières 3 barres:")
            for i, bar in enumerate(ohlc_5min[-3:]):
                print(f"      Barre {i+1}: O={bar['open']}, H={bar['high']}, L={bar['low']}, C={bar['close']}, V={bar['volume']}")
        else:
            print("   ❌ Données 5min non disponibles")
        
        # 4. Statistiques
        print("\n4️⃣ Statistiques...")
        if ohlc_1min:
            closes = [bar['close'] for bar in ohlc_1min]
            volumes = [bar['volume'] for bar in ohlc_1min]
            
            print(f"   Prix min: {min(closes)}")
            print(f"   Prix max: {max(closes)}")
            print(f"   Volume total: {sum(volumes):.0f}")
            print(f"   Volume moyen: {sum(volumes)/len(volumes):.0f}")
        
        return {
            'current_price': current_price,
            'ohlc_1min': ohlc_1min,
            'ohlc_5min': ohlc_5min,
            'conid': self.es_conid
        }
    
    def save_data_to_file(self, data, filename="es_data.json"):
        """Sauvegarder les données dans un fichier"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Données sauvegardées dans {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def disconnect(self):
        """Se déconnecter"""
        self.connector.disconnect()

def main():
    """Fonction principale"""
    print("🚀 Récupérateur de données ES futures")
    print("Conid: 265598 (validé)")
    print("=" * 60)
    
    retriever = ESDataRetriever()
    
    try:
        # Connexion
        if not retriever.connect():
            return
        
        # Récupération données
        data = retriever.get_es_summary()
        
        # Sauvegarde
        retriever.save_data_to_file(data)
        
        print("\n🎉 Récupération terminée avec succès!")
        print(f"💡 Conid ES à utiliser: {retriever.es_conid}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        retriever.disconnect()

if __name__ == "__main__":
    main()

