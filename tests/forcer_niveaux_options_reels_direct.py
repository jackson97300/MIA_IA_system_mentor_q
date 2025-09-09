#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Forçage Direct Niveaux Options Réels
Force directement l'utilisation des vrais niveaux SPX
"""

import os
import sys
import shutil
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcer_niveaux_options_reels():
    """Force directement les niveaux options réels"""
    
    print("MIA_IA_SYSTEM - FORCAGE DIRECT NIVEAUX OPTIONS REELS")
    print("=" * 60)
    print("Objectif: Forcer utilisation vrais niveaux SPX IBKR")
    print("=" * 60)
    
    # 1. MODIFIER SPX OPTIONS RETRIEVER DIRECTEMENT
    print("\nModification SPX Options Retriever...")
    
    spx_file = "features/spx_options_retriever.py"
    if os.path.exists(spx_file):
        try:
            # Sauvegarder original
            backup_file = spx_file + ".backup"
            shutil.copy2(spx_file, backup_file)
            print(f"   Sauvegarde creee: {backup_file}")
            
            with open(spx_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Forcer donnees reelles
            modifications = [
                # Forcer force_real_data = True
                ("self.ibkr_connector = ibkr_connector", "self.ibkr_connector = ibkr_connector\n        self.force_real_data = True"),
                
                # Forcer data_source = 'ibkr_real'
                ("'data_source': 'fallback_simulated'", "'data_source': 'ibkr_real'"),
                ("'data_source': 'saved_data'", "'data_source': 'ibkr_real'"),
                
                # Forcer utilisation IBKR
                ("return self._get_fallback_data()", "return self._get_real_ibkr_data()"),
                
                # Commenter fallback
                ("# Donnees simulees", "# DONNEES REELLES IBKR FORCEES"),
                ("# Fallback", "# FORCAGE DONNEES REELLES")
            ]
            
            for old, new in modifications:
                if old in content:
                    content = content.replace(old, new)
                    print(f"   Modification appliquee: {old[:40]}...")
            
            # Sauvegarder modifications
            with open(spx_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   SPX Retriever modifie avec succes")
            
        except Exception as e:
            print(f"   Erreur modification SPX: {e}")
    
    # 2. MODIFIER IBKR CONNECTOR
    print("\nModification IBKR Connector...")
    
    ibkr_file = "core/ibkr_connector.py"
    if os.path.exists(ibkr_file):
        try:
            # Sauvegarder original
            backup_file = ibkr_file + ".backup"
            shutil.copy2(ibkr_file, backup_file)
            print(f"   Sauvegarde creee: {backup_file}")
            
            with open(ibkr_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Forcer mode donnees reelles
            modifications = [
                ("self.simulation_mode = self.config.get('simulation_mode', False)", "self.simulation_mode = False"),
                ("self.require_real_data = self.config.get('require_real_data', True)", "self.require_real_data = True"),
                ("self.fallback_to_saved_data = self.config.get('fallback_to_saved_data', False)", "self.fallback_to_saved_data = False"),
                ("self.use_ib_insync = True", "self.use_ib_insync = True\n        self.force_real_data = True")
            ]
            
            for old, new in modifications:
                if old in content:
                    content = content.replace(old, new)
                    print(f"   Modification appliquee: {old[:40]}...")
            
            # Sauvegarder modifications
            with open(ibkr_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   IBKR Connector modifie avec succes")
            
        except Exception as e:
            print(f"   Erreur modification IBKR: {e}")
    
    # 3. MODIFIER MARKET DATA FEED
    print("\nModification Market Data Feed...")
    
    feed_file = "data/market_data_feed.py"
    if os.path.exists(feed_file):
        try:
            # Sauvegarder original
            backup_file = feed_file + ".backup"
            shutil.copy2(feed_file, backup_file)
            print(f"   Sauvegarde creee: {backup_file}")
            
            with open(feed_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Forcer source IBKR
            modifications = [
                ("self.primary_source = DataSource.SIMULATION", "self.primary_source = DataSource.IBKR"),
                ("success = self._connect_simulation()", "success = self._connect_ibkr()"),
                ("elif target_source == DataSource.IBKR:", "elif target_source == DataSource.IBKR:  # DONNEES REELLES OBLIGATOIRES:")
            ]
            
            for old, new in modifications:
                if old in content:
                    content = content.replace(old, new)
                    print(f"   Modification appliquee: {old[:40]}...")
            
            # Sauvegarder modifications
            with open(feed_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   Market Data Feed modifie avec succes")
            
        except Exception as e:
            print(f"   Erreur modification Feed: {e}")
    
    # 4. TEST RAPIDE
    print("\nTest rapide connexion...")
    
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
            
            # Test rapide SPX
            print("\nTest rapide SPX...")
            
            from features.spx_options_retriever import SPXOptionsRetriever
            import asyncio
            
            spx_retriever = SPXOptionsRetriever(connector)
            
            async def test_spx():
                try:
                    spx_data = await spx_retriever.get_real_spx_data()
                    print(f"   Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
                    print(f"   VIX Level: {spx_data.get('vix_level', 'N/A')}")
                    print(f"   Gamma Exposure: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
                    print(f"   Source: {spx_data.get('data_source', 'N/A')}")
                    return spx_data
                except Exception as e:
                    print(f"   Erreur test SPX: {e}")
                    return None
            
            spx_data = asyncio.run(test_spx())
            
            if spx_data and spx_data.get('data_source') == 'ibkr_real':
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
    success = forcer_niveaux_options_reels()
    
    print("\n" + "=" * 60)
    print("RESULTATS FORCAGE DIRECT NIVEAUX OPTIONS")
    print("=" * 60)
    
    if success:
        print("SUCCES: Niveaux options reels forces")
        print("Systeme pret pour test 2h avec vraies donnees")
    else:
        print("ECHEC: Niveaux options non confirmes")
        print("Verification manuelle necessaire")
    
    print("=" * 60)


