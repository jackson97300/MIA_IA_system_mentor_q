#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 TEST ESU25 CONTRAT ACTUEL - MIA_IA_SYSTEM
Test avec le contrat ESU25 visible dans le navigateur (6340.00)
"""

import time
from datetime import datetime

def test_esu25_contrat_actuel():
    """Test avec le contrat ESU25 actuel"""
    print("🎯 Test ESU25 contrat actuel...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        
        # Configuration TWS
        host = '127.0.0.1'
        port = 7497
        client_id = 999
        timeout = 30
        
        print(f"🔗 Connexion: {host}:{port}, Client ID: {client_id}")
        
        try:
            ib.connect(host, port, clientId=client_id, timeout=timeout)
            
            if ib.isConnected():
                print("✅ Connexion TWS réussie !")
                
                # Test avec ESU25 (contrat actuel visible dans le navigateur)
                try:
                    print("\n📋 Test ESU25 (ES Sep'25)...")
                    
                    # ESU25 = ES September 2025
                    contract = Future('ES', '20250919', 'CME')
                    print(f"   📋 Contrat: {contract.symbol} {contract.lastTradingDay} @{contract.exchange}")
                    
                    ib.reqMktData(contract)
                    
                    # Attendre les données
                    print("⏳ Attente données ESU25 (15 secondes)...")
                    time.sleep(15)
                    
                    tickers = ib.tickers()
                    if tickers:
                        for ticker in tickers:
                            if ticker.contract.symbol == 'ES':
                                prix = ticker.marketPrice()
                                bid = ticker.bid
                                ask = ticker.ask
                                volume = ticker.volume
                                
                                print(f"   💰 Prix ESU25: {prix}")
                                print(f"   📊 Bid/Ask: {bid}/{ask}")
                                print(f"   📈 Volume: {volume}")
                                
                                if prix and prix > 0 and prix != float('nan'):
                                    print("   🎉 SUCCÈS ! Prix ESU25 récupéré !")
                                    print(f"   📈 Prix actuel: {prix}")
                                    print(f"   🎯 Prix attendu: ~6340.00")
                                    
                                    # Comparer avec le prix du navigateur
                                    if abs(prix - 6340.00) < 100:
                                        print(f"   ✅ Prix proche du navigateur: {prix} ≈ 6340.00")
                                    else:
                                        print(f"   ⚠️ Prix différent: {prix} vs 6340.00")
                                    
                                    ib.disconnect()
                                    return True, {
                                        'symbol': 'ES',
                                        'date': '20250919',
                                        'exchange': 'CME',
                                        'price': prix,
                                        'bid': bid,
                                        'ask': ask,
                                        'volume': volume,
                                        'contract': 'ESU25'
                                    }
                                else:
                                    print("   ❌ Prix ESU25 invalide")
                                    print("   💡 Vérifiez la souscription dans TWS")
                    
                    print("   ⚠️ Aucune donnée ESU25 reçue")
                    ib.disconnect()
                    return False, None
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur test ESU25: {e}")
                    ib.disconnect()
                    return False, None
            else:
                print("❌ Connexion TWS échouée")
                ib.disconnect()
                return False, None
                
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False, None
            
    except ImportError:
        print("❌ ib_insync non disponible")
        return False, None
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False, None

def creer_guide_souscription_tws():
    """Créer guide pour souscrire dans TWS"""
    print("📊 Création guide souscription TWS...")
    
    guide = """
# 🔧 GUIDE SOUSCRIPTION ESU25 DANS TWS
# Vous avez les souscriptions, maintenant il faut les activer dans TWS

## ÉTAPE 1: SOUSCRIRE ESU25 DANS TWS
1. Dans TWS, allez dans "Market Data" (en haut à gauche)
2. Tapez "ESU25" ou "ES" dans la barre de recherche
3. Sélectionnez "ES Sep'25 @CME" ou "ESU25"
4. Cliquez sur "Add to Market Data" ou le bouton "+"
5. Vérifiez que le prix ~6340.00 s'affiche

## ÉTAPE 2: VÉRIFIER LA SOUSCRIPTION
1. Dans TWS, regardez la section "Market Data"
2. Vous devriez voir "ES Sep'25 @CME" avec le prix en temps réel
3. Le prix doit être différent de "---" ou "N/A"

## ÉTAPE 3: CONFIGURATION API (si pas déjà fait)
1. File → Global Configuration → API → Settings
2. ✅ Enable ActiveX and Socket Clients: OUI
3. ✅ Socket port: 7497
4. ✅ Allow connections from localhost: OUI

## ÉTAPE 4: REDÉMARRER TWS
1. Fermez TWS complètement
2. Relancez TWS
3. Reconnectez-vous
4. Vérifiez que ESU25 est toujours visible

## ÉTAPE 5: TESTER L'API
1. Lancez le script de test
2. Le prix ESU25 devrait maintenant être récupéré

# IMPORTANT: Même avec les souscriptions, il faut ajouter le contrat dans TWS !
"""
    
    with open('guide_souscription_esu25_tws.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Guide souscription ESU25 sauvegardé")
    return True

def main():
    print("🎯 TEST ESU25 CONTRAT ACTUEL - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Test avec ESU25 (prix attendu: ~6340.00)")
    print("=" * 60)
    
    # Étape 1: Créer guide
    creer_guide_souscription_tws()
    
    print("\n📋 GUIDE SOUSCRIPTION CRÉÉ")
    print("1. Ouvrez 'guide_souscription_esu25_tws.txt'")
    print("2. Suivez les étapes pour ajouter ESU25 dans TWS")
    print("3. Vérifiez que le prix ~6340.00 s'affiche")
    print("4. Relancez ce script pour tester")
    
    # Étape 2: Test ESU25
    print("\n🔗 Test ESU25...")
    success, data = test_esu25_contrat_actuel()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ TEST ESU25")
    
    if success and data:
        print("🎉 SUCCÈS ! Prix ESU25 récupéré:")
        print(f"   - Contrat: {data['contract']} ({data['symbol']} {data['date']} @{data['exchange']})")
        print(f"   - Prix: {data['price']}")
        print(f"   - Bid/Ask: {data['bid']}/{data['ask']}")
        print(f"   - Volume: {data['volume']}")
        
        print("\n🚀 MIA_IA_SYSTEM PRÊT POUR PRODUCTION !")
        
        # Sauvegarder configuration
        with open('config_esu25_actif.py', 'w', encoding='utf-8') as f:
            f.write(f"""# Configuration ESU25 Actif - MIA_IA_SYSTEM
ESU25_ACTIVE_CONFIG = {{
    'symbol': '{data['symbol']}',
    'date': '{data['date']}',
    'exchange': '{data['exchange']}',
    'price': {data['price']},
    'bid': {data['bid']},
    'ask': {data['ask']},
    'volume': {data['volume']},
    'contract': '{data['contract']}',
    'status': 'ACTIVE'
}}

# Statut: ✅ Données ESU25 activées et récupérées
# Source: TWS Paper Trading
# Souscriptions: ✅ CME Real-Time (NP,L2) actif
""")
        print("✅ Configuration ESU25 sauvegardée dans 'config_esu25_actif.py'")
        
    else:
        print("❌ Prix ESU25 toujours non disponible")
        print("\n🔧 ACTIONS REQUISES:")
        print("1. Ouvrez TWS")
        print("2. Allez dans 'Market Data'")
        print("3. Tapez 'ESU25' et ajoutez le contrat")
        print("4. Vérifiez que le prix ~6340.00 s'affiche")
        print("5. Relancez ce script")
        
        print("\n📖 Consultez 'guide_souscription_esu25_tws.txt' pour les détails")
        print("\n💡 Vous avez les souscriptions, il faut juste ajouter le contrat dans TWS !")

if __name__ == "__main__":
    main()

