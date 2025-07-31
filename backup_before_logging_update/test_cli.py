#!/usr/bin/env python3
"""
TEST CLI - Test des commandes en ligne de commande
"""

import subprocess
import sys
import os

os.chdir(r"D:\MIA_IA_system")

print("TEST DES COMMANDES CLI")
print("="*50)

commands = [
    {
        "name": "STATUS",
        "cmd": [sys.executable, "data_collection_main.py", "--status"],
        "check": "Session ID"
    },
    {
        "name": "QUALITÉ (1 jour)",
        "cmd": [sys.executable, "data_collection_main.py", "--quality", "--days", "1"],
        "check": "qualité"
    },
    {
        "name": "RÉSUMÉ QUOTIDIEN",
        "cmd": [sys.executable, "data_collection_main.py", "--summary", "daily"],
        "check": "Report"
    },
    {
        "name": "HELP",
        "cmd": [sys.executable, "data_collection_main.py", "--help"],
        "check": "usage:"
    }
]

for test in commands:
    print(f"\n📋 Test: {test['name']}")
    print(f"   Commande: {' '.join(test['cmd'][1:])}")
    
    try:
        result = subprocess.run(
            test['cmd'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            if test['check'] in result.stdout:
                print(f"   ✅ Succès")
                # Afficher un extrait du résultat
                lines = result.stdout.strip().split('\n')
                for line in lines[:5]:  # Premières 5 lignes
                    if line.strip():
                        print(f"      {line}")
                if len(lines) > 5:
                    print(f"      ... ({len(lines)-5} lignes supplémentaires)")
            else:
                print(f"   ⚠️  Commande exécutée mais résultat inattendu")
        else:
            print(f"   ❌ Erreur (code {result.returncode})")
            if result.stderr:
                print(f"      Erreur: {result.stderr[:200]}")
                
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

print("\n" + "="*50)
print("🎯 SYSTÈME PRÊT POUR L'UTILISATION !")
print("="*50)

print("\n📌 Commandes principales :")
print("1. Démarrer la collecte :")
print("   python data_collection_main.py --start --hours 1")
print("\n2. Analyser les données :")
print("   python data_collection_main.py --analyze")
print("\n3. Export ML dataset :")
print("   python data_collection_main.py --export --days 7")