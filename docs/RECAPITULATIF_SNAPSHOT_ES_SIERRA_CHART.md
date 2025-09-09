# 📊 RÉCAPITULATIF - SNAPSHOT ES ULTRA-LÉGER POUR SIERRA CHART

## 🎯 **OBJECTIF**

Créer un snapshot **ultra-minimal** pour tracer **uniquement les niveaux critiques ES** sur Sierra Chart, sans complexité inutile.

---

## 🔥 **SPÉCIFICATION MINIMALE DU SNAPSHOT (ES UNIQUEMENT)**

### **Champs obligatoires (pour tracer 4–6 lignes max)**

* `symbol` : `"ES"`
* `trade_datetime_utc` : horodatage ISO (ex. `2025-08-29T21:30:00Z`)
* `spot` : dernier prix ES (futur)
* `gex_total` : valeur signée (pour le fond Gamma +/–)
* `gex_regime` : `"POS"` ou `"NEG"` (dérivé du signe de `gex_total`)
* `gex1_flip` : **Gamma Flip** (pivot)
* `gex2_call_wall` : **Call Wall** (résistance)
* `gex3_put_wall` : **Put Wall** (support)
* `gex4_max_pain` : **Max Pain** (aimant)
* `gex5_pin1` : **Gamma Pin #1** (optionnel si pertinent)
* `gex6_pin2` : **Gamma Pin #2** (optionnel si pertinent)
* `window_pct` : fenêtre de sélection autour du spot (ex. `0.03` pour ±3 %)
* `min_gap_pts` : écart mini entre niveaux (ex. `20` points ES)
* `source` : `"DealerBias/Options"`
* `notes` : libre (ex. "pins forts uniquement")

> Tu n'as **pas besoin** de VIX, PCR, IV, etc. dans ce fichier si le but est *uniquement* d'afficher des **traits** sur ES.

---

## 📄 **FORMAT RECOMMANDÉ**

### **1) CSV (pratique pour Sierra Chart – Spreadsheet Study)**

**En-tête :**

```csv
symbol,trade_datetime_utc,spot,gex_total,gex_regime,gex1_flip,gex2_call_wall,gex3_put_wall,gex4_max_pain,gex5_pin1,gex6_pin2,window_pct,min_gap_pts,source,notes
```

**Exemple de ligne :**

```csv
ES,2025-08-29T21:30:00Z,5512.25,2.75e10,POS,5468.00,5525.00,5450.00,5538.00,5510.00,,0.03,20,DealerBias/Options,"Pins>=Strong; fond vert pâle"
```

*(si pas de pin #2, laisse vide `gex6_pin2`)*

### **2) JSON (si tu préfères)**

```json
{
  "symbol": "ES",
  "trade_datetime_utc": "2025-08-29T21:30:00Z",
  "spot": 5512.25,
  "gex_total": 2.75e10,
  "gex_regime": "POS",
  "gex1_flip": 5468.0,
  "gex2_call_wall": 5525.0,
  "gex3_put_wall": 5450.0,
  "gex4_max_pain": 5538.0,
  "gex5_pin1": 5510.0,
  "gex6_pin2": null,
  "window_pct": 0.03,
  "min_gap_pts": 20,
  "source": "DealerBias/Options",
  "notes": "Pins>=Strong; fond vert pâle"
}
```

---

## 🎯 **MÉTHODE SIERRA CHART (SANS CODE)**

### **A. Feuille "LEVELS" (importe le CSV)**

1. **File → New Spreadsheet** (crée une feuille dédiée, nomme-la "LEVELS").
2. Dans la fenêtre Spreadsheet "LEVELS" : **File → Import Text/CSV…** et sélectionne `ES_gex_levels.csv`.
3. Vérifie que les colonnes sont bien lues (tu dois voir tes champs en ligne 2).

> À chaque mise à jour de niveaux, **réécris** le CSV (même nom) puis dans "LEVELS", refais **File → Import Text/CSV…** (écrase les valeurs). C'est rapide.

### **B. Feuille du chart ES (trace les lignes depuis "LEVELS")**

1. Ouvre ton **graph ES** (le futur).

2. **Analysis → Studies… → Add: Spreadsheet Study – Simple** → **OK**.
   * Ça crée une feuille liée au chart (ex. `Sheet: ES #1`).

3. Dans `Sheet: ES #1`, on va **répliquer** les 4–6 niveaux en colonnes **K → P** (qui sont "graphiques") :

   * En **K3** (GEX1 Flip) tape une formule qui pointe vers la cellule de "LEVELS" contenant `gex1_flip` (ex. *colonne F, ligne 2*) :
     ```
     =LEVELS!F$2
     ```
     puis **copie/descends** la formule jusqu'en bas (K3→K10000) pour faire un trait horizontal.

   * En **L3** (Call Wall) :
     ```
     =LEVELS!G$2
     ```
     descends.

   * **M3** (Put Wall) : `=LEVELS!H$2` → descends.
   * **N3** (Max Pain) : `=LEVELS!I$2` → descends.
   * **O3** (Pin1) : `=LEVELS!J$2` → descends (si vide, la ligne ne s'affichera pas).
   * **P3** (Pin2) : `=LEVELS!K$2` → descends.

4. **Retourne à Studies** du chart ES : dans la **Spreadsheet Study – Simple**, règle les **Subgraphs** :

   * **SG1 (col K)** : *Draw Style = Line at Last Bar to Edge*, **Couleur orange** (Gamma Flip).
   * **SG2 (col L)** : *Line at Last Bar to Edge*, **Rouge** (Call Wall).
   * **SG3 (col M)** : *Line at Last Bar to Edge*, **Vert** (Put Wall).
   * **SG4 (col N)** : *Line at Last Bar to Edge*, **Bleu pointillé** (Max Pain).
   * **SG5 (col O)** : *Line at Last Bar to Edge*, **Gris** (Pin1).
   * **SG6 (col P)** : *Line at Last Bar to Edge*, **Gris** (Pin2).

### **C. Fond coloré Gamma + / –**

1. **Analysis → Studies… → Add: Color Background Based on Study Value**.
2. Input = **Spreadsheet Study – Simple → Subgraph "Extra"** (choisis un SG libre, ex. **SG7**).

   * Dans `Sheet: ES #1`, mets **Q3** = `=LEVELS!D$2` (où `gex_total` est en D2) et descends ; puis mappe **SG7** à la **colonne Q**.

3. Règle 2 conditions :
   * **Cond A** : `SG7 > 0` → Vert pâle (Opacity ~12–20%).
   * **Cond B** : `SG7 < 0` → Rouge pâle (Opacity ~12–20%).
   * (Optionnel) ajoute une **EMA(5)** sur Q pour lisser et branche la Study sur l'EMA.

---

## 📋 **RÈGLES D'AFFICHAGE (LISIBILITÉ)**

* **Max 6 niveaux** (Flip, Call Wall, Put Wall, Max Pain, Pin1, Pin2).
* **Évite les niveaux trop proches** en amont (dans ton CSV) avec **min_gap_pts** (ex. 20 pts ES).
* **Fenêtre** autour du prix (dans ta génération) : ±3% pour rester pertinent.

---

## 🔄 **ROUTINE D'USAGE SIMPLE**

### **Workflow quotidien :**

1. **Génère/actualise** `ES_gex_levels.csv` (valeurs propres, pas collées).
2. Dans la feuille **LEVELS** : **File → Import Text/CSV…** (écrase l'ancienne ligne).
3. Les lignes sur le chart ES se mettent à jour **instantanément** (car `Sheet: ES #1` référence `LEVELS`).
4. Ajuste, si besoin, **couleurs/épaisseurs** dans les Subgraphs.

### **Exemple de fichier `ES_gex_levels.csv` :**

```csv
symbol,trade_datetime_utc,spot,gex_total,gex_regime,gex1_flip,gex2_call_wall,gex3_put_wall,gex4_max_pain,gex5_pin1,gex6_pin2,window_pct,min_gap_pts,source,notes
ES,2025-08-29T21:30:00Z,5512.25,2.75e10,POS,5468.00,5525.00,5450.00,5538.00,5510.00,,0.03,20,DealerBias/Options,"Pins forts uniquement"
```

---

## ✅ **CHECKLIST DE CONTRÔLE**

### **Avant import dans Sierra :**

- [ ] **Valeurs présentes** : Aucun champ vide pour les 4 niveaux obligatoires
- [ ] **Pas de NaN** : Toutes les valeurs sont numériques valides
- [ ] **Écart mini respecté** : `min_gap_pts` appliqué (ex. 20 points ES minimum)
- [ ] **Fenêtre respectée** : Niveaux dans `window_pct` autour du spot (ex. ±3%)
- [ ] **Horodatage récent** : `trade_datetime_utc` pas trop ancien (< 4h)
- [ ] **Format correct** : CSV bien formé avec virgules, pas de caractères spéciaux

### **Après import dans Sierra :**

- [ ] **6 lignes visibles** : Gamma Flip, Call Wall, Put Wall, Max Pain, Pin1, Pin2
- [ ] **Couleurs correctes** : Orange (Flip), Rouge (Call), Vert (Put), Bleu (Pain), Gris (Pins)
- [ ] **Fond Gamma** : Vert pâle si POS, Rouge pâle si NEG
- [ ] **Pas de collision** : Niveaux bien espacés (>20 pts)
- [ ] **Position cohérente** : Prix actuel entre les niveaux logiques

---

## 🎯 **AVANTAGES DE CETTE APPROCHE**

### **Simplicité maximale :**
- ✅ **1 seul fichier CSV** à maintenir
- ✅ **0 ligne de code** Sierra Chart
- ✅ **Mise à jour instantanée** par import CSV
- ✅ **6 niveaux maximum** pour la lisibilité

### **Performance optimale :**
- ✅ **Données légères** (pas de VIX, PCR, IV inutiles)
- ✅ **Fenêtre ciblée** (±3% autour du prix)
- ✅ **Espacement intelligent** (min 20 pts)
- ✅ **Affichage propre** sur le graphique

### **Maintenance facile :**
- ✅ **Format standardisé** CSV simple
- ✅ **Validation automatique** avec checklist
- ✅ **Mise à jour rapide** (30 secondes max)
- ✅ **Pas de dépendance** externe

---

## 🚀 **EXEMPLE COMPLET D'UTILISATION**

### **Fichier : `ES_gex_levels.csv`**
```csv
symbol,trade_datetime_utc,spot,gex_total,gex_regime,gex1_flip,gex2_call_wall,gex3_put_wall,gex4_max_pain,gex5_pin1,gex6_pin2,window_pct,min_gap_pts,source,notes
ES,2025-08-29T21:30:00Z,5512.25,2.75e10,POS,5468.00,5525.00,5450.00,5538.00,5510.00,5490.00,0.03,20,DealerBias/Options,"Session forte, pins actifs"
```

### **Résultat visuel sur Sierra Chart :**
- **Ligne orange** à 5468 (Gamma Flip) 
- **Ligne rouge** à 5525 (Call Wall)
- **Ligne verte** à 5450 (Put Wall)
- **Ligne bleue pointillée** à 5538 (Max Pain)
- **Ligne grise** à 5510 (Pin1)
- **Ligne grise** à 5490 (Pin2)
- **Fond vert pâle** (régime Gamma positif)

---

*Document créé le : 29 Août 2025*  
*Version : 1.0 - Ultra-Simple*  
*Auteur : MIA_IA_SYSTEM Team*  
*Status : ✅ PRÊT POUR USAGE*


