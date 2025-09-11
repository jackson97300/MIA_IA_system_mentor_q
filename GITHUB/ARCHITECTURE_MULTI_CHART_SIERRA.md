# 🏗️ ARCHITECTURE MULTI-CHART SIERRA CHART - MIA IA SYSTEM

**Date :** 11 septembre 2025  
**Statut :** ✅ **OPÉRATIONNEL**  
**Version :** v1.1  

---

## 📋 **RÉSUMÉ EXÉCUTIF**

Le système MIA IA dispose maintenant d'une **architecture multi-chart Sierra Chart** complète avec **4 dumpers C++ autonomes** compilés avec succès. Chaque dumper est spécialisé pour un chart spécifique et collecte des données optimisées.

---

## 🎯 **ARCHITECTURE MULTI-CHART**

### **4 Dumpers C++ Autonomes**

#### **1. MIA_Dumper_G3_Core.cpp - Chart 3 (1 minute)**
- **✅ BaseData** : OHLCV + Bid/Ask Volume
- **✅ VWAP** : Study ID 22 + 3 bandes
- **✅ VVA** : Current (ID 1) + Previous (ID 2) - POC/VAH/VAL
- **✅ PVWAP** : Previous VWAP calculé
- **✅ NBCV** : Study ID 33 - Ask/Bid Volume, Delta, Trades, Cumulative Delta
- **✅ DOM Live** : 20 niveaux de profondeur
- **✅ Time & Sales** : Quotes et Trades avec anti-doublons
- **✅ Cumulative Delta** : Study ID 32, SG 3
- **✅ Bearish/Bullish Logic** : SG 10,16,17 + calculs de pression

#### **2. MIA_Dumper_G4_Studies.cpp - Chart 4 (30 minutes)**
- **✅ OHLC** : Données de base
- **✅ VWAP** : Study ID 1 + bandes
- **✅ PVWAP** : Study ID 3 + bandes
- **✅ NBCV** : Study ID 14 - Ask/Bid Volume, Delta, Trades
- **✅ Cumulative Delta** : Study ID 6, SG 3
- **✅ Correlation** : Study ID 15
- **✅ ATR** : Study ID 5, SG 0
- **✅ Volume Profile** : Study ID 13 - VPOC/VAH/VAL + HVN/LVN
- **✅ VVA Previous** : Study ID 9 - PPOC/PVAH/PVAL

#### **3. MIA_Dumper_G8_VIX.cpp - Chart 8 (VIX)**
- **✅ VIX OHLC** : Lecture directe de sc.BaseDataIn
- **✅ Mode minimal** : Close seulement
- **✅ Mode complet** : OHLC + Volume

#### **4. MIA_Dumper_G10_MenthorQ.cpp - Chart 10 (MenthorQ)**
- **✅ Gamma Levels** : Study ID 1, 19 subgraphs
- **✅ Blind Spots** : Study ID 3, 9 subgraphs
- **✅ Swing Levels** : Study ID 2, 60 subgraphs
- **✅ Indexation 0-based** : Correction des boucles

---

## 🔧 **TECHNOLOGIES UTILISÉES**

### **Approach 1 - Headers Intégrés**
- **✅ Headers intégrés** dans chaque .cpp
- **✅ Plus de dépendances externes**
- **✅ Compilation garantie** sur Sierra Chart
- **✅ Fichiers autonomes** - un seul fichier par dumper

### **Mappings Validés**
- **✅ Study IDs** : Tous corrigés selon l'inventaire
- **✅ Subgraph Indices** : Indexation 0-based (ACSIL)
- **✅ Constantes** : NBCV_SG_*, VVA_SG_*, VWAP_SG_*
- **✅ Documentation** : MAPPING_MIA_CLEF.md complet

### **Fonctions Utilitaires**
- **✅ NormalizePx** : Normalisation des prix
- **✅ ReadSubgraph** : Lecture sécurisée des subgraphs
- **✅ ValidateStudyData** : Validation des données
- **✅ WriteToSpecializedFile** : Écriture fichiers spécialisés
- **✅ Anti-doublons** : T&S et DOM

---

## 📊 **TYPES DE DONNÉES EXPORTÉES**

### **Chart 3 (1 min)**
- `basedata` : OHLCV + Bid/Ask Volume
- `vwap` : VWAP + 3 bandes
- `vva` : VVA Current + Previous
- `pvwap` : Previous VWAP
- `nbcv` : NBCV + Bearish/Bullish logic
- `depth` : DOM Live
- `quote` : Quotes
- `trade` : Trades
- `cumulative_delta` : Cumulative Delta

### **Chart 4 (30 min)**
- `ohlc` : Données de base
- `vwap_current` : VWAP actuel
- `pvwap` : Previous VWAP
- `nbcv` : NBCV
- `cumulative_delta` : Cumulative Delta
- `correlation` : Correlation
- `atr` : ATR
- `volume_profile` : Volume Profile
- `vva_previous` : VVA Previous

### **Chart 8 (VIX)**
- `vix` : VIX OHLC

### **Chart 10 (MenthorQ)**
- `menthorq` : MenthorQ levels

---

## 🚀 **UNIFIER MIA**

### **Types Supportés**
```python
SUPPORTED_ONLY = {
    'basedata', 'vwap', 'vva', 'pvwap', 'nbcv', 'vix', 'quote', 'trade', 
    'depth', 'menthorq_levels', 'correlation', 'hvn_lvn', 'atr', 
    'vva_previous', 'cumulative_delta'
}
```

### **Fichiers de Sortie**
- `chart_3_*_YYYYMMDD.jsonl` : Chart 3
- `chart_4_*_YYYYMMDD.jsonl` : Chart 4
- `chart_8_*_YYYYMMDD.jsonl` : Chart 8
- `chart_10_*_YYYYMMDD.jsonl` : Chart 10

---

## 🔒 **SÉCURITÉ ET EXCLUSIONS**

### **Fichiers Exclus du Repository**
- ❌ **Tests** : `tests/`, `test_*`
- ❌ **Backups** : `backups/`, `*_backup*`
- ❌ **Outils temporaires** : `tools/` (scripts de test)
- ❌ **Données JSONL** : `chart_*.jsonl`, `mia_unified_*.jsonl`
- ❌ **Logs** : `*.log`, `logs/`
- ❌ **Fichiers temporaires** : `*.tmp`, `*.bak`

### **Repository Propre**
- ✅ **Code source uniquement**
- ✅ **Documentation complète**
- ✅ **Configurations sécurisées**
- ✅ **Aucune donnée sensible**

---

## 📈 **PERFORMANCE**

### **Compilation**
- **✅ 4/4 dumpers** compilés avec succès
- **✅ Aucune erreur** de compilation
- **✅ Headers intégrés** - pas de dépendances

### **Exports**
- **✅ Temps réel** : Chaque tick
- **✅ Anti-doublons** : T&S et DOM
- **✅ Validation** : Données sécurisées
- **✅ Fichiers spécialisés** : Par chart et type

---

## 🎯 **PROCHAINES ÉTAPES**

1. **✅ Architecture Multi-Chart** : Implémentée et opérationnelle
2. **Tests de Production** : Valider les exports en conditions réelles
3. **Monitoring** : Surveiller les performances
4. **Optimisations** : Ajustements selon les retours
5. **Documentation** : Mise à jour continue

---

## 📞 **SUPPORT**

- **Repository** : [https://github.com/jackson97300/MIA_IA_system_mentor_q](https://github.com/jackson97300/MIA_IA_system_mentor_q)
- **Documentation** : `extracteur/MAPPING_MIA_CLEF.md`
- **Issues** : Système d'issues GitHub

---

*Architecture Multi-Chart Sierra Chart - MIA IA System v1.1 - 11/09/2025*
