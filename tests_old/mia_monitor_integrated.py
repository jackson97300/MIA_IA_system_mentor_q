#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mia_monitor_integrated.py
Monitoring MIA_IA - Version INTÉGRÉE avec modules existants
Utilise directement les modules de votre système MIA_IA
Version: Integrated v3.0 - Modules réels du système
"""

import time
import math
import csv
import sys
import os
from datetime import datetime, timezone
from ib_insync import *

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# IMPORTS SYSTÈME MIA_IA
# ============================================

try:
    # Core modules
    from core.battle_navale import BattleNavaleAnalyzer
    from core.base_types import MarketData, OrderFlowData, TradingFeatures
    
    # Features modules
    from features.feature_calculator import FeatureCalculator
    from features.confluence_analyzer import ConfluenceAnalyzer
    from features.order_book_imbalance import OrderBookImbalanceCalculator
    
    # Advanced features
    from features.advanced.tick_momentum import TickMomentumAnalyzer
    from features.advanced.delta_divergence import DeltaDivergenceAnalyzer
    from features.advanced.volatility_regime import VolatilityRegimeDetector
    from features.advanced.session_optimizer import SessionOptimizer
    
    # ML modules
    from ml.ensemble_filter import MLEnsembleFilter
    from ml.gamma_cycles import GammaCyclesAnalyzer
    
    # Strategies
    from strategies.signal_core.signal_generator import SignalGenerator
    from strategies.signal_core.technique_analyzers import TechniqueAnalyzers
    
    MIA_IA_MODULES_AVAILABLE = True
    print("✅ Tous les modules MIA_IA importés avec succès")
    
except ImportError as e:
    print(f"⚠️ Certains modules MIA_IA non disponibles: {e}")
    MIA_IA_MODULES_AVAILABLE = False

# ============================================
# CONFIG INTÉGRÉE
# ============================================
HOST = "127.0.0.1"
PORT = 7496  # Paper = 7497 | Live = 7496
CLIENT_ID = 52  # Incrémenté pour éviter conflit
REFRESH_SEC = 15

# Logging CSV Intégré
LOG_FILE = f"mia_monitor_integrated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
SNAPSHOTS_FILE = f"mia_snapshots_integrated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Stockage des snapshots
snapshots_history = []

def log_to_csv(data, filename):
    """Sauvegarde les données en CSV"""
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    except Exception as e:
        print(f"⚠️ Erreur log CSV {filename}: {e}")

def capture_tick_data(ib, contract, filename):
    """Capture les données de tick pour un contrat"""
    try:
        ticker = ib.ticker(contract)
        if ticker and ticker.last and ticker.lastSize:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            tick_data = [
                timestamp,
                contract.localSymbol,
                ticker.last,
                ticker.lastSize,
                ticker.bid,
                ticker.ask,
                ticker.close,
                ticker.high,
                ticker.low
            ]
            snapshots_history.append(tick_data)
            log_to_csv(tick_data, filename)
    except Exception as e:
        pass  # Ignore les erreurs de tick pour éviter le spam

def pick_front_month(ib, symbol, exchange="CME"):
    """Sélectionne le contrat front month (prochaine échéance négociable)"""
    base = Future(symbol, exchange=exchange)
    det = ib.reqContractDetails(base)
    if not det:
        return None
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    cds = [d.contract for d in det if d.contract.lastTradeDateOrContractMonth]
    cds.sort(key=lambda c: c.lastTradeDateOrContractMonth)
    for c in cds:
        if c.lastTradeDateOrContractMonth >= today:
            return c
    return cds[-1] if cds else None

def best_price(tk):
    """Récupère le meilleur prix disponible (last -> mid -> close)"""
    if tk is None:
        return None
    # ordre: last -> mid -> close
    if tk.last:
        return tk.last
    if tk.bid and tk.ask:
        return (tk.bid + tk.ask) / 2
    return tk.close

def safe_num(x):
    """Retourne None si NaN / non numérique ou négatif suspect"""
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return None
        # Filtrer les valeurs négatives suspectes pour les prix
        if isinstance(x, (int, float)) and x < 0:
            return None
        return x
    except Exception:
        return None

def f(x):
    """Format helper pour affichage"""
    return "n/a" if x is None else f"{x:.2f}"

# ============================================
# INTÉGRATION SYSTÈME MIA_IA RÉEL
# ============================================

class MIA_IA_Integrated_Monitor:
    """Monitor intégré utilisant les modules réels du système MIA_IA"""
    
    def __init__(self):
        """Initialisation avec tous les modules MIA_IA"""
        self.modules_available = MIA_IA_MODULES_AVAILABLE
        
        if not self.modules_available:
            print("⚠️ Mode dégradé - modules MIA_IA non disponibles")
            return
        
        try:
            # === INITIALISATION MODULES CORE ===
            self.battle_navale = BattleNavaleAnalyzer()
            self.feature_calculator = FeatureCalculator()
            self.confluence_analyzer = ConfluenceAnalyzer()
            self.order_book_calculator = OrderBookImbalanceCalculator()
            
            # === INITIALISATION FEATURES AVANCÉES ===
            self.tick_momentum = TickMomentumAnalyzer()
            self.delta_divergence = DeltaDivergenceAnalyzer()
            self.volatility_regime = VolatilityRegimeDetector()
            self.session_optimizer = SessionOptimizer()
            
            # === INITIALISATION ML ===
            self.ml_ensemble = MLEnsembleFilter()
            self.gamma_cycles = GammaCyclesAnalyzer()
            
            # === INITIALISATION STRATEGIES ===
            self.signal_generator = SignalGenerator()
            self.technique_analyzers = TechniqueAnalyzers()
            
            print("✅ Tous les modules MIA_IA initialisés avec succès")
            
        except Exception as e:
            print(f"❌ Erreur initialisation modules MIA_IA: {e}")
            self.modules_available = False
    
    def create_market_data(self, es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance):
        """Crée un objet MarketData pour les modules MIA_IA"""
        try:
            return MarketData(
                timestamp=datetime.now(),
                symbol="ES",
                open=es_ticker.open or 0,
                high=es_ticker.high or 0,
                low=es_ticker.low or 0,
                close=es_ticker.close or 0,
                volume=es_ticker.volume or 0,
                bid=es_ticker.bid or 0,
                ask=es_ticker.ask or 0,
                last=es_ticker.last or 0,
                last_size=es_ticker.lastSize or 0
            )
        except Exception as e:
            print(f"⚠️ Erreur création MarketData: {e}")
            return None
    
    def analyze_with_mia_ia_modules(self, market_data, es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance):
        """Analyse complète avec tous les modules MIA_IA"""
        if not self.modules_available:
            return self._fallback_analysis(es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance)
        
        try:
            # === 1. BATTLE NAVALE ANALYSIS ===
            battle_navale_result = self.battle_navale.analyze(market_data)
            
            # === 2. FEATURE CALCULATION ===
            features_result = self.feature_calculator.calculate_all_features(
                market_data=market_data,
                order_flow=OrderFlowData(cvd=cvd, dom_imbalance=dom_imbalance),
                options_data=None,  # À implémenter avec SPX options
                structure_data=None,
                es_nq_data=None,
                sierra_patterns=None,
                order_book=None
            )
            
            # === 3. CONFLUENCE ANALYSIS ===
            confluence_result = self.confluence_analyzer.analyze_confluence(market_data)
            
            # === 4. ORDER BOOK IMBALANCE ===
            order_book_result = self.order_book_calculator.calculate_imbalance(market_data, None)
            
            # === 5. ADVANCED FEATURES ===
            tick_momentum_result = self.tick_momentum.analyze_momentum(market_data)
            delta_divergence_result = self.delta_divergence.analyze_divergence(market_data)
            volatility_result = self.volatility_regime.detect_regime(market_data)
            session_result = self.session_optimizer.optimize_session(market_data)
            
            # === 6. ML ENSEMBLE ===
            ml_result = self.ml_ensemble.predict_signal_quality(features_result)
            
            # === 7. GAMMA CYCLES ===
            gamma_result = self.gamma_cycles.analyze_gamma_cycle(market_data)
            
            # === 8. TECHNIQUE ANALYZERS ===
            technique_result = self.technique_analyzers.analyze_all_techniques(
                market_data, None, None
            )
            
            # === 9. SIGNAL GENERATION ===
            signal_result = self.signal_generator.generate_signal(
                market_data, features_result, battle_navale_result
            )
            
            return {
                'battle_navale': battle_navale_result,
                'features': features_result,
                'confluence': confluence_result,
                'order_book': order_book_result,
                'tick_momentum': tick_momentum_result,
                'delta_divergence': delta_divergence_result,
                'volatility': volatility_result,
                'session': session_result,
                'ml_ensemble': ml_result,
                'gamma_cycles': gamma_result,
                'technique_analyzers': technique_result,
                'signal': signal_result
            }
            
        except Exception as e:
            print(f"⚠️ Erreur analyse MIA_IA: {e}")
            return self._fallback_analysis(es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance)
    
    def _fallback_analysis(self, es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance):
        """Analyse de fallback si modules non disponibles"""
        return {
            'battle_navale': {'score': 0.0, 'signal': 'NEUTRAL'},
            'features': {'total_score': 0.0},
            'confluence': {'score': 0.0},
            'order_book': {'imbalance': dom_imbalance},
            'tick_momentum': {'momentum': 0.0},
            'delta_divergence': {'divergence': 0.0},
            'volatility': {'regime': 'normal'},
            'session': {'optimization': 0.0},
            'ml_ensemble': {'confidence': 0.5, 'approved': False},
            'gamma_cycles': {'phase': 'normal', 'factor': 1.0},
            'technique_analyzers': {'status': 'unavailable'},
            'signal': {'decision': 'NEUTRAL', 'confidence': 0.0}
        }

def main():
    print("🚀 MIA Monitor INTÉGRÉ - Version avec modules MIA_IA réels")
    print("=" * 80)
    print(f"📁 Log file: {LOG_FILE}")
    print(f"📊 Snapshots file: {SNAPSHOTS_FILE}")
    print("🎯 INTÉGRATION: Modules réels du système MIA_IA")
    
    # Initialiser le monitor intégré
    mia_monitor = MIA_IA_Integrated_Monitor()
    
    # Initialiser les fichiers CSV
    headers_main = [
        "timestamp", "cycle", "es_price", "nq_price", "vix_value", 
        "cvd", "dom_imbalance", "battle_navale_score", "features_score", 
        "confluence_score", "ml_confidence", "gamma_phase", "signal_decision",
        "signal_confidence", "order_book_imbalance", "tick_momentum", 
        "volatility_regime", "session_optimization", "dom_bids", "dom_asks"
    ]
    headers_snapshots = ["timestamp", "symbol", "last", "last_size", "bid", "ask", "close", "high", "low"]
    
    log_to_csv(headers_main, LOG_FILE)
    log_to_csv(headers_snapshots, SNAPSHOTS_FILE)
    print("✅ Logging CSV Intégré initialisé")
    
    # Connexion
    ib = IB()
    try:
        print(f"🔌 Connexion → {HOST}:{PORT} (clientId={CLIENT_ID})")
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print("✅ Connexion réussie")
        
        # === SETUP MARKET DATA MODE ===
        ib.reqMarketDataType(1)  # REALTIME
        
        print("\n📊 Setup instruments INTÉGRÉ...")
        
        # === ES ===
        es = pick_front_month(ib, 'ES', 'CME')
        if not es:
            raise RuntimeError("ES introuvable (permissions CME ?)")
        print(f"✅ ES: {es.localSymbol} @ {es.exchange}")
        tkr_es = ib.reqMktData(es, '', False, False)
        ib.reqMktDepth(es, numRows=10)
        ib.reqTickByTickData(es, "AllLast", 0, False)
        
        # === NQ ===
        nq = pick_front_month(ib, 'NQ', 'CME')
        if not nq:
            raise RuntimeError("NQ introuvable (permissions CME ?)")
        print(f"✅ NQ: {nq.localSymbol} @ {nq.exchange}")
        tkr_nq = ib.reqMktData(nq, '', False, False)
        ib.reqTickByTickData(nq, "AllLast", 0, False)
        
        # === VIX (index) ===
        vix = Index("VIX", "CBOE")
        ib.qualifyContracts(vix)
        ib.reqMktData(vix, "", False, False)
        print("✅ VIX configuré")
        
        # === SPX OPTIONS (pour Gamma Levels) ===
        try:
            spx = Index("SPX", "CBOE")
            ib.qualifyContracts(spx)
            print("✅ SPX Options configuré (Gamma Levels)")
        except Exception as e:
            print(f"⚠️ SPX Options non disponible: {e}")
        
        # === WARM-UP ===
        print("⏳ Attente données initiales (15 s)...")
        for _ in range(15):
            ib.waitOnUpdate(timeout=1.0)
        
        # === LECTURE INITIALE ===
        es_price = best_price(ib.ticker(es))
        nq_price = best_price(ib.ticker(nq))
        
        if es_price is None or nq_price is None:
            print("⚠️ Données live manquantes, tentative delayed...")
            ib.reqMarketDataType(3)  # DELAYED
            ib.cancelMktData(es); ib.cancelMktData(nq)
            tkr_es = ib.reqMktData(es, '', False, False)
            tkr_nq = ib.reqMktData(nq, '', False, False)
            for _ in range(8):
                ib.waitOnUpdate(timeout=1.0)
            es_price = es_price or best_price(ib.ticker(es))
            nq_price = nq_price or best_price(ib.ticker(nq))
        
        print("🚀 Monitoring INTÉGRÉ démarré (Ctrl+C pour arrêter)")
        print("-" * 80, flush=True)
        
        # Variables
        cvd = 0
        last_es_price = None
        cycle = 0
        
        while True:
            cycle += 1
            now = datetime.now()
            
            # Attendre les updates avant de lire
            ib.waitOnUpdate(timeout=0.5)
            
            # Récupérer données
            es_ticker = ib.ticker(es)
            nq_ticker = ib.ticker(nq)
            vix_ticker = ib.ticker(vix)
            
            es_price = best_price(es_ticker)
            nq_price = best_price(nq_ticker)
            vix_value = best_price(vix_ticker)
            
            # Si pas de données, on attend un peu
            if es_price is None or nq_price is None:
                ib.waitOnUpdate(timeout=0.5)
                es_price = best_price(ib.ticker(es))
                nq_price = best_price(ib.ticker(nq))
            
            # === CVD CALCULATION ===
            trade_size = safe_num(getattr(es_ticker, "lastSize", None))
            ref_price = es_price
            if ref_price and trade_size:
                if last_es_price is not None:
                    if ref_price > last_es_price:
                        cvd += trade_size
                    elif ref_price < last_es_price:
                        cvd -= trade_size
                last_es_price = ref_price
            
            # === DOM IMBALANCE ===
            dom_imbalance = 0.0
            try:
                bids = getattr(es_ticker, "domBids", []) or []
                asks = getattr(es_ticker, "domAsks", []) or []
                bid_vol = sum(safe_num(b.size) or 0 for b in bids[:5])
                ask_vol = sum(safe_num(a.size) or 0 for a in asks[:5])
                if (bid_vol + ask_vol) > 0:
                    dom_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)
            except Exception:
                pass
            
            # === CRÉATION MARKET DATA ===
            market_data = mia_monitor.create_market_data(es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance)
            
            # === ANALYSE COMPLÈTE MIA_IA ===
            analysis_result = mia_monitor.analyze_with_mia_ia_modules(
                market_data, es_ticker, nq_ticker, vix_ticker, cvd, dom_imbalance
            )
            
            # === EXTRACTION RÉSULTATS ===
            battle_navale_score = analysis_result.get('battle_navale', {}).get('score', 0.0)
            features_score = analysis_result.get('features', {}).get('total_score', 0.0)
            confluence_score = analysis_result.get('confluence', {}).get('score', 0.0)
            ml_confidence = analysis_result.get('ml_ensemble', {}).get('confidence', 0.5)
            gamma_phase = analysis_result.get('gamma_cycles', {}).get('phase', 'normal')
            signal_decision = analysis_result.get('signal', {}).get('decision', 'NEUTRAL')
            signal_confidence = analysis_result.get('signal', {}).get('confidence', 0.0)
            order_book_imbalance = analysis_result.get('order_book', {}).get('imbalance', dom_imbalance)
            tick_momentum = analysis_result.get('tick_momentum', {}).get('momentum', 0.0)
            volatility_regime = analysis_result.get('volatility', {}).get('regime', 'normal')
            session_optimization = analysis_result.get('session', {}).get('optimization', 0.0)
            
            # === LOG CSV INTÉGRÉ ===
            log_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                cycle,
                es_price,
                nq_price,
                vix_value,
                cvd,
                dom_imbalance,
                battle_navale_score,
                features_score,
                confluence_score,
                ml_confidence,
                gamma_phase,
                signal_decision,
                signal_confidence,
                order_book_imbalance,
                tick_momentum,
                volatility_regime,
                session_optimization,
                len(bids),
                len(asks)
            ]
            log_to_csv(log_data, LOG_FILE)
            
            # === CAPTURE TICK DATA ===
            capture_tick_data(ib, es, SNAPSHOTS_FILE)
            capture_tick_data(ib, nq, SNAPSHOTS_FILE)
            
            # === AFFICHAGE INTÉGRÉ ===
            print(f"\n⏰ {now:%H:%M:%S} | Cycle {cycle}")
            print(f"📊 ES: {f(es_price)} | NQ: {f(nq_price)} | VIX: {f(vix_value)}")
            print(f"📈 CVD: {cvd:+.0f} | DOM: {dom_imbalance:+.2f}")
            
            # === AFFICHAGE RÉSULTATS MIA_IA ===
            print(f"⚔️ Battle Navale: {battle_navale_score:.3f}")
            print(f"📊 Features Score: {features_score:.3f}")
            print(f"🎯 Confluence: {confluence_score:.3f}")
            print(f"🤖 ML Confidence: {ml_confidence:.2f}")
            print(f"📈 Gamma Phase: {gamma_phase}")
            print(f"🚀 Signal: {signal_decision} (conf: {signal_confidence:.2f})")
            
            # === AFFICHAGE FEATURES AVANCÉES ===
            print(f"💰 Order Book: {order_book_imbalance:+.3f}")
            print(f"⚡ Tick Momentum: {tick_momentum:+.3f}")
            print(f"📊 Volatility: {volatility_regime}")
            print(f"⏰ Session Opt: {session_optimization:+.3f}")
            
            # === ANALYSE DÉTAILLÉE ===
            if features_score > 0.3:
                print(f"   🔥 Système MIA_IA actif - Score élevé détecté")
            else:
                print(f"   💤 Marché calme - Score faible (normal en session asiatique)")
            
            # === INFO DOM ===
            bids = getattr(es_ticker, "domBids", []) or []
            asks = getattr(es_ticker, "domAsks", []) or []
            print(f"🔍 DOM: {len(bids)} bids, {len(asks)} asks")
            print(f"💾 Log: {LOG_FILE}")
            print(f"📊 Snaps: {len(snapshots_history)}")
            print("-" * 80, flush=True)
            
            time.sleep(REFRESH_SEC)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêté par l'utilisateur")
        print(f"📊 Données INTÉGRÉES sauvegardées dans:")
        print(f"   - Main: {LOG_FILE}")
        print(f"   - Snapshots: {SNAPSHOTS_FILE} ({len(snapshots_history)} snapshots)")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        ib.disconnect()
        print("✅ Connexion fermée")

if __name__ == "__main__":
    main()



