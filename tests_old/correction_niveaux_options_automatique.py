#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Automatique Niveaux Options
Force l'utilisation des niveaux options réels
"""

import os
import sys
import shutil
from datetime import datetime

def corriger_niveaux_options():
    """Correction automatique des niveaux options"""
    
    print("MIA_IA_SYSTEM - CORRECTION AUTOMATIQUE NIVEAUX OPTIONS")
    print("=" * 60)
    print(f"Correction: {datetime.now()}")
    print("=" * 60)
    
    # Liste des fichiers à corriger
    fichiers_a_corriger = [
        'features/spx_options_retriever.py',
        'core/ibkr_connector.py',
        'data/market_data_feed.py',
        'config/automation_config.py',
        'config/mia_ia_system_tws_paper_fixed.py'
    ]
    
    corrections_appliquees = 0
    
    for fichier in fichiers_a_corriger:
        if os.path.exists(fichier):
            print(f"\nCorrection de {fichier}...")
            
            try:
                # Créer backup
                backup_file = f"{fichier}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(fichier, backup_file)
                print(f"   Backup créé: {backup_file}")
                
                # Lire contenu
                with open(fichier, 'r', encoding='utf-8') as f:
                    contenu = f.read()
                
                # Appliquer corrections
                contenu_modifie = contenu
                
                # 1. Forcer données réelles
                contenu_modifie = contenu_modifie.replace(
                    'self.simulation_mode = True',
                    'self.simulation_mode = False'
                )
                contenu_modifie = contenu_modifie.replace(
                    'simulation_mode = True',
                    'simulation_mode = False'
                )
                contenu_modifie = contenu_modifie.replace(
                    'USE_REAL_DATA = False',
                    'USE_REAL_DATA = True'
                )
                contenu_modifie = contenu_modifie.replace(
                    'FORCE_REAL_DATA = False',
                    'FORCE_REAL_DATA = True'
                )
                
                # 2. Forcer source IBKR
                contenu_modifie = contenu_modifie.replace(
                    'DataSource.SIMULATION',
                    'DataSource.IBKR'
                )
                contenu_modifie = contenu_modifie.replace(
                    'data_source = "simulation"',
                    'data_source = "ibkr_real"'
                )
                contenu_modifie = contenu_modifie.replace(
                    'data_source = "saved_data"',
                    'data_source = "ibkr_real"'
                )
                
                # 3. Forcer port TWS
                contenu_modifie = contenu_modifie.replace(
                    'port = 7496',
                    'port = 7497'
                )
                contenu_modifie = contenu_modifie.replace(
                    'port: 7496',
                    'port: 7497'
                )
                
                # 4. Forcer fallback vers données réelles
                contenu_modifie = contenu_modifie.replace(
                    'return self._get_fallback_data()',
                    'return self._get_real_ibkr_data()'
                )
                contenu_modifie = contenu_modifie.replace(
                    'FALLBACK_TO_SIMULATION = True',
                    'FALLBACK_TO_SIMULATION = False'
                )
                
                # 5. Ajouter force_real_data si pas présent
                if 'self.force_real_data = True' not in contenu_modifie:
                    contenu_modifie = contenu_modifie.replace(
                        'self.simulation_mode = False',
                        'self.simulation_mode = False\n        self.force_real_data = True'
                    )
                
                # Écrire modifications
                if contenu_modifie != contenu:
                    with open(fichier, 'w', encoding='utf-8') as f:
                        f.write(contenu_modifie)
                    print(f"   ✅ Corrections appliquées")
                    corrections_appliquees += 1
                else:
                    print(f"   ⚠️ Aucune modification nécessaire")
                    
            except Exception as e:
                print(f"   ❌ Erreur correction: {e}")
        else:
            print(f"\n⚠️ Fichier non trouvé: {fichier}")
    
    print(f"\n" + "=" * 60)
    print("RÉSULTATS CORRECTION")
    print("=" * 60)
    print(f"Corrections appliquées: {corrections_appliquees}")
    
    if corrections_appliquees > 0:
        print("✅ Corrections appliquées avec succès")
        print("🔄 Redémarrage recommandé du système")
        print("🧪 Test recommandé: python test_niveaux_options_simple.py")
    else:
        print("⚠️ Aucune correction appliquée")
        print("🔍 Vérification manuelle recommandée")
    
    print("=" * 60)

def main():
    """Fonction principale"""
    try:
        corriger_niveaux_options()
    except Exception as e:
        print(f"❌ Erreur correction: {e}")

if __name__ == "__main__":
    main()


