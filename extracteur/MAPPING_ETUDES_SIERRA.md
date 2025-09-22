# 📋 MAPPING COMPLET DES ÉTUDES SIERRA CHART

## 🎯 **Objectif**
Liste exhaustive de toutes les études utilisées avec leurs Study IDs et Subgraph mappings, organisées par chart pour éliminer les problèmes d'ID. Configuration finale avec 3 charts optimisés.

---

## 📊 **ÉTUDES PAR CHART**

### **📈 CHART 3 (1 minute) - Données natives complètes**

**VWAP (Volume Weighted Average Price)**:
- Study ID: Auto-résolution par nom (recommandé) ou id 22
- Subgraphs:
  - SG1: VWAP Principal
  - SG2: SD+1 Top Band 1
  - SG3: SD-1 Bottom Band 1
  - SG4: SD+2 Top Band 2
  - SG5: SD-2 Bottom Band 2
  - SG6: SD+3 Top Band 3
  - SG7: SD-3 Bottom Band 3

**VVA (Volume Value Area Lines)**:
- Current Study ID: 1 (Volume Profile courant)
- Previous Study ID: 8 (Volume Profile précédent)
- Subgraphs:
  - SG0: POC (Point of Control)
  - SG1: VAH (Value Area High)
  - SG2: VAL (Value Area Low)

**NBCV (Numbers Bars Calculated Values)**:
- Study ID: 33 (Graph 3)
- Subgraphs:
  - SG0: Delta (Ask - Bid Volume)
  - SG5: Ask Volume Total
  - SG6: Bid Volume Total
  - SG9: Cumulative Delta
  - SG10: Delta Percentage
  - SG11: Number of Trades
  - SG12: Total Volume
  - SG16: Ask Percentage
  - SG17: Bid Percentage

**Cumulative Delta**:
- Study ID: 32 (Graph 3)
- Subgraph: SG3 (Close - Cumulative Delta)

**ATR (Average True Range)**:
- Study ID: 45 (Graph 3)
- Subgraph: SG0 (ATR Value)

**Correlation (optionnel)**:
- Study ID: 46 (Graph 3)
- Subgraph: SG0 (Correlation Coefficient)

### **📈 CHART 8 (VIX) - Volatilité**

**VIX (Volatility Index)**:
- Chart Number: 8
- Lecture directe du chart VIX (pas d'étude)
- Données: OHLC + Volume
- Mode optimisé: Close seulement

### **🎯 CHART 10 (MenthorQ) - Niveaux de trading**

**MenthorQ Levels**:
- Chart Number: 10

**Gamma Levels**:
- Study ID: 1
- Subgraphs Count: 19
- SG0: Call Resistance
- SG1: Put Support
- SG2: HVL
- SG3: 1D Min
- SG4: 1D Max
- SG5: Call Resistance 0DTE
- SG6: Put Support 0DTE
- SG7: HVL 0DTE
- SG8: Gamma Wall 0DTE
- SG9-18: GEX 1-10

**Blind Spots**:
- Study ID: 3
- Subgraphs Count: 10
- SG0-9: BL 1 à BL 10

**Correlation Coefficient**:
- Study ID: 4
- Subgraphs Count: 1
- SG0: CC (Correlation Coefficient)

**Swing Levels**:
- Study ID: 0 (désactivé)
- Subgraphs Count: 0 (désactivé)
- Raison: MenthorQ ne fournit pas encore cette fonctionnalité

---

## 📋 **RÉSUMÉ PAR CHART**

### **Chart 3 (1m) - Données natives complètes**
- ✅ BaseData (OHLC/Volume/Bid/Ask Volumes)
- ✅ DOM (Depth of Market - 20 niveaux)
- ✅ Time & Sales + Quotes
- ✅ VWAP + 6 bandes (SD±1, ±2, ±3)
- ✅ VVA (VAH/VAL/VPOC) Current + Previous
- ✅ PVWAP (Previous VWAP)
- ✅ NBCV (OrderFlow - Delta, Ask/Bid, Ratios)
- ✅ Cumulative Delta
- ✅ ATR (Average True Range)
- ✅ Correlation (optionnel)

### **Chart 8 (VIX) - Volatilité**
- ✅ VIX Close (lecture directe du chart)
- ✅ VIX OHLC (optionnel)
- ✅ Événements VIX pour scoring IA

### **Chart 10 (MenthorQ) - Niveaux de trading**
- ✅ Gamma Levels (19 subgraphs - Call/Put/HVL/GEX)
- ✅ Blind Spots (10 subgraphs - BL 1 à BL 10)
- ✅ Correlation Coefficient (1 subgraph - CC)
- ❌ Swing Levels (désactivé - MenthorQ ne fournit pas encore)

---

## 🔧 **CONFIGURATION RECOMMANDÉE**

### **Configuration par Chart**

#### **Chart 3 (1m) - Configuration**
```cpp
// VWAP
sc.Input[3].SetInt(22);  // Study ID Chart 3
sc.Input[4].SetInt(3);   // 3 bandes

// VVA
sc.Input[6].SetInt(1);   // Current Study ID
sc.Input[7].SetInt(8);   // Previous Study ID

// NBCV
sc.Input[11].SetInt(33); // Study ID

// Cumulative Delta
sc.Input[15].SetInt(32); // Study ID
sc.Input[16].SetInt(3);  // Subgraph Index

// ATR
sc.Input[23].SetInt(45); // Study ID
sc.Input[24].SetInt(0);  // Subgraph Index

// Correlation (optionnel)
sc.Input[26].SetInt(46); // Study ID
sc.Input[27].SetInt(0);  // Subgraph Index
```

#### **Chart 8 (VIX) - Configuration**
```cpp
// VIX
sc.Input[0].SetInt(1);   // Export VIX
sc.Input[1].SetInt(0);   // Close seulement (plus efficace)
```

#### **Chart 10 (MenthorQ) - Configuration**
```cpp
// MenthorQ
sc.Input[0].SetInt(1);   // Export MenthorQ Levels
sc.Input[1].SetInt(1);   // Gamma Levels Study ID
sc.Input[2].SetInt(19);  // Gamma Levels Subgraphs Count
sc.Input[3].SetInt(3);   // Blind Spots Study ID
sc.Input[4].SetInt(10);  // Blind Spots Subgraphs Count
sc.Input[5].SetInt(0);   // Swing Levels Study ID (désactivé)
sc.Input[6].SetInt(0);   // Swing Levels Subgraphs Count (désactivé)
sc.Input[7].SetInt(4);   // Correlation Study ID
sc.Input[8].SetInt(1);   // Correlation Subgraphs Count
sc.Input[9].SetInt(1);   // MenthorQ On New Bar Only
```

---

## 📝 **NOTES IMPORTANTES**

1. **Auto-résolution VWAP** : Utiliser `sc.GetStudyIDByName()` pour trouver automatiquement l'ID
2. **Validation des IDs** : Toujours vérifier que les Study IDs existent avant utilisation
3. **Subgraphs 0-indexés** : Les subgraphs commencent à 0 dans ACSIL
4. **Cross-chart** : Certaines études sont sur des charts différents
5. **Fallback** : Prévoir des valeurs de fallback si une étude n'est pas trouvée

---

## 🚀 **UTILISATION**

Ce mapping peut être utilisé pour :
- ✅ Configuration automatique des études
- ✅ Validation des Study IDs
- ✅ Debugging des problèmes de mapping
- ✅ Documentation pour les développeurs
- ✅ Tests automatisés
