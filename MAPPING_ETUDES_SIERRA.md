# 📋 MAPPING COMPLET DES ÉTUDES SIERRA CHART

## 🎯 **Objectif**
Liste exhaustive de toutes les études utilisées avec leurs Study IDs et Subgraph mappings, organisées par chart pour éliminer les problèmes d'ID.

---

## 📊 **ÉTUDES PAR CHART**

### **📈 CHART 3 (1 minute)**

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
- Current Study ID: 8 ou 1 (Volume Profile courant)
- Previous Study ID: 9 ou 2 (Volume Profile précédent)
- Subgraphs:
  - SG1: POC (Point of Control)
  - SG2: VAH (Value Area High)
  - SG3: VAL (Value Area Low)

**NBCV (Numbers Bars Calculated Values)**:
- Study ID: 33 (Graph 3)
- Subgraphs:
  - SG6: Ask Volume Total
  - SG7: Bid Volume Total
  - SG1: ask volume bid volume difference 
  - SG12: Number of Trades
  - SG10: Cumulative Sum Of Ask Volume Bid Volume Difference - Day

### **📊 CHART 4 (30 minutes)**

**Correlation ES/NQ**:
- Study ID: 15 (Graph 4)
- Subgraph: SG0 (Correlation Coefficient)

**Cumulative Delta Bars**:
- Study ID: 6 (Graph 4)
- Subgraph: SG4 (Close - Cumulative Delta)

### **📈 CHART 8 (VIX)**

**VIX (Volatility Index)**:
- Chart Number: 8
- Study ID: 23 (Study/Price Overlay)
- Subgraph: SG4 (Last)

### **🎯 CHART 10 (MenthorQ)**

**MenthorQ Levels**:
- Chart Number: 10

**Gamma Levels**:
- Study ID: 1
- Subgraphs Count: 19
- SG1-19: Gamma levels (Call Resistance, Put Support, HVL, etc.)

**Blind Spots**:
- Study ID: 3
- Subgraphs Count: 9
- SG1-9: Blind spot levels

**Swing Levels**:
- Study ID: 2
- Subgraphs Count: 9
- SG1-9: Swing levels

---

## 📋 **RÉSUMÉ PAR CHART**

### **Chart 3 (1m) - Données principales**
- ✅ VWAP + 6 bandes (SD±1, ±2, ±3)
- ✅ VVA (VAH/VAL/VPOC) courant et précédent
- ✅ NBCV (Ask/Bid/Delta/Trades/Cumulative)
- ✅ BaseData (OHLC/Volume)
- ✅ DOM (Depth of Market)
- ✅ Time & Sales

### **Chart 4 (30m) - Données M30**
- ✅ Correlation ES/NQ
- ✅ Cumulative Delta Bars
- ✅ Cross-chart data (OHLC, VWAP, NBCV)

### **Chart 8 (VIX) - Volatilité**
- ✅ VIX Last (SG4)
- ✅ Study/Price Overlay (ID 23)

### **Chart 10 (MenthorQ) - Niveaux**
- ✅ Gamma Levels (19 subgraphs)
- ✅ Blind Spots (9 subgraphs)
- ✅ Swing Levels (9 subgraphs)

---

## 🔧 **CONFIGURATION RECOMMANDÉE**

### **Configuration par Chart**

#### **Chart 3 (1m) - Configuration**
```cpp
// VWAP
sc.Input[4].SetInt(0);  // Auto-résolution par nom
sc.Input[39].SetInt(1); // SG1 = VWAP principal
sc.Input[40].SetInt(2); // SG2 = SD+1
sc.Input[41].SetInt(3); // SG3 = SD-1
sc.Input[42].SetInt(4); // SG4 = SD+2
sc.Input[43].SetInt(5); // SG5 = SD-2
sc.Input[44].SetInt(6); // SG6 = SD+3
sc.Input[45].SetInt(7); // SG7 = SD-3

// VVA
sc.Input[7].SetInt(9);  // Volume Profile courant
sc.Input[8].SetInt(8);  // Volume Profile précédent

// NBCV
sc.Input[20].SetInt(33); // Study ID
sc.Input[21].SetInt(6);  // SG6 - Ask Volume
sc.Input[22].SetInt(7);  // SG7 - Bid Volume
sc.Input[23].SetInt(1);  // SG1 - Delta
sc.Input[24].SetInt(12); // SG12 - Trades
sc.Input[25].SetInt(10); // SG10 - Cumulative
```

#### **Chart 4 (30m) - Configuration**
```cpp
// Correlation
sc.Input[46].SetInt(15); // Study ID

// Cumulative Delta
sc.Input[26].SetInt(6);  // Study ID
```

#### **Chart 8 (VIX) - Configuration**
```cpp
// VIX
sc.Input[16].SetInt(8); // Chart 8
sc.Input[17].SetInt(23); // Study ID
sc.Input[18].SetInt(4);  // SG4
```

#### **Chart 10 (MenthorQ) - Configuration**
```cpp
// MenthorQ
sc.Input[32].SetInt(10); // Chart 10
sc.Input[33].SetInt(1);  // Gamma Levels
sc.Input[34].SetInt(19); // Gamma SG Count
sc.Input[35].SetInt(3);  // Blind Spots
sc.Input[36].SetInt(9);  // Blind SG Count
sc.Input[37].SetInt(2);  // Swing Levels
sc.Input[38].SetInt(9);  // Swing SG Count
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
