#!/usr/bin/env python3
"""
Test basique pour vérifier que Python fonctionne
Sans aucune configuration UTF-8 problématique
"""

print("=" * 50)
print("TEST PYTHON BASIQUE")
print("=" * 50)

# Test 1: Print simple
print("\n1. Test print simple: OK")

# Test 2: Import standard
try:
    import sys
    import os
    print("2. Import sys/os: OK")
except Exception as e:
    print(f"2. Import sys/os: ERREUR - {e}")

# Test 3: Logging
try:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("3. Test logging: OK")
except Exception as e:
    print(f"3. Test logging: ERREUR - {e}")

# Test 4: Import pandas
try:
    import pandas as pd
    print("4. Import pandas: OK")
except Exception as e:
    print(f"4. Import pandas: ERREUR - {e}")

# Test 5: Import local simple
try:
    import core
    print("5. Import core: OK")
except Exception as e:
    print(f"5. Import core: ERREUR - {e}")

print("\n" + "=" * 50)
print("Si vous voyez ce message, Python fonctionne!")
print("=" * 50)