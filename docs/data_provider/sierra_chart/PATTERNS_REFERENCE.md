# 🎨 SIERRA CHART - RÉFÉRENCE PATTERNS

## 📊 **GUIDE COMPLET DES 19 PATTERNS INTÉGRÉS**

### **🎯 CLASSIFICATION PATTERNS**

```
📊 DOM Patterns (6)
├── Iceberg Detection
├── Wall Detection
├── Ladder Detection
├── Spoofing Detection
├── Absorption Detection
└── Squeeze Detection

📈 VIX Patterns (3)
├── Spike Reversal
├── Complacency Warning
└── Regime Change

⚔️ Battle Navale (5)
├── Long Down Up Bar
├── Long Up Down Bar
├── Color Down Setting
├── Vikings Patterns
└── Defenders Patterns

🎯 Advanced Patterns (5)
├── Gamma Pin
├── HeadFake
├── Microstructure Anomaly
├── Transition Bars
└── Volume Profile Imbalance
```

---

## 📊 **PATTERNS DOM - DÉTAIL TECHNIQUE**

### **1️⃣ ICEBERG PATTERN**
**🎯 Définition** : Gros ordres cachés dans le DOM, souvent institutionnels

**🔍 Détection** :
```python
# Critères détection
if level.size >= iceberg_threshold:  # >300-1000 contrats
    avg_size = mean(all_levels_size)
    if level.size > avg_size * 2.0:  # 2x plus gros que moyenne
        return ICEBERG_DETECTED
```

**📈 Trading Implications** :
- **Direction** : Suivre direction iceberg
- **Strength** : Très fort (institutions)
- **Time Horizon** : Court/Moyen terme
- **Position Sizing** : Standard à élevé

**📊 Exemple Réel** :
```
Bid Levels:
4998.75  [150]
4998.50  [200]  
4998.25  [1500] ← ICEBERG DÉTECTÉ
4998.00  [180]
```

### **2️⃣ WALL PATTERN**
**🎯 Définition** : Mur de support/résistance massif

**🔍 Détection** :
```python
# Mur = niveau avec size exceptionnelle
if level.size >= wall_threshold:  # >600-2000 contrats
    if level == max_size_level:
        return WALL_DETECTED
```

**📈 Trading Implications** :
- **Support Wall** : BULLISH (défense prix)
- **Resistance Wall** : BEARISH (plafond prix)
- **Break Wall** : MOMENTUM (continuation forte)

**📊 Exemple Réel** :
```
Ask Levels:
5001.25  [180]
5001.00  [2200] ← WALL RÉSISTANCE
5000.75  [190]
5000.50  [160]
```

### **3️⃣ LADDER PATTERN**
**🎯 Définition** : Échelle ordres progressifs agressifs

**🔍 Détection** :
```python
# Ladder = tailles croissantes vers best bid/ask
for i in range(ladder_min_levels):
    if levels[i].size > levels[i+1].size * 1.2:  # 20% progression
        ladder_count += 1
if ladder_count >= 3:
    return LADDER_DETECTED
```

**📈 Trading Implications** :
- **Ladder Bid** : BULLISH (achat agressif)
- **Ladder Ask** : BEARISH (vente agressive)
- **Time Horizon** : IMMÉDIAT
- **Strength** : Momentum fort

### **4️⃣ SPOOFING PATTERN**
**🎯 Définition** : Ordres fantômes (apparition/disparition rapide)

**🔍 Détection** :
```python
# Spoofing = gros ordre soudain puis disparition
if big_order_appeared_suddenly():
    if order_size >= 500:
        if not_present_in_recent_history():
            return SPOOFING_DETECTED
```

**📈 Trading Implications** :
- **Spoofing Bid** : BEARISH (fausse demande)
- **Spoofing Ask** : BULLISH (fausse offre)
- **Action** : FADE le movement
- **Confidence** : Modérée (manipulation)

### **5️⃣ ABSORPTION PATTERN**
**🎯 Définition** : Gros ordres absorbés/consommés

**🔍 Détection** :
```python
# Absorption = niveau réduit >50%
prev_size = previous_snapshot.level_size
curr_size = current_snapshot.level_size
if curr_size < prev_size * 0.5:  # 50% réduction
    if absorbed_size >= 200:
        return ABSORPTION_DETECTED
```

**📈 Trading Implications** :
- **Absorption Bid** : BEARISH (support cassé)
- **Absorption Ask** : BULLISH (résistance cassée)
- **Signal** : Continuation probable
- **Time Horizon** : IMMÉDIAT

### **6️⃣ SQUEEZE PATTERN**
**🎯 Définition** : Compression spread (breakout imminent)

**🔍 Détection** :
```python
# Squeeze = spread réduit significativement
if current_spread < avg_spread * 0.6:  # 40% réduction
    if current_spread <= 0.75:  # ≤3 ticks ES
        return SQUEEZE_DETECTED
```

**📈 Trading Implications** :
- **Direction** : Selon imbalance DOM
- **Time Horizon** : IMMÉDIAT
- **Volatility** : Breakout explosif attendu
- **Position Sizing** : Réduit (risque gap)

---

## 📈 **PATTERNS VIX - DÉTAIL TECHNIQUE**

### **1️⃣ VIX SPIKE REVERSAL**
**🎯 Définition** : Spike VIX = bottom marché probable

**🔍 Détection** :
```python
# Spike = hausse rapide >20% + VIX >25
spike_pct = (current_vix - min_recent_vix) / min_recent_vix
if spike_pct > 0.20 and current_vix > 25:
    return VIX_SPIKE_REVERSAL
```

**📈 Trading Implications** :
- **Direction** : CONTRARIAN (bottom)
- **Position Sizing** : 1.5x (opportunité)
- **Stop** : Serré (0.8x)
- **Target** : Généreux (1.3x)

**📊 VIX Régimes** :
```
VIX < 12   → ULTRA_LOW (Complacency)
VIX 12-18  → LOW (Calme)  
VIX 18-25  → NORMAL
VIX 25-35  → HIGH (Stress)
VIX > 35   → EXTREME (Panique)
```

### **2️⃣ COMPLACENCY WARNING**
**🎯 Définition** : VIX trop bas = correction probable

**🔍 Détection** :
```python
# Complacency = VIX <10ème percentile + VIX <15
if vix_percentile < 10.0 and vix_spot < 15:
    return COMPLACENCY_WARNING
```

**📈 Trading Implications** :
- **Action** : ADD HEDGING
- **Position Sizing** : 0.8x (prudence)
- **Time Horizon** : MOYEN terme
- **Risk Level** : ÉLEVÉ

### **3️⃣ REGIME CHANGE**
**🎯 Définition** : Changement régime volatilité

**🔍 Détection** :
```python
# Regime change = transition <2 jours
if regime_change_detected():
    if days_since_change < 2:
        return REGIME_CHANGE_SIGNAL
```

**📈 Trading Implications par Régime** :
- **→ ULTRA_LOW** : Add hedging
- **→ LOW** : Increase size  
- **→ NORMAL** : Standard trading
- **→ HIGH** : Reduce size
- **→ EXTREME** : Defensive + Contrarian

---

## ⚔️ **PATTERNS BATTLE NAVALE**

### **1️⃣ LONG DOWN UP BAR**
**🎯 Définition** : Barre longue baissière puis clôture haute = reversal

**📈 Trading Implications** :
- **Signal** : BULLISH reversal
- **Entry** : Break du high de la barre
- **Stop** : Low de la barre
- **Target** : 1.5x risk

### **2️⃣ LONG UP DOWN BAR**  
**🎯 Définition** : Barre longue haussière puis clôture basse = reversal

**📈 Trading Implications** :
- **Signal** : BEARISH reversal
- **Entry** : Break du low de la barre
- **Stop** : High de la barre
- **Target** : 1.5x risk

### **3️⃣ COLOR DOWN SETTING**
**🎯 Définition** : Configuration baissière multi-barres

**📈 Trading Implications** :
- **Signal** : BEARISH trend change
- **Confirmation** : Volume + momentum
- **Time Horizon** : MOYEN terme

### **4️⃣ VIKINGS PATTERNS**
**🎯 Définition** : Patterns agressifs (attaque)

**📈 Trading Implications** :
- **Signal** : MOMENTUM strong
- **Action** : Suivre direction
- **Position Sizing** : Agressif

### **5️⃣ DEFENDERS PATTERNS**
**🎯 Définition** : Patterns défensifs (défense niveaux)

**📈 Trading Implications** :
- **Signal** : SUPPORT holding
- **Action** : Fade breakout
- **Position Sizing** : Conservateur

---

## 🎯 **PATTERNS AVANCÉS**

### **1️⃣ GAMMA PIN**
**🎯 Définition** : Prix attiré vers niveaux gamma élevé

**🔍 Détection** :
```python
# Gamma pin = concentration gamma à niveau prix
if gamma_exposure_at_level > threshold:
    if price_near_gamma_level:
        return GAMMA_PIN_DETECTED
```

**📈 Trading Implications** :
- **Direction** : Vers gamma pin
- **Strength** : Fort (options flow)
- **Time Horizon** : Court terme (expiration)

### **2️⃣ HEADFAKE**
**🎯 Définition** : Faux breakout puis reversal

**🔍 Détection** :
```python
# HeadFake = breakout puis absorption
if breakout_detected():
    if orderflow_absorption():
        return HEADFAKE_DETECTED
```

**📈 Trading Implications** :
- **Signal** : FADE breakout
- **Entry** : Reversal confirmation
- **Stop** : Beyond fakeout level

### **3️⃣ MICROSTRUCTURE ANOMALY**
**🎯 Définition** : Anomalies structure marché

**🔍 Détection** :
```python
# Anomalies = spread anormal, volume spike, tick imbalance
if spread_anomaly or volume_spike or tick_imbalance:
    return MICROSTRUCTURE_ANOMALY
```

**📈 Trading Implications** :
- **Signal** : Inefficiency temporaire
- **Action** : ARBITRAGE opportunity
- **Time Horizon** : TRÈS court terme

### **4️⃣ TRANSITION BARS**
**🎯 Définition** : Barres marquant transition régime

**🔍 Détection** :
```python
# Transition = volatility regime change + volume
if volatility_regime_change():
    if volume_confirmation():
        return TRANSITION_BAR
```

**📈 Trading Implications** :
- **Signal** : Regime change confirmation  
- **Action** : Adjust strategy parameters
- **Position Sizing** : Adapt to new regime

### **5️⃣ VOLUME PROFILE IMBALANCE**
**🎯 Définition** : Déséquilibre volume institutionnel

**🔍 Détection** :
```python
# Imbalance = volume concentré + smart money
if volume_concentration > threshold:
    if smart_money_detected():
        return VOLUME_PROFILE_IMBALANCE
```

**📈 Trading Implications** :
- **Signal** : Institutional positioning
- **Direction** : Suivre smart money
- **Confidence** : Élevée (institutions)

---

## 🎯 **CONFLUENCE PATTERNS**

### **🔥 SIGNAUX ELITE (Score >70%)**

**Confluence Optimale** :
```
VIX Spike (35.0) + DOM Iceberg + Battle Navale + Volume Profile
→ Elite Score: 85%
→ Direction: BULLISH  
→ Position Sizing: 1.8x
→ Confidence: 90%
```

**Confluence Forte** :
```
DOM Wall Break + VIX Regime Change + Absorption
→ Elite Score: 75%
→ Direction: Momentum
→ Position Sizing: 1.3x
→ Confidence: 80%
```

**Confluence Moyenne** :
```
Ladder + HeadFake + Microstructure
→ Elite Score: 65%
→ Direction: Fade
→ Position Sizing: 0.9x
→ Confidence: 70%
```

---

## 📊 **GUIDE UTILISATION RAPIDE**

### **🚀 Pattern Priority (Trading)**
1. **VIX Spike** : Contrarian entry (highest priority)
2. **DOM Iceberg** : Institution positioning  
3. **Wall Break** : Momentum continuation
4. **Absorption** : Liquidity exhaustion
5. **Gamma Pin** : Options flow attraction

### **⚙️ Configuration Recommandée**
```python
# Production optimale
DOM: iceberg_threshold=500, wall_threshold=1000
VIX: spike_threshold=0.20, analysis_interval=60s  
Elite: min_score=0.70, max_signals=6/hour
```

### **🎯 Position Sizing Guide**
```python
# Selon pattern + VIX regime
if VIX_SPIKE and DOM_ICEBERG:
    size = base_size * 1.8  # Opportunité majeure
elif WALL_BREAK and HIGH_VOL:
    size = base_size * 1.3  # Momentum fort
elif COMPLACENCY_WARNING:
    size = base_size * 0.6  # Prudence
```

---

**🎨 PATTERNS REFERENCE - ELITE TOOLKIT ! 🎯**

*19 patterns intégrés - Performance validée - Production ready*


