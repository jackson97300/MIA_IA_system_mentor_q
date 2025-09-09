# MIA_IA_DataGenerator - Documentation Complète

## 📋 Vue d'ensemble

Le `MIA_IA_DataGenerator` est un générateur de données de marché synthétiques spécialement conçu pour le système MIA_IA. Il produit des données réalistes et cohérentes pour le backtesting, incluant tous les composants nécessaires au pipeline de trading automatisé.

### 🎯 Objectifs

- **Génération de données complètes** : L1, L2, Bars, Footprint, Contexte Options, Leadership Features, Ground Truth
- **Scénarios réalistes** : Simulation de conditions de marché variées (trend, chop, news, gamma pinning, etc.)
- **Intégration MIA_IA** : Support des patterns spécifiques (orderflow, confluence, delta divergence)
- **Pipeline compatible** : Export direct vers format Parquet pour backtesting

## 🏗️ Architecture

### Structure des données générées

```python
{
    "l1": DataFrame,           # Level 1 - Trades et quotes
    "l2": DataFrame,           # Level 2 - Order book simplifié
    "bars": DataFrame,         # OHLCV + VWAP bands
    "footprint": DataFrame,    # Delta par bar et niveau pivot
    "context": DataFrame,      # Contexte options enrichi
    "leadership_features": DataFrame,  # Features de leadership MIA_IA
    "ground_truth": DataFrame  # Labels pour validation
}
```

### Colonnes par DataFrame

#### L1 (Level 1)
- `ts`: Timestamp (epoch_ms)
- `symbol`: Symbole (ES/NQ)
- `bid`: Prix bid
- `ask`: Prix ask
- `last_price`: Dernier prix de trade
- `bid_size`: Taille bid
- `ask_size`: Taille ask
- `last_size`: Taille du dernier trade

#### L2 (Level 2)
- `ts`: Timestamp (epoch_ms)
- `symbol`: Symbole (ES/NQ)
- `levels`: Nombre de niveaux
- `bid_px`: Liste des prix bid
- `bid_sz`: Liste des tailles bid
- `ask_px`: Liste des prix ask
- `ask_sz`: Liste des tailles ask
- `mid`: Prix médian
- `spread`: Spread bid-ask

#### Bars (OHLCV)
- `ts`: Timestamp (epoch_ms)
- `symbol`: Symbole (ES/NQ)
- `open`: Prix d'ouverture
- `high`: Prix maximum
- `low`: Prix minimum
- `close`: Prix de fermeture
- `volume`: Volume
- `vwap`: Volume Weighted Average Price
- `vwap_sd1`: VWAP + 1 écart-type
- `vwap_sd2`: VWAP + 2 écarts-types

#### Footprint
- `bar_start_ts`: Timestamp début de bar
- `symbol`: Symbole (ES/NQ)
- `price_level`: Niveau de prix pivot
- `bid_volume`: Volume bid
- `ask_volume`: Volume ask
- `delta`: Delta (ask_volume - bid_volume)

#### Context (Options)
- `ts`: Timestamp (epoch_ms)
- `vix`: Niveau VIX
- `gamma_flip`: Niveau de flip gamma
- `call_wall`: Mur de calls
- `put_wall`: Mur de puts
- `pin_strength`: Force de pinning
- `put_call_ratio`: Ratio put/call

#### Leadership Features
- `ts`: Timestamp (epoch_ms)
- `symbol`: Symbole (ES/NQ)
- `confluence_score`: Score de confluence
- `delta_divergence`: Divergence delta
- `volume_imbalance`: Déséquilibre volume
- `sierra_pattern_strength`: Force pattern Sierra
- `leadership_strength`: Force de leadership
- `volatility_regime`: Régime de volatilité
- `options_flow_bias`: Biais flux options
- `gamma_proximity`: Proximité gamma

#### Ground Truth
- `ts`: Timestamp (epoch_ms)
- `symbol`: Symbole (ES/NQ)
- `label`: Label prédictif
- `confidence`: Confiance du label
- `side`: Direction (1=long, -1=short, 0=neutre)

## 🎮 Scénarios disponibles

### Scénarios de base
- **`normal`**: Marché équilibré, volatilité standard
- **`trend_up`**: Tendance haussière soutenue
- **`trend_down`**: Tendance baissière soutenue
- **`chop`**: Marché en range, faible volatilité
- **`news_spike`**: Pic de volatilité (événement)
- **`gamma_pin`**: Pinning gamma, faible volatilité

### Scénarios MIA_IA spécifiques
- **`orderflow_accumulation`**: Accumulation sous résistance, breakout haussier
- **`orderflow_distribution`**: Distribution sur support, flush baissier
- **`confluence_breakout`**: Alignement VWAP + leadership, breakout propre
- **`delta_divergence`**: Divergence prix vs delta (30-60s)

## 🚀 Utilisation rapide

### Installation et import

```python
from datetime import datetime, timezone
from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
```

### Exemple de base

```python
# Initialisation
gen = MIA_IA_DataGenerator(seed=42)
cfg = GenConfig(
    start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
    minutes=120  # 2 heures de données
)

# Génération simple
data = gen.generate_realistic_session(cfg, scenario="normal")

# Accès aux données
l1_data = data["l1"]
bars_data = data["bars"]
context_data = data["context"]
```

### Exemple avancé avec leadership

```python
# Configuration avec leadership NQ
data = gen.generate_realistic_session(
    cfg,
    scenario="confluence_breakout",
    leadership="NQ_leads",  # NQ_leads | ES_leads | balanced
    strength=0.18,          # Force du leadership (0.0-0.4)
    options_context=True,
    include_labels=True
)
```

## ⚙️ Configuration

### GenConfig

```python
@dataclass
class GenConfig:
    start: datetime              # Timestamp de début (UTC)
    minutes: int = 120          # Durée de session
    symbol_es: str = "ES"       # Symbole ES
    symbol_nq: str = "NQ"       # Symbole NQ
    tick_size: float = 0.25     # Taille de tick
    es_start_price: float = 5000.0    # Prix de départ ES
    nq_start_price: float = 18000.0   # Prix de départ NQ
    l1_interval_ms: int = 200   # Intervalle L1 (~5 ticks/sec)
    l2_interval_ms: int = 100   # Intervalle L2 (~10 snapshots/sec)
    bar_tf_s: int = 1           # Timeframe bars (secondes)
    book_levels: int = 10       # Niveaux order book
    base_size_mean: int = 3     # Taille moyenne trades
    base_size_std: int = 2      # Écart-type taille trades
    vix_start: float = 15.0     # VIX de départ
```

### Paramètres de génération

```python
def generate_realistic_session(
    self,
    cfg: GenConfig,
    scenario: str = "normal",
    leadership: str = "NQ_leads",     # NQ_leads | ES_leads | balanced
    strength: float = 0.15,           # 0.0-0.4 (corrélation & momentum)
    options_context: bool = True,     # Inclure contexte options
    include_labels: bool = True,      # Inclure ground truth
) -> Dict[str, pd.DataFrame]:
```

## 🔧 Fonctionnalités avancées

### Export Parquet

```python
# Export direct vers fichiers Parquet
MIA_IA_DataGenerator.export_to_parquet(
    data,
    output_dir="./data/backtest/"
)
```

### Validation des données

```python
# Vérification des invariants
assert (l1_data["ask"] > l1_data["bid"]).all()  # ask > bid
assert (bars_data["high"] >= bars_data["low"]).all()  # OHLC cohérent
assert (gt_data.loc[gt_data["label"] == "long_bias", "side"] == 1).all()  # Labels cohérents
```

### Personnalisation des scénarios

```python
# Application de patterns spécifiques
def _apply_mia_scenarios(self, cfg, df_l1, df_bars, scenario):
    # Injection de signatures orderflow
    # Modification des tailles bid/ask
    # Ajustement des prix
    # Recalcul des bars
```

## 📊 Exemples de données générées

### L1 Sample
```
ts                    symbol  bid     ask     last_price  bid_size  ask_size  last_size
1734787800000        ES      4999.75  5000.00  4999.75      150       200        3
1734787800200        ES      4999.75  5000.00  5000.00      180       190        2
1734787800400        NQ      17999.50 18000.00 17999.75     120       160        4
```

### Bars Sample
```
ts                    symbol  open    high    low     close   volume  vwap
1734787800000        ES      4999.75  5000.25  4999.50  5000.00  15      4999.88
1734787801000        ES      5000.00  5000.50  4999.75  5000.25  12      5000.12
1734787802000        NQ      17999.75 18000.50 17999.50 18000.25 18      17999.88
```

### Leadership Features Sample
```
ts                    symbol  confluence_score  delta_divergence  volume_imbalance  leadership_strength
1734787800000        ES      0.65              0.12              0.08              0.72
1734787800000        NQ      0.58              0.15              0.11              0.85
1734787801000        ES      0.68              0.09              0.06              0.71
```

### Ground Truth Sample
```
ts                    symbol  label           confidence  side
1734787800000        ES      long_bias       0.8         1
1734787800000        NQ      long_bias       0.8         1
1734787801000        ES      long_bias       0.8         1
```

## 🧪 Tests et validation

### Tests de base

```python
def test_shapes_and_invariants():
    """Test des formes et invariants critiques"""
    gen = MIA_IA_DataGenerator(seed=1)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=30)
    data = gen.generate_realistic_session(cfg, scenario="confluence_breakout")
    
    # Vérification des colonnes
    assert "ts" in data["l1"].columns
    assert "symbol" in data["bars"].columns
    
    # Vérification des invariants
    assert (data["l1"]["ask"] > data["l1"]["bid"]).all()
    assert (data["bars"]["high"] >= data["bars"]["low"]).all()
```

### Tests de scénarios

```python
def test_scenario_patterns():
    """Test des patterns de scénarios"""
    scenarios = ["orderflow_accumulation", "delta_divergence", "confluence_breakout"]
    
    for scenario in scenarios:
        data = gen.generate_realistic_session(cfg, scenario=scenario)
        
        # Vérification des labels
        if scenario == "orderflow_accumulation":
            assert "long_bias" in data["ground_truth"]["label"].values
        elif scenario == "delta_divergence":
            assert "divergence_warning" in data["ground_truth"]["label"].values
```

## 🔍 Détails techniques

### Algorithme de génération

1. **Trajectoires de prix** : Marche aléatoire avec drift et volatilité selon le scénario
2. **Corrélation ES/NQ** : Modélisation de la corrélation avec leadership
3. **L1 synthétique** : Génération de trades et quotes cohérents
4. **Application scénarios** : Injection de patterns MIA_IA spécifiques
5. **Recalcul bars** : Reconstruction des bars après modifications
6. **Contexte options** : Génération de VIX, gamma, pinning
7. **Features leadership** : Calcul des métriques MIA_IA
8. **Ground truth** : Labels pour validation

### Gestion de la cohérence

- **Timestamps UTC** : Tous les timestamps en epoch_ms UTC
- **Prix cohérents** : bid < ask, OHLC respecté
- **Volumes réalistes** : Distribution poisson pour les tailles
- **Corrélation ES/NQ** : Modélisation réaliste du leadership
- **Options context** : VIX, gamma, pinning cohérents

### Performance

- **Génération rapide** : ~1000 ticks/sec sur CPU standard
- **Mémoire optimisée** : Utilisation efficace des DataFrames
- **Seed reproductible** : Résultats identiques avec même seed
- **Scalabilité** : Support de sessions longues (24h+)

## 🚨 Limitations et considérations

### Limitations actuelles

- **Données synthétiques** : Ne reflète pas exactement les conditions réelles
- **Corrélation simplifiée** : Modélisation basique ES/NQ
- **Options context** : Simulation simplifiée des options
- **Order book** : L2 simplifié (10 niveaux max)

### Bonnes pratiques

- **Seed fixe** : Utiliser un seed fixe pour la reproductibilité
- **Validation** : Toujours valider les invariants critiques
- **Scénarios multiples** : Tester avec différents scénarios
- **Export Parquet** : Utiliser pour le stockage long terme

## 🔗 Intégration avec le pipeline MIA_IA

### Compatibilité OfflineFeed

```python
from data.offline_feed import OfflineFeed

# Création d'un feed offline
feed = OfflineFeed(
    data_dir="./data/backtest/",
    symbols=["ES", "NQ"],
    start_date="2025-08-21",
    end_date="2025-08-21"
)
```

### Intégration backtesting

```python
# Utilisation dans le pipeline de backtesting
def run_backtest_with_synthetic_data():
    # Génération des données
    data = gen.generate_realistic_session(cfg, scenario="confluence_breakout")
    
    # Export pour backtesting
    MIA_IA_DataGenerator.export_to_parquet(data, "./backtest_data/")
    
    # Lancement du backtest
    # ... intégration avec le système MIA_IA
```

## 📈 Roadmap et améliorations

### Améliorations prévues

- **Données réelles** : Intégration de données historiques réelles
- **Options avancées** : Modélisation plus sophistiquée des options
- **Microstructure** : Simulation de la microstructure de marché
- **Multi-timeframe** : Support de timeframes multiples
- **Stress testing** : Scénarios de stress et crash

### Extensions possibles

- **Autres instruments** : Support d'autres futures/options
- **News events** : Simulation d'événements de marché
- **Liquidity modeling** : Modélisation de la liquidité
- **Market impact** : Impact des ordres sur le marché

---

## 📞 Support et contact

Pour toute question ou amélioration concernant le `MIA_IA_DataGenerator`, consulter la documentation du projet MIA_IA ou contacter l'équipe de développement.

**Version** : 1.0  
**Dernière mise à jour** : 2025-01-21  
**Compatibilité** : Python 3.8+, pandas, numpy




