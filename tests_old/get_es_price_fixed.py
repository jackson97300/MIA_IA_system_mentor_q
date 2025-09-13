#!/usr/bin/env python3
"""
Récupérer le prix ES correct avec Client Portal Gateway BETA
Correction du format de prix (231.19 → 6482)
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

class ESPriceRetrieverFixed:
    """Récupérateur ES avec correction format prix"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.es_conid = None
        self.price_multiplier = 28  # 6482 / 231.19 ≈ 28
        
    def connect_and_authenticate(self):
        """Connexion et authentification"""
        print("🔌 Connexion au Client Portal Gateway BETA...")
        
        if not self.connector.connect():
            print("❌ Connexion échouée")
            return False
        
        if not self.connector.authenticate():
            print("❌ Authentification échouée")
            return False
        
        print("✅ Connecté et authentifié")
        return True
    
    def find_correct_es_conid(self):
        """Trouver le bon conid ES"""
        print("\n🔍 Recherche conid ES correct...")
        
        # Conids à tester (basés sur nos tests précédents)
        test_conids = [
            "265598",  # Conid testé (231.19)
            "265599", "265600", "265601", "265602",
            "265603", "265604", "265605", "265606",
            "265607", "265608", "265609", "265610"
        ]
        
        for conid in test_conids:
            print(f"   Test conid: {conid}")
            
            # Récupérer données
            fields = ["31", "84"]  # bid, last
            market_data = self.connector.get_market_data(conid, fields)
            
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                data = market_data[0]
                bid = data.get('31')
                last = data.get('84')
                
                if bid and bid != "-1":
                    try:
                        bid_price = float(bid)
                        print(f"      Bid brut: {bid_price}")
                        
                        # Appliquer correction
                        corrected_price = bid_price * self.price_multiplier
                        print(f"      Bid corrigé: {corrected_price}")
                        
                        # Vérifier si c'est dans la plage ES
                        if 6000 <= corrected_price <= 7000:
                            print(f"      🎯 CONID ES TROUVÉ: {conid}")
                            print(f"      Prix ES: {corrected_price}")
                            self.es_conid = conid
                            return True
                        
                    except ValueError:
                        print(f"      ❌ Prix invalide: {bid}")
                else:
                    print(f"      ❌ Pas de prix bid")
            else:
                print(f"      ❌ Pas de données")
        
        print("❌ Aucun conid ES valide trouvé")
        return False
    
    def get_current_price(self):
        """Récupérer le prix actuel ES (corrigé)"""
        if not self.es_conid:
            print("❌ Conid ES non trouvé")
            return None
        
        try:
            print(f"\n📊 Récupération prix ES (conid: {self.es_conid})")
            
            # Récupérer toutes les données
            fields = ["31", "83", "84", "86", "87", "88", "89", "90"]
            market_data = self.connector.get_market_data(self.es_conid, fields)
            
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                data = market_data[0]
                
                # Extraire et corriger les prix
                bid_raw = float(data.get('31', 0))
                ask_raw = float(data.get('83', 0))
                last_raw = float(data.get('84', 0))
                
                # Appliquer correction
                bid_corrected = bid_raw * self.price_multiplier
                ask_corrected = ask_raw * self.price_multiplier
                last_corrected = last_raw * self.price_multiplier
                
                print(f"✅ Prix ES corrigés:")
                print(f"   Bid: {bid_corrected:.2f} (brut: {bid_raw})")
                print(f"   Ask: {ask_corrected:.2f} (brut: {ask_raw})")
                print(f"   Last: {last_corrected:.2f} (brut: {last_raw})")
                print(f"   Volume: {data.get('86', 'N/A')}")
                print(f"   High: {float(data.get('87', 0)) * self.price_multiplier:.2f}")
                print(f"   Low: {float(data.get('88', 0)) * self.price_multiplier:.2f}")
                print(f"   Open: {float(data.get('89', 0)) * self.price_multiplier:.2f}")
                
                return {
                    'price': last_corrected,
                    'bid': bid_corrected,
                    'ask': ask_corrected,
                    'volume': data.get('86'),
                    'high': float(data.get('87', 0)) * self.price_multiplier,
                    'low': float(data.get('88', 0)) * self.price_multiplier,
                    'open': float(data.get('89', 0)) * self.price_multiplier,
                    'conid': self.es_conid,
                    'multiplier_used': self.price_multiplier
                }
            
            else:
                print("❌ Pas de données de prix")
                return None
                
        except Exception as e:
            print(f"❌ Erreur récupération prix: {e}")
            return None
    
    def get_historical_data(self, period="1d", bar_size="1min"):
        """Récupérer données historiques ES (corrigées)"""
        if not self.es_conid:
            print("❌ Conid ES non trouvé")
            return None
        
        try:
            print(f"\n📈 Récupération données historiques...")
            
            historical = self.connector.get_historical_data(self.es_conid, period, bar_size)
            
            if historical and len(historical) > 0:
                print(f"✅ {len(historical)} barres récupérées")
                
                # Corriger les prix historiques
                corrected_bars = []
                for bar in historical[-10:]:  # 10 dernières barres
                    corrected_bar = {
                        'timestamp': bar.get('t'),
                        'open': float(bar.get('o', 0)) * self.price_multiplier,
                        'high': float(bar.get('h', 0)) * self.price_multiplier,
                        'low': float(bar.get('l', 0)) * self.price_multiplier,
                        'close': float(bar.get('c', 0)) * self.price_multiplier,
                        'volume': bar.get('v')
                    }
                    corrected_bars.append(corrected_bar)
                
                print(f"   Dernière barre corrigée:")
                last_bar = corrected_bars[-1]
                print(f"   O={last_bar['open']:.2f}, H={last_bar['high']:.2f}, L={last_bar['low']:.2f}, C={last_bar['close']:.2f}, V={last_bar['volume']}")
                
                return corrected_bars
            else:
                print("❌ Pas de données historiques")
                return None
                
        except Exception as e:
            print(f"❌ Erreur données historiques: {e}")
            return None
    
    def save_data(self, data, filename="es_data_corrected.json"):
        """Sauvegarder les données corrigées"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Données corrigées sauvegardées: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def disconnect(self):
        """Déconnexion"""
        self.connector.disconnect()

def main():
    """Fonction principale"""
    
    print("🚀 Récupération prix ES corrigé")
    print("Correction: 231.19 → 6482 (x28)")
    print("=" * 50)
    
    retriever = ESPriceRetrieverFixed()
    
    try:
        # 1. Connexion et authentification
        if not retriever.connect_and_authenticate():
            return
        
        # 2. Trouver conid ES
        if not retriever.find_correct_es_conid():
            return
        
        # 3. Récupérer prix actuel
        current_data = retriever.get_current_price()
        
        if current_data:
            print(f"\n🎉 PRIX ES CORRIGÉ: {current_data['price']:.2f}")
            
            # 4. Récupérer données historiques
            historical_data = retriever.get_historical_data()
            
            # 5. Préparer données complètes
            complete_data = {
                'current_price': current_data,
                'historical_data': historical_data,
                'correction_info': {
                    'multiplier_used': retriever.price_multiplier,
                    'explanation': 'Client Portal Gateway BETA retourne prix divisés par 28',
                    'original_price': current_data['price'] / retriever.price_multiplier,
                    'corrected_price': current_data['price']
                },
                'conid_used': retriever.es_conid
            }
            
            # 6. Sauvegarder
            retriever.save_data(complete_data)
            
            print(f"\n💡 Résumé:")
            print(f"   Conid ES: {retriever.es_conid}")
            print(f"   Prix corrigé: {current_data['price']:.2f}")
            print(f"   Multiplicateur: x{retriever.price_multiplier}")
            print(f"   Prix brut: {current_data['price'] / retriever.price_multiplier:.2f}")
            
        else:
            print("\n❌ Impossible de récupérer le prix ES")
    
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    finally:
        retriever.disconnect()

if __name__ == "__main__":
    main()

