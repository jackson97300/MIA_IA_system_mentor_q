# GUIDE TESTS IB GATEWAY - MIA_IA_SYSTEM

## 🚀 Démarrage Rapide

### 1. Prérequis
- ✅ IB Gateway ouvert en mode simulé
- ✅ Port 4002 accessible
- ✅ MIA_IA_SYSTEM installé

### 2. Tests Disponibles

#### Test Simple (Recommandé en premier)
```bash
python test_ib_gateway_simple.py
```
**Objectif:** Vérifier la connexion de base à IB Gateway

#### Test Complet
```bash
python test_ib_gateway_simulated.py
```
**Objectif:** Tests complets (connexion, données marché, ordres, positions)

#### Test Simple Trader
```bash
python test_simple_trader_ib_gateway.py
```
**Objectif:** Tester le trader principal avec IB Gateway

### 3. Ordre Recommandé des Tests

1. **Test Simple** - Vérifier connexion
2. **Test Complet** - Valider toutes les fonctionnalités
3. **Test Simple Trader** - Tester le système complet

## 📋 Configuration IB Gateway

### Ports par Défaut
- **IB Gateway Simulé:** 4002
- **IB Gateway Live:** 4001
- **TWS Paper:** 7497
- **TWS Live:** 7496

### Configuration MIA_IA_SYSTEM
```python
# Dans config/sierra_config.py
host = "127.0.0.1"
port = 4002  # IB Gateway simulé
client_id = 999  # Unique
environment = "PAPER"
```

## 🔍 Diagnostic des Problèmes

### Erreur de Connexion
```
❌ Échec connexion IB Gateway
```
**Solutions:**
1. Vérifier que IB Gateway est ouvert
2. Vérifier le port 4002
3. Vérifier les permissions firewall

### Erreur Import
```
❌ Module IBKR non trouvé
```
**Solutions:**
1. Vérifier l'installation de MIA_IA_SYSTEM
2. Vérifier les dépendances Python

### Pas de Données Marché
```
⚠️ Aucune donnée marché
```
**Solutions:**
1. Vérifier les souscriptions de données
2. Vérifier les heures de trading
3. Vérifier les contrats configurés

## 📊 Interprétation des Résultats

### Test Simple
```
✅ Connexion réussie!
✅ Données marché reçues
🎉 IB Gateway connecté avec succès!
```

### Test Complet
```
📊 Résultat: 5/5 tests réussis
🎉 TOUS LES TESTS RÉUSSIS!
```

### Test Simple Trader
```
📊 Statistiques de la session:
   - Trades: 0
   - Signaux: 15
   - P&L: $0.00
```

## 🎯 Tests Avancés

### Mode Data Collection
```bash
python execution/simple_trader.py --mode data_collection --target 10
```

### Mode Paper Trading
```bash
python execution/simple_trader.py --mode paper
```

### Diagnostics Complets
```bash
python execution/simple_trader.py --diagnose-all
```

## 🔧 Configuration Avancée

### Changer le Port
```python
# Dans test_ib_gateway_simple.py
port = 4001  # Pour IB Gateway live
```

### Changer le Client ID
```python
client_id = 123  # ID unique différent
```

### Tester avec TWS
```python
port = 7497  # TWS Paper
# ou
port = 7496  # TWS Live
```

## 📈 Monitoring

### Logs en Temps Réel
```bash
tail -f logs/trading.log
```

### Vérifier Statut IB Gateway
- Ouvrir IB Gateway
- Vérifier "Connected" dans l'interface
- Vérifier les messages d'erreur

### Vérifier Ports
```bash
netstat -an | grep 4002
```

## 🚨 Problèmes Courants

### 1. IB Gateway ne démarre pas
- Vérifier les permissions administrateur
- Vérifier l'installation Java
- Vérifier les paramètres de connexion

### 2. Connexion refusée
- Vérifier que le port n'est pas utilisé
- Vérifier le firewall Windows
- Vérifier les paramètres réseau

### 3. Pas de données ES
- Vérifier les souscriptions de données
- Vérifier les heures de trading CME
- Vérifier les contrats configurés

## ✅ Checklist de Validation

- [ ] IB Gateway ouvert et connecté
- [ ] Port 4002 accessible
- [ ] Test simple réussi
- [ ] Test complet réussi
- [ ] Test simple trader réussi
- [ ] Données ES reçues
- [ ] Ordres simulés fonctionnels

## 🎉 Succès!

Une fois tous les tests réussis, votre système MIA_IA_SYSTEM est prêt pour:

1. **Trading simulé** avec IB Gateway
2. **Collecte de données** pour ML
3. **Backtesting** avec données réelles
4. **Trading live** (après configuration)

## 📞 Support

En cas de problème:
1. Vérifier les logs détaillés
2. Tester chaque composant séparément
3. Vérifier la configuration IB Gateway
4. Consulter la documentation IBKR

