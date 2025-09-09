# 📊 RAPPORT DE QUALITÉ DES DONNÉES MIA
**Fichier analysé :** `chart_3_20250904.jsonl`
**Date d'analyse :** 2025-09-04 13:00:22

## 📋 INVENTAIRE DES TYPES DE DONNÉES

| Type | Nombre de lignes | Champs détectés |
|------|------------------|-----------------|
| depth | 26,980 | group, lvl, price, seq, side, size, sym, t, type |
| trade | 8,953 | chart, px, qty, seq, source, sym, t, type, vol |
| vap | 2,866 | bar, k, price, seq, sym, t, type, vol |
| quote | 1,334 | aq, ask, bid, bq, chart, kind, mid, seq, spread, sym, t, type |
| basedata | 717 | askvol, bidvol, c, h, i, l, o, seq, sym, t, type, v |
| vwap | 717 | dn1, dn2, i, seq, src, sym, t, type, up1, up2, v |
| vix | 53 | chart, i, last, seq, source, sym, t, type |
| vva | 52 | i, id_curr, id_prev, ppoc, pvah, pval, sym, t, type, vah, val, vpoc |
| volume_profile | 5 | bar, poc, source, study_id, sym, t, type, vah, val |
| volume_profile_previous | 5 | bar, ppoc, pvah, pval, source, study_id, sym, t, type |
| vwap_current | 5 | bar, s_minus_1, s_minus_2, s_plus_1, s_plus_2, source, study_id, sym, t, type, vwap |
| pvwap_diag | 3 | currStart, msg, t, type |
| ohlc_graph4 | 3 | bar, chart, close, dt_g4, high, low, open, source, sym, t, type |
| vwap_diag | 2 | resolved_id, seq, sym, t, type |
| vwap_previous | 2 | bar, psd_minus_1, psd_plus_1, pvwap, source, study_id, t, type |
| vix_diag | 1 | chart, msg, t, type |

## 📈 STATISTIQUES CLÉS PAR TYPE

### BASEDATA
**Total :** 717 lignes

- **askvol:** min=31, avg=6023.53, max=6470
- **bidvol:** min=48, avg=6024.52, max=6470
- **c:** min=6462.5, avg=6469.35, max=6470.25
- **h:** min=6463.0, avg=6469.83, max=6470.25
- **i:** min=608, avg=780.64, max=786
- **l:** min=6462.25, avg=6469.07, max=6469.5
- **o:** min=6462.75, avg=6469.70, max=6470.0
- **seq:** min=1, avg=310.71, max=667
- **t:** min=45904.224477, avg=45904.53, max=45904.541921
- **v:** min=11, avg=300.41, max=750

### VWAP_DIAG
**Total :** 2 lignes

- **resolved_id:** min=22, avg=22.00, max=22
- **seq:** min=1, avg=0.50, max=1
- **t:** min=45904.224477, avg=45904.38, max=45904.538773

### VWAP
**Total :** 717 lignes

- **dn1:** min=6432.93, avg=6433.77, max=6433.8
- **dn2:** min=6420.95, avg=6420.96, max=6421.15
- **i:** min=608, avg=780.64, max=786
- **seq:** min=1, avg=310.71, max=667
- **t:** min=45904.224477, avg=45904.53, max=45904.541921
- **up1:** min=6456.5775, avg=6459.38, max=6459.495
- **up2:** min=6468.4, avg=6472.19, max=6472.345
- **v:** min=6444.7525, avg=6446.58, max=6446.6475

### VVA
**Total :** 52 lignes

- **i:** min=608, avg=723.46, max=786
- **id_curr:** min=1, avg=0.96, max=1
- **id_prev:** min=2, avg=1.92, max=2
- **ppoc:** min=0.0, avg=0.00, max=0.0
- **pvah:** min=0.0, avg=0.00, max=0.0
- **pval:** min=0.0, avg=0.00, max=0.0
- **t:** min=45904.224477, avg=45904.43, max=45904.541574
- **vah:** min=6430.75, avg=6432.24, max=6469.75
- **val:** min=6426.5, avg=6454.84, max=6457.0
- **vpoc:** min=6427.5, avg=6429.28, max=6473.75

### PVWAP_DIAG
**Total :** 3 lignes

- **currStart:** min=0, avg=0.00, max=0
- **t:** min=45904.224477, avg=45904.41, max=45904.531221

### VIX_DIAG
**Total :** 1 lignes

- **chart:** min=8, avg=8.00, max=8
- **t:** min=45904.534259, avg=45904.53, max=45904.534259

### VOLUME_PROFILE
**Total :** 5 lignes

- **bar:** min=608, avg=742.40, max=786
- **poc:** min=6440.0, avg=6453.50, max=6473.75
- **study_id:** min=9, avg=9.00, max=9
- **t:** min=45904.534259, avg=45904.54, max=45904.541574
- **vah:** min=6426.5, avg=6454.25, max=6473.75
- **val:** min=6426.5, avg=6443.70, max=6469.75

### VOLUME_PROFILE_PREVIOUS
**Total :** 5 lignes

- **bar:** min=608, avg=742.40, max=786
- **ppoc:** min=6440.0, avg=6453.50, max=6473.75
- **pvah:** min=6426.5, avg=6454.25, max=6473.75
- **pval:** min=6426.5, avg=6443.70, max=6469.75
- **study_id:** min=8, avg=8.00, max=8
- **t:** min=45904.534259, avg=45904.54, max=45904.541574

### VWAP_CURRENT
**Total :** 5 lignes

- **bar:** min=608, avg=742.40, max=786
- **s_minus_1:** min=6427.5, avg=6427.50, max=6427.5
- **s_minus_2:** min=0.0, avg=0.00, max=0.0
- **s_plus_1:** min=6454.0, avg=6456.30, max=6457.0
- **s_plus_2:** min=0.0, avg=0.00, max=0.0
- **study_id:** min=1, avg=1.00, max=1
- **t:** min=45904.534259, avg=45904.54, max=45904.541574
- **vwap:** min=6430.75, avg=6430.75, max=6430.75

### TRADE
**Total :** 8,953 lignes

- **chart:** min=3, avg=0.00, max=3
- **px:** min=6462.5, avg=646584.88, max=647025.015
- **qty:** min=11, avg=0.07, max=208
- **seq:** min=1, avg=5051.12, max=10187
- **t:** min=45904.224477, avg=45904.46, max=45904.541576
- **vol:** min=1, avg=1.25, max=37

### VAP
**Total :** 2,866 lignes

- **bar:** min=608, avg=780.60, max=786
- **k:** min=0, avg=1.60, max=4
- **price:** min=6462.5, avg=6469.34, max=6470.25
- **seq:** min=1, avg=341.34, max=667
- **t:** min=45904.534259, avg=45904.54, max=45904.541921
- **vol:** min=1, avg=75.13, max=264

### VIX
**Total :** 53 lignes

- **chart:** min=8, avg=8.00, max=8
- **i:** min=8442, avg=8528.83, max=8533
- **last:** min=16.22, avg=16.25, max=16.93
- **seq:** min=1, avg=314.79, max=657
- **t:** min=45904.534294, avg=45904.54, max=45904.541875

### DEPTH
**Total :** 26,980 lignes

- **group:** min=1, avg=313.77, max=667
- **lvl:** min=1, avg=10.00, max=19
- **price:** min=6463.5, avg=6469.51, max=6475.0
- **seq:** min=1, avg=313.77, max=667
- **size:** min=23, avg=45.91, max=146
- **t:** min=45904.534329, avg=45904.54, max=45904.541921

### OHLC_GRAPH4
**Total :** 3 lignes

- **bar:** min=1016, avg=1026.00, max=1031
- **chart:** min=4, avg=4.00, max=4
- **close:** min=6462.5, avg=6467.17, max=6469.75
- **dt_g4:** min=45904.538773, avg=30603.03, max=45904.541574
- **high:** min=6463.75, avg=6468.00, max=6470.25
- **low:** min=6462.25, avg=6466.42, max=6468.5
- **open:** min=6462.5, avg=6466.83, max=6469.0
- **t:** min=45904.534375, avg=45904.54, max=45904.541574

### VWAP_PREVIOUS
**Total :** 2 lignes

- **bar:** min=753, avg=766.50, max=780
- **psd_minus_1:** min=643600.0, avg=643600.00, max=643600.0
- **psd_plus_1:** min=646425.0, avg=646425.00, max=646425.0
- **pvwap:** min=645250.0, avg=645250.00, max=645250.0
- **study_id:** min=13, avg=13.00, max=13
- **t:** min=45904.534375, avg=45904.53, max=45904.534387

### QUOTE
**Total :** 1,334 lignes

- **aq:** min=1, avg=21.60, max=87
- **ask:** min=6469.0, avg=645033.34, max=647025.015
- **bid:** min=6468.75, avg=645007.68, max=647000.015
- **bq:** min=1, avg=19.40, max=43
- **chart:** min=3, avg=0.01, max=3
- **mid:** min=6468.875, avg=19.40, max=6469.62
- **seq:** min=1, avg=5003.97, max=10145
- **spread:** min=0.25, avg=0.00, max=0.25
- **t:** min=45904.451129, avg=45904.46, max=45904.541576

## ⚠️ TOP 10 ANOMALIES

| Règle | Nombre d'occurrences |
|-------|---------------------|
| timestamp | 10278 |
| vwap | 717 |
| basedata | 667 |
| vva | 102 |

## 🎯 RÉSUMÉ PAR FAMILLE

- **basedata:** ❌ Errors
- **depth:** ✅ OK
- **ohlc_graph4:** ✅ OK
- **pvwap_diag:** ✅ OK
- **quote:** ✅ OK
- **trade:** ✅ OK
- **vap:** ✅ OK
- **vix:** ✅ OK
- **vix_diag:** ✅ OK
- **volume_profile:** ✅ OK
- **volume_profile_previous:** ✅ OK
- **vva:** ❌ Errors
- **vwap:** ❌ Errors
- **vwap_current:** ✅ OK
- **vwap_diag:** ✅ OK
- **vwap_previous:** ✅ OK