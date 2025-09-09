#!/usr/bin/env python3
"""
Simulateur de données ES (E-mini S&P 500)
Pour continuer le développement sans authentification IBKR
Version corrigée - Pas d'imports ML
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class ESDataSimulator:
    """Simulateur de données ES pour le développement"""
    
    def __init__(self):
        # Prix de base ES (approximatif)
        self.base_price = 4500.0
        self.current_price = self.base_price
        self.volume = 0
        
        # Paramètres de simulation
        self.volatility = 0.002  # 0.2% de volatilité
        self.tick_size = 0.25    # Tick size ES
        self.volume_base = 1000  # Volume de base
        
        # Historique
        self.price_history = []
        self.volume_history = []
        
    def generate_ohlc(self) -> Dict[str, Any]:
        """Générer des données OHLC simulées"""
        # Simuler un mouvement de prix
        change = random.gauss(0, self.volatility)
        self.current_price += change * self.current_price
        
        # Arrondir au tick size
        self.current_price = round(self.current_price / self.tick_size) * self.tick_size
        
        # Générer OHLC pour la barre actuelle
        high = self.current_price + random.uniform(0, 5) * self.tick_size
        low = self.current_price - random.uniform(0, 5) * self.tick_size
        open_price = self.current_price + random.uniform(-2, 2) * self.tick_size
        close_price = self.current_price
        
        # Volume
        self.volume = int(self.volume_base + random.uniform(-200, 200))
        
        # Timestamp
        timestamp = datetime.now()
        
        ohlc_data = {
            "symbol": "ES",
            "exchange": "CME",
            "timestamp": timestamp.isoformat(),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close_price, 2),
            "volume": self.volume,
            "tick_size": self.tick_size,
            "contract_size": 50
        }
        
        # Ajouter à l'historique
        self.price_history.append(ohlc_data)
        if len(self.price_history) > 1000:  # Garder seulement 1000 barres
            self.price_history.pop(0)
            
        return ohlc_data
    
    def get_market_data(self) -> Dict[str, Any]:
        """Obtenir les données de marché actuelles"""
        ohlc = self.generate_ohlc()
        
        # Simuler des données de marché en temps réel
        bid = ohlc["close"] - random.uniform(0, 2) * self.tick_size
        ask = ohlc["close"] + random.uniform(0, 2) * self.tick_size
        
        market_data = {
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
        
        return market_data
    
    def get_historical_data(self, bars: int = 100) -> List[Dict[str, Any]]:
        """Obtenir l'historique des données"""
        if len(self.price_history) < bars:
            # Générer plus de données si nécessaire
            for _ in range(bars - len(self.price_history)):
                self.generate_ohlc()
        
        return self.price_history[-bars:]
    
    def get_volume_profile(self) -> Dict[str, Any]:
        """Obtenir le profil de volume"""
        if not self.volume_history:
            return {"volume": 0, "avg_volume": 0}
        
        return {
            "current_volume": self.volume,
            "avg_volume": sum(self.volume_history) / len(self.volume_history),
            "max_volume": max(self.volume_history),
            "min_volume": min(self.volume_history)
        }

def simulate_es_streaming(duration: int = 60):
    """Simuler un flux de données ES en temps réel"""
    print("=== SIMULATION DONNÉES ES EN TEMPS RÉEL ===")
    print(f"Durée: {duration} secondes")
    print("Format: [Timestamp] ES - Last: $X.XX | Bid: $X.XX | Ask: $X.XX | Volume: XXXX")
    print()
    
    simulator = ESDataSimulator()
    
    start_time = time.time()
    while time.time() - start_time < duration:
        data = simulator.get_market_data()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ES - Last: ${data['last']:.2f} | Bid: ${data['bid']:.2f} | Ask: ${data['ask']:.2f} | Volume: {data['volume']}")
        
        time.sleep(1)  # Mise à jour chaque seconde
    
    print("\n✅ Simulation terminée")

def test_simulator():
    """Tester le simulateur"""
    print("=== TEST SIMULATEUR DONNÉES ES ===")
    
    simulator = ESDataSimulator()
    
    # Test 1: Données OHLC
    print("📊 Test 1: Données OHLC")
    ohlc = simulator.generate_ohlc()
    print(json.dumps(ohlc, indent=2))
    
    print()
    
    # Test 2: Données de marché
    print("📈 Test 2: Données de marché")
    market_data = simulator.get_market_data()
    print(json.dumps(market_data, indent=2))
    
    print()
    
    # Test 3: Historique
    print("📋 Test 3: Historique (5 barres)")
    history = simulator.get_historical_data(5)
    for i, bar in enumerate(history):
        print(f"Barre {i+1}: O:{bar['open']:.2f} H:{bar['high']:.2f} L:{bar['low']:.2f} C:{bar['close']:.2f} V:{bar['volume']}")
    
    print()
    
    # Test 4: Streaming (5 secondes)
    print("🔄 Test 4: Streaming (5 secondes)")
    simulate_es_streaming(5)

if __name__ == "__main__":
    test_simulator()
