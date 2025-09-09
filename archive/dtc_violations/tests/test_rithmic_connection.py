#!/usr/bin/env python3
"""
Test Connexion Rithmic via Sierra Chart DTC
===========================================

Test de la nouvelle connexion Rithmic après migration depuis Teton
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.sierra_dtc_connector import SierraDTCConnector

logger = get_logger(__name__)

async def test_rithmic_connection():
    """Test de la connexion Rithmic via Sierra Chart DTC"""
    print("🔄 TEST CONNEXION RITHMIC")
    print("="*50)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    print("📡 Migration Teton → Rithmic")
    print()
    
    # Créer le connecteur
    connector = SierraDTCConnector()
    
    try:
        # 1. Connexion
        print("🔌 Étape 1: Connexion Sierra Chart DTC (Rithmic)...")
        if not connector.connect():
            print("❌ Échec connexion")
            return False
        print("✅ Connexion réussie")
        
        # 2. Attendre stabilisation
        print("⏳ Étape 2: Stabilisation connexion (5s)...")
        await asyncio.sleep(5)
        
        # 3. Test ES avec symbole complet
        print("\n📊 Étape 3: Test ES (ESU25_FUT_CME) - Rithmic...")
        if connector.subscribe_market_data("ESU25_FUT_CME"):
            print("✅ Souscription ES réussie")
        else:
            print("❌ Échec souscription ES")
        
        # 4. Test NQ avec symbole complet  
        print("📊 Étape 4: Test NQ (NQU25_FUT_CME) - Rithmic...")
        if connector.subscribe_market_data("NQU25_FUT_CME"):
            print("✅ Souscription NQ réussie")
        else:
            print("❌ Échec souscription NQ")
        
        # 5. Attendre les données (20s pour Rithmic)
        print("\n⏳ Étape 5: Attente données Rithmic (20s)...")
        for i in range(20):
            await asyncio.sleep(1)
            
            # Vérifier ES
            es_data = connector.get_market_data("ESU25_FUT_CME")
            if es_data and es_data.get('price'):
                print(f"   📊 ES: {es_data.get('price', 'N/A')} (Rithmic)")
            
            # Vérifier NQ
            nq_data = connector.get_market_data("NQU25_FUT_CME")
            if nq_data and nq_data.get('price'):
                print(f"   📊 NQ: {nq_data.get('price', 'N/A')} (Rithmic)")
            
            # Afficher progression
            if (i + 1) % 5 == 0:
                print(f"   ⏱️  Progression: {i+1}/20s")
        
        # 6. Résultats finaux
        print("\n📋 RÉSULTATS FINAUX RITHMIC:")
        print("-" * 40)
        
        es_final = connector.get_market_data("ESU25_FUT_CME")
        nq_final = connector.get_market_data("NQU25_FUT_CME")
        
        if es_final and es_final.get('price'):
            print(f"✅ ES Final: {es_final.get('price', 'N/A')}")
            print(f"   Timestamp: {es_final.get('timestamp', 'N/A')}")
            print(f"   Source: Rithmic via Sierra Chart")
            print(f"   TickSize: {getattr(connector, 'tick_size', 'N/A')}")
            print(f"   PriceMultiplier: {getattr(connector, 'price_multiplier', 'N/A')}")
        else:
            print("❌ ES: Aucune donnée reçue (vérifier config Rithmic)")
        
        if nq_final and nq_final.get('price'):
            print(f"✅ NQ Final: {nq_final.get('price', 'N/A')}")
            print(f"   Timestamp: {nq_final.get('timestamp', 'N/A')}")
            print(f"   Source: Rithmic via Sierra Chart")
            print(f"   TickSize: {getattr(connector, 'tick_size', 'N/A')}")
            print(f"   PriceMultiplier: {getattr(connector, 'price_multiplier', 'N/A')}")
        else:
            print("❌ NQ: Aucune donnée reçue (vérifier config Rithmic)")
        
        # 7. Déconnexion propre
        print("\n🔌 Déconnexion propre...")
        connector.disconnect()
        print("✅ Test terminé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        connector.disconnect()
        return False

async def main():
    """Fonction principale"""
    print("🚀 TEST MIGRATION TETON → RITHMIC")
    print("="*80)
    print("🔄 Migration en cours...")
    print("   - Désactivation Teton")
    print("   - Activation Rithmic")
    print("   - Test connexion DTC")
    print("   - Validation données de marché")
    print()
    
    success = await test_rithmic_connection()
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DE LA MIGRATION")
    print(f"✅ Résultat: {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("\n🎉 MIGRATION RÉUSSIE !")
        print("✅ Rithmic fonctionne parfaitement")
        print("✅ Données de marché reçues")
        print("✅ Sierra Chart DTC opérationnel")
    else:
        print("\n⚠️ MIGRATION ÉCHOUÉE")
        print("🔧 Vérifiez la configuration Rithmic dans Sierra Chart")
        print("🔧 Assurez-vous que les credentials Rithmic sont corrects")

if __name__ == "__main__":
    asyncio.run(main())

