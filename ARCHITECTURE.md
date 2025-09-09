# Architecture MIA_IA_system

## 🏗️ Vue d'ensemble

Système de trading automatisé basé sur **Sierra Chart** avec intégration **MenthorQ** et stratégie **Battle Navale**.

## 📊 Flux de données

```
Sierra Chart (C++) → JSONL Files → SierraTail → UnifiedWriter → mia_unified_YYYYMMDD.jsonl
                                                      ↓
                                              MenthorQ Processor
                                                      ↓
                                              Battle Navale Analyzer
                                                      ↓
                                              Signal Generation
```

## 🔧 Composants principaux

### 1. **Sierra Chart Integration**
- **`MIA_Chart_Dumper_patched.cpp`** : Custom study C++ pour Sierra Chart
- **Charts collectés** : 3, 4, 8, 10
- **Format sortie** : JSONL par chart et par jour

### 2. **Data Pipeline**
- **`SierraTail`** : Lecture asynchrone des fichiers JSONL
- **`UnifiedWriter`** : Consolidation en fichier unique
- **`DataCollectorEnhanced`** : Orchestrateur principal

### 3. **MenthorQ Integration**
- **`MenthorQProcessor`** : Traitement des niveaux MenthorQ
- **`MenthorQDealersBias`** : Calcul du Dealer's Bias
- **`MenthorQBattleNavale`** : Intégration avec Battle Navale

### 4. **Battle Navale Strategy**
- **Analyse technique** : Confluence, volume, momentum
- **Règles hard** : Blind spots, gamma levels
- **Position sizing** : Basé sur la volatilité VIX

## 📁 Structure des données

### Graph 3 (1 minute)
```json
{
  "ts": "2025-01-07T10:30:00Z",
  "sym": "ESU25_FUT_CME",
  "chart": 3,
  "type": "basedata",
  "open": 5295.0,
  "high": 5297.0,
  "low": 5293.0,
  "close": 5295.5,
  "volume": 1000
}
```

### Graph 8 (VIX)
```json
{
  "ts": "2025-01-07T10:30:00Z",
  "sym": "VIX",
  "chart": 8,
  "type": "vix",
  "last": 15.2,
  "policy": "normal"
}
```

### Graph 10 (MenthorQ)
```json
{
  "ts": "2025-01-07T10:30:00Z",
  "sym": "ESU25_FUT_CME",
  "chart": 10,
  "type": "menthorq_gamma_levels",
  "label": "Call Resistance",
  "price": 5300.0
}
```

## 🔄 Processus de traitement

### 1. **Collection**
- Sierra Chart écrit les données en JSONL
- `SierraTail` lit en continu les fichiers
- Détection automatique de rotation journalière

### 2. **Unification**
- `UnifiedWriter` consolide tous les charts
- Fichier unique : `mia_unified_YYYYMMDD.jsonl`
- Enrichissement des événements

### 3. **Analyse**
- `MenthorQProcessor` traite les niveaux
- `MenthorQBattleNavale` génère les signaux
- Règles de sécurité et position sizing

### 4. **Exécution**
- `launch_24_7.py` orchestre le système
- Mode lecture seule par défaut
- Monitoring et alertes

## 🛡️ Sécurité

### Mode Lecture Seule (Par défaut)
- **Trading automatique** : Désactivé
- **Exécution d'ordres** : Désactivée
- **Modifications** : Désactivées

### Mode Trading (Sierra Chart)
- **Ports DTC** : ES (11099), NQ (11100)
- **Trading via DTC** : Activé dans Sierra Chart
- **Symboles** : ESU25_FUT_CME, NQU25_FUT_CME

### Gestion des risques
- **Limites quotidiennes** : Perte max configurable
- **Position sizing** : Basé sur la volatilité
- **Hard rules** : Blind spots et gamma levels

## 📈 Performance

### Optimisations
- **Lecture asynchrone** : Non-bloquante
- **Cache VIX** : Mise à jour en temps réel
- **Pipeline unifié** : Réduction de la latence

### Monitoring
- **Logs détaillés** : Tous les événements
- **Métriques** : Performance et erreurs
- **Alertes** : Anomalies et seuils

## 🔧 Configuration

### Chemins Sierra
```python
# config/sierra_paths.py
CHART_OUT_DIR = Path(r"D:\MIA_IA_system")
UNIFIED_NAME_FORMAT = "mia_unified_{date}.jsonl"
```

### MenthorQ
```python
# config/menthorq_runtime.py
VIX_UPDATE_THRESHOLD = 2.0
EMISSION_THRESHOLD = 0.15
SIZING_FACTOR = 0.5
```

## 🚀 Déploiement

### Prérequis
- **Sierra Chart** avec custom study compilée
- **Python 3.11+** avec dépendances
- **Compte IBKR** (lecture seule)

### Installation
```bash
pip install -r requirements.txt
python test_menthorq_integration.py
```

### Lancement
```bash
python launchers/launch_24_7.py
```
