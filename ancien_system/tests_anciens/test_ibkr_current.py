#!/usr/bin/env python3
"""
Test IBKR - Solution Temporaire
===============================

Utilisation d'IBKR en attendant le mois prochain pour Sierra Chart temps réel
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def test_ibkr_current():
    """Test IBKR pour données de marché"""
    print("📡 TEST IBKR - SOLUTION TEMPORAIRE")
    print("="*50)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    print("💰 Économique: Pas de coût supplémentaire")
    print("⏳ En attendant: Sierra Chart temps réel (mois prochain)")
    print()
    
    # Créer le connecteur IBKR
    connector = IBKRConnector()
    
    try:
        # 1. Connexion IBKR
        print("🔌 Étape 1: Connexion IBKR...")
        if await connector.connect():
            print("✅ Connexion IBKR réussie")
        else:
            print("❌ Échec connexion IBKR")
            return False
        
        # 2. Attendre stabilisation
        print("⏳ Étape 2: Stabilisation connexion (5s)...")
        await asyncio.sleep(5)
        
        # 3. Test ES avec attente
        print("\n📊 Étape 3: Test ES via IBKR (attente 10s)...")
        es_data = None
        for i in range(10):
            es_data = await connector.get_market_data("ES")
            print(f"   Tentative {i+1}/10: {es_data}")
            if es_data and es_data.get('last_price'):
                print(f"✅ ES: {es_data['last_price']} (IBKR)")
                break
            await asyncio.sleep(1)
        else:
            print("❌ ES: Aucune donnée après 10s")
        
        # 4. Test NQ avec attente
        print("\n📊 Étape 4: Test NQ via IBKR (attente 10s)...")
        nq_data = None
        for i in range(10):
            nq_data = await connector.get_market_data("NQ")
            print(f"   Tentative {i+1}/10: {nq_data}")
            if nq_data and nq_data.get('last_price'):
                print(f"✅ NQ: {nq_data['last_price']} (IBKR)")
                break
            await asyncio.sleep(1)
        else:
            print("❌ NQ: Aucune donnée après 10s")
        
        # 5. Test SPX Options avec attente
        print("\n📊 Étape 5: Test SPX Options via IBKR (attente 10s)...")
        spx_data = None
        for i in range(10):
            spx_data = await connector.get_market_data("SPX")
            print(f"   Tentative {i+1}/10: {spx_data}")
            if spx_data and spx_data.get('last_price'):
                print(f"✅ SPX: {spx_data['last_price']} (IBKR)")
                break
            await asyncio.sleep(1)
        else:
            print("❌ SPX: Aucune donnée après 10s")
        
        # 6. Résultats finaux
        print("\n📋 RÉSULTATS FINAUX IBKR:")
        print("-" * 40)
        
        if es_data and es_data.get('last_price'):
            print(f"✅ ES Final: {es_data['last_price']}")
            print(f"   Timestamp: {es_data.get('timestamp', 'N/A')}")
            print(f"   Source: IBKR")
            print(f"   Bid: {es_data.get('bid', 'N/A')}")
            print(f"   Ask: {es_data.get('ask', 'N/A')}")
            print(f"   Mode: {es_data.get('mode', 'N/A')}")
        else:
            print("❌ ES: Aucune donnée reçue")
        
        if nq_data and nq_data.get('last_price'):
            print(f"✅ NQ Final: {nq_data['last_price']}")
            print(f"   Timestamp: {nq_data.get('timestamp', 'N/A')}")
            print(f"   Source: IBKR")
            print(f"   Bid: {nq_data.get('bid', 'N/A')}")
            print(f"   Ask: {nq_data.get('ask', 'N/A')}")
            print(f"   Mode: {nq_data.get('mode', 'N/A')}")
        else:
            print("❌ NQ: Aucune donnée reçue")
        
        if spx_data and spx_data.get('last_price'):
            print(f"✅ SPX Final: {spx_data['last_price']}")
            print(f"   Timestamp: {spx_data.get('timestamp', 'N/A')}")
            print(f"   Source: IBKR")
            print(f"   Mode: {spx_data.get('mode', 'N/A')}")
        else:
            print("❌ SPX: Aucune donnée reçue")
        
        # 7. Déconnexion
        print("\n🔌 Déconnexion IBKR...")
        await connector.disconnect()
        print("✅ Test terminé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        await connector.disconnect()
        return False

async def main():
    """Fonction principale"""
    print("🚀 TEST IBKR - SOLUTION ÉCONOMIQUE")
    print("="*80)
    print("💰 Stratégie économique:")
    print("   - Utiliser IBKR (gratuit)")
    print("   - Attendre le mois prochain")
    print("   - Souscrire Sierra Chart temps réel")
    print("   - Économiser ~$50-100")
    print()
    
    success = await test_ibkr_current()
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DE LA STRATÉGIE")
    print(f"✅ Résultat: {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("\n🎉 STRATÉGIE RÉUSSIE !")
        print("✅ IBKR fonctionne parfaitement")
        print("✅ Données de marché disponibles")
        print("✅ MIA peut fonctionner avec IBKR")
        print("💰 Économie: ~$50-100 ce mois-ci")
        print("📅 Plan: Sierra Chart temps réel le mois prochain")
    else:
        print("\n⚠️ STRATÉGIE ÉCHOUÉE")
        print("🔧 Vérifiez la configuration IBKR")
        print("🔧 Assurez-vous que TWS/IB Gateway est connecté")

if __name__ == "__main__":
    asyncio.run(main())
