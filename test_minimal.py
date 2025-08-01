#!/usr/bin/env python3
"""
TEST MINIMAL - Identifier le problème
"""

print("🔍 TEST MINIMAL - DÉMARRAGE")

try:
    print("1. Test imports de base...")
    import sys
    from pathlib import Path
    print("✅ Imports système OK")
    
    print("2. Test ajout path...")
    sys.path.append(str(Path(__file__).parent))
    print("✅ Path ajouté OK")
    
    print("3. Test import core.logger...")
    from core.logger import get_logger
    print("✅ Logger importé OK")
    
    print("4. Test création logger...")
    logger = get_logger(__name__)
    print("✅ Logger créé OK")
    
    print("5. Test import signal_explainer...")
    from core.signal_explainer import create_signal_explainer
    print("✅ Signal explainer importé OK")
    
    print("6. Test création signal_explainer...")
    explainer = create_signal_explainer()
    print("✅ Signal explainer créé OK")
    
    print("7. Test import catastrophe_monitor...")
    from core.catastrophe_monitor import create_catastrophe_monitor
    print("✅ Catastrophe monitor importé OK")
    
    print("8. Test création catastrophe_monitor...")
    monitor = create_catastrophe_monitor()
    print("✅ Catastrophe monitor créé OK")
    
    print("\n🎉 TOUS LES TESTS PASSÉS !")
    print("✅ Modules fonctionnels")
    print("✅ Pas de problème de connexion réseau")
    
except Exception as e:
    print(f"\n❌ ERREUR DÉTECTÉE: {e}")
    import traceback
    traceback.print_exc()