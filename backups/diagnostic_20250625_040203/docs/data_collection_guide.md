# Guide Collection de Données - MIA_IA_SYSTEM

## 🎯 **INTRODUCTION**

Ce guide détaille le système de collection de données du MIA_IA_SYSTEM, conçu pour capturer **TOUT** : chaque signal Battle Navale, chaque décision, chaque résultat. Ces données alimentent l'amélioration continue de votre méthode propriétaire et les modèles ML.

### **🏗️ Architecture Data Collection**
```
📊 Sources : IBKR + Sierra Chart + Battle Navale
🔄 Pipeline : Capture → Structure → Store → Analyze
🎯 Objectif : Dataset ML + Performance Analytics
⚡ Fréquence : Temps réel + Snapshots détaillés
```

---

## ⚙️ **1. CONFIGURATION SOURCES DONNÉES**

### **1.1 Configuration Data Collector**
```python
# Dans config/automation_config.py
DATA_COLLECTION_CONFIG = {
    'enabled': True,
    'real_time': True,
    'snapshot_frequency': 'every_trade',
    'backup_frequency': 'hourly',
    
    # Sources de données
    'sources': {
        'ibkr_market_data': True,
        'sierra_chart_data': True,
        'battle_navale_signals': True,
        'system_metrics': True,
        'performance_data': True
    },
    
    # Stockage
    'storage': {
        'format': 'json',  # json, csv, parquet
        'compression': 'gzip',
        'retention_days': 365,
        'archive_after_days': 90
    }
}
```

### **1.2 Configuration Sources**

#### **IBKR Market Data**
```python
IBKR_DATA_CONFIG = {
    'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
    'data_types': [
        'BID_ASK',      # Prix bid/ask
        'TRADES',       # Trades exécutés
        'VOLUME',       # Volume
        'VOLATILITY'    # Volatilité implicite
    ],
    'timeframes': ['1min', '5min', '15min'],
    'market_hours_only': False,  # Capturer H24
}
```

#### **Sierra Chart Integration**
```python
SIERRA_DATA_CONFIG = {
    'chart_data': True,
    'order_flow': True,
    'volume_profile': True,
    'indicators': [
        'VWAP',
        'BOLLINGER',
        'RSI',
        'CUSTOM_BATTLE_NAVALE'  # Vos indicateurs spécifiques
    ]
}
```

#### **Battle Navale Signals**
```python
BATTLE_NAVALE_DATA_CONFIG = {
    'capture_all_signals': True,
    'include_features': True,      # Vos 8 features
    'include_confluence': True,    # Scores confluence
    'include_regime': True,        # Trend/Range detection
    'signal_quality_score': True,
    'execution_context': True
}
```

### **1.3 Test Configuration**
```bash
# Test des sources de données
python -m data.data_collector --test-sources

# Vérification connexions
python -c "
from data.market_data_feed import MarketDataFeed
feed = MarketDataFeed()
print(f'IBKR: {feed.test_ibkr_connection()}')
print(f'Sierra: {feed.test_sierra_connection()}')
"
```

---

## 📁 **2. ORGANISATION FICHIERS**

### **2.1 Structure des Données**
```
data/
├── snapshots/                    # Snapshots détaillés trades
│   ├── daily/                   # Données journalières
│   │   ├── 2025-06-23/
│   │   │   ├── trades.json      # Tous les trades du jour
│   │   │   ├── signals.json     # Signaux Battle Navale
│   │   │   ├── market_data.json # Données marché
│   │   │   └── performance.json # Métriques performance
│   │   └── 2025-06-24/
│   └── archive/                 # Données archivées (>90 jours)
│       ├── 2025-01/
│       ├── 2025-02/
│       └── compressed/
├── live/                        # Données temps réel
│   ├── current_session/         # Session trading actuelle
│   │   ├── live_signals.json
│   │   ├── open_positions.json
│   │   └── system_status.json
│   └── streaming/               # Flux temps réel
├── processed/                   # Données traitées pour ML
│   ├── features_dataset.parquet
│   ├── labels_dataset.parquet
│   └── ml_ready/
└── backups/                     # Sauvegardes
    ├── hourly/
    ├── daily/
    └── weekly/
```

### **2.2 Format des Snapshots**

#### **Trade Snapshot**
```json
{
    "timestamp": "2025-06-23T14:30:15.123Z",
    "trade_id": "TRADE_20250623_143015_001",
    "symbol": "EURUSD",
    "action": "BUY",
    "quantity": 10000,
    "price": 1.0891,
    
    "battle_navale": {
        "signal_type": "VIKINGS_ATTACK",
        "pattern": "elite_pattern_2",
        "confluence_score": 0.87,
        "features": {
            "feature_1": 0.65,
            "feature_2": -0.23,
            "feature_3": 1.42,
            "feature_4": 0.78,
            "feature_5": -0.91,
            "feature_6": 2.15,
            "feature_7": 0.33,
            "feature_8": -1.67
        },
        "market_regime": "TRENDING",
        "strength": "HIGH"
    },
    
    "market_context": {
        "bid": 1.0890,
        "ask": 1.0892,
        "spread": 0.0002,
        "volume": 1250000,
        "volatility": 0.0145
    },
    
    "execution": {
        "order_id": "ORD_12345",
        "fill_price": 1.0891,
        "slippage": 0.0001,
        "latency_ms": 2.3,
        "commission": 0.50
    },
    
    "risk_management": {
        "position_size_pct": 0.015,
        "stop_loss": 1.0851,
        "take_profit": 1.0931,
        "risk_reward_ratio": 2.0,
        "portfolio_heat": 0.045
    }
}
```

#### **Signal Snapshot**
```json
{
    "timestamp": "2025-06-23T14:29:45.678Z",
    "signal_id": "SIG_20250623_142945_001",
    "symbol": "EURUSD",
    "timeframe": "5min",
    
    "battle_navale_analysis": {
        "primary_pattern": "elite_pattern_2",
        "secondary_patterns": ["support_pattern_a"],
        "confluence_levels": {
            "technical": 0.85,
            "fundamental": 0.72,
            "sentiment": 0.91,
            "overall": 0.83
        },
        "vikings_defenseurs": {
            "mode": "VIKINGS_DOMINANT",
            "strength": 8.5,
            "momentum": "INCREASING"
        }
    },
    
    "features_snapshot": {
        "calculation_timestamp": "2025-06-23T14:29:45.100Z",
        "raw_features": [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
        "normalized_features": [0.52, -0.18, 1.15, 0.63, -0.74, 1.75, 0.27, -1.35],
        "feature_importance": [0.15, 0.08, 0.22, 0.18, 0.12, 0.09, 0.07, 0.09]
    },
    
    "decision": {
        "action": "BUY",
        "confidence": 0.87,
        "reasoning": "High confluence + Elite pattern 2 + Vikings dominance",
        "executed": true,
        "execution_delay_ms": 1.8
    }
}
```

### **2.3 Gestion des Fichiers**
```bash
# Structure automatique des dossiers
python data/data_collector.py --create-structure

# Vérification intégrité
python data/data_collector.py --check-integrity

# Nettoyage automatique
python scripts/cleanup_data.py --older-than=365days
```

---

## 📤 **3. EXPORT POUR ML**

### **3.1 Pipeline de Transformation**
```python
# Dans data/data_processor.py
class MLDatasetBuilder:
    def __init__(self):
        self.features_count = 8  # Vos features Battle Navale
        self.lookback_periods = [5, 10, 15, 30]  # Contexte temporel
        
    def build_features_dataset(self, start_date, end_date):
        """
        Construit le dataset ML à partir des snapshots
        """
        # 1. Collecte des snapshots
        snapshots = self.load_snapshots(start_date, end_date)
        
        # 2. Extraction features
        features_matrix = self.extract_features(snapshots)
        
        # 3. Création labels (succès/échec trades)
        labels = self.create_labels(snapshots)
        
        # 4. Features engineering
        enhanced_features = self.feature_engineering(features_matrix)
        
        return enhanced_features, labels
```

### **3.2 Features Engineering**
```python
# Génération features ML
FEATURE_ENGINEERING = {
    'temporal_features': {
        'rolling_means': [5, 10, 20],      # Moyennes mobiles
        'rolling_stds': [5, 10, 20],       # Volatilités
        'momentum': [3, 7, 14],            # Momentum sur N périodes
        'rate_of_change': [5, 10]          # Taux de changement
    },
    
    'battle_navale_features': {
        'pattern_frequency': True,          # Fréquence patterns
        'confluence_history': True,        # Historique confluence
        'success_rate_by_pattern': True,   # Taux succès par pattern
        'market_regime_stability': True    # Stabilité régime marché
    },
    
    'interaction_features': {
        'feature_correlations': True,      # Corrélations entre features
        'feature_ratios': True,            # Ratios features importantes
        'composite_indicators': True       # Indicateurs composites
    }
}
```

### **3.3 Export Formats**

#### **CSV Export**
```bash
# Export CSV pour analyse externe
python scripts/export_ml_data.py --format=csv --period=last_month

# Génère :
# - features_dataset_202506.csv (features + labels)
# - metadata_202506.json (métadonnées)
# - statistics_202506.json (statistiques descriptives)
```

#### **Parquet Export**
```bash
# Export Parquet pour performance
python scripts/export_ml_data.py --format=parquet --compression=snappy

# Optimisé pour :
# - Chargement rapide en Python/R
# - Compression efficace
# - Types de données préservés
```

#### **JSON Export**
```bash
# Export JSON pour flexibilité
python scripts/export_ml_data.py --format=json --include-metadata

# Inclut :
# - Structure complète des données
# - Métadonnées Battle Navale
# - Contexte de génération
```

### **3.4 Validation Dataset**
```python
# Script de validation automatique
python scripts/validate_ml_dataset.py --dataset=features_dataset.parquet

# Vérifications :
# - Pas de valeurs manquantes critiques
# - Distribution des labels équilibrée
# - Corrélations features acceptables
# - Pas de data leakage temporel
```

---

## 🔧 **4. MAINTENANCE**

### **4.1 Monitoring Collection**
```python
# Dashboard monitoring data collection
DATA_MONITORING = {
    'metrics': {
        'snapshots_per_hour': 'target: 50-200',
        'data_quality_score': 'target: >0.95',
        'missing_data_rate': 'target: <0.01',
        'storage_growth_rate': 'monitor: MB/day'
    },
    
    'alerts': {
        'collection_stopped': 'CRITICAL',
        'data_quality_low': 'WARNING',
        'storage_full': 'CRITICAL',
        'backup_failed': 'WARNING'
    }
}
```

### **4.2 Automated Maintenance**
```bash
# Tâches automatiques quotidiennes
0 2 * * * python scripts/backup_data.py --daily
0 3 * * * python scripts/cleanup_data.py --optimize
0 4 * * * python scripts/validate_data_integrity.py

# Tâches hebdomadaires
0 1 * * 0 python scripts/archive_old_data.py
0 2 * * 0 python scripts/generate_ml_dataset.py --weekly
```

### **4.3 Optimisation Performance**
```python
# Configuration optimisation
PERFORMANCE_OPTIMIZATION = {
    'compression': {
        'algorithm': 'lz4',  # Compression rapide
        'level': 1,          # Niveau compression/vitesse
        'batch_size': 1000   # Compression par batch
    },
    
    'indexing': {
        'timestamp_index': True,
        'symbol_index': True, 
        'trade_id_index': True
    },
    
    'caching': {
        'memory_cache_mb': 512,
        'disk_cache_gb': 2,
        'cache_strategy': 'LRU'
    }
}
```

### **4.4 Backup et Recovery**

#### **Stratégie Backup**
```bash
# Backup incrémental horaire
python scripts/backup_data.py --incremental --hourly

# Backup complet quotidien
python scripts/backup_data.py --full --daily

# Backup archive hebdomadaire
python scripts/backup_data.py --archive --weekly
```

#### **Recovery Procedures**
```bash
# Recovery données corrompues
python scripts/recovery_data.py --validate-and-repair

# Recovery depuis backup
python scripts/recovery_data.py --restore-from-backup --date=2025-06-23

# Recovery partielle
python scripts/recovery_data.py --restore-trades --trade-ids=file.txt
```

---

## 📊 **5. ANALYSES AVANCÉES**

### **5.1 Data Quality Analytics**
```python
# Analyse qualité données
python scripts/analyze_data_quality.py --comprehensive

# Génère :
# - Rapport complétude données
# - Détection anomalies
# - Validation cohérence
# - Recommandations amélioration
```

### **5.2 Performance Analytics**
```python
# Analyse performance Battle Navale
python scripts/analyze_battle_navale_performance.py --timeframe=monthly

# Métriques analysées :
# - Taux succès par pattern
# - Performance par confluence score
# - Efficacité par régime marché
# - Évolution temporelle performance
```

### **5.3 Feature Importance Analysis**
```bash
# Analyse importance features
python scripts/analyze_feature_importance.py --method=permutation

# Outputs :
# - Ranking importance features
# - Corrélations features-performance
# - Suggestions optimisation
# - Visualisations interactives
```

---

## 🎯 **COMMANDES ESSENTIELLES**

### **5.1 Collection de Données**
```bash
# Démarrage collection
python data_collection_main.py --start

# Status collection
python data_collection_main.py --status

# Arrêt collection
python data_collection_main.py --stop
```

### **5.2 Export ML**
```bash
# Export rapide dataset
python scripts/export_ml_data.py --quick

# Export complet avec validation
python scripts/export_ml_data.py --full --validate

# Export personnalisé
python scripts/export_ml_data.py --custom --config=export_config.json
```

### **5.3 Maintenance**
```bash
# Vérification santé données
python scripts/data_health_check.py

# Optimisation stockage
python scripts/optimize_storage.py --compress --index

# Génération rapport
python scripts/generate_data_report.py --comprehensive
```

---

## ✅ **CHECKLIST COLLECTION DONNÉES**

### **Setup Initial**
- [ ] Configuration sources données
- [ ] Test connexions IBKR/Sierra
- [ ] Création structure dossiers
- [ ] Validation format snapshots

### **Monitoring Quotidien**
- [ ] Vérifier collection temps réel
- [ ] Contrôler qualité données
- [ ] Surveiller espace stockage
- [ ] Valider backups

### **Maintenance Hebdomadaire**
- [ ] Archivage données anciennes
- [ ] Génération dataset ML
- [ ] Analyse performance collection
- [ ] Optimisation stockage

### **Analyse Mensuelle**
- [ ] Rapport qualité données complet
- [ ] Analyse feature importance
- [ ] Validation pipeline ML
- [ ] Optimisation paramètres collection

---

**📊 Votre système de collection données capture maintenant TOUT pour alimenter l'évolution de Battle Navale !**