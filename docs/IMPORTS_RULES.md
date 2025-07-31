# 🚨 RÈGLES D'IMPORTS - GUIDE ANTI-ERREURS

> **CRITICAL** : Ce guide DOIT être suivi pour éviter TOUS les problèmes d'imports

---

## 🎯 RÈGLES D'OR

### RÈGLE #1 : ORDRE STRICT DES IMPORTS
```python
# TOUJOURS dans cet ordre EXACT :

# 1️⃣ STANDARD LIBRARY (Python built-in)
import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# 2️⃣ THIRD-PARTY PACKAGES
import numpy as np
import pandas as pd
from ib_insync import IB, Contract, Order

# 3️⃣ LOCAL IMPORTS (votre projet)
from config.trading_config import TradingConfig
from core.base_types import SignalType, MarketRegime
from features.feature_calculator import FeatureCalculator
```

### RÈGLE #2 : JAMAIS D'IMPORTS RELATIFS
```python
# ❌ INTERDIT
from ..config import trading_config
from . import base_types
from ...features import calculator

# ✅ TOUJOURS ABSOLUS
from config.trading_config import TradingConfig
from core.base_types import SignalType
from features.feature_calculator import FeatureCalculator
```

### RÈGLE #3 : HIÉRARCHIE STRICTE

```
🏔️ PYRAMIDE DES DÉPENDANCES

Level 5  ┌─────────────────┐
         │   Main Files    │ ← Peut tout importer
         └────────┬────────┘
Level 4  ┌────────┴────────┐
         │Execution/ML/Mon │ ← Import 0,1,2,3
         └────────┬────────┘
Level 3  ┌────────┴────────┐
         │   Strategies    │ ← Import 0,1,2
         └────────┬────────┘
Level 2  ┌────────┴────────┐
         │    Features     │ ← Import 0,1
         └────────┬────────┘
Level 1  ┌────────┴────────┐
         │   Core Modules  │ ← Import 0 only
         └────────┬────────┘
Level 0  ┌────────┴────────┐
         │Config/BaseTypes │ ← AUCUN import local
         └─────────────────┘
```

---

## 🚫 ERREURS FATALES À ÉVITER

### ❌ ERREUR #1 : Import Circulaire
```python
# fichier: features/calculator.py
from strategies.signal_generator import SignalGenerator  # ❌

# fichier: strategies/signal_generator.py
from features.calculator import Calculator  # ❌ CIRCULAR!
```

**SOLUTION** : Passer les dépendances en paramètres
```python
# ✅ CORRECT
def generate_signal(calculator: FeatureCalculator):
    features = calculator.calculate()
```

### ❌ ERREUR #2 : Star Imports
```python
# JAMAIS faire ça
from core.base_types import *  # ❌
from features import *          # ❌
```

**SOLUTION** : Toujours explicite
```python
# ✅ CORRECT
from core.base_types import SignalType, MarketRegime, TradingSignal
```

### ❌ ERREUR #3 : Import dans base_types
```python
# core/base_types.py
from features.calculator import FeatureCalculator  # ❌ FATAL!
```

**SOLUTION** : base_types ne doit JAMAIS importer de modules locaux

---

## 📁 IMPORTS PAR MODULE

### CONFIG/* - Level 0 (LEAF)
```python
# config/trading_config.py
# Standard library ONLY
import os
import json
from typing import Dict, Any

# Third-party OK
import yaml

# ❌ AUCUN import local!
```

### CORE/BASE_TYPES.PY - Level 0 (LEAF)
```python
# core/base_types.py
# Standard library
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

# Third-party OK
import numpy as np

# ❌ AUCUN import local!
```

### CORE/* - Level 1
```python
# core/battle_navale.py
# Peut importer Level 0 SEULEMENT
from config.constants import TICK_SIZE
from core.base_types import SignalType, MarketData

# ❌ PAS features, strategies, etc.
```

### FEATURES/* - Level 2
```python
# features/feature_calculator.py
# Peut importer Level 0 et 1
from config.trading_config import Config
from core.base_types import MarketData
from core.structure_data import DataBuffer

# ❌ PAS strategies, execution, etc.
```

### STRATEGIES/* - Level 3
```python
# strategies/signal_generator.py
# Peut importer Level 0, 1 et 2
from config.trading_config import Config
from core.base_types import SignalType
from core.patterns_detector import PatternDetector
from features.feature_calculator import FeatureCalculator

# ❌ PAS execution, ml, monitoring
```

### EXECUTION/* - Level 4
```python
# execution/order_manager.py
# Peut importer Level 0, 1, 2 et 3
from config.trading_config import Config
from core.base_types import Order
from features.market_regime import MarketRegime
from strategies.signal_generator import SignalGenerator

# ✅ OK d'importer strategies
```

---

## 🔍 DEBUGGING IMPORTS

### Commande de Vérification
```bash
# Vérifier les imports circulaires
python -m pytest tests/test_imports.py

# Visualiser l'arbre des dépendances
python scripts/check_imports.py --visualize
```

### Script de Validation
```python
# scripts/validate_imports.py
def check_module_imports(module_path):
    """Vérifie que les imports respectent la hiérarchie"""
    
    level_map = {
        'config': 0,
        'core/base_types.py': 0,
        'core': 1,
        'features': 2,
        'strategies': 3,
        'execution': 4,
        'monitoring': 4,
        'ml': 4
    }
    
    # Logique de vérification...
```

---

## 📋 CHECKLIST PRÉ-COMMIT

Avant CHAQUE commit, vérifier :

- [ ] Ordre des imports : stdlib → third-party → local
- [ ] Aucun import relatif (..)
- [ ] Aucun star import (*)
- [ ] Hiérarchie respectée (level N importe level < N)
- [ ] base_types.py n'importe RIEN de local
- [ ] Pas de dépendances circulaires
- [ ] Tests d'imports passent

---

## 🆘 RÉSOLUTION PROBLÈMES

### ModuleNotFoundError
```python
# Erreur: ModuleNotFoundError: No module named 'core'

# Solution 1: Ajouter le projet au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/MIA_IA_system"

# Solution 2: Lancer depuis la racine
cd /path/to/MIA_IA_system
python -m execution.simple_trader
```

### ImportError Circulaire
```python
# Erreur: ImportError: cannot import name 'X' from partially initialized module

# Solution: Refactorer pour casser la circularité
# Utiliser l'injection de dépendances
```

---

**⚡ REMEMBER: Des imports propres = Zéro bugs d'intégration!**