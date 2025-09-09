# ⚠️ AVERTISSEMENT SIERRA CHART - ÉVITER MALENTENDUS

## 🎯 **POINT CRITIQUE : NOMBRE DE TRAITS TRACÉS**

### **✅ CE QUI EST NORMAL :**
- **4-6 traits visibles** sur votre chart Sierra Chart
- **Vol Trigger (gex0) NON visible** par défaut
- **Configuration standard parfaitement fonctionnelle**

### **❌ ERREUR FRÉQUENTE :**
**NE PAS s'attendre à voir 7 traits !**

---

## 📊 **DÉTAIL TECHNIQUE**

### **Structure CSV Polygon :**
```csv
gex0_vol_trigger,gex1_flip,gex2_call_wall,gex3_put_wall,gex4_max_pain,gex5_pin1,gex6_pin2
6500.00,6475.00,6550.00,6450.00,6525.00,6510.00,
```

### **Mapping Sierra Chart :**
```
❌ gex0_vol_trigger → SG0 (Display = FALSE par défaut)
✅ gex1_flip       → SG1 (Display = TRUE) 🔄 Orange
✅ gex2_call_wall  → SG2 (Display = TRUE) 🔴 Rouge  
✅ gex3_put_wall   → SG3 (Display = TRUE) 🟢 Vert
✅ gex4_max_pain   → SG4 (Display = TRUE) 🔵 Bleu pointillé
✅ gex5_pin1       → SG5 (Display = TRUE si data) ⚪ Gris
✅ gex6_pin2       → SG6 (Display = TRUE si data) ⚪ Gris foncé
```

---

## 🎨 **RÉSULTAT VISUEL ATTENDU**

### **Configuration standard (optimale) :**
- **Minimum garanti** : 4 traits (Flip + Call Wall + Put Wall + Max Pain)
- **Maximum possible** : 6 traits (+ 2 Pins si détectés)
- **Vol Trigger** : Présent dans les données mais PAS affiché

### **Pourquoi Vol Trigger est désactivé :**
1. **Encombrement visuel** → 6 traits suffisent largement
2. **Usage optionnel** → La plupart des traders n'en ont pas besoin
3. **Activation manuelle** → Disponible si vraiment souhaité

---

## 🔧 **SI VOUS VOULEZ ACTIVER VOL TRIGGER**

### **Étapes (optionnel) :**
1. Sierra Chart → Studies → Spreadsheet Study
2. Subgraphs → SG0 (Vol Trigger)
3. **Enable Display** ✅
4. Line Style: Dash, Color: Yellow
5. Apply

### **Résultat :**
- **5-7 traits visibles** (selon pins détectés)
- **Vol Trigger jaune pointillé** ajouté
- **Performance identique** (pas d'impact)

---

## ✅ **VALIDATION NORMALE**

### **Checklist "tout va bien" :**
- [ ] **4 traits minimum** visibles (Flip + Walls + Max Pain)
- [ ] **Fond coloré** selon GEX (vert si POS, rose si NEG)
- [ ] **Pas d'erreur** dans Studies → Spreadsheet Study
- [ ] **Données à jour** (stale_minutes < 30)

### **⚠️ Si vous voyez MOINS de 4 traits :**
1. **Vérifier données CSV** → gex1-gex4 doivent être remplis
2. **Recharger spreadsheet** → F5 dans Sierra
3. **Vérifier subgraphs** → SG1-SG4 Display = TRUE

---

## 📞 **RÉSOLUTION PROBLÈMES FRÉQUENTS**

### **"Je ne vois que 3 traits"**
→ **Cause** : Put Wall ou Max Pain manquant dans les données
→ **Solution** : Vérifier sanity checks du snapshot Polygon

### **"Où est mon 7ème trait ?"**
→ **Cause** : Vol Trigger désactivé par défaut (normal)
→ **Solution** : Activation manuelle SG0 si souhaité

### **"Les traits changent de couleur"**
→ **Cause** : Configuration subgraphs incorrecte
→ **Solution** : Appliquer template SIERRA_CHART_SETTINGS.md

### **"Pas de fond coloré"**
→ **Cause** : Study "Color Background" non configurée
→ **Solution** : Ajouter study séparée pour gex_regime

---

## 🎯 **RÉCAPITULATIF IMPORTANT**

### **✅ CONFIGURATION STANDARD OPTIMALE :**
- **4-6 traits** = **Parfaitement normal et optimal**
- **Vol Trigger absent** = **Comportement attendu par défaut**
- **Fond coloré** = **Indicateur GEX regime**

### **❌ NE PAS CHERCHER 7 TRAITS !**
Le système fonctionne parfaitement avec 4-6 traits. Vol Trigger est un bonus optionnel, pas une nécessité.

**→ Configuration 4-6 traits = PRODUCTION OPTIMALE ! 🚀**


