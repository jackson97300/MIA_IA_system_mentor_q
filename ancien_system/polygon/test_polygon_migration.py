#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - TEST MIGRATION POLYGON.IO
Script de validation pour la migration IBKR → Polygon.io

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Août 2025
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Ajouter le répertoire features au path
sys.path.append('features')
sys.path.append('config')

def check_environment():
    """Vérifie l'environnement et les prérequis"""
    print("🔍 Vérification de l'environnement...")
    print("="*50)
    
    # Vérifier clé API
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("❌ POLYGON_API_KEY non définie")
        print("💡 Définir avec: export POLYGON_API_KEY='your_api_key'")
        return False
    else:
        print(f"✅ POLYGON_API_KEY définie: ***{api_key[-4:]}")
    
    # Vérifier dépendances
    try:
        import polygon
        print(f"✅ polygon-api-client installé: {polygon.__version__}")
    except ImportError:
        print("❌ polygon-api-client manquant")
        print("💡 Installer avec: pip install polygon-api-client")
        return False
    
    try:
        import aiohttp
        print(f"✅ aiohttp disponible")
    except ImportError:
        print("❌ aiohttp manquant")
        print("💡 Installer avec: pip install aiohttp")
        return False
    
    # Vérifier fichiers créés
    files_to_check = [
        "features/polygon_connector.py",
        "features/create_polygon_snapshot.py",
        "config/polygon_config.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} existe")
        else:
            print(f"❌ {file_path} manquant")
            return False
    
    print("="*50)
    return True

async def test_polygon_connector():
    """Test du connecteur Polygon.io"""
    print("\n🔗 Test du connecteur Polygon.io...")
    print("="*50)
    
    try:
        from polygon_connector import create_polygon_connector
        
        # Créer le connecteur
        connector = create_polygon_connector()
        print("✅ Connecteur créé")
        
        # Test connexion
        connected = await connector.connect()
        if not connected:
            print("❌ Échec connexion Polygon.io")
            return False
        print("✅ Connexion réussie")
        
        # Test prix sous-jacents
        spx_price = await connector.get_underlying_price("SPX")
        ndx_price = await connector.get_underlying_price("NDX")
        
        if spx_price:
            print(f"✅ Prix SPX récupéré: {spx_price}")
        else:
            print("⚠️ Prix SPX non disponible")
        
        if ndx_price:
            print(f"✅ Prix NDX récupéré: {ndx_price}")
        else:
            print("⚠️ Prix NDX non disponible")
        
        # Test info compte
        account_info = await connector.get_account_info()
        print(f"✅ Info compte: {account_info['provider']}")
        
        # Déconnexion
        await connector.disconnect()
        print("✅ Déconnexion réussie")
        
        print("="*50)
        return True
        
    except Exception as e:
        print(f"❌ Erreur test connecteur: {e}")
        print("="*50)
        return False

async def test_options_data():
    """Test de récupération des données options"""
    print("\n📊 Test des données options...")
    print("="*50)
    
    try:
        from polygon_connector import create_polygon_connector
        
        connector = create_polygon_connector()
        await connector.connect()
        
        # Test options SPX (échantillon réduit)
        print("🎯 Test options SPX...")
        spx_options = await connector.get_spx_options_levels("20250919")
        
        if spx_options and spx_options.get('strikes'):
            strikes_count = len(spx_options['strikes'])
            print(f"✅ {strikes_count} strikes SPX récupérés")
            
            # Afficher échantillon
            sample_strikes = list(spx_options['strikes'].keys())[:3]
            for strike in sample_strikes:
                strike_data = spx_options['strikes'][strike]
                call_bid = strike_data['call']['bid']
                call_ask = strike_data['call']['ask']
                put_bid = strike_data['put']['bid']
                put_ask = strike_data['put']['ask']
                print(f"   Strike {strike}: Call {call_bid:.2f}-{call_ask:.2f}, Put {put_bid:.2f}-{put_ask:.2f}")
        else:
            print("❌ Pas de données SPX récupérées")
        
        await connector.disconnect()
        print("="*50)
        return spx_options is not None
        
    except Exception as e:
        print(f"❌ Erreur test options: {e}")
        print("="*50)
        return False

async def test_snapshot_creation():
    """Test de création de snapshot"""
    print("\n📸 Test de création de snapshot...")
    print("="*50)
    
    try:
        from create_polygon_snapshot import create_polygon_snapshot
        
        # Créer snapshot SPX
        snapshot = await create_polygon_snapshot("SPX", "20250919", save_to_file=False)
        
        if snapshot:
            print("✅ Snapshot créé avec succès")
            print(f"   Symbol: {snapshot['symbol']}")
            print(f"   Options: {len(snapshot['options'])}")
            print(f"   Source: {snapshot['data_source']}")
            
            # Vérifier structure
            required_fields = ['snapshot_id', 'symbol', 'expiry', 'timestamp', 'options', 'analysis']
            missing_fields = [field for field in required_fields if field not in snapshot]
            
            if missing_fields:
                print(f"⚠️ Champs manquants: {missing_fields}")
            else:
                print("✅ Structure snapshot conforme")
            
            # Vérifier analyse
            analysis = snapshot.get('analysis', {})
            if 'dealers_bias' in analysis:
                bias = analysis['dealers_bias']
                print(f"✅ Dealer's Bias: {bias['dealers_bias_score']:.3f} ({bias['interpretation']['direction']})")
            else:
                print("⚠️ Dealer's Bias manquant")
        else:
            print("❌ Échec création snapshot")
        
        print("="*50)
        return snapshot is not None
        
    except Exception as e:
        print(f"❌ Erreur test snapshot: {e}")
        print("="*50)
        return False

def test_configuration():
    """Test de la configuration"""
    print("\n⚙️ Test de la configuration...")
    print("="*50)
    
    try:
        from polygon_config import get_polygon_config, test_polygon_config
        
        # Test config par défaut
        config = get_polygon_config("default")
        print("✅ Configuration par défaut chargée")
        print(f"   Rate limit: {config.rate_limit_delay}s")
        print(f"   Cache TTL: {config.cache_ttl_seconds}s")
        
        # Test config depuis environnement
        config_env = get_polygon_config("env")
        print("✅ Configuration environnement chargée")
        print(f"   API Key: {config_env.to_dict()['api_key']}")
        
        # Test validation
        errors = config.validate()
        if errors:
            print(f"⚠️ Erreurs validation: {errors}")
        else:
            print("✅ Configuration valide")
        
        print("="*50)
        return True
        
    except Exception as e:
        print(f"❌ Erreur test configuration: {e}")
        print("="*50)
        return False

def generate_migration_report(results: Dict[str, bool]):
    """Génère un rapport de migration"""
    print("\n📋 RAPPORT DE MIGRATION")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print()
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status}: {test_name}")
    
    print()
    if success_rate == 100:
        print("🎉 MIGRATION PRÊTE ! Tous les tests passent.")
        print("✅ Vous pouvez basculer vers Polygon.io en toute sécurité.")
    elif success_rate >= 75:
        print("⚠️ Migration majoritairement fonctionnelle.")
        print("💡 Corriger les échecs avant la bascule en production.")
    else:
        print("❌ Migration non prête.")
        print("🔧 Corriger les problèmes avant de continuer.")
    
    print("="*50)
    
    # Suggestions
    print("\n💡 SUGGESTIONS :")
    if not results.get("Environment Check", False):
        print("1. Vérifier POLYGON_API_KEY et dépendances")
    if not results.get("Connector Test", False):
        print("2. Vérifier connexion internet et clé API valide")
    if not results.get("Options Data Test", False):
        print("3. Vérifier limites de rate limiting Polygon")
    if not results.get("Snapshot Test", False):
        print("4. Vérifier permissions d'écriture fichiers")
    
    print("\n📖 Consulter: docs/GUIDE_MIGRATION_POLYGON_IO.md")
    print("="*50)

async def main():
    """Fonction principale de test"""
    print("🚀 TEST DE MIGRATION IBKR → POLYGON.IO")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # 1. Vérification environnement
    results["Environment Check"] = check_environment()
    
    if not results["Environment Check"]:
        print("\n❌ Prérequis manquants. Arrêt des tests.")
        return
    
    # 2. Test connecteur
    results["Connector Test"] = await test_polygon_connector()
    
    # 3. Test données options
    results["Options Data Test"] = await test_options_data()
    
    # 4. Test création snapshot
    results["Snapshot Test"] = await test_snapshot_creation()
    
    # 5. Test configuration
    results["Configuration Test"] = test_configuration()
    
    # 6. Rapport final
    generate_migration_report(results)

if __name__ == "__main__":
    asyncio.run(main())


