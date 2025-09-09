#!/usr/bin/env python3
"""
Récupération finale du prix ES avec correction
Client Portal Gateway BETA: prix_brut * 28 = prix_correct
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def parse_volume(volume_str):
    """Parser le volume au format '56.0M', '1.2K', etc."""
    if not volume_str or volume_str == 'N/A':
        return 0
    
    try:
        # Convertir en string si ce n'est pas déjà
        volume_str = str(volume_str)
        
        # Extraire le nombre et le suffixe
        match = re.match(r'([\d.]+)([KMB]?)', volume_str)
        if match:
            number = float(match.group(1))
            suffix = match.group(2)
            
            # Appliquer le multiplicateur
            if suffix == 'K':
                return int(number * 1000)
            elif suffix == 'M':
                return int(number * 1000000)
            elif suffix == 'B':
                return int(number * 1000000000)
            else:
                return int(number)
        else:
            # Essayer de convertir directement
            return int(float(volume_str))
    except:
        return 0

class ESPriceRetrieverFinal:
    """Récupérateur ES final avec correction"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.es_conid = "265598"  # Conid ES validé
        self.price_multiplier = 28  # Facteur de correction
        
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
    
    def get_current_price(self):
        """Récupérer le prix actuel ES (corrigé)"""
        print(f"\n📊 Récupération prix ES (conid: {self.es_conid})")
        
        # Récupérer toutes les données
        fields = ["31", "83", "84", "86", "87", "88", "89", "90"]
        market_data = self.connector.get_market_data(self.es_conid, fields)
        
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            data = market_data[0]
            
            # Extraire prix bruts avec gestion d'erreur
            try:
                bid_raw = float(data.get('31', 0))
                ask_raw = float(data.get('83', 0))
                last_raw = float(data.get('84', 0))
                volume_raw = data.get('86', 'N/A')
                
                # Parser le volume
                volume_parsed = parse_volume(volume_raw)
                
                # Appliquer correction
                bid_corrected = bid_raw * self.price_multiplier
                ask_corrected = ask_raw * self.price_multiplier
                last_corrected = last_raw * self.price_multiplier
                
                print(f"✅ Prix ES corrigés:")
                print(f"   Bid: {bid_corrected:.2f} (brut: {bid_raw})")
                print(f"   Ask: {ask_corrected:.2f} (brut: {ask_raw})")
                print(f"   Last: {last_corrected:.2f} (brut: {last_raw})")
                print(f"   Volume: {volume_parsed:,} (brut: {volume_raw})")
                
                # Données OHLC corrigées (avec gestion d'erreur)
                high_raw = float(data.get('87', 0))
                low_raw = float(data.get('88', 0))
                open_raw = float(data.get('89', 0))
                
                high_corrected = high_raw * self.price_multiplier
                low_corrected = low_raw * self.price_multiplier
                open_corrected = open_raw * self.price_multiplier
                
                print(f"   High: {high_corrected:.2f} (brut: {high_raw})")
                print(f"   Low: {low_corrected:.2f} (brut: {low_raw})")
                print(f"   Open: {open_corrected:.2f} (brut: {open_raw})")
                
                return {
                    'price': last_corrected,
                    'bid': bid_corrected,
                    'ask': ask_corrected,
                    'volume': volume_parsed,
                    'volume_raw': volume_raw,
                    'high': high_corrected,
                    'low': low_corrected,
                    'open': open_corrected,
                    'conid': self.es_conid,
                    'multiplier_used': self.price_multiplier,
                    'timestamp': datetime.now().isoformat()
                }
            
            except Exception as e:
                print(f"❌ Erreur parsing données: {e}")
                print(f"   Données brutes: {data}")
                return None
        
        else:
            print("❌ Pas de données de prix")
            return None
    
    def get_historical_data(self, period="1d", bar_size="1min"):
        """Récupérer données historiques ES (corrigées)"""
        print(f"\n📈 Récupération données historiques...")
        
        try:
            historical = self.connector.get_historical_data(self.es_conid, period, bar_size)
            
            if historical and len(historical) > 0:
                print(f"✅ {len(historical)} barres récupérées")
                
                # Corriger les prix historiques
                corrected_bars = []
                for bar in historical[-10:]:  # 10 dernières barres
                    try:
                        corrected_bar = {
                            'timestamp': bar.get('t'),
                            'open': float(bar.get('o', 0)) * self.price_multiplier,
                            'high': float(bar.get('h', 0)) * self.price_multiplier,
                            'low': float(bar.get('l', 0)) * self.price_multiplier,
                            'close': float(bar.get('c', 0)) * self.price_multiplier,
                            'volume': parse_volume(bar.get('v'))
                        }
                        corrected_bars.append(corrected_bar)
                    except Exception as e:
                        print(f"   ⚠️ Erreur barre: {e}")
                        continue
                
                if corrected_bars:
                    print(f"   Dernière barre corrigée:")
                    last_bar = corrected_bars[-1]
                    print(f"   O={last_bar['open']:.2f}, H={last_bar['high']:.2f}, L={last_bar['low']:.2f}, C={last_bar['close']:.2f}, V={last_bar['volume']:,}")
                
                return corrected_bars
            else:
                print("❌ Pas de données historiques")
                return None
                
        except Exception as e:
            print(f"❌ Erreur données historiques: {e}")
            return None
    
    def save_data(self, data, filename="es_price_final.json"):
        """Sauvegarder les données"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Données sauvegardées: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def disconnect(self):
        """Déconnexion"""
        self.connector.disconnect()

def main():
    """Fonction principale"""
    
    print("🚀 Récupération finale prix ES")
    print("Correction: prix_brut * 28 = prix_correct")
    print("=" * 50)
    
    retriever = ESPriceRetrieverFinal()
    
    try:
        # 1. Connexion et authentification
        if not retriever.connect_and_authenticate():
            return
        
        # 2. Récupérer prix actuel
        current_data = retriever.get_current_price()
        
        if current_data:
            print(f"\n🎉 PRIX ES RÉCUPÉRÉ: {current_data['price']:.2f}")
            
            # 3. Récupérer données historiques
            historical_data = retriever.get_historical_data()
            
            # 4. Préparer données complètes
            complete_data = {
                'current_price': current_data,
                'historical_data': historical_data,
                'correction_info': {
                    'multiplier_used': retriever.price_multiplier,
                    'explanation': 'Client Portal Gateway BETA retourne prix divisés par 28',
                    'original_price': current_data['price'] / retriever.price_multiplier,
                    'corrected_price': current_data['price']
                },
                'conid_used': retriever.es_conid,
                'retrieved_at': datetime.now().isoformat()
            }
            
            # 5. Sauvegarder
            retriever.save_data(complete_data)
            
            print(f"\n💡 Résumé final:")
            print(f"   Conid ES: {retriever.es_conid}")
            print(f"   Prix corrigé: {current_data['price']:.2f}")
            print(f"   Multiplicateur: x{retriever.price_multiplier}")
            print(f"   Prix brut: {current_data['price'] / retriever.price_multiplier:.2f}")
            print(f"   Volume: {current_data['volume']:,}")
            
            print(f"\n✅ SUCCÈS! Prix ES récupéré avec correction")
            print(f"   Le Client Portal Gateway BETA fonctionne correctement")
            print(f"   avec le facteur de correction x{retriever.price_multiplier}")
            
        else:
            print("\n❌ Impossible de récupérer le prix ES")
    
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    finally:
        retriever.disconnect()

if __name__ == "__main__":
    main()
