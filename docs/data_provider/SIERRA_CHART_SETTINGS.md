# 🎨 MATRICE SIERRA CHART - SETTINGS PRÊTS À COLLER

## ⚠️ **AVERTISSEMENT IMPORTANT - ÉVITER MALENTENDUS**

### **🎯 NOMBRE DE TRAITS ATTENDUS :**
- **4-6 traits maximum** visibles par défaut 
- **Vol Trigger (Slot 0) NON tracé** automatiquement
- **gex1-gex6 seulement** sont mappés aux subgraphs actifs

### **❌ ERREUR FRÉQUENTE :**
**NE PAS s'attendre à voir 7 traits !** Le CSV contient 7 colonnes (gex0-gex6) mais seules 6 sont tracées automatiquement.

---

## 📊 **Configuration Spreadsheet Study - Polygon Overlay**

### **🎯 SLOTS DE DONNÉES (Mapping CSV)**

#### **⚠️ IMPORTANT : Seuls gex1-gex6 sont tracés automatiquement**
```
✅ TRACÉS AUTOMATIQUEMENT :
Slot 1: gex1_flip          → SG1 🔄 Gamma Flip
Slot 2: gex2_call_wall     → SG2 🔴 Call Wall  
Slot 3: gex3_put_wall      → SG3 🟢 Put Wall
Slot 4: gex4_max_pain      → SG4 🔵 Max Pain
Slot 5: gex5_pin1          → SG5 ⚪ Gamma Pin #1
Slot 6: gex6_pin2          → SG6 ⚪ Gamma Pin #2

❌ NON TRACÉ PAR DÉFAUT :
Slot 0: gex0_vol_trigger   → SG0 (activation manuelle requise)
```

#### **📊 Résultat visuel attendu : 4-6 traits (jamais 7)**
- **Minimum** : 4 traits (Flip + Call Wall + Put Wall + Max Pain)
- **Maximum** : 6 traits (+ 2 Pins si détectés et espacés)
- **Vol Trigger** : Disponible mais PAS affiché automatiquement

---

## 🎨 **SUBGRAPH SETTINGS (Copier-Coller)**

### **SG0 - Vol Trigger (⚠️ OPTIONNEL - NON TRACÉ PAR DÉFAUT)**
```
Name: Vol Trigger
Draw Style: Line at Last Bar to Edge
Line Width: 2
Line Style: Dash
Color: RGB(255, 255, 0) - Jaune
Display: FALSE (désactivé par défaut)

⚠️ ATTENTION : Ce niveau N'EST PAS tracé automatiquement !
Activation manuelle requise si souhaité.
```

### **SG1 - Gamma Flip** 🔄
```
Name: Gamma Flip
Draw Style: Line at Last Bar to Edge  
Line Width: 3
Line Style: Solid
Color: RGB(255, 165, 0) - Orange
Display: Always On
```

### **SG2 - Call Wall** 🔴
```
Name: Call Wall
Draw Style: Line at Last Bar to Edge
Line Width: 3
Line Style: Solid  
Color: RGB(220, 20, 60) - Crimson
Display: Always On
```

### **SG3 - Put Wall** 🟢
```
Name: Put Wall
Draw Style: Line at Last Bar to Edge
Line Width: 3
Line Style: Solid
Color: RGB(34, 139, 34) - Forest Green
Display: Always On
```

### **SG4 - Max Pain** 🔵
```
Name: Max Pain
Draw Style: Line at Last Bar to Edge
Line Width: 2
Line Style: Dot
Color: RGB(30, 144, 255) - Dodger Blue
Display: Always On
```

### **SG5 - Gamma Pin #1** ⚪
```
Name: Pin 1
Draw Style: Line at Last Bar to Edge
Line Width: 2
Line Style: Dash
Color: RGB(169, 169, 169) - Dark Gray
Display: When Data Available
```

### **SG6 - Gamma Pin #2** ⚪
```
Name: Pin 2  
Draw Style: Line at Last Bar to Edge
Line Width: 2
Line Style: Dash
Color: RGB(105, 105, 105) - Dim Gray
Display: When Data Available
```

---

## 🌈 **FOND GAMMA REGIME (Study Séparée)**

### **Color Background Based on Study Value**
```
Study: Color Background Based on Study Value
Input: gex_regime column (POS/NEG)

Condition 1:
  Formula: POS
  Color: RGB(144, 238, 144) - Light Green  
  Opacity: 15%
  
Condition 2:
  Formula: NEG
  Color: RGB(255, 182, 193) - Light Pink
  Opacity: 15%
```

---

## 📋 **CONFIGURATION RAPIDE (Step-by-Step)**

### **Étape 1 : Importer le CSV**
1. File → New Spreadsheet (nommer "Polygon_Levels")
2. File → Import Text/CSV → Sélectionner votre overlay CSV
3. Vérifier headers/data correctement parsés

### **Étape 2 : Chart Principal ES**
1. Analysis → Studies → Add: Spreadsheet Study - Simple
2. Input: Link to "Polygon_Levels" spreadsheet
3. Configurer les 7 Subgraphs selon matrice ci-dessus

### **Étape 3 : Fond Gamma** 
1. Analysis → Studies → Add: Color Background Based on Study Value
2. Input: Référencer colonne `gex_regime` 
3. Conditions POS/NEG avec couleurs/opacité

### **Étape 4 : Sauvegarde Template**
1. File → Save Chart Settings As → "Polygon_Options_Overlay"
2. Apply to → All Charts (optionnel)

---

## 🎛️ **PARAMÈTRES AVANCÉS**

### **⚠️ GESTION VOL TRIGGER (SLOT 0) - IMPORTANT**

#### **État par défaut : NON TRACÉ**
```
SG0 Display = FALSE (désactivé)
Résultat : 4-6 traits visibles (gex1-gex6 seulement)
```

#### **Activation manuelle (optionnelle) :**
```
1. Studies → Spreadsheet Study → Subgraphs
2. SG0 → Enable Display ✅
3. Apply → Couleur Jaune pointillé
4. Résultat : 5-7 traits visibles (gex0-gex6)
```

#### **⚠️ Éviter malentendus :**
- **NE PAS s'attendre** à voir 7 traits par défaut
- **Vol Trigger disponible** mais nécessite activation manuelle
- **Configuration standard** = 4-6 traits (ce qui est optimal)

### **Transparence Lines**
```
Toutes lignes: Transparency = 0% (opaque)
Exception: Pins = 20% (plus discret)
```

### **Extension Lines**
```
Tous: Extended Lines Until End of Chart = True
Pour tracer au-delà de la dernière barre
```

### **Labels Display**
```
Show Study Name in Chart: True
Show Values in Chart: False (évite surcharge)
Position: Top Left
```

---

## 🔧 **TEMPLATE SETTINGS (Export/Import)**

### **Fichier de configuration ready-to-use :**
```json
{
  "study_name": "Polygon_Options_Overlay",
  "subgraphs": {
    "SG0": {"name": "Vol Trigger", "color": "#FFFF00", "enabled": false},
    "SG1": {"name": "Gamma Flip", "color": "#FFA500", "enabled": true},
    "SG2": {"name": "Call Wall", "color": "#DC143C", "enabled": true},
    "SG3": {"name": "Put Wall", "color": "#228B22", "enabled": true},  
    "SG4": {"name": "Max Pain", "color": "#1E90FF", "enabled": true},
    "SG5": {"name": "Pin 1", "color": "#A9A9A9", "enabled": true},
    "SG6": {"name": "Pin 2", "color": "#696969", "enabled": true}
  },
  "background": {
    "pos_regime": {"color": "#90EE90", "opacity": 15},
    "neg_regime": {"color": "#FFB6C1", "opacity": 15}
  }
}
```

---

## 🎯 **RÉSULTAT VISUEL ATTENDU**

### **Chart avec overlay actif (4-6 traits) :**
- **🔄 Orange** : Gamma Flip (pivot principal) - **TOUJOURS**
- **🔴 Rouge** : Call Wall (résistance) - **TOUJOURS**
- **🟢 Vert** : Put Wall (support) - **TOUJOURS**
- **🔵 Bleu pointillé** : Max Pain (aimant) - **TOUJOURS**
- **⚪ Gris** : Pin #1 (attracteur) - **SI DÉTECTÉ**
- **⚪ Gris foncé** : Pin #2 (attracteur) - **SI DÉTECTÉ**
- **🌈 Fond** : Vert pâle (GEX+) ou Rose pâle (GEX-)

### **⚠️ Vol Trigger (Slot 0) :**
- **🟡 Jaune pointillé** : Vol Trigger - **NON TRACÉ PAR DÉFAUT**
- Disponible dans CSV mais nécessite activation manuelle
- La plupart des utilisateurs n'en ont pas besoin

### **Slots vides normaux :**
- Pins vides si déduplication/qualité insuffisante
- **JAMAIS 7 traits simultanément** en configuration standard

---

## 📱 **UTILISATION QUOTIDIENNE**

### **Import nouveau CSV :**
1. Remplacer fichier CSV (même nom)
2. F5 (Refresh) dans spreadsheet "Polygon_Levels"  
3. Lines se mettent à jour automatiquement

### **Debug rapide :**
- **Pas de traits** → Vérifier données dans fenêtre ±3%
- **Traits collés** → Sanity check failed, revoir min_gap_pts
- **Fond incorrect** → Vérifier colonne gex_regime POS/NEG

**→ Configuration Sierra Chart optimisée pour overlay Polygon ! 🚀**
