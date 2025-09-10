#!/usr/bin/env python3
"""
Intégration IBKR Gateway avec le système MIA_IA
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(str(Path(__file__).parent.parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig
import logging

def setup_ibkr_integration():
    """Configurer l'intégration IBKR"""
    print("=== INTÉGRATION IBKR GATEWAY ===")
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Créer la configuration IBKR
    config = IBKRBetaConfig()
    print(f"Configuration IBKR:")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  Base URL: {config.base_url}")
    print()
    
    # Créer le connecteur
    connector = IBKRBetaConnector(config)
    
    # Tester la connexion
    print("🔍 Test de connexion au Gateway...")
    if connector.connect():
        print("✅ Connexion au Gateway réussie")
        
        # Tester l'authentification
        print("🔍 Vérification de l'authentification...")
        if connector.authenticate():
            print("✅ Authentification réussie")
            
            # Test des fonctionnalités de base
            print("🔍 Test des fonctionnalités...")
            
            # Test des comptes
            try:
                accounts = connector.get_accounts()
                print(f"✅ Comptes récupérés: {len(accounts) if accounts else 0}")
            except Exception as e:
                print(f"⚠️ Erreur récupération comptes: {e}")
            
            # Test des positions
            try:
                positions = connector.get_positions()
                print(f"✅ Positions récupérées: {len(positions) if positions else 0}")
            except Exception as e:
                print(f"⚠️ Erreur récupération positions: {e}")
            
            # Test des données de marché
            try:
                # Test avec un symbole populaire
                market_data = connector.get_market_data("AAPL")
                print(f"✅ Données de marché récupérées pour AAPL")
            except Exception as e:
                print(f"⚠️ Erreur récupération données marché: {e}")
            
        else:
            print("❌ Authentification échouée")
            print("💡 Assurez-vous d'être connecté sur https://localhost:5000")
    else:
        print("❌ Connexion au Gateway échouée")
        print("💡 Vérifiez que le Gateway IBKR est démarré")
    
    return connector

def main():
    """Fonction principale"""
    try:
        connector = setup_ibkr_integration()
        
        print("\n🎉 Intégration IBKR configurée !")
        print("Vous pouvez maintenant utiliser le connecteur IBKR dans votre système MIA_IA")
        
        # Exemple d'utilisation
        print("\n📋 Exemple d'utilisation:")
        print("""
        # Dans votre code MIA_IA:
        from core.ibkr_beta_connector import IBKRBetaConnector
        
        # Créer le connecteur
        connector = IBKRBetaConnector()
        
        # Se connecter
        if connector.connect() and connector.authenticate():
            # Récupérer les comptes
            accounts = connector.get_accounts()
            
            # Récupérer les positions
            positions = connector.get_positions()
            
            # Récupérer les données de marché
            market_data = connector.get_market_data("ES")
        """)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'intégration: {e}")
        logging.exception("Erreur détaillée:")

if __name__ == "__main__":
    main()













