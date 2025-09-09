#!/usr/bin/env python3
"""
SAUVEGARDE NIVEAUX OPTIONS SPX - DÉTAILLÉ
MIA_IA_SYSTEM - Sauvegarde complète avant session US
"""
import os
import shutil
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import sys

sys.path.append(str(Path(__file__).parent))

from features.spx_options_retriever import create_spx_options_retriever
from core.ibkr_connector import IBKRConnector

class SauvegardeOptionsSPX:
    """Sauvegarde détaillée des niveaux options SPX"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.backup_dir = f"data/backups/options_spx_{self.timestamp.strftime('%Y%m%d_%H%M%S')}/"
        
    def sauvegarde_fichiers_existants(self):
        """Sauvegarde tous les fichiers options existants"""
        print("📊 SAUVEGARDE FICHIERS OPTIONS EXISTANTS")
        print("=" * 50)
        
        repertoires_options = [
            "data/options_snapshots/",
            "data/snapshots/options/",
            "data/ml/options_data/",
            "data/processed/options/",
            "data/live/current_session/options/",
            "data/performance/options/"
        ]
        
        fichiers_sauvegardes = []
        
        for source_dir in repertoires_options:
            if os.path.exists(source_dir):
                print(f"\n📂 Sauvegarde: {source_dir}")
                
                # Créer sous-répertoire
                dir_name = os.path.basename(source_dir.rstrip('/'))
                backup_subdir = os.path.join(self.backup_dir, dir_name)
                os.makedirs(backup_subdir, exist_ok=True)
                
                # Copier fichiers
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.csv', '.json', '.pkl', '.txt')):
                            source_file = os.path.join(root, file)
                            relative_path = os.path.relpath(source_file, source_dir)
                            dest_file = os.path.join(backup_subdir, relative_path)
                            
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            shutil.copy2(source_file, dest_file)
                            fichiers_sauvegardes.append(dest_file)
                            print(f"   ✅ {file}")
        
        return fichiers_sauvegardes
    
    async def collecte_derniers_niveaux_reels(self):
        """Collecte les derniers niveaux options SPX réels via IB Gateway"""
        print("\n📊 COLLECTE DERNIERS NIVEAUX RÉELS")
        print("=" * 40)
        
        # Configuration IB Gateway
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 4002,
            'ibkr_client_id': 1,
            'connection_timeout': 30,
            'simulation_mode': False,
            'require_real_data': True,
            'use_ib_insync': True
        }
        
        try:
            # Connexion IB Gateway
            connector = IBKRConnector(config)
            success = await connector.connect()
            
            if success:
                print("✅ CONNEXION IB GATEWAY RÉUSSIE!")
                
                # Créer SPX Options Retriever
                spx_retriever = create_spx_options_retriever(connector)
                
                # Récupérer données SPX réelles
                print("📊 Récupération données SPX réelles...")
                spx_data = await spx_retriever.get_real_spx_data()
                
                if spx_data:
                    print("✅ DONNÉES SPX RÉCUPÉRÉES!")
                    
                    # Afficher niveaux critiques
                    self._afficher_niveaux_critiques(spx_data)
                    
                    # Sauvegarder données réelles
                    await self._sauvegarder_donnees_reelles(spx_data)
                    
                    # Sauvegarder automatiquement
                    await spx_retriever._save_spx_data_automatically(spx_data)
                    print("💾 Données SPX sauvegardées automatiquement")
                    
                else:
                    print("⚠️ Pas de données SPX récupérées")
                
                # Déconnexion
                await connector.disconnect()
                
            else:
                print("❌ ÉCHEC CONNEXION IB GATEWAY")
                
        except Exception as e:
            print(f"❌ ERREUR COLLECTE OPTIONS: {e}")
    
    def _afficher_niveaux_critiques(self, spx_data):
        """Affiche les niveaux options critiques"""
        print("\n🎯 NIVEAUX OPTIONS CRITIQUES:")
        print("-" * 30)
        print(f"📈 VIX Level: {spx_data.get('vix_level', 'N/A')}")
        print(f"⚖️ Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
        print(f"🏗️ Gamma Exposure: ${spx_data.get('total_gamma_exposure', 0)/1e9:.1f}B")
        print(f"🔄 Gamma Flip Level: {spx_data.get('gamma_flip_level', 'N/A')}")
        print(f"🎯 Call Wall: {spx_data.get('call_wall', 'N/A')}")
        print(f"🎯 Put Wall: {spx_data.get('put_wall', 'N/A')}")
        print(f"📊 Dealer Position: {spx_data.get('dealer_position', 'N/A')}")
        print(f"🎯 Pin Levels: {spx_data.get('pin_levels', 'N/A')}")
    
    async def _sauvegarder_donnees_reelles(self, spx_data):
        """Sauvegarde les données réelles dans le backup"""
        real_data_file = os.path.join(self.backup_dir, "spx_real_data.json")
        
        # Ajouter métadonnées
        spx_data['backup_timestamp'] = self.timestamp.isoformat()
        spx_data['session'] = 'BEFORE_US'
        spx_data['source'] = 'IB_GATEWAY'
        
        with open(real_data_file, 'w', encoding='utf-8') as f:
            json.dump(spx_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données réelles sauvegardées: {real_data_file}")
    
    def creer_metadata_complete(self, fichiers_sauvegardes):
        """Crée un fichier de métadonnées complet"""
        metadata_file = os.path.join(self.backup_dir, "metadata_complete.txt")
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("SAUVEGARDE NIVEAUX OPTIONS SPX - COMPLÈTE\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Session: Avant US\n")
            f.write(f"Fichiers: {len(fichiers_sauvegardes)}\n\n")
            
            f.write("NIVEAUX OPTIONS CRITIQUES SAUVEGARDÉS:\n")
            f.write("-" * 40 + "\n")
            f.write("🏗️ Gamma Exposure (Exposition gamma totale)\n")
            f.write("🎯 Call/Put Walls (Murs call/put)\n")
            f.write("🔄 Gamma Flip Levels (Niveaux flip gamma)\n")
            f.write("📈 VIX Data (Données volatilité)\n")
            f.write("⚖️ Put/Call Ratios (Ratios put/call)\n")
            f.write("🎯 Pin Risk Levels (Niveaux pin risk)\n")
            f.write("🏦 Dealer Positioning (Positionnement dealers)\n")
            f.write("📊 Options Chain Data (Données chaîne options)\n")
            f.write("🎯 Max Pain Levels (Niveaux max pain)\n")
            f.write("📈 Term Structure (Structure temporelle)\n\n")
            
            f.write("UTILISATION POUR SESSIONS ASIA/LONDON:\n")
            f.write("-" * 40 + "\n")
            f.write("1. Analyse niveaux gamma avant ouverture\n")
            f.write("2. Identification zones de résistance/support\n")
            f.write("3. Calcul biais gamma (bullish/bearish)\n")
            f.write("4. Détection pin risk potentiels\n")
            f.write("5. Optimisation timing d'entrée\n")
            f.write("6. Gestion risque selon dealer positioning\n\n")
            
            f.write("FICHIERS SAUVEGARDÉS:\n")
            f.write("-" * 20 + "\n")
            for file in fichiers_sauvegardes:
                f.write(f"- {file}\n")
        
        print(f"📋 Métadonnées complètes: {metadata_file}")

async def main():
    """Fonction principale"""
    print("📊 SAUVEGARDE NIVEAUX OPTIONS SPX - DÉTAILLÉE")
    print("=" * 60)
    
    # Créer sauvegarde
    sauvegarde = SauvegardeOptionsSPX()
    
    # Créer répertoire de sauvegarde
    os.makedirs(sauvegarde.backup_dir, exist_ok=True)
    print(f"📁 Sauvegarde vers: {sauvegarde.backup_dir}")
    
    # Sauvegarde fichiers existants
    fichiers_sauvegardes = sauvegarde.sauvegarde_fichiers_existants()
    
    # Collecte derniers niveaux réels
    await sauvegarde.collecte_derniers_niveaux_reels()
    
    # Créer métadonnées
    sauvegarde.creer_metadata_complete(fichiers_sauvegardes)
    
    print(f"\n🎉 SAUVEGARDE OPTIONS SPX TERMINÉE!")
    print(f"📊 {len(fichiers_sauvegardes)} fichiers sauvegardés")
    print(f"📁 Répertoire: {sauvegarde.backup_dir}")
    print("\n📋 Niveaux critiques sauvegardés pour sessions Asia/London")

if __name__ == "__main__":
    asyncio.run(main())























