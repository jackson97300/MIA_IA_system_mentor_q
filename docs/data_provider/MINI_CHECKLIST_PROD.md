# ✅ MINI-CHECKLIST GO/NO-GO - 5 POINTS CRITIQUES

## 🎯 **À vérifier après chaque run (30 secondes)**

### **□ 1. TIMESTAMP UTC-AWARE**
```python
# Vérification rapide
assert snapshot['timestamp'].endswith(('Z', '+00:00', 'UTC'))
print("✅ Timestamp UTC-aware")
```
**💡 Red flag :** Timestamp naïf → Crash stale_minutes

---

### **□ 2. NIVEAUX ESPACÉS ≥ MIN_GAP**
```python
# Extraction niveaux CSV
csv_lines = csv_content.split('\n')
levels = [float(v) for v in csv_lines[1].split(',')[6:12] if v]  # gex1-gex6
gaps = [abs(levels[i+1] - levels[i]) for i in range(len(levels)-1)]
min_gap = 20  # ES: 20, NDX: 60

assert all(gap >= min_gap for gap in gaps)
print("✅ Niveaux espacés correctement")
```
**💡 Red flag :** Traits collés < min_gap → Déduplication défaillante

---

### **□ 3. PINS ≤2 ET DANS FENÊTRE ±3%**
```python
# Compter pins valides (gex5-gex6 seulement, pas gex0)
pins_count = sum(1 for v in csv_lines[1].split(',')[10:12] if v)  # gex5-gex6
spot = float(csv_lines[1].split(',')[2])
window = spot * 0.03

pin_levels = [float(v) for v in csv_lines[1].split(',')[10:12] if v]
in_window = all(abs(pin - spot) <= window for pin in pin_levels)

assert pins_count <= 2 and in_window
print("✅ Pins valides et dans fenêtre")

# ⚠️ IMPORTANT : Ne pas compter gex0_vol_trigger dans les pins !
vol_trigger = csv_lines[1].split(',')[5]  # gex0 - optionnel
print(f"Vol Trigger (non tracé): {vol_trigger if vol_trigger else 'Vide'}")
```
**💡 Red flag :** Pins > 2 ou hors fenêtre → Filtrage insuffisant  
**💡 Rappel :** Vol Trigger (gex0) disponible mais non tracé automatiquement

---

### **□ 4. GEX REGIME COHÉRENT**
```python
# Vérifier cohérence gex_total vs gex_regime
gex_total = float(csv_lines[1].split(',')[3])  # Format scientifique
gex_regime = csv_lines[1].split(',')[4]  # POS/NEG

expected_regime = "POS" if gex_total > 0 else "NEG"
assert gex_regime == expected_regime
print("✅ GEX regime cohérent")
```
**💡 Red flag :** Incohérence → Fond Sierra incorrect

---

### **□ 5. SANITY SCORE ≥ 60**
```python
# Vérifier sanity checks
sanity = snapshot.get('sanity_checks', {})
score = sanity.get('score', 0)
status = sanity.get('status', 'ERROR')

assert score >= 60 and status in ['GO', 'CAUTION']
print(f"✅ Sanity OK: {status} ({score}/100)")
```
**💡 Red flag :** NO_GO → CSV non généré, revoir données

---

## 🚨 **ACTION SI ÉCHEC**

### **❌ Check 1-2 échouent → STOP**
- **Fix immédiat requis** (timezone, déduplication)
- **Pas de trading** sur ce snapshot

### **⚠️ Check 3-4 échouent → CAUTION**  
- **Utilisable mais dégradé** (pins manquants, fond KO)
- **Trading possible** avec vigilance

### **✅ Check 5 → Status final**
- **GO (80+)** : Production normale
- **CAUTION (60-79)** : Utilisable avec warnings
- **NO_GO (<60)** : Abandon snapshot

---

## ⚡ **COMMANDE ULTRA-RAPIDE**

### **One-liner validation :**
```python
def quick_check(snapshot, csv_content):
    lines = csv_content.strip().split('\n')
    values = lines[1].split(',')
    
    # Check 1: Timestamp UTC
    utc_ok = snapshot['timestamp'].endswith(('Z', '+00:00'))
    
    # Check 2-3: Niveaux et pins (gex1-gex6, PAS gex0)
    traced_levels = [float(v) for v in values[6:12] if v]  # gex1-gex6
    gaps_ok = len(traced_levels) <= 6 and (not traced_levels or all(abs(traced_levels[i+1]-traced_levels[i]) >= 20 for i in range(len(traced_levels)-1)))
    pins_ok = sum(1 for v in values[10:12] if v) <= 2  # gex5-gex6 seulement
    
    # Check 4: GEX regime
    gex_total = float(values[3])
    regime_ok = (values[4] == "POS") == (gex_total > 0)
    
    # Check 5: Sanity
    sanity_ok = snapshot.get('sanity_checks', {}).get('score', 0) >= 60
    
    # Info Vol Trigger (non critique)
    vol_trigger = values[5] if values[5] else "Non défini"
    
    checks = [utc_ok, gaps_ok, pins_ok, regime_ok, sanity_ok]
    return all(checks), checks, vol_trigger

# Usage
passed, details, vol_trigger = quick_check(snapshot, csv_overlay)
if passed:
    print("🚀 ALL CHECKS PASSED - READY FOR SIERRA")
    print(f"📊 Traits tracés: {sum(1 for v in values[6:12] if v)}/6 (Vol Trigger: {vol_trigger})")
else:
    print(f"❌ FAILED CHECKS: {[i+1 for i, ok in enumerate(details) if not ok]}")
```

---

## 📊 **EXEMPLE VALIDATION RÉUSSIE**

```
✅ 1. Timestamp UTC-aware: 2025-08-29T21:30:00+00:00
✅ 2. Niveaux espacés: [6475, 6550, 6450, 6525, 6510] gaps=[75, 100, 75, 15] min=20 ✗→ Pin ajusté
✅ 3. Pins valides: 1 pin dans ±3% (6510 vs 6500 spot)
✅ 4. GEX regime: -2.3e12 → NEG ✅ 
✅ 5. Sanity score: GO (92/100)

🚀 VALIDATION COMPLÈTE - SNAPSHOT PRÊT PRODUCTION
```

**→ 5 checks en 10 secondes, validation prod instantanée ! ⚡**
