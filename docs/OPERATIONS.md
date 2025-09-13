# 🔧 MIA_IA_SYSTEM - Guide Opérationnel

## 📋 Opérations Quotidiennes

### **Rotation des Fichiers**

#### **Automatique (Recommandé)**
```bash
# Configuration dans feature_config.json
"data_sources": {
  "rotation_schedule": "daily",
  "retention_days": 30,
  "compression": true
}
```

#### **Manuelle**
```bash
# Rotation quotidienne
mia-launch rotate --date 20250107

# Compression des anciens fichiers
mia-launch compress --older-than 7

# Suppression des fichiers > 30 jours
mia-launch cleanup --retention 30
```

### **Purge des Données**

#### **Critères de Purge**
- Fichiers JSONL > 30 jours
- Logs > 7 jours
- Cache temporaire > 1 jour
- Snapshots de test > 3 jours

#### **Commandes**
```bash
# Purge complète
mia-launch purge --all --confirm

# Purge sélective
mia-launch purge --type logs --older-than 7
mia-launch purge --type data --older-than 30
```

### **Vérification Espace Disque**

#### **Seuils d'Alerte**
- < 10GB libre → Alerte
- < 5GB libre → Arrêt automatique
- < 1GB libre → Urgence

#### **Commandes**
```bash
# Vérification espace
mia-launch disk-check

# Nettoyage automatique
mia-launch auto-cleanup --threshold 10GB
```

## 🔄 Redémarrage du Service

### **Redémarrage Standard**
```bash
# Arrêt propre
mia-launch stop --graceful

# Redémarrage
mia-launch start --mode production
```

### **Redémarrage d'Urgence**
```bash
# Arrêt forcé
mia-launch stop --force

# Redémarrage complet
mia-launch restart --full --reset-cache
```

### **Redémarrage par Composant**
```bash
# Redémarrage collecteur uniquement
mia-launch restart --component collector

# Redémarrage trading uniquement
mia-launch restart --component trading

# Redémarrage monitoring uniquement
mia-launch restart --component monitoring
```

## 📊 Checklist Séance US

### **Pré-Séance (9h00 EST / 15h00 CET)**

#### **Vérifications Système**
- [ ] **Sierra Chart** : Connexion DTC active
- [ ] **Ports** : 11099 (ES), 11100 (NQ) ouverts
- [ ] **Symboles** : ESU25, NQU25, VIX actifs
- [ ] **Charts** : 3, 4, 8, 10 fonctionnels

#### **Vérifications Données**
- [ ] **Fichiers JSONL** : Générés depuis minuit
- [ ] **Fichier unifié** : `mia_unified_YYYYMMDD.jsonl` présent
- [ ] **VIX** : Valeur cohérente (10-50)
- [ ] **MenthorQ** : Niveaux gamma mis à jour

#### **Vérifications Système**
- [ ] **Kill-switch** : Actif et testé
- [ ] **Limites** : Position et perte configurées
- [ ] **Logs** : Aucune erreur critique
- [ ] **Latence** : < 1 seconde

### **Pendant la Séance (9h30-16h00 EST)**

#### **Monitoring Continu**
- [ ] **Latence** : Surveillance temps réel
- [ ] **Données** : Pas de trous > 5 minutes
- [ ] **Signaux** : Génération normale
- [ ] **Exécution** : Ordres passés correctement
- [ ] **Risque** : Drawdown < limite

#### **Alertes à Surveiller**
- [ ] **Latence > 2s** : Vérifier connexion
- [ ] **Pas de données > 5min** : Kill-switch
- [ ] **Erreurs > 10/h** : Diagnostic
- [ ] **Drawdown > 10%** : Arrêt si nécessaire

### **Post-Séance (16h00 EST)**

#### **Fermeture**
- [ ] **Positions** : Fermées automatiquement
- [ ] **Ordres** : Annulés
- [ ] **PnL** : Calculé et loggé
- [ ] **Rapport** : Généré automatiquement

#### **Maintenance**
- [ ] **Logs** : Archivés
- [ ] **Données** : Rotées
- [ ] **Cache** : Nettoyé
- [ ] **Métriques** : Exportées

## 🚨 Matrices de Ports DTC

### **Ports Sierra Chart**
| Symbole | Port DTC | Description |
|---------|----------|-------------|
| ES      | 11099    | E-mini S&P 500 |
| NQ      | 11100    | E-mini NASDAQ 100 |
| VIX     | 11098    | VIX Index (optionnel) |

### **Configuration Sierra Chart**
```
1. File → Global Settings → Data/Trade
2. DTC Server Settings
3. Port 11099 → ES
4. Port 11100 → NQ
5. Enable "Allow Trading"
```

### **Vérification Ports**
```bash
# Windows
netstat -an | findstr "11099\|11100"

# Résultat attendu :
# TCP    0.0.0.0:11099    0.0.0.0:0    LISTENING
# TCP    0.0.0.0:11100    0.0.0.0:0    LISTENING
```

## 📈 Monitoring des Performances

### **Métriques Temps Réel**
```bash
# Dashboard live
mia-launch dashboard --live

# Métriques spécifiques
mia-launch metrics --component trading
mia-launch metrics --component data-collection
mia-launch metrics --component safety
```

### **Export des Données**
```bash
# Export CSV
mia-launch export --format csv --date 20250107

# Export JSON
mia-launch export --format json --date 20250107

# Export Prometheus
mia-launch export --format prometheus --port 9090
```

### **Rapports Automatiques**
- **Quotidien** : PnL, trades, performance
- **Hebdomadaire** : Tendances, optimisations
- **Mensuel** : Analyse complète, recommandations

## 🔧 Maintenance Préventive

### **Quotidienne**
- Vérification espace disque
- Nettoyage logs anciens
- Test kill-switch
- Vérification connexions

### **Hebdomadaire**
- Test complet du système
- Validation des données
- Mise à jour des niveaux MenthorQ
- Analyse des performances

### **Mensuelle**
- Nettoyage complet
- Optimisation base de données
- Mise à jour des modèles ML
- Audit de sécurité

## 🚨 Procédures d'Urgence

### **Kill-Switch Déclenché**
1. **Identifier la cause** : `mia-launch logs --component safety`
2. **Résoudre le problème** : Connexion, données, etc.
3. **Réinitialiser** : `mia-launch reset --component kill-switch`
4. **Redémarrer** : `mia-launch restart --component trading`

### **Perte de Connexion Sierra**
1. **Vérifier Sierra Chart** : Redémarrer si nécessaire
2. **Vérifier ports DTC** : `netstat -an | findstr "11099"`
3. **Redémarrer collecteur** : `mia-launch restart --component collector`
4. **Vérifier données** : `mia-launch validate-data --live`

### **Erreurs Système**
1. **Arrêt d'urgence** : `mia-launch stop --force`
2. **Diagnostic** : `mia-launch diagnose --full`
3. **Redémarrage** : `mia-launch start --mode simulation`
4. **Test complet** : `mia-launch test --full`

## 📞 Escalade

### **Niveau 1 : Opérateur**
- Problèmes de routine
- Redémarrages simples
- Vérifications standard

### **Niveau 2 : Support Technique**
- Problèmes complexes
- Erreurs système
- Optimisations

### **Niveau 3 : Développement**
- Bugs critiques
- Nouvelles fonctionnalités
- Architecture

---

**📋 Checklist Rapide :**
- [ ] Sierra Chart connecté
- [ ] Ports DTC ouverts
- [ ] Données JSONL générées
- [ ] Kill-switch actif
- [ ] Logs sans erreur
- [ ] Espace disque > 10GB

