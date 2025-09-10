# 🔧 GUIDE TWS - IBKR EUROPE

## 📋 Vue d'ensemble

Ce guide détaille la configuration de **TWS (Trader Workstation)** pour **IBKR Europe** afin de résoudre les problèmes de connexion API.

---

## 🎯 PROBLÈMES COURANTS IBKR EUROPE

### **1. Configuration API incorrecte**
- API non activée dans TWS
- Ports mal configurés
- Firewall qui bloque

### **2. Problèmes de connexion**
- TWS non connecté au marché
- Market data non souscrit
- Client ID en conflit

### **3. Problèmes système**
- Firewall Windows
- Antivirus qui interfère
- Ports bloqués

---

## 🔧 CONFIGURATION TWS ÉTAPE PAR ÉTAPE

### **ÉTAPE 1: Démarrage TWS**

1. **Lancer TWS** :
   - Ouvrir TWS (Trader Workstation)
   - Sélectionner **"Paper Trading"** (recommandé pour tests)
   - Se connecter avec vos identifiants IBKR Europe

2. **Vérifier connexion** :
   - Status doit être **"Connected"**
   - Pas de popup de sécurité
   - Market data disponible

### **ÉTAPE 2: Configuration API**

1. **Accéder aux paramètres** :
   - Dans TWS: **Edit** → **Global Configuration**
   - Ou **File** → **Global Configuration**

2. **Configuration API Settings** :
   - Aller dans **API** → **Settings**
   - ✅ **Enable ActiveX and Socket Clients**
   - ✅ **Download open orders on connection**
   - ✅ **Include FX positions in portfolio**

3. **Configuration Ports** :
   - **Socket port**: 7497 (Paper Trading)
   - **Socket port**: 7496 (Live Trading)
   - ✅ **Allow connections from localhost**
   - ✅ **Read-Only API** (recommandé pour tests)

### **ÉTAPE 3: Configuration Firewall**

1. **Windows Defender Firewall** :
   - Ouvrir **Windows Defender Firewall**
   - **Autoriser une application**
   - Ajouter **TWS.exe** et **IBGateway.exe**

2. **Ports à autoriser** :
   - **7497** : TWS Paper Trading
   - **7496** : TWS Live Trading
   - **4001** : IB Gateway Live
   - **4002** : IB Gateway Paper

### **ÉTAPE 4: Test Connexion**

1. **Redémarrer TWS** :
   - Fermer TWS complètement
   - Relancer TWS
   - Vérifier configuration

2. **Test Python** :
   ```bash
   python diagnostic_tws_complet.py
   ```

---

## 🛠️ RÉSOLUTION PROBLÈMES SPÉCIFIQUES

### **Problème 1: "Connection refused"**

**Causes possibles :**
- TWS non démarré
- Port incorrect
- API non activée

**Solutions :**
1. Vérifier TWS en cours d'exécution
2. Vérifier port dans configuration
3. Activer API dans TWS

### **Problème 2: "Client ID already in use"**

**Causes possibles :**
- Autre application connectée
- TWS redémarré sans fermer connexion

**Solutions :**
1. Changer Client ID (1, 999, 1000)
2. Redémarrer TWS
3. Attendre quelques minutes

### **Problème 3: "Market data not available"**

**Causes possibles :**
- Market data non souscrit
- Compte en mode paper trading
- Connexion marché perdue

**Solutions :**
1. Vérifier souscriptions market data
2. Se reconnecter au marché
3. Vérifier statut compte

### **Problème 4: "Firewall blocking connection"**

**Causes possibles :**
- Windows Defender
- Antivirus
- Pare-feu réseau

**Solutions :**
1. Autoriser TWS dans firewall
2. Désactiver antivirus temporairement
3. Vérifier pare-feu réseau

---

## 🔍 DIAGNOSTIC AVANCÉ

### **Test 1: Vérification processus**
```bash
# Windows
tasklist /FI "IMAGENAME eq tws.exe"

# Linux/Mac
ps aux | grep tws
```

### **Test 2: Vérification ports**
```bash
# Test port 7497
telnet 127.0.0.1 7497

# Ou avec Python
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 7497)); print('Port ouvert')"
```

### **Test 3: Test connexion Python**
```python
from ib_insync import IB

ib = IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
    if ib.isConnected():
        print("✅ Connexion réussie")
    else:
        print("❌ Connexion échouée")
    ib.disconnect()
except Exception as e:
    print(f"❌ Erreur: {e}")
```

---

## 💡 CONSEILS IBKR EUROPE

### **1. Utiliser IB Gateway**
- Plus stable que TWS
- Moins de problèmes de configuration
- Recommandé pour trading automatique

### **2. Configuration Paper Trading**
- Commencer avec Paper Trading
- Tester connexion et API
- Passer en Live Trading après validation

### **3. Client ID recommandés**
- **1** : Client ID par défaut
- **999** : Client ID alternatif
- **1000** : Client ID de secours

### **4. Market Data Europe**
- Vérifier souscriptions CME
- Vérifier souscriptions OPRA
- Vérifier connexion marché

---

## 🚀 ALTERNATIVES SI PROBLÈME PERSISTE

### **1. IB Gateway**
- Plus stable que TWS
- Configuration plus simple
- Moins de problèmes de ports

### **2. IBKR Web API REST**
- API moderne et stable
- Pas de TWS/Gateway nécessaire
- Connexion HTTP directe

### **3. Support IBKR Europe**
- Contacter support IBKR Europe
- Problème spécifique à la région
- Assistance technique

---

## 📞 SUPPORT ET CONTACT

### **IBKR Europe Support :**
- **Téléphone** : +44 20 7715 9999
- **Email** : support@interactivebrokers.co.uk
- **Chat** : Disponible sur le portail

### **Documentation :**
- [IBKR Europe API](https://www.interactivebrokers.co.uk/en/trading/ib-api.php)
- [TWS Configuration](https://www.interactivebrokers.co.uk/en/trading/tws.php)

---

## 🎯 CHECKLIST FINALE

### **Avant de tester MIA_IA :**
- [ ] TWS démarré et connecté
- [ ] API activée dans TWS
- [ ] Port 7497 accessible
- [ ] Firewall configuré
- [ ] Test Python réussi
- [ ] Market data disponible

### **Si problème persiste :**
- [ ] Essayer IB Gateway
- [ ] Tester différents Client ID
- [ ] Vérifier support IBKR Europe
- [ ] Considérer IBKR Web API REST

---

**Document créé pour :** IBKR Europe
**Version :** 1.0
**Dernière mise à jour :** 2025-01-XX
**Statut :** Guide de configuration TWS
















