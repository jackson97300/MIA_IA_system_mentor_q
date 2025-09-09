#!/usr/bin/env python3
"""
Test d'intégration Sierra Chart DTC avec MIA_IA_SYSTEM
======================================================

Teste le nouveau connecteur Sierra Chart et son intégration avec MIA
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.sierra_dtc_connector import SierraDTCConnector, SierraConnectorInterface
from core.base_types import MarketData

logger = get_logger(__name__)

def test_sierra_connection():
    """Test de connexion Sierra Chart DTC"""
    print("🔍 TEST CONNEXION SIERRA CHART DTC")
    print("="*50)
    
    # Créer le connecteur
    connector = SierraDTCConnector()
    
    try:
        # Test de connexion
        print("🔌 Test de connexion...")
        if connector.connect():
            print("✅ Connexion Sierra Chart réussie")
            
            # Test souscription market data
            print("📊 Test souscription market data...")
            if connector.subscribe_market_data("ES"):
                print("✅ Souscription ES réussie")
            else:
                print("❌ Souscription ES échouée")
            
            if connector.subscribe_market_data("NQ"):
                print("✅ Souscription NQ réussie")
            else:
                print("❌ Souscription NQ échouée")
            
            # Attendre quelques secondes pour recevoir des données
            print("⏳ Attente données de marché (5s)...")
            import time
            time.sleep(5)
            
            # Vérifier les données reçues
            es_data = connector.get_market_data("ES")
            nq_data = connector.get_market_data("NQ")
            
            if es_data:
                print(f"📊 Données ES reçues: {es_data}")
            else:
                print("❌ Aucune donnée ES reçue")
            
            if nq_data:
                print(f"📊 Données NQ reçues: {nq_data}")
            else:
                print("❌ Aucune donnée NQ reçue")
            
            # Déconnexion
            print("🔌 Déconnexion...")
            connector.disconnect()
            print("✅ Déconnexion réussie")
            
        else:
            print("❌ Connexion Sierra Chart échouée")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")

def test_mia_interface():
    """Test de l'interface compatible MIA"""
    print("\n🔍 TEST INTERFACE MIA")
    print("="*50)
    
    # Créer l'interface MIA
    interface = SierraConnectorInterface()
    
    try:
        # Test de connexion asynchrone
        print("🔌 Test connexion asynchrone...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(interface.connect())
        if result:
            print("✅ Connexion interface MIA réussie")
            
            # Test récupération données au format MIA
            print("📊 Test récupération données MIA...")
            es_market_data = interface.get_market_data("ES")
            nq_market_data = interface.get_market_data("NQ")
            
            if es_market_data:
                print(f"📊 MarketData ES: {es_market_data}")
            else:
                print("❌ Aucune MarketData ES")
            
            if nq_market_data:
                print(f"📊 MarketData NQ: {nq_market_data}")
            else:
                print("❌ Aucune MarketData NQ")
            
            # Test statut connexion
            status = interface.get_connection_status()
            print(f"📡 Statut connexion: {status}")
            
            # Déconnexion
            print("🔌 Déconnexion interface...")
            loop.run_until_complete(interface.disconnect())
            print("✅ Déconnexion interface réussie")
            
        else:
            print("❌ Connexion interface MIA échouée")
            
        loop.close()
        
    except Exception as e:
        print(f"❌ Erreur test interface: {e}")

def test_callback_system():
    """Test du système de callbacks"""
    print("\n🔍 TEST SYSTÈME CALLBACKS")
    print("="*50)
    
    # Variables pour stocker les données reçues
    received_ticks = []
    
    def on_market_data(tick):
        """Callback pour les données de marché"""
        received_ticks.append(tick)
        print(f"📊 Tick reçu: {tick.symbol} - {tick.tick_type} - {tick.price}")
    
    # Créer le connecteur avec callback
    connector = SierraDTCConnector()
    connector.set_market_data_callback(on_market_data)
    
    try:
        # Connexion
        print("🔌 Connexion avec callbacks...")
        if connector.connect():
            print("✅ Connexion réussie")
            
            # Souscription
            connector.subscribe_market_data("ES")
            connector.subscribe_market_data("NQ")
            
            # Attendre des données
            print("⏳ Attente données avec callbacks (10s)...")
            import time
            time.sleep(10)
            
            print(f"📊 Nombre de ticks reçus: {len(received_ticks)}")
            
            # Déconnexion
            connector.disconnect()
            print("✅ Test callbacks terminé")
            
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur test callbacks: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 TEST INTÉGRATION SIERRA CHART MIA")
    print("="*60)
    print(f"⏰ Début: {datetime.now()}")
    print()
    
    # Test 1: Connexion de base
    test_sierra_connection()
    
    # Test 2: Interface MIA
    test_mia_interface()
    
    # Test 3: Système de callbacks
    test_callback_system()
    
    print("\n" + "="*60)
    print("✅ TESTS TERMINÉS")
    print(f"⏰ Fin: {datetime.now()}")

if __name__ == "__main__":
    main()

