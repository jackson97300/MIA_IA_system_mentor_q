#!/usr/bin/env python3
"""
Test MIA_IA avec derniers niveaux d'options SPX (avant fermeture)
Version: Simulation avec données historiques
"""

from ib_insync import *
from datetime import datetime, timezone
import argparse
import pytz
import numpy as np
from typing import Dict, List, Tuple, Optional

def is_market_open():
    """Vérifie si les marchés US sont ouverts"""
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)
    
    if now_ny.weekday() >= 5:
        return False, "Weekend - Marché fermé"
    
    current_time = now_ny.time()
    futures_start = datetime.strptime("18:00", "%H:%M").time()
    futures_end = datetime.strptime("17:00", "%H:%M").time()
    options_start = datetime.strptime("09:30", "%H:%M").time()
    options_end = datetime.strptime("16:00", "%H:%M").time()
    
    if now_ny.weekday() == 6:  # Dimanche
        if current_time < futures_start:
            return False, "Futures fermés"
    elif now_ny.weekday() == 4:  # Vendredi
        if current_time > futures_end:
            return False, "Futures fermés"
    
    if options_start <= current_time <= options_end:
        return True, "Marché ouvert"
    else:
        return False, "Options fermées"

class MIAOptionsCalculator:
    """Calculateur MIA_IA avec données options SPX"""
    
    def __init__(self):
        # Données options SPX (derniers niveaux avant fermeture)
        self.spx_options_data = {
            'spot_price': 6395.78,
            'selected_strike': 6395.0,
            'expiry': '20250918',
            'greeks': {
                'delta': 0.5381645886260984,
                'gamma': 0.0016999524845584496,
                'vega': 7.243671911907313,
                'theta': -1.97930528122788,
                'implied_vol': 0.12807960473088492,
                'und_price': 6396.38427734375
            },
            'option_price': 102.37988335630736,
            'trading_class': 'SPX',
            'exchange': 'CBOE'
        }
        
        # Niveaux gamma approximatifs (basés sur les données historiques)
        self.gamma_levels = {
            'call_walls': [6400, 6450, 6500],  # Niveaux de résistance
            'put_walls': [6350, 6300, 6250],   # Niveaux de support
            'gamma_flip': 6395  # Niveau ATM
        }
    
    def calculate_gamma_levels_proximity(self, current_price: float) -> float:
        """Feature #1: Gamma Levels Proximity (32% weight)"""
        if not current_price:
            return 0.5
        
        # Distance aux niveaux gamma critiques
        distances = []
        
        # Distance au gamma flip (ATM)
        gamma_flip_dist = abs(current_price - self.gamma_levels['gamma_flip'])
        distances.append(gamma_flip_dist)
        
        # Distance aux call walls
        for call_wall in self.gamma_levels['call_walls']:
            if current_price < call_wall:
                distances.append(call_wall - current_price)
        
        # Distance aux put walls
        for put_wall in self.gamma_levels['put_walls']:
            if current_price > put_wall:
                distances.append(current_price - put_wall)
        
        if not distances:
            return 0.5
        
        # Normaliser la distance minimale (0-50 points)
        min_distance = min(distances)
        proximity_score = max(0.0, min(1.0, 1.0 - (min_distance / 50.0)))
        
        return proximity_score
    
    def calculate_options_flow_bias(self, vix_level: float) -> float:
        """Feature #5: Options Flow Bias (15% weight) - Version améliorée"""
        # Utiliser les Greeks SPX + VIX pour le sentiment
        if not vix_level:
            return 0.5
        
        # Analyse des Greeks SPX
        delta = self.spx_options_data['greeks']['delta']
        gamma = self.spx_options_data['greeks']['gamma']
        implied_vol = self.spx_options_data['greeks']['implied_vol']
        
        # Sentiment basé sur Delta (position des options)
        if delta > 0.6:
            delta_sentiment = 0.7  # Bullish (beaucoup de calls)
        elif delta < 0.4:
            delta_sentiment = 0.3  # Bearish (beaucoup de puts)
        else:
            delta_sentiment = 0.5  # Neutral
        
        # Sentiment basé sur VIX
        if vix_level > 25:
            vix_sentiment = 0.3  # Bearish (peur)
        elif vix_level < 15:
            vix_sentiment = 0.7  # Bullish (complaisance)
        else:
            vix_sentiment = 0.5  # Neutral
        
        # Sentiment basé sur Implied Vol
        if implied_vol > 0.15:
            vol_sentiment = 0.3  # Bearish (volatilité élevée)
        elif implied_vol < 0.10:
            vol_sentiment = 0.7  # Bullish (volatilité basse)
        else:
            vol_sentiment = 0.5  # Neutral
        
        # Combiner les sentiments
        combined_sentiment = (delta_sentiment * 0.4 + vix_sentiment * 0.4 + vol_sentiment * 0.2)
        
        return combined_sentiment
    
    def calculate_order_book_imbalance(self, dom_bids: List, dom_asks: List) -> float:
        """Feature #9: Order Book Imbalance (15% weight)"""
        if not dom_bids or not dom_asks:
            return 0.5
        
        # Calculer la pression achat/vente
        bid_volume = sum(bid.size for bid in dom_bids[:5])
        ask_volume = sum(ask.size for ask in dom_asks[:5])
        
        if bid_volume + ask_volume == 0:
            return 0.5
        
        imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        return max(0.0, min(1.0, (imbalance + 1) / 2))
    
    def calculate_es_nq_correlation(self, es_price: float, nq_price: float, 
                                  es_change: float, nq_change: float) -> float:
        """Feature #8: ES/NQ Correlation (7% weight)"""
        if not es_price or not nq_price:
            return 0.5
        
        # Ratio de corrélation normalisé
        correlation_ratio = nq_price / es_price
        normalized_ratio = min(abs(correlation_ratio - 3.6) / 0.5, 1.0)
        
        # Direction de corrélation
        if (es_change > 0 and nq_change > 0) or (es_change < 0 and nq_change < 0):
            direction_bonus = 0.2
        else:
            direction_bonus = -0.2
        
        return max(0.0, min(1.0, 0.5 + direction_bonus + (1 - normalized_ratio) * 0.3))
    
    def calculate_vwap_trend_signal(self, current_price: float) -> float:
        """Feature #3: VWAP Trend Signal (18% weight)"""
        if not current_price:
            return 0.5
        
        # Utiliser le prix underlying des options comme proxy VWAP
        vwap_price = self.spx_options_data['greeks']['und_price']
        
        # Position par rapport au VWAP
        vwap_distance = (current_price - vwap_price) / vwap_price
        
        # Normaliser sur 0-1
        if vwap_distance > 0.01:  # 1% au-dessus
            return 0.8
        elif vwap_distance < -0.01:  # 1% en-dessous
            return 0.2
        else:
            return 0.5 + (vwap_distance * 50)  # Proche du VWAP
    
    def calculate_volume_confirmation(self, aggressive_buys: float, aggressive_sells: float) -> float:
        """Feature #2: Volume Confirmation (23% weight)"""
        total_volume = aggressive_buys + aggressive_sells
        if total_volume == 0:
            return 0.5
        
        # Ratio de pression
        buy_ratio = aggressive_buys / total_volume
        return buy_ratio
    
    def calculate_session_context(self, current_time: datetime) -> float:
        """Feature #10: Session Context (2.5% weight)"""
        ny_tz = pytz.timezone('America/New_York')
        now_ny = current_time.astimezone(ny_tz)
        current_time_ny = now_ny.time()
        
        # Multiplicateurs par session
        opening_time = datetime.strptime("09:30", "%H:%M").time()
        power_hour_start = datetime.strptime("15:00", "%H:%M").time()
        power_hour_end = datetime.strptime("16:00", "%H:%M").time()
        
        if opening_time <= current_time_ny <= datetime.strptime("10:30", "%H:%M").time():
            return 1.2  # Opening boost
        elif power_hour_start <= current_time_ny <= power_hour_end:
            return 1.2  # Power hour boost
        else:
            return 1.0  # Normal session
    
    def calculate_confluence_score(self, market_data: Dict) -> Tuple[float, Dict]:
        """Calcul du score de confluence MIA_IA avec options"""
        
        # Extraire les données
        es_price = market_data.get('es_price', 0)
        nq_price = market_data.get('nq_price', 0)
        es_change = market_data.get('es_change', 0)
        nq_change = market_data.get('nq_change', 0)
        vix_level = market_data.get('vix_level', 0)
        aggressive_buys = market_data.get('aggressive_buys', 0)
        aggressive_sells = market_data.get('aggressive_sells', 0)
        dom_bids = market_data.get('dom_bids', [])
        dom_asks = market_data.get('dom_asks', [])
        current_time = market_data.get('current_time', datetime.now())
        
        # Calculer les features avec options
        features = {
            'gamma_levels_proximity': self.calculate_gamma_levels_proximity(es_price),
            'volume_confirmation': self.calculate_volume_confirmation(aggressive_buys, aggressive_sells),
            'vwap_trend_signal': self.calculate_vwap_trend_signal(es_price),
            'options_flow_bias': self.calculate_options_flow_bias(vix_level),
            'order_book_imbalance': self.calculate_order_book_imbalance(dom_bids, dom_asks),
            'es_nq_correlation': self.calculate_es_nq_correlation(es_price, nq_price, es_change, nq_change),
            'session_context': self.calculate_session_context(current_time)
        }
        
        # Pondération MIA_IA (version complète avec options)
        weights = {
            'gamma_levels_proximity': 0.32,  # Feature #1 - Options
            'volume_confirmation': 0.23,      # Feature #2
            'vwap_trend_signal': 0.18,        # Feature #3
            'options_flow_bias': 0.15,        # Feature #5 - Options
            'order_book_imbalance': 0.15,     # Feature #9
            'es_nq_correlation': 0.07,        # Feature #8
            'session_context': 0.025          # Feature #10
        }
        
        # Calcul du score final
        confluence_score = 0.0
        for feature, value in features.items():
            weight = weights.get(feature, 0.0)
            confluence_score += value * weight
        
        # Normaliser sur 0-1
        confluence_score = max(0.0, min(1.0, confluence_score))
        
        return confluence_score, features

def test_mia_with_options(host: str = '127.0.0.1', port: int = 7496, client_id: int = 17):
    """Test MIA_IA avec données options SPX"""
    print("🧠 TEST MIA_IA AVEC OPTIONS SPX")
    print("=" * 50)
    
    ib = IB()
    try:
        # Connexion
        print(f"Connexion → host={host}, port={port}, clientId={client_id}")
        ib.connect(host, port, clientId=client_id)
        print("✅ Connexion réussie")
        
        # Check horaires
        market_open, market_status = is_market_open()
        print(f"\n🕐 STATUT MARCHÉ: {market_status}")
        
        # Initialiser le calculateur MIA avec options
        mia_calc = MIAOptionsCalculator()
        
        # Afficher les données options utilisées
        print("\n📊 DONNÉES OPTIONS SPX (derniers niveaux):")
        print(f"  Spot Price: {mia_calc.spx_options_data['spot_price']}")
        print(f"  Selected Strike: {mia_calc.spx_options_data['selected_strike']}")
        print(f"  Expiry: {mia_calc.spx_options_data['expiry']}")
        print(f"  Trading Class: {mia_calc.spx_options_data['trading_class']}")
        print(f"  Option Price: {mia_calc.spx_options_data['option_price']:.2f}")
        
        print("\n📈 GREEKS SPX:")
        greeks = mia_calc.spx_options_data['greeks']
        print(f"  Delta: {greeks['delta']:.4f}")
        print(f"  Gamma: {greeks['gamma']:.6f}")
        print(f"  Vega: {greeks['vega']:.2f}")
        print(f"  Theta: {greeks['theta']:.2f}")
        print(f"  Implied Vol: {greeks['implied_vol']:.4f}")
        print(f"  Underlying Price: {greeks['und_price']:.2f}")
        
        print("\n🎯 GAMMA LEVELS:")
        print(f"  Gamma Flip (ATM): {mia_calc.gamma_levels['gamma_flip']}")
        print(f"  Call Walls: {mia_calc.gamma_levels['call_walls']}")
        print(f"  Put Walls: {mia_calc.gamma_levels['put_walls']}")
        
        # -------- RÉCUPÉRATION DONNÉES ACTUELLES --------
        print("\n📊 RÉCUPÉRATION DONNÉES ACTUELLES:")
        
        # ES Futures
        es_found = None
        es_base = Future('ES', exchange="CME")
        es_det = ib.reqContractDetails(es_base)
        if es_det:
            es_found = es_det[0].contract
            print(f"✅ ES trouvé: {es_found.localSymbol}")
            
            # L1 ES
            tkr_es = ib.reqMktData(es_found, '', False)
            for _ in range(10): ib.waitOnUpdate(timeout=1.0)
            es_price = tkr_es.last or ((tkr_es.bid + tkr_es.ask) / 2 if tkr_es.bid and tkr_es.ask else None)
            es_change = tkr_es.last - tkr_es.close if tkr_es.last and tkr_es.close else 0
            
            # DOM ES
            dom_es = ib.reqMktDepth(es_found, numRows=5)
            for _ in range(5): ib.waitOnUpdate(timeout=1.0)
            dom_bids = dom_es.domBids if dom_es.domBids else []
            dom_asks = dom_es.domAsks if dom_es.domAsks else []
            
            print(f"ES Price: {es_price:.2f} | Change: {es_change:+.2f}")
            print(f"DOM Bids: {len(dom_bids)} | DOM Asks: {len(dom_asks)}")
        
        # NQ Futures
        nq_found = None
        nq_base = Future('NQ', exchange="CME")
        nq_det = ib.reqContractDetails(nq_base)
        if nq_det:
            nq_found = nq_det[0].contract
            print(f"✅ NQ trouvé: {nq_found.localSymbol}")
            
            # L1 NQ
            tkr_nq = ib.reqMktData(nq_found, '', False)
            for _ in range(10): ib.waitOnUpdate(timeout=1.0)
            nq_price = tkr_nq.last or ((tkr_nq.bid + tkr_nq.ask) / 2 if tkr_nq.bid and tkr_nq.ask else None)
            nq_change = tkr_nq.last - tkr_nq.close if tkr_nq.last and tkr_nq.close else 0
            
            print(f"NQ Price: {nq_price:.2f} | Change: {nq_change:+.2f}")
        
        # VIX
        vix_idx = Index('VIX', 'CBOE')
        ib.qualifyContracts(vix_idx)
        tkr_vix = ib.reqMktData(vix_idx, '', False)
        for _ in range(10): ib.waitOnUpdate(timeout=1.0)
        vix_level = tkr_vix.last or tkr_vix.close
        
        print(f"VIX Level: {vix_level:.2f}")
        
        # Order Flow (si marché ouvert)
        aggressive_buys = aggressive_sells = 0
        if market_open:
            print("\n🔬 ORDER FLOW (marché ouvert):")
            tbt_trades = ib.reqTickByTickData(es_found, "AllLast", 0, False)
            
            @tbt_trades.updateEvent
            def _on_trade(t):
                nonlocal aggressive_buys, aggressive_sells
                if t.price and t.size:
                    if t.price > es_price:
                        aggressive_buys += t.size
                    else:
                        aggressive_sells += t.size
            
            for _ in range(20): ib.waitOnUpdate(timeout=1.0)
            ib.cancelTickByTickData(tbt_trades)
            
            print(f"Aggressive Buys: {aggressive_buys:.0f} | Aggressive Sells: {aggressive_sells:.0f}")
        else:
            print("\n⚠️ Order Flow non disponible (marché fermé)")
        
        # -------- CALCUL FEATURES MIA_IA AVEC OPTIONS --------
        print("\n🧠 CALCUL FEATURES MIA_IA AVEC OPTIONS:")
        
        # Préparer les données
        market_data = {
            'es_price': es_price,
            'nq_price': nq_price,
            'es_change': es_change,
            'nq_change': nq_change,
            'vix_level': vix_level,
            'aggressive_buys': aggressive_buys,
            'aggressive_sells': aggressive_sells,
            'dom_bids': dom_bids,
            'dom_asks': dom_asks,
            'current_time': datetime.now()
        }
        
        # Calculer le score de confluence avec options
        confluence_score, features = mia_calc.calculate_confluence_score(market_data)
        
        # Afficher les résultats
        print("\n📈 FEATURES CALCULÉES (avec options):")
        for feature_name, feature_value in features.items():
            print(f"  {feature_name}: {feature_value:.3f}")
        
        print(f"\n🎯 SCORE CONFLUENCE MIA_IA: {confluence_score:.3f}")
        
        # Interprétation du score
        if confluence_score >= 0.85:
            signal_quality = "🔥 PREMIUM SIGNAL (size ×1.5)"
        elif confluence_score >= 0.70:
            signal_quality = "✅ STRONG SIGNAL (size ×1.0)"
        elif confluence_score >= 0.60:
            signal_quality = "⚠️ WEAK SIGNAL (size ×0.5)"
        else:
            signal_quality = "❌ NO TRADE (attendre)"
        
        print(f"🎯 QUALITÉ SIGNAL: {signal_quality}")
        
        # Analyse détaillée des options
        print(f"\n📊 ANALYSE OPTIONS SPX:")
        gamma_prox = features['gamma_levels_proximity']
        options_bias = features['options_flow_bias']
        
        print(f"  Gamma Levels Proximity: {gamma_prox:.3f}")
        if gamma_prox > 0.7:
            print("    → Proche d'un niveau gamma critique")
        elif gamma_prox < 0.3:
            print("    → Loin des niveaux gamma")
        else:
            print("    → Distance modérée aux niveaux gamma")
        
        print(f"  Options Flow Bias: {options_bias:.3f}")
        if options_bias > 0.6:
            print("    → Sentiment options bullish")
        elif options_bias < 0.4:
            print("    → Sentiment options bearish")
        else:
            print("    → Sentiment options neutral")
        
        # Recommandation de trading
        print(f"\n💡 RECOMMANDATION AVEC OPTIONS:")
        if confluence_score >= 0.60:
            if confluence_score > 0.7:
                direction = "LONG" if features['volume_confirmation'] > 0.6 else "SHORT"
            else:
                direction = "NEUTRAL"
            print(f"  Signal détecté: {direction}")
            print(f"  Confluence: {confluence_score:.1%}")
            print(f"  Volume bias: {'Bullish' if features['volume_confirmation'] > 0.6 else 'Bearish'}")
            print(f"  Options sentiment: {'Bullish' if options_bias > 0.6 else 'Bearish' if options_bias < 0.4 else 'Neutral'}")
        else:
            print("  Aucun signal de trading")
            print("  Attendre meilleure confluence")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        ib.disconnect()
        print("\n✅ Test terminé")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test MIA_IA avec options SPX")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Hôte TWS/IBG")
    parser.add_argument("--port", type=int, default=7496, help="Port API")
    parser.add_argument("--clientId", type=int, default=17, help="Identifiant client")
    args = parser.parse_args()
    
    test_mia_with_options(host=args.host, port=args.port, client_id=args.clientId)



