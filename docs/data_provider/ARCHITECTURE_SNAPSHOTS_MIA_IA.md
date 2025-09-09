# 📋 ARCHITECTURE SNAPSHOTS MIA_IA_SYSTEM

## 🎯 Vue d'ensemble

Cette architecture définit les 3 familles de snapshots du système MIA_IA avec une fusion logique du VIX (CBOE) dans les snapshots Orderflow puisqu'ils partagent la même source technique (Sierra Chart).

---

## 📊 **TABLEAU COMPARATIF DES SNAPSHOTS**

| Snapshot | Source Technique | Fournisseur de Données | Contenu Principal | Fichier/Module | Utilisation MIA | Fréquence |
|----------|------------------|------------------------|-------------------|----------------|-----------------|-----------|
| **📊 Options SPX/NDX** | Polygon.io API | Polygon.io Options Chain | Call Wall, Put Wall, Gamma Flip, Max Pain, Pins, GEX, Greeks | `create_options_snapshot.py` | Dealer's Bias (75%) + Niveaux Sierra | Avant clôture US |
| **⚡ Orderflow + VIX** | Sierra Chart DTC | Sierra Pack 12 + Denali CME + CBOE | ES/NQ tick, DOM, Footprint, Volume Profile, VIX officiel, VXN | `orderflow_snapshots/` | Battle Navale (60%) + Dealer's Bias (25%) | Temps réel continu |
| **🎯 Trades Execution** | MIA Engine | Interne (via Sierra DTC) | Timestamp, Prix, Side, P&L, Features snapshot | `trade_snapshots/` | Validation ML + Backtest + Performance | À chaque trade |

---

## 📋 **DÉTAIL DES SNAPSHOTS**

### **1. 📊 Snapshots Options (SPX / NDX)**

#### **🔧 Configuration technique :**
```python
SNAPSHOTS_OPTIONS = {
    'source': 'Polygon.io API',
    'endpoint': 'Options Chain Snapshot',
    'symbols': ['SPX', 'NDX'],
    'fichier': 'create_options_snapshot.py',
    'format_sortie': 'JSON + CSV ultra-léger Sierra'
}
```

#### **📊 Contenu détaillé :**
```
✅ Call Wall (résistance gamma majeure)
✅ Put Wall (support gamma majeur)  
✅ Gamma Flip (niveau pivot dealers)
✅ Max Pain (aimantation Open Interest)
✅ Gamma Pins 1-2 (zones de pinning)
✅ Vol Trigger (seuils volatilité, optionnel)
✅ GEX total signé (exposition gamma globale)
✅ Net Gamma / Net Delta (position dealers)
✅ Put/Call Ratios (volume + OI)
✅ IV Skew (puts vs calls)
```

#### **🎯 Utilisation dans MIA :**
- **Dealer's Bias (75%)** : PCR, Skew, GEX, Gamma analysis
- **Niveaux Sierra Chart** : Import CSV → lignes horizontales automatiques
- **Persistance** : Garde dernier snapshot quand marché options fermé
- **Timing** : Collecte avant clôture US pour sessions Asia/London

---

### **2. ⚡ Snapshots Orderflow + Volatilité (ES/NQ + VIX/VXN)**

#### **🔧 Configuration technique :**
```python
SNAPSHOTS_ORDERFLOW = {
    'source': 'Sierra Chart DTC + Denali + CBOE',
    'connections': {
        'es_port': 11099,
        'nq_port': 11100,
        'vix_feed': 'CBOE Global Indexes'
    },
    'fichier': 'orderflow_snapshots/',
    'format_sortie': 'JSON temps réel'
}
```

#### **📊 Contenu détaillé :**
```
ES/NQ FUTURES:
✅ Tick par tick (prix, volume, timestamp)
✅ DOM complet (10 niveaux bid/ask)
✅ Footprint (volume par niveau de prix)
✅ Volume Profile (VAH, VAL, POC)
✅ Sierra Patterns (long down/up bar, climax)
✅ Cumulative Delta (pression achat/vente)
✅ Order Book Imbalance (déséquilibre DOM)

VOLATILITÉ (FUSION VIX):
✅ VIX officiel temps réel (CBOE)
✅ VXN optionnel (volatilité Nasdaq)
✅ Term Structure (si disponible)
✅ Volatility Regime (High/Normal/Low Vol)
```

#### **🎯 Utilisation dans MIA :**
- **Battle Navale (60%)** : Features microstructure orderflow
- **Smart Money Tracker** : Détection gros ordres institutionnels
- **Volume Confirmation** : Validation signals via volume
- **Dealer's Bias (25%)** : Composant VIX pour volatility regime
- **Trading Execution** : DOM en temps réel pour slippage control
- **VWAP Analysis** : Calculs VWAP bands et trends

---

### **3. 🎯 Snapshots Trades (Exécutions)**

#### **🔧 Configuration technique :**
```python
SNAPSHOTS_TRADES = {
    'source': 'MIA Engine (via Sierra DTC)',
    'trigger': 'À chaque order fill',
    'fichier': 'trade_snapshots/',
    'format_sortie': 'JSON structuré + CSV ML'
}
```

#### **📊 Contenu détaillé :**
```
TRADE DATA:
✅ Timestamp exact (entry + exit)
✅ Symbol (ES/NQ)
✅ Side (BUY/SELL)
✅ Quantity (contracts)
✅ Price (entry + exit)
✅ P&L réalisé (ticks + USD)
✅ Slippage (vs prix théorique)
✅ Execution time (ms)

FEATURES SNAPSHOT:
✅ Battle Navale score au moment du signal
✅ Dealer's Bias score
✅ Confluence des features (28 features)
✅ Market regime (TREND/RANGE/VOLATILE)
✅ Session context (Asia/London/US)
✅ VIX level au moment du trade
```

#### **🎯 Utilisation dans MIA :**
- **Validation ML** : Ensemble Filter training
- **Backtest continu** : Performance analysis temps réel
- **Réentraînement adaptatif** : Amélioration modèles
- **Risk Management** : Drawdown tracking
- **Performance Analytics** : Win rate, profit factor, Sharpe ratio

---

## 🔄 **FLUX DE DONNÉES INTÉGRÉ**

### **Workflow snapshots en temps réel :**

```python
# 1. COLLECTE CONTINUE (Orderflow + VIX)
async def collect_realtime_snapshots():
    sierra = SierraDTCConnector()
    
    while trading_active:
        # Données ES/NQ + VIX en une seule source
        orderflow_data = await sierra.get_orderflow_data()
        vix_data = await sierra.get_vix_data()
        
        # Snapshot unifié
        snapshot = {
            'orderflow': orderflow_data,
            'volatility': vix_data,
            'timestamp': datetime.now(),
            'source': 'Sierra Chart Unified'
        }
        
        # Alimente Battle Navale + Dealer's Bias VIX component
        await process_orderflow_snapshot(snapshot)

# 2. COLLECTE QUOTIDIENNE (Options)
async def collect_daily_options():
    polygon = PolygonConnector()
    
    # Avant clôture US (15:30 EST)
    if is_pre_close_time():
        options_data = await polygon.get_spx_options_levels()
        
        # Génère niveaux pour Sierra + Dealer's Bias
        snapshot = create_options_snapshot(options_data)
        
        # Export CSV pour Sierra Chart
        export_sierra_levels_csv(snapshot)

# 3. COLLECTE TRADES (À chaque exécution)
async def collect_trade_snapshot(trade_result):
    # Capture état complet au moment du trade
    snapshot = {
        'trade_data': trade_result,
        'market_context': get_current_market_state(),
        'features': get_current_features(),
        'dealer_bias': get_current_dealer_bias(),
        'timestamp': datetime.now()
    }
    
    # Stockage pour ML et analytics
    await store_trade_snapshot(snapshot)
```

---

## 📁 **STRUCTURE FICHIERS SNAPSHOTS**

### **Organisation des répertoires :**

```
data/snapshots/
├── options/                     # Snapshots options SPX/NDX
│   ├── spx_snapshot_YYYYMMDD_HHMMSS.json
│   ├── ndx_snapshot_YYYYMMDD_HHMMSS.json
│   └── sierra_levels_YYYYMMDD.csv    # Export Sierra Chart
│
├── orderflow/                   # Snapshots orderflow + VIX unifié
│   ├── es_orderflow_YYYYMMDD/
│   │   ├── es_tick_data_HHMMSS.json
│   │   ├── es_dom_HHMMSS.json
│   │   └── es_patterns_HHMMSS.json
│   ├── nq_orderflow_YYYYMMDD/
│   └── vix_data_YYYYMMDD.json        # VIX intégré
│
├── trades/                      # Snapshots executions
│   ├── trades_YYYYMMDD.json
│   ├── performance_daily_YYYYMMDD.json
│   └── ml_features_YYYYMMDD.csv      # Dataset ML
│
└── archive/                     # Archivage automatique
    ├── options_archive_YYYYMM.gz
    ├── orderflow_archive_YYYYMM.gz
    └── trades_archive_YYYYMM.gz
```

---

## ⚡ **OPTIMISATIONS PERFORMANCE**

### **Cache intelligent :**
```python
CACHE_CONFIG = {
    'options_snapshots': {
        'ttl_seconds': 14400,       # 4h (marché options)
        'max_size': 100,            # 100 snapshots max
        'compression': 'gzip'
    },
    'orderflow_snapshots': {
        'ttl_seconds': 60,          # 1min (temps réel)
        'max_size': 1000,           # Buffer 1000 snapshots
        'compression': None         # Pas de compression (speed)
    },
    'trade_snapshots': {
        'ttl_seconds': 86400,       # 24h (analytics)
        'max_size': 10000,          # 10k trades
        'compression': 'lz4'        # Compression rapide
    }
}
```

### **Monitoring qualité :**
```python
QUALITY_METRICS = {
    'options_snapshots': {
        'completeness_min': 95,     # 95% données présentes
        'freshness_max': 900,       # 15min max age
        'strikes_min': 20           # 20 strikes minimum
    },
    'orderflow_snapshots': {
        'completeness_min': 99,     # 99% données présentes
        'freshness_max': 5,         # 5s max age
        'dom_levels_min': 5         # 5 niveaux DOM minimum
    },
    'trade_snapshots': {
        'completeness_min': 100,    # 100% données trade
        'features_count_min': 25,   # 25 features minimum
        'execution_time_max': 1000  # 1s max execution
    }
}
```

---

## 🎯 **AVANTAGES DE CETTE ARCHITECTURE**

### ✅ **Fusion logique VIX + Orderflow :**
- **Une seule source technique** : Sierra Chart
- **Synchro parfaite** : VIX et ES/NQ en temps réel
- **Simplicité** : Pas de gestion multi-sources
- **Performance** : Moins de connexions réseau

### ✅ **Spécialisation claire :**
- **Polygon** : Excellence options SPX/NDX
- **Sierra** : Excellence orderflow + VIX officiel
- **MIA** : Excellence execution tracking

### ✅ **Optimisation coûts :**
- **VIX inclus** dans CBOE Global Indexes ($6/mois)
- **Pas de doublon** : VIX proxy vs VIX officiel
- **Architecture unifiée** : Moins de complexity

---

## 📋 **CHECKLIST IMPLÉMENTATION**

### **Phase 1 - Snapshots Options :**
- [ ] Configurer Polygon.io connector
- [ ] Implémenter create_options_snapshot.py
- [ ] Tester collecte SPX/NDX
- [ ] Valider calculs Dealer's Bias
- [ ] Export CSV Sierra Chart

### **Phase 2 - Snapshots Orderflow + VIX :**
- [ ] Configurer Sierra Chart DTC
- [ ] Activer CBOE Global Indexes
- [ ] Implémenter orderflow_snapshots/
- [ ] Tester collecte ES/NQ + VIX unifié
- [ ] Valider features Battle Navale

### **Phase 3 - Snapshots Trades :**
- [ ] Implémenter trade_snapshots/
- [ ] Intégrer avec execution engine
- [ ] Configurer ML features capture
- [ ] Tester analytics pipeline
- [ ] Valider backtest integration

---

*Document créé le : 29 Août 2025*  
*Version : 1.0*  
*Auteur : MIA_IA_SYSTEM Team*  
*Architecture : 3 familles snapshots optimisées*  
*Status : ✅ FUSION VIX + ORDERFLOW VALIDÉE*


