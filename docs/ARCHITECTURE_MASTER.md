# 🏗️ ARCHITECTURE MASTER - MIA TRADING SYSTEM V3.0

> **Document de Référence Principal**  
> Dernière mise à jour : 2025-01-25  
> Version : 3.0

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Système](#architecture-système)
3. [Règles d'Imports](#règles-dimports)
4. [Dépendances et Intégration](#dépendances-et-intégration)
5. [Modules Principaux](#modules-principaux)
6. [Workflow d'Exécution](#workflow-dexécution)
7. [Guide de Développement](#guide-de-développement)
8. [Références Rapides](#références-rapides)

---

## 🎯 VUE D'ENSEMBLE

### Mission du Système
Bot de trading automatisé pour ES Futures avec edge options SPX, utilisant la méthode propriétaire "Battle Navale" et ML progressif.

### Statistiques Projet
- **Fichiers Python** : 47
- **Modules principaux** : 9
- **Tests unitaires** : 15
- **Documentation** : 6 guides complets

### Performance Cible
- Latence : < 10ms
- Win Rate : ≥ 60%
- Sharpe Ratio : ≥ 1.5
- Uptime : > 99%

---

## 🏗️ ARCHITECTURE SYSTÈME

```
D:\MIA_IA_system\
├── config/          # Configuration centralisée
├── core/            # Fondations (types, connecteurs, patterns)
├── features/        # Calcul des indicateurs (18 features)
├── strategies/      # Logique de trading (signal generation)
├── execution/       # Gestion ordres et automation
├── monitoring/      # Surveillance temps réel
├── ml/              # Intelligence artificielle
├── performance/     # Analyse et optimisation
├── data/            # Collection et stockage
├── tests/           # Tests unitaires complets
├── scripts/         # Scripts d'administration
└── docs/            # Documentation technique
```

---

## 🔧 RÈGLES D'IMPORTS

### ⚡ Règle #1 : Ordre Strict
```python
# 1. STDLIB (toujours en premier)
import time
import json
from typing import Dict, List, Optional

# 2. THIRD-PARTY (ensuite)
import numpy as np
import pandas as pd
from ib_insync import IB

# 3. LOCAL (en dernier, imports absolus uniquement)
from config.trading_config import TradingConfig
from core.base_types import SignalType
```

### 🚫 Imports INTERDITS
```python
# ❌ JAMAIS d'imports circulaires
# ❌ JAMAIS d'imports relatifs (..)
# ❌ JAMAIS de star imports (from x import *)
```

### 📊 Hiérarchie des Dépendances

```
Level 0 (LEAF - aucune dépendance locale):
├── config/*
└── core/base_types.py

Level 1 (dépend de Level 0):
└── core/* (sauf base_types)

Level 2 (dépend de Level 0-1):
└── features/*

Level 3 (dépend de Level 0-2):
└── strategies/*

Level 4 (dépend de Level 0-3):
├── execution/*
├── monitoring/*
└── ml/*

Level 5 (peut tout importer):
└── main files (main.py, automation_main.py)
```

---

## 🔄 DÉPENDANCES ET INTÉGRATION

### Flux de Données Principal
```
Sierra Chart/IQFeed
    ↓
core/connectors
    ↓
features/calculators → 18 features
    ↓
strategies/generators → signals
    ↓
execution/managers → orders
    ↓
monitoring/trackers → metrics
```

### Points d'Intégration Critiques

1. **Data Pipeline**
   - Sierra → core → features (< 5ms)
   - Validation données en temps réel
   - Buffer circulaire optimisé

2. **Signal Pipeline**
   - Features → Strategies → Risk → Execution (< 10ms)
   - Confluence multi-niveaux
   - Validation signaux

3. **Monitoring Pipeline**
   - Tous modules → Performance Tracker → Alertes
   - Métriques temps réel
   - Health checks continus

---

## 📦 MODULES PRINCIPAUX

### 🎯 CORE - Fondations
| Module | Responsabilité | Imports Autorisés |
|--------|---------------|-------------------|
| base_types.py | Types partagés | AUCUN local |
| battle_navale.py | Méthode propriétaire | base_types only |
| patterns_detector.py | 5 patterns ES | base_types only |
| ibkr_connector.py | API IBKR | config, base_types |
| sierra_connector.py | Sierra Chart | config, base_types |

### 🧮 FEATURES - Indicateurs
| Module | Features | Performance |
|--------|----------|-------------|
| feature_calculator.py | 8 order flow + 6 options + 4 context | < 3ms |
| market_regime.py | Trend vs Range detection | < 1ms |
| confluence_analyzer.py | Multi-level analysis | < 2ms |

### 🎲 STRATEGIES - Signaux
| Module | Stratégie | Win Rate |
|--------|-----------|----------|
| signal_generator.py | Orchestrateur principal | - |
| trend_strategy.py | Mode tendance | > 65% |
| range_strategy.py | Mode range | > 60% |
| strategy_selector.py | Sélection adaptative | - |

### ⚡ EXECUTION - Trading
| Module | Fonction | Latence |
|--------|----------|---------|
| order_manager.py | Gestion ordres | < 20ms |
| risk_manager.py | Kelly sizing, stops | < 5ms |
| simple_trader.py | Loop automation | - |
| trade_snapshotter.py | Capture données | < 10ms |

---

## 🚀 WORKFLOW D'EXÉCUTION

### 1. Démarrage Système
```python
# main.py
1. Load configurations
2. Initialize connectors
3. Start data feeds
4. Initialize strategies  
5. Start automation
6. Enable monitoring
```

### 2. Cycle Trading (Loop)
```
[Market Data] → [Features] → [Regime] → [Strategy] → [Signal]
                                                          ↓
[Monitoring] ← [Execution] ← [Risk Check] ← [Validation]
```

### 3. Gestion Erreurs
```python
try:
    # Code principal
except SpecificError as e:
    logger.error(f"Handled: {e}")
    # Recovery action
except Exception as e:
    logger.critical(f"Unhandled: {e}")
    alert_system.send_critical(e)
    # Emergency shutdown if needed
```

---

## 🛠️ GUIDE DE DÉVELOPPEMENT

### Ajout Nouveau Module

1. **Déterminer le niveau** dans la hiérarchie
2. **Créer le fichier** avec header standard
3. **Importer uniquement** les niveaux inférieurs
4. **Ajouter tests** dans tests/
5. **Mettre à jour** __init__.py
6. **Documenter** l'interface

### Template Module Standard
```python
"""
Module: [nom_module]
Responsabilité: [description]
Niveau hiérarchie: [0-5]
"""

# === IMPORTS (ordre strict) ===
# 1. STDLIB
import logging
from typing import Dict, List, Optional

# 2. THIRD-PARTY
import numpy as np

# 3. LOCAL (selon niveau)
from core.base_types import BaseType

# === LOGGER ===
logger = logging.getLogger(__name__)

# === CLASSES/FUNCTIONS ===
class ModuleClass:
    """Documentation classe"""
    pass

# === EXPORTS ===
__all__ = ['ModuleClass']
```

### Checklist Pré-commit

- [ ] Imports suivent hiérarchie
- [ ] Pas de dépendances circulaires
- [ ] Logger configuré
- [ ] Gestion erreurs robuste
- [ ] Tests unitaires passent
- [ ] Documentation à jour
- [ ] Type hints complets

---

## 📌 RÉFÉRENCES RAPIDES

### Commandes Essentielles
```bash
# Tests
pytest tests/test_core/test_battle_navale.py

# Backtest
python scripts/run_backtest.py --days 30

# Monitoring only
python monitoring/live_monitor.py --no-trading

# Full system
python automation_main.py --config production
```

### Variables Environnement
```env
# .env.automation
TRADING_MODE=paper
RISK_LEVEL=conservative
MAX_DAILY_LOSS=1000
DISCORD_WEBHOOK=xxx
```

### Métriques Clés
- CVD (Cumulative Volume Delta)
- Gamma Exposure (GEX)
- VWAP Deviation
- Market Profile (VAH/VAL/POC)
- Battle Navale Score

---

## 📞 CONTACTS & SUPPORT

- **Documentation** : /docs/
- **Logs** : /logs/
- **Monitoring** : Discord #alerts
- **Backup** : Automatique toutes les 4h

---

**Document maintenu par l'équipe MIA Trading System**  
*Pour modifications, mettre à jour via l'artifact dans Claude*