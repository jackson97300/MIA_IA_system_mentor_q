# 🔧 GUIDE DE RÉSOLUTION TWS - MIA_IA_SYSTEM

## 📊 DIAGNOSTIC ACTUEL

✅ **TWS.exe en cours d'exécution**  
✅ **Port 7497 accessible** (socket)  
❌ **API IB ne fonctionne pas** (timeout)

## 🎯 PROBLÈME IDENTIFIÉ

Le problème est que **TWS accepte les connexions socket mais refuse les connexions API**. Cela indique un problème de configuration API dans TWS.

## 💡 SOLUTIONS À ESSAYER

### 1️⃣ **VÉRIFICATION CONFIGURATION TWS**

Dans TWS, suivez ces étapes :

1. **Edit > Global Configuration**
2. **API > Settings**
3. Vérifiez :
   - ✅ **Enable ActiveX and Socket Clients**
   - **Socket port: 7497**
   - ✅ **Allow connections from localhost**
   - ✅ **Read-Only API** (recommandé)
   - ✅ **Download open orders on connection**

### 2️⃣ **REDÉMARRAGE COMPLET**

1. **Fermez TWS complètement**
2. **Fermez IB Gateway** (s'il est ouvert)
3. **Attendez 30 secondes**
4. **Relancez TWS en mode Paper Trading**
5. **Connectez-vous au marché**
6. **Vérifiez que TWS est "Connected"**

### 3️⃣ **VÉRIFICATION FIREWALL**

1. **Windows Defender Firewall**
2. **Autorisez TWS** dans les applications autorisées
3. **Autorisez le port 7497**

### 4️⃣ **TEST AVEC DIFFÉRENTS PORTS**

Essayez ces configurations :

```python
# Test 1: TWS Paper (7497)
ib.connect('127.0.0.1', 7497, clientId=1)

# Test 2: TWS Live (7496)
ib.connect('127.0.0.1', 7496, clientId=1)

# Test 3: IB Gateway Paper (4002)
ib.connect('127.0.0.1', 4002, clientId=1)

# Test 4: IB Gateway Live (4001)
ib.connect('127.0.0.1', 4001, clientId=1)
```

### 5️⃣ **TEST AVEC DIFFÉRENTS CLIENT IDs**

```python
# Test avec différents Client IDs
for client_id in [1, 2, 3, 10, 100]:
    try:
        ib.connect('127.0.0.1', 7497, clientId=client_id, timeout=5)
        if ib.isConnected():
            print(f"✅ Client ID {client_id} fonctionne !")
            break
    except:
        continue
```

## 🚀 CONFIGURATION MIA_IA_SYSTEM RECOMMANDÉE

Une fois la connexion établie, utilisez cette configuration :

```python
MIA_IA_SYSTEM_CONFIG = {
    'ibkr': {
        'host': '127.0.0.1',
        'port': 7497,  # ou le port qui fonctionne
        'client_id': 1,  # ou le Client ID qui fonctionne
        'timeout': 30,
        'paper_trading': True,
        'read_only': True,
        'enable_trading': False,
    }
}
```

## 🔍 TESTS À EFFECTUER

1. **Test socket simple** ✅ (fonctionne)
2. **Test API ib_insync** ❌ (timeout)
3. **Test API ibapi** ❌ (timeout)
4. **Test différents ports** (à essayer)
5. **Test différents Client IDs** (à essayer)

## 📞 SUPPORT

Si le problème persiste :

1. **Redémarrez l'ordinateur**
2. **Réinstallez TWS**
3. **Vérifiez la version de TWS** (doit être compatible)
4. **Contactez le support IBKR**

## 🎯 PROCHAINES ÉTAPES

1. **Suivez le guide de configuration TWS**
2. **Testez les différentes solutions**
3. **Une fois connecté, lancez MIA_IA_SYSTEM**
4. **Vérifiez les données de marché**

---

**MIA_IA_SYSTEM** - Système de trading intelligent



