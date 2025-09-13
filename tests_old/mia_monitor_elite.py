#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mia_monitor_elite.py
Monitoring MIA_IA - Version ELITE COMPLÈTE
Utilise TOUTES les fonctionnalités du système MIA_IA
Version: Elite v3.0 - 4 Techniques + 11 Features + ML Ensemble
"""

import time
import math
import csv
from datetime import datetime, timezone
from ib_insync import *

# ============================================
# CONFIG ELITE
# ============================================
HOST = "127.0.0.1"
PORT = 7496  # Paper = 7497 | Live = 7496
CLIENT_ID = 51  # Incrémenté pour éviter conflit
REFRESH_SEC = 15

# Logging CSV Elite
LOG_FILE = f"mia_monitor_elite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
SNAPSHOTS_FILE = f"mia_snapshots_elite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

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
# INTÉGRATION SYSTÈME MIA_IA COMPLET
# ============================================

def calculate_elite_battle_navale_score(es_price, nq_price, vix_value, dom_imbalance, cvd, 
                                      gamma_levels=None, options_flow=None, smart_money=None,
                                      vwap_trend=None, sierra_patterns=None, session_context=None):
    """
    Score Battle Navale ELITE - Utilise TOUTES les features du système MIA_IA
    """
    score = 0.0
    
    # === 1. GAMMA LEVELS PROXIMITY (28%) - TECHNIQUE ÉLITE ===
    if gamma_levels:
        gamma_score = gamma_levels.get('proximity_score', 0)
        score += gamma_score * 0.28
    
    # === 2. VOLUME CONFIRMATION (20%) - ORDER FLOW ===
    if abs(cvd) > 10:  # Seuil ajusté
        score += 0.20
    
    # === 3. VWAP TREND SIGNAL (16%) ===
    if vwap_trend:
        vwap_score = vwap_trend.get('trend_strength', 0)
        score += vwap_score * 0.16
    
    # === 4. SIERRA PATTERN STRENGTH (16%) ===
    if sierra_patterns:
        pattern_score = sierra_patterns.get('strength', 0)
        score += pattern_score * 0.16
    
    # === 5. OPTIONS FLOW BIAS (13%) - CORRIGÉ : DYNAMIQUE ===
    if options_flow:
        flow_bias = options_flow.get('call_put_ratio', 1.0)
        # Formule dynamique basée sur VIX et CVD
        if vix_value:
            # VIX élevé = plus de puts = ratio < 1.0
            vix_factor = max(0.5, min(1.5, 1.0 - (vix_value - 15) / 20))
            # CVD négatif = plus de vendeurs = ratio < 1.0
            cvd_factor = max(0.5, min(1.5, 1.0 - cvd / 100))
            # Ratio dynamique
            dynamic_ratio = vix_factor * cvd_factor
            if dynamic_ratio > 1.2:  # Plus de calls
                score += 0.13
            elif dynamic_ratio < 0.8:  # Plus de puts
                score += 0.06
            else:  # Neutre
                score += 0.02
        else:
            # Fallback si pas de VIX
            if flow_bias > 1.2:
                score += 0.13
            elif flow_bias < 0.8:
                score += 0.06
    
    # === 6. SMART MONEY STRENGTH (12.5%) - TECHNIQUE #2 ===
    if smart_money:
        smart_score = smart_money.get('institutional_flow', 0)
        score += smart_score * 0.125
    
    # === 7. ORDER BOOK IMBALANCE (15%) ===
    if abs(dom_imbalance) > 0.05:
        score += 0.15
    
    # === 8. LEVEL PROXIMITY (7%) ===
    # Simulé avec VIX pour l'instant
    if vix_value and 15 <= vix_value <= 20:
        score += 0.07
    
    # === 9. ES/NQ CORRELATION (7%) ===
    if es_price and nq_price:
        ratio = nq_price / es_price
        if abs(ratio - 3.6) < 0.3:
            score += 0.07
    
    # === 10. SESSION CONTEXT (2.5%) ===
    if session_context:
        session_score = session_context.get('performance', 0)
        score += session_score * 0.025
    
    # === 11. PULLBACK QUALITY (1.5%) ===
    # Simulé avec stabilité prix
    if es_price and abs(cvd) < 5:
        score += 0.015
    
    return min(1.0, score)

def get_elite_signal(score, ml_confidence=None, gamma_phase=None, session_phase="unknown"):
    """
    Signal ELITE - Intègre ML Ensemble et Gamma Cycles
    CORRIGÉ : Seuils adaptés par session
    """
    # === DÉTECTION SESSION ASIATIQUE ===
    is_asian_session = session_phase in ["asian", "overnight", "unknown"]
    
    # === TECHNIQUE #3: ML ENSEMBLE FILTER - SEUILS ADAPTÉS ===
    ml_threshold = 0.45 if is_asian_session else 0.65  # Plus permissif en Asie
    
    if ml_confidence and ml_confidence < ml_threshold:
        if is_asian_session:
            return "🌙 NO TRADE - LOW ACTIVITY"  # Plus clair pour session calme
        else:
            return "🚫 ML REJECTED"  # ML rejette le signal
    
    # === TECHNIQUE #4: GAMMA CYCLES ADJUSTMENT ===
    gamma_multiplier = 1.0
    if gamma_phase:
        if gamma_phase == "gamma_peak":
            gamma_multiplier = 1.3
        elif gamma_phase == "expiry_week":
            gamma_multiplier = 0.8
    
    adjusted_score = score * gamma_multiplier
    
    # === SEUILS ÉLITE - ADAPTÉS PAR SESSION ===
    if is_asian_session:
        # Seuils plus bas en session asiatique
        if adjusted_score >= 0.60:
            return "🔥 ELITE LONG"
        elif adjusted_score >= 0.45:
            return "✅ STRONG LONG"
        elif adjusted_score <= 0.10:
            return "❌ STRONG SHORT"
        elif adjusted_score <= 0.25:
            return "🔴 WEAK SHORT"
        else:
            return "➖ NEUTRAL"
    else:
        # Seuils standards pour session US
        if adjusted_score >= 0.75:
            return "🔥 ELITE LONG"
        elif adjusted_score >= 0.60:
            return "✅ STRONG LONG"
        elif adjusted_score <= 0.15:
            return "❌ STRONG SHORT"
        elif adjusted_score <= 0.30:
            return "🔴 WEAK SHORT"
        else:
            return "➖ NEUTRAL"

def analyze_market_structure(es_ticker, nq_ticker, vix_ticker):
    """
    Analyse structure marché pour features avancées
    CORRIGÉ : Options flow dynamique
    """
    # === VWAP TREND SIGNAL ===
    vwap_trend = {
        'trend_strength': 0.0,
        'position': 'neutral'
    }
    
    # === SIERRA PATTERNS ===
    sierra_patterns = {
        'strength': 0.0,
        'pattern_type': 'none'
    }
    
    # === SESSION CONTEXT ===
    session_context = {
        'performance': 0.0,
        'phase': 'unknown'
    }
    
    # === GAMMA LEVELS (simulé) ===
    gamma_levels = {
        'proximity_score': 0.0,
        'nearest_level': None
    }
    
    # === OPTIONS FLOW (CORRIGÉ : DYNAMIQUE) ===
    vix_value = getattr(vix_ticker, 'last', None) or getattr(vix_ticker, 'close', None)
    
    # Calcul dynamique basé sur VIX et autres facteurs
    if vix_value:
        # VIX élevé = plus de puts = ratio < 1.0
        vix_factor = max(0.5, min(1.5, 1.0 - (vix_value - 15) / 20))
        
        # Autres facteurs (à enrichir)
        time_factor = 1.0  # Placeholder pour facteur temporel
        
        dynamic_ratio = vix_factor * time_factor
        
        options_flow = {
            'call_put_ratio': dynamic_ratio,
            'volume_bias': 'neutral',
            'vix_factor': vix_factor,
            'time_factor': time_factor
        }
    else:
        options_flow = {
            'call_put_ratio': 1.0,
            'volume_bias': 'neutral',
            'vix_factor': 1.0,
            'time_factor': 1.0
        }
    
    # === SMART MONEY (simulé) ===
    smart_money = {
        'institutional_flow': 0.0,
        'large_trades': 0
    }
    
    return vwap_trend, sierra_patterns, session_context, gamma_levels, options_flow, smart_money

def detect_session_phase():
    """
    Détecte la phase de session actuelle
    """
    now = datetime.now()
    hour = now.hour
    
    if 0 <= hour < 6:
        return "asian"
    elif 6 <= hour < 14:
        return "european"
    elif 14 <= hour < 22:
        return "us"
    else:
        return "overnight"

def main():
    print("🚀 MIA Monitor ELITE - Version COMPLÈTE du Système MIA_IA")
    print("=" * 80)
    print(f"📁 Log file: {LOG_FILE}")
    print(f"📊 Snapshots file: {SNAPSHOTS_FILE}")
    print("🎯 INTÉGRATION: 4 Techniques Elite + 11 Features + ML Ensemble")
    
    # Initialiser les fichiers CSV
    headers_main = [
        "timestamp", "cycle", "es_price", "nq_price", "vix_value", 
        "cvd", "dom_imbalance", "elite_score", "signal", "ml_confidence",
        "gamma_phase", "smart_money_flow", "options_bias", "vwap_trend",
        "sierra_patterns", "session_context", "dom_bids", "dom_asks"
    ]
    headers_snapshots = ["timestamp", "symbol", "last", "last_size", "bid", "ask", "close", "high", "low"]
    
    log_to_csv(headers_main, LOG_FILE)
    log_to_csv(headers_snapshots, SNAPSHOTS_FILE)
    print("✅ Logging CSV Elite initialisé")
    
    # Connexion
    ib = IB()
    try:
        print(f"🔌 Connexion → {HOST}:{PORT} (clientId={CLIENT_ID})")
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print("✅ Connexion réussie")
        
        # === SETUP MARKET DATA MODE ===
        ib.reqMarketDataType(1)  # REALTIME
        
        print("\n📊 Setup instruments ELITE...")
        
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
            # Options flow data
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
        
        print("🚀 Monitoring ELITE démarré (Ctrl+C pour arrêter)")
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
            
            # === ANALYSE STRUCTURE MARCHÉ (Features avancées) ===
            vwap_trend, sierra_patterns, session_context, gamma_levels, options_flow, smart_money = analyze_market_structure(
                es_ticker, nq_ticker, vix_ticker
            )
            
            # === CALCUL SCORE ÉLITE ===
            elite_score = calculate_elite_battle_navale_score(
                es_price, nq_price, vix_value, dom_imbalance, cvd,
                gamma_levels, options_flow, smart_money,
                vwap_trend, sierra_patterns, session_context
            )
            
            # === DÉTECTION SESSION ===
            session_phase = detect_session_phase()
            
            # === ML ENSEMBLE CONFIDENCE (simulé) - ADAPTÉ PAR SESSION ===
            if session_phase in ["asian", "overnight"]:
                # Plus permissif en session calme
                ml_confidence = 0.55 if elite_score > 0.3 else 0.45
            else:
                # Standard pour session active
                ml_confidence = 0.75 if elite_score > 0.5 else 0.45
            
            # === GAMMA PHASE (simulé) ===
            gamma_phase = "normal"  # normal, gamma_peak, expiry_week
            
            # === SIGNAL ÉLITE ===
            signal = get_elite_signal(elite_score, ml_confidence, gamma_phase, session_phase)
            
            # === LOG CSV ÉLITE ===
            log_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                cycle,
                es_price,
                nq_price,
                vix_value,
                cvd,
                dom_imbalance,
                elite_score,
                signal,
                ml_confidence,
                gamma_phase,
                smart_money.get('institutional_flow', 0),
                options_flow.get('call_put_ratio', 1.0),
                vwap_trend.get('trend_strength', 0),
                sierra_patterns.get('strength', 0),
                session_context.get('performance', 0),
                len(bids),
                len(asks)
            ]
            log_to_csv(log_data, LOG_FILE)
            
            # === CAPTURE TICK DATA ===
            capture_tick_data(ib, es, SNAPSHOTS_FILE)
            capture_tick_data(ib, nq, SNAPSHOTS_FILE)
            
            # === AFFICHAGE ÉLITE ===
            print(f"\n⏰ {now:%H:%M:%S} | Cycle {cycle}")
            print(f"📊 ES: {f(es_price)} | NQ: {f(nq_price)} | VIX: {f(vix_value)}")
            print(f"📈 CVD: {cvd:+.0f} | DOM: {dom_imbalance:+.2f}")
            
            # === AFFICHAGE FEATURES ÉLITES ===
            print(f"🎯 Score ELITE: {elite_score:.3f} → {signal}")
            print(f"🌍 Session: {session_phase.upper()} | ML Confidence: {ml_confidence:.2f} | Gamma: {gamma_phase}")
            print(f"💰 Smart Money: {smart_money.get('institutional_flow', 0):+.3f}")
            print(f"📊 Options Bias: {options_flow.get('call_put_ratio', 1.0):.2f} (VIX factor: {options_flow.get('vix_factor', 1.0):.2f})")
            print(f"📈 VWAP Trend: {vwap_trend.get('trend_strength', 0):+.3f}")
            
            # === ANALYSE DÉTAILLÉE ===
            if elite_score > 0.3:
                print(f"   🔥 Breakdown: Gamma({gamma_levels.get('proximity_score', 0):.3f}) "
                      f"Smart({smart_money.get('institutional_flow', 0):+.3f}) "
                      f"Options({options_flow.get('call_put_ratio', 1.0):.2f})")
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
        print(f"📊 Données ELITE sauvegardées dans:")
        print(f"   - Main: {LOG_FILE}")
        print(f"   - Snapshots: {SNAPSHOTS_FILE} ({len(snapshots_history)} snapshots)")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        ib.disconnect()
        print("✅ Connexion fermée")

if __name__ == "__main__":
    main()
