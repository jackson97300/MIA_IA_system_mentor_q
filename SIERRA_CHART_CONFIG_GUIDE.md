# 🎯 Guide de Configuration Sierra Chart - Résolution des Anomalies

## 🚨 **Problèmes Identifiés et Solutions**

### 1. **Quotes ×100 (Scale Issues) - 636 cas**

#### **Configuration Symbol Settings (Global)**
1. **Global Settings → Symbol Settings → [ESU25/MESU25]**
   - `Price Display Format`: **0.25** (pour ES/MES)
   - `Tick Size`: **0.25**
   - `Currency Value per Tick`: **12.5** (ES) / **1.25** (MES)
   - `Real-Time Price Multiplier`: **1.0** ⚠️ **CRITIQUE**
   - Cliquer **Update from Server** → **Apply** → **OK**

#### **Configuration Chart Settings (Local)**
2. **Chart Settings (F5) → Advanced Settings 2**
   - `Real-Time Price Multiplier`: **1.0** ⚠️ **CRITIQUE**
   - `Price Display Format`: **0.25**
   - `Lock Fill Space`: **décoché**
   - **Apply** (force refresh)

3. **Redémarrage du Chart**
   - `Chart → Recalculate` (Ctrl+Insert)
   - Ou fermer/rouvrir le chart

### 2. **VVA (VAL/VAH inversées + VPOC hors limites) - 654 cas**

#### **Configuration Volume by Price**
1. **Étude**: `Volume by Price` (pas "Volume Value Area Lines" seule)
2. **Paramètres**:
   - `Number of Profiles`: **1 Day** (recommandé)
   - `Value Area %`: **70**
   - `Use Separate Profiles for Day Session Only`: **désactivé** (pour Globex)
   - `Based on`: **Use Chart Data**
   - `TPO/Letter/Block`: **désactivé** (si volume uniquement)

#### **Vérification Subgraphs**
3. **Subgraphs Order** (dans l'étude):
   - **SG0**: VAH (Value Area High)
   - **SG1**: VAL (Value Area Low)  
   - **SG2**: VPOC (Volume Point of Control)

4. **Mapping dans le Dumper**:
   ```cpp
   // Vérifier que l'ordre correspond
   vah = gd[0][vi];  // SG0
   val = gd[1][vi];  // SG1  
   vpoc = gd[2][vi]; // SG2
   ```

### 3. **VIX Mode Invalid - 327 cas**

#### **Acceptation des Modes Numériques**
- **Mode 0**: Normal
- **Mode 1**: Contango  
- **Mode 2**: Backwardation

**Solution**: Le script d'analyse accepte maintenant `0, 1, 2` en plus des chaînes.

### 4. **Lignes Non-JSON (Processing) - 12,426 cas**

#### **Filtrage Côté Analyseur**
- ✅ **Corrigé**: Le script filtre maintenant les lignes non-JSON
- **Critères**: Ligne doit commencer par `{` et finir par `}`

#### **Nettoyage Côté Dumper**
- **Écrire uniquement** des lignes JSON complètes
- **Pas de logs** intercalés
- **Pas de lignes vides**

## 🔧 **Vérifications Post-Configuration**

### **Check-list de Validation**
- [ ] Symbol Settings → Real-Time Price Multiplier = 1.0
- [ ] Chart Settings → Real-Time Price Multiplier = 1.0  
- [ ] Volume by Price → Profil quotidien configuré
- [ ] Subgraphs VAH/VAL/VPOC dans le bon ordre
- [ ] Chart recalculé (Ctrl+Insert)

### **Test de Validation**
1. **Lancer la collecte** 2-3 minutes
2. **Relancer** `analyze_chart_data.py`
3. **Vérifier** que `scale_issue` ≈ 0
4. **Vérifier** que `processing` ≈ 0

## 📊 **Résultats Attendus**

| Anomalie | Avant | Après | Statut |
|----------|-------|-------|---------|
| `scale_issue` | 636 | ~0 | ✅ Résolu |
| `processing` | 12,426 | ~0 | ✅ Résolu |
| `val_vah_inverted` | 327 | ~0 | ✅ Résolu |
| `vpoc_out_of_range` | 327 | ~0 | ✅ Résolu |
| `mode_invalid` | 327 | ~0 | ✅ Résolu |

## 🚀 **Prochaines Étapes**

1. **Appliquer les configurations** Sierra Chart
2. **Relancer la compilation** du dumper corrigé
3. **Tester la collecte** avec les nouveaux paramètres
4. **Analyser les résultats** avec le script amélioré
5. **Valider** que toutes les anomalies sont résolues

---

**Note**: Si des anomalies persistent après ces corrections, vérifier les **charts secondaires** et **études overlay** qui pourraient avoir des paramètres différents.







