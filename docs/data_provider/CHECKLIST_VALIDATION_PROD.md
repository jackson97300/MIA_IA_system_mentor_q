# ✅ CHECKLIST VALIDATION PRODUCTION - POLYGON SNAPSHOT

## 🎯 **10 assertions à vérifier après chaque run**

### **📊 SECTION 1 : TIMESTAMPS & TIMEZONE**
- [ ] **1.1** : `snapshot['timestamp']` se termine par `+00:00` (UTC aware) ✅
- [ ] **1.2** : `stale_minutes` est un entier positif < 1440 (max 24h) ✅
- [ ] **1.3** : `market_status` = "OPEN" si `stale_minutes < 30`, "CLOSED" sinon ✅

### **🔢 SECTION 2 : GAMMA FLIP PRÉCISION**
- [ ] **2.1** : `gamma_flip_strike` existe et > 0 ✅
- [ ] **2.2** : `cumulative_gamma_at_flip` ≠ `cumulative_gamma_final` (sauvegarde au bon moment) ✅
- [ ] **2.3** : `quality` ∈ ["clear", "moderate", "ambiguous", "edge", "unknown"] ✅

### **🏢 SECTION 3 : WALLS & NIVEAUX**
- [ ] **3.1** : `call_wall.strike` ≠ `put_wall.strike` (pas identiques) ✅
- [ ] **3.2** : Niveaux dans fenêtre `spot ± (window_pct * spot)` ✅
- [ ] **3.3** : Aucun niveau à < `min_gap_pts` d'un autre (déduplication OK) ✅

### **📈 SECTION 4 : SANITY SCORE**
- [ ] **4.1** : `sanity_checks.status` ∈ ["GO", "CAUTION", "NO_GO"] + score 0-100 ✅

---

## 🧪 **TESTS RAPIDES VISUELS**

### **A. Cohérence GEX**
```bash
# Vérifier signe dealers cohérent
gex_total_signed < 0  # Dealers short → gamma négatif normal ✅
net_gamma < 0         # Idem pour net gamma ✅
```

### **B. CSV Overlay propre**
```bash
# Compter colonnes non vides (hors Vol Trigger slot 0)
slots_filled = count(gex1_flip, gex2_call_wall, gex3_put_wall, gex4_max_pain, gex5_pin1, gex6_pin2)
assert 4 <= slots_filled <= 6  # Au moins Flip+Walls+MaxPain ✅
```

### **C. Normalisation par symbole**
```bash
# SPX vs NDX
assert gex_normalization_factor['SPX'] <= gex_normalization_factor['NDX']  ✅
```

---

## 🚨 **RED FLAGS (arrêter si détecté)**

### **❌ Timezone naive/aware mixé**
```python
TypeError: can't subtract offset-naive and offset-aware datetimes
```
→ **Fix** : Tous les timestamps en UTC aware

### **❌ Flip quality bancale**
```python
quality = "unknown" and gamma_flip_present = True
```
→ **Fix** : Vérifier données gamma_by_strike

### **❌ Walls identiques répétées**
```python
call_wall.strike == put_wall.strike and sanity_score > 80
```
→ **Fix** : Logic second_best_put défaillante

### **❌ CSV slots débordants**
```csv
gex7_extra,gex8_extra  # Plus de 6 slots ❌
```
→ **Fix** : Déduplication insuffisante

---

## 🎛️ **COMMANDES DEBUG RAPIDES**

### **Snapshot complete :**
```python
snapshot = await create_polygon_snapshot("SPX")
print(f"Status: {snapshot['sanity_checks']['status']}")
print(f"Levels: {list(snapshot['analysis']['levels'].keys())}")
```

### **CSV overlay seul :**
```python
csv_content = generate_csv_overlay(snapshot)
headers = csv_content.split('\n')[0].split(',')
values = csv_content.split('\n')[1].split(',')
print(f"Slots remplis: {sum(1 for v in values[5:11] if v)}")  # gex0-gex6
```

### **Sanity rapide :**
```python
checks = run_sanity_checks(snapshot)
print(f"Erreurs: {checks['errors']}")
print(f"Warnings: {checks['warnings']}")
if checks['score'] < 80: print("⚠️ CAUTION/NO_GO")
```

---

## 🏁 **VALIDATION RÉUSSIE SI :**

✅ **Aucun red flag détecté**  
✅ **10 assertions cochées**  
✅ **Sanity status ≠ "ERROR"**  
✅ **CSV overlay 4-6 niveaux max**  
✅ **Timestamps UTC aware cohérents**

### **→ Production OK, snapshot prêt pour Sierra Chart ! 🚀**

---

## 📋 **EXEMPLE VALIDATION RÉUSSIE**

```json
{
  "sanity_checks": {
    "status": "GO",
    "score": 92,
    "errors": [],
    "warnings": ["FLIP_GEX_UNUSUAL"]
  },
  "analysis": {
    "levels": {
      "gamma_flip": {"gamma_flip_strike": 6475, "quality": "clear"},
      "call_wall": {"strike": 6550},
      "put_wall": {"strike": 6450},
      "max_pain": 6525,
      "gamma_pins": [{"strike": 6510}]
    },
    "gex": {
      "gex_total_signed": -2.3e12,
      "net_gamma": -2.3e12,
      "gex_total_normalized": -2.3
    }
  }
}
```

**✅ Tous les critères respectés = VALIDATION PRODUCTION OK !**


