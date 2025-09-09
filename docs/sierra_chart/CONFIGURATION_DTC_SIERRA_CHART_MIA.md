# CONFIGURATION DTC SIERRA CHART POUR MIA_IA_SYSTEM

## 📋 TABLE DES MATIÈRES

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture 2 Instances](#architecture-2-instances)
3. [Configuration DTC](#configuration-dtc)
4. [Paramètres Détaillés](#paramètres-détaillés)
5. [Intégration MIA](#intégration-mia)
6. [Tests et Validation](#tests-et-validation)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## 🎯 VUE D'ENSEMBLE

### **Objectif**
Configuration de Sierra Chart avec protocole DTC pour l'intégration avec MIA_IA_SYSTEM, permettant la réception de données futures ES et NQ en temps réel avec Market Depth.

### **Architecture**
- **2 instances Sierra Chart** : 1 pour ES, 1 pour NQ
- **Protocole DTC** : Connexion native et stable
- **Market Depth** : Level 2 complet pour Orderflow
- **Visualisation** : Trades MIA visibles sur graphiques

---

## 🏗️ ARCHITECTURE 2 INSTANCES

### **Configuration Recommandée**

```
MIA_IA_SYSTEM (Backend)
├── Instance ES : E-mini S&P 500 Futures
│   ├── Port DTC : 11099 (Trading)
│   ├── Port Historical : 11098
│   └── Symbol : ESU25_FUT_CME
└── Instance NQ : E-mini NASDAQ Futures
    ├── Port DTC : 11100 (Trading)
    ├── Port Historical : 11097
    └── Symbol : NQU25_FUT_CME
```

### **Architecture Trading**

- **Market Data** : `MIA_Chart_Dumper_patched.cpp` → `mia_unified_YYYYMMDD.jsonl`
- **Trading** : DTC Sierra Chart (ports 11099/11100) via `core/sierra_order_router.py`
- **Pas de DTC** pour les données (uniquement pour les ordres)

### **Avantages de cette Architecture**
- **Performance optimisée** : Chaque instance dédiée
- **Pas de conflit** : Ports séparés
- **Stabilité** : Connexions indépendantes
- **Flexibilité** : Configurations spécifiques par instrument

---

## ⚙️ CONFIGURATION DTC

### **Étapes de Configuration**

#### **1. Instance ES (E-mini S&P 500)**

**Accès aux paramètres :**
1. **Global Settings** → **Data/Trade**
2. **Onglet** : "DTC Protocol Server"

**Paramètres à configurer :**
```
Enable DTC Protocol Server: Yes
Listening Port: 11099
Historical Data Port: 11098
Allow Trading: Yes
Require Authentication: No
Require TLS: No
```

#### **2. Instance NQ (E-mini NASDAQ)**

**Accès aux paramètres :**
1. **Global Settings** → **Data/Trade**
2. **Onglet** : "DTC Protocol Server"

**Paramètres à configurer :**
```
Enable DTC Protocol Server: Yes
Listening Port: 11100
Historical Data Port: 11097
Allow Trading: Yes
Require Authentication: No
Require TLS: No
```

---

## 📊 PARAMÈTRES DÉTAILLÉS

### **Paramètres Critiques**

| Paramètre | Instance ES | Instance NQ | Description |
|-----------|-------------|-------------|-------------|
| **Enable DTC Protocol Server** | `Yes` | `Yes` | Active le serveur DTC |
| **Listening Port** | `11099` | `11100` | Port d'écoute pour MIA |
| **Historical Data Port** | `11098` | `11097` | Port données historiques |
| **Allow Trading** | `Yes` | `Yes` | Permet trading via DTC |
| **Require Authentication** | `No` | `No` | Simplifie connexion |
| **Require TLS** | `No` | `No` | Pas de chiffrement SSL |

### **Paramètres Optionnels**

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Use Delayed Sends** | `Yes` | Optimise performance |
| **Auto Send Security Definition** | `No` | Pas nécessaire pour MIA |
| **Enable JSON Logging** | `No` | Réduit logs |
| **Allowed Incoming IPs** | `Local Computer Only` | Sécurité |

---

## 🔌 INTÉGRATION MIA

### **Configuration MIA pour DTC**

```python
# Configuration DTC pour MIA_IA_SYSTEM
DTC_CONFIG = {
    'ES_INSTANCE': {
        'host': 'localhost',
        'port': 11099,
        'symbol': 'ESU26_FUT_CME',
        'description': 'E-mini S&P 500 Futures'
    },
    'NQ_INSTANCE': {
        'host': 'localhost', 
        'port': 11100,
        'symbol': 'NQU26_FUT_CME',
        'description': 'E-mini NASDAQ Futures'
    }
}

# Paramètres de connexion
CONNECTION_PARAMS = {
    'timeout': 30,
    'reconnect_interval': 5,
    'max_reconnect_attempts': 10,
    'heartbeat_interval': 30
}
```

### **Données Disponibles via DTC**

#### **Données Temps Réel**
- **OHLC** : Open, High, Low, Close
- **Volume** : Volume par barre
- **Bid/Ask** : Spreads en temps réel
- **Market Depth** : Level 2 (10 niveaux)

#### **Données Orderflow**
- **Cumulative Delta** : Pression achat/vente
- **Volume Imbalance** : Déséquilibre volume
- **Tick Data** : Données tick par tick
- **Smart Money** : Détection flux institutionnel

---

## 🧪 TESTS ET VALIDATION

### **Checklist de Validation**

#### **1. Test Connexion DTC**
- [ ] **Instance ES** : Port 11099 accessible
- [ ] **Instance NQ** : Port 11100 accessible
- [ ] **DTC Protocol Server is Listening** : `Yes` pour les deux
- [ ] **DTC Protocol Clients** : `1` (quand MIA connecté)

#### **1.1. Health Check Automatique**
```bash
# Test simple
python tools/sierra_health_check.py

# Monitoring continu
python tools/sierra_health_check.py --monitor 30

# Test rapide
python tools/sierra_health_check.py --quick
```

#### **1.2. Test Routeur d'Ordres**
```bash
# Test unitaire
python tests/test_sierra_order_router.py

# Test configuration
python -m config.sierra_trading_ports
```

#### **2. Test Données Temps Réel**
- [ ] **Prix ES** : Mise à jour en temps réel
- [ ] **Prix NQ** : Mise à jour en temps réel
- [ ] **Volume** : Données volume correctes
- [ ] **Market Depth** : Level 2 visible

#### **3. Test Intégration MIA**
- [ ] **Connexion MIA** : Réussie aux deux instances
- [ ] **Réception données** : MIA reçoit les données
- [ ] **Latence** : <50ms pour données temps réel
- [ ] **Stabilité** : Connexion stable sur 24h

### **Métriques de Performance**

| Métrique | Objectif | Mesure |
|----------|----------|--------|
| **Latence DTC** | <10ms | Temps réponse |
| **Uptime** | >99.9% | Disponibilité |
| **Data Quality** | >99.5% | Données complètes |
| **Reconnection** | <5s | Temps reconnexion |

---

## 🔧 TROUBLESHOOTING

### **Problèmes Courants**

#### **1. DTC Server Not Listening**
**Symptôme :** `DTC Protocol Server is Listening: No`

**Solutions :**
- Vérifier `Enable DTC Protocol Server: Yes`
- Redémarrer Sierra Chart
- Vérifier que le port n'est pas utilisé par un autre processus

#### **2. Port Already in Use**
**Symptôme :** Erreur de connexion au port

**Solutions :**
- Changer le port dans la configuration
- Vérifier qu'aucune autre instance n'utilise le port
- Redémarrer Sierra Chart

#### **3. MIA Cannot Connect**
**Symptôme :** MIA ne peut pas se connecter à DTC

**Solutions :**
- Vérifier les paramètres de connexion MIA
- Vérifier que les ports sont corrects
- Vérifier `Allow Trading: Yes`
- Vérifier `Require Authentication: No`

### **Logs de Diagnostic**

#### **Sierra Chart Logs**
- **Global Settings** → **Data/Trade** → **View**
- Vérifier les erreurs de connexion
- Vérifier les tentatives de reconnexion

#### **MIA Logs**
- Vérifier les logs de connexion DTC
- Vérifier les erreurs de réception données
- Vérifier la latence des données

---

## 🛠️ MAINTENANCE

### **Maintenance Préventive**

#### **Quotidien**
- [ ] Vérifier connexion DTC
- [ ] Vérifier qualité données
- [ ] Vérifier latence
- [ ] Vérifier logs d'erreur

#### **Hebdomadaire**
- [ ] Redémarrer instances Sierra Chart
- [ ] Vérifier mises à jour Sierra Chart
- [ ] Nettoyer logs anciens
- [ ] Vérifier performance système

#### **Mensuel**
- [ ] Vérifier licences Sierra Chart
- [ ] Mettre à jour documentation
- [ ] Réviser paramètres de performance
- [ ] Sauvegarder configurations

### **Sauvegarde Configuration**

#### **Fichiers à Sauvegarder**
- **Configuration Sierra Chart** : Paramètres DTC
- **Configuration MIA** : Paramètres connexion DTC
- **Logs** : Historique des connexions
- **Documentation** : Ce document

#### **Procédure de Sauvegarde**
1. **Exporter** configuration Sierra Chart
2. **Sauvegarder** fichier de config MIA
3. **Archiver** logs importants
4. **Mettre à jour** documentation

---

## 📈 OPTIMISATION

### **Optimisations Recommandées**

#### **Performance**
- **Use Delayed Sends** : `Yes` pour optimiser latence
- **Network Socket Delayed Send Interval** : `0` pour latence minimale
- **JSON Compact Encoding** : `Yes` pour réduire taille données

#### **Stabilité**
- **Reconnect on Failure** : `Yes` pour reconnexion automatique
- **Allowed Incoming IPs** : `Local Computer Only` pour sécurité
- **Require Authentication** : `No` pour simplifier

#### **Monitoring**
- **Enable JSON Logging** : `No` pour réduire logs
- **FIX Logging** : `Yes` pour debugging si nécessaire
- **Heartbeat** : Configuré dans MIA

---

## 🎯 CONCLUSION

### **Configuration Finale**

**Instance ES :**
- **Port DTC** : 11099
- **Port Historical** : 11098
- **Statut** : ✅ Actif et prêt

**Instance NQ :**
- **Port DTC** : 11100
- **Port Historical** : 11097
- **Statut** : ✅ Actif et prêt

### **Avantages Obtenus**

✅ **Données futures ES/NQ** en temps réel  
✅ **Market Depth Level 2** complet  
✅ **Orderflow** avancé pour MIA  
✅ **Visualisation** professionnelle des trades  
✅ **Latence ultra-faible** via DTC  
✅ **Stabilité** maximale avec 2 instances  

### **Prêt pour MIA**

**Votre configuration Sierra Chart est maintenant parfaitement optimisée pour MIA_IA_SYSTEM !**

---

## 📞 SUPPORT

### **En cas de problème :**

1. **Vérifier** ce document en premier
2. **Consulter** la section Troubleshooting
3. **Vérifier** les logs Sierra Chart et MIA
4. **Redémarrer** les instances si nécessaire
5. **Contacter** le support si problème persiste

### **Documentation Sierra Chart :**
- **Site officiel** : https://www.sierrachart.com
- **Documentation DTC** : https://www.sierrachart.com/index.php?page=doc/helpdetails76.html
- **Support** : Via le forum Sierra Chart

---

*Document créé le : 27 août 2025*  
*Version : 1.0*  
*Système : MIA_IA_SYSTEM*  
*Configuration : Sierra Chart DTC 2 Instances*



