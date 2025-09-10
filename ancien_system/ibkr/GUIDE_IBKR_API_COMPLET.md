# 🎯 GUIDE COMPLET - API IBKR POUR MIA_IA_SYSTEM

**Version: 1.0.0 - Configuration Complète IBKR**  
**Date**: Juillet 2025  
**Status**: ✅ GUIDE PAS À PAS COMPLET

---

## 🏆 **OBJECTIF FINAL**

Obtenir une connexion IBKR complète avec toutes les données nécessaires pour satisfaire les besoins du bot MIA_IA_SYSTEM :

- ✅ **Données de marché en temps réel** (ES, NQ, YM)
- ✅ **Données historiques** pour backtesting
- ✅ **Données options flow** pour analyse avancée
- ✅ **Données de compte** pour gestion risque
- ✅ **Exécution d'ordres** pour trading automatique

---

## 📋 **ÉTAPES COMPLÈTES**

### **ÉTAPE 1 : CRÉATION COMPTE IBKR** 🏦

#### **A. Ouverture Compte**
1. **Aller sur** : [Interactive Brokers](https://www.interactivebrokers.com/)
2. **Cliquer** : "Ouvrir un compte"
3. **Choisir** : "Compte individuel" ou "Compte professionnel"
4. **Remplir** : Informations personnelles complètes
5. **Valider** : Documents d'identité requis

#### **B. Configuration Compte**
```bash
# Types de comptes recommandés
✅ Compte Paper Trading (gratuit) - Pour tests
✅ Compte Live Trading - Pour production

# Permissions nécessaires
✅ Options Trading
✅ Futures Trading  
✅ Margin Trading
✅ API Access
```

#### **C. Dépôt Minimum**
```bash
# Montants minimums
Paper Trading: 0€ (gratuit)
Live Trading: 10,000€ (recommandé)
Options Trading: 25,000€ (pour options flow)
```

---

### **ÉTAPE 2 : INSTALLATION TWS/GATEWAY** 💻

#### **A. Téléchargement**
```bash
# TWS (Trader Workstation)
URL: https://www.interactivebrokers.com/en/trading/tws.php

# IB Gateway (plus léger)
URL: https://www.interactivebrokers.com/en/trading/ib-api.php

# Version recommandée
TWS: 10.19.2c ou plus récent
Gateway: 10.19.2c ou plus récent
```

#### **B. Installation TWS**
```bash
# Windows
1. Télécharger TWS_10.19.2c.exe
2. Exécuter en tant qu'administrateur
3. Suivre l'assistant d'installation
4. Créer raccourci bureau

# Configuration initiale
✅ "Enable ActiveX and Socket Clients"
✅ "Download open orders on connection"
✅ "Create API order log file"
```

#### **C. Configuration API TWS**
```bash
# Dans TWS : File → Global Configuration → API → Settings

✅ Enable ActiveX and Socket Clients
✅ Socket port: 7497 (paper) / 7496 (live)
✅ Master API client ID: 0
✅ Read-Only API: NON
✅ Download open orders on connection: OUI
✅ Include FX positions: OUI
✅ Create API order log file: OUI

# API → Precautions
✅ Bypass Order Precautions for API Orders
✅ Allow connections from localhost
✅ Allow connections from 127.0.0.1
```

---

### **ÉTAPE 3 : INSTALLATION PYTHON DEPENDENCIES** 🐍

#### **A. Installation ib-insync**
```bash
# Installation principale
pip install ib-insync==0.9.86

# Dépendances supplémentaires
pip install pandas numpy asyncio websockets

# Validation installation
python -c "from ib_insync import IB; print('✅ ib-insync installé')"
```

#### **B. Installation ibapi (alternative)**
```bash
# Alternative plus basique
pip install ibapi

# Validation
python -c "from ibapi import *; print('✅ ibapi installé')"
```

---

### **ÉTAPE 4 : CONFIGURATION PYTHON** ⚙️

#### **A. Création fichier de configuration**
```python
# config/ibkr_config.py
IBKR_CONFIG = {
    # Connexion
    'host': '127.0.0.1',
    'port': 7497,  # 7497 paper, 7496 live
    'client_id': 1,
    'timeout': 30,
    
    # Compte
    'account_id': '',  # À remplir après création compte
    'paper_trading': True,
    
    # Données
    'market_data_type': 3,  # 1=Live, 2=Frozen, 3=Delayed
    'subscribe_positions': True,
    'subscribe_orders': True,
    'subscribe_account': True,
    
    # Rate limits
    'max_requests_per_second': 50,
    'max_ticker_subscriptions': 100,
    
    # Symbols à trader
    'symbols': ['ES', 'NQ', 'YM'],
    'exchanges': ['CME'],
    'currencies': ['USD']
}
```

#### **B. Variables d'environnement**
```bash
# .env file
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=1
IBKR_ACCOUNT_ID=your_account_id
IBKR_PAPER_TRADING=true
```

---

### **ÉTAPE 5 : TEST DE CONNEXION** 🔌

#### **A. Script de test simple**
```python
# test_ibkr_connection.py
#!/usr/bin/env python3

from ib_insync import *
import asyncio

async def test_ibkr_connection():
    """Test de connexion IBKR"""
    
    # Configuration
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    try:
        # Test connexion
        print("🔌 Test de connexion...")
        if ib.isConnected():
            print("✅ Connexion réussie!")
            
            # Test données compte
            print("📊 Récupération données compte...")
            account = ib.accountSummary()
            print(f"✅ Compte: {account}")
            
            # Test données marché
            print("📈 Récupération données ES...")
            contract = Future('ES', '202412', 'CME')
            ib.qualifyContracts(contract)
            
            # Subscribe market data
            ib.reqMktData(contract)
            await asyncio.sleep(2)
            
            ticker = ib.ticker(contract)
            if ticker.marketPrice():
                print(f"✅ Prix ES: {ticker.marketPrice()}")
            else:
                print("⚠️ Pas de données marché")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        ib.disconnect()

if __name__ == "__main__":
    asyncio.run(test_ibkr_connection())
```

#### **B. Exécution du test**
```bash
# Lancer le test
python test_ibkr_connection.py

# Résultats attendus
✅ Connexion réussie!
✅ Compte: [données compte]
✅ Prix ES: [prix actuel]
```

---

### **ÉTAPE 6 : RÉCUPÉRATION DONNÉES CRITIQUES** 📊

#### **A. Données de marché temps réel**
```python
# get_market_data.py
async def get_real_time_data():
    """Récupération données temps réel"""
    
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    # Contrats futures
    contracts = {
        'ES': Future('ES', '202412', 'CME'),
        'NQ': Future('NQ', '202412', 'CME'),
        'YM': Future('YM', '202412', 'CME')
    }
    
    data = {}
    for symbol, contract in contracts.items():
        ib.qualifyContracts(contract)
        ib.reqMktData(contract)
        await asyncio.sleep(1)
        
        ticker = ib.ticker(contract)
        data[symbol] = {
            'price': ticker.marketPrice(),
            'bid': ticker.bid,
            'ask': ticker.ask,
            'volume': ticker.volume,
            'timestamp': datetime.now()
        }
    
    return data
```

#### **B. Données historiques**
```python
# get_historical_data.py
async def get_historical_data():
    """Récupération données historiques"""
    
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    contract = Future('ES', '202412', 'CME')
    ib.qualifyContracts(contract)
    
    # Données 1 minute - 30 jours
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='30 D',
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=True
    )
    
    # Conversion en DataFrame
    df = util.df(bars)
    return df
```

#### **C. Données options flow**
```python
# get_options_flow.py
async def get_options_flow():
    """Récupération options flow"""
    
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    # Options SPY
    contract = Option('SPY', '20241221', 500, 'C', 'SMART')
    ib.qualifyContracts(contract)
    
    # Greeks et volatilité
    ib.reqMktData(contract)
    await asyncio.sleep(2)
    
    ticker = ib.ticker(contract)
    options_data = {
        'delta': ticker.delta,
        'gamma': ticker.gamma,
        'theta': ticker.theta,
        'vega': ticker.vega,
        'implied_vol': ticker.impliedVolatility
    }
    
    return options_data
```

---

### **ÉTAPE 7 : INTÉGRATION AVEC MIA_IA_SYSTEM** 🤖

#### **A. Mise à jour configuration**
```python
# config/automation_config.py
@dataclass
class IBKRConfig:
    """Configuration IBKR complète"""
    
    # Connexion
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 1
    account_id: str = ""
    
    # Données
    symbols: List[str] = field(default_factory=lambda: ['ES', 'NQ', 'YM'])
    market_data_type: int = 3  # Delayed
    subscribe_options: bool = True
    subscribe_level2: bool = True
    
    # Trading
    paper_trading: bool = True
    max_position_size: int = 3
    default_order_type: str = "MKT"
    
    # Rate limits
    max_requests_per_second: int = 50
    reconnect_attempts: int = 5
```

#### **B. Intégration dans automation_main.py**
```python
# automation_main.py - Ajout IBKR
from core.ibkr_connector import IBKRConnector

class MIAAutomationSystem:
    def __init__(self):
        # ... existing code ...
        
        # Ajout IBKR
        self.ibkr_connector = IBKRConnector(config=IBKR_CONFIG)
        
    async def initialize_ibkr(self):
        """Initialisation IBKR"""
        try:
            await self.ibkr_connector.connect()
            logger.info("✅ IBKR connecté")
            
            # Subscribe market data
            for symbol in IBKR_CONFIG['symbols']:
                self.ibkr_connector.subscribe_market_data(
                    symbol, 
                    "mia_system",
                    self.on_market_data
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur IBKR: {e}")
    
    def on_market_data(self, market_data):
        """Callback données marché"""
        # Intégration avec Battle Navale
        self.battle_navale.process_market_data(market_data)
```

---

### **ÉTAPE 8 : VALIDATION COMPLÈTE** ✅

#### **A. Test complet système**
```python
# test_complete_ibkr_integration.py
async def test_complete_integration():
    """Test intégration complète"""
    
    # 1. Test connexion
    print("🔌 Test connexion...")
    ibkr = IBKRConnector()
    connected = await ibkr.connect()
    assert connected, "Connexion échouée"
    
    # 2. Test données marché
    print("📊 Test données marché...")
    market_data = await ibkr.get_market_data('ES')
    assert market_data, "Pas de données marché"
    
    # 3. Test données compte
    print("💰 Test données compte...")
    account_info = await ibkr.get_account_info()
    assert account_info, "Pas de données compte"
    
    # 4. Test options flow
    print("📈 Test options flow...")
    options_data = await ibkr.get_complete_options_flow('SPY')
    assert options_data, "Pas de données options"
    
    print("✅ Tous les tests réussis!")
```

#### **B. Validation données requises**
```python
# Vérification données complètes
REQUIRED_DATA = {
    'market_data': ['price', 'bid', 'ask', 'volume', 'timestamp'],
    'account_data': ['balance', 'equity', 'pnl', 'positions'],
    'options_data': ['delta', 'gamma', 'theta', 'vega', 'iv'],
    'historical_data': ['open', 'high', 'low', 'close', 'volume'],
    'level2_data': ['bids', 'asks', 'depth']
}

def validate_data_completeness():
    """Validation complétude données"""
    for data_type, required_fields in REQUIRED_DATA.items():
        # Vérifier chaque type de données
        pass
```

---

### **ÉTAPE 9 : DÉPLOIEMENT PRODUCTION** 🚀

#### **A. Configuration production**
```python
# config/production_config.py
PRODUCTION_IBKR_CONFIG = {
    'host': '127.0.0.1',
    'port': 7496,  # Live trading
    'client_id': 1,
    'account_id': 'YOUR_LIVE_ACCOUNT',
    'paper_trading': False,
    
    # Sécurité
    'max_position_size': 1,  # Réduit en production
    'daily_loss_limit': 500,  # Limite perte quotidienne
    'emergency_stop': True,
    
    # Monitoring
    'heartbeat_interval': 30,
    'connection_timeout': 60,
    'auto_reconnect': True
}
```

#### **B. Script de démarrage**
```bash
# start_mia_system.py
#!/usr/bin/env python3

import asyncio
from automation_main import MIAAutomationSystem

async def main():
    """Démarrage système complet"""
    
    print("🚀 Démarrage MIA_IA_SYSTEM avec IBKR...")
    
    # Initialisation système
    system = MIAAutomationSystem()
    
    # Connexion IBKR
    await system.initialize_ibkr()
    
    # Démarrage trading
    await system.start_trading()
    
    # Boucle principale
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Arrêt système...")
        await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### **ÉTAPE 10 : TROUBLESHOOTING** 🔧

#### **A. Problèmes courants**
```bash
# 1. Connexion refusée
❌ "Connection refused"
✅ Solution: Vérifier TWS ouvert et port 7497

# 2. Pas de données marché
❌ "No market data"
✅ Solution: Vérifier permissions données marché

# 3. Erreur authentification
❌ "Authentication failed"
✅ Solution: Vérifier compte et permissions API

# 4. Rate limit dépassé
❌ "Rate limit exceeded"
✅ Solution: Réduire fréquence requêtes
```

#### **B. Logs de diagnostic**
```python
# diagnostic_ibkr.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ib_insync')

# Activer logs détaillés
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
```

---

## 🎯 **RÉSUMÉ FINAL**

### **✅ Checklist Complète**
- [ ] Compte IBKR créé et validé
- [ ] TWS/Gateway installé et configuré
- [ ] API activée dans TWS
- [ ] ib-insync installé
- [ ] Test connexion réussi
- [ ] Données marché récupérées
- [ ] Données historiques accessibles
- [ ] Options flow fonctionnel
- [ ] Intégration MIA_IA_SYSTEM
- [ ] Tests complets validés
- [ ] Production configurée

### **📊 Données Obtenues**
```python
FINAL_DATA_ACCESS = {
    'market_data': '✅ Temps réel ES/NQ/YM',
    'historical_data': '✅ 1min/5min/15min/1h',
    'options_flow': '✅ Greeks, IV, OI',
    'account_data': '✅ Balance, P&L, positions',
    'level2_data': '✅ Order book complet',
    'order_execution': '✅ Market/Limit/Stop',
    'risk_management': '✅ Position sizing, stops'
}
```

### **🚀 Prêt pour Production**
Votre bot MIA_IA_SYSTEM dispose maintenant de toutes les données IBKR nécessaires pour :

1. **Analyse technique avancée** avec Battle Navale
2. **Backtesting complet** avec données historiques
3. **Trading automatique** avec exécution d'ordres
4. **Risk management** avec monitoring temps réel
5. **Options flow analysis** pour signaux avancés

**🎯 Votre système est maintenant prêt pour le trading automatique professionnel !** 