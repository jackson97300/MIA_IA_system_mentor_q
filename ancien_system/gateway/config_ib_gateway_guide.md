# 🎯 GUIDE CONFIGURATION IB GATEWAY - MIA_IA_SYSTEM

**Version: 1.0.0 - Configuration IB Gateway 2025**  
**Date**: Août 2025  
**Status**: ✅ GUIDE SPÉCIFIQUE IB GATEWAY

---

## 🏆 **CONFIGURATION IB GATEWAY**

### **ÉTAPE 1 : CONFIGURATION IB GATEWAY** ⚙️

#### **A. Paramètres de connexion**
```bash
# Configuration IB Gateway
Host: 127.0.0.1
Port: 4001 (ou 4002 pour second client)
Client ID: 1
Timeout: 30 secondes
```

#### **B. Configuration dans IB Gateway**
```bash
# Dans IB Gateway :
1. File → Global Configuration
2. API → Settings
3. ✅ Enable ActiveX and Socket Clients
4. Socket port: 4001
5. ✅ Download open orders on connection
6. ✅ Create API order log file

# API → Precautions
✅ Bypass Order Precautions for API Orders
✅ Allow connections from localhost
```

---

### **ÉTAPE 2 : SCRIPT DE TEST** 🔌

#### **A. Test de connexion**
```python
# test_ib_gateway.py
#!/usr/bin/env python3

from ib_insync import *
import asyncio

async def test_ib_gateway():
    """Test connexion IB Gateway"""
    
    # Configuration
    ib = IB()
    
    try:
        # Connexion IB Gateway
        print("🔌 Connexion IB Gateway...")
        ib.connect('127.0.0.1', 4001, clientId=1)
        
        # Attendre connexion
        await asyncio.sleep(3)
        
        if ib.isConnected():
            print("✅ Connexion réussie!")
            
            # Test données compte
            account = ib.accountSummary()
            print(f"✅ Compte: {len(account)} éléments")
            
            # Test données marché
            contract = Future('ES', '202412', 'CME')
            ib.qualifyContracts(contract)
            ib.reqMktData(contract)
            await asyncio.sleep(2)
            
            ticker = ib.ticker(contract)
            if ticker.marketPrice():
                print(f"✅ Prix ES: {ticker.marketPrice()}")
            else:
                print("⚠️ Pas de données marché")
                
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()

if __name__ == "__main__":
    asyncio.run(test_ib_gateway())
```

#### **B. Exécution du test**
```bash
# Lancer le test
python test_ib_gateway.py

# Résultats attendus
✅ Connexion réussie!
✅ Compte: [nombre] éléments
✅ Prix ES: [prix actuel]
```

---

### **ÉTAPE 3 : CONFIGURATION MIA_IA_SYSTEM** 🤖

#### **A. Mise à jour configuration**
```python
# config/ibkr_config.py
IB_GATEWAY_CONFIG = {
    # Connexion IB Gateway
    'host': '127.0.0.1',
    'port': 4001,  # Port IB Gateway
    'client_id': 1,
    'timeout': 30,
    
    # Compte simulé avec données réelles
    'paper_trading': True,
    'real_market_data': True,
    
    # Données
    'symbols': ['ES', 'NQ', 'YM'],
    'market_data_type': 1,  # Live data
    'subscribe_positions': True,
    'subscribe_orders': True,
    
    # Rate limits
    'max_requests_per_second': 50,
    'reconnect_attempts': 5
}
```

#### **B. Intégration dans automation_main.py**
```python
# automation_main.py - Ajout IB Gateway
from core.ibkr_connector import IBKRConnector

class MIAAutomationSystem:
    def __init__(self):
        # ... existing code ...
        
        # Configuration IB Gateway
        self.ibkr_config = IB_GATEWAY_CONFIG
        self.ibkr_connector = IBKRConnector(config=self.ibkr_config)
        
    async def initialize_ib_gateway(self):
        """Initialisation IB Gateway"""
        try:
            await self.ibkr_connector.connect()
            logger.info("✅ IB Gateway connecté")
            
            # Subscribe market data
            for symbol in self.ibkr_config['symbols']:
                self.ibkr_connector.subscribe_market_data(
                    symbol, 
                    "mia_system",
                    self.on_market_data
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur IB Gateway: {e}")
    
    def on_market_data(self, market_data):
        """Callback données marché"""
        # Intégration avec Battle Navale
        self.battle_navale.process_market_data(market_data)
```

---

### **ÉTAPE 4 : VALIDATION DONNÉES** 📊

#### **A. Test données complètes**
```python
# test_data_complete.py
async def test_complete_data():
    """Test données complètes IB Gateway"""
    
    ib = IB()
    ib.connect('127.0.0.1', 4001, clientId=1)
    
    try:
        # 1. Données compte
        account = ib.accountSummary()
        print(f"✅ Compte: {len(account)} éléments")
        
        # 2. Données marché ES
        contract = Future('ES', '202412', 'CME')
        ib.qualifyContracts(contract)
        ib.reqMktData(contract)
        await asyncio.sleep(2)
        
        ticker = ib.ticker(contract)
        print(f"✅ ES - Prix: {ticker.marketPrice()}")
        print(f"   Bid: {ticker.bid} | Ask: {ticker.ask}")
        
        # 3. Données historiques
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True
        )
        print(f"✅ Historique: {len(bars)} barres")
        
        # 4. Options flow (si disponible)
        try:
            spy_contract = Option('SPY', '20241221', 500, 'C', 'SMART')
            ib.qualifyContracts(spy_contract)
            ib.reqMktData(spy_contract)
            await asyncio.sleep(2)
            
            spy_ticker = ib.ticker(spy_contract)
            if spy_ticker.delta:
                print(f"✅ Options - Delta: {spy_ticker.delta}")
        except:
            print("⚠️ Options non disponibles")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        ib.disconnect()
```

---

### **ÉTAPE 5 : TROUBLESHOOTING IB GATEWAY** 🔧

#### **A. Problèmes courants**
```bash
# 1. Port 4001 fermé
❌ "Connection refused on port 4001"
✅ Solution: Vérifier IB Gateway ouvert et port configuré

# 2. Pas de données marché
❌ "No market data"
✅ Solution: Vérifier permissions données marché dans compte

# 3. Erreur authentification
❌ "Authentication failed"
✅ Solution: Vérifier login IB Gateway

# 4. Timeout connexion
❌ "Connection timeout"
✅ Solution: Augmenter timeout à 60 secondes
```

#### **B. Logs de diagnostic**
```python
# diagnostic_ib_gateway.py
import logging

# Activer logs détaillés
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ib_insync')

# Test avec logs
ib = IB()
ib.connect('127.0.0.1', 4001, clientId=1)
```

---

### **ÉTAPE 6 : DÉMARRAGE SYSTÈME** 🚀

#### **A. Script de démarrage complet**
```python
# start_mia_ib_gateway.py
#!/usr/bin/env python3

import asyncio
from automation_main import MIAAutomationSystem

async def main():
    """Démarrage MIA_IA_SYSTEM avec IB Gateway"""
    
    print("🚀 Démarrage MIA_IA_SYSTEM avec IB Gateway...")
    
    # Initialisation système
    system = MIAAutomationSystem()
    
    # Connexion IB Gateway
    await system.initialize_ib_gateway()
    
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

## 🎯 **RÉSUMÉ CONFIGURATION**

### **✅ Configuration IB Gateway**
- [ ] IB Gateway ouvert et connecté
- [ ] Port 4001 configuré
- [ ] API activée dans IB Gateway
- [ ] Test connexion réussi
- [ ] Données marché accessibles
- [ ] Intégration MIA_IA_SYSTEM

### **📊 Données Disponibles**
```python
IB_GATEWAY_DATA = {
    'market_data': '✅ Temps réel ES/NQ/YM',
    'historical_data': '✅ 1min/5min/15min/1h',
    'account_data': '✅ Balance, P&L, positions',
    'paper_trading': '✅ Simulation avec données réelles',
    'order_execution': '✅ Market/Limit/Stop'
}
```

### **🚀 Prêt pour Trading**
Votre bot MIA_IA_SYSTEM est maintenant configuré avec IB Gateway pour :

1. **Trading simulé** avec données réelles
2. **Backtesting** avec données historiques
3. **Risk management** avec monitoring temps réel
4. **Battle Navale** avec signaux avancés

**🎯 Votre système est prêt pour le trading automatique avec IB Gateway !** 