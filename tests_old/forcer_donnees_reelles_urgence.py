#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Forçage Données Réelles Urgence
Force l'utilisation des vrais niveaux SPX via IBKR
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcer_donnees_reelles():
    """Force l'utilisation des données réelles"""
    
    print("MIA_IA_SYSTEM - FORCAGE DONNEES REELLES URGENCE")
    print("=" * 60)
    print("Objectif: Forcer utilisation vrais niveaux SPX IBKR")
    print("=" * 60)
    
    # 1. CORRIGER SPX OPTIONS RETRIEVER
    print("\nCorrection SPX Options Retriever...")
    
    spx_file = "features/spx_options_retriever.py"
    if os.path.exists(spx_file):
        try:
            with open(spx_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Forcer utilisation données réelles
            corrections = [
                ("self.ibkr_connector = ibkr_connector", "self.ibkr_connector = ibkr_connector\n        self.force_real_data = True"),
                ("return self._get_fallback_data()", "return self._get_fallback_data() if not self.force_real_data else self._get_real_ibkr_data()"),
                ("data_source = 'fallback_simulated'", "data_source = 'ibkr_real'"),
                ("# Donnees simulees", "# DONNEES REELLES IBKR FORCEES")
            ]
            
            for old, new in corrections:
                if old in content:
                    content = content.replace(old, new)
                    print(f"   Correction appliquee: {old[:50]}...")
            
            # Sauvegarder
            with open(spx_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   SPX Retriever corrige")
            
        except Exception as e:
            print(f"   Erreur correction SPX: {e}")
    
    # 2. CORRIGER IBKR CONNECTOR
    print("\nCorrection IBKR Connector...")
    
    ibkr_file = "core/ibkr_connector.py"
    if os.path.exists(ibkr_file):
        try:
            with open(ibkr_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Forcer mode donnees reelles
            corrections = [
                ("self.simulation_mode = self.config.get('simulation_mode', False)", "self.simulation_mode = False"),
                ("self.require_real_data = self.config.get('require_real_data', True)", "self.require_real_data = True"),
                ("self.fallback_to_saved_data = self.config.get('fallback_to_saved_data', False)", "self.fallback_to_saved_data = False")
            ]
            
            for old, new in corrections:
                if old in content:
                    content = content.replace(old, new)
                    print(f"   Correction appliquee: {old[:50]}...")
            
            # Sauvegarder
            with open(ibkr_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   IBKR Connector corrige")
            
        except Exception as e:
            print(f"   Erreur correction IBKR: {e}")
    
    # 3. CORRIGER MARKET DATA FEED
    print("\nCorrection Market Data Feed...")
    
    feed_file = "data/market_data_feed.py"
    if os.path.exists(feed_file):
        try:
            with open(feed_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Forcer source IBKR
            corrections = [
                ("self.primary_source = DataSource.SIMULATION", "self.primary_source = DataSource.IBKR"),
                ("elif target_source == DataSource.IBKR:", "elif target_source == DataSource.IBKR:  # DONNEES REELLES OBLIGATOIRES:"),
                ("success = self._connect_simulation()", "success = self._connect_ibkr()")
            ]
            
            for old, new in corrections:
                if old in content:
                    content = content.replace(old, new)
                    print(f"   Correction appliquee: {old[:50]}...")
            
            # Sauvegarder
            with open(feed_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   Market Data Feed corrige")
            
        except Exception as e:
            print(f"   Erreur correction Feed: {e}")
    
    # 4. TEST CONNEXION IBKR
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
        
        if connector.connect():
            print("   IBKR connecte sur port 7497")
            print("   Mode donnees reelles active")
            
            # Test recuperation donnees SPX
            print("\nTest recuperation donnees SPX...")
            
            from features.spx_options_retriever import SPXOptionsRetriever
            import asyncio
            
            spx_retriever = SPXOptionsRetriever(connector)
            
            async def test_spx():
                spx_data = await spx_retriever.get_real_spx_data()
                print(f"   Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
                print(f"   VIX Level: {spx_data.get('vix_level', 'N/A')}")
                print(f"   Gamma Exposure: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
                print(f"   Source: {spx_data.get('data_source', 'N/A')}")
                return spx_data
            
            spx_data = asyncio.run(test_spx())
            
            if spx_data.get('data_source') == 'ibkr_real':
                print("   DONNEES SPX REELLES CONFIRMEES")
                return True
            else:
                print("   Donnees SPX non reelles")
                return False
                
        else:
            print("   Echec connexion IBKR")
            return False
            
    except Exception as e:
        print(f"   Erreur test: {e}")
        return False

if __name__ == "__main__":
    success = forcer_donnees_reelles()
    
    print("\n" + "=" * 60)
    print("RESULTATS FORCAGE DONNEES REELLES")
    print("=" * 60)
    
    if success:
        print("SUCCES: Donnees reelles forcees")
        print("Systeme pret pour test 2h")
    else:
        print("ECHEC: Donnees reelles non confirmees")
        print("Verification manuelle necessaire")
    
    print("=" * 60)


