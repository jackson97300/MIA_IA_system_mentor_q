#!/usr/bin/env python3
"""
🔧 SIERRA CHART TRADING PORTS CONFIGURATION
============================================

Configuration des ports DTC pour trading via Sierra Chart
Basé sur la documentation : docs/sierra_chart/CONFIGURATION_DTC_SIERRA_CHART_MIA.md
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class SierraTradingConfig:
    """Configuration des ports de trading Sierra Chart"""
    
    # === PORTS DTC ===
    
    # Instance ES (E-mini S&P 500)
    es_dtc_port: int = 11099
    es_historical_port: int = 11098
    es_symbol: str = "ESU25_FUT_CME"  # Ajuster selon le contrat actuel
    
    # Instance NQ (E-mini NASDAQ)
    nq_dtc_port: int = 11100
    nq_historical_port: int = 11097
    nq_symbol: str = "NQU25_FUT_CME"  # Ajuster selon le contrat actuel
    
    # === CONFIGURATION GÉNÉRALE ===
    
    host: str = "127.0.0.1"
    enable_trading: bool = True
    require_authentication: bool = False
    
    # === MÉTHODES UTILITAIRES ===
    
    def get_es_config(self) -> Dict[str, Any]:
        """Retourne la configuration ES"""
        return {
            "host": self.host,
            "dtc_port": self.es_dtc_port,
            "historical_port": self.es_historical_port,
            "symbol": self.es_symbol,
            "description": "E-mini S&P 500 Futures"
        }
    
    def get_nq_config(self) -> Dict[str, Any]:
        """Retourne la configuration NQ"""
        return {
            "host": self.host,
            "dtc_port": self.nq_dtc_port,
            "historical_port": self.nq_historical_port,
            "symbol": self.nq_symbol,
            "description": "E-mini NASDAQ Futures"
        }
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Retourne toutes les configurations"""
        return {
            "ES_INSTANCE": self.get_es_config(),
            "NQ_INSTANCE": self.get_nq_config()
        }
    
    def get_port_by_symbol(self, symbol: str) -> int:
        """Retourne le port DTC pour un symbole donné"""
        if "ES" in symbol.upper():
            return self.es_dtc_port
        elif "NQ" in symbol.upper():
            return self.nq_dtc_port
        else:
            raise ValueError(f"Symbole non supporté: {symbol}")
    
    def get_symbol_by_port(self, port: int) -> str:
        """Retourne le symbole pour un port donné"""
        if port == self.es_dtc_port:
            return self.es_symbol
        elif port == self.nq_dtc_port:
            return self.nq_symbol
        else:
            raise ValueError(f"Port non supporté: {port}")
    
    def get_current_symbols(self) -> Dict[str, str]:
        """Retourne les symboles actuels avec auto-roll appliqué"""
        return {
            "ES": roll_symbol(self.es_symbol),
            "NQ": roll_symbol(self.nq_symbol)
        }

# === INSTANCE GLOBALE ===

sierra_trading_config = SierraTradingConfig()

def get_sierra_trading_config() -> SierraTradingConfig:
    """Retourne la configuration de trading Sierra Chart"""
    return sierra_trading_config

# === CONFIGURATION POUR TESTS ===

test_sierra_trading_config = SierraTradingConfig(
    es_dtc_port=12099,  # Ports différents pour les tests
    nq_dtc_port=12100,
    es_historical_port=12098,
    nq_historical_port=12097
)

def get_test_sierra_trading_config() -> SierraTradingConfig:
    """Retourne la configuration de test"""
    return test_sierra_trading_config

# === AUTO-ROLL HELPER ===

CONTRACT_MONTHS = ("H", "M", "U", "Z")  # Mar, Jun, Sep, Dec

def next_contract(letter: str) -> str:
    """Retourne le mois de contrat suivant"""
    if letter not in CONTRACT_MONTHS:
        return letter
    idx = CONTRACT_MONTHS.index(letter)
    return CONTRACT_MONTHS[(idx + 1) % 4]

def roll_symbol(symbol: str, now: datetime = None) -> str:
    """
    Auto-roll des symboles de contrats.
    
    Ex: ESU25_FUT_CME -> ESZ25_FUT_CME si on approche le rollover.
    
    TODO: Implémenter ta propre règle de rollover:
    - Date SPAN (2e jeudi du mois)
    - Volume/OI basé
    - Date fixe
    """
    if now is None:
        now = datetime.now()
    
    # Placeholder: conserve le symbole tel quel
    # TODO: Ajouter la logique de rollover ici
    return symbol

def get_contract_month(symbol: str) -> str:
    """Extrait le mois de contrat d'un symbole (ex: ESU25 -> U)"""
    if len(symbol) >= 4:
        return symbol[2]  # 3ème caractère = mois
    return "U"  # Default

def get_contract_year(symbol: str) -> str:
    """Extrait l'année de contrat d'un symbole (ex: ESU25 -> 25)"""
    if len(symbol) >= 5:
        return symbol[3:5]  # 4ème et 5ème caractères = année
    return "25"  # Default

# === VÉRIFICATIONS ===

def validate_sierra_config() -> Dict[str, bool]:
    """Valide la configuration Sierra Chart"""
    config = sierra_trading_config
    
    return {
        "es_port_valid": 10000 <= config.es_dtc_port <= 65535,
        "nq_port_valid": 10000 <= config.nq_dtc_port <= 65535,
        "es_historical_port_valid": 10000 <= config.es_historical_port <= 65535,
        "nq_historical_port_valid": 10000 <= config.nq_historical_port <= 65535,
        "ports_different": config.es_dtc_port != config.nq_dtc_port,
        "symbols_valid": "ES" in config.es_symbol and "NQ" in config.nq_symbol
    }

if __name__ == "__main__":
    # Test de la configuration
    config = get_sierra_trading_config()
    
    print("🔧 Configuration Sierra Chart Trading:")
    print(f"ES: {config.es_symbol} -> Port {config.es_dtc_port}")
    print(f"NQ: {config.nq_symbol} -> Port {config.nq_dtc_port}")
    
    print("\n✅ Validation:")
    validation = validate_sierra_config()
    for key, value in validation.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
