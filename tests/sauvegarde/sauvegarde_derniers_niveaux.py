#!/usr/bin/env python3
"""
SAUVEGARDE DERNIERS NIVEAUX CSV
MIA_IA_SYSTEM - Sauvegarde avant session US
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

def sauvegarde_derniers_niveaux():
    """Sauvegarde les derniers niveaux CSV"""
    
    print("💾 SAUVEGARDE DERNIERS NIVEAUX CSV")
    print("=" * 40)
    
    # Répertoires source
    repertoires_source = [
        "data/live/current_session/",
        "data/snapshots/",
        "data/processed/",
        "data/ml_processed/",
        "data/options_snapshots/"
    ]
    
    # Répertoire de sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"data/backups/derniers_niveaux_{timestamp}/"
    
    print(f"📁 Sauvegarde vers: {backup_dir}")
    
    try:
        # Créer répertoire de sauvegarde
        os.makedirs(backup_dir, exist_ok=True)
        
        fichiers_sauvegardes = []
        
        for source_dir in repertoires_source:
            if os.path.exists(source_dir):
                print(f"\n📂 Sauvegarde: {source_dir}")
                
                # Créer sous-répertoire
                dir_name = os.path.basename(source_dir.rstrip('/'))
                backup_subdir = os.path.join(backup_dir, dir_name)
                os.makedirs(backup_subdir, exist_ok=True)
                
                # Copier fichiers CSV
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith('.csv'):
                            source_file = os.path.join(root, file)
                            relative_path = os.path.relpath(source_file, source_dir)
                            dest_file = os.path.join(backup_subdir, relative_path)
                            
                            # Créer répertoires parents si nécessaire
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            
                            # Copier fichier
                            shutil.copy2(source_file, dest_file)
                            fichiers_sauvegardes.append(dest_file)
                            print(f"   ✅ {file}")
        
        print(f"\n🎉 SAUVEGARDE TERMINÉE!")
        print(f"📊 {len(fichiers_sauvegardes)} fichiers sauvegardés")
        print(f"📁 Répertoire: {backup_dir}")
        
        # Créer fichier de métadonnées
        metadata_file = os.path.join(backup_dir, "metadata.txt")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"SAUVEGARDE DERNIERS NIVEAUX CSV\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Session: Avant US\n")
            f.write(f"Fichiers: {len(fichiers_sauvegardes)}\n\n")
            f.write("Fichiers sauvegardés:\n")
            for file in fichiers_sauvegardes:
                f.write(f"- {file}\n")
        
        return backup_dir, len(fichiers_sauvegardes)
        
    except Exception as e:
        print(f"❌ ERREUR SAUVEGARDE: {e}")
        return None, 0

def verifier_sauvegarde(backup_dir):
    """Vérifier la sauvegarde"""
    if not backup_dir or not os.path.exists(backup_dir):
        print("❌ SAUVEGARDE ÉCHOUÉE")
        return False
    
    # Compter fichiers CSV
    csv_count = 0
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_count += 1
    
    print(f"✅ SAUVEGARDE VÉRIFIÉE")
    print(f"📊 {csv_count} fichiers CSV sauvegardés")
    return csv_count > 0

if __name__ == "__main__":
    print("💾 SAUVEGARDE AVANT SESSION US")
    print("=" * 40)
    
    # Sauvegarde
    backup_dir, file_count = sauvegarde_derniers_niveaux()
    
    if backup_dir:
        # Vérification
        print("\n🔍 VÉRIFICATION SAUVEGARDE...")
        success = verifier_sauvegarde(backup_dir)
        
        if success:
            print("\n🎉 PRÊT POUR SESSION US!")
            print("📋 Prochaines étapes:")
            print("   1. Lancer lance_collecte_session_us.py")
            print("   2. Collecter données ES réelles")
            print("   3. Analyser OrderFlow")
            print("   4. Préparer trading session Asie/Londres")
        else:
            print("\n⚠️ Vérifier la sauvegarde")
    else:
        print("\n❌ ÉCHEC SAUVEGARDE")
        print("Vérifier les permissions et l'espace disque")
























