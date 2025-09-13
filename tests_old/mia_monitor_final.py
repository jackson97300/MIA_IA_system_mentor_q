#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mia_monitor_final.py
Monitoring MIA_IA - Version Finale Patchée avec Logging Complet
Version: Final v1.0 + CSV Logs + Trades + Snapshots
"""

import time
import math
import csv
from datetime import datetime, timezone
from ib_insync import *

# ============================================
# CONFIG SIMPLE
# ============================================
HOST = "127.0.0.1"
PORT = 7496  # Paper = 7497 | Live = 7496
CLIENT_ID = 50
REFRESH_SEC = 15

# Logging CSV
LOG_FILE = f"mia_monitor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
SNAPSHOTS_FILE = f"mia_snapshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

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




def mid_or(value1, value2):
    """Calcule le mid price avec gestion d'erreurs"""
    try:
        if value1 is not None and value2 is not None:
            return (value1 + value2) / 2
    except Exception:
        pass
    return None

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

def simple_battle_navale_score(es_price, nq_price, vix_value, dom_imbalance, cvd):
    """Score Battle Navale simplifié - Seuils ajustés pour session calme"""
    score = 0.0
    
    # 1. DOM Imbalance (15%) - Seuil abaissé pour session calme
    if abs(dom_imbalance) > 0.05:  # 0.05 au lieu de 0.2
        score += 0.15
    
    # 2. CVD Flow (23%) - Seuil abaissé pour session calme
    if abs(cvd) > 10:  # 10 au lieu de 50
        score += 0.23
    
    # 3. VIX Sentiment (18%) - Ajusté pour session calme
    if vix_value:
        if vix_value < 15:  # Complaisance
            score += 0.18
        elif vix_value > 25:  # Peur
            score += 0.09
        elif 15 <= vix_value <= 20:  # Normal
            score += 0.05  # Petit bonus pour normalité
    
    # 4. ES/NQ Correlation (7%) - Seuil élargi
    if es_price and nq_price:
        ratio = nq_price / es_price
        if abs(ratio - 3.6) < 0.3:  # 0.3 au lieu de 0.2
            score += 0.07
    
    # 5. Bonus pour activité détectée (10%)
    if abs(dom_imbalance) > 0.02 or abs(cvd) > 5:
        score += 0.10
    
    return min(1.0, score)

def get_signal(score):
    """Signal simple - Logique corrigée pour éviter biais SHORT"""
    if score >= 0.6:  # Seuil abaissé pour LONG
        return "✅ LONG"
    elif score <= 0.1:  # Seuil abaissé pour SHORT (éviter biais)
        return "❌ SHORT"
    else:
        return "➖ NEUTRAL"  # Zone neutre élargie

def main():
    print("🚀 MIA Monitor Final - Version Patchée avec Logging Complet")
    print("=" * 70)
    print(f"📁 Log file: {LOG_FILE}")
    print(f"📊 Snapshots file: {SNAPSHOTS_FILE}")
    
    # Initialiser les fichiers CSV
    headers_main = ["timestamp", "cycle", "es_price", "nq_price", "vix_value", "cvd", "dom_imbalance", "score", "signal", "dom_bids", "dom_asks"]
    headers_snapshots = ["timestamp", "symbol", "last", "last_size", "bid", "ask", "close", "high", "low"]
    
    log_to_csv(headers_main, LOG_FILE)
    log_to_csv(headers_snapshots, SNAPSHOTS_FILE)
    print("✅ Logging CSV initialisé (main + snapshots)")
    
    # Connexion
    ib = IB()
    try:
        print(f"🔌 Connexion → {HOST}:{PORT} (clientId={CLIENT_ID})")
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print("✅ Connexion réussie")
        
        # Note: Les callbacks tradeEvent et pendingTickersEvent ne sont pas disponibles dans ib_insync
        # La capture des trades se fait via tick-by-tick data
        
        # --- setup market data mode ---
        ib.reqMarketDataType(1)  # REALTIME
        
        print("\n📊 Setup instruments...")
        
        # --- ES ---
        es = pick_front_month(ib, 'ES', 'CME')
        if not es:
            raise RuntimeError("ES introuvable (permissions CME ?)")
        print(f"✅ ES: {es.localSymbol} @ {es.exchange}")
        tkr_es = ib.reqMktData(es, '', False, False)
        ib.reqMktDepth(es, numRows=5)
        # Tick-by-tick pour capturer tous les trades
        ib.reqTickByTickData(es, "AllLast", 0, False)
        
        # --- NQ ---
        nq = pick_front_month(ib, 'NQ', 'CME')
        if not nq:
            raise RuntimeError("NQ introuvable (permissions CME ?)")
        print(f"✅ NQ: {nq.localSymbol} @ {nq.exchange}")
        tkr_nq = ib.reqMktData(nq, '', False, False)
        # Tick-by-tick pour capturer tous les trades
        ib.reqTickByTickData(nq, "AllLast", 0, False)
        
        # --- VIX (index) ---
        vix = Index("VIX", "CBOE")
        ib.qualifyContracts(vix)
        ib.reqMktData(vix, "", False, False)
        print("✅ VIX configuré")
        
        # --- warm-up pour remplir les tickers ---
        print("⏳ Attente données initiales (12 s)...")
        for _ in range(12):
            ib.waitOnUpdate(timeout=1.0)
        
        # --- lecture robuste sans fallback magique ---
        es_price = best_price(ib.ticker(es))
        nq_price = best_price(ib.ticker(nq))
        
        # si rien en live, tenter delayed (rare la nuit)
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
        print("🚀 Monitoring démarré (Ctrl+C pour arrêter)")
        print("-" * 70, flush=True)
        
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
            
            # Si pas de données, on attend un peu au lieu d'imprimer de vieux close
            if es_price is None or nq_price is None:
                ib.waitOnUpdate(timeout=0.5)
                es_price = best_price(ib.ticker(es))
                nq_price = best_price(ib.ticker(nq))
            
            # CVD basé sur variation last/close si last absent
            trade_size = safe_num(getattr(es_ticker, "lastSize", None))
            ref_price = es_price
            if ref_price and trade_size:
                if last_es_price is not None:
                    if ref_price > last_es_price:
                        cvd += trade_size
                    elif ref_price < last_es_price:
                        cvd -= trade_size
                last_es_price = ref_price
            
            # DOM imbalance + gardes
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
            
            # Calculer score
            score = simple_battle_navale_score(es_price, nq_price, vix_value, dom_imbalance, cvd)
            signal = get_signal(score)
            
            # Log CSV principal
            log_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                cycle,
                es_price,
                nq_price,
                vix_value,
                cvd,
                dom_imbalance,
                score,
                signal.replace("✅", "LONG").replace("❌", "SHORT").replace("➖", "NEUTRAL"),
                len(bids),
                len(asks)
            ]
            log_to_csv(log_data, LOG_FILE)
            
            # Capture des données de tick pour ES et NQ
            capture_tick_data(ib, es, SNAPSHOTS_FILE)
            capture_tick_data(ib, nq, SNAPSHOTS_FILE)
            
            # Impression toujours lisible + avertissements clairs
            print(f"\n⏰ {now:%H:%M:%S} | Cycle {cycle}")
            print(f"📊 ES: {f(es_price)} | NQ: {f(nq_price)} | VIX: {f(vix_value)}")
            print(f"📈 CVD: {cvd:+.0f} | DOM: {dom_imbalance:+.2f}")
            
            if es_price is None:
                print("⚠️ ES: pas de prix (RTH off / pas de tick).")
            if nq_price is None:
                print("⚠️ NQ: pas de prix (marché calme ou abonnement).")
            if vix_value is None:
                print("⚠️ VIX: pas de prix (indice hors push).")
            
            # Affichage du score avec analyse détaillée
            print(f"🎯 Score: {score:.3f} → {signal}")
            
            # Analyse détaillée du score pour debug
            if score > 0.1:
                print(f"   📊 Breakdown: DOM({abs(dom_imbalance):.3f}) CVD({abs(cvd)}) VIX({vix_value:.1f})")
            else:
                print(f"   💤 Marché calme - Score faible (normal en session asiatique)")
            
            # Info DOM détaillée
            bids = getattr(es_ticker, "domBids", []) or []
            asks = getattr(es_ticker, "domAsks", []) or []
            print(f"🔍 DOM: {len(bids)} bids, {len(asks)} asks")
            print(f"💾 Log: {LOG_FILE}")
            print(f"📊 Snaps: {len(snapshots_history)}")
            print("-" * 70, flush=True)
            
            time.sleep(REFRESH_SEC)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêté par l'utilisateur")
        print(f"📊 Données sauvegardées dans:")
        print(f"   - Main: {LOG_FILE}")
        print(f"   - Snapshots: {SNAPSHOTS_FILE} ({len(snapshots_history)} snapshots)")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        ib.disconnect()
        print("✅ Connexion fermée")

if __name__ == "__main__":
    main()
