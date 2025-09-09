#!/usr/bin/env python3
"""
Position Sizing basé sur VIX pour MIA_IA System
"""

class VIXPositionSizer:
    def __init__(self, vix_manager):
        self.vix_mgr = vix_manager
        
    def calculate_position_size(self, base_size, instrument_type="ES"):
        """
        Ajuster la taille des positions selon VIX
        
        Args:
            base_size: Taille de base de la position
            instrument_type: Type d'instrument (ES, SPX, etc.)
        """
        vix_spot = self.vix_mgr.get_vix_spot()
        sentiment = self.vix_mgr.get_market_sentiment()
        
        # Multiplicateurs selon le sentiment VIX
        vix_multipliers = {
            'COMPLACENT': {
                'ES': 1.3,    # +30% (marché calme, plus d'opportunités)
                'SPX': 1.2,   # +20% (options plus chères)
                'VIX': 0.8    # -20% (VIX bas, moins d'opportunités)
            },
            'NORMAL': {
                'ES': 1.0,    # Taille normale
                'SPX': 1.0,
                'VIX': 1.0
            },
            'STRESSED': {
                'ES': 0.6,    # -40% (marché stressé)
                'SPX': 0.7,   # -30% (options plus chères)
                'VIX': 1.4    # +40% (opportunités VIX)
            },
            'PANIC': {
                'ES': 0.3,    # -70% (panique, très risqué)
                'SPX': 0.4,   # -60% (options très chères)
                'VIX': 2.0    # +100% (excellentes opportunités)
            }
        }
        
        multiplier = vix_multipliers.get(sentiment, {}).get(instrument_type, 1.0)
        adjusted_size = base_size * multiplier
        
        return {
            'original_size': base_size,
            'adjusted_size': adjusted_size,
            'vix_spot': vix_spot,
            'sentiment': sentiment,
            'multiplier': multiplier,
            'reason': f"VIX {vix_spot} → {sentiment} → {multiplier}x"
        }
    
    def get_risk_adjustment(self, portfolio_value, max_risk_pct=0.02):
        """
        Ajuster le risque maximum selon VIX
        """
        vix_spot = self.vix_mgr.get_vix_spot()
        
        # Ajuster le risque selon VIX
        if vix_spot < 15:
            risk_multiplier = 1.5  # Plus de risque en marché calme
        elif vix_spot < 25:
            risk_multiplier = 1.0  # Risque normal
        elif vix_spot < 35:
            risk_multiplier = 0.6  # Moins de risque en marché stressé
        else:
            risk_multiplier = 0.3  # Très peu de risque en panique
        
        adjusted_risk = max_risk_pct * risk_multiplier
        
        return {
            'original_risk_pct': max_risk_pct,
            'adjusted_risk_pct': adjusted_risk,
            'vix_spot': vix_spot,
            'risk_multiplier': risk_multiplier,
            'max_dollar_risk': portfolio_value * adjusted_risk
        }

# Exemple d'utilisation
if __name__ == "__main__":
    from vix_integration import VIXManager
    from ib_insync import IB
    
    # Connexion
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=7)
    
    # Initialiser
    vix_mgr = VIXManager(ib)
    position_sizer = VIXPositionSizer(vix_mgr)
    
    # Tests
    print("=== VIX POSITION SIZING TEST ===")
    
    # Position sizing pour ES
    es_sizing = position_sizer.calculate_position_size(100, "ES")
    print(f"ES Position Sizing: {es_sizing}")
    
    # Position sizing pour SPX
    spx_sizing = position_sizer.calculate_position_size(50, "SPX")
    print(f"SPX Position Sizing: {spx_sizing}")
    
    # Risk adjustment
    risk_adj = position_sizer.get_risk_adjustment(100000)
    print(f"Risk Adjustment: {risk_adj}")
    
    ib.disconnect()




