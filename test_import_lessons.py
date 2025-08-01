#!/usr/bin/env python3
"""
Test minimal d'import du module lessons_learned_analyzer
"""

print("🧪 TEST IMPORT LESSONS LEARNED")
print("=" * 50)

try:
    print("1️⃣ Import des modules de base...")
    import os
    import sys
    from pathlib import Path
    print("✅ Modules de base importés")
    
    print("\n2️⃣ Import du logger...")
    from core.logger import get_logger
    logger = get_logger(__name__)
    print("✅ Logger importé")
    
    print("\n3️⃣ Import lessons_learned_analyzer...")
    from core.lessons_learned_analyzer import create_lessons_learned_analyzer, TradeLesson
    print("✅ LessonsLearnedAnalyzer importé")
    
    print("\n4️⃣ Création d'une instance...")
    analyzer = create_lessons_learned_analyzer()
    print("✅ Instance créée")
    
    print("\n5️⃣ Test méthodes simples...")
    progress = analyzer.get_progress_to_target()
    print(f"✅ Progrès: {progress['current_trades']}/{progress['target_trades']}")
    
    print("\n🎉 TOUS LES IMPORTS RÉUSSIS!")
    
except ImportError as e:
    print(f"❌ ERREUR D'IMPORT: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"❌ ERREUR AUTRE: {e}")
    import traceback
    traceback.print_exc()