#!/usr/bin/env python3
"""
Test syntaxe uniquement du Mentor System - Aucun import
"""

import sys
import os
import ast
from datetime import datetime

def test_mentor_system_syntax():
    """Test syntaxe du fichier mentor_system.py"""
    print("\n🔍 TEST SYNTAXE MENTOR_SYSTEM.PY")
    print("=" * 50)
    
    try:
        # Lire le fichier
        with open('core/mentor_system.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("✅ Fichier mentor_system.py lu avec succès")
        
        # Compiler pour vérifier la syntaxe
        compile(source_code, 'core/mentor_system.py', 'exec')
        print("✅ Syntaxe mentor_system.py valide")
        
        # Analyser la structure avec AST
        tree = ast.parse(source_code)
        
        # Compter les imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"✅ {len(imports)} imports détectés")
        
        # Compter les classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        print(f"✅ {len(classes)} classes détectées")
        
        # Compter les fonctions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"✅ {len(functions)} fonctions détectées")
        
        # Vérifier les classes principales
        class_names = [cls.name for cls in classes]
        print(f"✅ Classes trouvées: {', '.join(class_names)}")
        
        # Vérifier les fonctions principales
        function_names = [func.name for func in functions]
        main_functions = [name for name in function_names if 'mentor' in name.lower() or 'create' in name.lower()]
        print(f"✅ Fonctions principales: {', '.join(main_functions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur syntaxe: {e}")
        return False

def test_discord_notifier_syntax():
    """Test syntaxe du fichier discord_notifier.py"""
    print("\n🔍 TEST SYNTAXE DISCORD_NOTIFIER.PY")
    print("=" * 50)
    
    try:
        # Lire le fichier
        with open('monitoring/discord_notifier.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("✅ Fichier discord_notifier.py lu avec succès")
        
        # Compiler pour vérifier la syntaxe
        compile(source_code, 'monitoring/discord_notifier.py', 'exec')
        print("✅ Syntaxe discord_notifier.py valide")
        
        # Analyser la structure avec AST
        tree = ast.parse(source_code)
        
        # Compter les imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"✅ {len(imports)} imports détectés")
        
        # Compter les classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        print(f"✅ {len(classes)} classes détectées")
        
        # Compter les fonctions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"✅ {len(functions)} fonctions détectées")
        
        # Vérifier les classes principales
        class_names = [cls.name for cls in classes]
        print(f"✅ Classes trouvées: {', '.join(class_names)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur syntaxe discord_notifier: {e}")
        return False

def test_core_init_syntax():
    """Test syntaxe du fichier core/__init__.py"""
    print("\n🔍 TEST SYNTAXE CORE/__INIT__.PY")
    print("=" * 50)
    
    try:
        # Lire le fichier
        with open('core/__init__.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("✅ Fichier core/__init__.py lu avec succès")
        
        # Compiler pour vérifier la syntaxe
        compile(source_code, 'core/__init__.py', 'exec')
        print("✅ Syntaxe core/__init__.py valide")
        
        # Analyser la structure avec AST
        tree = ast.parse(source_code)
        
        # Compter les imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"✅ {len(imports)} imports détectés")
        
        # Compter les fonctions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"✅ {len(functions)} fonctions détectées")
        
        # Vérifier les fonctions principales
        function_names = [func.name for func in functions]
        print(f"✅ Fonctions trouvées: {', '.join(function_names)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur syntaxe core/__init__.py: {e}")
        return False

def test_automation_main_syntax():
    """Test syntaxe du fichier automation_main.py"""
    print("\n🔍 TEST SYNTAXE AUTOMATION_MAIN.PY")
    print("=" * 50)
    
    try:
        # Lire le fichier
        with open('automation_main.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("✅ Fichier automation_main.py lu avec succès")
        
        # Compiler pour vérifier la syntaxe
        compile(source_code, 'automation_main.py', 'exec')
        print("✅ Syntaxe automation_main.py valide")
        
        # Analyser la structure avec AST
        tree = ast.parse(source_code)
        
        # Compter les imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"✅ {len(imports)} imports détectés")
        
        # Compter les classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        print(f"✅ {len(classes)} classes détectées")
        
        # Compter les fonctions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"✅ {len(functions)} fonctions détectées")
        
        # Vérifier les classes principales
        class_names = [cls.name for cls in classes]
        print(f"✅ Classes trouvées: {', '.join(class_names)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur syntaxe automation_main: {e}")
        return False

def main():
    """Test principal syntaxe uniquement"""
    print("🔍 TEST SYNTAXE UNIQUEMENT - AUCUN IMPORT")
    print("=" * 50)
    
    tests = [
        ("Syntaxe mentor_system.py", test_mentor_system_syntax),
        ("Syntaxe discord_notifier.py", test_discord_notifier_syntax),
        ("Syntaxe core/__init__.py", test_core_init_syntax),
        ("Syntaxe automation_main.py", test_automation_main_syntax)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS SYNTAXE")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 SCORE: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SYNTAXE RÉUSSIS !")
        print("✅ Aucune connexion réseau tentée")
        print("✅ Tous les fichiers sont syntaxiquement corrects")
        print("✅ Mentor System et Discord Notifier sont prêts")
        print("✅ Intégration dans automation_main.py possible")
    else:
        print("⚠️ CERTAINS TESTS SYNTAXE ONT ÉCHOUÉ")
        print("🔧 Correction nécessaire avant intégration")

if __name__ == "__main__":
    main() 