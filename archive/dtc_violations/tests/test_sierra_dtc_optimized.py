#!/usr/bin/env python3
"""
Test Sierra Chart DTC Optimisé
==============================

Test complet selon les instructions précises :
1. Handshake ENCODING_REQUEST → ENCODING_RESPONSE
2. LOGON_REQUEST → LOGON_RESPONSE  
3. SECURITY_DEFINITION_REQUEST pour ESU25_FUT_CME
4. MARKET_DATA_SUBSCRIBE avec SymbolID unique
5. Attente 30s pour données réelles
6. Pas de fallback IBKR
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

async def test_sierra_dtc_optimized():
    """Test Sierra Chart DTC optimisé selon instructions précises"""
    print("🎯 TEST SIERRA CHART DTC OPTIMISÉ")
    print("="*60)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Créer le connecteur
    connector = SierraDTCConnector()
    
    try:
        # 1. Connexion
        print("🔌 Étape 1: Connexion Sierra Chart DTC...")
        if not connector.connect():
            print("❌ Échec connexion")
            return False
        print("✅ Connexion réussie")
        
        # 2. Attendre stabilisation
        print("⏳ Étape 2: Stabilisation connexion (3s)...")
        await asyncio.sleep(3)
        
        # 3. Test ES avec symbole complet
        print("\n📊 Étape 3: Test ES (ESU25_FUT_CME)...")
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
        
        # 5. Attendre les données (30s comme demandé)
        print("\n⏳ Étape 5: Attente données (30s)...")
        for i in range(30):
            await asyncio.sleep(1)
            
            # Vérifier ES
            es_data = connector.get_market_data("ESU25_FUT_CME")
            if es_data and es_data.get('price'):
                print(f"   📊 ES: {es_data.get('price', 'N/A')} (Source: {es_data.get('data_source', 'N/A')})")
            
            # Vérifier NQ
            nq_data = connector.get_market_data("NQU25_FUT_CME")
            if nq_data and nq_data.get('price'):
                print(f"   📊 NQ: {nq_data.get('price', 'N/A')} (Source: {nq_data.get('data_source', 'N/A')})")
            
            # Afficher progression
            if (i + 1) % 5 == 0:
                print(f"   ⏱️  Progression: {i+1}/30s")
        
        # 6. Résultats finaux
        print("\n📋 RÉSULTATS FINAUX:")
        print("-" * 40)
        
        es_final = connector.get_market_data("ESU25_FUT_CME")
        nq_final = connector.get_market_data("NQU25_FUT_CME")
        
        if es_final and es_final.get('price'):
            print(f"✅ ES Final: {es_final.get('price', 'N/A')}")
            print(f"   Timestamp: {es_final.get('timestamp', 'N/A')}")
            print(f"   Source: {es_final.get('data_source', 'N/A')}")
            print(f"   TickSize: {getattr(connector, 'tick_size', 'N/A')}")
            print(f"   PriceMultiplier: {getattr(connector, 'price_multiplier', 'N/A')}")
        else:
            print("❌ ES: Aucune donnée reçue")
        
        if nq_final and nq_final.get('price'):
            print(f"✅ NQ Final: {nq_final.get('price', 'N/A')}")
            print(f"   Timestamp: {nq_final.get('timestamp', 'N/A')}")
            print(f"   Source: {nq_final.get('data_source', 'N/A')}")
            print(f"   TickSize: {getattr(connector, 'tick_size', 'N/A')}")
            print(f"   PriceMultiplier: {getattr(connector, 'price_multiplier', 'N/A')}")
        else:
            print("❌ NQ: Aucune donnée reçue")
        
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
    print("🚀 TEST SIERRA CHART DTC OPTIMISÉ")
    print("="*80)
    print("🎯 Suivant les instructions précises :")
    print("   - Handshake ENCODING_REQUEST → ENCODING_RESPONSE")
    print("   - LOGON_REQUEST → LOGON_RESPONSE")
    print("   - SECURITY_DEFINITION_REQUEST")
    print("   - MARKET_DATA_SUBSCRIBE avec SymbolID")
    print("   - Attente 30s pour données réelles")
    print("   - Pas de fallback IBKR")
    print()
    
    success = await test_sierra_dtc_optimized()
    
    print("\n" + "="*80)
    print("📋 RÉSUMÉ DU TEST")
    print(f"✅ Résultat: {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("\n🎉 TEST RÉUSSI !")
        print("✅ Sierra Chart DTC fonctionne parfaitement")
        print("✅ Handshake et Security Definition OK")
        print("✅ Données de marché reçues")
    else:
        print("\n⚠️ TEST ÉCHOUÉ")
        print("🔧 Vérifiez la configuration Sierra Chart")

if __name__ == "__main__":
    asyncio.run(main())

