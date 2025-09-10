#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ACTIVATION DONNÉES ES TWS - MIA_IA_SYSTEM
Guide pour activer les données ES dans TWS
"""

import time
from datetime import datetime

def creer_guide_activation_es():
    """Créer guide d'activation des données ES"""
    print("📊 Création guide activation données ES...")
    
    guide = """
# 🔧 GUIDE ACTIVATION DONNÉES ES DANS TWS
# Suivez ces étapes pour activer les données ES

## ÉTAPE 1: SOUSCRIRE AUX DONNÉES ES
1. Dans TWS, allez dans "Market Data" (en haut à gauche)
2. Tapez "ES" dans la barre de recherche
3. Sélectionnez "ES Sep19'25 @CME" (le contrat visible dans votre TWS)
4. Cliquez sur "Add to Market Data" ou le bouton "+"
5. Vérifiez que le prix 6468.50 s'affiche

## ÉTAPE 2: VÉRIFIER LA SOUSCRIPTION
1. Dans TWS, regardez la section "Market Data"
2. Vous devriez voir "ES Sep19'25 @CME" avec le prix en temps réel
3. Le prix doit être différent de "---" ou "N/A"

## ÉTAPE 3: CONFIGURATION API
1. File → Global Configuration → API → Settings
2. ✅ Enable ActiveX and Socket Clients: OUI
3. ✅ Socket port: 7497
4. ✅ Allow connections from localhost: OUI
5. ✅ Download open orders on connection: OUI
6. ✅ Include FX positions in portfolio: OUI

## ÉTAPE 4: REDÉMARRER TWS
1. Fermez TWS complètement
2. Relancez TWS
3. Reconnectez-vous
4. Vérifiez que les données ES sont toujours visibles

## ÉTAPE 5: TESTER L'API
1. Lancez le script de test
2. Le prix ES devrait maintenant être récupéré

# IMPORTANT: Les données ES doivent être visibles dans TWS AVANT que l'API puisse les récupérer !
"""
    
    with open('guide_activation_es_tws.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Guide activation ES sauvegardé")
    return True

def test_prix_es_apres_activation():
    """Test prix ES après activation"""
    print("🔗 Test prix ES après activation...")
    
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
                
                # Test ES Sep19'25 (contrat visible dans votre TWS)
                try:
                    print("\n📋 Test ES Sep19'25 @CME...")
                    
                    contract = Future('ES', '20250919', 'CME')
                    ib.reqMktData(contract)
                    
                    # Attendre plus longtemps pour les données
                    print("⏳ Attente données ES (10 secondes)...")
                    time.sleep(10)
                    
                    tickers = ib.tickers()
                    if tickers:
                        for ticker in tickers:
                            if ticker.contract.symbol == 'ES':
                                prix = ticker.marketPrice()
                                bid = ticker.bid
                                ask = ticker.ask
                                volume = ticker.volume
                                
                                print(f"   💰 Prix ES: {prix}")
                                print(f"   📊 Bid/Ask: {bid}/{ask}")
                                print(f"   📈 Volume: {volume}")
                                
                                if prix and prix > 0 and prix != float('nan'):
                                    print("   🎉 SUCCÈS ! Prix ES récupéré !")
                                    print(f"   📈 Prix actuel: {prix}")
                                    
                                    ib.disconnect()
                                    return True, {
                                        'symbol': 'ES',
                                        'date': '20250919',
                                        'exchange': 'CME',
                                        'price': prix,
                                        'bid': bid,
                                        'ask': ask,
                                        'volume': volume
                                    }
                                else:
                                    print("   ❌ Prix ES toujours invalide")
                                    print("   💡 Vérifiez que ES est souscrit dans TWS")
                    
                    print("   ⚠️ Aucune donnée ES reçue")
                    ib.disconnect()
                    return False, None
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur test ES: {e}")
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

def main():
    print("📊 ACTIVATION DONNÉES ES TWS - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Activation des données ES dans TWS")
    print("=" * 60)
    
    # Étape 1: Créer guide
    creer_guide_activation_es()
    
    print("\n📋 GUIDE D'ACTIVATION CRÉÉ")
    print("1. Ouvrez 'guide_activation_es_tws.txt'")
    print("2. Suivez les étapes pour activer ES dans TWS")
    print("3. Vérifiez que le prix 6468.50 s'affiche dans TWS")
    print("4. Relancez ce script pour tester")
    
    # Étape 2: Test après activation
    print("\n🔗 Test prix ES après activation...")
    success, data = test_prix_es_apres_activation()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ ACTIVATION ES")
    
    if success and data:
        print("🎉 SUCCÈS ! Prix ES récupéré:")
        print(f"   - Contrat: {data['symbol']} {data['date']} @{data['exchange']}")
        print(f"   - Prix: {data['price']}")
        print(f"   - Bid/Ask: {data['bid']}/{data['ask']}")
        print(f"   - Volume: {data['volume']}")
        
        print("\n🚀 MIA_IA_SYSTEM PRÊT POUR PRODUCTION !")
        
        # Sauvegarder configuration
        with open('config_es_actif.py', 'w', encoding='utf-8') as f:
            f.write(f"""# Configuration ES Actif - MIA_IA_SYSTEM
ES_ACTIVE_CONFIG = {{
    'symbol': '{data['symbol']}',
    'date': '{data['date']}',
    'exchange': '{data['exchange']}',
    'price': {data['price']},
    'bid': {data['bid']},
    'ask': {data['ask']},
    'volume': {data['volume']},
    'status': 'ACTIVE'
}}

# Statut: ✅ Données ES activées et récupérées
# Source: TWS Paper Trading
""")
        print("✅ Configuration ES sauvegardée dans 'config_es_actif.py'")
        
    else:
        print("❌ Prix ES toujours non disponible")
        print("\n🔧 ACTIONS REQUISES:")
        print("1. Ouvrez TWS")
        print("2. Allez dans 'Market Data'")
        print("3. Tapez 'ES' et ajoutez 'ES Sep19'25 @CME'")
        print("4. Vérifiez que le prix 6468.50 s'affiche")
        print("5. Relancez ce script")
        
        print("\n📖 Consultez 'guide_activation_es_tws.txt' pour les détails")

if __name__ == "__main__":
    main()

