#!/usr/bin/env python3
"""
Script pour déplacer les fichiers de configuration obsolètes vers backup
"""

import os
import shutil
from pathlib import Path

def move_obsolete_configs():
    """Déplace les fichiers obsolètes vers config/backup/"""
    
    config_dir = Path("config")
    backup_dir = config_dir / "backup"
    
    # Créer le dossier backup s'il n'existe pas
    backup_dir.mkdir(exist_ok=True)
    
    # Liste des fichiers obsolètes à déplacer
    obsolete_files = [
        # Fichiers backup/anciens
        "feature_calculator.backup_20250701_031129.py",
        
        # Fichiers bypass obsolètes
        "bypass_async_session.json",
        "bypass_direct_session.json", 
        "bypass_final_session.json",
        "bypass_options_patch.py",
        "bypass_options_session.json",
        
        # Doublons features/ (obsolètes dans config/)
        "confluence_analyzer.py",
        "confluence_integrator.py",
        "feature_calculator.py",
        "feature_calculator_integrated.py",
        "enhanced_feature_calculator.py",
        "menthorq_config.py",
        "menthorq_dealers_bias.py",
        "menthorq_es_bridge.py",
        "menthorq_integration.py",
        "menthorq_processor.py",
        "menthorq_runtime.py",
        "menthorq_three_types_integration.py",
        "order_book_imbalance.py",
        "volume_profile_imbalance.py",
        "vwap_bands_analyzer.py",
        "volatility_regime.py",
        "smart_money_tracker.py",
        "mtf_confluence_elite.py",
        
        # Fichiers de développement/test
        "create_real_snapshot.py",
        "create_simulated_snapshot.py",
        "live_leadership_demo.py",
        "live_leadership_integration.py",
        "test_config.json",
        
        # Sessions obsolètes
        "es_real_direct_session.json",
        "es_real_only_session.json",
        "force_trading_session.json",
        "performance_optimized_session.json",
        "real_data_session.json",
        
        # Fichiers redondants
        "market_regime.py",  # doublon avec market_regime_optimized.py
        "es_bias_bridge.py",
        "mia_hybrid_final_plus.py"
    ]
    
    moved_count = 0
    not_found_count = 0
    
    print("🧹 Déplacement des fichiers de configuration obsolètes...")
    print("=" * 60)
    
    for filename in obsolete_files:
        source_path = config_dir / filename
        
        if source_path.exists():
            try:
                destination_path = backup_dir / filename
                shutil.move(str(source_path), str(destination_path))
                print(f"✅ Déplacé: {filename}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Erreur déplacement {filename}: {e}")
        else:
            print(f"⚠️ Non trouvé: {filename}")
            not_found_count += 1
    
    print("=" * 60)
    print(f"📊 Résumé:")
    print(f"   ✅ Fichiers déplacés: {moved_count}")
    print(f"   ⚠️ Fichiers non trouvés: {not_found_count}")
    print(f"   📁 Destination: {backup_dir}")
    
    # Afficher les fichiers restants dans config/
    remaining_files = [f.name for f in config_dir.iterdir() if f.is_file() and f.name != "__init__.py"]
    print(f"\n📋 Fichiers restants dans config/ ({len(remaining_files)}):")
    for filename in sorted(remaining_files):
        print(f"   • {filename}")

if __name__ == "__main__":
    move_obsolete_configs()

