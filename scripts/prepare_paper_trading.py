#!/usr/bin/env python3
"""
Prepare Paper Trading - MIA_IA_SYSTEM
=====================================

Script de préparation pour Paper Trading IBKR
avec Level 2 + Options.

USAGE:
python scripts/prepare_paper_trading.py
"""

import sys
import os
import asyncio
from datetime import datetime
import json

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.ibkr_config import IB_GATEWAY_CONFIG, MARKET_DATA_CONFIG

def check_ib_gateway_installation():
    """Vérifie l'installation IB Gateway"""
    print("🔍 VÉRIFICATION INSTALLATION IB GATEWAY")
    print("=" * 50)
    
    # Vérifications système
    print("1️⃣ Vérifications système...")
    
    # Vérifier Python
    print(f"   Python version : {sys.version}")
    
    # Vérifier ib_insync
    try:
        import ib_insync
        print("✅ ib_insync installé")
    except ImportError:
        print("❌ ib_insync non installé")
        print("   Installez avec : pip install ib_insync")
        return False
    
    # Vérifier configuration
    print("\n2️⃣ Vérification configuration...")
    
    config_file = "config/ibkr_config.py"
    if os.path.exists(config_file):
        print("✅ Fichier de configuration trouvé")
    else:
        print("❌ Fichier de configuration manquant")
        return False
    
    print("\n3️⃣ Configuration IB Gateway...")
    print("   Host :", IB_GATEWAY_CONFIG['host'])
    print("   Port :", IB_GATEWAY_CONFIG['port'])
    print("   Client ID :", IB_GATEWAY_CONFIG['client_id'])
    
    print("\n4️⃣ Données souscrites...")
    print("   CME Level 2 :", MARKET_DATA_CONFIG['cme_level2']['cost'], "$/mois")
    print("   OPRA Level 1 :", MARKET_DATA_CONFIG['opra_level1']['cost'], "$/mois")
    print("   Total :", MARKET_DATA_CONFIG['cme_level2']['cost'] + MARKET_DATA_CONFIG['opra_level1']['cost'], "$/mois")
    
    return True

def create_paper_trading_config():
    """Crée la configuration Paper Trading"""
    print("\n📝 CRÉATION CONFIGURATION PAPER TRADING")
    print("=" * 50)
    
    config = {
        'paper_trading': {
            'enabled': True,
            'account_type': 'Paper',
            'data_source': 'IBKR',
            'trading_platform': 'MFFU/Tradovate'
        },
        'market_data': {
            'cme_level2': MARKET_DATA_CONFIG['cme_level2'],
            'opra_level1': MARKET_DATA_CONFIG['opra_level1']
        },
        'testing_plan': {
            'phase_1': 'Validation Order Book Imbalance',
            'phase_2': 'Test Options Greeks',
            'phase_3': 'Validation Signaux',
            'phase_4': 'Optimisation Paramètres',
            'phase_5': 'Préparation Live'
        },
        'performance_targets': {
            'win_rate_min': 0.55,
            'profit_factor_min': 1.5,
            'max_drawdown': 0.10,
            'latency_max': 0.5
        }
    }
    
    # Sauvegarder configuration
    config_file = "config/paper_trading_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration Paper Trading créée :", config_file)
    return config

def create_test_plan():
    """Crée le plan de test détaillé"""
    print("\n📋 PLAN DE TEST PAPER TRADING")
    print("=" * 50)
    
    test_plan = {
        'week_1': {
            'day_1_2': 'Installation et configuration IB Gateway',
            'day_3_4': 'Test connexion et données Level 2',
            'day_5_7': 'Test Order Book Imbalance'
        },
        'week_2': {
            'day_1_3': 'Test Options Greeks et OPRA',
            'day_4_5': 'Intégration avec bot MIA_IA_SYSTEM',
            'day_6_7': 'Test signaux générés'
        },
        'week_3': {
            'day_1_3': 'Validation performances (win rate)',
            'day_4_5': 'Optimisation paramètres',
            'day_6_7': 'Test stabilité 24/7'
        },
        'week_4': {
            'day_1_3': 'Validation finale',
            'day_4_5': 'Préparation passage live',
            'day_6_7': 'Configuration MFFU/Tradovate'
        }
    }
    
    # Sauvegarder plan
    plan_file = "config/paper_trading_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(test_plan, f, indent=2)
    
    print("✅ Plan de test créé :", plan_file)
    return test_plan

def print_next_steps():
    """Affiche les prochaines étapes"""
    print("\n🚀 PROCHAINES ÉTAPES")
    print("=" * 50)
    
    print("1️⃣ En attente du compte Paper IBKR...")
    print("   - Vérifiez vos emails IBKR")
    print("   - Compte créé sous 24-48h")
    
    print("\n2️⃣ Une fois le compte créé :")
    print("   - Connectez-vous à IB Gateway")
    print("   - Sélectionnez compte Paper")
    print("   - Lancez : python scripts/test_ib_connection.py")
    
    print("\n3️⃣ Test complet :")
    print("   - Test Level 2 ES/NQ")
    print("   - Test Options SPX")
    print("   - Test Order Book Imbalance")
    
    print("\n4️⃣ Intégration bot :")
    print("   - Test avec votre bot MIA_IA_SYSTEM")
    print("   - Validation des signaux")
    print("   - Optimisation performances")

async def main():
    """Fonction principale"""
    print("🚀 PRÉPARATION PAPER TRADING MIA_IA_SYSTEM")
    print("=" * 60)
    print(f"⏰ Préparation démarrée : {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # 1. Vérification installation
    if not check_ib_gateway_installation():
        print("\n❌ Problèmes détectés. Corrigez avant de continuer.")
        return
    
    # 2. Création configuration
    config = create_paper_trading_config()
    
    # 3. Création plan de test
    test_plan = create_test_plan()
    
    # 4. Prochaines étapes
    print_next_steps()
    
    print("\n" + "=" * 60)
    print("✅ PRÉPARATION TERMINÉE")
    print("=" * 60)
    print("📧 Attendez l'email de création du compte Paper")
    print("🔧 Tout est prêt pour commencer les tests !")
    print("💰 Coût mensuel : $12.50 (CME L2 + OPRA L1)")

if __name__ == "__main__":
    asyncio.run(main()) 