#!/usr/bin/env python3
"""
Test des features MIA_IA avec données IBKR disponibles
Version: Test avec données réelles
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

class MIAFeatureCalculator:
    """Calculateur de features MIA_IA avec données IBKR"""
    
    def __init__(self):
        self.feature_cache = {}
        
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
    
    def calculate_vwap_trend_signal(self, current_price: float, vwap_price: float) -> float:
        """Feature #3: VWAP Trend Signal (18% weight)"""
        if not vwap_price or vwap_price == 0:
            return 0.5
        
        # Position par rapport au VWAP
        vwap_distance = (current_price - vwap_price) / vwap_price
        
        # Normaliser sur -1 à +1
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
    
    def calculate_options_flow_bias(self, option_volume: Optional[int], 
                                  option_oi: Optional[int], vix_level: float) -> float:
        """Feature #5: Options Flow Bias (15% weight)"""
        # Utiliser le VIX comme proxy pour le sentiment options
        if vix_level is None:
            return 0.5
        
        # Normaliser VIX (10-50 range typique)
        vix_normalized = max(0.0, min(1.0, (vix_level - 10) / 40))
        
        # VIX élevé = peur = baisse potentielle
        # VIX bas = complaisance = hausse potentielle
        if vix_level > 25:
            return 0.3  # Bearish
        elif vix_level < 15:
            return 0.7  # Bullish
        else:
            return 0.5  # Neutral
    
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
        """Calcul du score de confluence MIA_IA"""
        
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
        
        # Calculer les features
        features = {
            'order_book_imbalance': self.calculate_order_book_imbalance(dom_bids, dom_asks),
            'es_nq_correlation': self.calculate_es_nq_correlation(es_price, nq_price, es_change, nq_change),
            'vwap_trend_signal': self.calculate_vwap_trend_signal(es_price, es_price * 0.999),  # Proxy VWAP
            'volume_confirmation': self.calculate_volume_confirmation(aggressive_buys, aggressive_sells),
            'options_flow_bias': self.calculate_options_flow_bias(None, None, vix_level),
            'session_context': self.calculate_session_context(current_time)
        }
        
        # Pondération MIA_IA (version simplifiée)
        weights = {
            'order_book_imbalance': 0.15,
            'es_nq_correlation': 0.07,
            'vwap_trend_signal': 0.18,
            'volume_confirmation': 0.23,
            'options_flow_bias': 0.15,
            'session_context': 0.025
        }
        
        # Calcul du score final
        confluence_score = 0.0
        for feature, value in features.items():
            weight = weights.get(feature, 0.0)
            confluence_score += value * weight
        
        # Normaliser sur 0-1
        confluence_score = max(0.0, min(1.0, confluence_score))
        
        return confluence_score, features

def test_mia_features(host: str = '127.0.0.1', port: int = 7496, client_id: int = 15):
    """Test des features MIA_IA avec données IBKR"""
    print("🧠 TEST FEATURES MIA_IA AVEC DONNÉES IBKR")
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
        
        # Initialiser le calculateur MIA
        mia_calc = MIAFeatureCalculator()
        
        # -------- RÉCUPÉRATION DONNÉES --------
        print("\n📊 RÉCUPÉRATION DONNÉES POUR MIA_IA:")
        
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
                    # Logique simplifiée pour déterminer agressivité
                    if t.price > es_price:
                        aggressive_buys += t.size
                    else:
                        aggressive_sells += t.size
            
            for _ in range(20): ib.waitOnUpdate(timeout=1.0)
            ib.cancelTickByTickData(tbt_trades)
            
            print(f"Aggressive Buys: {aggressive_buys:.0f} | Aggressive Sells: {aggressive_sells:.0f}")
        else:
            print("\n⚠️ Order Flow non disponible (marché fermé)")
        
        # -------- CALCUL FEATURES MIA_IA --------
        print("\n🧠 CALCUL FEATURES MIA_IA:")
        
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
        
        # Calculer le score de confluence
        confluence_score, features = mia_calc.calculate_confluence_score(market_data)
        
        # Afficher les résultats
        print("\n📈 FEATURES CALCULÉES:")
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
        
        # Recommandation de trading
        print(f"\n💡 RECOMMANDATION:")
        if confluence_score >= 0.60:
            if confluence_score > 0.7:
                direction = "LONG" if features['volume_confirmation'] > 0.6 else "SHORT"
            else:
                direction = "NEUTRAL"
            print(f"  Signal détecté: {direction}")
            print(f"  Confluence: {confluence_score:.1%}")
            print(f"  Volume bias: {'Bullish' if features['volume_confirmation'] > 0.6 else 'Bearish'}")
        else:
            print("  Aucun signal de trading")
            print("  Attendre meilleure confluence")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        ib.disconnect()
        print("\n✅ Test terminé")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test features MIA_IA avec IBKR")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Hôte TWS/IBG")
    parser.add_argument("--port", type=int, default=7496, help="Port API")
    parser.add_argument("--clientId", type=int, default=15, help="Identifiant client")
    args = parser.parse_args()
    
    test_mia_features(host=args.host, port=args.port, client_id=args.clientId)



