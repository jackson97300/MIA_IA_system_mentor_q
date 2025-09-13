#!/usr/bin/env python3
"""
Script ultra-simple pour prix ES
Prix direct sans calculs complexes - optimisé pour bot de trading
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def clean_price(price_str):
    """Nettoyer prix - fonction ultra-simple"""
    if not price_str or price_str == 'N/A':
        return 0.0
    try:
        price_str = str(price_str).strip()
        price_str = re.sub(r'^[C$€£¥]\s*', '', price_str)
        return float(price_str)
    except:
        return 0.0

class ESSimplePrice:
    """Prix ES ultra-simple pour bot"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.price_factor = 28  # Facteur fixe pour ES
        
    def get_es_price(self):
        """Récupérer prix ES simple"""
        
        try:
            # Connexion
            if not self.connector.connect() or not self.connector.authenticate():
                return None
            
            # Récupérer données
            conid = "265598"
            fields = ["31", "84"]  # Bid et Last seulement
            market_data = self.connector.get_market_data(conid, fields)
            
            if market_data and len(market_data) > 0:
                data = market_data[0]
                
                # Prix brut
                bid_raw = clean_price(data.get('31', 0))
                last_raw = clean_price(data.get('84', 0))
                
                # Prix corrigé (simple multiplication)
                bid_corrected = bid_raw * self.price_factor
                last_corrected = last_raw * self.price_factor
                
                # Prix final (priorité au last, sinon bid)
                final_price = last_corrected if last_corrected > 0 else bid_corrected
                
                return {
                    'price': final_price,
                    'bid': bid_corrected,
                    'last': last_corrected,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"Erreur: {e}")
            return None
        finally:
            self.connector.disconnect()
    
    def save_price(self, price_data, filename="es_simple_price.json"):
        """Sauvegarder prix simple"""
        if price_data:
            try:
                with open(filename, 'w') as f:
                    json.dump(price_data, f, indent=2)
                print(f"Prix sauvegardé: {filename}")
            except:
                pass

def main():
    """Fonction principale - ultra-simple"""
    
    print("🚀 Prix ES ultra-simple")
    print("=" * 30)
    
    es = ESSimplePrice()
    price_data = es.get_es_price()
    
    if price_data:
        print(f"✅ Prix ES: {price_data['price']:.2f}")
        print(f"   Bid: {price_data['bid']:.2f}")
        print(f"   Last: {price_data['last']:.2f}")
        
        # Sauvegarder
        es.save_price(price_data)
        
        print(f"\n💡 Utilisation bot:")
        print(f"   prix_es = {price_data['price']:.2f}")
        print(f"   # Utiliser directement dans vos calculs")
        
    else:
        print("❌ Erreur récupération prix")

if __name__ == "__main__":
    main()

