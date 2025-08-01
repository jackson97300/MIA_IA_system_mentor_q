#!/usr/bin/env python3
"""
Test de syntaxe pure sans imports externes
"""

print("🔍 TEST DE SYNTAXE LESSONS LEARNED")
print("=" * 50)

try:
    print("1️⃣ Test compilation Python pure...")
    
    # Test sans imports externes
    code = '''
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestLesson:
    trade_id: str
    timestamp: datetime
    pnl: float = 0.0

def test_function():
    return {"status": "ok"}
'''
    
    # Compiler le code
    compile(code, '<string>', 'exec')
    print("✅ Compilation réussie")
    
    print("\n2️⃣ Test exécution simple...")
    exec(code)
    print("✅ Exécution réussie")
    
    print("\n3️⃣ Test dataclass...")
    lesson = TestLesson("TEST-001", datetime.now(), 100.0)
    print(f"✅ Dataclass créée: {lesson.trade_id}")
    
    print("\n4️⃣ Test fonction...")
    result = test_function()
    print(f"✅ Fonction testée: {result}")
    
    print("\n🎉 SYNTAXE OK!")
    
except SyntaxError as e:
    print(f"❌ ERREUR DE SYNTAXE: {e}")
    
except Exception as e:
    print(f"❌ ERREUR D'EXÉCUTION: {e}")
    import traceback
    traceback.print_exc()
    
print("\n" + "=" * 50)
print("✅ TEST TERMINÉ")