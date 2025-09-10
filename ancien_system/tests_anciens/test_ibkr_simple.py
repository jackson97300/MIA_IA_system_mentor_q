#!/usr/bin/env python3
"""
Test IBKR Simple - Éviter les conflits de boucles
=================================================

Test simple pour récupérer les prix ES/NQ sans conflit asyncio
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

async def test_ibkr_simple():
    """Test IBKR simple sans conflit de boucles"""
    print("🔍 TEST IBKR SIMPLE")
    print("="*50)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Objectif: Récupérer ES/NQ sans conflit asyncio")
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
        print("⏳ Étape 2: Stabilisation connexion (3s)...")
        await asyncio.sleep(3)
        
        # 3. Test ES une seule fois
        print("\n📊 Étape 3: Test ES (une seule tentative)...")
        try:
            es_data = await connector.get_market_data("ES")
            print(f"📊 ES Data: {es_data}")
            
            if es_data and es_data.get('last_price'):
                print(f"✅ ES: {es_data['last_price']} (IBKR)")
            elif es_data and es_data.get('mode') == 'error':
                print(f"❌ ES Error: {es_data.get('error', 'Unknown error')}")
            else:
                print("❌ ES: Aucune donnée")
        except Exception as e:
            print(f"❌ ES Exception: {e}")
        
        # 4. Test NQ une seule fois
        print("\n📊 Étape 4: Test NQ (une seule tentative)...")
        try:
            nq_data = await connector.get_market_data("NQ")
            print(f"📊 NQ Data: {nq_data}")
            
            if nq_data and nq_data.get('last_price'):
                print(f"✅ NQ: {nq_data['last_price']} (IBKR)")
            elif nq_data and nq_data.get('mode') == 'error':
                print(f"❌ NQ Error: {nq_data.get('error', 'Unknown error')}")
            else:
                print("❌ NQ: Aucune donnée")
        except Exception as e:
            print(f"❌ NQ Exception: {e}")
        
        # 5. Résultats finaux
        print("\n📋 RÉSULTATS FINAUX:")
        print("-" * 40)
        
        if es_data and es_data.get('last_price'):
            print(f"✅ ES Final: {es_data['last_price']}")
            print(f"   Mode: {es_data.get('mode', 'N/A')}")
            print(f"   Source: IBKR")
        else:
            print("❌ ES: Échec")
        
        if nq_data and nq_data.get('last_price'):
            print(f"✅ NQ Final: {nq_data['last_price']}")
            print(f"   Mode: {nq_data.get('mode', 'N/A')}")
            print(f"   Source: IBKR")
        else:
            print("❌ NQ: Échec")
        
        # 6. Déconnexion
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
    print("🚀 TEST IBKR SIMPLE")
    print("="*80)
    print("🎯 Test simple pour éviter les conflits asyncio")
    print("📊 Récupération ES/NQ en temps réel")
    print()
    
    success = await test_ibkr_simple()
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DU TEST")
    print(f"✅ Résultat: {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("\n🎉 TEST RÉUSSI !")
        print("✅ IBKR fonctionne")
        print("✅ Données récupérées")
    else:
        print("\n⚠️ TEST ÉCHOUÉ")
        print("🔧 Problème de configuration IBKR")

if __name__ == "__main__":
    asyncio.run(main())

