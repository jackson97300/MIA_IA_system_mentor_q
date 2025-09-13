# 🚀 MIA_IA_SYSTEM - Guide de Lancement Opérationnel

## 📋 Prérequis

### 1. **Système**
- Windows 10/11 (64-bit)
- Python 3.11+
- Sierra Chart installé et configuré
- 8GB RAM minimum, 16GB recommandé
- 50GB espace disque libre

### 2. **Sierra Chart**
- Version 2500+ avec custom study compilée
- Ports DTC configurés : ES (11099), NQ (11100)
- Symboles : ESU25_FUT_CME, NQU25_FUT_CME, VIX
- Charts 3, 4, 8, 10 actifs

### 3. **Python Environment**
```bash
# Installation des dépendances
pip install -e .

# Ou avec poetry (recommandé)
poetry install --extras "sierra monitoring"
```

### 4. **Configuration**
```bash
# Copier le fichier d'environnement
cp env.example .env

# Éditer .env avec vos paramètres
# Variables critiques :
# - MIA_DATA_PATH=D:\MIA_IA_system
# - SIERRA_DTC_PORT_ES=11099
# - SIERRA_DTC_PORT_NQ=11100
```

## 🎯 Lancement du Système

### **Mode 1 : Collecteur 24/7 (Recommandé)**

```bash
# Lancement du collecteur principal
mia-launch collector --charts 3,4,8,10 --mode production

# Ou directement
python -m mia_ia_system.launchers.collector --charts 3,4,8,10 --mode production
```

**Vérifications :**
- ✅ Fichiers JSONL générés dans `D:\MIA_IA_system\`
- ✅ Fichier unifié `mia_unified_YYYYMMDD.jsonl` créé
- ✅ Logs dans `logs/collector.log`

### **Mode 2 : Trading Paper (Test)**

```bash
# Lancement en mode paper trading
mia-launch trading --mode paper --strategy battle_navale

# Ou directement
python -m mia_ia_system.launchers.launch_24_7 --mode paper
```

**Vérifications :**
- ✅ Connexion Sierra Chart établie
- ✅ Données MenthorQ reçues
- ✅ Signaux générés (logs `logs/trading.log`)

### **Mode 3 : Trading Live (Production)**

⚠️ **ATTENTION : Mode réel avec argent**

```bash
# Lancement en mode live (après tests complets)
mia-launch trading --mode live --strategy battle_navale --max-position 1

# Ou directement
python -m mia_ia_system.launchers.launch_24_7 --mode live --max-position 1
```

**Prérequis obligatoires :**
- ✅ Tests d'acceptation passés
- ✅ Kill-switch opérationnel
- ✅ Limites de risque configurées
- ✅ Hard-stop côté broker

## 🔧 Commandes de Maintenance

### **Vérification du Système**
```bash
# Test de santé général
mia-test health-check

# Test des composants
mia-test schema-validation
mia-test menthorq-integration
mia-test kill-switch
```

### **Monitoring**
```bash
# Visionneuse de logs en temps réel
mia-launch monitor --live

# Métriques système
mia-launch metrics --export csv
```

### **Gestion des Données**
```bash
# Nettoyage des anciens fichiers
mia-launch cleanup --days 30

# Validation des données
mia-launch validate-data --file mia_unified_20250107.jsonl
```

## 📊 Checklist Pré-Séance US

### **Avant 9h30 EST (15h30 CET)**

- [ ] **Sierra Chart** : Vérifier connexion DTC
- [ ] **Données** : Fichiers JSONL du jour présents
- [ ] **VIX** : Valeur cohérente (< 50)
- [ ] **MenthorQ** : Niveaux gamma mis à jour
- [ ] **Système** : Kill-switch actif
- [ ] **Logs** : Aucune erreur critique

### **Pendant la Séance**

- [ ] **Latence** : < 1 seconde (logs)
- [ ] **Données** : Pas de trous > 5 minutes
- [ ] **Signaux** : Génération normale
- [ ] **Exécution** : Ordres passés correctement
- [ ] **Risque** : Drawdown < limite

### **Après la Séance**

- [ ] **Résultats** : PnL journalier calculé
- [ ] **Logs** : Archivage automatique
- [ ] **Données** : Rotation des fichiers
- [ ] **Rapport** : Génération automatique

## 🚨 Gestion des Incidents

### **Problème : Pas de données**
```bash
# Diagnostic
mia-launch diagnose --component data-collection

# Redémarrage
mia-launch restart --component collector
```

### **Problème : Kill-switch déclenché**
```bash
# Vérification des causes
mia-launch logs --component safety --level ERROR

# Réactivation (si problème résolu)
mia-launch reset --component kill-switch
```

### **Problème : Sierra Chart déconnecté**
```bash
# Vérification des ports
netstat -an | findstr "11099\|11100"

# Redémarrage Sierra Chart
# Puis redémarrage du système
mia-launch restart --full
```

## 📈 Monitoring des Performances

### **Métriques Clés**
- **Latence** : < 1 seconde
- **Win Rate** : 65-70% (cible)
- **Drawdown** : < 15%
- **Trades/jour** : 5-10

### **Alertes Automatiques**
- Drawdown > 10% → Alerte
- Latence > 2s → Alerte
- Pas de données > 5min → Kill-switch
- Erreurs > 10/h → Alerte

## 🔒 Sécurité

### **Modes de Sécurité**
1. **Simulation** : Aucun ordre réel
2. **Paper** : Ordres simulés avec données réelles
3. **Live** : Ordres réels (avec protections)

### **Protections Actives**
- Kill-switch automatique
- Limites de position
- Limites de perte quotidienne
- Hard-stop côté broker

## 📞 Support

### **Logs Importants**
- `logs/collector.log` : Collecte de données
- `logs/trading.log` : Exécution des trades
- `logs/safety.log` : Kill-switch et sécurité
- `logs/system.log` : Système général

### **En Cas de Problème**
1. Vérifier les logs
2. Tester les composants individuellement
3. Redémarrer en mode simulation
4. Contacter le support technique

---

**⚠️ IMPORTANT : Toujours tester en mode simulation avant le live trading !**

