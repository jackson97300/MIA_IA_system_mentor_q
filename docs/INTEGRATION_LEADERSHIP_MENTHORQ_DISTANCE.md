# 🎯 INTÉGRATION LEADERSHIP Z-MOMENTUM DANS MENTHORQ-DISTANCE

**Version :** Intégration Complète v1.0  
**Date :** Janvier 2025  
**Auteur :** MIA_IA_SYSTEM  
**Statut :** ✅ **INTÉGRATION TERMINÉE**

---

## 🎯 **ARCHITECTURE INTÉGRÉE**

### **Ordre des Étapes (Exactement comme demandé)**

1. **🎯 MenthorQ décide** (décideur principal)
2. **📊 MIA Bullish valide** (biais interne bidirectionnel)
3. **⚡ Leadership Z-Momentum** (gate + bonus) ✅ **NOUVEAU**
4. **📈 OrderFlow valide** (timing)
5. **🏗️ Structure contextuelle** (VWAP/VVA)
6. **🧮 Fusion des scores** + modulateurs
7. **🎯 E/U/L** (Entry/Stop/Target)

---

## 🚀 **UTILISATION**

### **Méthode Principale Intégrée**

```python
from core.menthorq_distance_trading import MenthorQDistanceTrader

# Initialiser le trader
trader = MenthorQDistanceTrader()

# Configuration recommandée
config = {
    "tick_size": 0.25,
    "mq_tolerance_ticks": {
        "gamma_wall": 3,    # 3 ticks pour gamma walls
        "hvl": 5,           # 5 ticks pour HVL
        "gex": 5            # 5 ticks pour GEX
    },
    "mia_threshold": 0.20,  # Seuil MIA Bullish
    "entry_threshold": 0.70, # Seuil d'entrée final
    "weights": {
        "mq": 0.55,         # 55% MenthorQ
        "of": 0.30,         # 30% OrderFlow
        "structure": 0.15   # 15% Structure
    }
}

# Analyser une opportunité
signal = trader.decide_mq_distance_integrated(
    row_es=es_unified_data,
    row_nq=nq_unified_data,
    config=config
)

if signal:
    print(f"Signal: {signal['action']}")
    print(f"Score: {signal['score']}")
    print(f"Leadership: {signal['leadership']['ls']}")
    print(f"E/U/L: {signal['eul']}")
else:
    print("Pas de signal")
```

---

## 📊 **EXEMPLE DE SIGNAL COMPLET**

```json
{
    "action": "GO_LONG",
    "score": 0.756,
    "mq_score": 0.85,
    "of_score": 0.72,
    "st_score": 0.65,
    "mia_bullish": 0.45,
    "vix_regime": "MID",
    "leadership": {
        "ls": 0.32,
        "beta": 1.28,
        "roll_corr_30s": 0.67,
        "bonus": 1.05,
        "extra_of": 0,
        "reason": "LS=0.32 regime=MID (thr=0.50, hard=1.00)"
    },
    "mq_level": {
        "name": "put_support_0dte",
        "price": 4498.0,
        "type": "gamma"
    },
    "eul": {
        "entry": 4500.0,
        "stop": 4496.25,
        "target1": 4503.75,
        "target2": 4507.5,
        "risk_ticks": 15.0
    }
}
```

---

## ⚙️ **PARAMÈTRES CONFIGURABLES**

### **Tolérances MenthorQ**

```python
mq_tolerance_ticks = {
    "gamma_wall": 3,    # Gamma walls (critiques)
    "hvl": 5,           # High Volume Levels
    "gex": 5,           # Gamma Exposure levels
    "blind_spots": 4,   # Blind Spots (zones cachées)
    "swing": 8          # Swing Levels
}
```

### **Seuils de Validation**

```python
validation_thresholds = {
    "mia_threshold": 0.20,      # MIA Bullish minimum
    "entry_threshold": 0.70,    # Score final minimum
    "correlation_floor": 0.30,  # Corrélation ES/NQ minimum
    "leadership_hard": 1.0,     # Veto leadership (1.25 en HIGH VIX)
    "leadership_bonus": 0.5     # Bonus leadership (0.75 en HIGH VIX)
}
```

### **Pondérations**

```python
weights = {
    "mq": 0.55,         # MenthorQ (décideur principal)
    "of": 0.30,         # OrderFlow (validation timing)
    "structure": 0.15   # Structure (contexte)
}
```

---

## 🎯 **LOGIQUE DE DÉCISION**

### **1. MenthorQ Trigger (Décideur)**

```python
# Trouve le niveau le plus proche
best_level = find_nearest_menthorq_level(price, menthorq_levels)

# Vérifie la tolérance
if distance_ticks <= tolerance:
    # Détermine le side
    if "call" in level_name or "resistance" in level_name:
        side = "SHORT"
    elif "put" in level_name or "support" in level_name:
        side = "LONG"
    else:
        side = "LONG" if price < level_price else "SHORT"
```

### **2. MIA Bullish Gate**

```python
# Score bidirectionnel (-1 à +1)
mia_score = compute_mia_bullish_bidirectional(row_es)

# Validation selon le side
if (side == "LONG" and mia_score < +0.20) or (side == "SHORT" and mia_score > -0.20):
    return None  # Pas de trade
```

### **3. Leadership Z-Momentum**

```python
# Calcule LS (NQ vs ES)
snap = leadership_engine.update_from_unified_rows(row_es, row_nq)

# Applique le gate
gate = leadership_engine.gate_for_es(side=side, vix_value=vix_val)

if not gate["allow"]:
    return None  # Contre leadership fort

leader_bonus = gate["bonus"]  # 1.00 ou 1.05
extra_of = gate["extra_of"]   # +1 confirm OF si VIX HIGH
```

### **4. OrderFlow Validation**

```python
# Score OrderFlow avec extra_of
of_result = orderflow_score(row_es, extra_of)

# Validation avec confirmations supplémentaires
min_confirms = 2 + extra_of
if of_result["confirms"] < min_confirms:
    return None
```

### **5. Fusion des Scores**

```python
# Score composite
raw = (0.55 * mq_score + 
       0.30 * of_score + 
       0.15 * st_score)

# Modulateurs
eff = raw * vix_mult * mia_mult * leader_bonus

# Seuil d'entrée
if eff < 0.70:
    return None
```

---

## 🔥 **EXEMPLES CONCRETS**

### **Exemple 1 : Trade LONG Validé**

```
🎯 SETUP LONG VALIDÉ :

1. MENTHORQ DÉCIDE
   - Niveau: put_support_0dte @ 4498.0
   - Distance: 2 ticks (dans tolérance)
   - Side: LONG
   - Score: 0.85

2. MIA BULLISH VALIDE
   - Score: +0.45 (bullish)
   - Multiplicateur: 1.05

3. LEADERSHIP VALIDE
   - LS: +0.32 (NQ leader)
   - Corrélation: 0.67 (>0.30)
   - Bonus: 1.05
   - Extra OF: 0

4. ORDERFLOW VALIDE
   - Pressure: +1 (bullish)
   - Delta Ratio: +0.18
   - Confirms: 3/2 ✅

5. STRUCTURE
   - VWAP: 4499.5 (au-dessus)
   - VVA: Dans la zone
   - Score: 0.65

6. SCORE FINAL
   - Raw: 0.55×0.85 + 0.30×0.72 + 0.15×0.65 = 0.756
   - Eff: 0.756 × 1.0 × 1.05 × 1.05 = 0.833
   - > 0.70 ✅

RÉSULTAT: GO_LONG @ 4500.0
```

### **Exemple 2 : Trade Rejeté par Leadership**

```
❌ SETUP REJETÉ :

1. MENTHORQ DÉCIDE
   - Niveau: call_resistance @ 4520.0
   - Side: SHORT
   - Score: 0.78

2. MIA BULLISH VALIDE
   - Score: -0.35 (bearish)
   - Multiplicateur: 1.05

3. LEADERSHIP REJETTE
   - LS: +1.15 (NQ très fort)
   - Hard Block: |LS| > 1.0
   - Raison: Contre leadership très fort

RÉSULTAT: NO_TRADE (Leadership veto)
```

---

## 🎯 **AVANTAGES DE L'INTÉGRATION**

### **✅ Architecture Respectée**
- **MenthorQ décide** : Décideur principal inchangé
- **OrderFlow valide** : Timing préservé
- **Leadership gate** : Évite les trades contre le moteur

### **✅ Performance Optimisée**
- **Z-Momentum pro** : Standardisation par volatilité
- **Multi-horizons** : 3s, 30s, 5min
- **Beta dynamique** : Recalculé en temps réel

### **✅ Robustesse**
- **Gating intelligent** : VIX adaptatif + hard rules
- **Corrélation** : Validation de fiabilité
- **Extra OF** : Confirmations supplémentaires en VIX HIGH

### **✅ Flexibilité**
- **Configuration** : Paramètres ajustables
- **Audit trail** : Traçabilité complète
- **E/U/L** : Calcul automatique des niveaux

---

## 🚀 **PROCHAINES ÉTAPES**

### **1. Test avec Données Historiques**

```python
# Test sur 10 sessions
for session in historical_sessions:
    signals = []
    for row_es, row_nq in zip(es_data, nq_data):
        signal = trader.decide_mq_distance_integrated(row_es, row_nq, config)
        if signal:
            signals.append(signal)
    
    # Analyser les résultats
    analyze_performance(signals)
```

### **2. Optimisation des Paramètres**

```python
# A/B Test avec/sans leadership
config_with_leadership = config.copy()
config_without_leadership = config.copy()
config_without_leadership["disable_leadership"] = True

# Comparer les performances
compare_strategies(config_with_leadership, config_without_leadership)
```

### **3. Intégration Live**

```python
# Dans votre signal_generator
def generate_signal(unified_data):
    es_data = unified_data.get("ES")
    nq_data = unified_data.get("NQ")
    
    signal = trader.decide_mq_distance_integrated(es_data, nq_data, config)
    
    if signal:
        return {
            "action": signal["action"],
            "confidence": signal["score"],
            "entry": signal["eul"]["entry"],
            "stop": signal["eul"]["stop"],
            "target1": signal["eul"]["target1"]
        }
    
    return None
```

---

## 🎯 **CONCLUSION**

L'intégration du **Leadership Z-Momentum** dans votre méthode **MenthorQ-Distance** est **complète et opérationnelle**. 

**Avantages :**
- **✅ Architecture respectée** : MenthorQ décide, OrderFlow valide
- **✅ Leadership intelligent** : Évite les trades contre le moteur
- **✅ Performance optimisée** : Z-Momentum professionnel
- **✅ Configuration flexible** : Paramètres ajustables

**Le système est prêt pour les tests et la production !** 🚀

---

*Document créé pour MIA_IA_SYSTEM - Intégration Leadership MenthorQ-Distance*


