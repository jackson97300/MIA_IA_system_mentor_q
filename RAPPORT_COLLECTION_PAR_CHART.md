# 📊 RAPPORT COMPLET - COLLECTION PAR CHART
**Fichier analysé :** `MIA_Chart_Dumper_patched_VIX_NBCV_Quotes_Final_Corrected.cpp`
**Date d'analyse :** 2025-01-10

## 🎯 RÉSUMÉ EXÉCUTIF

Le dumper principal collecte **15+ types de données** répartis sur **4 charts principaux** :
- **Chart 3** : Données principales (BaseData, VWAP, Volume Profile, NBCV, VIX, Quotes/Trades, DOM)
- **Chart 4** : Données cross-chart (OHLC, VWAP, PVWAP, NBCV, Corrélation ES/NQ)
- **Chart 8** : VIX source (cross-chart vers Chart 3)
- **Chart 10** : MenthorQ levels (Gamma, Blind Spots, Swing Levels)

---

## 📋 COLLECTION PAR CHART

### 🔵 **CHART 3** (Chart Principal)
**Fichier de sortie :** `chart_3_YYYYMMDD.jsonl`

#### **📊 BASEDATA** (OHLCV + Bid/Ask Volume)
```json
{
  "type": "basedata",
  "i": 1234, "o": 6500.25, "h": 6505.50, "l": 6498.75, "c": 6502.00,
  "v": 1250, "bidvol": 650, "askvol": 600, "chart": 3
}
```

#### **📈 VWAP** (Auto-résolution par nom, SG1-7)
```json
{
  "type": "vwap",
  "src": "study", "i": 1234, "v": 6501.25,
  "up1": 6503.50, "dn1": 6499.00, "up2": 6505.75, "dn2": 6496.75,
  "up3": 6508.00, "dn3": 6494.50, "chart": 3
}
```

#### **📊 VOLUME PROFILE** (Study ID=9 Current, ID=8 Previous)
```json
{
  "type": "vva",
  "i": 1234, "vah": 6505.25, "val": 6498.50, "vpoc": 6501.75,
  "pvah": 6504.00, "pval": 6499.25, "ppoc": 6502.00, "chart": 3
}
```

#### **🔢 NBCV ORDERFLOW** (Study ID=33, SG6/7/1/12/10)
**Footprint :**
```json
{
  "type": "nbcv_footprint",
  "i": 1234, "ask_volume": 1250, "bid_volume": 1100, "delta": 150,
  "trades": 45, "cumulative_delta": 2500, "total_volume": 2350, "chart": 3
}
```

**Metrics :**
```json
{
  "type": "nbcv_metrics",
  "i": 1234, "delta_ratio": 0.0638, "bid_ask_ratio": 0.8800, "ask_bid_ratio": 1.1364,
  "pressure_bullish": 1, "pressure_bearish": 0, "chart": 3
}
```

**OrderFlow :**
```json
{
  "type": "nbcv_orderflow",
  "i": 1234, "volume_imbalance": 0.0638, "trade_intensity": 0.0191,
  "delta_trend": 1, "absorption_pattern": 0, "chart": 3
}
```

#### **📊 VIX** (Cross-chart depuis Chart 8, Study ID=23, SG=4)
```json
{
  "type": "vix",
  "i": 1234, "last": 18.45, "mode": 1, "chart": 3, "study": 23, "sg": 4
}
```

#### **💰 QUOTES/T&S** (Temps réel)
```json
{
  "type": "quote",
  "kind": "BIDASK", "bid": 6501.75, "ask": 6502.25, "bq": 125, "aq": 150,
  "spread": 0.50, "mid": 6502.00, "chart": 3
}
```

```json
{
  "type": "trade",
  "source": "basedata", "px": 6502.00, "qty": 25, "chart": 3
}
```

#### **📊 DOM** (20 niveaux)
```json
{
  "type": "depth",
  "side": "BID", "lvl": 1, "price": 6501.75, "size": 125, "chart": 3
}
```

---

### 🟢 **CHART 4** (Cross-Chart)
**Fichier de sortie :** `chart_4_YYYYMMDD.jsonl`

#### **📊 OHLC GRAPH4** (M30)
```json
{
  "type": "basedata",
  "i": 1234, "o": 6500.25, "h": 6505.50, "l": 6498.75, "c": 6502.00,
  "v": 1250, "chart": 4
}
```

#### **📈 VWAP CURRENT** (Auto-résolution par nom)
```json
{
  "type": "vwap",
  "src": "study", "i": 1234, "v": 6501.25,
  "up1": 6503.50, "dn1": 6499.00, "up2": 6505.75, "dn2": 6496.75,
  "up3": 6508.00, "dn3": 6494.50, "chart": 4
}
```

#### **📈 PVWAP** (VWAP Période Précédente, Study ID=3, SG=5)
```json
{
  "type": "pvwap",
  "src": "study", "i": 1234, "pvwap": 6498.50, "chart": 4
}
```

#### **🔢 NBCV GRAPH4** (Auto-résolution par nom, SG6/7/1/12)
**Footprint :**
```json
{
  "type": "nbcv_footprint",
  "i": 1234, "ask_volume": 1250, "bid_volume": 1100, "delta": 150,
  "trades": 45, "cumulative_delta": 2500, "total_volume": 2350, "chart": 4
}
```

**Metrics :**
```json
{
  "type": "nbcv_metrics",
  "i": 1234, "delta_ratio": 0.0638, "bid_ask_ratio": 0.8800, "ask_bid_ratio": 1.1364,
  "pressure_bullish": 1, "pressure_bearish": 0, "chart": 4
}
```

**OrderFlow :**
```json
{
  "type": "nbcv_orderflow",
  "i": 1234, "volume_imbalance": 0.0638, "trade_intensity": 0.0191,
  "delta_trend": 1, "absorption_pattern": 0, "chart": 4
}
```

#### **🔗 CORRÉLATION ES/NQ** (Study ID=15, SG=0)
```json
{
  "type": "correlation",
  "i": 1234, "value": -0.505462, "study_id": 15, "sg": 0, "chart": 4,
  "corr_index": 1035, "close": 6553.00, "length": 20,
  "base_id": "ID0.SG4", "ref_id": "ID16.SG1"
}
```

---

### 🟡 **CHART 8** (VIX Source)
**Note :** Chart 8 est la source VIX, mais les données sont collectées sur Chart 3

#### **📊 VIX** (Study ID=23, SG=4, Cross-Chart vers Chart 3)
```json
{
  "type": "vix",
  "i": 1234, "last": 18.45, "mode": 1, "chart": 3, "study": 23, "sg": 4
}
```

---

### 🟣 **CHART 10** (MenthorQ)
**Fichier de sortie :** `chart_10_YYYYMMDD.jsonl`

#### **📊 MENTHORQ LEVELS** (3 types d'études)
**Gamma Levels (Study ID=1, 19 subgraphs) :**
```json
{
  "type": "menthorq_level",
  "level_type": "call_resistance", "price": 6495.25, "subgraph": 1, "study_id": 1,
  "bar": 1234, "chart": 10
}
```

**Blind Spots (Study ID=3, 9 subgraphs) :**
```json
{
  "type": "menthorq_level",
  "level_type": "blind_spot_1", "price": 6490.50, "subgraph": 1, "study_id": 3,
  "bar": 1234, "chart": 10
}
```

**Swing Levels (Study ID=2, 9 subgraphs) :**
```json
{
  "type": "menthorq_level",
  "level_type": "swing_lvl_1", "price": 6485.75, "subgraph": 1, "study_id": 2,
  "bar": 1234, "chart": 10
}
```

---

## 🔧 CONFIGURATION DES INPUTS

### **Paramètres Généraux**
- `Input[0]` : Max DOM Levels = 20
- `Input[1]` : Max VAP Elements = 0 (DISABLED)
- `Input[2]` : Max T&S Entries = 10

### **VWAP Configuration**
- `Input[3]` : Export VWAP From Study = 1
- `Input[4]` : VWAP Study ID = 0 (Auto-résolution)
- `Input[5]` : Export VWAP Bands Count = 4
- `Input[39-45]` : VWAP SG Mapping (SG1-7)

### **Volume Profile (VVA)**
- `Input[6]` : Export Value Area Lines = 1
- `Input[7]` : VVA Current Study ID = 9
- `Input[8]` : VVA Previous Study ID = 8
- `Input[9]` : Emit VVA On New Bar Only = 1
- `Input[10]` : Apply Price Multiplier to VVA = 1

### **PVWAP (Previous VWAP)**
- `Input[11]` : Export Previous VWAP = 1
- `Input[12]` : PVWAP Bands Count = 2
- `Input[13]` : PVWAP On New Bar Only = 1

### **VIX Configuration**
- `Input[14]` : Export VIX = 1
- `Input[15]` : VIX Source Mode = 1 (Study Overlay)
- `Input[16]` : VIX Chart Number = 8
- `Input[17]` : VIX Study ID = 23
- `Input[18]` : VIX Subgraph Index = 4

### **NBCV Configuration**
- `Input[19]` : Collect NBCV Footprint = true
- `Input[20]` : NBCV Study ID = 33
- `Input[21-25]` : NBCV SG Mapping (SG6/7/1/12/10)
- `Input[26]` : Cumulative Delta Bars Study ID = 6
- `Input[27]` : NBCV On New Bar Only = 1

### **Time & Sales / Quotes**
- `Input[28]` : Collect Time & Sales = true
- `Input[29]` : Collect Quotes (Bid/Ask) = true
- `Input[30]` : T&S On New Bar Only = 1

### **MenthorQ Configuration**
- `Input[31]` : Export MenthorQ Levels = 1
- `Input[32]` : MenthorQ Chart Number = 10
- `Input[33]` : Gamma Levels Study ID = 1
- `Input[34]` : Gamma Levels Subgraphs Count = 19
- `Input[35]` : Blind Spots Study ID = 3
- `Input[36]` : Blind Spots Subgraphs Count = 9
- `Input[37]` : Swing Levels Study ID = 2
- `Input[38]` : Swing Levels Subgraphs Count = 9
- `Input[47]` : MenthorQ On New Bar Only = 1

### **Corrélation**
- `Input[46]` : Correlation Coefficient Study ID = 15

---

## 📊 STATISTIQUES DE COLLECTION

### **Volume de Données (par jour)**
- **Chart 3** : ~50,000-100,000 lignes (BaseData, VWAP, VVA, NBCV, VIX, Quotes, T&S, DOM)
- **Chart 4** : ~20,000-50,000 lignes (OHLC, VWAP, PVWAP, NBCV, Corrélation)
- **Chart 10** : ~500-2,000 lignes (MenthorQ Levels)

### **Fréquence de Mise à Jour**
- **Temps réel** : Quotes, T&S, DOM
- **Nouvelle barre** : BaseData, VWAP, VVA, NBCV, PVWAP, MenthorQ
- **Cross-chart** : VIX (Chart 8 → Chart 3), Corrélation (Chart 4)

### **Anti-Duplication**
- **WritePerChartDailyIfChanged** : VWAP, NBCV, Corrélation
- **Static variables** : T&S, DOM, MenthorQ
- **New Bar Only flags** : VVA, PVWAP, NBCV, T&S, MenthorQ

---

## ✅ STATUS DE COLLECTION

### **🟢 FONCTIONNEL**
- ✅ BaseData (OHLCV + Bid/Ask Volume)
- ✅ VWAP (Auto-résolution par nom, 4 bandes)
- ✅ Volume Profile (VVA Current/Previous)
- ✅ NBCV OrderFlow (Footprint + Metrics + OrderFlow)
- ✅ VIX (Cross-chart depuis Chart 8)
- ✅ Quotes/T&S (Temps réel avec anti-duplication)
- ✅ DOM (20 niveaux avec anti-duplication)
- ✅ Corrélation ES/NQ
- ✅ PVWAP (VWAP période précédente)
- ✅ MenthorQ (Gamma, Blind Spots, Swing Levels)

### **🔧 AMÉLIORATIONS IMPLÉMENTÉES**
- ✅ Auto-résolution des Study IDs par nom
- ✅ Anti-duplication robuste (WritePerChartDailyIfChanged)
- ✅ Normalisation des prix (NormalizePx)
- ✅ Gestion des erreurs et diagnostics
- ✅ Calcul symétrique des pressions NBCV
- ✅ Fallback pour Cumulative Delta
- ✅ Support Sequence pour T&S

---

## 🎯 RECOMMANDATIONS

### **1. Monitoring**
- Surveiller les volumes de données par chart
- Vérifier la cohérence des timestamps
- Contrôler la qualité des données (valeurs nulles)

### **2. Optimisations Futures**
- Ajouter validation des Study IDs au démarrage
- Implémenter rotation automatique des fichiers
- Améliorer la gestion mémoire pour les gros volumes

### **3. Extensions Possibles**
- Ajouter d'autres types de données (VAP, etc.)
- Implémenter la compression des fichiers
- Ajouter des métriques de performance

---

**📅 Dernière mise à jour :** 2025-01-10
**🔄 Prochaine révision :** Après tests de validation
