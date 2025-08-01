#!/usr/bin/env python3
"""
Test ultra minimal - juste vérifier si Python peut lire le fichier
"""

print("🔎 TEST ULTRA MINIMAL")
print("=" * 30)

try:
    print("1️⃣ Lecture du fichier...")
    with open('core/lessons_learned_analyzer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"✅ Fichier lu: {len(content)} caractères")
    
    print("\n2️⃣ Test compilation...")
    compile(content, 'core/lessons_learned_analyzer.py', 'exec')
    print("✅ Compilation réussie")
    
    print("\n3️⃣ Test imports standards...")
    import json
    import sqlite3
    from datetime import datetime
    print("✅ Imports standards OK")
    
    print("\n🎉 FICHIER VALIDE!")
    
except FileNotFoundError:
    print("❌ Fichier non trouvé")
except SyntaxError as e:
    print(f"❌ ERREUR SYNTAXE: {e}")
except Exception as e:
    print(f"❌ ERREUR: {e}")

print("=" * 30)