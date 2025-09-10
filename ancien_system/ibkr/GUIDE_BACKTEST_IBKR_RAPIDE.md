# 🚀 GUIDE RAPIDE - BACKTESTING AVEC IBKR

**MIA_IA_SYSTEM - Backtesting avec données IBKR réelles**  
**Version**: 1.0.0  
**Temps estimé**: 5-10 minutes

---

## 🎯 **VOS DONNÉES IBKR DISPONIBLES**

Selon votre capture d'écran, vous avez accès à :

### **✅ Données Activées**
- **CME Real-Time (NP,L2)** - Level 2 data pour futures
- **OPRA (Options US)** - Données options flow
- **Cotations US continues** - Données futures temps réel
- **Données historiques** - Pour backtesting

### **💰 Coût Mensuel**
- **Total**: EUR 10.8/mois
- **CME Real-Time**: USD 11.00/mois
- **OPRA**: USD 1.50/mois
- **Autres**: Frais levés

---

## ⚡ **DÉMARRAGE ULTRA-RAPIDE**

### **1. Test Connexion IBKR**
```bash
# Test connexion IBKR
python scripts/backtest_ibkr_complete.py --test-connection
```

### **2. Backtest Rapide (30 jours)**
```bash
# Backtest rapide avec données récentes
python scripts/backtest_ibkr_complete.py --quick
```

### **3. Backtest Complet (1 an)**
```bash
# Backtest complet avec Battle Navale + Confluence
python scripts/backtest_ibkr_complete.py --start-date 2024-01-01 --end-date 2025-06-30
```

---

## 🎯 **COMMANDES PRATIQUES**

### **A. Tests de Base**
```bash
# Test connexion uniquement
python scripts/backtest_ibkr_complete.py --test-connection

# Backtest rapide (30 jours)
python scripts/backtest_ibkr_complete.py --quick

# Backtest sans Battle Navale
python scripts/backtest_ibkr_complete.py --quick --no-battle-navale

# Backtest sans Confluence
python scripts/backtest_ibkr_complete.py --quick --no-confluence
```

### **B. Backtests Avancés**
```bash
# Backtest personnalisé
python scripts/backtest_ibkr_complete.py \
  --start-date 2024-01-01 \
  --end-date 2025-06-30 \
  --symbol ES \
  --capital 100000 \
  --commission 2.50 \
  --slippage 0.5

# Backtest sans ML (plus rapide)
python scripts/backtest_ibkr_complete.py --quick --no-ml

# Backtest sans rapports (plus rapide)
python scripts/backtest_ibkr_complete.py --quick --no-reports
```

### **C. Tests Multi-Symboles**
```bash
# Test ES (E-mini S&P 500)
python scripts/backtest_ibkr_complete.py --quick --symbol ES

# Test NQ (E-mini NASDAQ)
python scripts/backtest_ibkr_complete.py --quick --symbol NQ

# Test YM (E-mini Dow)
python scripts/backtest_ibkr_complete.py --quick --symbol YM
```

---

## 📊 **INTERPRÉTATION RÉSULTATS**

### **Métriques Clés à Surveiller**

#### **✅ Métriques Positives**
- **Win Rate > 55%** - Stratégie profitable
- **Profit Factor > 1.5** - Bon ratio risque/récompense
- **Sharpe Ratio > 1.0** - Bonne performance ajustée au risque
- **Max Drawdown < 15%** - Gestion risque acceptable

#### **⚠️ Métriques à Améliorer**
- **Win Rate < 45%** - Revoir stratégie
- **Profit Factor < 1.2** - Optimiser stops/targets
- **Max Drawdown > 20%** - Réduire taille positions
- **Sharpe Ratio < 0.5** - Améliorer cohérence

### **Exemple de Sortie**
```
🚀 LANCEMENT BACKTEST...
Symbole: ES
Période: 2024-01-01 → 2025-06-30
Capital: $100,000.00
Battle Navale: ✅
Confluence: ✅
ML Training: ✅
IBKR Connecté: ✅

📊 RÉSULTATS BACKTEST:
Trades totaux: 156
Win rate: 62.8%
P&L total: $8,450.25
Profit factor: 1.85
Max drawdown: 12.3%
Sharpe ratio: 1.42
Return: 8.45%
```

---

## 🔧 **CONFIGURATION IBKR**

### **A. Vérifications Préalables**
1. **TWS/Gateway ouvert**
2. **Port API correct** (7497 paper, 7496 live)
3. **API clients activés**
4. **Souscriptions données actives**

### **B. Test Connexion Manuel**
```python
# Test manuel connexion
python -c "
from core.ibkr_connector import IBKRConnector
import asyncio

async def test():
    ibkr = IBKRConnector({'ibkr_port': 7497})
    return await ibkr.connect()

print('Connecté:', asyncio.run(test()))
"
```

### **C. Données Disponibles**
```python
# Vérifier données disponibles
print("📊 Données IBKR disponibles:")
print("   - CME Real-Time (NP,L2) - Level 2 data")
print("   - OPRA (Options US) - Options flow")
print("   - Cotations US continues - Futures data")
print("   - Données historiques - Backtesting")
```

---

## 🚨 **TROUBLESHOOTING**

### **Problème: Connexion IBKR échoue**
```bash
❌ Connexion IBKR échouée
```

**Solutions**:
1. **Vérifier TWS/Gateway**:
   - TWS ouvert et connecté
   - Port API correct (7497/7496)
   - API clients activés

2. **Test manuel**:
```bash
python scripts/backtest_ibkr_complete.py --test-connection
```

### **Problème: Erreur import modules**
```bash
❌ Erreur import MIA_IA_SYSTEM: No module named 'core'
```

**Solution**:
```bash
# Vérifier structure projet
ls -la core/ scripts/ ml/

# Installer dépendances
pip install -r requirements.txt
```

### **Problème: Pas de données historiques**
```bash
Aucune donnée historique trouvée - génération données simulées
```

**Solutions**:
1. **Vérifier connexion IBKR**
2. **Tester avec données simulées** (normal pour tests)
3. **Configurer données historiques** dans IBKR

---

## ⚡ **OPTIMISATION PERFORMANCE**

### **Backtest Rapide**
```bash
# Mode ultra-rapide (30 jours, sans ML, sans rapports)
python scripts/backtest_ibkr_complete.py --quick --no-ml --no-reports
```

### **Backtest Complet**
```bash
# Mode complet avec toutes les fonctionnalités
python scripts/backtest_ibkr_complete.py \
  --start-date 2024-01-01 \
  --end-date 2025-06-30 \
  --symbol ES \
  --capital 100000
```

### **Tests Multi-Paramètres**
```bash
# Test différentes configurations
python scripts/backtest_ibkr_complete.py --quick --no-battle-navale
python scripts/backtest_ibkr_complete.py --quick --no-confluence
python scripts/backtest_ibkr_complete.py --quick --capital 50000
python scripts/backtest_ibkr_complete.py --quick --commission 1.50
```

---

## 📋 **FICHIERS GÉNÉRÉS**

### **Rapports Backtest**
```
backtest_report_ES_20250701_143022.json
├── backtest_info
│   ├── symbol: ES
│   ├── start_date: 2024-01-01
│   ├── end_date: 2025-06-30
│   ├── initial_capital: 100000
│   └── data_source: IBKR_API
├── performance_metrics
│   ├── total_trades: 156
│   ├── win_rate: 0.628
│   ├── total_pnl: 8450.25
│   ├── profit_factor: 1.85
│   ├── max_drawdown: 0.123
│   └── sharpe_ratio: 1.42
├── trades: [...]
├── equity_history: [...]
└── generated_at: 2025-07-01T14:30:22
```

### **Données ML**
```
data/ml/datasets/
└── backtest_dataset_20250701_143022.parquet
```

---

## 🎯 **PROCHAINES ÉTAPES**

### **1. Validation Stratégie**
- ✅ Backtest sur données historiques
- 🔄 Optimisation paramètres
- 🔄 Validation robustesse

### **2. Paper Trading**
- 🔄 Test en temps réel
- 🔄 Validation exécution
- 🔄 Ajustement paramètres

### **3. Live Trading**
- 🔄 Déploiement production
- 🔄 Monitoring continu
- 🔄 Optimisation continue

---

## 📞 **SUPPORT**

### **En cas de problème**:
1. **Vérifier connexion IBKR**: `--test-connection`
2. **Consulter logs**: Messages d'erreur détaillés
3. **Tester données simulées**: Mode fallback automatique
4. **Vérifier configuration**: Ports, clients ID, etc.

### **Données IBKR confirmées**:
- ✅ **CME Real-Time (NP,L2)** - Level 2 data
- ✅ **OPRA (Options US)** - Options flow
- ✅ **Cotations US continues** - Futures data
- ✅ **Données historiques** - Backtesting

---

**🎯 Votre système est prêt pour le backtesting avec IBKR !** 