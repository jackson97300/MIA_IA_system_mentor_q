#!/usr/bin/env python3
"""
Connecteur IBKR simulé pour le développement
Remplace temporairement IBKR pendant la réparation du téléphone
Version corrigée - Pas d'imports ML
"""

import time
import json
import asyncio
from datetime import datetime

# Import direct du simulateur sans passer par les modules ML
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import direct du simulateur
try:
    from es_data_simulator import ESDataSimulator
except ImportError:
    # Si l'import direct échoue, on définit une classe simple
    class ESDataSimulator:
        def __init__(self):
            self.base_price = 4500.0
            self.current_price = self.base_price
            self.volume = 1000
            self.volatility = 0.002
            self.tick_size = 0.25
            self.price_history = []
            
        def generate_ohlc(self):
            import random
            change = random.gauss(0, self.volatility)
            self.current_price += change * self.current_price
            self.current_price = round(self.current_price / self.tick_size) * self.tick_size
            
            high = self.current_price + random.uniform(0, 5) * self.tick_size
            low = self.current_price - random.uniform(0, 5) * self.tick_size
            open_price = self.current_price + random.uniform(-2, 2) * self.tick_size
            close_price = self.current_price
            self.volume = int(1000 + random.uniform(-200, 200))
            
            return {
                "symbol": "ES",
                "exchange": "CME",
                "timestamp": datetime.now().isoformat(),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close_price, 2),
                "volume": self.volume,
                "tick_size": self.tick_size,
                "contract_size": 50
            }
            
        def get_market_data(self):
            ohlc = self.generate_ohlc()
            import random
            bid = ohlc["close"] - random.uniform(0, 2) * self.tick_size
            ask = ohlc["close"] + random.uniform(0, 2) * self.tick_size
            
            return {
                "symbol": "ES",
                "last": ohlc["close"],
                "bid": round(bid, 2),
                "ask": round(ask, 2),
                "high": ohlc["high"],
                "low": ohlc["low"],
                "volume": ohlc["volume"],
                "timestamp": ohlc["timestamp"],
                "change": round(ohlc["close"] - self.base_price, 2),
                "change_percent": round((ohlc["close"] - self.base_price) / self.base_price * 100, 2)
            }
            
        def get_historical_data(self, bars=100):
            return [self.generate_ohlc() for _ in range(bars)]
            
        def get_volume_profile(self):
            return {
                "current_volume": self.volume,
                "avg_volume": 1000,
                "max_volume": 1200,
                "min_volume": 800
            }

class SimulatedIBKRConnector:
    """Connecteur IBKR simulé pour le développement"""
    
    def __init__(self):
        self.simulator = ESDataSimulator()
        self.connected = False
        self.authenticated = False
        self.accounts = ["DU1234567"]  # Compte simulé
        self.positions = []
        
    async def connect(self) -> bool:
        """Simuler la connexion async"""
        print("🔌 Connexion simulée au Gateway IBKR...")
        await asyncio.sleep(0.1)  # Simuler le délai de connexion
        self.connected = True
        print("✅ Connexion simulée réussie")
        return True
    
    async def authenticate(self) -> bool:
        """Simuler l'authentification async"""
        print("🔐 Authentification simulée...")
        await asyncio.sleep(0.1)
        self.authenticated = True
        print("✅ Authentification simulée réussie")
        return True
    
    async def disconnect(self):
        """Simuler la déconnexion async"""
        self.connected = False
        self.authenticated = False
        print("🔌 Déconnexion simulée")
    
    async def get_accounts(self) -> list:
        """Obtenir les comptes simulés async"""
        await asyncio.sleep(0.05)
        return self.accounts
    
    async def get_positions(self) -> list:
        """Obtenir les positions simulées async"""
        await asyncio.sleep(0.05)
        return self.positions
    
    async def get_market_data(self, symbol: str = "ES") -> dict:
        """Obtenir les données de marché simulées async"""
        await asyncio.sleep(0.05)
        if symbol.upper() == "ES":
            return self.simulator.get_market_data()
        else:
            return {"error": f"Symbole {symbol} non supporté"}
    
    async def get_historical_data(self, symbol: str = "ES", bars: int = 100) -> list:
        """Obtenir l'historique simulé async"""
        await asyncio.sleep(0.05)
        if symbol.upper() == "ES":
            return self.simulator.get_historical_data(bars)
        else:
            return []
    
    async def get_ohlc_data(self, symbol: str = "ES") -> dict:
        """Obtenir les données OHLC simulées async"""
        await asyncio.sleep(0.05)
        if symbol.upper() == "ES":
            return self.simulator.generate_ohlc()
        else:
            return {"error": f"Symbole {symbol} non supporté"}
    
    async def get_volume_data(self, symbol: str = "ES") -> dict:
        """Obtenir les données de volume simulées async"""
        await asyncio.sleep(0.05)
        if symbol.upper() == "ES":
            return self.simulator.get_volume_profile()
        else:
            return {"error": f"Symbole {symbol} non supporté"}
    
    async def get_streaming_data(self, symbol: str = "ES") -> dict:
        """Obtenir les données streaming simulées async"""
        await asyncio.sleep(0.05)
        if symbol.upper() == "ES":
            return self.simulator.get_market_data()
        else:
            return {"error": f"Symbole {symbol} non supporté"}
    
    # Méthodes synchrones pour compatibilité
    def connect_sync(self) -> bool:
        """Simuler la connexion sync"""
        print("🔌 Connexion simulée au Gateway IBKR...")
        time.sleep(0.1)
        self.connected = True
        print("✅ Connexion simulée réussie")
        return True
    
    def authenticate_sync(self) -> bool:
        """Simuler l'authentification sync"""
        print("🔐 Authentification simulée...")
        time.sleep(0.1)
        self.authenticated = True
        print("✅ Authentification simulée réussie")
        return True
    
    def disconnect_sync(self):
        """Simuler la déconnexion sync"""
        self.connected = False
        self.authenticated = False
        print("🔌 Déconnexion simulée")
    
    def get_accounts_sync(self) -> list:
        """Obtenir les comptes simulés sync"""
        return self.accounts
    
    def get_positions_sync(self) -> list:
        """Obtenir les positions simulées sync"""
        return self.positions
    
    def get_market_data_sync(self, symbol: str = "ES") -> dict:
        """Obtenir les données de marché simulées sync"""
        if symbol.upper() == "ES":
            return self.simulator.get_market_data()
        else:
            return {"error": f"Symbole {symbol} non supporté"}
    
    def get_historical_data_sync(self, symbol: str = "ES", bars: int = 100) -> list:
        """Obtenir l'historique simulé sync"""
        if symbol.upper() == "ES":
            return self.simulator.get_historical_data(bars)
        else:
            return []
    
    def get_ohlc_sync(self, symbol: str = "ES") -> dict:
        """Obtenir les données OHLC simulées sync"""
        if symbol.upper() == "ES":
            return self.simulator.generate_ohlc()
        else:
            return {"error": f"Symbole {symbol} non supporté"}
    
    def get_volume_sync(self, symbol: str = "ES") -> dict:
        """Obtenir les données de volume simulées sync"""
        if symbol.upper() == "ES":
            return self.simulator.get_volume_profile()
        else:
            return {"error": f"Symbole {symbol} non supporté"}

async def test_simulated_connector():
    """Tester le connecteur simulé async"""
    print("=== TEST CONNECTEUR IBKR SIMULÉ ASYNC ===")
    
    connector = SimulatedIBKRConnector()
    
    # Test 1: Connexion
    print("🔌 Test 1: Connexion")
    if await connector.connect():
        print("✅ Connexion OK")
    
    print()
    
    # Test 2: Authentification
    print("🔐 Test 2: Authentification")
    if await connector.authenticate():
        print("✅ Authentification OK")
    
    print()
    
    # Test 3: Comptes
    print("💰 Test 3: Comptes")
    accounts = await connector.get_accounts()
    print(f"Comptes: {accounts}")
    
    print()
    
    # Test 4: Données ES
    print("📊 Test 4: Données ES")
    market_data = await connector.get_market_data("ES")
    print("Données de marché:")
    print(json.dumps(market_data, indent=2))
    
    print()
    
    # Test 5: OHLC
    print("📈 Test 5: Données OHLC")
    ohlc = await connector.get_ohlc_data("ES")
    print("Données OHLC:")
    print(json.dumps(ohlc, indent=2))
    
    print()
    
    # Test 6: Volume
    print("📊 Test 6: Données Volume")
    volume = await connector.get_volume_data("ES")
    print("Données Volume:")
    print(json.dumps(volume, indent=2))
    
    print()
    
    # Test 7: Historique
    print("📋 Test 7: Historique (5 barres)")
    history = await connector.get_historical_data("ES", 5)
    for i, bar in enumerate(history):
        print(f"Barre {i+1}: O:{bar['open']:.2f} H:{bar['high']:.2f} L:{bar['low']:.2f} C:{bar['close']:.2f} V:{bar['volume']}")
    
    print()
    
    # Test 8: Streaming simulé
    print("🔄 Test 8: Streaming simulé (5 secondes)")
    start_time = time.time()
    while time.time() - start_time < 5:
        data = await connector.get_streaming_data("ES")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ES - Last: ${data['last']:.2f} | Volume: {data['volume']}")
        await asyncio.sleep(1)
    
    print()
    print("🎉 Test connecteur simulé terminé !")
    
    # Déconnexion
    await connector.disconnect()

def test_simulated_connector_sync():
    """Tester le connecteur simulé sync"""
    print("=== TEST CONNECTEUR IBKR SIMULÉ SYNC ===")
    
    connector = SimulatedIBKRConnector()
    
    # Test 1: Connexion
    print("🔌 Test 1: Connexion")
    if connector.connect_sync():
        print("✅ Connexion OK")
    
    print()
    
    # Test 2: Authentification
    print("🔐 Test 2: Authentification")
    if connector.authenticate_sync():
        print("✅ Authentification OK")
    
    print()
    
    # Test 3: Comptes
    print("💰 Test 3: Comptes")
    accounts = connector.get_accounts_sync()
    print(f"Comptes: {accounts}")
    
    print()
    
    # Test 4: Données ES
    print("📊 Test 4: Données ES")
    market_data = connector.get_market_data_sync("ES")
    print("Données de marché:")
    print(json.dumps(market_data, indent=2))
    
    print()
    
    # Test 5: OHLC
    print("📈 Test 5: Données OHLC")
    ohlc = connector.get_ohlc_sync("ES")
    print("Données OHLC:")
    print(json.dumps(ohlc, indent=2))
    
    print()
    
    # Test 6: Volume
    print("📊 Test 6: Données Volume")
    volume = connector.get_volume_sync("ES")
    print("Données Volume:")
    print(json.dumps(volume, indent=2))
    
    print()
    
    # Test 7: Historique
    print("📋 Test 7: Historique (5 barres)")
    history = connector.get_historical_data_sync("ES", 5)
    for i, bar in enumerate(history):
        print(f"Barre {i+1}: O:{bar['open']:.2f} H:{bar['high']:.2f} L:{bar['low']:.2f} C:{bar['close']:.2f} V:{bar['volume']}")
    
    print()
    
    # Test 8: Streaming simulé
    print("🔄 Test 8: Streaming simulé (5 secondes)")
    start_time = time.time()
    while time.time() - start_time < 5:
        data = connector.get_market_data_sync("ES")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ES - Last: ${data['last']:.2f} | Volume: {data['volume']}")
        time.sleep(1)
    
    print()
    print("🎉 Test connecteur simulé terminé !")
    
    # Déconnexion
    connector.disconnect_sync()

if __name__ == "__main__":
    # Test async
    asyncio.run(test_simulated_connector())
    
    print("\n" + "="*50 + "\n")
    
    # Test sync
    test_simulated_connector_sync()
