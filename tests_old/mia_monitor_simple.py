#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mia_monitor_simple.py
Monitoring MIA_IA simplifié (test rapide)
Version: Test v1.0
"""

import time
import datetime
from ib_insync import *

# ============================================
# CONFIG SIMPLE
# ============================================
HOST = "127.0.0.1"
PORT = 7496  # Paper = 7497 | Live = 7496
CLIENT_ID = 43
REFRESH_SEC = 15

def simple_battle_navale_score(es_price, nq_price, vix_value, dom_imbalance, cvd):
    """Score Battle Navale simplifié"""
    score = 0.0
    
    # 1. DOM Imbalance (15%)
    if abs(dom_imbalance) > 0.2:
        score += 0.15
    
    # 2. CVD Flow (23%)
    if abs(cvd) > 50:
        score += 0.23
    
    # 3. VIX Sentiment (18%)
    if vix_value:
        if vix_value < 15:  # Complaisance
            score += 0.18
        elif vix_value > 25:  # Peur
            score += 0.09
    
    # 4. ES/NQ Correlation (7%)
    if es_price and nq_price:
        ratio = nq_price / es_price
        if abs(ratio - 3.6) < 0.2:  # Bonne corrélation
            score += 0.07
    
    return min(1.0, score)

def get_signal(score):
    """Signal simple"""
    if score >= 0.7:
        return "✅ LONG"
    elif score <= 0.3:
        return "❌ SHORT"
    else:
        return "➖ NEUTRAL"

def main():
    print("🚀 MIA Monitor Simple - Test Rapide")
    print("=" * 50)
    
    # Connexion
    ib = IB()
    try:
        print(f"🔌 Connexion → {HOST}:{PORT} (clientId={CLIENT_ID})")
        ib.connect(HOST, PORT, clientId=CLIENT_ID)
        print("✅ Connexion réussie")
        
        # Setup instruments
        print("\n📊 Setup instruments...")
        
        # ES Futures
        es_base = Future('ES', exchange="CME")
        es_det = ib.reqContractDetails(es_base)
        if es_det:
            es = es_det[0].contract
            print(f"✅ ES: {es.localSymbol}")
            ib.reqMktData(es, '', False, False)
            ib.reqMktDepth(es, numRows=5)  # Activer DOM
        else:
            print("❌ ES non trouvé")
            return
        
        # NQ Futures
        nq_base = Future('NQ', exchange="CME")
        nq_det = ib.reqContractDetails(nq_base)
        if nq_det:
            nq = nq_det[0].contract
            print(f"✅ NQ: {nq.localSymbol}")
            ib.reqMktData(nq, '', False, False)
        else:
            print("❌ NQ non trouvé")
            return
        
        # VIX
        vix = Index('VIX', 'CBOE')
        ib.qualifyContracts(vix)
        ib.reqMktData(vix, '', False, False)
        print("✅ VIX configuré")
        
        # Attendre données initiales
        print("⏳ Attente données...")
        for _ in range(5):
            ib.waitOnUpdate(timeout=1.0)
        
        # Variables
        cvd = 0
        last_es_price = None
        cycle = 0
        
        print("\n🚀 Monitoring démarré (Ctrl+C pour arrêter)")
        print("-" * 50)
        
        while True:
            cycle += 1
            now = datetime.datetime.now()
            
            # Récupérer données
            es_ticker = ib.ticker(es)
            nq_ticker = ib.ticker(nq)
            vix_ticker = ib.ticker(vix)
            
            # ES avec fallback robuste
            es_price = (
                es_ticker.last if es_ticker else None
                or ((es_ticker.bid + es_ticker.ask) / 2 if es_ticker and es_ticker.bid and es_ticker.ask else None)
                or es_ticker.close if es_ticker else None
            )
            
            # NQ avec fallback robuste
            nq_price = (
                nq_ticker.last if nq_ticker else None
                or ((nq_ticker.bid + nq_ticker.ask) / 2 if nq_ticker and nq_ticker.bid and nq_ticker.ask else None)
                or nq_ticker.close if nq_ticker else None
            )
            
            # VIX avec fallback
            vix_value = (
                vix_ticker.last if vix_ticker else None
                or vix_ticker.close if vix_ticker else None
            )
            
            # Update CVD
            if es_price and last_es_price:
                if es_price > last_es_price:
                    cvd += 1
                elif es_price < last_es_price:
                    cvd -= 1
            last_es_price = es_price
            
            # DOM Imbalance (corrigé - utiliser ticker.domBids/domAsks)
            dom_imbalance = 0.0
            try:
                if es_ticker and es_ticker.domBids and es_ticker.domAsks:
                    bid_vol = sum(b.size for b in es_ticker.domBids[:3])
                    ask_vol = sum(a.size for a in es_ticker.domAsks[:3])
                    if bid_vol + ask_vol > 0:
                        dom_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)
            except:
                pass
            
            # Calculer score
            score = simple_battle_navale_score(es_price, nq_price, vix_value, dom_imbalance, cvd)
            signal = get_signal(score)
            
            # Afficher
            print(f"\n⏰ {now:%H:%M:%S} | Cycle {cycle}")
            print(f"📊 ES: {es_price:.2f} | NQ: {nq_price:.2f} | VIX: {vix_value:.2f}")
            print(f"📈 CVD: {cvd:+.0f} | DOM: {dom_imbalance:+.2f}")
            print(f"🎯 Score: {score:.3f} → {signal}")
            
            # Debug info
            if nq_price is None or str(nq_price) == 'nan':
                print("⚠️ NQ: données manquantes (marché fermé ou pas de trades)")
            if dom_imbalance == 0.0:
                print("⚠️ DOM: pas d'imbalance détectée")
            print("-" * 40)
            
            time.sleep(REFRESH_SEC)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        ib.disconnect()
        print("✅ Connexion fermée")

if __name__ == "__main__":
    main()
