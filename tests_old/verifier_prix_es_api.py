#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 VÉRIFICATION PRIX ES DEPUIS API - MIA_IA_SYSTEM
Récupération du prix ES en temps réel via API TWS
"""

import time
from datetime import datetime

def verifier_prix_es_api():
    """Vérifier le prix ES depuis l'API TWS"""
    print("💰 Vérification prix ES depuis API TWS...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        
        # Configuration TWS qui fonctionne
        host = '127.0.0.1'
        port = 7497
        client_id = 999
        timeout = 30
        
        print(f"🔗 Connexion API: {host}:{port}, Client ID: {client_id}")
        
        try:
            ib.connect(host, port, clientId=client_id, timeout=timeout)
            
            if ib.isConnected():
                print("✅ Connexion API TWS réussie !")
                
                # Test avec différents contrats ES
                contrats_es = [
                    ('ES', '20250919', 'CME'),  # ES Sep19'25
                    ('ES', '20241220', 'CME'),  # ES Dec20'24
                    ('ES', '20250321', 'CME'),  # ES Mar21'25
                ]
                
                for symbol, date, exchange in contrats_es:
                    try:
                        print(f"\n📋 Test contrat: {symbol} {date} @{exchange}")
                        
                        contract = Future(symbol, date, exchange)
                        ib.reqMktData(contract)
                        time.sleep(2)
                        
                        tickers = ib.tickers()
                        if tickers:
                            for ticker in tickers:
                                if ticker.contract.symbol == symbol:
                                    prix = ticker.marketPrice()
                                    bid = ticker.bid
                                    ask = ticker.ask
                                    volume = ticker.volume
                                    
                                    print(f"   💰 Prix: {prix}")
                                    print(f"   📊 Bid/Ask: {bid}/{ask}")
                                    print(f"   📈 Volume: {volume}")
                                    
                                    if prix and prix > 0:
                                        print(f"   ✅ Prix ES valide: {prix}")
                                        
                                        # Comparer avec le prix attendu (6468.50)
                                        if abs(prix - 6468.50) < 50:
                                            print(f"   🎯 Prix proche de l'attendu: {prix} ≈ 6468.50")
                                        else:
                                            print(f"   ⚠️ Prix différent de l'attendu: {prix} vs 6468.50")
                                        
                                        return True, {
                                            'symbol': symbol,
                                            'date': date,
                                            'exchange': exchange,
                                            'price': prix,
                                            'bid': bid,
                                            'ask': ask,
                                            'volume': volume
                                        }
                                    else:
                                        print(f"   ❌ Prix invalide: {prix}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Erreur contrat {symbol} {date}: {e}")
                
                print("\n⚠️ Aucun prix ES valide trouvé")
                ib.disconnect()
                return False, None
                
            else:
                print("❌ Connexion API TWS échouée")
                ib.disconnect()
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur connexion API: {e}")
            return False, None
            
    except ImportError:
        print("❌ ib_insync non disponible")
        return False, None
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False, None

def test_prix_continu():
    """Test prix ES en continu"""
    print("🔄 Test prix ES en continu...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        
        # Connexion
        ib.connect('127.0.0.1', 7497, clientId=999, timeout=30)
        
        if ib.isConnected():
            print("✅ Connexion établie pour surveillance continue")
            
            # Contrat ES Sep19'25
            contract = Future('ES', '20250919', 'CME')
            ib.reqMktData(contract)
            
            print("📊 Surveillance prix ES en temps réel...")
            print("   (Appuyez sur Ctrl+C pour arrêter)")
            
            try:
                for i in range(10):  # 10 lectures
                    time.sleep(2)
                    
                    tickers = ib.tickers()
                    if tickers:
                        for ticker in tickers:
                            if ticker.contract.symbol == 'ES':
                                prix = ticker.marketPrice()
                                bid = ticker.bid
                                ask = ticker.ask
                                
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                print(f"   [{timestamp}] ES: {prix} | Bid: {bid} | Ask: {ask}")
                                
                                if prix and prix > 0:
                                    print(f"   ✅ Prix ES valide: {prix}")
                                else:
                                    print(f"   ❌ Prix ES invalide: {prix}")
                    
            except KeyboardInterrupt:
                print("\n⏹️ Surveillance arrêtée par l'utilisateur")
            
            ib.disconnect()
            return True
            
        else:
            print("❌ Impossible de se connecter pour la surveillance")
            return False
            
    except Exception as e:
        print(f"❌ Erreur surveillance: {e}")
        return False

def main():
    print("💰 VÉRIFICATION PRIX ES DEPUIS API - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Récupération prix ES en temps réel")
    print("=" * 60)
    
    # Test 1: Vérification prix unique
    print("\n🔍 Test 1: Vérification prix unique...")
    success, data = verifier_prix_es_api()
    
    if success and data:
        print(f"\n🎉 SUCCÈS ! Prix ES récupéré:")
        print(f"   - Contrat: {data['symbol']} {data['date']} @{data['exchange']}")
        print(f"   - Prix: {data['price']}")
        print(f"   - Bid/Ask: {data['bid']}/{data['ask']}")
        print(f"   - Volume: {data['volume']}")
        
        # Sauvegarder données
        with open('prix_es_api.txt', 'w', encoding='utf-8') as f:
            f.write(f"""# Prix ES depuis API TWS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
PRIX_ES_API = {{
    'symbol': '{data['symbol']}',
    'date': '{data['date']}',
    'exchange': '{data['exchange']}',
    'price': {data['price']},
    'bid': {data['bid']},
    'ask': {data['ask']},
    'volume': {data['volume']},
    'timestamp': '{datetime.now().isoformat()}'
}}

# Statut: ✅ Prix ES récupéré avec succès
# Source: API TWS Paper Trading
""")
        print("✅ Données prix sauvegardées dans 'prix_es_api.txt'")
        
        # Test 2: Surveillance continue
        print(f"\n🔄 Test 2: Surveillance continue (10 lectures)...")
        test_prix_continu()
        
    else:
        print("❌ Impossible de récupérer le prix ES")
        print("\n🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS est en cours d'exécution")
        print("2. Vérifiez que l'API est activée dans TWS")
        print("3. Vérifiez que vous avez souscrit aux données ES")
        print("4. Redémarrez TWS si nécessaire")

if __name__ == "__main__":
    main()

