# 🚀 GUIDE DÉMARRAGE RAPIDE - POLYGON.IO SPX

## ⚡ Utilisation Immédiate

### **1. Test Rapide du Bridge ES**
```bash
# Depuis la racine du projet
python -u es_bias_bridge.py 2>&1
```

**Résultat attendu** :
```json
{
  "ok": true,
  "status": "ok",
  "direction": "NEUTRAL",
  "strength": "WEAK",
  "score": 0.100,
  "underlying_price": 6450.5,
  "meta": {"calls": 204, "puts": 204},
  "ts": "2025-08-31T18:08:44.023384"
}
```

### **2. Test de l'Adaptateur Complet**
```bash
python data/polygon_spx_adapter.py
```

**Résultat attendu** :
```
Options SPY: OK
Stocks SPY: OK
Options récupérées: 204 calls, 204 puts (total: 408)
Dealer's Bias: NEUTRAL WEAK (0.100)
Test SPX réussi!
```

---

## 🎯 Intégration dans Votre Code

### **Appel Simple du Bridge**
```python
import subprocess
import json

def get_spx_bias():
    """Récupère le Dealer's Bias SPX pour ES trading"""
    try:
        result = subprocess.run(
            ["python", "es_bias_bridge.py"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data["ok"]:
                return {
                    "direction": data["direction"],
                    "strength": data["strength"], 
                    "score": data["score"],
                    "price": data["underlying_price"]
                }
        return None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

# Utilisation
bias = get_spx_bias()
if bias:
    print(f"SPX Bias: {bias['direction']} {bias['strength']} ({bias['score']:.3f})")
```

### **Utilisation Directe de l'Adaptateur**
```python
import asyncio
from data.polygon_spx_adapter import PolygonSPXAdapter

async def get_spx_data():
    adapter = PolygonSPXAdapter()
    snapshot = await adapter.get_spx_snapshot_for_es()
    
    if snapshot and snapshot["status"] != "empty":
        bias = snapshot["dealers_bias"]
        return {
            "direction": bias["direction"],
            "strength": bias["strength"],
            "score": bias["score"],
            "price": snapshot["underlying_price"]
        }
    return None

# Utilisation
bias = asyncio.run(get_spx_data())
```

---

## 🔧 Configuration

### **Clé API Polygon.io**
- **Plan** : Starter ($29/mois)
- **Clé** : `wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy` (déjà configurée)
- **Entitlements** : Stocks SPY + Options SPY

### **Variables d'Environnement (Optionnel)**
```bash
export POLYGON_API_KEY="wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy"
```

---

## 📊 Interprétation des Résultats

### **Codes de Sortie**
- **0** : Succès (données exploitables)
- **2** : Erreur ou données insuffisantes

### **Status des Données**
- **"ok"** : Données complètes (≥10 calls ET ≥10 puts)
- **"partial"** : Données partielles (≥5 calls OU ≥5 puts)
- **"empty"** : Données insuffisantes

### **Dealer's Bias**
- **Direction** : `BULLISH` / `BEARISH` / `NEUTRAL`
- **Strength** : `STRONG` / `MODERATE` / `WEAK`
- **Score** : -1.0 à +1.0 (négatif = bearish, positif = bullish)

---

## 🧪 Tests

### **Tests Automatisés**
```bash
# Tests du bridge
python tests/test_es_bridge.py

# Tests de validation
python tests/test_adapter_validation.py
```

### **Test Simple**
```bash
python test_bridge_simple.py
```

---

## ⚠️ Limitations Plan Starter

- **Rate Limit** : 5 calls/minute
- **Data Delay** : 15 minutes
- **Pas de quotes temps réel** (données simulées)
- **Pas d'historique étendu**

---

## 🆘 Dépannage

### **Problème : Pas de sortie JSON**
```bash
# Vérifier que vous êtes à la racine du projet
pwd  # Doit afficher D:\MIA_IA_system

# Tester avec logs détaillés
python -u es_bias_bridge.py 2>&1
```

### **Problème : Import Error**
```bash
# Vérifier les fichiers __init__.py
ls data/__init__.py
ls tests/__init__.py
```

### **Problème : Timeout**
```bash
# Augmenter le timeout dans es_bias_bridge.py
# Ligne : timeout=20 → timeout=30
```

---

## 📞 Support

- **Logs** : `polygon_spx.log`
- **Cache** : 5 minutes TTL
- **Retry** : Backoff exponentiel automatique

---

**🎉 Votre système Polygon.io SPX est prêt pour le trading ES !**











