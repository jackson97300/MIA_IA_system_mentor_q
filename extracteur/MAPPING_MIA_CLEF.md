# 🎯 MAPPING MIA - ÉTUDES CLÉS

## 📊 **CHART 3 (1-min - Flux Principal)**

### **VWAP** - Study ID: 22
- **SG 0**: "V" (Main VWAP)
- **SG 1**: "+1" (Upper Band 1)
- **SG 2**: "-1" (Lower Band 1)
- **SG 3**: "+2" (Upper Band 2)
- **SG 4**: "-2" (Lower Band 2)
- **SG 5**: "+3" (Upper Band 3)
- **SG 6**: "-3" (Lower Band 3)

### **VVA Current** - Study ID: 1
- **SG 0**: "Vol POC" (Point of Control)
- **SG 1**: "Vol Value Area High" (VAH)
- **SG 2**: "Vol Value Area Low" (VAL)

### **VVA Previous** - Study ID: 2
- **SG 0**: "PPOC" (Previous POC)
- **SG 1**: "PVAH" (Previous VAH)
- **SG 2**: "PVAL" (Previous VAL)

### **NBCV** - Study ID: 33
- **SG 0**: "Ask Volume Bid Volume Difference" (Delta)
- **SG 5**: "Ask Volume Total"
- **SG 6**: "Bid Volume Total"
- **SG 9**: "Cumulative Sum Of Ask Volume Bid Volume Difference - Day"
- **SG 11**: "Number of Trades"
- **SG 12**: "Total Volume"

### **Cumulative Delta** - Study ID: 32
- **SG 3**: "Close" (Cumulative Delta Close)

---

## 📊 **CHART 4 (30-min - Cross-Chart)**

### **VWAP Current** - Study ID: 1
- **SG 0**: "VWAP" (Main)
- **SG 1**: "SD+1" (Upper Band 1)
- **SG 2**: "SD-1" (Lower Band 1)
- **SG 3**: "SD+2" (Upper Band 2)
- **SG 4**: "SD-2" (Lower Band 2)

### **PVWAP** - Study ID: 3
- **SG 4**: "PVWAP" (Previous VWAP)

### **VVA Previous** - Study ID: 9
- **SG 0**: "PPOC" (Previous POC)
- **SG 1**: "PVAH" (Previous VAH)
- **SG 2**: "PVAL" (Previous VAL)

### **NBCV** - Study ID: 14
- **SG 0**: "Ask Volume Bid Volume Difference" (Delta)
- **SG 5**: "Ask Volume Total"
- **SG 6**: "Bid Volume Total"
- **SG 9**: "Cumulative Sum Of Ask Volume Bid Volume Difference - Day"
- **SG 10**: "Ask Volume Bid Volume Difference Percent" (Delta %)
- **SG 11**: "Number of Trades"
- **SG 16**: "Ask Volume Percent" (Ask %)
- **SG 17**: "Bid Volume Percent" (Bid %)
- **SG 12**: "Total Volume"

### **Correlation** - Study ID: 15
- **SG 0**: "CC" (Correlation Coefficient)

### **VVA Previous** - Study ID: 9
- **SG 0**: "PPOC" (Previous POC)
- **SG 1**: "PVAH" (Previous VAH)
- **SG 2**: "PVAL" (Previous VAL)

### **Cumulative Delta** - Study ID: 6
- **SG 3**: "Close" (Cumulative Delta Close)

### **ATR** - Study ID: 5
- **SG 0**: "ATR" (Average True Range)

### **Volume Profile** - Study ID: 13
- **SG 1**: "VPOC" (Volume POC)
- **SG 2**: "VAH" (Value Area High)
- **SG 3**: "VAL" (Value Area Low)
- **SG 17**: "HVN" (High Volume Nodes)
- **SG 18**: "LVN" (Low Volume Nodes)

---

## 📊 **CHART 10 (MenthorQ)**

### **Gamma Levels** - Study ID: 1
- **SG 0**: "Call Resistance"
- **SG 1**: "Put Support"
- **SG 2**: "HVL"
- **SG 5**: "Call Resistance 0DTE & Gamma Wall 0DTE"
- **SG 6**: "Put Support 0DTE"
- **SG 8**: "Gamma Wall 0DTE"
- **SG 9-18**: "GEX 1-10" (Gamma Exposure)

### **Swing Levels** - Study ID: 2
- **SG 0-59**: "SG1-SG60" (60 Swing Levels)

### **Blind Spots** - Study ID: 3
- **SG 0-9**: "BL 1-10" (10 Blind Spot Levels)

---

## 🔧 **CONFIGURATION DUMPER - PRÊT À COLLER**

### **Chart 3 - MIA_Dumper_G3_Core.cpp**
```cpp
// VWAP
sc.Input[3].SetInt(1);        // Export VWAP from Study
sc.Input[4].SetInt(22);       // VWAP Study ID
sc.Input[39].SetInt(0);       // Main (SG 0)
sc.Input[40].SetInt(1);       // UP1 (SG 1)
sc.Input[41].SetInt(2);       // DN1 (SG 2)
sc.Input[42].SetInt(3);       // UP2 (SG 3)
sc.Input[43].SetInt(4);       // DN2 (SG 4)
sc.Input[44].SetInt(5);       // UP3 (SG 5)
sc.Input[45].SetInt(6);       // DN3 (SG 6)

// VVA
sc.Input[6].SetInt(1);        // Export VVA ON
sc.Input[7].SetInt(1);        // VVA Current Study ID
sc.Input[8].SetInt(2);        // VVA Previous Study ID
// CORRECTION: POC=0, VAH=1, VAL=2 (pas 1,2,3)

// NBCV
sc.Input[10].SetInt(1);       // Export NBCV ON
sc.Input[11].SetInt(33);      // NBCV Study ID
// SGs: 0=Delta, 5=Ask, 6=Bid, 9=CumDelta, 11=Trades, 12=Volume, 10=Delta%, 16=Ask%, 17=Bid%

// OrderFlow Pressure (NBCV)
sc.Input[17].SetFloat(200.0); // Min Total Volume
sc.Input[18].SetFloat(0.15);  // Min |Delta Ratio| (15%)
sc.Input[19].SetFloat(1.60);  // Min Ask/Bid or Bid/Ask Ratio (1.6x)

// Cumulative Delta
sc.Input[14].SetInt(1);       // Export Cumulative Delta ON
sc.Input[15].SetInt(32);      // Cumulative Delta Study ID
sc.Input[16].SetInt(3);       // Close (SG 3)
```

### **Chart 4 - MIA_Dumper_G4_Studies.cpp**
```cpp
// VWAP Current
sc.Input[1].SetInt(1);        // VWAP Current Study ID
sc.Input[2].SetInt(0);        // VWAP Main (SG 0)
sc.Input[3].SetInt(1);        // VWAP UP1 (SG 1)
sc.Input[4].SetInt(2);        // VWAP DN1 (SG 2)

// PVWAP
sc.Input[5].SetInt(3);        // PVWAP Study ID
sc.Input[6].SetInt(4);        // PVWAP Main (SG 4)

// VVA Previous
sc.Input[7].SetInt(9);        // VVA Previous Study ID
sc.Input[8].SetInt(0);        // PPOC (SG 0)
sc.Input[9].SetInt(1);        // PVAH (SG 1)
sc.Input[10].SetInt(2);       // PVAL (SG 2)

// NBCV
sc.Input[11].SetInt(14);      // NBCV Study ID
sc.Input[12].SetInt(0);       // Delta (SG 0)
sc.Input[13].SetInt(5);       // Ask Volume (SG 5)
sc.Input[14].SetInt(6);       // Bid Volume (SG 6)

// Correlation
sc.Input[15].SetInt(15);      // Correlation Study ID
sc.Input[16].SetInt(0);       // CC (SG 0)

// Cumulative Delta
sc.Input[8].SetInt(1);        // Export Cumulative Delta ON
sc.Input[9].SetInt(6);        // Cumulative Delta Study ID

// ATR
sc.Input[12].SetInt(1);       // Export ATR ON
sc.Input[13].SetInt(5);       // ATR Study ID
sc.Input[14].SetInt(0);       // ATR (SG 0)

// Volume Profile
sc.Input[20].SetInt(1);       // Export Volume Profile ON
sc.Input[21].SetInt(13);      // Volume Profile Study ID
sc.Input[22].SetInt(1);       // Export VPOC/VAH/VAL ON
sc.Input[23].SetInt(1);       // Export HVN/LVN ON
```

### **Chart 10 - MIA_Dumper_G10_MenthorQ.cpp**
```cpp
// Gamma Levels
sc.Input[1].SetInt(1);        // Gamma Levels Study ID
sc.Input[2].SetInt(19);       // Number of Gamma SGs (0-18)

// Swing Levels
sc.Input[5].SetInt(2);        // Swing Levels Study ID
sc.Input[6].SetInt(60);       // Number of Swing SGs (0-59)

// Blind Spots
sc.Input[3].SetInt(3);        // Blind Spots Study ID
sc.Input[4].SetInt(10);       // Number of Blind Spot SGs (0-9)
```

---

## ⚠️ **CORRECTIFS CRITIQUES**

### **1. VVA Subgraph Indices**
- **AVANT**: POC=1, VAH=2, VAL=3 ❌
- **APRÈS**: POC=0, VAH=1, VAL=2 ✅

### **2. VWAP Auto-Detection**
Ajouter "VWAP" dans la résolution de nom (en plus de "Volume Weighted Average Price")

### **3. MIA_Study_Inspector.cpp**
```cpp
// AVANT (erreur)
const SCString shortName = sc.GetChartStudyShortName(chart, studyID);

// APRÈS (correct)
SCString shortName;
sc.GetChartStudyShortName(chart, studyID, shortName);
```

---

## 🎯 **RÉSUMÉ DES IDS CLÉS**

| Chart | Étude | Study ID | Subgraphs Importants |
|-------|-------|----------|---------------------|
| 3 | VWAP | 22 | 0,1,2,3,4,5,6 |
| 3 | VVA Current | 1 | 0,1,2 |
| 3 | VVA Previous | 2 | 0,1,2 |
| 3 | NBCV | 33 | 0,5,6,9,11,12 |
| 3 | VIX | 23 | 3 |
| 3 | Cumulative Delta | 32 | 3 |
| 4 | VWAP | 1 | 0,1,2,3,4 |
| 4 | PVWAP | 3 | 4 |
| 4 | VVA Previous | 9 | 0,1,2 |
| 4 | NBCV | 14 | 0,5,6,9,11,12 |
| 4 | Correlation | 15 | 0 |
| 4 | ATR | 5 | 0 |
| 4 | Volume Profile | 13 | 1,2,3,17,18 |
| 10 | Gamma Levels | 1 | 0,1,2,5,6,8,9-18 |
| 10 | Swing Levels | 2 | 0-59 |
| 10 | Blind Spots | 3 | 0-9 |

---

## 🚀 **PROCHAINES ÉTAPES**

1. ✅ **Corriger MIA_Study_Inspector.cpp** (erreur build)
2. ✅ **Mettre à jour les dumper avec les bons IDs**
3. ✅ **Corriger les indices VVA (0,1,2 au lieu de 1,2,3)**
4. ✅ **Ajouter ATR export sur Chart 4**
5. ✅ **Ajouter logique bearish/bullish sur Chart 3**
6. ✅ **Collecter les ratios SG 10, 16, 17 (Delta %, Ask %, Bid %)**
7. ✅ **Implémenter code robuste avec fallbacks et seuils configurables**
8. ✅ **Tester la compilation et les exports**

**🎉 MINE D'OR EXPLOITÉE ! Tous les mappings sont maintenant documentés et prêts à l'emploi !**
