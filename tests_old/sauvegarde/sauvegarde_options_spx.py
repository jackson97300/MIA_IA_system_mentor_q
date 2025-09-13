#!/usr/bin/env python3
"""
SAUVEGARDE OPTIONS SPX - NIVEAUX CRITIQUES
MIA_IA_SYSTEM - Sauvegarde données options SPX avant session US
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
import asyncio
import sys

sys.path.append(str(Path(__file__).parent))

from features.spx_options_retriever import create_spx_options_retriever
from core.ibkr_connector import IBKRConnector

def sauvegarde_options_spx():
    """Sauvegarde les données options SPX critiques"""
    
    print("📊 SAUVEGARDE OPTIONS SPX - NIVEAUX CRITIQUES")
    print("=" * 50)
    
    # Répertoires options SPX
    repertoires_options = [
        "data/options_snapshots/",
        "data/snapshots/options/",
        "data/ml/options_data/",
        "data/processed/options/"
    ]
    
    # Répertoire de sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"data/backups/options_spx_{timestamp}/"
    
    print(f"📁 Sauvegarde vers: {backup_dir}")
    
    try:
        # Créer répertoire de sauvegarde
        os.makedirs(backup_dir, exist_ok=True)
        
        fichiers_sauvegardes = []
        
        for source_dir in repertoires_options:
            if os.path.exists(source_dir):
                print(f"\n📂 Sauvegarde: {source_dir}")
                
                # Créer sous-répertoire
                dir_name = os.path.basename(source_dir.rstrip('/'))
                backup_subdir = os.path.join(backup_dir, dir_name)
                os.makedirs(backup_subdir, exist_ok=True)
                
                # Copier fichiers options
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.csv', '.json', '.pkl')):
                            source_file = os.path.join(root, file)
                            relative_path = os.path.relpath(source_file, source_dir)
                            dest_file = os.path.join(backup_subdir, relative_path)
                            
                            # Créer répertoires parents si nécessaire
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            
                            # Copier fichier
                            shutil.copy2(source_file, dest_file)
                            fichiers_sauvegardes.append(dest_file)
                            print(f"   ✅ {file}")
        
        print(f"\n🎉 SAUVEGARDE OPTIONS TERMINÉE!")
        print(f"📊 {len(fichiers_sauvegardes)} fichiers sauvegardés")
        print(f"📁 Répertoire: {backup_dir}")
        
        # Créer fichier de métadonnées
        metadata_file = os.path.join(backup_dir, "metadata_options.txt")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"SAUVEGARDE OPTIONS SPX - NIVEAUX CRITIQUES\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Session: Avant US\n")
            f.write(f"Fichiers: {len(fichiers_sauvegardes)}\n\n")
            f.write("Données Options SPX Sauvegardées:\n")
            f.write("- Gamma Exposure\n")
            f.write("- Call/Put Walls\n")
            f.write("- Gamma Flip Levels\n")
            f.write("- VIX Data\n")
            f.write("- Put/Call Ratios\n")
            f.write("- Pin Risk Levels\n")
            f.write("- Dealer Positioning\n\n")
            f.write("Fichiers sauvegardés:\n")
            for file in fichiers_sauvegardes:
                f.write(f"- {file}\n")
        
        return backup_dir, len(fichiers_sauvegardes)
        
    except Exception as e:
        print(f"❌ ERREUR SAUVEGARDE OPTIONS: {e}")
        return None, 0

async def collecte_derniers_niveaux_options():
    """Collecte les derniers niveaux options SPX via TWS"""
    
    print("\n📊 COLLECTE DERNIERS NIVEAUX OPTIONS SPX")
    print("=" * 45)
    
    # Configuration TWS
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,  # TWS
        'ibkr_client_id': 1,  # Client ID fonctionnel
        'connection_timeout': 30,
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True
    }
    
    try:
        # Connexion TWS
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            print("✅ CONNEXION TWS RÉUSSIE!")
            
            # Créer SPX Options Retriever
            spx_retriever = create_spx_options_retriever(connector)
            
            # Récupérer données SPX réelles
            print("📊 Récupération données SPX réelles...")
            spx_data = await spx_retriever.get_real_spx_data()
            
            if spx_data:
                print("✅ DONNÉES SPX RÉCUPÉRÉES!")
                print(f"   📈 VIX: {spx_data.get('vix_level', 'N/A')}")
                print(f"   ⚖️ Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
                print(f"   🏗️ Gamma Exposure: ${spx_data.get('total_gamma_exposure', 0)/1e9:.1f}B")
                print(f"   🔄 Gamma Flip: {spx_data.get('gamma_flip_level', 'N/A')}")
                print(f"   🎯 Call Wall: {spx_data.get('call_wall', 'N/A')}")
                print(f"   🎯 Put Wall: {spx_data.get('put_wall', 'N/A')}")
                
                # Sauvegarder automatiquement
                await spx_retriever._save_spx_data_automatically(spx_data)
                print("💾 Données SPX sauvegardées automatiquement")
                
            else:
                print("⚠️ Pas de données SPX récupérées")
            
            # Déconnexion
            await connector.disconnect()
            
        else:
            print("❌ ÉCHEC CONNEXION TWS")
            
    except Exception as e:
        print(f"❌ ERREUR COLLECTE OPTIONS: {e}")

def verifier_sauvegarde_options(backup_dir):
    """Vérifier la sauvegarde options"""
    if not backup_dir or not os.path.exists(backup_dir):
        print("❌ SAUVEGARDE OPTIONS ÉCHOUÉE")
        return False
    
    # Compter fichiers options
    options_count = 0
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            if file.endswith(('.csv', '.json', '.pkl')):
                options_count += 1
    
    print(f"✅ SAUVEGARDE OPTIONS VÉRIFIÉE")
    print(f"📊 {options_count} fichiers options sauvegardés")
    return options_count > 0

if __name__ == "__main__":
    print("📊 SAUVEGARDE OPTIONS SPX AVANT SESSION US")
    print("=" * 50)
    
    # Sauvegarde fichiers existants
    backup_dir, file_count = sauvegarde_options_spx()
    
    if backup_dir:
        # Vérification
        print("\n🔍 VÉRIFICATION SAUVEGARDE OPTIONS...")
        success = verifier_sauvegarde_options(backup_dir)
        
        if success:
            print("\n📊 COLLECTE DERNIERS NIVEAUX...")
            # Collecte derniers niveaux via TWS
            asyncio.run(collecte_derniers_niveaux_options())
            
            print("\n🎉 OPTIONS SPX PRÊTES POUR SESSION US!")
            print("📋 Niveaux critiques sauvegardés:")
            print("   - Gamma Exposure")
            print("   - Call/Put Walls")
            print("   - Gamma Flip Levels")
            print("   - VIX Data")
            print("   - Pin Risk Levels")
            print("   - Dealer Positioning")
        else:
            print("\n⚠️ Vérifier la sauvegarde options")
    else:
        print("\n❌ ÉCHEC SAUVEGARDE OPTIONS")
        print("Vérifier les permissions et l'espace disque")
























