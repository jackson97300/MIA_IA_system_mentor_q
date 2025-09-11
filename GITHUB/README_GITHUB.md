# 📚 DOCUMENTATION GITHUB - MIA IA SYSTEM

## 🚀 **REPOSITORY GITHUB**

**URL du dépôt :** [https://github.com/jackson97300/MIA_IA_system_mentor_q](https://github.com/jackson97300/MIA_IA_system_mentor_q)

**Statut :** ✅ **ACTIF ET À JOUR**

**Dernière mise à jour :** 11 septembre 2025

---

## 📋 **CONTENU DU REPOSITORY**

### **Système MIA IA Complet**
- ✅ **16 stratégies** de trading avancées
- ✅ **Architecture multi-chart Sierra Chart** avec 4 dumpers C++ autonomes
- ✅ **Architecture robuste** avec gestion d'erreurs
- ✅ **Performance optimisée** (+20-28% win rate projeté)
- ✅ **Sécurité maximale** (données sensibles exclues)

### **Stratégies Intégrées**
1. **10 stratégies originales** (gamma_pin_reversion, dealer_flip_breakout, etc.)
2. **6 stratégies MenthorQ** (zero_dte_wall_sweep_reversal, gamma_wall_break_and_go, etc.)

### **Fonctionnalités**
- ✅ **Dédoublonnage par famille** (REVERSAL, BREAKOUT, MEAN_REVERT, etc.)
- ✅ **Scoring contextuel** optimisé
- ✅ **Cooldown intelligent** par stratégie
- ✅ **Limite quotidienne** (12 signaux max)

### **Architecture Multi-Chart Sierra Chart**
- ✅ **4 Dumpers C++ Autonomes** compilés avec succès
- ✅ **Chart 3 (1 min)** : BaseData, VWAP, VVA, PVWAP, NBCV, DOM, T&S, Cumulative Delta + Bearish/Bullish
- ✅ **Chart 4 (30 min)** : OHLC, VWAP, PVWAP, NBCV, Cumulative Delta, Correlation, ATR, Volume Profile, VVA Previous
- ✅ **Chart 8 (VIX)** : VIX OHLC direct du chart
- ✅ **Chart 10 (MenthorQ)** : MenthorQ levels (Gamma, Blind Spots, Swing Levels)
- ✅ **Headers Intégrés** (Approach 1) - plus de dépendances externes
- ✅ **Mappings Validés** - Study IDs et Subgraphs corrigés
- ✅ **Unifier Mis à Jour** - Support de tous les nouveaux types de données

---

## 🔧 **WORKFLOWS GITHUB ACTIONS**

### **CI Pipeline** (`.github/workflows/ci.yml`)
- ✅ Tests MenthorQ integration
- ✅ Tests Sierra collector
- ✅ Vérification composants legacy
- ✅ Upload des logs d'erreur

### **Atlas Generator** (`.github/workflows/atlas.yml`)
- ✅ Analyse des imports
- ✅ Détection composants legacy/Sierra/MenthorQ
- ✅ Génération hebdomadaire automatique
- ✅ Rapport sur les Pull Requests

---

## 🔒 **SÉCURITÉ**

### **Données Exclues** (`.gitignore`)
- ❌ Fichiers JSONL (données marché)
- ❌ Logs système
- ❌ Backups et fichiers temporaires
- ❌ Dossiers de tests (`tests/`, `test_*`)
- ❌ Outils temporaires (`tools/` - scripts de test)
- ❌ Modèles entraînés volumineux
- ❌ Fichiers sensibles (clés, mots de passe)

### **Repository Privé**
- 🔒 **Accès restreint** (données sensibles)
- 🔒 **Mode lecture seule** (pas de trading automatique)
- 🔒 **Sierra-only** (plus de dépendances externes)

---

## 📊 **STATISTIQUES**

- **Commits :** 7
- **Branches :** main
- **Languages :** Python (63.5%), HTML (33.7%), C++ (2.8%)
- **Stars :** 0
- **Forks :** 0

---

## 🚀 **COMMANDES GITHUB**

### **Cloner le repository**
```bash
git clone https://github.com/jackson97300/MIA_IA_system_mentor_q.git
```

### **Mettre à jour**
```bash
git pull origin main
```

### **Pousser des modifications**
```bash
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
```

### **Créer une Pull Request**
```bash
git checkout -b feature/nouvelle-fonctionnalite
git push origin feature/nouvelle-fonctionnalite
# Puis créer PR sur GitHub
```

---

## 📁 **STRUCTURE DU REPOSITORY**

```
MIA_IA_system_mentor_q/
├── .github/workflows/          # CI/CD automatisé
├── core/                       # Modules principaux
├── features/                   # Fonctionnalités avancées
├── strategies/                 # 16 stratégies de trading
├── config/                     # Configurations
├── extracteur/                 # 4 dumpers C++ Sierra Chart
│   ├── MIA_Dumper_G3_Core.cpp      # Chart 3 (1 min)
│   ├── MIA_Dumper_G4_Studies.cpp   # Chart 4 (30 min)
│   ├── MIA_Dumper_G8_VIX.cpp       # Chart 8 (VIX)
│   ├── MIA_Dumper_G10_MenthorQ.cpp # Chart 10 (MenthorQ)
│   └── MAPPING_MIA_CLEF.md         # Mappings Study IDs/Subgraphs
├── docs/                       # Documentation
├── GITHUB/                     # Documentation GitHub
├── .gitignore                  # Exclusion données sensibles
├── README.md                   # Documentation principale
└── ARCHITECTURE.md             # Architecture détaillée
```

---

## 🎯 **PROCHAINES ÉTAPES**

1. **✅ Architecture Multi-Chart** : 4 dumpers C++ compilés et opérationnels
2. **Monitoring** : Surveiller les workflows GitHub Actions
3. **Tests** : Valider les performances en production
4. **Optimisation** : Ajuster les paramètres selon les résultats
5. **Documentation** : Mettre à jour selon les retours

---

## 📞 **SUPPORT**

- **Repository :** [https://github.com/jackson97300/MIA_IA_system_mentor_q](https://github.com/jackson97300/MIA_IA_system_mentor_q)
- **Issues :** Utiliser le système d'issues GitHub
- **Documentation :** Voir `docs/` et `ARCHITECTURE.md`

---

*Documentation GitHub - MIA IA System v1.1 - 11/09/2025*

