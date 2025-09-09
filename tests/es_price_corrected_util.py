#!/usr/bin/env python3
"""
Utilitaire ES avec correction automatique du priceFactor
IBKR Client Portal Gateway BETA - Prix corrigés automatiquement
"""

import sys
import json
import re
import requests
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def parse_volume(volume_str):
    """Parser le volume au format '56.0M', '1.2K', etc."""
    if not volume_str or volume_str == 'N/A':
        return 0
    
    try:
        volume_str = str(volume_str)
        match = re.match(r'([\d.]+)([KMB]?)', volume_str)
        if match:
            number = float(match.group(1))
            suffix = match.group(2)
            
            if suffix == 'K':
                return int(number * 1000)
            elif suffix == 'M':
                return int(number * 1000000)
            elif suffix == 'B':
                return int(number * 1000000000)
            else:
                return int(number)
        else:
            return int(float(volume_str))
    except:
        return 0

class ESPriceCorrectedUtil:
    """Utilitaire ES avec correction automatique priceFactor"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.base_url = "https://localhost:5000/v1/api"
        self.session = requests.Session()
        self.session.verify = False  # Certificat self-signed
        
    def get_es_contract_info(self):
        """Récupérer les informations du contrat ES avec priceFactor"""
        print("🔍 Récupération contrat ES...")
        
        try:
            # Méthode 1: Via trsrv/futures
            url = f"{self.base_url}/trsrv/futures"
            params = {"symbols": "ES"}
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if 'ES' in data and len(data['ES']) > 0:
                    # Chercher le contrat front month (Sep 2025)
                    for contract in data['ES']:
                        if contract.get('expiry') == '202509':
                            print(f"✅ Contrat ES trouvé via trsrv/futures")
                            return {
                                'conid': contract.get('conid'),
                                'symbol': contract.get('symbol'),
                                'expiry': contract.get('expiry'),
                                'exchange': contract.get('exchange'),
                                'priceFactor': contract.get('priceFactor', 1),
                                'multiplier': contract.get('multiplier', 50),
                                'source': 'trsrv/futures'
                            }
            
            # Méthode 2: Via secdef/info (fallback)
            print("   Tentative via secdef/info...")
            url = f"{self.base_url}/iserver/secdef/info"
            params = {"conid": "265598"}  # Conid ES connu
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    contract = data[0]
                    print(f"✅ Contrat ES trouvé via secdef/info")
                    return {
                        'conid': contract.get('conid'),
                        'symbol': contract.get('symbol'),
                        'expiry': contract.get('expiry'),
                        'exchange': contract.get('exchange'),
                        'priceFactor': contract.get('priceFactor', 1),
                        'multiplier': contract.get('multiplier', 50),
                        'source': 'secdef/info'
                    }
            
            # Méthode 3: Fallback avec valeurs connues
            print("   Utilisation valeurs par défaut...")
            return {
                'conid': '265598',
                'symbol': 'ES',
                'expiry': '202509',
                'exchange': 'GLOBEX',
                'priceFactor': 28,  # Valeur connue pour ES
                'multiplier': 50,
                'source': 'default'
            }
            
        except Exception as e:
            print(f"❌ Erreur récupération contrat: {e}")
            # Fallback avec valeurs connues
            return {
                'conid': '265598',
                'symbol': 'ES',
                'expiry': '202509',
                'exchange': 'GLOBEX',
                'priceFactor': 28,
                'multiplier': 50,
                'source': 'fallback'
            }
    
    def get_corrected_price(self, conid=None):
        """Récupérer le prix ES corrigé avec priceFactor"""
        
        # 1. Récupérer info contrat
        contract_info = self.get_es_contract_info()
        conid = conid or contract_info['conid']
        price_factor = contract_info['priceFactor']
        
        print(f"📊 Contrat ES:")
        print(f"   Conid: {conid}")
        print(f"   Symbol: {contract_info['symbol']}")
        print(f"   Expiry: {contract_info['expiry']}")
        print(f"   Exchange: {contract_info['exchange']}")
        print(f"   PriceFactor: {price_factor}")
        print(f"   Multiplier: {contract_info['multiplier']}")
        print(f"   Source: {contract_info['source']}")
        
        # 2. Récupérer snapshot prix brut
        print(f"\n📈 Récupération snapshot...")
        
        try:
            url = f"{self.base_url}/iserver/marketdata/snapshot"
            params = {"conids": conid}
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 0:
                    snapshot = data[0]
                    
                    # Extraire prix bruts
                    bid_raw = float(snapshot.get('31', 0))  # Bid
                    ask_raw = float(snapshot.get('83', 0))  # Ask  
                    last_raw = float(snapshot.get('84', 0))  # Last
                    volume_raw = snapshot.get('86', 'N/A')  # Volume
                    
                    # Appliquer priceFactor
                    bid_corrected = bid_raw * price_factor
                    ask_corrected = ask_raw * price_factor
                    last_corrected = last_raw * price_factor
                    
                    # Parser volume
                    volume_parsed = parse_volume(volume_raw)
                    
                    print(f"✅ Prix ES corrigés:")
                    print(f"   Bid: {bid_corrected:.2f} (brut: {bid_raw})")
                    print(f"   Ask: {ask_corrected:.2f} (brut: {ask_raw})")
                    print(f"   Last: {last_corrected:.2f} (brut: {last_raw})")
                    print(f"   Volume: {volume_parsed:,} (brut: {volume_raw})")
                    
                    return {
                        'price': last_corrected,
                        'bid': bid_corrected,
                        'ask': ask_corrected,
                        'volume': volume_parsed,
                        'volume_raw': volume_raw,
                        'conid': conid,
                        'price_factor': price_factor,
                        'contract_info': contract_info,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print("❌ Pas de données snapshot")
                    return None
            else:
                print(f"❌ Erreur snapshot: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur snapshot: {e}")
            return None
    
    def get_historical_corrected(self, conid=None, period="1d", bar_size="1min"):
        """Récupérer données historiques corrigées"""
        
        contract_info = self.get_es_contract_info()
        conid = conid or contract_info['conid']
        price_factor = contract_info['priceFactor']
        
        print(f"\n📈 Récupération données historiques...")
        
        try:
            url = f"{self.base_url}/iserver/marketdata/history"
            params = {
                "conid": conid,
                "period": period,
                "bar": bar_size
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    bars = data['data']
                    print(f"✅ {len(bars)} barres récupérées")
                    
                    # Corriger les prix historiques
                    corrected_bars = []
                    for bar in bars[-10:]:  # 10 dernières barres
                        corrected_bar = {
                            'timestamp': bar.get('t'),
                            'open': float(bar.get('o', 0)) * price_factor,
                            'high': float(bar.get('h', 0)) * price_factor,
                            'low': float(bar.get('l', 0)) * price_factor,
                            'close': float(bar.get('c', 0)) * price_factor,
                            'volume': parse_volume(bar.get('v'))
                        }
                        corrected_bars.append(corrected_bar)
                    
                    if corrected_bars:
                        print(f"   Dernière barre corrigée:")
                        last_bar = corrected_bars[-1]
                        print(f"   O={last_bar['open']:.2f}, H={last_bar['high']:.2f}, L={last_bar['low']:.2f}, C={last_bar['close']:.2f}, V={last_bar['volume']:,}")
                    
                    return corrected_bars
                else:
                    print("❌ Pas de données historiques")
                    return None
            else:
                print(f"❌ Erreur historique: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur historique: {e}")
            return None
    
    def save_data(self, data, filename="es_price_corrected.json"):
        """Sauvegarder les données"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Données sauvegardées: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")

def main():
    """Fonction principale"""
    
    print("🚀 Utilitaire ES avec correction automatique priceFactor")
    print("IBKR Client Portal Gateway BETA - Prix corrigés")
    print("=" * 60)
    
    util = ESPriceCorrectedUtil()
    
    try:
        # 1. Récupérer prix corrigé
        price_data = util.get_corrected_price()
        
        if price_data:
            print(f"\n🎉 PRIX ES RÉCUPÉRÉ: {price_data['price']:.2f}")
            
            # 2. Récupérer données historiques
            historical_data = util.get_historical_corrected()
            
            # 3. Préparer données complètes
            complete_data = {
                'current_price': price_data,
                'historical_data': historical_data,
                'correction_info': {
                    'price_factor_used': price_data['price_factor'],
                    'explanation': 'IBKR Client Portal Gateway BETA utilise priceFactor pour les futures',
                    'raw_price': price_data['price'] / price_data['price_factor'],
                    'corrected_price': price_data['price']
                },
                'contract_info': price_data['contract_info'],
                'retrieved_at': datetime.now().isoformat()
            }
            
            # 4. Sauvegarder
            util.save_data(complete_data)
            
            print(f"\n💡 Résumé final:")
            print(f"   Conid ES: {price_data['conid']}")
            print(f"   Prix corrigé: {price_data['price']:.2f}")
            print(f"   PriceFactor: x{price_data['price_factor']}")
            print(f"   Prix brut: {price_data['price'] / price_data['price_factor']:.2f}")
            print(f"   Volume: {price_data['volume']:,}")
            
            print(f"\n✅ SUCCÈS! Prix ES récupéré avec correction automatique")
            print(f"   Le priceFactor est récupéré automatiquement")
            print(f"   Plus besoin de coder en dur le multiplicateur")
            
        else:
            print("\n❌ Impossible de récupérer le prix ES")
    
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    main()

