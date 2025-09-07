# MIA_IA_system

Pipeline marché **Sierra → Collector → Fichier unifié** + intégration **MenthorQ**.

## 🚀 Vue rapide

- **Entrée** : `chart_{3,4,8,10}_YYYYMMDD.jsonl` (écrits par `MIA_Chart_Dumper_patched.cpp`)
- **Collector** : `launchers/collector.py` (lit 3/4/8/10, unifie, feed MenthorQ)
- **Sortie** : `mia_unified_YYYYMMDD.jsonl` (un seul fichier/jour)
- **Signal** : Battle Navale + MenthorQ + régime VIX

## 📊 Architecture

```
Sierra Chart (.cpp) → JSONL Files → SierraTail → UnifiedWriter → mia_unified_YYYYMMDD.jsonl
                                                      ↓
                                              MenthorQ Processor
                                                      ↓
                                              Battle Navale Analyzer
```

## 🛠️ Lancer

### Test rapide
```bash
python -m launchers.collector --charts 3,4,8,10 --once
python test_menthorq_integration.py
```

### Mode production
```bash
python launchers/launch_24_7.py
```

## 📁 Structure

- **`core/`** : Modules principaux (data_collector, menthorq_battle_navale)
- **`features/`** : Fonctionnalités (sierra_stream, unifier, menthorq_processor)
- **`config/`** : Configurations (sierra_paths, menthorq_runtime)
- **`launchers/`** : Lanceurs (launch_24_7.py, collector.py)
- **`ancien_system/`** : Systèmes legacy (IBKR, Polygon.io)

## 🔧 Données collectées

- **Graph 3 (1m)** : basedata, vwap, vva, vap, depth, trade, quote
- **Graph 4 (30m)** : basedata, vwap, pvwap
- **Graph 8 (VIX)** : vix + policy
- **Graph 10 (MenthorQ)** : gamma (SG1..19), blind spots (BL1..10), swings (SG1..9)

## 🧪 Tests CI

Les workflows GitHub exécutent `test_menthorq_integration.py` et génèrent un **Atlas** du repo.

## 📚 Documentation

- `ARCHITECTURE.md` : Architecture détaillée
- `AUDIT_LISTE_DETAILLEE_MODULES.md` : Liste complète des modules
- `RAPPORT_FINAL_MIGRATION_SIERRA.md` : Migration vers Sierra

## ⚠️ Sécurité

- **Repo privé** : Données de marché sensibles
- **Aucune donnée marché** versionnée (JSONL exclus)
- **Mode lecture seule** : Pas de trading automatique