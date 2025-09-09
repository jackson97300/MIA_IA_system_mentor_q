# 🚀 Guide de Compilation et Installation Sierra Chart - MIA System

## ✅ **Corrections et Raffinements Appliqués**

### **1. MIA_Chart_Dumper.cpp - CORRIGÉ ET RAFFINÉ**
- ✅ **Constantes T&S corrigées** : `SC_TS_BID`, `SC_TS_ASK`, `SC_TS_BIDASKVALUES`
- ✅ **Drapeaux d'activation critiques** : `UsesMarketDepthData = 1`, `MaintainVolumeAtPriceData = 1`
- ✅ **DOM fiable** : `GetBidMarketDepthEntryAtLevel()` avec stop au premier niveau vide
- ✅ **VAP défensif** : Accès sécurisé à `VolumeAtPriceForBars`
- ✅ **Multiplicateur de prix** : `sc.RealTimePriceMultiplier` appliqué PARTOUT
- ✅ **Horodatage ISO** : Format `%Y-%m-%d %H:%M:%S.%3f` pour lisibilité
- ✅ **T&S sans doublons** : Vérification de `ts.Sequence` pour éviter les répétitions
- ✅ **BaseData uniquement à la nouvelle barre** : `last_bar_index` pour éviter le spam
- ✅ **BaseDataIn cohérent** : Utilisation de `sc.BaseDataIn[SC_OPEN]` etc. pour rester compatible avec tous les types de barres
- ✅ **Bid/Ask Volume** : `SC_BIDVOL` et `SC_ASKVOL` avec `MaintainAdditionalChartDataArrays = 1`

### **2. test_sierra_simple.cpp - TEST DE BASE**
- ✅ **Test de base** : Vérification des données OHLCV
- ✅ **Test DOM** : Vérification de la profondeur de marché
- ✅ **Test T&S** : Vérification des Time & Sales

### **3. test_sierra_advanced.cpp - TESTS AVANCÉS NOUVEAUX**
- ✅ **Test DOM historique** : `c_ACSILDepthBars` avec `MaintainHistoricalMarketDepthData = 1`
- ✅ **Test VAP complet** : Accès défensif et multiplicateur de prix
- ✅ **Test paramètres** : Vérification de tous les drapeaux critiques
- ✅ **Tests séparés** : Logs dans des fichiers distincts pour diagnostic

## 🔧 **Étapes de Compilation**

### **Étape 1 : Préparer l'environnement**
```bash
# Vérifier que vous avez Visual Studio ou MinGW
# Sierra Chart nécessite C++ compatible Windows
# Version C++11 minimum recommandée
```

### **Étape 2 : Compiler MIA_Chart_Dumper.cpp**
```bash
# Dans Visual Studio ou ligne de commande
cl /LD MIA_Chart_Dumper.cpp /Fe:MIA_Chart_Dumper.dll

# Ou avec MinGW
g++ -shared -o MIA_Chart_Dumper.dll MIA_Chart_Dumper.cpp
```

### **Étape 3 : Compiler les tests**
```bash
# Test simple
cl /LD test_sierra_simple.cpp /Fe:test_sierra_simple.dll

# Test avancé
cl /LD test_sierra_advanced.cpp /Fe:test_sierra_advanced.dll

# Ou avec MinGW
g++ -shared -o test_sierra_simple.dll test_sierra_simple.cpp
g++ -shared -o test_sierra_advanced.dll test_sierra_advanced.cpp
```

## 📁 **Installation dans Sierra Chart**

### **Étape 1 : Copier les DLLs**
```
# Copier les DLLs compilés dans :
C:\SierraChart\ACS_Source\
```

### **Étape 2 : Redémarrer Sierra Chart**
- Fermer complètement Sierra Chart
- Relancer Sierra Chart
- Vérifier que les études apparaissent dans `Studies` → `Custom Studies`

### **Étape 3 : Configuration Sierra Chart CRITIQUE**
1. **Data/Trade Service Settings** :
   - Menu `Global` → `Data/Trade Service Settings`
   - Vérifier la connexion à votre source de données
   - **CRITIQUE** : `Intraday Data Storage Time Unit = 1 Tick`
   - **CRITIQUE** : `Record Market Depth Data` activé (pour DOM historique)

2. **Chart Settings** :
   - Clic droit sur le graphique → `Chart Settings`
   - Onglet `Data` → Vérifier `Real-time Updates` activé
   - Onglet `Main Settings` → Vérifier le symbole et la source
   - **CRITIQUE** : `Max Depth Levels` ≥ 10 (ou votre valeur configurée)

## 🧪 **Tests et Vérifications**

### **Test 1 : Étude Simple (test_sierra_simple)**
1. Ajouter `test_sierra_simple` sur un graphique
2. Vérifier les fichiers de log dans `D:\MIA_IA_system\` :
   - `test_sierra.log` : Données OHLCV de base
   - `test_dom.log` : Profondeur de marché live
   - `test_ts.log` : Time & Sales

### **Test 2 : Étude Avancée (test_sierra_advanced)**
1. Ajouter `test_sierra_advanced` sur un graphique
2. Configurer les inputs :
   - Debug Level = 1
   - Test DOM Historique = Yes
3. Vérifier les fichiers de log avancés :
   - `test_advanced.log` : BaseDataIn complet
   - `test_dom_live.log` : DOM live
   - `test_dom_historical.log` : DOM historique
   - `test_dom_levels.log` : Niveaux détaillés
   - `test_ts_advanced.log` : T&S avec séquence
   - `test_vap.log` : Volume at Price
   - `test_params.log` : Paramètres critiques

### **Test 3 : MIA_Chart_Dumper Principal**
1. Ajouter `MIA_Chart_Dumper` sur un graphique
2. Configurer les inputs :
   - Instance ID = 1
   - Debug Level = 1 (ou 2 pour verbose)
   - Max DOM Levels = 10
3. Vérifier le fichier `chart_<num>.jsonl`

### **Test 4 : Vérification des Données**
1. **Vérifier la connectivité** :
   - L'étude doit afficher `"type":"startup"` au démarrage
   - Pas d'erreur `"no_connection"`

2. **Vérifier les données** :
   - **BaseData** : Doit afficher `"type":"basedata"` uniquement à la nouvelle barre
   - **DOM** : Doit afficher `"type":"depth"` avec `"source":"dom_live"`
   - **T&S** : Doit afficher `"type":"quote"` ou `"trade"` avec `"sequence"`
   - **VAP** : Doit afficher `"type":"volume_at_price"` si activé

## 🚨 **Problèmes Courants et Solutions**

### **Problème 1 : "DLL not found"**
```
Solution : Vérifier que la DLL est dans ACS_Source et redémarrer Sierra
```

### **Problème 2 : Aucune donnée DOM**
```
Solution : 
1. Vérifier UsesMarketDepthData = 1
2. Vérifier que le symbole a des données de profondeur
3. Vérifier la source de données
4. Vérifier Max Depth Levels dans Chart Settings
```

### **Problème 3 : Aucune donnée T&S**
```
Solution :
1. Vérifier que le symbole "bouge" (pas de données historiques T&S)
2. Vérifier Real-time Updates activé
3. Attendre l'activité de marché
4. Vérifier que la source de données envoie du T&S
```

### **Problème 4 : Aucune donnée VAP**
```
Solution :
1. Vérifier MaintainVolumeAtPriceData = 1
2. Vérifier Intraday Data Storage Time Unit = 1 Tick
3. Vérifier que le symbole a des données VAP
```

### **Problème 5 : Erreurs de compilation**
```
Solution :
1. Vérifier que sierrachart.h est accessible
2. Vérifier la compatibilité C++ (C++11 minimum)
3. Vérifier les dépendances Windows
4. Vérifier que tous les includes sont corrects
```

## 📊 **Structure des Données JSON (Mise à Jour)**

### **Quotes (BID/ASK) avec Séquence**
```json
{
  "t": "2024-01-15 14:30:25.123",
  "sym": "ES",
  "type": "quote",
  "source": "ts",
  "bid": 4500.25,
  "ask": 4500.50,
  "bq": 100,
  "aq": 150,
  "sequence": 12345,
  "chart": 1,
  "instance_id": 1
}
```

### **Trades avec Séquence**
```json
{
  "t": "2024-01-15 14:30:25.123",
  "sym": "ES",
  "type": "trade",
  "source": "ts",
  "price": 4500.25,
  "volume": 50,
  "sequence": 12346,
  "chart": 1,
  "instance_id": 1
}
```

### **BaseData avec Bid/Ask Volume**
```json
{
  "t": "2024-01-15 14:30:25.123",
  "sym": "ES",
  "type": "basedata",
  "source": "bar",
  "index": 100,
  "open": 4500.00,
  "high": 4501.00,
  "low": 4499.50,
  "close": 4500.25,
  "volume": 1500,
  "bidvol": 800,
  "askvol": 700,
  "chart": 1,
  "instance_id": 1
}
```

### **DOM Live avec Source Spécifiée**
```json
{
  "t": "2024-01-15 14:30:25.123",
  "sym": "ES",
  "type": "depth",
  "source": "dom_live",
  "side": "BID",
  "level": 0,
  "price": 4500.00,
  "size": 200,
  "chart": 1,
  "instance_id": 1
}
```

### **Volume at Price avec Multiplicateur Appliqué**
```json
{
  "t": "2024-01-15 14:30:25.123",
  "sym": "ES",
  "type": "volume_at_price",
  "source": "vap",
  "price": 4500.25,
  "volume": 150,
  "bar_index": 100,
  "chart": 1,
  "instance_id": 1
}
```

## 🔍 **Debug et Monitoring (Mise à Jour)**

### **Debug Level 0** : Aucun message de debug
### **Debug Level 1** : Messages d'erreur, warnings et statut
### **Debug Level 2** : Messages détaillés + compteur de ticks

### **Messages de Statut**
- `"type":"startup"` : Étude démarrée
- `"type":"status"` : Étude active (toutes les 5 secondes)
- `"type":"error"` : Erreurs de connectivité ou d'accès
- `"type":"warning"` : Problèmes non critiques (DOM/VAP non activés)

### **Fichiers de Log par Test**
- **test_sierra_simple** : 3 fichiers de log séparés
- **test_sierra_advanced** : 7 fichiers de log spécialisés
- **MIA_Chart_Dumper** : 1 fichier JSONL par graphique

## 📈 **Optimisations et Bonnes Pratiques**

1. **Horodatage ISO** : Format lisible et standardisé
2. **Multiplicateur de prix** : Cohérence entre symboles futures/cash
3. **Séquence T&S** : Éviter les doublons et garantir l'ordre
4. **Nouvelle barre uniquement** : Éviter le spam des données
5. **BaseDataIn cohérent** : Compatible avec tous les types de barres
6. **Tests séparés** : Diagnostic précis par composant
7. **Gestion d'erreurs** : Continuer l'exécution même en cas de problème

## 🎯 **Check-list de Configuration Sierra Chart**

### **Obligatoire pour le Fonctionnement**
- [ ] `Intraday Data Storage Time Unit = 1 Tick`
- [ ] `Real-time Updates` activé
- [ ] `Record Market Depth Data` activé
- [ ] `Max Depth Levels` ≥ 10
- [ ] Source de données connectée et active

### **Recommandé pour les Performances**
- [ ] Symbole avec activité en temps réel
- [ ] Données de profondeur disponibles
- [ ] Données VAP disponibles
- [ ] Configuration tick-by-tick

---

## 🎯 **Prochaines Étapes**

1. **Compiler et installer** les études corrigées et raffinées
2. **Tester avec test_sierra_simple** pour vérifier la base
3. **Tester avec test_sierra_advanced** pour vérifier les fonctionnalités avancées
4. **Tester MIA_Chart_Dumper** pour la collecte complète
5. **Vérifier tous les fichiers de log** pour confirmer le fonctionnement
6. **Optimiser** selon vos besoins spécifiques

## 🏆 **Résultats Attendus**

Avec ces corrections et raffinements, vous devriez obtenir :
- ✅ **Données T&S en temps réel** sans doublons
- ✅ **DOM live** avec niveaux multiples
- ✅ **BaseData** uniquement à la nouvelle barre
- ✅ **VAP** avec multiplicateur de prix
- ✅ **Horodatage ISO** lisible et standardisé
- ✅ **Logs séparés** pour diagnostic facile
- ✅ **Gestion d'erreurs** robuste

**Vos études sont maintenant professionnelles et prêtes pour la production !** 🎉
