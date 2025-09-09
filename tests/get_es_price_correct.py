#!/usr/bin/env python3
"""
Récupérer le vrai prix ES (~6482) avec ib-insync
"""

import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    from ib_insync import *
    print("✅ ib-insync installé")
except ImportError:
    print("❌ ib-insync non installé")
    print("💡 Installez avec: pip install ib-insync")
    sys.exit(1)

class ESPriceRetriever:
    """Récupérateur de prix ES avec ib-insync"""
    
    def __init__(self):
        self.ib = IB()
        self.es_contract = None
        self.current_price = None
        
    async def connect(self):
        """Connexion à TWS/Gateway"""
        try:
            print("🔌 Connexion à TWS/Gateway...")
            await self.ib.connectAsync('127.0.0.1', 7497, clientId=1)
            
            if not self.ib.isConnected():
                print("❌ Connexion échouée")
                return False
            
            print("✅ Connecté à TWS/Gateway")
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    async def find_es_contract(self):
        """Trouver le contrat ES actif"""
        print("\n🔍 Recherche contrat ES...")
        
        # Essayer différents contrats ES
        es_contracts = [
            Future('ES', '202509', 'CME'),  # Sept 2025
            Future('ES', '202512', 'CME'),  # Dec 2025
            Future('ES', '202503', 'CME'),  # March 2025
            Future('ES', '202506', 'CME'),  # June 2025
        ]
        
        for contract in es_contracts:
            try:
                print(f"   Test: {contract}")
                
                # Qualifier le contrat
                await self.ib.qualifyContractsAsync(contract)
                print(f"   ✅ Qualifié: {contract.localSymbol}")
                
                # Test market data
                ticker = self.ib.reqMktData(contract, '', False, False)
                await asyncio.sleep(2)
                
                if ticker.last != -1 and 6000 <= ticker.last <= 7000:
                    print(f"   🎯 CONTRAT ES TROUVÉ!")
                    print(f"      Prix: {ticker.last}")
                    print(f"      Symbol: {contract.localSymbol}")
                    print(f"      ConId: {contract.conId}")
                    
                    self.es_contract = contract
                    return True
                    
                elif ticker.bid != -1 and 6000 <= ticker.bid <= 7000:
                    print(f"   🎯 CONTRAT ES TROUVÉ (bid)!")
                    print(f"      Prix: {ticker.bid}")
                    print(f"      Symbol: {contract.localSymbol}")
                    print(f"      ConId: {contract.conId}")
                    
                    self.es_contract = contract
                    return True
                
                # Annuler subscription
                self.ib.cancelMktData(contract)
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        print("❌ Aucun contrat ES valide trouvé")
        return False
    
    async def get_current_price(self):
        """Récupérer le prix actuel ES"""
        if not self.es_contract:
            print("❌ Contrat ES non trouvé")
            return None
        
        try:
            print(f"\n📊 Récupération prix ES: {self.es_contract.localSymbol}")
            
            # Subscription market data
            ticker = self.ib.reqMktData(self.es_contract, '', False, False)
            
            # Attendre données
            await asyncio.sleep(3)
            
            if ticker.last != -1:
                self.current_price = ticker.last
                print(f"✅ Prix ES actuel: {self.current_price}")
                
                # Afficher toutes les données
                print(f"   Bid: {ticker.bid}")
                print(f"   Ask: {ticker.ask}")
                print(f"   Volume: {ticker.volume}")
                print(f"   High: {ticker.high}")
                print(f"   Low: {ticker.low}")
                print(f"   Open: {ticker.open}")
                
                return {
                    'price': self.current_price,
                    'bid': ticker.bid,
                    'ask': ticker.ask,
                    'volume': ticker.volume,
                    'high': ticker.high,
                    'low': ticker.low,
                    'open': ticker.open,
                    'timestamp': datetime.now().isoformat(),
                    'symbol': self.es_contract.localSymbol,
                    'conid': self.es_contract.conId
                }
            
            elif ticker.bid != -1:
                self.current_price = ticker.bid
                print(f"✅ Prix ES (bid): {self.current_price}")
                return {
                    'price': self.current_price,
                    'bid': ticker.bid,
                    'ask': ticker.ask,
                    'timestamp': datetime.now().isoformat(),
                    'symbol': self.es_contract.localSymbol,
                    'conid': self.es_contract.conId
                }
            
            else:
                print("❌ Pas de données de prix")
                return None
                
        except Exception as e:
            print(f"❌ Erreur récupération prix: {e}")
            return None
    
    async def get_historical_data(self, period="1d", bar_size="1min"):
        """Récupérer données historiques ES"""
        if not self.es_contract:
            print("❌ Contrat ES non trouvé")
            return None
        
        try:
            print(f"\n📈 Récupération données historiques...")
            
            bars = self.ib.reqHistoricalData(
                self.es_contract,
                endDateTime='',
                durationStr=period,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            
            if bars:
                print(f"✅ {len(bars)} barres récupérées")
                
                # Convertir en format simple
                historical_data = []
                for bar in bars[-10:]:  # 10 dernières barres
                    historical_data.append({
                        'timestamp': bar.date.isoformat(),
                        'open': bar.open,
                        'high': bar.high,
                        'low': bar.low,
                        'close': bar.close,
                        'volume': bar.volume
                    })
                
                return historical_data
            else:
                print("❌ Pas de données historiques")
                return None
                
        except Exception as e:
            print(f"❌ Erreur données historiques: {e}")
            return None
    
    def save_data(self, data, filename="es_data.json"):
        """Sauvegarder les données"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Données sauvegardées: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def disconnect(self):
        """Déconnexion"""
        if self.ib.isConnected():
            self.ib.disconnect()
            print("🔌 Déconnecté")

async def main():
    """Fonction principale"""
    
    print("🚀 Récupération prix ES correct")
    print("Prix attendu: ~6482")
    print("=" * 50)
    
    retriever = ESPriceRetriever()
    
    try:
        # 1. Connexion
        if not await retriever.connect():
            return
        
        # 2. Trouver contrat ES
        if not await retriever.find_es_contract():
            return
        
        # 3. Récupérer prix actuel
        current_data = await retriever.get_current_price()
        
        if current_data:
            print(f"\n🎉 PRIX ES RÉCUPÉRÉ: {current_data['price']}")
            
            # 4. Récupérer données historiques
            historical_data = await retriever.get_historical_data()
            
            # 5. Préparer données complètes
            complete_data = {
                'current_price': current_data,
                'historical_data': historical_data,
                'contract_info': {
                    'symbol': retriever.es_contract.localSymbol,
                    'conid': retriever.es_contract.conId,
                    'exchange': retriever.es_contract.exchange,
                    'currency': retriever.es_contract.currency
                },
                'retrieved_at': datetime.now().isoformat()
            }
            
            # 6. Sauvegarder
            retriever.save_data(complete_data)
            
            print(f"\n💡 Utilisez ce contrat:")
            print(f"   Symbol: {retriever.es_contract.localSymbol}")
            print(f"   ConId: {retriever.es_contract.conId}")
            print(f"   Prix: {current_data['price']}")
            
        else:
            print("\n❌ Impossible de récupérer le prix ES")
    
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    finally:
        retriever.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

