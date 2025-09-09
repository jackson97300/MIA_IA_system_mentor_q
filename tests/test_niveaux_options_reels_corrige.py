#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Corrigé Niveaux Options Réels
Test avec gestion correcte des méthodes async
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_niveaux_options_reels():
    """Test async des niveaux options réels"""
    
    print("MIA_IA_SYSTEM - TEST CORRIGE NIVEAUX OPTIONS REELS")
    print("=" * 60)
    print("Objectif: Confirmer utilisation vrais niveaux SPX IBKR")
    print("=" * 60)
    
    # 1. TEST CONNEXION IBKR
    print("\nTest connexion IBKR...")
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,
            'ibkr_client_id': 1,
            'simulation_mode': False,
            'require_real_data': True,
            'fallback_to_saved_data': False
        }
        
        connector = IBKRConnector(config)
        
        # Test connexion async correctement
        try:
            connected = await connector.connect()
            print("   IBKR connecte sur port 7497")
            print("   Mode donnees reelles active")
            
            # 2. TEST SPX OPTIONS RETRIEVER
            print("\nTest SPX Options Retriever...")
            
            from features.spx_options_retriever import SPXOptionsRetriever
            
            spx_retriever = SPXOptionsRetriever(connector)
            
            # Test recuperation donnees SPX
            spx_data = await spx_retriever.get_real_spx_data()
            
            print("   Donnees SPX recuperees:")
            print(f"      Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
            print(f"      VIX Level: {spx_data.get('vix_level', 'N/A')}")
            print(f"      Gamma Exposure: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
            print(f"      Dealer Position: {spx_data.get('dealer_position', 'N/A')}")
            print(f"      Source: {spx_data.get('data_source', 'N/A')}")
            print(f"      Timestamp: {spx_data.get('timestamp', 'N/A')}")
            
            # 3. VERIFICATION DONNEES REELLES
            print("\nVerification donnees reelles...")
            
            if spx_data.get('data_source') == 'ibkr_real':
                print("   DONNEES SPX REELLES CONFIRMEES")
                print("   Niveaux options reels actifs")
                return True
            else:
                print("   Donnees SPX non reelles")
                print(f"   Source actuelle: {spx_data.get('data_source', 'N/A')}")
                return False
                
        except Exception as e:
            print(f"   Erreur connexion IBKR: {e}")
            return False
            
    except Exception as e:
        print(f"   Erreur test: {e}")
        return False

def main():
    """Fonction principale"""
    try:
        # Executer test async
        success = asyncio.run(test_niveaux_options_reels())
        
        print("\n" + "=" * 60)
        print("RESULTATS TEST CORRIGE NIVEAUX OPTIONS")
        print("=" * 60)
        
        if success:
            print("SUCCES: Niveaux options reels confirmes")
            print("Systeme pret pour test 2h avec vraies donnees")
            print("Lancement recommande: python lance_mia_ia_tws.py")
        else:
            print("ECHEC: Niveaux options non confirmes")
            print("Verification manuelle necessaire")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Erreur execution: {e}")

if __name__ == "__main__":
    main()


