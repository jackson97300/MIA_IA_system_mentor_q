# STRATÉGIE 15MIN + 1HOUR - DOCUMENT DE MÉMOIRE
## MIA_IA_SYSTEM - APPROCHE VALIDÉE

---

## **📋 DÉCISION STRATÉGIQUE**

### **✅ APPROCHE CHOISIE : OPTION 1**
```
Configuration : 15min + 1hour (Direction)
Timeframes : ["15min", "1hour"]
Objectif : Direction macro + Exécution précise
```

### **🎯 OBJECTIFS**
```
✅ Direction claire (1hour) - 30% poids
✅ Exécution précise (15min) - 70% poids
✅ Confirmation robuste sans excès
✅ Équilibre complexité/performance
✅ Maintenance modérée
```

---

## **⚖️ CONFIGURATION TECHNIQUE**

### **📊 POIDS TIMEFRAMES**
```python
timeframes = ["15min", "1hour"]
weights = {
    "15min": 0.70,  # 70% - Exécution précise
    "1hour": 0.30   # 30% - Direction macro
}
```

### **🎪 LOGIQUE DE DÉCLENCHEMENT**
```python
# Logique de confluence
if 1hour_signal == "BULLISH" and 15min_signal == "BULLISH":
    return "LONG"
elif 1hour_signal == "BEARISH" and 15min_signal == "BEARISH":
    return "SHORT"
else:
    return "NO_TRADE"
```

### ** SEUILS DE CONFIRMATION**
```python
# Seuils minimum
MIN_15MIN_CONFLUENCE = 0.65    # 65% confluence 15min
MIN_1HOUR_CONFLUENCE = 0.60    # 60% confluence 1hour
MIN_FINAL_CONFLUENCE = 0.70    # 70% confluence finale
```

---

## **📈 AVANTAGES DE CETTE APPROCHE**

### **✅ ÉQUILIBRE PARFAIT**
```
✅ Complexité modérée (2 timeframes)
✅ Performance acceptable (~3-5ms)
✅ Confirmation robuste
✅ Maintenance gérable
✅ Risque conflits faible
```

### **✅ VALIDATION ROBUSTE**
```
✅ 1hour = Direction macro claire
✅ 15min = Exécution précise
✅ Double validation
✅ Réduction faux signaux
```

### **✅ SIMPLICITÉ MAINTENUE**
```
✅ 2 timeframes seulement
✅ Logique claire
✅ Paramètres réduits
✅ Tests facilités
```

---

## **⚠️ RISQUES IDENTIFIÉS ET MITIGATION**

### **📊 RISQUES PRINCIPAUX**
```
⚠️ Conflits 15min/1hour
⚠️ Latence légèrement augmentée
⚠️ Maintenance double
⚠️ Paramètres à optimiser
```

### **🛡️ MITIGATION**
```
✅ Timeframes complémentaires (pas de conflit)
✅ Performance acceptable (~3-5ms)
✅ Tests rigoureux avant déploiement
✅ Optimisation progressive
```

---

## **🚀 PLAN D'IMPLÉMENTATION**

### **📋 PHASE 1 : CONFIGURATION**
```
✅ Créer configuration 15min + 1hour
✅ Ajuster poids timeframes
✅ Configurer seuils
✅ Tests unitaires
```

### **⚖️ PHASE 2 : OPTIMISATION**
```
✅ Ajuster poids 15min/1hour
✅ Optimiser seuils confluence
✅ Fine-tuner paramètres
✅ Test paper trading
```

### **📊 PHASE 3 : VALIDATION**
```
✅ Analyse performance
✅ Comparaison historique
✅ Validation robustesse
✅ Déploiement production
```

---

## **📁 ORGANISATION FICHIERS**

### **🗂️ DOSSIER TESTS**
```
tests_15min_1hour/
├── config/
│   ├── timeframe_config.json
│   └── weights_config.json
├── scripts/
│   ├── test_15min_1hour_setup.py
│   ├── test_confluence_logic.py
│   └── test_performance.py
├── data/
│   └── test_results/
└── docs/
    └── test_documentation.md
```

### **📋 FICHIERS À CRÉER**
```
✅ Configuration timeframes
✅ Scripts de test
✅ Documentation
✅ Résultats tests
```

---

## **💡 RÈGLES IMPORTANTES**

### **🔒 PRINCIPES**
```
✅ Garder racine projet propre
✅ Tests dans dossier dédié
✅ Documentation complète
✅ Validation rigoureuse
```

### **📊 MÉTRIQUES DE SUIVI**
```
✅ Win rate par timeframe
✅ Confluence scores
✅ Latence calculs
✅ Faux signaux
```

---

## **📅 CALENDRIER**

### **⏳ PHASE ACTUELLE**
```
✅ Décision stratégique (FAIT)
✅ Document mémoire (FAIT)
✅ Organisation fichiers (EN COURS)
```

### **🚀 PROCHAINES ÉTAPES**
```
📋 Configuration technique
⚖️ Tests unitaires
📊 Optimisation paramètres
🎯 Validation paper trading
```

---

## **📞 CONTACTS ET RESSOURCES**

### **📋 DOCUMENTATION**
```
✅ Ce document : Stratégie mémoire
✅ Tests : tests_15min_1hour/
✅ Config : config/timeframe_config.json
✅ Scripts : scripts/test_*.py
```

### **🎯 OBJECTIFS**
```
✅ Implémenter 15min + 1hour
✅ Valider performance
✅ Optimiser paramètres
✅ Déployer production
```

---

**📝 NOTE : Ce document doit être mis à jour à chaque étape importante**

**Dernière mise à jour : $(date)**
**Version : 1.0**
**Statut : APPROUVÉ** 