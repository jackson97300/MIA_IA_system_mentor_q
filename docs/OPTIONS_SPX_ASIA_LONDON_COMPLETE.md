# 📊 GUIDE COMPLET - OPTIONS SPX ASIA/LONDON
## MIA_IA_SYSTEM - Collecte, Sauvegarde & Utilisation

---

## 🎯 **OBJECTIF GLOBAL**

Collecter et sauvegarder les niveaux options SPX critiques avant la clôture US pour les utiliser dans les sessions Asia et London, compensant l'indisponibilité des données options pendant ces sessions.

---

## 🚨 **PROBLÈME IDENTIFIÉ**

### **IBKR Limitations :**
- **Options SPX** : Disponibles uniquement pendant les heures US (09:30-16:00 EST)
- **Session Asia** (18:00-03:00 EST) : Pas de données options
- **Session London** (03:00-09:30 EST) : Données limitées/inexistantes
- **Impact** : Feature `gamma_levels_proximity (28%)` inutilisable

### **Solution :**
- **Sauvegarde préventive** avant clôture US
- **Utilisation données sauvegardées** en sessions Asia/London
- **Actualisation** à chaque ouverture US

---

## 📋 **DONNÉES CRITIQUES À COLLECTER**

### **1. 🏗️ Gamma Exposure - Exposition Gamma Totale**
- **Total Exposure** : Exposition gamma totale ($75B+)
- **Call Gamma** : Exposition gamma des calls
- **Put Gamma** : Exposition gamma des puts
- **Net Gamma** : Exposition gamma nette (call - put)
- **Impact** : Détermine la force des mouvements de prix

### **2. 🎯 Call/Put Walls - Murs de Résistance/Support**
- **Major Call Walls** : Niveaux de résistance gamma majeurs
- **Major Put Walls** : Niveaux de support gamma majeurs
- **Gamma Walls** : Murs gamma combinés
- **Utilisation** : Zones de retournement potentielles

### **3. 🔄 Gamma Flip Level - Niveau Pivot Dealer**
- **Level** : Niveau exact du flip gamma
- **Significance** : Importance du niveau
- **Distance from Price** : Distance par rapport au prix actuel
- **Biais** : Au-dessus = bullish, en-dessous = bearish

### **4. 📈 VIX Level - Indice de Volatilité**
- **Current VIX** : Niveau VIX actuel
- **VIX Percentile** : Percentile historique
- **VIX Trend** : Tendance VIX (bullish/bearish/neutral)
- **Impact** : VIX élevé = volatilité élevée

### **5. ⚖️ Put/Call Ratio - Ratio Put/Call Volume**
- **Current Ratio** : Ratio actuel
- **Volume Ratio** : Ratio basé sur le volume
- **Ratio Trend** : Tendance du ratio
- **Interprétation** : Ratio élevé = sentiment bearish (potentiel bullish)

### **6. 🎯 Pin Levels - Niveaux de Pin Risk**
- **Major Pin Levels** : Niveaux de pin majeurs
- **Pin Risk Score** : Score de risque pin
- **Pin Probability** : Probabilité de pin
- **Détection** : Proximité aux strikes d'expiration

### **7. 🏦 Dealer Positioning - Positionnement des Dealers**
- **Dealer Position** : Position des dealers (long/short/neutral)
- **Dealer Flow** : Flux des dealers
- **Dealer Confidence** : Confiance des dealers
- **Impact** : Dealers short gamma = mouvements plus violents

---

## 🚀 **SCRIPTS DE COLLECTE ET SAUVEGARDE**

### **1. Collecte Niveaux Options SPX**
```bash
python collecte_niveaux_options_spx.py
```

### **2. Sauvegarde Détaillée**
```bash
python sauvegarde_niveaux_options_detaille.py
```

### **3. Préparation Sessions**
```bash
python preparation_sessions_asia_london.py
```

### **Timing Recommandé :**
- **Collecte** : 15:30-15:45 EST (avant clôture US)
- **Validité** : 24 heures
- **Sessions cibles** : Asia (22:00-06:00) et London (08:00-16:00)

---

## 📁 **STRUCTURE DES DONNÉES**

### **1. Sauvegarde Options SPX**
```
data/backups/options_spx_20250811_XXXXXX/
├── options_snapshots/          # Snapshots options
├── snapshots/options/          # Données options historiques
├── ml/options_data/           # Données ML options
├── processed/options/         # Données traitées
├── live/current_session/options/  # Données session actuelle
├── performance/options/       # Métriques performance
├── spx_real_data.json        # Données SPX réelles IBKR
└── metadata_complete.txt     # Métadonnées complètes
```

### **2. Préparation Sessions**
```
data/preparation/sessions_20250812/
├── asia_session/              # Données session Asia
│   ├── strategy.json         # Stratégie Asia
│   └── [données historiques]
├── london_session/           # Données session London
│   ├── strategy.json        # Stratégie London
│   └── [données historiques]
├── shared_data/             # Données partagées
│   ├── spx_options_backup/  # Backup options SPX
│   └── [données générales]
├── lance_asia_session.py    # Script lancement Asia
├── lance_london_session.py  # Script lancement London
└── metadata_preparation.txt # Métadonnées préparation
```

---

## 📊 **FORMATS DE SORTIE**

### **1. Fichier Données Complètes**
```
data/snapshots/options_flow/spx_niveaux_critiques_YYYYMMDD_HHMMSS.json
```

**Contenu :**
```json
{
  "metadata": {
    "timestamp": "2025-08-11T15:30:00",
    "session": "US_PRE_CLOSE",
    "source": "TWS_IBKR",
    "valid_until": "2025-08-12T15:30:00",
    "next_sessions": ["ASIA", "LONDON"]
  },
  "gamma_exposure": {
    "total_exposure": 75000000000,
    "call_gamma": 45000000000,
    "put_gamma": 30000000000,
    "net_gamma": 15000000000
  },
  "gamma_flip_level": {
    "level": 5400,
    "significance": 0.85,
    "distance_from_price": 25
  },
  "vix_data": {
    "current_vix": 18.5,
    "vix_percentile": 0.35,
    "vix_trend": "neutral"
  },
  "put_call_ratio": {
    "current_ratio": 0.75,
    "volume_ratio": 0.72,
    "ratio_trend": "decreasing"
  }
}
```

### **2. Fichier Résumé Sessions**
```
data/snapshots/options_flow/resume_sessions_asia_london.json
```

**Contenu :**
```json
{
  "session_info": {
    "collecte_time": "2025-08-11T15:30:00",
    "valid_until": "2025-08-12T15:30:00",
    "sessions_cibles": ["ASIA", "LONDON"]
  },
  "niveaux_cles": {
    "gamma_flip": 5400,
    "vix_level": 18.5,
    "put_call_ratio": 0.75,
    "dealer_position": "long"
  },
  "signaux_trading": {
    "gamma_bias": "bullish",
    "vix_signal": "low_vol",
    "flow_signal": "call_heavy",
    "dealer_signal": "long"
  },
  "niveaux_techniques": {
    "resistance_levels": [5450, 5500, 5550],
    "support_levels": [5350, 5300, 5250],
    "pin_levels": [5400, 5450, 5350]
  }
}
```

---

## 🌍 **STRATÉGIES PAR SESSION**

### **🌏 SESSION ASIA (01:00-08:00 CET)**

#### **🎯 Caractéristiques**
- **Heures** : 01:00-08:00 CET
- **Focus** : Breakout/Reversal patterns
- **Risk Level** : Moderate
- **Volume** : Faible à modéré

#### **📈 Stratégie Asia**
```json
{
  "session": "ASIA",
  "focus": "Breakout/Reversal patterns",
  "risk_level": "Moderate",
  "key_levels": [
    "Gamma Flip",
    "Call/Put Walls", 
    "VIX Support"
  ]
}
```

#### **🎯 Niveaux Clés Asia**
1. **Gamma Flip Level** : Point pivot majeur
2. **Call/Put Walls** : Zones de retournement
3. **VIX Support** : Niveaux de volatilité

### **🇬🇧 SESSION LONDON (08:00-16:30 CET)**

#### **🎯 Caractéristiques**
- **Heures** : 08:00-16:30 CET
- **Focus** : Trend continuation
- **Risk Level** : High
- **Volume** : Élevé

#### **📈 Stratégie London**
```json
{
  "session": "LONDON",
  "focus": "Trend continuation",
  "risk_level": "High",
  "key_levels": [
    "Gamma Exposure",
    "Pin Risk",
    "Dealer Positioning"
  ]
}
```

#### **🎯 Niveaux Clés London**
1. **Gamma Exposure** : Force des mouvements
2. **Pin Risk** : Zones de consolidation
3. **Dealer Positioning** : Flow du marché

---

## 🎯 **INTERPRÉTATION DES SIGNAUX**

### **Gamma Bias :**
- **Bullish** : Net gamma > 0 (dealer long gamma)
- **Bearish** : Net gamma < 0 (dealer short gamma)

### **VIX Signal :**
- **High Vol** : VIX > 25 (volatilité élevée)
- **Low Vol** : VIX < 25 (volatilité faible)

### **Flow Signal :**
- **Call Heavy** : Put/Call ratio < 0.8 (flux call dominant)
- **Put Heavy** : Put/Call ratio > 1.2 (flux put dominant)
- **Balanced** : Ratio entre 0.8 et 1.2

### **Dealer Signal :**
- **Long** : Dealers positionnés long
- **Short** : Dealers positionnés short
- **Neutral** : Position neutre

---

## 🔧 **INTÉGRATION DANS LE SYSTÈME**

### **1. Chargement des Niveaux :**
```python
def load_session_levels():
    """Charger les niveaux pour la session actuelle"""
    with open('data/snapshots/options_flow/resume_sessions_asia_london.json', 'r') as f:
        return json.load(f)
```

### **2. Application des Signaux :**
```python
def apply_options_signals(signals):
    """Appliquer les signaux options au trading"""
    if signals['gamma_bias'] == 'bullish':
        # Ajuster stratégie bullish
        pass
    elif signals['vix_signal'] == 'high_vol':
        # Ajuster gestion risque
        pass
```

### **3. Utilisation des Niveaux :**
```python
def check_technical_levels(price, levels):
    """Vérifier les niveaux techniques"""
    resistance = levels['niveaux_techniques']['resistance_levels']
    support = levels['niveaux_techniques']['support_levels']
    
    for level in resistance:
        if price >= level:
            # Signal de résistance
            pass
```

---

## 🚀 **WORKFLOW COMPLET**

### **1. Sauvegarde Options SPX (avant session US)**
```bash
python sauvegarde_niveaux_options_detaille.py
```

### **2. Préparation Sessions (pour demain)**
```bash
python preparation_sessions_asia_london.py
```

### **3. Lancement Session Asia (01:00 CET)**
```bash
cd data/preparation/sessions_20250812/
python lance_asia_session.py
```

### **4. Lancement Session London (08:00 CET)**
```bash
cd data/preparation/sessions_20250812/
python lance_london_session.py
```

---

## 📈 **EXEMPLE D'UTILISATION**

### **Session Asia (22:00-06:00) :**
1. **Charger** les niveaux collectés à 15:30 US
2. **Appliquer** les signaux gamma et VIX
3. **Utiliser** les niveaux de résistance/support
4. **Ajuster** la stratégie selon le dealer positioning

### **Session London (08:00-16:00) :**
1. **Actualiser** les niveaux si nécessaire
2. **Combiner** avec les données London
3. **Optimiser** les signaux selon le contexte

---

## ⚠️ **POINTS D'ATTENTION**

### **1. Validité des Données :**
- **Durée** : 24 heures maximum
- **Actualisation** : Collecter avant chaque session
- **Fiabilité** : Vérifier la source TWS

### **2. Interprétation :**
- **Contexte** : Considérer le contexte macro
- **Corrélation** : Vérifier les corrélations
- **Dynamique** : Les niveaux évoluent

### **3. Gestion des Erreurs :**
- **Fallback** : Données sauvegardées si échec
- **Validation** : Vérifier la cohérence des données
- **Logs** : Tracer toutes les collectes

### **4. Vérifications Avant Lancement :**
1. **IB Gateway démarré** et connecté
2. **Client ID 1** disponible
3. **Données options** sauvegardées
4. **Scripts de lancement** créés

---

## 🎉 **BÉNÉFICES**

### **1. Amélioration Précision :**
- **Niveaux précis** : Données options réelles
- **Signaux avancés** : Gamma, VIX, dealer flow
- **Timing optimal** : Collecte avant clôture

### **2. Optimisation Sessions :**
- **Asia** : Données US fraîches
- **London** : Contexte complet
- **Performance** : Meilleur win rate

### **3. Gestion Risque :**
- **Niveaux techniques** : Support/résistance précis
- **Volatilité** : Signaux VIX
- **Flow** : Compréhension du marché

### **4. Continuité :**
- **Données partagées** : Entre sessions
- **Analyse continue** : 24h/24
- **Optimisation** : Basée sur résultats

---

## 📊 **MONITORING**

- **Logs de connexion** IBKR
- **Données collectées** temps réel
- **Sauvegarde CSV** automatique
- **Performance** système
- **Niveaux gamma** mis à jour
- **Stratégies** adaptées
- **Risk management** ajusté
- **Performance** analysée

---

*Document créé le : 11 Août 2025*  
*Version : 2.0 - Document Unifié*  
*Auteur : MIA_IA_SYSTEM Team*  
*Status : ✅ PRÊT*  
*Sessions : Asia (01:00) + London (08:00)*






