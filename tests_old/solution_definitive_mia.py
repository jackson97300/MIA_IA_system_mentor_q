#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SOLUTION DÉFINITIVE MIA_IA_SYSTEM
Solution complète pour récupérer les données ES
"""

import time
import subprocess
import os
from datetime import datetime

def creer_guide_solution_definitive():
    """Créer guide solution définitive"""
    print("📊 Création guide solution définitive...")
    
    guide = """
# 🚀 SOLUTION DÉFINITIVE MIA_IA_SYSTEM
# Suivez ces étapes EXACTEMENT dans l'ordre

## ÉTAPE 1: CONFIGURATION TWS (OBLIGATOIRE)
1. Ouvrez TWS
2. File → Global Configuration → API → Settings
3. ✅ Enable ActiveX and Socket Clients: OUI
4. ✅ Socket port: 7497
5. ✅ Allow connections from localhost: OUI
6. ✅ Download open orders on connection: OUI
7. ✅ Include FX positions in portfolio: OUI
8. Cliquez "OK" et redémarrez TWS

## ÉTAPE 2: SOUSCRIRE ESU25 DANS TWS (CRUCIAL)
1. Dans TWS, allez dans "Market Data" (en haut à gauche)
2. Tapez "ESU25" dans la barre de recherche
3. Sélectionnez "ES Sep'25 @CME"
4. Cliquez sur "Add to Market Data" ou le bouton "+"
5. Vérifiez que le prix ~6340.00 s'affiche (PAS "---" ou "N/A")

## ÉTAPE 3: VÉRIFIER LA SOUSCRIPTION
1. Dans TWS, regardez la section "Market Data"
2. Vous devriez voir "ES Sep'25 @CME" avec le prix en temps réel
3. Le prix doit être différent de "---" ou "N/A"

## ÉTAPE 4: TESTER L'API
1. Lancez le script de test
2. Le prix ESU25 devrait maintenant être récupéré

# IMPORTANT: 
# - Vous avez les souscriptions CME Real-Time (NP,L2)
# - Le problème est que TWS n'a pas ESU25 dans Market Data
# - L'API ne peut récupérer que ce qui est affiché dans TWS
"""
    
    with open('solution_definitive_mia.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Guide solution définitive sauvegardé")
    return True

def test_solution_definitive():
    """Test solution définitive"""
    print("🔗 Test solution définitive...")
    
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
                
                # Test avec ESU25
                try:
                    print("\n📋 Test ESU25 (ES Sep'25)...")
                    
                    contract = Future('ES', '20250919', 'CME')
                    print(f"   📋 Contrat: {contract.symbol} {contract.lastTradeDateOrContractMonth} @{contract.exchange}")
                    
                    ib.reqMktData(contract)
                    
                    # Attendre les données
                    print("⏳ Attente données ESU25 (20 secondes)...")
                    time.sleep(20)
                    
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
                                    print("   💡 ESU25 n'est pas dans Market Data de TWS")
                    
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

def creer_configuration_mia():
    """Créer configuration MIA_IA_SYSTEM"""
    print("📊 Création configuration MIA_IA_SYSTEM...")
    
    config = """# Configuration MIA_IA_SYSTEM - ES Futures
# Fichier de configuration pour le trading ES

# Configuration IBKR
IBKR_CONFIG = {
    'host': '127.0.0.1',
    'port': 7497,  # TWS Paper Trading
    'client_id': 999,
    'timeout': 30
}

# Configuration ES Futures
ES_CONFIG = {
    'symbol': 'ES',
    'date': '20250919',  # ESU25
    'exchange': 'CME',
    'contract': 'ESU25'
}

# Configuration Market Data
MARKET_DATA_CONFIG = {
    'enable_streaming': True,
    'auto_subscribe': True,
    'subscription': 'CME Real-Time (NP,L2)'
}

# Statut: En attente d'activation ESU25 dans TWS
# Action requise: Ajouter ESU25 dans Market Data de TWS
"""
    
    with open('config_mia_ia_system.py', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("✅ Configuration MIA_IA_SYSTEM sauvegardée")
    return True

def main():
    print("🚀 SOLUTION DÉFINITIVE MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Solution complète pour récupérer les données ES")
    print("=" * 60)
    
    # Étape 1: Créer guide solution
    creer_guide_solution_definitive()
    
    # Étape 2: Créer configuration MIA
    creer_configuration_mia()
    
    print("\n📋 SOLUTION CRÉÉE")
    print("1. Ouvrez 'solution_definitive_mia.txt'")
    print("2. Suivez les étapes EXACTEMENT dans l'ordre")
    print("3. Ajoutez ESU25 dans Market Data de TWS")
    print("4. Vérifiez que le prix ~6340.00 s'affiche")
    print("5. Relancez ce script pour tester")
    
    # Étape 3: Test solution
    print("\n🔗 Test solution définitive...")
    success, data = test_solution_definitive()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ SOLUTION DÉFINITIVE")
    
    if success and data:
        print("🎉 SUCCÈS ! MIA_IA_SYSTEM OPÉRATIONNEL !")
        print(f"   - Contrat: {data['contract']} ({data['symbol']} {data['date']} @{data['exchange']})")
        print(f"   - Prix: {data['price']}")
        print(f"   - Bid/Ask: {data['bid']}/{data['ask']}")
        print(f"   - Volume: {data['volume']}")
        
        print("\n🚀 MIA_IA_SYSTEM PRÊT POUR PRODUCTION !")
        
        # Sauvegarder configuration finale
        with open('config_mia_ia_system_final.py', 'w', encoding='utf-8') as f:
            f.write(f"""# Configuration MIA_IA_SYSTEM Finale - ES Futures
# Configuration opérationnelle

IBKR_CONFIG = {{
    'host': '127.0.0.1',
    'port': 7497,
    'client_id': 999,
    'timeout': 30,
    'status': 'ACTIVE'
}}

ES_CONFIG = {{
    'symbol': '{data['symbol']}',
    'date': '{data['date']}',
    'exchange': '{data['exchange']}',
    'contract': '{data['contract']}',
    'price': {data['price']},
    'bid': {data['bid']},
    'ask': {data['ask']},
    'volume': {data['volume']},
    'status': 'ACTIVE'
}}

# Statut: ✅ MIA_IA_SYSTEM OPÉRATIONNEL
# Source: TWS Paper Trading
# Souscriptions: ✅ CME Real-Time (NP,L2) actif
""")
        print("✅ Configuration finale sauvegardée dans 'config_mia_ia_system_final.py'")
        
    else:
        print("❌ Prix ESU25 toujours non disponible")
        print("\n🔧 ACTIONS REQUISES:")
        print("1. Ouvrez TWS")
        print("2. File → Global Configuration → API → Settings")
        print("3. Configurez les paramètres API")
        print("4. Allez dans Market Data")
        print("5. Tapez 'ESU25' et ajoutez le contrat")
        print("6. Vérifiez que le prix ~6340.00 s'affiche")
        print("7. Relancez ce script")
        
        print("\n📖 Consultez 'solution_definitive_mia.txt' pour les détails")
        print("\n💡 Le problème est que ESU25 n'est pas dans Market Data de TWS")

if __name__ == "__main__":
    main()

