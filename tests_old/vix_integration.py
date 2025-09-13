#!/usr/bin/env python3
"""
Module d'intégration VIX pour MIA_IA System
"""

from ib_insync import *
import datetime as dt

class VIXManager:
    def __init__(self, ib_connection):
        self.ib = ib_connection
        self.vix_spot = None
        self.vix_futures = {}
        self.vix_options = {}
        
    def get_vix_spot(self):
        """Récupérer le VIX spot temps réel"""
        try:
            vix_idx = Index('VIX', 'CBOE')
            self.ib.qualifyContracts(vix_idx)
            
            # Live d'abord
            self.ib.reqMarketDataType(1)
            tkr_vix = self.ib.reqMktData(vix_idx, '', False)
            for _ in range(20): self.ib.waitOnUpdate(timeout=1.0)
            spot = tkr_vix.last or (tkr_vix.bid and tkr_vix.ask and (tkr_vix.bid + tkr_vix.ask) / 2) or tkr_vix.close

            # Fallback: delayed si toujours None
            if spot is None:
                self.ib.cancelMktData(vix_idx)
                self.ib.reqMarketDataType(3)  # DELAYED
                tkr_vix = self.ib.reqMktData(vix_idx, '', False)
                for _ in range(12): self.ib.waitOnUpdate(timeout=1.0)
                spot = tkr_vix.last or (tkr_vix.bid and tkr_vix.ask and (tkr_vix.bid + tkr_vix.ask) / 2) or tkr_vix.close

            self.vix_spot = spot
            return spot
            
        except Exception as e:
            print(f"❌ Erreur VIX spot: {e}")
            return None
    
    def get_vix_futures(self, num_contracts=4):
        """Récupérer les VIX futures - DÉSACTIVÉ pour ES/NQ trading"""
        print("⚠️ VIX futures désactivé - VIX spot suffit pour ES/NQ")
        return {}
    
    def get_market_sentiment(self):
        """Analyser le sentiment de marché basé sur VIX"""
        vix_spot = self.get_vix_spot()
        
        if vix_spot is None:
            return "UNKNOWN"
        
        if vix_spot < 15:
            return "COMPLACENT"  # Marché calme, risque de correction
        elif vix_spot < 25:
            return "NORMAL"      # Volatilité normale
        elif vix_spot < 35:
            return "STRESSED"    # Marché stressé
        else:
            return "PANIC"       # Panique, opportunités d'achat
    
    def get_hedging_recommendation(self, portfolio_delta, threshold=1000):
        """Recommandation de hedging basée sur VIX et delta du portefeuille"""
        sentiment = self.get_market_sentiment()
        vix_spot = self.get_vix_spot()
        
        if portfolio_delta > threshold:
            if sentiment in ["STRESSED", "PANIC"]:
                return {
                    'action': 'HEDGE_AGGRESSIVE',
                    'vix_futures_size': portfolio_delta * 0.1,  # 10% du delta
                    'reason': f'High delta ({portfolio_delta}) + High VIX ({vix_spot})'
                }
            else:
                return {
                    'action': 'HEDGE_MODERATE',
                    'vix_futures_size': portfolio_delta * 0.05,  # 5% du delta
                    'reason': f'High delta ({portfolio_delta}) + Normal VIX ({vix_spot})'
                }
        else:
            return {
                'action': 'NO_HEDGE',
                'vix_futures_size': 0,
                'reason': f'Low delta ({portfolio_delta})'
            }
    
    def get_position_sizing_adjustment(self, base_size):
        """Ajuster la taille des positions selon VIX"""
        sentiment = self.get_market_sentiment()
        
        adjustments = {
            'COMPLACENT': 1.2,   # +20% (marché calme)
            'NORMAL': 1.0,       # Taille normale
            'STRESSED': 0.7,     # -30% (marché stressé)
            'PANIC': 0.5         # -50% (panique)
        }
        
        return base_size * adjustments.get(sentiment, 1.0)

# Exemple d'utilisation
if __name__ == "__main__":
    # Connexion IBKR
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=7)
    
    # Initialiser VIX Manager
    vix_mgr = VIXManager(ib)
    
    # Tests
    print("=== VIX INTEGRATION TEST ===")
    
    # VIX Spot
    vix_spot = vix_mgr.get_vix_spot()
    print(f"VIX Spot: {vix_spot}")
    
    # Sentiment
    sentiment = vix_mgr.get_market_sentiment()
    print(f"Market Sentiment: {sentiment}")
    
    # VIX Futures
    vix_futures = vix_mgr.get_vix_futures()
    print(f"VIX Futures: {len(vix_futures)} contracts")
    
    # Recommandation hedging
    hedge_rec = vix_mgr.get_hedging_recommendation(1500)
    print(f"Hedging Recommendation: {hedge_rec}")
    
    # Ajustement position sizing
    adj_size = vix_mgr.get_position_sizing_adjustment(100)
    print(f"Position Size Adjustment: {adj_size}")
    
    ib.disconnect()

