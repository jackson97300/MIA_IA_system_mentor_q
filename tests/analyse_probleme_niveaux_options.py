#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Analyse Problème Niveaux Options
Analyse détaillée du problème de niveaux options non confirmés
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def analyser_probleme_niveaux():
    """Analyse détaillée du problème niveaux options"""
    
    print("MIA_IA_SYSTEM - ANALYSE PROBLÈME NIVEAUX OPTIONS")
    print("=" * 60)
    print(f"Analyse: {datetime.now()}")
    print("=" * 60)
    
    # 1. Vérification configuration système
    print("\n1. VÉRIFICATION CONFIGURATION SYSTÈME")
    print("-" * 40)
    
    try:
        from config.automation_config import get_automation_config
        config = get_automation_config()
        print("✅ Configuration chargée")
        
        # Vérifier paramètres critiques
        print(f"   Simulation mode: {getattr(config, 'simulation_mode', 'N/A')}")
        print(f"   Use real data: {getattr(config, 'USE_REAL_DATA', 'N/A')}")
        print(f"   Force real data: {getattr(config, 'FORCE_REAL_DATA', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
    
    # 2. Vérification connexion IBKR
    print("\n2. VÉRIFICATION CONNEXION IBKR")
    print("-" * 40)
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        config_ibkr = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,
            'ibkr_client_id': 1,
            'simulation_mode': False,
            'require_real_data': True,
            'fallback_to_saved_data': False
        }
        
        connector = IBKRConnector(config_ibkr)
        print("✅ IBKRConnector créé")
        
        # Test connexion rapide
        try:
            connected = await asyncio.wait_for(connector.connect(), timeout=5.0)
            if connected:
                print("✅ Connexion IBKR réussie")
                print(f"   Status: {connector.connection_status}")
                print(f"   Connected: {connector.is_connected_flag}")
            else:
                print("❌ Connexion IBKR échouée")
                return False
        except asyncio.TimeoutError:
            print("❌ Timeout connexion IBKR")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur IBKR: {e}")
        return False
    
    # 3. Vérification SPX Options Retriever
    print("\n3. VÉRIFICATION SPX OPTIONS RETRIEVER")
    print("-" * 40)
    
    try:
        from features.spx_options_retriever import SPXOptionsRetriever
        
        spx_retriever = SPXOptionsRetriever(connector)
        print("✅ SPXOptionsRetriever créé")
        
        # Vérifier attributs critiques
        print(f"   Force real data: {getattr(spx_retriever, 'force_real_data', 'N/A')}")
        print(f"   Use ib insync: {getattr(spx_retriever, 'use_ib_insync', 'N/A')}")
        
        # Test récupération données
        print("\n   Test récupération données SPX...")
        spx_data = await spx_retriever.get_real_spx_data()
        
        print(f"   Données récupérées: {spx_data is not None}")
        if spx_data:
            print(f"   Source: {spx_data.get('data_source', 'N/A')}")
            print(f"   Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
            print(f"   VIX Level: {spx_data.get('vix_level', 'N/A')}")
            
            # Analyse source
            data_source = spx_data.get('data_source', 'N/A')
            if data_source == 'ibkr_real':
                print("✅ Source confirmée comme réelle")
                return True
            else:
                print(f"❌ Source non réelle: {data_source}")
                
                # Analyse causes possibles
                print("\n   ANALYSE CAUSES POSSIBLES:")
                print("   - TWS non connecté ou port fermé")
                print("   - Souscription données SPX non activée")
                print("   - Données SPX non disponibles en temps réel")
                print("   - Configuration IBKR incorrecte")
                print("   - Fallback vers données simulées activé")
                
                return False
        else:
            print("❌ Aucune donnée récupérée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur SPX retriever: {e}")
        return False

def main():
    """Fonction principale"""
    try:
        print("Démarrage analyse problème niveaux options...")
        
        # Exécuter analyse
        success = asyncio.run(analyser_probleme_niveaux())
        
        print("\n" + "=" * 60)
        print("RÉSULTATS ANALYSE")
        print("=" * 60)
        
        if success:
            print("✅ SUCCÈS: Niveaux options réels confirmés")
            print("✅ Système prêt pour test 2h")
            print("🚀 Lancement recommandé: python lance_mia_ia_tws.py")
        else:
            print("❌ ÉCHEC: Niveaux options non confirmés")
            print("\n🔧 ACTIONS CORRECTIVES RECOMMANDÉES:")
            print("1. Vérifier TWS est démarré et connecté")
            print("2. Vérifier port 7497 ouvert")
            print("3. Activer souscription données SPX options")
            print("4. Vérifier configuration IBKR")
            print("5. S'assurer marchés SPX sont ouverts")
            print("6. Vérifier pas de fallback vers simulation")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")

if __name__ == "__main__":
    main()


