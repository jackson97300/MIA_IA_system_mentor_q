# 🔍 CHECKLIST SANITY POLYGON - Go/No-Go

## 📋 **Validation automatique snapshot options**

Cette checklist est intégrée dans `create_polygon_snapshot.py` via la fonction `run_sanity_checks()`.

---

## ✅ **CRITÈRES GO/NO-GO**

### **🎯 Score système (Base: 100 points)**
- **GO** : Score ≥ 80 → CSV overlay généré
- **CAUTION** : Score 60-79 → CSV généré avec warnings
- **NO_GO** : Score < 60 → Pas de CSV, recommandations affichées

---

## 📊 **CHECKS AUTOMATIQUES**

### **1. Niveaux de base présents (-20 à -25 pts)**
- ❌ `MISSING_CALL_WALL` : Call Wall introuvable → **-20 pts**
- ❌ `MISSING_PUT_WALL` : Put Wall introuvable → **-20 pts**  
- ❌ `MISSING_GAMMA_FLIP` : Gamma Flip introuvable → **-25 pts**

### **2. Cohérence Flip vs GEX (-5 pts)**
- ⚠️ `FLIP_GEX_UNUSUAL` : Flip au-dessus spot + GEX positif → **-5 pts**
  - *Normal : GEX+ → flip sous spot (pinning effect)*

### **3. Walls identiques (-15 pts)**
- ❌ `WALLS_IDENTICAL` : Call Wall == Put Wall → **-15 pts**
  - *Auto-correction normalement active (second best put)*

### **4. Normalisation GEX (-5 pts)**
- ⚠️ `GEX_NORM_HIGH` : |GEX normalized| > 50 → **-5 pts**
  - *Valeurs anormalement élevées vs échelle symbole*

### **5. Pins cohérents (-5 pts)**
- ⚠️ `TOO_MANY_PINS` : Plus de 2 pins → **-5 pts**
  - *Déduplication insuffisante*

### **6. Vol Trigger position (-3 pts)**
- ⚠️ `VOL_TRIGGER_FAR` : Vol Trigger > 10% du spot → **-3 pts**
  - *Trigger trop éloigné, peu pertinent*

### **7. Validation errors (-2 pts/erreur)**
- ⚠️ `VALIDATION_*` : Erreurs meta_overlay → **-2 pts chacune**

---

## 🛠️ **RECOMMANDATIONS AUTOMATIQUES**

### **Call Wall manquant**
```
"Vérifier données OI calls"
→ Plan Polygon avec OI réel vs estimé
```

### **Gamma Flip manquant**
```
"Recalculer gamma exposure par strike"  
→ Vérifier Greeks et OI non nuls
```

### **Walls identiques**
```
"Forcer second best put wall"
→ Logique déjà implémentée, vérifier données
```

---

## 📈 **WORKFLOW INTÉGRÉ**

### **Snapshot créé** ✅
1. Calculs options complets
2. **Sanity checks lancés automatiquement**
3. Score et status déterminés

### **Status GO/CAUTION** ✅  
1. CSV overlay généré
2. Niveaux dédupliqués affichés
3. Sauvegarde fichier

### **Status NO_GO** ❌
1. **Pas de CSV overlay**
2. Erreurs et recommandations affichées
3. Snapshot JSON sauvé pour debug

---

## 🔧 **PERSONNALISATION**

### **Seuils modifiables** (dans code)
```python
# Scores penalties  
MISSING_WALL_PENALTY = 20
MISSING_FLIP_PENALTY = 25
IDENTICAL_WALLS_PENALTY = 15

# Seuils status
GO_THRESHOLD = 80
CAUTION_THRESHOLD = 60
```

### **Checks additionnels**
- Ajouter dans `run_sanity_checks()`
- Pattern : `checks['errors'].append("NEW_CHECK")`
- Décrémenter score : `checks['score'] -= penalty`

---

## 📊 **SLOT 0 VOL TRIGGER (OPTIONNEL)**

### **⚠️ Important : Vol Trigger par défaut NON TRACÉ**
```csv
gex0_vol_trigger,gex1_flip,gex2_call_wall,gex3_put_wall,gex4_max_pain,gex5_pin1,gex6_pin2
6500.00,6475.00,6550.00,6450.00,6525.00,6510.00,
```

### **Configuration Sierra Chart :**
- **Slot 0** : Vol Trigger (désactivé par défaut)
- **Slots 1-6** : Niveaux principaux (tracés automatiquement)

### **Activation manuelle Vol Trigger :**
1. Sierra Chart → Studies → Spreadsheet Study
2. Subgraph 0 (SG0) → **Enable** + Line Style
3. Couleur recommandée : **Jaune pointillé** (niveau de transition)

---

## 📱 **UTILISATION**

### **Lancement manuel**
```python
from create_polygon_snapshot import run_sanity_checks

sanity = run_sanity_checks(snapshot)
print(f"Status: {sanity['status']} ({sanity['score']}/100)")
```

### **Intégration automatique**
```python
# Déjà intégré dans create_polygon_snapshot()
snapshot = await create_polygon_snapshot("SPX")
# → Sanity checks lancés automatiquement
```

---

## 🎯 **EXEMPLES RÉSULTATS**

### **✅ GO (Score: 95)**
```json
{
  "status": "GO",
  "errors": [],
  "warnings": ["FLIP_GEX_UNUSUAL"],
  "score": 95,
  "recommendations": []
}
```

### **⚠️ CAUTION (Score: 75)**
```json
{
  "status": "CAUTION", 
  "errors": ["MISSING_CALL_WALL"],
  "warnings": ["GEX_NORM_HIGH", "VOL_TRIGGER_FAR"],
  "score": 75,
  "recommendations": ["Vérifier données OI calls"]
}
```

### **❌ NO_GO (Score: 40)**
```json
{
  "status": "NO_GO",
  "errors": ["MISSING_CALL_WALL", "MISSING_GAMMA_FLIP", "WALLS_IDENTICAL"],
  "warnings": ["TOO_MANY_PINS"],
  "score": 40,
  "recommendations": [
    "Vérifier données OI calls",
    "Recalculer gamma exposure par strike", 
    "Forcer second best put wall"
  ]
}
```

---

## 🚀 **AVANTAGES**

- **✅ Validation automatique** : Pas d'intervention manuelle
- **✅ Scoring objectif** : Critères quantifiés et reproductibles  
- **✅ Traçabilité** : Erreurs/warnings documentés dans snapshot
- **✅ Sécurité** : Pas de CSV overlay si données douteuses
- **✅ Debug facilité** : Recommandations ciblées par erreur

**→ Garantit la qualité des niveaux envoyés à Sierra Chart !**
