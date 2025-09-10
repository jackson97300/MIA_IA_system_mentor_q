# 🔧 GUIDE DE RÉSOLUTION DES PROBLÈMES IBKR

## ❌ ERREURS RÉCURRENTES IDENTIFIÉES

### 1. **ConnectionRefusedError - Port 7497 fermé**

**Erreur :**
```
API connection failed: ConnectionRefusedError(22, 'Le système distant a refusé la connexion réseau', None, 1225, None)
Make sure API port on TWS/IBG is open
```

**Solutions :**

#### A. **Démarrer IB Gateway**
1. Ouvrir IB Gateway
2. Se connecter avec vos identifiants
3. Vérifier que le port 7497 est ouvert

#### B. **Vérifier Configuration API**
1. Dans IB Gateway : `Edit` → `Global Configuration`
2. Onglet `API` → `Settings`
3. ✅ Cocher `Enable ActiveX and Socket EClients`
4. Vérifier `Socket Port` = 7497 (Paper Trading)
5. Redémarrer IB Gateway

#### C. **Ports par défaut :**
- **Paper Trading :** 7497 (IB Gateway) / 7497 (TWS)
- **Live Trading :** 4002 (IB Gateway) / 7496 (TWS)

### 2. **Messages Confus dans les Logs**

**Problème :** Le système affiche "✅ Connexion IBKR réussie!" même en mode simulation

**Solution :** ✅ **CORRIGÉ** - Maintenant les messages sont clairs :
- `✅ Connexion IBKR RÉELLE réussie` = Vraie connexion
- `❌ Connexion IBKR échouée - Activation mode simulation` = Mode simulation

## 🔧 CORRECTIONS APPLIQUÉES

### 1. **Messages de Log Améliorés**
- Distinction claire entre connexion réelle et simulation
- Messages d'erreur plus explicites
- Indicateurs visuels (✅/❌) pour faciliter la lecture

### 2. **Logique de Connexion Corrigée**
- Vérification du mode simulation
- Fallback automatique vers données simulées
- Pas de confusion entre succès et échec

## 🚀 PROCÉDURE DE RÉSOLUTION

### **Étape 1 : Vérifier IB Gateway**
```bash
# Vérifier si IB Gateway est démarré
netstat -an | findstr 7497
```

### **Étape 2 : Configuration IB Gateway**
1. Ouvrir IB Gateway
2. `Edit` → `Global Configuration`
3. Onglet `API` → `Settings`
4. ✅ `Enable ActiveX and Socket EClients`
5. `Socket Port` = 7497
6. Redémarrer

### **Étape 3 : Tester la Connexion**
```bash
# Lancer le système
python launch_24_7_orderflow_trading.py --dry-run
```

### **Étape 4 : Vérifier les Logs**
- ✅ `Connexion IBKR RÉELLE réussie` = OK
- ❌ `Connexion IBKR échouée` = Problème à résoudre

## 📊 MODE SIMULATION

Si la connexion IBKR échoue, le système bascule automatiquement en mode simulation :
- ✅ Collecte de données simulées
- ✅ Trading simulé (DRY RUN)
- ✅ Pas de perte de données
- ✅ Système continue de fonctionner

## 🔍 DIAGNOSTIC AVANCÉ

### **Vérifier les Ports**
```bash
# Windows
netstat -an | findstr 7497

# Linux/Mac
netstat -an | grep 7497
```

### **Tester Connexion Manuelle**
```python
from ib_insync import IB

ib = IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=1)
    print("✅ Connexion réussie")
    ib.disconnect()
except Exception as e:
    print(f"❌ Erreur: {e}")
```

### **Logs Détaillés**
Le système affiche maintenant :
- 🔗 Tentative de connexion
- ❌ Erreurs spécifiques
- ✅ Succès de connexion
- 📊 Source des données (IBKR/SIMULATION)

## 🎯 RÉSULTAT ATTENDU

Après correction, vous devriez voir :
```
🔗 Tentative connexion IBKR...
🔗 Connexion à 127.0.0.1:7497...
✅ Connexion IBKR RÉELLE réussie!
📊 Source: IBKR (données réelles)
```

Au lieu de :
```
❌ Connexion IBKR échouée - Activation mode simulation
📊 Source: SIMULATION (fallback)
```

## 📞 SUPPORT

Si les problèmes persistent :
1. Vérifier la version d'IB Gateway
2. Redémarrer IB Gateway
3. Vérifier les paramètres de pare-feu
4. Contacter le support IBKR si nécessaire
