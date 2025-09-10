#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST CONNECTEUR SIERRA CHART RÉEL
====================================
Test du vrai connecteur DTC binaire de notre codebase
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from core.sierra_connector import SierraConnector, DTCMessageBuilder, DTCMessageParser
    from core.logger import get_logger
    print("✅ Import SierraConnector réussi")
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    sys.exit(1)

logger = get_logger(__name__)

def test_sierra_connector():
    """Test du connecteur Sierra Chart réel"""
    print("🏆 TEST CONNECTEUR SIERRA CHART RÉEL")
    print("=" * 50)
    
    # Configuration Sierra Chart
    config = {
        'sierra_host': '127.0.0.1',
        'sierra_port': 11100,  # Port NQ
        'sierra_username': 'lazard973',
        'sierra_password': 'LEpretre-973',
        'sierra_client_name': 'MIA_IA_SYSTEM'
    }
    
    print(f"🔧 Configuration:")
    print(f"   Host: {config['sierra_host']}")
    print(f"   Port: {config['sierra_port']}")
    print(f"   Username: {config['sierra_username']}")
    print(f"   Client: {config['sierra_client_name']}")
    
    # Créer le connecteur
    print("\n🔌 Création connecteur Sierra Chart...")
    connector = SierraConnector(config)
    
    try:
        # Test connexion
        print("\n🔗 Test connexion...")
        if connector.connect():
            print("✅ Connexion TCP réussie")
            
            # Test authentification
            print("\n🔐 Test authentification...")
            if connector.is_authenticated:
                print("✅ Authentification réussie")
                
                # Test heartbeat
                print("\n💓 Test heartbeat...")
                connector._send_heartbeat()
                print("✅ Heartbeat envoyé")
                
                # Test market data
                print("\n📊 Test market data...")
                if connector.subscribe_market_data("ESU26-FUT-CME"):
                    print("✅ Souscription market data réussie")
                else:
                    print("❌ Souscription market data échouée")
                
            else:
                print("❌ Authentification échouée")
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        
    finally:
        # Nettoyage
        print("\n🧹 Nettoyage...")
        if hasattr(connector, 'disconnect'):
            connector.disconnect()
        print("✅ Nettoyage terminé")

def test_dtc_messages():
    """Test des messages DTC"""
    print("\n📋 TEST MESSAGES DTC")
    print("-" * 30)
    
    # Test LOGON_REQUEST
    print("📤 Test LOGON_REQUEST...")
    logon_msg = DTCMessageBuilder.build_logon_request(
        username="lazard973",
        password="LEpretre-973",
        client_name="MIA_IA_SYSTEM"
    )
    print(f"   Taille: {len(logon_msg)} bytes")
    print(f"   Hex: {logon_msg[:20].hex()}...")
    
    # Test HEARTBEAT
    print("\n📤 Test HEARTBEAT...")
    heartbeat_msg = DTCMessageBuilder.build_heartbeat()
    print(f"   Taille: {len(heartbeat_msg)} bytes")
    print(f"   Hex: {heartbeat_msg.hex()}")
    
    # Test MARKET_DATA_REQUEST
    print("\n📤 Test MARKET_DATA_REQUEST...")
    market_msg = DTCMessageBuilder.build_market_data_request("ESU26-FUT-CME")
    print(f"   Taille: {len(market_msg)} bytes")
    print(f"   Hex: {market_msg[:20].hex()}...")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE TEST SIERRA CHART RÉEL")
    print("=" * 50)
    
    # Test messages DTC
    test_dtc_messages()
    
    # Test connecteur
    test_sierra_connector()
    
    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    print("🎯 Test Sierra Chart terminé")
    print("📝 Consultez les résultats ci-dessus")

