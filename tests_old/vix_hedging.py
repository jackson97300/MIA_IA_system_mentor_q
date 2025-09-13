#!/usr/bin/env python3
"""
Hedging automatique basé sur VIX pour MIA_IA System
"""

class VIXHedging:
    def __init__(self, vix_manager, ib_connection):
        self.vix_mgr = vix_manager
        self.ib = ib_connection
        self.current_hedge = None
        
    def calculate_hedge_needs(self, portfolio_positions):
        """
        Calculer les besoins de hedging selon VIX et positions
        
        Args:
            portfolio_positions: Dict des positions actuelles
        """
        vix_spot = self.vix_mgr.get_vix_spot()
        sentiment = self.vix_mgr.get_market_sentiment()
        
        # Calculer le delta total du portefeuille
        total_delta = 0
        for symbol, pos in portfolio_positions.items():
            if symbol == 'ES':
                total_delta += pos['quantity'] * 50  # Multiplicateur ES
            elif symbol == 'SPX':
                total_delta += pos['quantity'] * pos.get('delta', 0)
        
        # Déterminer si hedging nécessaire
        hedge_thresholds = {
            'COMPLACENT': 2000,  # Seuil plus élevé en marché calme
            'NORMAL': 1500,      # Seuil normal
            'STRESSED': 800,     # Seuil plus bas en marché stressé
            'PANIC': 500         # Seuil très bas en panique
        }
        
        threshold = hedge_thresholds.get(sentiment, 1500)
        needs_hedge = abs(total_delta) > threshold
        
        return {
            'total_delta': total_delta,
            'vix_spot': vix_spot,
            'sentiment': sentiment,
            'threshold': threshold,
            'needs_hedge': needs_hedge,
            'hedge_size': abs(total_delta) * 0.1 if needs_hedge else 0
        }
    
    def get_optimal_hedge_instrument(self, hedge_size, hedge_type="POSITION_REDUCTION"):
        """
        Choisir le meilleur instrument de hedging - OPTIMISÉ POUR ES/NQ
        """
        if hedge_type == "POSITION_REDUCTION":
            # Hedging par réduction de position (plus simple)
            return {
                'instrument': 'POSITION_REDUCTION',
                'action': 'REDUCE_POSITIONS',
                'reduction_pct': 0.5,  # -50% positions
                'reason': 'VIX élevé - réduction exposure'
            }
        
        elif hedge_type == "STOP_TIGHTENING":
            # Serrer les stops
            return {
                'instrument': 'STOP_TIGHTENING',
                'action': 'TIGHTEN_STOPS',
                'stop_multiplier': 0.7,  # Stops 30% plus serrés
                'reason': 'VIX élevé - protection capital'
            }
        
        elif hedge_type == "PAUSE_TRADING":
            # Pause trading
            return {
                'instrument': 'PAUSE_TRADING',
                'action': 'PAUSE_UNTIL_VIX_NORMAL',
                'resume_threshold': 20.0,  # Reprendre si VIX < 20
                'reason': 'VIX très élevé - attendre calme'
            }
    
    def execute_hedge(self, hedge_info):
        """
        Exécuter l'ordre de hedging
        """
        if not hedge_info or not hedge_info.get('contract'):
            print("❌ Pas d'instrument de hedging disponible")
            return False
        
        try:
            contract = hedge_info['contract']
            size = hedge_info['size']
            
            # Créer l'ordre de hedging
            order = MarketOrder('BUY', size)
            
            # Soumettre l'ordre
            trade = self.ib.placeOrder(contract, order)
            
            # Attendre l'exécution
            self.ib.sleep(2)
            
            if trade.orderStatus.status == 'Filled':
                self.current_hedge = {
                    'contract': contract,
                    'size': size,
                    'fill_price': trade.orderStatus.avgFillPrice,
                    'timestamp': self.ib.reqCurrentTime()
                }
                print(f"✅ Hedge exécuté: {size} {contract.localSymbol} @ {trade.orderStatus.avgFillPrice}")
                return True
            else:
                print(f"❌ Hedge non exécuté: {trade.orderStatus.status}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur exécution hedge: {e}")
            return False
    
    def monitor_hedge_effectiveness(self, portfolio_positions):
        """
        Surveiller l'efficacité du hedge
        """
        if not self.current_hedge:
            return {'status': 'NO_HEDGE'}
        
        # Calculer la performance du hedge
        hedge_info = self.calculate_hedge_needs(portfolio_positions)
        
        # Si le delta a diminué significativement, considérer réduire le hedge
        if abs(hedge_info['total_delta']) < hedge_info['threshold'] * 0.5:
            return {
                'status': 'REDUCE_HEDGE',
                'reason': 'Delta significativement réduit',
                'current_delta': hedge_info['total_delta'],
                'threshold': hedge_info['threshold']
            }
        
        return {
            'status': 'MAINTAIN_HEDGE',
            'current_delta': hedge_info['total_delta'],
            'hedge_size': self.current_hedge['size']
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
    hedging = VIXHedging(vix_mgr, ib)
    
    # Simuler des positions
    portfolio = {
        'ES': {'quantity': 10, 'delta': 50},
        'SPX': {'quantity': 5, 'delta': 0.6}
    }
    
    # Analyser les besoins de hedging
    hedge_needs = hedging.calculate_hedge_needs(portfolio)
    print(f"Hedge Needs: {hedge_needs}")
    
    if hedge_needs['needs_hedge']:
        # Choisir l'instrument de hedging
        hedge_instrument = hedging.get_optimal_hedge_instrument(hedge_needs['hedge_size'])
        print(f"Hedge Instrument: {hedge_instrument}")
        
        # Surveiller l'efficacité
        effectiveness = hedging.monitor_hedge_effectiveness(portfolio)
        print(f"Hedge Effectiveness: {effectiveness}")
    
    ib.disconnect()

