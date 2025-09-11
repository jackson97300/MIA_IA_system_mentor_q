# 📋 DOCUMENTATION : SUBGRAPHS SIERRA CHART - MAPPING ET INDEXATION

## 🎯 **OBJECTIF**
Ce document explique la confusion entre l'affichage des subgraphs dans l'interface Sierra Chart et leur indexation en programmation ACSIL, ainsi que la solution pour éviter les erreurs de mapping.

---

## 🚨 **PROBLÈME IDENTIFIÉ**

### **Confusion Interface vs Programmation**
- **Interface utilisateur** : Affiche SG1, SG2, SG3... (commence à 1)
- **Programmation ACSIL** : Utilise 0, 1, 2... (commence à 0)
- **Résultat** : Mauvais mapping des subgraphs = données incorrectes

### **Exemple Concret**
```cpp
// ❌ ERREUR : Utilisation des mauvais IDs
VVA Current Study ID: 9    // Mauvais ID
VVA Previous Study ID: 8   // Mauvais ID

// ✅ CORRECT : Utilisation des bons IDs
VVA Current Study ID: 1    // Volume Value Area Lines
VVA Previous Study ID: 2   // Volume Value Area Previous
```

---

## 📊 **MAPPING CORRECT DES SUBGRAPHS**

### **Volume Value Area Lines (ID 1) - Current**
| Interface | Programmation | Nom | Description |
|-----------|---------------|-----|-------------|
| SG1 | Index 0 | "Vol POC" | Volume Point of Control |
| SG2 | Index 1 | "Vol Value Area High" | Volume Value Area High (VAH) |
| SG3 | Index 2 | "Vol Value Area Low" | Volume Value Area Low (VAL) |

### **Volume Value Area Previous (ID 2) - Previous**
| Interface | Programmation | Nom | Description |
|-----------|---------------|-----|-------------|
| SG1 | Index 0 | "PPOC" | Previous Point of Control |
| SG2 | Index 1 | "PVAH" | Previous Value Area High |
| SG3 | Index 2 | "PVAL" | Previous Value Area Low |

### **VWAP (ID 22) - Standard**
| Interface | Programmation | Nom | Description |
|-----------|---------------|-----|-------------|
| SG1 | Index 0 | "V" | VWAP Principal |
| SG2 | Index 1 | "+1" | Bande +1 |
| SG3 | Index 2 | "-1" | Bande -1 |
| SG4 | Index 3 | "+2" | Bande +2 |
| SG5 | Index 4 | "-2" | Bande -2 |
| SG6 | Index 5 | "+3" | Bande +3 |
| SG7 | Index 6 | "-3" | Bande -3 |

### **Numbers Bars Calculated Values (ID 33) - NBCV**
| Interface | Programmation | Nom | Description |
|-----------|---------------|-----|-------------|
| SG1 | Index 0 | "Ask Volume Bid Volume Difference" | Delta |
| SG2 | Index 1 | "Ask Volume Bid Volume Total" | Total |
| SG3 | Index 2 | "Ask Volume Bid Volume Difference Change" | Change |
| SG4 | Index 3 | "Positive Delta Sum" | Positive Delta |
| SG5 | Index 4 | "Negative Delta Sum" | Negative Delta |
| SG6 | Index 5 | "Ask Volume Total" | Ask Volume |
| SG7 | Index 6 | "Bid Volume Total" | Bid Volume |
| SG8 | Index 7 | "Maximum Ask Volume Bid Volume Difference" | Max Delta |
| SG9 | Index 8 | "Minimum Ask Volume Bid Volume Difference" | Min Delta |
| SG10 | Index 9 | "Cumulative Sum Of Ask Volume Bid Volume Difference - Day" | Cumulative Delta |
| SG11 | Index 10 | "Ask Volume Bid Volume Difference Percent" | Delta % |
| SG12 | Index 11 | "Number of Trades" | Number of Trades |
| SG13 | Index 12 | "Total Volume" | Total Volume |

---

## 🔧 **CONFIGURATION CORRIGÉE**

### **MIA_Dumper_G3_Core.cpp - Configuration Finale**
```cpp
// === CONFIGURATION CORRECTE ===
VWAP Study ID: 22                    // VWAP standard
VVA Current Study ID: 1              // Volume Value Area Lines
VVA Previous Study ID: 2             // Volume Value Area Previous
NBCV Study ID: 33                    // Numbers Bars Calculated Values
VIX Study ID: 23                     // VIX_CGI[M] 1 Min #8
Cumulative Delta Study ID: 32        // Cumulative Delta Bars - Volume

// === MAPPING DES SUBGRAPHS EN PROGRAMMATION ===
// VVA Current (ID 1):
//   Index 0 = Vol POC (Point of Control)
//   Index 1 = Vol Value Area High (VAH)
//   Index 2 = Vol Value Area Low (VAL)

// VVA Previous (ID 2):
//   Index 0 = PPOC (Previous Point of Control)
//   Index 1 = PVAH (Previous Value Area High)
//   Index 2 = PVAL (Previous Value Area Low)

// VWAP (ID 22):
//   Index 0 = V (VWAP principal)
//   Index 1 = +1 (Bande +1)
//   Index 2 = -1 (Bande -1)
//   Index 3 = +2 (Bande +2)
//   Index 4 = -2 (Bande -2)
//   Index 5 = +3 (Bande +3)
//   Index 6 = -3 (Bande -3)

// NBCV (ID 33):
//   Index 0 = Ask Volume Bid Volume Difference (Delta)
//   Index 1 = Ask Volume Bid Volume Total
//   Index 2 = Ask Volume Bid Volume Difference Change
//   Index 3 = Positive Delta Sum
//   Index 4 = Negative Delta Sum
//   Index 5 = Ask Volume Total
//   Index 6 = Bid Volume Total
//   Index 7 = Maximum Ask Volume Bid Volume Difference
//   Index 8 = Minimum Ask Volume Bid Volume Difference
//   Index 9 = Cumulative Sum Of Ask Volume Bid Volume Difference - Day
//   Index 10 = Ask Volume Bid Volume Difference Percent
//   Index 11 = Number of Trades
//   Index 12 = Total Volume
```

---

## 🛠️ **PROCÉDURE DE VÉRIFICATION**

### **1. Générer l'Inventaire des Études**
```bash
# Utiliser MIA_Study_Inspector.cpp
# Placer l'étude sur le chart à analyser
# Configurer : Chart to Inspect = 0 (current)
# Exécuter et vérifier le fichier de sortie
```

### **2. Analyser l'Inventaire**
```bash
# Utiliser analyze_study_inventory.py
python analyze_study_inventory.py study_inventory_chart_3_YYYYMMDD.jsonl
```

### **3. Vérifier les Subgraphs**
- **Interface** : Aller dans Study Settings → Subgraphs
- **Programmation** : Utiliser l'indexation 0-based dans le code
- **Mapping** : Créer un tableau de correspondance

### **4. Tester la Configuration**
- Compiler le dumper avec les bons IDs
- Placer l'étude sur le chart
- Vérifier que les données collectées sont correctes
- Comparer avec les valeurs affichées dans Sierra Chart

---

## 📝 **CHECKLIST DE VALIDATION**

### **Avant Déploiement**
- [ ] Inventaire des études généré
- [ ] IDs des études vérifiés
- [ ] Mapping des subgraphs validé
- [ ] Configuration mise à jour dans le code
- [ ] Tests de collecte effectués
- [ ] Données comparées avec l'interface

### **Après Déploiement**
- [ ] Fichiers de sortie créés
- [ ] Données cohérentes avec l'interface
- [ ] Aucune erreur dans les logs
- [ ] Performance acceptable
- [ ] Documentation mise à jour

---

## 🚨 **ERREURS COMMUNES À ÉVITER**

### **1. Confusion Interface vs Programmation**
```cpp
// ❌ ERREUR : Utiliser l'indexation de l'interface
ReadSubgraph(sc, studyID, 1, array);  // SG1 dans l'interface

// ✅ CORRECT : Utiliser l'indexation de programmation
ReadSubgraph(sc, studyID, 0, array);  // Index 0 en programmation
```

### **2. Mauvais IDs d'Études**
```cpp
// ❌ ERREUR : IDs incorrects
VVA Current Study ID: 9    // Mauvais ID
VVA Previous Study ID: 8   // Mauvais ID

// ✅ CORRECT : IDs corrects
VVA Current Study ID: 1    // Volume Value Area Lines
VVA Previous Study ID: 2   // Volume Value Area Previous
```

### **3. Mapping des Subgraphs Incorrect**
```cpp
// ❌ ERREUR : Mapping incorrect
#define VVA_SG_POC 1   // Mauvais index
#define VVA_SG_VAH 2   // Mauvais index
#define VVA_SG_VAL 3   // Mauvais index

// ✅ CORRECT : Mapping correct
#define VVA_SG_POC 0   // Index 0 = Vol POC
#define VVA_SG_VAH 1   // Index 1 = Vol Value Area High
#define VVA_SG_VAL 2   // Index 2 = Vol Value Area Low
```

---

## 📚 **RESSOURCES UTILES**

### **Outils de Diagnostic**
- **MIA_Study_Inspector.cpp** : Génère l'inventaire des études
- **analyze_study_inventory.py** : Analyse l'inventaire
- **Sierra Chart Study Settings** : Vérification manuelle

### **Documentation**
- **Sierra Chart ACSIL Documentation** : API de programmation
- **Study Settings Interface** : Configuration des études
- **Subgraph Mapping** : Correspondance interface/programmation

### **Fichiers de Référence**
- **study_inventory_chart_3_YYYYMMDD.jsonl** : Inventaire des études
- **MAPPING_ETUDES_SIERRA.md** : Mapping complet des études
- **studies_mapping.json** : Données structurées

---

## 🎯 **RÉSUMÉ**

### **Points Clés**
1. **Interface** : SG1, SG2, SG3... (commence à 1)
2. **Programmation** : 0, 1, 2... (commence à 0)
3. **IDs Corrects** : Vérifier avec l'inventaire des études
4. **Mapping** : Créer un tableau de correspondance
5. **Tests** : Valider avec des données réelles

### **Actions Requises**
1. **Générer** l'inventaire des études
2. **Vérifier** les IDs et subgraphs
3. **Corriger** la configuration
4. **Tester** la collecte
5. **Documenter** les changements

**Cette documentation doit être mise à jour à chaque modification des études ou des IDs !**

---

*Document créé le : 2025-01-11*
*Dernière mise à jour : 2025-01-11*
*Version : 1.0*
