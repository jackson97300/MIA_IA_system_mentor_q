#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Détaillé Niveaux Options Réels
Diagnostic étape par étape pour identifier les problèmes
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_niveaux_options():
    """Diagnostic détaillé des niveaux options réels"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC DÉTAILLÉ NIVEAUX OPTIONS")
    print("=" * 70)
    print("Objectif: Identifier précisément où ça bloque")
    print("=" * 70)
    
    # ÉTAPE 1: Vérification imports
    print("\n1. VÉRIFICATION IMPORTS...")
    try:
        from core.ibkr_connector import IBKRConnector
        print("   ✅ IBKRConnector importé")
    except Exception as e:
        print(f"   ❌ Erreur import IBKRConnector: {e}")
        return False
    
    try:
        from features.spx_options_retriever import SPXOptionsRetriever
        print("   ✅ SPXOptionsRetriever importé")
    except Exception as e:
        print(f"   ❌ Erreur import SPXOptionsRetriever: {e}")
        return False
    
    # ÉTAPE 2: Configuration
    print("\n2. CONFIGURATION...")
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,
        'ibkr_client_id': 1,
        'simulation_mode': False,
        'require_real_data': True,
        'fallback_to_saved_data': False
    }
    print(f"   Configuration: {config}")
    
    # ÉTAPE 3: Création connector
    print("\n3. CRÉATION IBKR CONNECTOR...")
    try:
        connector = IBKRConnector(config)
        print("   ✅ IBKRConnector créé")
        print(f"   Host: {connector.host}")
        print(f"   Port: {connector.port}")
        print(f"   Simulation mode: {connector.simulation_mode}")
        print(f"   Require real data: {connector.require_real_data}")
    except Exception as e:
        print(f"   ❌ Erreur création connector: {e}")
        return False
    
    # ÉTAPE 4: Test connexion IBKR
    print("\n4. TEST CONNEXION IBKR...")
    try:
        print("   Tentative connexion...")
        connected = await connector.connect()
        print(f"   Résultat connexion: {connected}")
        
        if connected:
            print("   ✅ IBKR connecté avec succès")
            print(f"   Status: {connector.connection_status}")
            print(f"   Is connected: {connector.is_connected_flag}")
        else:
            print("   ❌ Échec connexion IBKR")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return False
    
    # ÉTAPE 5: Création SPX Retriever
    print("\n5. CRÉATION SPX OPTIONS RETRIEVER...")
    try:
        spx_retriever = SPXOptionsRetriever(connector)
        print("   ✅ SPXOptionsRetriever créé")
        
        # Vérification attributs
        print(f"   Force real data: {getattr(spx_retriever, 'force_real_data', 'N/A')}")
        print(f"   Use ib insync: {getattr(spx_retriever, 'use_ib_insync', 'N/A')}")
        
    except Exception as e:
        print(f"   ❌ Erreur création SPX retriever: {e}")
        return False
    
    # ÉTAPE 6: Test récupération données SPX
    print("\n6. TEST RÉCUPÉRATION DONNÉES SPX...")
    try:
        print("   Tentative récupération données...")
        spx_data = await spx_retriever.get_real_spx_data()
        print("   ✅ Données SPX récupérées")
        
        # Affichage détaillé des données
        print("\n   DÉTAILS DONNÉES SPX:")
        print(f"      Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
        print(f"      VIX Level: {spx_data.get('vix_level', 'N/A')}")
        print(f"      Gamma Exposure: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
        print(f"      Dealer Position: {spx_data.get('dealer_position', 'N/A')}")
        print(f"      Source: {spx_data.get('data_source', 'N/A')}")
        print(f"      Timestamp: {spx_data.get('timestamp', 'N/A')}")
        
        # Vérification source
        data_source = spx_data.get('data_source', 'N/A')
        print(f"\n   VÉRIFICATION SOURCE: {data_source}")
        
        if data_source == 'ibkr_real':
            print("   ✅ DONNÉES SPX REELLES CONFIRMÉES")
            return True
        else:
            print(f"   ❌ Source non réelle: {data_source}")
            print("   🔍 Analyse des causes possibles...")
            
            # Vérification méthodes internes
            print("\n   VÉRIFICATION MÉTHODES INTERNES:")
            
            # Test méthode _get_real_ibkr_data
            try:
                real_data = await spx_retriever._get_real_ibkr_data()
                print(f"      _get_real_ibkr_data: {real_data.get('data_source', 'N/A')}")
            except Exception as e:
                print(f"      _get_real_ibkr_data: Erreur - {e}")
            
            # Test méthode _get_fallback_data
            try:
                fallback_data = spx_retriever._get_fallback_data()
                print(f"      _get_fallback_data: {fallback_data.get('data_source', 'N/A')}")
            except Exception as e:
                print(f"      _get_fallback_data: Erreur - {e}")
            
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur récupération données: {e}")
        return False

def main():
    """Fonction principale"""
    try:
        print(f"Début diagnostic: {datetime.now()}")
        
        # Exécuter diagnostic async
        success = asyncio.run(diagnostic_niveaux_options())
        
        print("\n" + "=" * 70)
        print("RÉSULTATS DIAGNOSTIC DÉTAILLÉ")
        print("=" * 70)
        
        if success:
            print("✅ SUCCÈS: Niveaux options réels confirmés")
            print("✅ Système prêt pour test 2h avec vraies données")
            print("🚀 Lancement recommandé: python lance_mia_ia_tws.py")
        else:
            print("❌ ÉCHEC: Niveaux options non confirmés")
            print("🔧 Correction manuelle nécessaire")
            print("📋 Vérifier:")
            print("   - Connexion TWS sur port 7497")
            print("   - Souscription données SPX options")
            print("   - Configuration IBKR")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erreur exécution diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


