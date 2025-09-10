#!/usr/bin/env python3
"""
Test de l'API BETA IBKR - Client Portal Gateway
"""

import sys
import os
import time
import logging
from datetime import datetime

# Ajouter le dossier core au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig, get_es_futures_conid, get_spx_options_conid

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_connexion_gateway():
    """Test de connexion au gateway"""
    print("🔌 TEST DE CONNEXION AU GATEWAY...")
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        # Test de connexion
        if connector.connect():
            print("✅ Gateway accessible")
            return connector
        else:
            print("❌ Gateway non accessible")
            print("💡 Assurez-vous que le gateway est démarré:")
            print("   cd clientportal.beta.gw")
            print("   bin\\run.bat root\\conf.yaml")
            return None
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_authentification(connector: IBKRBetaConnector):
    """Test d'authentification"""
    print("\n🔐 TEST D'AUTHENTIFICATION...")
    
    try:
        if connector.authenticate():
            print("✅ Authentification réussie")
            return True
        else:
            print("❌ Authentification échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        return False

def test_account_info(connector: IBKRBetaConnector):
    """Test récupération informations compte"""
    print("\n💼 TEST INFORMATIONS COMPTE...")
    
    try:
        account_info = connector.get_account_info()
        if account_info:
            print("✅ Informations compte récupérées:")
            print(f"   📊 Compte: {account_info}")
            return True
        else:
            print("❌ Impossible de récupérer les informations compte")
            return False
            
    except Exception as e:
        print(f"❌ Erreur account_info: {e}")
        return False

def test_positions(connector: IBKRBetaConnector):
    """Test récupération positions"""
    print("\n📋 TEST POSITIONS...")
    
    try:
        positions = connector.get_positions()
        print(f"✅ Positions récupérées: {len(positions)} positions")
        for pos in positions:
            print(f"   📊 {pos}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur positions: {e}")
        return False

def test_search_contracts(connector: IBKRBetaConnector):
    """Test recherche de contrats"""
    print("\n🔍 TEST RECHERCHE CONTRATS...")
    
    try:
        # Test ES futures
        print("🔍 Recherche ES futures...")
        es_contracts = connector.search_contract("ES", "FUT")
        if es_contracts:
            print(f"✅ ES futures trouvés: {len(es_contracts)} contrats")
            for contract in es_contracts[:3]:  # Afficher les 3 premiers
                print(f"   📊 {contract}")
        else:
            print("❌ Aucun contrat ES trouvé")
        
        # Test SPX options
        print("\n🔍 Recherche SPX options...")
        spx_contracts = connector.search_contract("SPX", "OPT")
        if spx_contracts:
            print(f"✅ SPX options trouvés: {len(spx_contracts)} contrats")
            for contract in spx_contracts[:3]:  # Afficher les 3 premiers
                print(f"   📊 {contract}")
        else:
            print("❌ Aucun contrat SPX trouvé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur recherche contrats: {e}")
        return False

def test_market_data(connector: IBKRBetaConnector):
    """Test données de marché"""
    print("\n📈 TEST DONNÉES DE MARCHÉ...")
    
    try:
        # Obtenir le conid ES
        es_conid = get_es_futures_conid(connector)
        if not es_conid:
            print("❌ Impossible d'obtenir le conid ES")
            return False
        
        print(f"🔍 Conid ES: {es_conid}")
        
        # Récupérer les données de marché
        market_data = connector.get_market_data(es_conid)
        if market_data:
            print("✅ Données de marché ES récupérées:")
            print(f"   📊 {market_data}")
            return True
        else:
            print("❌ Impossible de récupérer les données de marché")
            return False
            
    except Exception as e:
        print(f"❌ Erreur market_data: {e}")
        return False

def test_historical_data(connector: IBKRBetaConnector):
    """Test données historiques"""
    print("\n📊 TEST DONNÉES HISTORIQUES...")
    
    try:
        # Obtenir le conid ES
        es_conid = get_es_futures_conid(connector)
        if not es_conid:
            print("❌ Impossible d'obtenir le conid ES")
            return False
        
        # Récupérer les données historiques
        historical_data = connector.get_historical_data(es_conid, period="1d", bar="1min")
        if historical_data:
            print(f"✅ Données historiques ES récupérées: {len(historical_data)} barres")
            if historical_data:
                print(f"   📊 Dernière barre: {historical_data[-1]}")
            return True
        else:
            print("❌ Impossible de récupérer les données historiques")
            return False
            
    except Exception as e:
        print(f"❌ Erreur historical_data: {e}")
        return False

def test_orders(connector: IBKRBetaConnector):
    """Test gestion des ordres"""
    print("\n📋 TEST GESTION ORDRES...")
    
    try:
        # Récupérer les ordres existants
        orders = connector.get_orders()
        print(f"✅ Ordres récupérés: {len(orders)} ordres")
        for order in orders:
            print(f"   📊 {order}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur orders: {e}")
        return False

def test_websocket(connector: IBKRBetaConnector):
    """Test WebSocket pour données temps réel"""
    print("\n🔌 TEST WEBSOCKET...")
    
    try:
        # Se connecter au WebSocket
        if connector.connect_websocket():
            print("✅ WebSocket connecté")
            
            # Attendre un peu pour la connexion
            time.sleep(2)
            
            # Obtenir le conid ES
            es_conid = get_es_futures_conid(connector)
            if es_conid:
                # S'abonner aux données de marché
                def market_data_callback(data):
                    print(f"📈 Données temps réel ES: {data}")
                
                if connector.subscribe_market_data(es_conid, callback=market_data_callback):
                    print("✅ Abonnement aux données ES activé")
                    print("⏳ Attente des données temps réel (10 secondes)...")
                    time.sleep(10)
                else:
                    print("❌ Échec de l'abonnement aux données")
            
            return True
        else:
            print("❌ Impossible de se connecter au WebSocket")
            return False
            
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        return False

def main():
    """Fonction principale de test"""
    
    print("🚀 TEST COMPLET DE L'API BETA IBKR")
    print("="*50)
    
    # Test de connexion
    connector = test_connexion_gateway()
    if not connector:
        print("\n❌ Impossible de se connecter au gateway")
        print("💡 Vérifiez que le gateway est démarré")
        return
    
    # Test d'authentification
    if not test_authentification(connector):
        print("\n❌ Authentification échouée")
        return
    
    # Tests des fonctionnalités
    tests = [
        ("Informations compte", test_account_info),
        ("Positions", test_positions),
        ("Recherche contrats", test_search_contracts),
        ("Données de marché", test_market_data),
        ("Données historiques", test_historical_data),
        ("Gestion ordres", test_orders),
        ("WebSocket", test_websocket)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(connector)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans le test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des tests
    print("\n" + "="*50)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("🎯 L'API BETA IBKR est prête pour MIA_IA!")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez la configuration et les permissions")
    
    # Déconnexion
    connector.disconnect()
    print("\n🔌 Déconnexion terminée")

if __name__ == "__main__":
    main()














