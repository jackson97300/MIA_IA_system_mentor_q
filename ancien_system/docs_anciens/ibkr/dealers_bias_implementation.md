# Dealer's Bias Implementation - MIA_IA System

## 📋 Vue d'ensemble

Le **Dealer's Bias** est une fonctionnalité avancée intégrée dans MIA_IA qui analyse les positions des market makers sur les options pour prédire les mouvements de prix. Cette implémentation complète inclut :

- **Gamma Flip Detection** : Identification du strike où la gamma cumulative change de signe
- **Gamma Pins** : Zones d'aimantation des prix
- **GEX (Gamma Exposure)** : Exposition gamma normalisée
- **Score composite** : Dealer's Bias score (-1 à +1) avec pondérations
- **Intégration Sierra Chart** : Overlays visuels en temps réel

## 🏗️ Architecture

### Fichiers principaux

```
features/
├── create_options_snapshot.py      # Génération snapshots avec Dealer's Bias
├── dealers_bias_analyzer.py        # Analyseur principal
├── feature_calculator.py           # Intégration dans MIA
└── ibkr_connector3.py              # Connecteur IBKR

data/options_snapshots/             # Snapshots JSON/CSV
├── spx_snapshot_*.json
└── ndx_snapshot_*.json

docs/ibkr/
└── dealers_bias_implementation.md  # Ce document
```

### Workflow

1. **Collecte données** : `ibkr_connector3.py` → IBKR API
2. **Génération snapshot** : `create_options_snapshot.py` → Calculs Dealer's Bias
3. **Analyse** : `dealers_bias_analyzer.py` → Traitement et cache
4. **Intégration** : `feature_calculator.py` → Score confluence MIA
5. **Visualisation** : Sierra Chart DTC → Overlays temps réel

## 🧮 Algorithmes Dealer's Bias

### 1. Gamma Flip Detection

```python
def _compute_gamma_flip(options, underlying_price, contract_multiplier):
    """
    Trouve le strike où la gamma cumulative change de signe
    """
    # Agréger gamma par strike
    gamma_by_strike = {}
    for option in options:
        strike = option["strike"]
        gamma = option["gamma"]
        oi = option["open_interest"]
        gex = gamma * underlying_price² * oi * contract_multiplier
        gamma_by_strike[strike] = gamma_by_strike.get(strike, 0) + gex
    
    # Trouver le flip (changement de signe)
    strikes = sorted(gamma_by_strike.keys())
    cumulative_gamma = 0
    for strike in strikes:
        cumulative_gamma += gamma_by_strike[strike]
        if abs(cumulative_gamma) < threshold:
            return strike  # Gamma Flip détecté
```

### 2. Gamma Pins Detection

```python
def _compute_gamma_pins(options, underlying_price, contract_multiplier):
    """
    Détecte les zones d'aimantation (pics de gamma)
    """
    # Calculer gamma exposure par strike
    gamma_by_strike = {}
    for option in options:
        strike = option["strike"]
        gamma = option["gamma"]
        oi = option["open_interest"]
        gex = abs(gamma * underlying_price² * oi * contract_multiplier)
        gamma_by_strike[strike] = gamma_by_strike.get(strike, 0) + gex
    
    # Trouver les pics locaux (maxima)
    pins = []
    strikes = sorted(gamma_by_strike.keys())
    for i, strike in enumerate(strikes[1:-1]):
        current = gamma_by_strike[strike]
        prev = gamma_by_strike[strikes[i-1]]
        next = gamma_by_strike[strikes[i+1]]
        
        if current > prev and current > next:
            strength = current / max(prev, next)
            pins.append({
                "strike": strike,
                "gamma_exposure": current,
                "strength": strength,
                "strength_category": "Strong" if strength > 1.5 else "Medium"
            })
```

### 3. Dealer's Bias Score

```python
def _compute_dealers_bias(gamma_flip_data, gamma_pins, pcr_oi, pcr_volume, 
                         iv_skew, vix_value, underlying_price, gex_signed):
    """
    Score composite (-1 à +1) avec pondérations
    """
    # 1. Gamma Flip Bias (25%)
    gamma_flip_bias = 0.5  # Neutre par défaut
    if gamma_flip_data and gamma_flip_data.get("gamma_flip_strike"):
        flip_strike = gamma_flip_data["gamma_flip_strike"]
        distance = flip_strike - underlying_price
        if abs(distance) < 50:
            gamma_flip_bias = 0.5  # Très proche = neutre
        elif distance > 0:
            gamma_flip_bias = 0.3  # Prix sous flip = bearish
        else:
            gamma_flip_bias = 0.7  # Prix au-dessus = bullish
    
    # 2. Gamma Pins Bias (20%)
    gamma_pins_bias = 0.5
    if gamma_pins:
        closest_pin = min(gamma_pins, key=lambda x: abs(x["distance_from_current"]))
        distance_to_pin = abs(closest_pin["distance_from_current"])
        if distance_to_pin < 25 and closest_pin["strength"] > 1.3:
            gamma_pins_bias = 0.5  # Pinning = neutre
    
    # 3. PCR Bias (15%) - Contrariant
    pcr_bias = 0.5
    if pcr_oi > 1.5:
        pcr_bias = 0.2  # PCR élevé = bearish
    elif pcr_oi < 0.8:
        pcr_bias = 0.7  # PCR faible = bullish
    
    # 4. IV Skew Bias (15%)
    skew_bias = 0.5
    if iv_skew > 0.05:
        skew_bias = 0.3  # Skew positif = bearish
    elif iv_skew < -0.05:
        skew_bias = 0.7  # Skew négatif = bullish
    
    # 5. VIX Regime Bias (10%)
    vix_bias = 0.5
    if vix_value > 25:
        vix_bias = 0.5  # Stress = neutralisation
    elif vix_value < 15:
        vix_bias = 0.7  # Calme = amplification
    
    # 6. GEX Bias (15%)
    gex_bias = 0.5
    if gex_signed > 0:
        gex_bias = 0.5  # Dealers long gamma = pinning
    else:
        gex_bias = 0.3 if gex_signed < -1e9 else 0.7  # Short gamma = amplification
    
    # Score final pondéré
    dealers_bias_score = (
        0.25 * gamma_flip_bias +
        0.20 * gamma_pins_bias +
        0.15 * pcr_bias +
        0.15 * skew_bias +
        0.10 * vix_bias +
        0.15 * gex_bias
    )
    
    # Normalisation (-1 à +1)
    dealers_bias_normalized = 2 * (dealers_bias_score - 0.5)
    
    return dealers_bias_normalized
```

## 📊 Métriques et Seuils

### Seuils calibrés (v1.0)

| Métrique | Seuil NEUTRAL | Seuil MODERATE | Seuil STRONG |
|----------|---------------|----------------|--------------|
| Dealer's Bias | ±0.15 | 0.15–0.45 | >0.45 |
| PCR OI | 0.8–1.2 | 0.5–0.8 ou 1.2–1.5 | <0.5 ou >1.5 |
| IV Skew | ±0.05 | ±0.05–0.10 | >0.10 |
| VIX | 15–25 | 10–15 ou 25–30 | <10 ou >30 |

### Auto-inférence du signe des dealers

```python
# Règle : position du spot par rapport au Gamma Flip
if underlying_price >= gamma_flip_strike:
    dealer_sign = +1  # Dealers long gamma
else:
    dealer_sign = -1  # Dealers short gamma
```

## 🔧 Utilisation

### 1. Génération de snapshots

```bash
# Avec données réelles IBKR
python features/create_options_snapshot.py --symbols SPX,NDX --dynamic --window 5

# Avec données simulées (test)
python create_test_snapshot.py
```

### 2. Test de l'analyzer

```bash
python test_dealers_bias.py
```

### 3. Intégration dans MIA

```python
from features.dealers_bias_analyzer import get_dealers_bias_analyzer

analyzer = get_dealers_bias_analyzer()
bias_data = analyzer.get_dealers_bias("SPX")
overlay_data = analyzer.get_sierra_overlay_data("SPX")
confluence_score = analyzer.get_confluence_score("SPX")
```

## 📈 Format des snapshots

### Structure JSON

```json
{
  "snapshot_id": "20250828_020000",
  "symbol": "SPX",
  "expiry": "20250919",
  "timestamp": "2025-08-28T02:00:00",
  "options": [...],
  "analysis": {
    "underlying_price": 6477.0,
    "put_call_ratio_oi": 1.24,
    "put_call_ratio_volume": 1.18,
    "implied_volatility_avg": 0.16,
    "iv_skew_puts_minus_calls": 0.03,
    "vix": 18.5,
    "gex": {
      "gex_total_magnitude": 2445809000000,
      "gex_total_signed": -2445809000000,
      "dealer_sign_assumption": -1,
      "normalized": {
        "gex_total_signed_normalized": -2.45
      }
    },
    "gamma_flip": {
      "gamma_flip_strike": 6500.0,
      "distance_from_current": 23.0
    },
    "gamma_pins": [
      {
        "strike": 6450.0,
        "gamma_exposure": 1500000000000,
        "strength": 1.8,
        "strength_category": "Strong"
      }
    ],
    "dealers_bias": {
      "dealers_bias_score": -0.410,
      "interpretation": {
        "direction": "BEARISH",
        "strength": "MODERATE"
      }
    }
  }
}
```

## 🎯 Sierra Chart Overlay

### Lignes horizontales

- **Gamma Flip** : Ligne rouge/verte solide (2px)
- **Gamma Pins** : Lignes bleues/grises pointillées (1px)
- **Max Pain** : Ligne orange pointillée (fallback)

### Métriques texte

```
SPX_DealersBias: -0.410
SPX_Direction: BEARISH
SPX_Strength: MODERATE
SPX_PCR: 1.24
SPX_VIX: 18.5
SPX_GEX_M: -244.6M
SPX_GEXn: -2.45
SPX_Quality: 1.00
```

## 🔍 Dépannage

### Erreurs communes

1. **"Connection refused"** : TWS/IB Gateway non démarré
2. **"No snapshots found"** : Aucun snapshot dans `data/options_snapshots/`
3. **"Quality insufficient"** : Données trop anciennes (>5min)

### Validation des données

```python
# Vérifier la qualité
quality = analyzer.calculate_data_quality(data)
if quality < 0.6:
    print("⚠️ Qualité insuffisante")

# Vérifier la fraîcheur
age_seconds = (datetime.now() - timestamp).total_seconds()
if age_seconds > 300:
    print("⚠️ Données anciennes (>5min)")
```

## 🚀 Optimisations futures

### Calibration automatique

- Ajustement des seuils basé sur les performances historiques
- Machine learning pour optimiser les pondérations
- Validation croisée avec d'autres indicateurs MIA

### Intégrations avancées

- Alertes temps réel sur franchissement de seuils
- Backtesting automatisé des signaux
- Interface web pour monitoring

### Métriques supplémentaires

- **Call/Put Walls** : Niveaux de résistance/support
- **Volatility Trigger** : Seuils de volatilité
- **Market Regime Detection** : Adaptation aux conditions de marché

## 📚 Références

- **Gamma Exposure** : [SpotGamma](https://spotgamma.com/)
- **Options Flow** : [FlowAlgo](https://flowalgo.com/)
- **Market Making** : Hull, J.C. "Options, Futures, and Other Derivatives"

---

**Version** : 1.0  
**Date** : 2025-08-28  
**Auteur** : MIA_IA Development Team  
**Statut** : Production Ready ✅

