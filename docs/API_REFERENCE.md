# MIA_IA_SYSTEM - RÉFÉRENCE API COMPLÈTE

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble API](#vue-densemble-api)
2. [Système principal](#système-principal)
3. [Intelligence artificielle](#intelligence-artificielle)
4. [Stratégies de trading](#stratégies-de-trading)
5. [Monitoring et surveillance](#monitoring-et-surveillance)
6. [Configuration](#configuration)
7. [Types de données](#types-de-données)
8. [Exemples d'utilisation](#exemples-dutilisation)

---

## 🎯 VUE D'ENSEMBLE API

### Architecture API

**MIA_IA_SYSTEM** expose une API modulaire avec les composants suivants :

- **🤖 Intelligence artificielle** : ML Ensemble, Gamma Cycles
- **📊 Stratégies trading** : Battle Navale, MTF Confluence
- **🛡️ Protection** : Catastrophe Monitor, Risk Manager
- **📈 Monitoring** : Surveillance temps réel
- **🎓 Coaching** : Mentor System

### Conventions de nommage

```python
# Classes principales
MIAAutomationSystem          # Système principal
AutomationConfig             # Configuration
MLEnsembleFilter            # ML Ensemble
GammaCyclesAnalyzer         # Gamma Cycles

# Méthodes
async def start()           # Démarrage asynchrone
def get_status()           # Statut synchrone
async def emergency_stop() # Arrêt d'urgence

# Types de données
MLPredictionResult         # Résultat ML
TradingSignal             # Signal trading
SystemMetrics             # Métriques système
```

---

## 🚀 SYSTÈME PRINCIPAL

### MIAAutomationSystem

**Fichier :** `automation_main.py`

**Description :** Classe principale orchestrant l'ensemble du système de trading automatisé.

#### Constructeur

```python
class MIAAutomationSystem:
    def __init__(self, config: AutomationConfig):
        """
        Initialiser le système MIA_IA_SYSTEM
        
        Args:
            config: Configuration du système
        """
```

#### Méthodes principales

##### start()
```python
async def start(self) -> None:
    """
    Démarrer le système de trading automatisé
    
    Raises:
        SystemError: Erreur de démarrage
        ConnectionError: Erreur de connexion IBKR
    """
```

##### stop()
```python
async def stop(self) -> None:
    """
    Arrêter le système de trading
    
    Raises:
        SystemError: Erreur d'arrêt
    """
```

##### emergency_stop()
```python
async def emergency_stop(self) -> None:
    """
    Arrêt d'urgence - ferme toutes les positions
    
    Raises:
        EmergencyStopError: Erreur lors de l'arrêt d'urgence
    """
```

##### get_status()
```python
def get_status(self) -> Dict[str, Any]:
    """
    Obtenir le statut complet du système
    
    Returns:
        Dict contenant le statut de tous les composants
    """
```

#### Exemple d'utilisation

```python
from automation_main import MIAAutomationSystem, AutomationConfig

# Configuration
config = AutomationConfig()
config.trading.max_position_size = 1
config.trading.daily_loss_limit = 200.0

# Créer et démarrer le système
system = MIAAutomationSystem(config)
await system.start()

# Obtenir le statut
status = system.get_status()
print(f"Statut: {status}")

# Arrêt
await system.stop()
```

---

## 🤖 INTELLIGENCE ARTIFICIELLE

### MLEnsembleFilter

**Fichier :** `ml/ensemble_filter.py`

**Description :** Système d'apprentissage automatique combinant Random Forest, XGBoost et Logistic Regression.

#### Constructeur

```python
class MLEnsembleFilter:
    def __init__(self, config: MLConfig = None):
        """
        Initialiser le filtre ML Ensemble
        
        Args:
            config: Configuration ML (optionnel)
        """
```

#### Méthodes principales

##### predict_signal_quality()
```python
def predict_signal_quality(self, features: Dict[str, float]) -> MLPredictionResult:
    """
    Prédire la qualité d'un signal de trading
    
    Args:
        features: Dictionnaire des features techniques
        
    Returns:
        MLPredictionResult: Résultat de la prédiction
        
    Raises:
        ValueError: Features invalides
        ModelNotTrainedError: Modèles non entraînés
    """
```

##### train_models()
```python
async def train_models(self, training_data: List[Dict]) -> bool:
    """
    Entraîner les modèles ML avec de nouvelles données
    
    Args:
        training_data: Données d'entraînement
        
    Returns:
        bool: True si entraînement réussi
        
    Raises:
        TrainingError: Erreur lors de l'entraînement
    """
```

##### get_model_performance()
```python
def get_model_performance(self) -> Dict[str, float]:
    """
    Obtenir les performances des modèles
    
    Returns:
        Dict: Métriques de performance par modèle
    """
```

#### Types de données

##### MLPredictionResult
```python
@dataclass
class MLPredictionResult:
    signal_approved: bool          # Signal approuvé
    confidence: float              # Confiance (0-1)
    ensemble_score: float          # Score ensemble
    individual_predictions: Dict[str, float]  # Prédictions individuelles
    model_weights: Dict[str, float]  # Poids des modèles
    features_importance: Dict[str, float]  # Importance des features
```

#### Exemple d'utilisation

```python
from ml.ensemble_filter import MLEnsembleFilter

# Créer le filtre
ml_filter = MLEnsembleFilter()

# Features de test
features = {
    "confluence_score": 0.75,
    "momentum_flow": 0.8,
    "trend_alignment": 0.7,
    "volume_profile": 0.6,
    "support_resistance": 0.5,
    "market_regime_score": 0.6,
    "volatility_regime": 0.5,
    "time_factor": 0.5
}

# Prédiction
result = ml_filter.predict_signal_quality(features)
print(f"Signal approuvé: {result.signal_approved}")
print(f"Confiance: {result.confidence:.3f}")
print(f"Score ensemble: {result.ensemble_score:.3f}")
```

### GammaCyclesAnalyzer

**Fichier :** `ml/gamma_cycles.py`

**Description :** Analyseur des cycles d'expiration des options pour optimiser les entrées/sorties.

#### Constructeur

```python
class GammaCyclesAnalyzer:
    def __init__(self, config: GammaCycleConfig):
        """
        Initialiser l'analyseur Gamma Cycles
        
        Args:
            config: Configuration Gamma Cycles
        """
```

#### Méthodes principales

##### analyze_gamma_cycle()
```python
def analyze_gamma_cycle(self) -> GammaAnalysisResult:
    """
    Analyser le cycle gamma actuel
    
    Returns:
        GammaAnalysisResult: Résultat de l'analyse
        
    Raises:
        DataError: Erreur de données
    """
```

##### get_expiry_dates()
```python
def get_expiry_dates(self) -> List[datetime]:
    """
    Obtenir les dates d'expiration futures
    
    Returns:
        List[datetime]: Dates d'expiration
    """
```

##### calculate_adjustment_factor()
```python
def calculate_adjustment_factor(self, days_to_expiry: int) -> float:
    """
    Calculer le facteur d'ajustement selon les jours jusqu'à expiration
    
    Args:
        days_to_expiry: Jours jusqu'à expiration
        
    Returns:
        float: Facteur d'ajustement (0.5-2.0)
    """
```

#### Types de données

##### GammaAnalysisResult
```python
@dataclass
class GammaAnalysisResult:
    gamma_phase: GammaPhase              # Phase gamma
    days_to_expiry: int                 # Jours jusqu'à expiration
    adjustment_factor: float             # Facteur d'ajustement
    volatility_expectation: VolatilityExpectation  # Attente volatilité
    recommended_position_size: float     # Taille position recommandée
    risk_level: RiskLevel               # Niveau de risque
```

##### GammaPhase (Enum)
```python
class GammaPhase(Enum):
    EXPIRY_WEEK = "expiry_week"         # Semaine expiration
    GAMMA_PEAK = "gamma_peak"           # Pic gamma
    GAMMA_MODERATE = "gamma_moderate"    # Gamma modéré
    NORMAL = "normal"                    # Normal
    POST_EXPIRY = "post_expiry"         # Post-expiration
```

#### Exemple d'utilisation

```python
from ml.gamma_cycles import GammaCyclesAnalyzer, GammaCycleConfig

# Configuration
config = GammaCycleConfig()
analyzer = GammaCyclesAnalyzer(config)

# Analyse
analysis = analyzer.analyze_gamma_cycle()
print(f"Phase: {analysis.gamma_phase.value}")
print(f"Jours jusqu'expiration: {analysis.days_to_expiry}")
print(f"Facteur ajustement: {analysis.adjustment_factor:.2f}")
print(f"Taille recommandée: {analysis.recommended_position_size:.2f}")
```

---

## 📊 STRATÉGIES DE TRADING

### BattleNavale

**Fichier :** `core/battle_navale.py`

**Description :** Stratégie propriétaire basée sur l'analyse des flux de capitaux.

#### Constructeur

```python
class BattleNavale:
    def __init__(self, config: BattleNavaleConfig):
        """
        Initialiser la stratégie Battle Navale
        
        Args:
            config: Configuration Battle Navale
        """
```

#### Méthodes principales

##### analyze_market_conditions()
```python
def analyze_market_conditions(self, market_data: MarketData) -> BattleNavaleAnalysis:
    """
    Analyser les conditions de marché
    
    Args:
        market_data: Données de marché
        
    Returns:
        BattleNavaleAnalysis: Résultat de l'analyse
    """
```

##### generate_signal()
```python
def generate_signal(self, analysis: BattleNavaleAnalysis) -> TradingSignal:
    """
    Générer un signal de trading
    
    Args:
        analysis: Analyse Battle Navale
        
    Returns:
        TradingSignal: Signal de trading
    """
```

##### calculate_position_size()
```python
def calculate_position_size(self, signal: TradingSignal, account_balance: float) -> int:
    """
    Calculer la taille de position selon Kelly Criterion
    
    Args:
        signal: Signal de trading
        account_balance: Solde du compte
        
    Returns:
        int: Taille de position
    """
```

#### Types de données

##### BattleNavaleAnalysis
```python
@dataclass
class BattleNavaleAnalysis:
    smart_money_flow: float              # Flux smart money
    momentum_score: float                # Score momentum
    volume_profile: VolumeProfile        # Profil volume
    pattern_detected: Optional[str]      # Pattern détecté
    confidence_level: float              # Niveau de confiance
    risk_assessment: RiskAssessment      # Évaluation risque
```

##### TradingSignal
```python
@dataclass
class TradingSignal:
    signal_type: SignalType              # Type de signal
    direction: SignalDirection           # Direction (LONG/SHORT)
    confidence: float                    # Confiance (0-1)
    entry_price: float                   # Prix d'entrée
    stop_loss: float                     # Stop loss
    take_profit: float                   # Take profit
    position_size: int                   # Taille position
    timestamp: datetime                  # Timestamp
    metadata: Dict[str, Any]            # Métadonnées
```

#### Exemple d'utilisation

```python
from core.battle_navale import BattleNavale, BattleNavaleConfig

# Configuration
config = BattleNavaleConfig()
strategy = BattleNavale(config)

# Analyser les conditions
analysis = strategy.analyze_market_conditions(market_data)
print(f"Smart money flow: {analysis.smart_money_flow:.3f}")
print(f"Confidence: {analysis.confidence_level:.3f}")

# Générer signal
signal = strategy.generate_signal(analysis)
print(f"Signal: {signal.signal_type.value}")
print(f"Direction: {signal.direction.value}")
print(f"Entry: {signal.entry_price}")
```

### MTFConfluenceElite

**Fichier :** `features/mtf_confluence_elite.py`

**Description :** Analyse multi-timeframe pour identifier les zones de confluence.

#### Constructeur

```python
class MTFConfluenceElite:
    def __init__(self, config: ConfluenceConfig):
        """
        Initialiser l'analyseur MTF Confluence
        
        Args:
            config: Configuration confluence
        """
```

#### Méthodes principales

##### analyze_confluence()
```python
def analyze_confluence(self, market_data: Dict[str, MarketData]) -> ConfluenceAnalysis:
    """
    Analyser la confluence multi-timeframe
    
    Args:
        market_data: Données par timeframe
        
    Returns:
        ConfluenceAnalysis: Résultat de l'analyse
    """
```

##### calculate_confluence_score()
```python
def calculate_confluence_score(self, signals: Dict[str, float]) -> float:
    """
    Calculer le score de confluence
    
    Args:
        signals: Signaux par timeframe
        
    Returns:
        float: Score de confluence (0-1)
    """
```

##### get_timeframe_weights()
```python
def get_timeframe_weights(self) -> Dict[str, float]:
    """
    Obtenir les poids des timeframes
    
    Returns:
        Dict[str, float]: Poids par timeframe
    """
```

#### Types de données

##### ConfluenceAnalysis
```python
@dataclass
class ConfluenceAnalysis:
    confluence_score: float              # Score confluence
    timeframe_signals: Dict[str, float]  # Signaux par timeframe
    strongest_timeframe: str             # Timeframe le plus fort
    weakest_timeframe: str               # Timeframe le plus faible
    alignment_direction: SignalDirection # Direction d'alignement
    confidence_level: float              # Niveau de confiance
    risk_level: RiskLevel                # Niveau de risque
```

#### Exemple d'utilisation

```python
from features.mtf_confluence_elite import MTFConfluenceElite, ConfluenceConfig

# Configuration
config = ConfluenceConfig()
analyzer = MTFConfluenceElite(config)

# Analyser confluence
analysis = analyzer.analyze_confluence(market_data)
print(f"Score confluence: {analysis.confluence_score:.3f}")
print(f"Direction: {analysis.alignment_direction.value}")
print(f"Confidence: {analysis.confidence_level:.3f}")
```

---

## 📈 MONITORING ET SURVEILLANCE

### ContinuousMonitor

**Fichier :** `monitoring_continu.py`

**Description :** Système de surveillance en temps réel du système.

#### Constructeur

```python
class ContinuousMonitor:
    def __init__(self, db_path: str = "data/monitoring.db"):
        """
        Initialiser le moniteur continu
        
        Args:
            db_path: Chemin de la base de données
        """
```

#### Méthodes principales

##### start_monitoring()
```python
async def start_monitoring(self, interval_seconds: int = 30) -> None:
    """
    Démarrer le monitoring continu
    
    Args:
        interval_seconds: Intervalle de collecte en secondes
    """
```

##### collect_system_metrics()
```python
async def collect_system_metrics(self) -> Optional[SystemMetrics]:
    """
    Collecter les métriques système
    
    Returns:
        SystemMetrics: Métriques système collectées
    """
```

##### save_metrics()
```python
async def save_metrics(self, metrics: SystemMetrics) -> bool:
    """
    Sauvegarder les métriques en base
    
    Args:
        metrics: Métriques à sauvegarder
        
    Returns:
        bool: True si sauvegarde réussie
    """
```

##### get_system_status()
```python
def get_system_status(self) -> Dict[str, Any]:
    """
    Obtenir le statut système actuel
    
    Returns:
        Dict: Statut système
    """
```

##### check_thresholds()
```python
def check_thresholds(self, metrics: SystemMetrics) -> List[Alert]:
    """
    Vérifier les seuils d'alerte
    
    Args:
        metrics: Métriques à vérifier
        
    Returns:
        List[Alert]: Alertes générées
    """
```

#### Types de données

##### SystemMetrics
```python
@dataclass
class SystemMetrics:
    timestamp: datetime                  # Timestamp
    cpu_percent: float                  # Usage CPU (%)
    memory_percent: float               # Usage mémoire (%)
    disk_usage_percent: float           # Usage disque (%)
    network_io: Dict[str, float]       # I/O réseau
    process_count: int                  # Nombre processus
    uptime: float                       # Temps fonctionnement (h)
```

##### Alert
```python
@dataclass
class Alert:
    timestamp: datetime                  # Timestamp
    level: str                          # Niveau (INFO/WARNING/CRITICAL)
    category: str                       # Catégorie
    message: str                        # Message
    details: Dict[str, Any]            # Détails
```

#### Exemple d'utilisation

```python
from monitoring_continu import ContinuousMonitor

# Créer le moniteur
monitor = ContinuousMonitor()

# Démarrer le monitoring
await monitor.start_monitoring(interval_seconds=30)

# Obtenir le statut
status = monitor.get_system_status()
print(f"CPU: {status.get('cpu_percent', 0):.1f}%")
print(f"Mémoire: {status.get('memory_percent', 0):.1f}%")

# Collecter métriques
metrics = await monitor.collect_system_metrics()
if metrics:
    print(f"Processus: {metrics.process_count}")
    print(f"Uptime: {metrics.uptime:.2f}h")
```

---

## ⚙️ CONFIGURATION

### AutomationConfig

**Fichier :** `config/automation_config.py`

**Description :** Configuration principale du système avec sous-configurations.

#### Structure

```python
@dataclass
class AutomationConfig:
    trading: TradingConfig = field(default_factory=TradingConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    confluence: ConfluenceConfig = field(default_factory=ConfluenceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
```

#### TradingConfig
```python
@dataclass
class TradingConfig:
    max_position_size: int = 1              # Taille position max
    daily_loss_limit: float = 200.0         # Limite perte quotidienne
    min_signal_confidence: float = 0.75     # Confiance signal min
    trading_start_hour: int = 9             # Heure début trading
    trading_end_hour: int = 16              # Heure fin trading
    risk_factor: float = 0.02               # Facteur risque Kelly
    stop_loss_percent: float = 0.02         # Stop loss (%)
    take_profit_percent: float = 0.04       # Take profit (%)
```

#### MLConfig
```python
@dataclass
class MLConfig:
    ensemble_enabled: bool = True            # ML Ensemble activé
    gamma_cycles_enabled: bool = True        # Gamma Cycles activé
    model_update_interval: int = 3600        # Intervalle mise à jour
    cache_enabled: bool = True               # Cache activé
    cache_ttl_hours: int = 6                # TTL cache
    min_accuracy_threshold: float = 0.6     # Seuil précision min
    min_confidence_threshold: float = 0.5    # Seuil confiance min
```

#### ConfluenceConfig
```python
@dataclass
class ConfluenceConfig:
    base_threshold: float = 0.25            # Seuil de base
    timeframe_weights: Dict[str, float] = field(default_factory=lambda: {
        "1m": 0.1, "5m": 0.2, "15m": 0.3, "1h": 0.25, "4h": 0.15
    })
    min_confluence_score: float = 0.6       # Score confluence min
    max_timeframe_divergence: float = 0.3   # Divergence max timeframes
```

#### MonitoringConfig
```python
@dataclass
class MonitoringConfig:
    enabled: bool = True                     # Monitoring activé
    interval_seconds: int = 30               # Intervalle collecte
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_critical": 90.0,
        "cpu_warning": 70.0,
        "memory_critical": 85.0,
        "memory_warning": 70.0,
        "latency_critical": 5.0,
        "latency_warning": 2.0
    })
    database_path: str = "data/monitoring.db"  # Chemin base données
```

#### Exemple d'utilisation

```python
from config.automation_config import AutomationConfig

# Configuration par défaut
config = AutomationConfig()

# Personnaliser la configuration
config.trading.max_position_size = 2
config.trading.daily_loss_limit = 500.0
config.ml.ensemble_enabled = True
config.confluence.base_threshold = 0.3
config.monitoring.interval_seconds = 60

# Utiliser la configuration
system = MIAAutomationSystem(config)
```

---

## 📊 TYPES DE DONNÉES

### Types de base

#### SignalType (Enum)
```python
class SignalType(Enum):
    BUY = "buy"                     # Signal d'achat
    SELL = "sell"                   # Signal de vente
    HOLD = "hold"                   # Maintenir position
    CLOSE = "close"                 # Fermer position
```

#### SignalDirection (Enum)
```python
class SignalDirection(Enum):
    LONG = "long"                   # Position longue
    SHORT = "short"                 # Position courte
    NEUTRAL = "neutral"             # Neutre
```

#### RiskLevel (Enum)
```python
class RiskLevel(Enum):
    LOW = "low"                     # Risque faible
    MEDIUM = "medium"               # Risque moyen
    HIGH = "high"                   # Risque élevé
    CRITICAL = "critical"           # Risque critique
```

#### VolatilityExpectation (Enum)
```python
class VolatilityExpectation(Enum):
    LOW = "low"                     # Volatilité faible
    MODERATE = "moderate"           # Volatilité modérée
    HIGH = "high"                   # Volatilité élevée
    EXTREME = "extreme"             # Volatilité extrême
```

### Types complexes

#### MarketData
```python
@dataclass
class MarketData:
    symbol: str                      # Symbole
    timestamp: datetime              # Timestamp
    open: float                      # Prix d'ouverture
    high: float                      # Prix le plus haut
    low: float                       # Prix le plus bas
    close: float                     # Prix de fermeture
    volume: int                      # Volume
    spread: float                    # Spread
    bid: float                       # Prix d'achat
    ask: float                       # Prix de vente
```

#### VolumeProfile
```python
@dataclass
class VolumeProfile:
    poc_price: float                 # Point of Control
    value_area_high: float           # Value Area High
    value_area_low: float            # Value Area Low
    volume_nodes: Dict[float, int]   # Nœuds de volume
    volume_delta: float              # Delta volume
```

#### RiskAssessment
```python
@dataclass
class RiskAssessment:
    risk_level: RiskLevel            # Niveau de risque
    max_loss: float                  # Perte maximale
    probability_loss: float          # Probabilité de perte
    risk_reward_ratio: float        # Ratio risque/récompense
    position_size_recommendation: int # Taille position recommandée
```

---

## 💡 EXEMPLES D'UTILISATION

### Exemple 1 : Démarrage complet du système

```python
import asyncio
from automation_main import MIAAutomationSystem, AutomationConfig
from monitoring_continu import monitor

async def main():
    # Configuration
    config = AutomationConfig()
    config.trading.max_position_size = 1
    config.trading.daily_loss_limit = 200.0
    config.ml.ensemble_enabled = True
    
    # Créer le système
    system = MIAAutomationSystem(config)
    
    try:
        # Démarrer le monitoring
        monitoring_task = asyncio.create_task(
            monitor.start_monitoring(interval_seconds=30)
        )
        
        # Démarrer le système
        await system.start()
        
        # Boucle principale
        while True:
            status = system.get_status()
            print(f"Statut: {status}")
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        print("Arrêt demandé...")
    finally:
        await system.stop()
        monitoring_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
```

### Exemple 2 : Test des composants ML

```python
from ml.ensemble_filter import MLEnsembleFilter
from ml.gamma_cycles import GammaCyclesAnalyzer, GammaCycleConfig

def test_ml_components():
    # Test ML Ensemble
    ml_filter = MLEnsembleFilter()
    
    features = {
        "confluence_score": 0.75,
        "momentum_flow": 0.8,
        "trend_alignment": 0.7,
        "volume_profile": 0.6,
        "support_resistance": 0.5,
        "market_regime_score": 0.6,
        "volatility_regime": 0.5,
        "time_factor": 0.5
    }
    
    result = ml_filter.predict_signal_quality(features)
    print(f"ML Ensemble - Signal approuvé: {result.signal_approved}")
    print(f"ML Ensemble - Confiance: {result.confidence:.3f}")
    
    # Test Gamma Cycles
    config = GammaCycleConfig()
    analyzer = GammaCyclesAnalyzer(config)
    
    analysis = analyzer.analyze_gamma_cycle()
    print(f"Gamma Cycles - Phase: {analysis.gamma_phase.value}")
    print(f"Gamma Cycles - Facteur: {analysis.adjustment_factor:.2f}")

test_ml_components()
```

### Exemple 3 : Monitoring personnalisé

```python
import asyncio
from monitoring_continu import ContinuousMonitor

async def custom_monitoring():
    monitor = ContinuousMonitor()
    
    # Démarrer monitoring
    await monitor.start_monitoring(interval_seconds=10)
    
    # Collecter métriques personnalisées
    for i in range(10):
        metrics = await monitor.collect_system_metrics()
        if metrics:
            print(f"CPU: {metrics.cpu_percent:.1f}%")
            print(f"Mémoire: {metrics.memory_percent:.1f}%")
            print(f"Processus: {metrics.process_count}")
            print("---")
        
        await asyncio.sleep(10)

asyncio.run(custom_monitoring())
```

### Exemple 4 : Configuration avancée

```python
from config.automation_config import AutomationConfig, TradingConfig, MLConfig

def create_advanced_config():
    # Configuration trading avancée
    trading_config = TradingConfig(
        max_position_size=2,
        daily_loss_limit=500.0,
        min_signal_confidence=0.8,
        trading_start_hour=8,
        trading_end_hour=17,
        risk_factor=0.03,
        stop_loss_percent=0.015,
        take_profit_percent=0.03
    )
    
    # Configuration ML avancée
    ml_config = MLConfig(
        ensemble_enabled=True,
        gamma_cycles_enabled=True,
        model_update_interval=1800,  # 30 minutes
        cache_enabled=True,
        cache_ttl_hours=4,
        min_accuracy_threshold=0.7,
        min_confidence_threshold=0.6
    )
    
    # Configuration complète
    config = AutomationConfig()
    config.trading = trading_config
    config.ml = ml_config
    
    return config

config = create_advanced_config()
print(f"Position max: {config.trading.max_position_size}")
print(f"Confiance min: {config.trading.min_signal_confidence}")
print(f"Cache TTL: {config.ml.cache_ttl_hours}h")
```

---

## 🎯 CONCLUSION

Cette référence API complète couvre tous les aspects de **MIA_IA_SYSTEM** :

- **🤖 Intelligence artificielle** : ML Ensemble, Gamma Cycles
- **📊 Stratégies trading** : Battle Navale, MTF Confluence
- **🛡️ Protection** : Catastrophe Monitor, Risk Manager
- **📈 Monitoring** : Surveillance temps réel
- **⚙️ Configuration** : Système de configuration flexible

### Points clés

1. **API modulaire** : Chaque composant est indépendant
2. **Types de données** : Structures claires et typées
3. **Configuration flexible** : Système de configuration hiérarchique
4. **Monitoring intégré** : Surveillance continue
5. **Documentation complète** : Exemples et cas d'usage

**MIA_IA_SYSTEM v3.0.0** offre une API robuste et complète pour le trading automatisé de nouvelle génération.

---

*Référence API MIA_IA_SYSTEM v3.0.0 - Août 2025* 