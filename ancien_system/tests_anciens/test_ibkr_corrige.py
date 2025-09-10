#!/usr/bin/env python3
"""
Script de test IBKR corrigé avec détection automatique des contrats
"""

from ib_insync import *
from datetime import datetime, timezone
import argparse
import pytz
from core.market_hours_manager import get_market_status, is_us_options_open
from core.spx_subscription_manager import subscribe_spx_marketdata

def is_market_open():
    """Vérifie si les marchés US sont ouverts (Futures + Options)"""
    market_status = get_market_status()
    return market_status['options_open'], market_status['description']

def test_ibkr_corrige(host: str = '127.0.0.1', port: int = 7497, client_id: int = 7):
    """Test de connexion IBKR avec corrections"""
    print("🚀 TEST CONNEXION IBKR CORRIGÉ")
    print("=" * 40)
    
    ib = IB()
    try:
        # Connexion Paper
        print(f"Tentative de connexion → host={host}, port={port}, clientId={client_id}")
        ib.connect(host, port, clientId=client_id)
        print("✅ Connexion réussie")
        print(f"TWS time: {ib.reqCurrentTime()}")
        
        # Vérifier le compte connecté
        accounts = ib.managedAccounts()
        print(f"Comptes disponibles: {accounts}")
        acc = accounts[0] if accounts else ''
        
        def is_paper_du(a: str) -> bool:
            return len(a) >= 3 and a[:2] == 'DU' and a[2].isdigit()
        
        if acc.startswith('DUM'):
            raise RuntimeError(f"Demo détecté ({acc}). Ouvre TWS Paper DU…, pas DUM/U.")
        elif acc.startswith('U'):
            print("⚠️ Live détecté (7496). Pour tester: DU… (7497).")
        elif is_paper_du(acc):
            print("✅ Paper détecté.")
        else:
            raise RuntimeError(f"Compte non reconnu: {acc}")
        
        # Forcer le mode live market data
        ib.reqMarketDataType(1)  # 1=REALTIME, 3=DELAYED
        print("✅ Market data mode: REALTIME")
        
        # -------- CHECK HORAIRES MARCHÉ --------
        market_open, market_status = is_market_open()
        print(f"\n🕐 STATUT MARCHÉ: {market_status}")
        if not market_open:
            print("⚠️  MARCHÉ FERMÉ → Volume/OI/OrderFlow indisponibles")
            print("   Les données L1/DOM restent disponibles")
            print("   📊 Greeks: possibles (si tick 106), Volume/OI: indisponibles hors 9h30-16h00 NY")
            print("   📊 DOM L2: dépend d'un abo CME Depth; si vide = abonnement manquant ou TWS à redémarrer")
        else:
            print("✅ MARCHÉ OUVERT → Toutes les données disponibles")
        
        # -------- ES FUTURES (résolution robuste) --------
        print("\n📊 TEST ES FUTURES:")
        
        # Diagnostic préliminaire
        matches = ib.reqMatchingSymbols('ES')
        print(f"[MATCH] ES: {len(matches)} résultats")
        for m in matches[:6]:
            print(f"  {m}")
        
        def pick_front_month(details):
            today = datetime.now(timezone.utc).strftime('%Y%m%d')
            cds = [d.contract for d in details if d.contract.lastTradeDateOrContractMonth]
            cds.sort(key=lambda c: c.lastTradeDateOrContractMonth)
            for c in cds:
                if c.lastTradeDateOrContractMonth >= today:
                    return c
            return cds[0] if cds else None
        
        found = None
        
        # 1) Essayer GLOBEX puis CME
        for ex in ("GLOBEX", "CME"):
            base = Future('ES', exchange=ex)
            det = ib.reqContractDetails(base)
            print(f"[TRY] ES on {ex}: {len(det)} candidates")
            if det:
                found = pick_front_month(det)
                if found:
                    break
        
        # 2) Si rien, tenter des contrats datés (prochains trimestres)
        if not found:
            year = datetime.now(timezone.utc).year
            for ym in (f"{year}09", f"{year}12", f"{year+1}03"):
                for ex in ("GLOBEX", "CME"):
                    cand = Future('ES', lastTradeDateOrContractMonth=ym, exchange=ex)
                    det = ib.reqContractDetails(cand)
                    print(f"[TRY] ES {ym} on {ex}: {len(det)} candidates")
                    if det:
                        found = det[0].contract
                        break
                if found:
                    break
        
        # 3) Dernier recours : localSymbol (ex: ESU5, ESZ5…)
        if not found:
            year_digit = datetime.now(timezone.utc).year % 10  # 2025 -> 5
            for ls in (f"ESU{year_digit}", f"ESZ{year_digit}"):
                for ex in ("CME", "GLOBEX"):
                    cand = Future(localSymbol=ls, exchange=ex)
                    det = ib.reqContractDetails(cand)
                    print(f"[TRY] localSymbol {ls} on {ex}: {len(det)} candidates")
                    if det:
                        found = det[0].contract
                        break
                if found:
                    break
        
        if not found:
            print("❌ ES introuvable → très probable : permission Futures (US) pas encore effective ou TWS non redémarré.")
        else:
            print(f"✅ ES sélectionné: {found.localSymbol} {found.lastTradeDateOrContractMonth} {found.exchange}")
            # L1
            tkr_es = ib.reqMktData(found, '', False, False)
            ib.sleep(2)
            print(f"ES L1: Bid={tkr_es.bid}, Ask={tkr_es.ask}, Last={tkr_es.last}")
            # DOM L2 (CME Depth requis)
            try:
                dom = ib.reqMktDepth(found, numRows=10)
                ib.sleep(2)
                print("ES DOM bids (top 5):", [(l.price, l.size) for l in dom.domBids[:5]])
                print("ES DOM asks (top 5):", [(l.price, l.size) for l in dom.domAsks[:5]])
                if not dom.domBids and not dom.domAsks:
                    print("⚠️ DOM vide → abonnement **CME L2/Depth** manquant ou TWS à redémarrer.")
            except Exception as e:
                print("❌ DOM L2 error:", e)
            
            # -------- ORDERFLOW DÉTAILLÉ (tick-by-tick) --------
            print("\n🔬 ORDERFLOW DÉTAILLÉ (tick-by-tick):")
            
            tbt_bbo    = ib.reqTickByTickData(found, "BidAsk",  0, False)
            tbt_trades = ib.reqTickByTickData(found, "AllLast", 0, False)
            
            best_bid = None
            best_ask = None
            buy_vol  = 0.0
            sell_vol = 0.0
            cvd      = 0.0
            trade_count = 0
            
            @tbt_bbo.updateEvent
            def _on_bbo(t):
                nonlocal best_bid, best_ask
                if t.bidPrice and t.bidPrice > 0: best_bid = t.bidPrice
                if t.askPrice and t.askPrice > 0: best_ask = t.askPrice
            
            @tbt_trades.updateEvent
            def _on_trade(t):
                nonlocal best_bid, best_ask, buy_vol, sell_vol, cvd, trade_count
                trade_count += 1
                px = float(t.price)
                sz = float(t.size or 0.0)
                if best_bid is not None and best_ask is not None:
                    if px >= best_ask:      buy_vol += sz; cvd += sz
                    elif px <= best_bid:    sell_vol += sz; cvd -= sz
                    else:
                        mid = 0.5*(best_bid + best_ask)
                        if px > mid:        buy_vol += sz; cvd += sz
                        elif px < mid:      sell_vol += sz; cvd -= sz
            
            # WARM-UP: attendre un BBO valide
            for _ in range(10):
                ib.waitOnUpdate(timeout=1.0)
                if (best_bid is not None) and (best_ask is not None):
                    break
            
            # Collecte 30s
            for _ in range(30):
                ib.waitOnUpdate(timeout=1.0)
            
            print(f"Trades observés = {trade_count} | Aggressive Buys = {buy_vol:.0f} | "
                  f"Aggressive Sells = {sell_vol:.0f} | CVD = {cvd:.0f}")
            
            if trade_count == 0 and not market_open:
                print("   → Normal (marché fermé)")
            elif trade_count == 0 and market_open:
                print("   → Vérifier la connexion ou les permissions")
            
            def _cancel_tbt(ib, sub):
                try:
                    ib.cancelTickByTickData(sub)
                    return
                except TypeError:
                    pass
                rid = getattr(sub, 'reqId', None)
                if rid is not None:
                    ib.client.cancelTickByTickData(rid)
            
            _cancel_tbt(ib, tbt_trades)
            _cancel_tbt(ib, tbt_bbo)
        
        # -------- NQ FUTURES (Nasdaq 100) --------
        print("\n📊 TEST NQ FUTURES:")
        
        # Recherche NQ sur CME directement
        nq_base = Future('NQ', exchange="CME")
        nq_det = ib.reqContractDetails(nq_base)
        print(f"[TRY] NQ on CME: {len(nq_det)} candidates")
        
        nq_found = None
        if nq_det:
            # Utiliser la même fonction pick_front_month que pour ES
            nq_found = pick_front_month(nq_det)
        
        # Si rien, tenter des contrats datés
        if not nq_found:
            year = datetime.now(timezone.utc).year
            for ym in (f"{year}09", f"{year}12", f"{year+1}03"):
                nq_cand = Future('NQ', lastTradeDateOrContractMonth=ym, exchange="CME")
                nq_det = ib.reqContractDetails(nq_cand)
                print(f"[TRY] NQ {ym} on CME: {len(nq_det)} candidates")
                if nq_det:
                    nq_found = nq_det[0].contract
                    break
        
        # Dernier recours : localSymbol
        if not nq_found:
            year_digit = datetime.now(timezone.utc).year % 10
            for ls in (f"NQU{year_digit}", f"NQZ{year_digit}"):
                nq_cand = Future(localSymbol=ls, exchange="CME")
                nq_det = ib.reqContractDetails(nq_cand)
                print(f"[TRY] localSymbol {ls} on CME: {len(nq_det)} candidates")
                if nq_det:
                    nq_found = nq_det[0].contract
                    break
        
        if not nq_found:
            print("❌ NQ introuvable → vérifier permission Futures (US)")
        else:
            print(f"✅ NQ sélectionné: {nq_found.localSymbol} {nq_found.lastTradeDateOrContractMonth} {nq_found.exchange}")
            
            # L1 NQ
            tkr_nq = ib.reqMktData(nq_found, '', False)
            for _ in range(12): ib.waitOnUpdate(timeout=1.0)
            print(f"NQ L1: Bid={tkr_nq.bid}, Ask={tkr_nq.ask}, Last={tkr_nq.last}")
            
            # DOM L2 NQ
            try:
                nq_dom = ib.reqMktDepth(nq_found, numRows=5)
                for _ in range(5): ib.waitOnUpdate(timeout=1.0)
                print("NQ DOM bids (top 3):", [(l.price, l.size) for l in nq_dom.domBids[:3]])
                print("NQ DOM asks (top 3):", [(l.price, l.size) for l in nq_dom.domAsks[:3]])
            except Exception as e:
                print("❌ NQ DOM L2 error:", e)
        
        # -------- SPX OPTIONS (détection propre) --------
        print("\n📈 TEST SPX OPTIONS:")
        
        # 1) Récupérer le conId de l'index SPX (CBOE)
        spx_idx = Index('SPX', 'CBOE')
        cd = ib.reqContractDetails(spx_idx)
        if not cd:
            print("❌ SPX index introuvable → 'Index Options (US – CBOE/C2)' non active sur le compte ou TWS à redémarrer.")
        else:
            uconid = cd[0].contract.conId
            print("SPX index conId:", uconid)
            
            # 2) Lire la chaîne avec le VRAI underlyingConId
            params = ib.reqSecDefOptParams('SPX', '', 'IND', uconid)
            if not params or not params[0].expirations:
                print("❌ Chaîne SPX vide → autorisation 'Options sur indice – US (CBOE/C2)' indisponible/inactive.")
            else:
                p = params[0]
                expiries = sorted(p.expirations)
                strikes = sorted(float(s) for s in p.strikes if s is not None)
                
                # 3) Choix ATM SPX robuste
                from statistics import median
                
                # 1) tenter le spot index
                t_spx = ib.reqMktData(spx_idx, '', False)
                for _ in range(15): ib.waitOnUpdate(timeout=1.0)
                px = t_spx.last or t_spx.close or ((t_spx.bid + t_spx.ask) / 2 if t_spx.bid and t_spx.ask else None)
                
                # 2) si toujours None, probe via Greeks pour récupérer undPrice
                if not px:
                    mid_strike = median(strikes)
                    probe = Option('SPX', expiries[0], mid_strike, 'C', 'CBOE', 'USD')
                    ib.qualifyContracts(probe)
                    tk = ib.reqMktData(probe, genericTickList='106', snapshot=False)
                    for _ in range(12): ib.waitOnUpdate(timeout=1.0)
                    px = getattr(tk.modelGreeks, 'undPrice', None) or mid_strike
                    if px != mid_strike:
                        print(f"⚠️ SPX spot via Greeks fallback: {px}")
                
                # 3) choisir l'ATM final avec expiry valide
                strike = min(strikes, key=lambda k: abs(k - px))
                
                # Trouver une expiry valide (vendredi pour SPXW)
                valid_expiry = None
                for exp in expiries[:10]:  # Vérifier les 10 premières
                    try:
                        d = datetime.strptime(exp, "%Y%m%d").date()
                        if d.weekday() == 4:  # Vendredi
                            valid_expiry = exp
                            break
                    except:
                        continue
                
                if not valid_expiry:
                    valid_expiry = expiries[0]  # Fallback
                
                expiry = valid_expiry
                print(f"SPX spot: {px}, Chosen strike: {strike}, expiry: {expiry}")
                
                # 4) Construire l'option CBOE avec tradingClass correct
                def is_third_friday(yyyymmdd: str) -> bool:
                    from datetime import datetime
                    d = datetime.strptime(yyyymmdd, "%Y%m%d").date()
                    return d.weekday() == 4 and 15 <= d.day <= 21  # vendredi et 15–21 => 3e vendredi
                
                def qualify_spx_option(ib, expiry: str, strike: float, right='C'):
                    # 1) Choisir la classe attendue
                    tr_class = 'SPX' if is_third_friday(expiry) else 'SPXW'
                    print(f"🔍 Recherche SPX {tr_class} pour {expiry} @ {strike}")
                    
                    # 2) Essayer plusieurs places avec la classe principale
                    for ex in ('CBOE', 'CBOE2', 'SMART'):
                        opt = Option('SPX', expiry, strike, right,
                                     exchange=ex, currency='USD',
                                     tradingClass=tr_class, multiplier='100')
                        cds = ib.reqContractDetails(opt)
                        if cds:
                            print(f"✅ Trouvé {tr_class} sur {ex}")
                            return cds[0].contract
                    
                    # 3) Fallback : essayer l'autre classe
                    alt_class = 'SPX' if tr_class == 'SPXW' else 'SPXW'
                    print(f"🔄 Fallback vers {alt_class}")
                    for ex in ('CBOE', 'CBOE2', 'SMART'):
                        opt = Option('SPX', expiry, strike, right,
                                     exchange=ex, currency='USD',
                                     tradingClass=alt_class, multiplier='100')
                        cds = ib.reqContractDetails(opt)
                        if cds:
                            print(f"✅ Trouvé {alt_class} sur {ex}")
                            return cds[0].contract
                    
                    print(f"❌ Aucune option SPX trouvée pour {expiry} @ {strike}")
                    return None
                
                opt = qualify_spx_option(ib, expiry, strike, 'C')
                if not opt:
                    # aide au debug : montre les 5 premières échéances et 10 strikes autour d'ATM
                    print("❌ SPX option introuvable pour", expiry, strike, "(SPXW/SPX). Essaie une autre place ou une autre expiry.")
                else:
                    print(f"SPX option ({opt.tradingClass} @ {opt.exchange}):", opt.localSymbol)
                    tkr_opt = ib.reqMktData(opt, genericTickList='106', snapshot=False)
                    
                    # Attente optimisée pour les Greeks (45s max)
                    for _ in range(45):  # 45 x 1s
                        ib.waitOnUpdate(timeout=1.0)
                        if tkr_opt.modelGreeks:
                            break
                    
                    # Si toujours None, 1 resubscribe propre puis re-attente 30s
                    if not tkr_opt.modelGreeks:
                        ib.cancelMktData(opt)
                        tkr_opt = ib.reqMktData(opt, genericTickList='106', snapshot=False)
                        for _ in range(30):
                            ib.waitOnUpdate(timeout=1.0)
                            if tkr_opt.modelGreeks:
                                break
                    
                    print("SPX Greeks:", tkr_opt.modelGreeks)
        
        # -------- OPTIONS FLOW (Volume & Open Interest) --------
        print("\n📦 OPTIONS FLOW (volume / open interest):")
        
        # Utiliser le nouveau gestionnaire de souscription SPX optimisé
        if opt:
            tkr_opt_flow = subscribe_spx_marketdata(ib, opt)
            if tkr_opt_flow:
                vol = getattr(tkr_opt_flow, 'optionVolume', None)
                oi = getattr(tkr_opt_flow, 'optionOpenInterest', None)
                print(f"Option Volume={vol if vol is not None else 'n/a'} | Open Interest={oi if oi is not None else 'n/a'}")
            else:
                print("❌ Échec souscription SPX")
                vol = oi = None
        else:
            print("❌ Contrat SPX non disponible")
            vol = oi = None
        
        # -------- CORRELATION ES/NQ --------
        print("\n🔗 CORRELATION ES/NQ:")
        
        # Vérifier si ES et NQ ont été trouvés
        if 'found' in locals() and 'nq_found' in locals() and found and nq_found:
            # Récupérer les prix ES et NQ
            es_price = tkr_es.last if tkr_es.last else ((tkr_es.bid + tkr_es.ask) / 2 if tkr_es.bid and tkr_es.ask else None)
            nq_price = tkr_nq.last if tkr_nq.last else ((tkr_nq.bid + tkr_nq.ask) / 2 if tkr_nq.bid and tkr_nq.ask else None)
            
            if es_price and nq_price:
                # Calculer le ratio de corrélation
                correlation_ratio = nq_price / es_price
                
                # Calculer les variations
                es_change = tkr_es.last - tkr_es.close if tkr_es.last and tkr_es.close else 0
                nq_change = tkr_nq.last - tkr_nq.close if tkr_nq.last and tkr_nq.close else 0
                
                # Direction de corrélation
                if es_change > 0 and nq_change > 0:
                    correlation_direction = "✅ POSITIVE"
                elif es_change < 0 and nq_change < 0:
                    correlation_direction = "✅ POSITIVE"
                elif es_change > 0 and nq_change < 0:
                    correlation_direction = "❌ NEGATIVE"
                elif es_change < 0 and nq_change > 0:
                    correlation_direction = "❌ NEGATIVE"
                else:
                    correlation_direction = "➖ NEUTRAL"
                
                print(f"ES: {es_price:.2f} | NQ: {nq_price:.2f}")
                print(f"Ratio NQ/ES: {correlation_ratio:.4f}")
                print(f"ES Change: {es_change:+.2f} | NQ Change: {nq_change:+.2f}")
                print(f"Correlation: {correlation_direction}")
                
                # Score de corrélation pour MIA_IA (0-1)
                correlation_score = min(abs(correlation_ratio - 3.6) / 0.5, 1.0)  # Normalisé autour de 3.6
                print(f"Correlation Score: {correlation_score:.3f}")
            else:
                print("❌ Prix ES ou NQ non disponibles")
        else:
            print("❌ ES ou NQ non trouvés")
        
        # -------- VIX (spot + futures + DOM) --------
        print("\n📊 TEST VIX:")
        
        # VIX spot (CBOE)
        vix_idx = Index('VIX', 'CBOE')
        ib.qualifyContracts(vix_idx)
        
        # Live d'abord
        ib.reqMarketDataType(1)
        tkr_vix = ib.reqMktData(vix_idx, '', False)
        for _ in range(20): ib.waitOnUpdate(timeout=1.0)
        spot = tkr_vix.last or (tkr_vix.bid and tkr_vix.ask and (tkr_vix.bid + tkr_vix.ask) / 2) or tkr_vix.close
        
        # Fallback: delayed si toujours None
        if spot is None:
            ib.cancelMktData(vix_idx)
            ib.reqMarketDataType(3)  # DELAYED
            tkr_vix = ib.reqMktData(vix_idx, '', False)
            for _ in range(12): ib.waitOnUpdate(timeout=1.0)
            spot = tkr_vix.last or (tkr_vix.bid and tkr_vix.ask and (tkr_vix.bid + tkr_vix.ask) / 2) or tkr_vix.close
        
        print(f"VIX spot: {spot if spot is not None else 'NaN'}")
        
        # VX futures: désactivé tant que CFE n'est pas souscrit
        print("\n== VX futures ==\nIgnoré (pas de permission CFE).")
        
        # -------- TEST CONTRATS HORS MARCHÉ (reqContractDetails) --------
        print("\n🔍 TEST CONTRATS HORS MARCHÉ (reqContractDetails):")
        
        # Test SPX Options
        print("\n📈 TEST SPX OPTIONS (reqContractDetails):")
        spx_opt = Option('SPX', '20250918', 6400, 'C', 'CBOE', 'USD', tradingClass='SPX')
        spx_details = ib.reqContractDetails(spx_opt)
        if spx_details:
            print(f"✅ SPX Options reconnues: {len(spx_details)} contrats trouvés")
            for i, detail in enumerate(spx_details[:3]):  # Afficher les 3 premiers
                contract = detail.contract
                print(f"  {i+1}. {contract.localSymbol} - Strike: {contract.strike} - Expiry: {contract.lastTradeDateOrContractMonth}")
        else:
            print("❌ SPX Options non reconnues")
        
        # Test VIX Options
        print("\n📊 TEST VIX OPTIONS (reqContractDetails):")
        vix_opt = Option('VIX', '20250918', 15, 'C', 'CFE', 'USD')
        vix_details = ib.reqContractDetails(vix_opt)
        if vix_details:
            print(f"✅ VIX Options reconnues: {len(vix_details)} contrats trouvés")
            for i, detail in enumerate(vix_details[:3]):  # Afficher les 3 premiers
                contract = detail.contract
                print(f"  {i+1}. {contract.localSymbol} - Strike: {contract.strike} - Expiry: {contract.lastTradeDateOrContractMonth}")
        else:
            print("❌ VIX Options non reconnues")
        
        # Test QQQ Options
        print("\n📈 TEST QQQ OPTIONS (reqContractDetails):")
        qqq_opt = Option('QQQ', '20250918', 400, 'C', 'SMART', 'USD')
        qqq_details = ib.reqContractDetails(qqq_opt)
        if qqq_details:
            print(f"✅ QQQ Options reconnues: {len(qqq_details)} contrats trouvés")
            for i, detail in enumerate(qqq_details[:3]):  # Afficher les 3 premiers
                contract = detail.contract
                print(f"  {i+1}. {contract.localSymbol} - Strike: {contract.strike} - Expiry: {contract.lastTradeDateOrContractMonth}")
        else:
            print("❌ QQQ Options non reconnues")
        
        # Résumé des abonnements
        print("\n📋 RÉSUMÉ DES ABONNEMENTS:")
        abonnements_actifs = []
        if spx_details:
            abonnements_actifs.append("✅ OPRA (CBOE Options)")
        if vix_details:
            abonnements_actifs.append("✅ CFE (VIX Options)")
        if qqq_details:
            abonnements_actifs.append("✅ OPRA (NASDAQ Options)")
        
        if abonnements_actifs:
            print("Abonnements actifs:")
            for abonnement in abonnements_actifs:
                print(f"  {abonnement}")
        else:
            print("❌ Aucun abonnement options actif")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        print("\n🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS/Gateway est lancé")
        print("2. Vérifiez le port (7497 pour Paper)")
        print("3. Vérifiez les abonnements data (CME, OPRA, CFE)")
        print("4. Changez clientId si nécessaire")
    
    finally:
        ib.disconnect()
        print("\n✅ Test terminé")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de test IBKR corrigé")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Hôte TWS/IBG")
    parser.add_argument("--port", type=int, default=7497, help="Port API (TWS Paper=7497, Gateway Paper=4002)")
    parser.add_argument("--clientId", type=int, default=7, help="Identifiant client unique")
    args = parser.parse_args()

    test_ibkr_corrige(host=args.host, port=args.port, client_id=args.clientId)
