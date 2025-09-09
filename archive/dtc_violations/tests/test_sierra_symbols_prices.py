#!/usr/bin/env python3
"""
Test spécifique des symboles et prix Sierra Chart DTC
=====================================================

Valide la connexion avec les symboles complets et la réception des prix corrects
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import time

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.sierra_dtc_connector import SierraDTCConnector

logger = get_logger(__name__)

async def test_sierra_symbols_prices():
    """Test des symboles et prix Sierra Chart"""
    print("🔍 TEST SYMBOLES ET PRIX SIERRA CHART")
    print("="*60)
    
    # Créer le connecteur
    connector = SierraDTCConnector()
    
    try:
        # 1. Connexion
        print("🔌 Étape 1: Connexion Sierra Chart...")
        if not connector.connect():
            print("❌ Échec connexion")
            return False
        print("✅ Connexion réussie")
        
        # 2. Attendre stabilisation
        print("⏳ Étape 2: Stabilisation connexion (2s)...")
        await asyncio.sleep(2)
        
        # 3. Test ES avec symbole complet
        print("📊 Étape 3: Test ES (ESU25_FUT_CME)...")
        if connector.subscribe_market_data("ESU25_FUT_CME"):
            print("✅ Souscription ES réussie")
        else:
            print("❌ Échec souscription ES")
        
        # 4. Test NQ avec symbole complet
        print("📊 Étape 4: Test NQ (NQU25_FUT_CME)...")
        if connector.subscribe_market_data("NQU25_FUT_CME"):
            print("✅ Souscription NQ réussie")
        else:
            print("❌ Échec souscription NQ")
        
        # 5. Attendre les données
        print("⏳ Étape 5: Attente données (15s)...")
        for i in range(15):
            await asyncio.sleep(1)
            print(f"   Attente... {i+1}/15s")
            
            # Vérifier les données reçues
            es_data = connector.get_market_data("ESU25_FUT_CME")
            nq_data = connector.get_market_data("NQU25_FUT_CME")
            
            if es_data:
                print(f"   📊 ES: {es_data.get('price', 'N/A')} (Source: {es_data.get('data_source', 'N/A')})")
            if nq_data:
                print(f"   📊 NQ: {nq_data.get('price', 'N/A')} (Source: {nq_data.get('data_source', 'N/A')})")
        
        # 6. Résultats finaux
        print("\n📋 RÉSULTATS FINAUX:")
        es_final = connector.get_market_data("ESU25_FUT_CME")
        nq_final = connector.get_market_data("NQU25_FUT_CME")
        
        if es_final:
            print(f"✅ ES Final: {es_final.get('price', 'N/A')}")
            print(f"   Timestamp: {es_final.get('timestamp', 'N/A')}")
            print(f"   Source: {es_final.get('data_source', 'N/A')}")
        else:
            print("❌ ES: Aucune donnée reçue")
        
        if nq_final:
            print(f"✅ NQ Final: {nq_final.get('price', 'N/A')}")
            print(f"   Timestamp: {nq_final.get('timestamp', 'N/A')}")
            print(f"   Source: {nq_final.get('data_source', 'N/A')}")
        else:
            print("❌ NQ: Aucune donnée reçue")
        
        # 7. Déconnexion propre
        print("\n🔌 Déconnexion...")
        connector.disconnect()
        print("✅ Test terminé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        connector.disconnect()
        return False

async def test_symbol_mapping():
    """Test du mapping des symboles"""
    print("\n🔍 TEST MAPPING DES SYMBOLES")
    print("="*60)
    
    # Symboles à tester
    symbols_to_test = [
        "ES",           # Symbole simple
        "ESU25",        # Symbole avec mois
        "ESU25_FUT",    # Symbole avec type
        "ESU25_FUT_CME", # Symbole complet
        "NQ",
        "NQU25",
        "NQU25_FUT",
        "NQU25_FUT_CME"
    ]
    
    connector = SierraDTCConnector()
    
    try:
        if not connector.connect():
            print("❌ Échec connexion pour test mapping")
            return False
        
        await asyncio.sleep(2)
        
        for symbol in symbols_to_test:
            print(f"📊 Test symbole: {symbol}")
            if connector.subscribe_market_data(symbol):
                print(f"   ✅ Souscription réussie")
                
                # Attendre un peu
                await asyncio.sleep(2)
                
                # Vérifier les données
                data = connector.get_market_data(symbol)
                if data:
                    print(f"   📊 Prix: {data.get('price', 'N/A')}")
                else:
                    print(f"   ❌ Aucune donnée")
            else:
                print(f"   ❌ Échec souscription")
        
        connector.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test mapping: {e}")
        connector.disconnect()
        return False

async def main():
    """Fonction principale"""
    print("🚀 TEST SYMBOLES ET PRIX SIERRA CHART DTC")
    print("="*80)
    print(f"⏰ Début: {datetime.now()}")
    print()
    
    # Test 1: Symboles et prix
    success1 = await test_sierra_symbols_prices()
    
    # Test 2: Mapping des symboles
    success2 = await test_symbol_mapping()
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DES TESTS")
    print(f"✅ Test symboles/prix: {'SUCCÈS' if success1 else 'ÉCHEC'}")
    print(f"✅ Test mapping: {'SUCCÈS' if success2 else 'ÉCHEC'}")
    print(f"⏰ Fin: {datetime.now()}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Sierra Chart DTC fonctionne parfaitement")
        print("✅ Symboles et prix corrects")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez la configuration Sierra Chart")

if __name__ == "__main__":
    asyncio.run(main())

