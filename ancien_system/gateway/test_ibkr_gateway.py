#!/usr/bin/env python3
"""
Test de connexion au Client Portal Gateway IBKR BETA
"""

import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_gateway_connection():
    """Tester la connexion au gateway IBKR"""
    
    print("🔌 Test de connexion au Client Portal Gateway IBKR BETA")
    print("=" * 60)
    
    # Configuration
    config = IBKRBetaConfig()
    print(f"📍 URL de base: {config.base_url}")
    print(f"🔐 WebSocket URL: {config.ws_url}")
    
    # Créer le connecteur
    connector = IBKRBetaConnector(config)
    
    try:
        # 1. Test de connexion
        print("\n1️⃣ Test de connexion au gateway...")
        if connector.connect():
            print("✅ Gateway accessible")
        else:
            print("❌ Gateway non accessible")
            print("💡 Vérifiez que le gateway est démarré sur https://localhost:5000/")
            return False
        
        # 2. Test d'authentification
        print("\n2️⃣ Test d'authentification...")
        print("🌐 Ouvrez votre navigateur et allez sur: https://localhost:5000/")
        print("📝 Connectez-vous avec vos identifiants IBKR")
        
        if connector.authenticate():
            print("✅ Authentification réussie!")
        else:
            print("❌ Authentification échouée")
            return False
        
        # 3. Test récupération compte
        print("\n3️⃣ Test récupération informations compte...")
        account_info = connector.get_account_info()
        if account_info:
            print("✅ Informations compte récupérées")
            print(f"   Compte: {account_info.get('accounts', [])}")
        else:
            print("❌ Impossible de récupérer les informations compte")
        
        # 4. Test recherche ES futures
        print("\n4️⃣ Test recherche ES futures...")
        es_conid = connector.get_es_futures_conid()
        if es_conid:
            print(f"✅ ES futures trouvé: {es_conid}")
        else:
            print("❌ ES futures non trouvé")
        
        # 5. Test données de marché
        if es_conid:
            print("\n5️⃣ Test données de marché ES...")
            market_data = connector.get_market_data(es_conid)
            if market_data:
                print("✅ Données de marché récupérées")
                print(f"   Données: {market_data}")
            else:
                print("❌ Impossible de récupérer les données de marché")
        
        print("\n🎉 Tests terminés avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False
        
    finally:
        connector.disconnect()

if __name__ == "__main__":
    success = test_gateway_connection()
    if not success:
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez que le gateway est démarré")
        print("   2. Vérifiez que le port 5000 est libre")
        print("   3. Vérifiez vos identifiants IBKR")
        print("   4. Vérifiez la configuration SSL")
        sys.exit(1)

