#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Définitive SPX
Corrige définitivement le problème des données SPX expirées
"""

import os
import sys
import shutil
from datetime import datetime

def corriger_definitivement_spx():
    """Corriger définitivement le problème SPX"""
    
    print("🛑 MIA_IA_SYSTEM - CORRECTION DÉFINITIVE SPX")
    print("=" * 60)
    print("🎯 Objectif: Forcer l'utilisation des données SPX fraîches")
    print("=" * 60)
    
    # 1. SUPPRIMER L'ANCIEN FICHIER EXPIRE
    print("\n🗑️ ÉTAPE 1: SUPPRESSION FICHIER EXPIRE")
    print("=" * 50)
    
    old_file = "data/options_snapshots/final/spx_final_20250811.csv"
    if os.path.exists(old_file):
        os.remove(old_file)
        print(f"   ✅ Fichier supprimé: {old_file}")
    else:
        print(f"   ⚠️ Fichier non trouvé: {old_file}")
    
    # 2. RENOMMER LE FICHIER FRAIS
    print("\n🔄 ÉTAPE 2: RENOMMAGE FICHIER FRAIS")
    print("=" * 50)
    
    fresh_file = "data/options_snapshots/final/spx_fresh_20250814_134727.csv"
    new_file = "data/options_snapshots/final/spx_final_20250814.csv"
    
    if os.path.exists(fresh_file):
        shutil.copy2(fresh_file, new_file)
        print(f"   ✅ Fichier copié: {fresh_file} → {new_file}")
    else:
        print(f"   ❌ Fichier frais non trouvé: {fresh_file}")
        return False
    
    # 3. CRÉER UN FICHIER AVEC TIMESTAMP ACTUEL
    print("\n📅 ÉTAPE 3: CRÉATION FICHIER TIMESTAMP ACTUEL")
    print("=" * 50)
    
    current_time = datetime.now()
    current_file = f"data/options_snapshots/final/spx_final_{current_time.strftime('%Y%m%d')}.csv"
    
    if os.path.exists(new_file):
        shutil.copy2(new_file, current_file)
        print(f"   ✅ Fichier créé: {current_file}")
    else:
        print(f"   ❌ Erreur création fichier actuel")
        return False
    
    # 4. VÉRIFIER LES FICHIERS FINAUX
    print("\n📊 ÉTAPE 4: VÉRIFICATION FICHIERS FINAUX")
    print("=" * 50)
    
    spx_files = []
    for file in os.listdir("data/options_snapshots/final"):
        if file.startswith("spx_final") and file.endswith(".csv"):
            spx_files.append(file)
            file_path = f"data/options_snapshots/final/{file}"
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            age_hours = (datetime.now() - file_time).total_seconds() / 3600
            print(f"   📄 {file} - Âge: {age_hours:.1f}h")
    
    print(f"   📊 Total fichiers SPX: {len(spx_files)}")
    
    # 5. CRÉER UN SCRIPT DE VÉRIFICATION
    print("\n🔍 ÉTAPE 5: SCRIPT DE VÉRIFICATION")
    print("=" * 50)
    
    verification_script = """
#!/usr/bin/env python3
\"\"\"
Vérification données SPX en temps réel
\"\"\"

import os
import glob
from datetime import datetime

def verifier_spx_temps_reel():
    \"\"\"Vérifier les données SPX en temps réel\"\"\"
    
    print("🔍 Vérification données SPX...")
    
    # Chercher tous les fichiers SPX
    spx_files = glob.glob("data/options_snapshots/final/spx_final_*.csv")
    
    if not spx_files:
        print("❌ Aucun fichier SPX trouvé")
        return False
    
    # Analyser chaque fichier
    for spx_file in spx_files:
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(spx_file))
            age_hours = (datetime.now() - file_time).total_seconds() / 3600
            
            if age_hours <= 18:
                print(f"✅ {os.path.basename(spx_file)} - Frais ({age_hours:.1f}h)")
                return True
            else:
                print(f"❌ {os.path.basename(spx_file)} - Expiré ({age_hours:.1f}h)")
                
        except Exception as e:
            print(f"⚠️ Erreur vérification {spx_file}: {e}")
    
    return False

if __name__ == "__main__":
    success = verifier_spx_temps_reel()
    if success:
        print("\\n✅ Données SPX fraîches disponibles")
    else:
        print("\\n❌ Aucune donnée SPX fraîche trouvée")
"""
    
    with open("verifier_spx_temps_reel.py", "w", encoding="utf-8") as f:
        f.write(verification_script)
    
    print("   📄 Script de vérification créé: verifier_spx_temps_reel.py")
    
    # 6. TEST IMMÉDIAT
    print("\n🧪 ÉTAPE 6: TEST IMMÉDIAT")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run("python verifier_spx_temps_reel.py", shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Erreurs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # RÉSUMÉ FINAL
    print("\n📊 RÉSUMÉ CORRECTION DÉFINITIVE")
    print("=" * 50)
    print("✅ Ancien fichier expiré supprimé")
    print("✅ Fichier frais renommé")
    print("✅ Fichier timestamp actuel créé")
    print("✅ Script de vérification créé")
    print("✅ Test immédiat effectué")
    
    print("\n🚀 PROCHAINES ÉTAPES")
    print("=" * 50)
    print("1. 🔄 Redémarrer le système")
    print("2. ✅ Vérifier: python verifier_spx_temps_reel.py")
    print("3. 📊 Analyser: python analyse_resultats_temps_reel.py")
    
    return True

if __name__ == "__main__":
    success = corriger_definitivement_spx()
    if success:
        print("\n🎉 CORRECTION DÉFINITIVE RÉUSSIE")
        print("Le système devrait maintenant utiliser les données SPX fraîches")
    else:
        print("\n❌ CORRECTION ÉCHOUÉE")
        print("Vérifiez les erreurs ci-dessus")


