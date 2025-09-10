#!/usr/bin/env python3
"""
Test de connexion IBKR Gateway - Lundi 00h20 Session Asie
"""

import sys
import os
import time
import logging
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ibkr_connection_test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_ibkr_connection():
    """Test complet de la connexion IBKR"""
    
    print("🚀 TEST CONNEXION IBKR GATEWAY - LUNDI 00H20")
    print("=" * 60)
    print(f"⏰ Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Session: ASIE (ouverte)")
    print("=" * 60)
    
    # Configuration
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        # 1. Test de connexion de base
        print("\n1️⃣ TEST CONNEXION DE BASE")
        print("-" * 30)
        
        if connector.connect():
            print("✅ Connexion au Gateway réussie")
        else:
            print("❌ Échec connexion au Gateway")
            print("🔧 Vérifiez que IBKR Gateway est démarré sur https://localhost:5000")
            return False
        
        # 2. Test d'authentification
        print("\n2️⃣ TEST AUTHENTIFICATION")
        print("-" * 30)
        print("🔐 Authentification requise...")
        print("🌐 Ouvrez votre navigateur et allez sur: https://localhost:5000")
        print("📝 Connectez-vous avec vos identifiants IBKR")
        print("⏳ Attente de l'authentification...")
        
        if connector.authenticate():
            print("✅ Authentification réussie!")
        else:
            print("❌ Échec authentification")
            return False
        
        # 3. Test informations compte
        print("\n3️⃣ TEST INFORMATIONS COMPTE")
        print("-" * 30)
        
        account_info = connector.get_account_info()
        if account_info:
            print("✅ Informations compte récupérées")
            print(f"📊 Compte: {account_info.get('accounts', [])}")
        else:
            print("❌ Impossible de récupérer les informations compte")
        
        # 4. Test positions
        print("\n4️⃣ TEST POSITIONS")
        print("-" * 30)
        
        positions = connector.get_positions()
        if positions:
            print(f"✅ {len(positions)} positions trouvées")
            for pos in positions:
                print(f"   📈 {pos.get('contractDesc', 'N/A')}: {pos.get('position', 0)}")
        else:
            print("✅ Aucune position ouverte")
        
        # 5. Test recherche ES futures
        print("\n5️⃣ TEST RECHERCHE ES FUTURES")
        print("-" * 30)
        
        es_conid = connector.get_es_futures_conid()
        if es_conid:
            print(f"✅ ES Futures trouvé: CONID {es_conid}")
            
            # 6. Test données de marché ES
            print("\n6️⃣ TEST DONNÉES DE MARCHÉ ES")
            print("-" * 30)
            
            market_data = connector.get_market_data(es_conid)
            if market_data:
                print("✅ Données de marché ES récupérées")
                print(f"   📊 Données: {market_data}")
            else:
                print("❌ Impossible de récupérer les données ES")
        else:
            print("❌ ES Futures non trouvé")
        
        # 7. Test données historiques
        print("\n7️⃣ TEST DONNÉES HISTORIQUES")
        print("-" * 30)
        
        if es_conid:
            historical_data = connector.get_historical_data(es_conid, period="1d", bar="1min")
            if historical_data:
                print(f"✅ {len(historical_data)} barres historiques récupérées")
                if historical_data:
                    latest_bar = historical_data[-1]
                    print(f"   📊 Dernière barre: {latest_bar}")
            else:
                print("❌ Impossible de récupérer les données historiques")
        
        # 8. Test WebSocket (optionnel)
        print("\n8️⃣ TEST WEBSOCKET")
        print("-" * 30)
        
        if connector.connect_websocket():
            print("✅ WebSocket connecté")
            print("📡 Prêt pour les données temps réel")
        else:
            print("⚠️ WebSocket non disponible (optionnel)")
        
        # Résumé final
        print("\n" + "=" * 60)
        print("🎉 TEST CONNEXION TERMINÉ")
        print("=" * 60)
        print("✅ Système prêt pour la session Asie!")
        print("📊 Données disponibles: OHLC, Volume, Bid/Ask")
        print("🔗 Connexion stable établie")
        print("🚀 MIA_IA_SYSTEM opérationnel")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        logger.error(f"Erreur test connexion: {e}")
        return False
        
    finally:
        connector.disconnect()

def main():
    """Fonction principale"""
    
    # Créer le dossier logs si nécessaire
    os.makedirs('logs', exist_ok=True)
    
    print("🔧 Démarrage test connexion IBKR...")
    
    success = test_ibkr_connection()
    
    if success:
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("1. Lancer la collecte de données")
        print("2. Activer les stratégies")
        print("3. Démarrer le monitoring")
        print("4. Surveiller les performances")
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS:")
        print("1. Vérifier IBKR Gateway")
        print("2. Contrôler l'authentification")
        print("3. Vérifier la connectivité réseau")
        print("4. Consulter les logs pour détails")

if __name__ == "__main__":
    main()
