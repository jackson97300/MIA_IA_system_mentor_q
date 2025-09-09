#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest robuste MIA_IA avec patch dynamique intégré - SANS CORE
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import sys
import argparse
import json
import time
from pathlib import Path
from collections import defaultdict
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

# Désactiver les imports core problématiques
os.environ['MIA_SKIP_CORE_INIT'] = '1'

def run_backtest_robuste(scenario="confluence_breakout", leadership="NQ_leads", strength=0.18, 
                        preset="baseline", minutes=30):
    """Backtest avec patch dynamique intégré"""
    
    print(f"🚀 BACKTEST ROBUSTE - {scenario} | {leadership} | {preset}")
    print("=" * 60)
    
    try:
        # 1. Import direct du générateur (sans core)
        print("📦 Import direct du générateur...")
        
        # --- Import sans-core robuste: on neutralise 'from __future__ import annotations' pour dataclasses (Py 3.13) ---
        from types import ModuleType
        gen_path = Path(__file__).parent / "core" / "mia_data_generator.py"
        src = gen_path.read_text(encoding="utf-8")

        # Supprime proprement la future-annotation (ligne complète, avec espaces possibles)
        src = "\n".join(
            line for line in src.splitlines()
            if "from __future__ import annotations" not in line.strip()
        )

        mia_module = ModuleType("mia_data_generator")
        mia_module.__file__ = str(gen_path)
        exec(compile(src, str(gen_path), "exec"), mia_module.__dict__)

        MIA_IA_DataGenerator = mia_module.MIA_IA_DataGenerator
        GenConfig = mia_module.GenConfig
        print("✅ Générateur importé directement (future annotations neutralisées)")
        
        # 2. Configuration selon preset
        cfg = GenConfig(
            start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
            minutes=minutes
        )
        
        # Presets d'exécution
        execution_configs = {
            "baseline": {"slippage_ticks": 1, "latency_ms": 80, "max_bars_in_trade": 60},
            "stress": {"slippage_ticks": 2, "latency_ms": 120, "max_bars_in_trade": 120},
            "tight-stops": {"slippage_ticks": 0, "latency_ms": 40, "max_bars_in_trade": 30},
            "optimized": {
                "slippage_ticks": 1,
                "latency_ms": 60,
                "max_bars_in_trade": 180,
                "position_size": 1,
                "stop_ticks": 6,             # Stop plus serré pour NQ
                "takeprofit_rr": 1.8,
                "symbol_specs": {
                    "ES": {"tick_size": 0.25, "tick_value": 12.5, "point_value": 50, "enabled": False},  # Désactivé
                    "NQ": {"tick_size": 0.25, "tick_value": 5.0,  "point_value": 20, "enabled": True},
                },
                # flags d'exits avancées
                "intrabar_exits": True,      # TP/Stop intrabar
                "be_enable": True,           # break-even
                "be_trigger_ratio": 0.6,     # arme BE plus tôt (0.6R au lieu de 0.8R)
                "trail_be_ticks": 2,         # BE+2 ticks au lieu de 1
            }
        }
        
        execution_config = execution_configs.get(preset, execution_configs["baseline"])
        
        # PATCH 3: Configuration exécution avec tick values corrects (pour presets non-optimized)
        if preset != "optimized":
            base_config = {
                "position_size": 1,           # 1 contrat
                "stop_ticks": 8,              # ~100$ risque ES, ~40$ NQ
                "takeprofit_rr": 1.6,         # TP à 1.6R
                "max_bars_in_trade": 120,     # 2 minutes si bar=1s
                "symbol_specs": {
                    "ES": {"tick_size": 0.25, "tick_value": 12.5, "point_value": 50},
                    "NQ": {"tick_size": 0.25, "tick_value": 5.0,  "point_value": 20},
                }
            }
            execution_config.update(base_config)
        
        # Configuration risque
        risk_config = {
            "daily_max_loss_pct": 0.02,
            "use_unrealized_for_daily_limit": False  # coupe-circuit sur le RÉALISÉ uniquement
        }
        
        print(f"⚙️ Preset: {preset} - {execution_config}")
        
        # PATCH 4: Afficher les paramètres de sécurité
        R = execution_config.get("stop_ticks", 8)
        RR = execution_config.get("takeprofit_rr", 1.6)
        max_profit_ticks = int(R * RR)
        print(f"🔒 Sécurité: Stop={R} ticks, TP={RR}R, Max profit={max_profit_ticks} ticks")
        
        # 3. Génération de données
        print("\n📊 Génération de données...")
        gen = MIA_IA_DataGenerator(seed=42)
        
        # Générer plusieurs scénarios pour équilibrer
        data_up = gen.generate_realistic_session(cfg, scenario=scenario, leadership=leadership, strength=strength)
        
        cfg.start = datetime(2025, 8, 21, 14, 0, tzinfo=timezone.utc)
        data_dn = gen.generate_realistic_session(cfg, scenario="orderflow_distribution", leadership="ES_leads", strength=strength)
        
        # Fusionner les données
        bars = pd.concat([data_up["bars"], data_dn["bars"]], ignore_index=True)
        leadership_features = pd.concat([data_up["leadership_features"], data_dn["leadership_features"]], ignore_index=True)
        context = pd.concat([data_up["context"], data_dn["context"]], ignore_index=True)
        ground_truth = pd.concat([data_up["ground_truth"], data_dn["ground_truth"]], ignore_index=True)
        
        print(f"✅ Données générées: {len(bars)} bars, {len(leadership_features)} leadership")
        
        # 4. PATCH DYNAMIQUE INTÉGRÉ - Calcul des quantiles par symbole
        print("\n🔧 PATCH DYNAMIQUE - Calcul quantiles par symbole...")
        
        # Préparation des données
        bars["ts_min"] = (bars["ts"] // 60000) * 60000
        context["ts_min"] = (context["ts"] // 60000) * 60000
        
        # Quantiles par symbole - PLUS SOUPLES
        leadership_q = leadership_features.groupby("symbol")["leadership_strength"] \
                                         .quantile([0.25, 0.75]).unstack().rename(columns={0.25:"q25", 0.75:"q75"})  # Retour à 0.25/0.75
        
        print(f"📊 Quantiles calculés:")
        for sym in leadership_q.index:
            print(f"  {sym}: q25={leadership_q.loc[sym, 'q25']:.3f}, q75={leadership_q.loc[sym, 'q75']:.3f}")
        
        # PATCH 2: Seuils adaptatifs pour distribution plate
        def adaptive_thresholds(sym):
            q25 = float(leadership_q.loc[sym, "q25"]) if sym in leadership_q.index else 0.35
            q75 = float(leadership_q.loc[sym, "q75"]) if sym in leadership_q.index else 0.65
            if (q75 - q25) < 0.06:  # Distribution trop plate
                # élargir un peu les fourchettes
                m = (q75 + q25) / 2.0
                q25 = max(0.0, m - 0.10)
                q75 = min(1.0, m + 0.10)
            return q25, q75
        
        # Fusion des données
        merged = bars.merge(leadership_features, on=["ts", "symbol"], how="left") \
                     .merge(context[["ts_min", "vix", "put_call_ratio"]], on="ts_min", how="left")
        
        # PATCH 2: Garantir l'ordre temporel
        merged = merged.sort_values(["symbol", "ts"]).reset_index(drop=True)
        
        # 5. État de trading par symbole - PATCH 1: débloquer la génération
        state = defaultdict(lambda: {"buy": 0, "sell": 0, "last_ts": None})  # Retiré "open"
        target, tol, cooldown_bars = 0.50, 0.15, 8  # budget & cooldown augmenté
        
        # DIAGNOSTIC 2: Compteur de raisons de rejet
        reject = {"cooldown": 0, "budget": 0, "concurrency": 0, "daily": 0}
        
        def can_fire(sym, side, ts, reject_counter):
            st = state[sym]
            tot = st["buy"] + st["sell"] + 1e-9
            # cooldown par symbole
            if st["last_ts"] and (ts - st["last_ts"]) < cooldown_bars * 1000:
                reject_counter["cooldown"] += 1
                return False
            # budget anti-biais
            buy_ratio = st["buy"] / tot if tot > 0 else 0.5
            if side == "BUY" and buy_ratio > (target + tol):
                reject_counter["budget"] += 1
                return False
            if side == "SELL" and (1 - buy_ratio) > (target + tol):
                reject_counter["budget"] += 1
                return False
            return True
        
        # 6. Génération des signaux avec patch dynamique
        print("\n🎯 Génération des signaux...")
        signals = []
        
        for _, row in merged.iterrows():
            sym, ts = row["symbol"], int(row["ts"])
            
            # PATCH 2: Récupération des quantiles adaptatifs
            q25, q75 = adaptive_thresholds(sym)
            
            # Features
            ls = float(row.get("leadership_strength", 0.0))
            conf = float(row.get("confluence_score", 0.0))
            vol = float(row.get("volume_imbalance", 0.0))
            pcr = float(row.get("put_call_ratio", 1.0))
            vix = float(row.get("vix", 15.0))
            
            # Gates de confluence (plus sélectifs)
            bull_gate = (conf >= 0.55 and vol >= 0.25) or (vix < 15 and pcr < 0.90)
            bear_gate = (conf >= 0.55 and vol <= -0.25) or (vix > 25 and pcr > 1.20)
            
            # Décision
            side = None
            if ls >= q75 or (ls >= q75 - 0.02 and bull_gate):
                side = "BUY"
            elif ls <= q25 or (ls <= q25 + 0.02 and bear_gate):
                side = "SELL"
            
            # Vérification et enregistrement
            if side and can_fire(sym, side, ts, reject):
                signals.append({
                    "timestamp": ts,
                    "symbol": sym,
                    "side": side,
                    "price": float(row["close"]),
                    "confidence": float(ls),
                    "leadership_strength": float(ls),
                    "confluence_score": float(conf),
                    "volume_imbalance": float(vol)
                })
                st = state[sym]
                st["last_ts"] = ts
                st[side.lower()] += 1
        
        print(f"✅ {len(signals)} signaux générés")
        
        # 7. Statistiques des signaux
        if signals:
            df_signals = pd.DataFrame(signals)
            buy_count = len(df_signals[df_signals["side"] == "BUY"])
            sell_count = len(df_signals[df_signals["side"] == "SELL"])
            total_signals = len(df_signals)
            
            print(f"\n📊 STATISTIQUES SIGNAUX:")
            print(f"  BUY: {buy_count} ({buy_count/total_signals*100:.1f}%)")
            print(f"  SELL: {sell_count} ({sell_count/total_signals*100:.1f}%)")
            print(f"  Total: {total_signals}")
            
            if 45 <= (buy_count/total_signals*100) <= 55:
                print("  ✅ Ratio équilibré !")
            else:
                print("  ⚠️ Ratio déséquilibré")
        
        # 8. Simulation d'exécution avec PATCH 3 - Tick values corrects
        print(f"\n💼 Simulation d'exécution ({preset})...")
        
        fills = []
        positions = {}
        initial_capital = 100000
        current_capital = initial_capital
        last_px = {}  # Prix courants par symbole
        
        # PATCH B: Compteur de clamps
        clamp_hit = {"neg": 0, "pos": 0}
        
        # DIAGNOSTIC 2: Compteur de raisons de rejet
        reject = {"cooldown": 0, "budget": 0, "concurrency": 0, "daily": 0}
        
        # DIAGNOSTIC 3: Compteur de sorties avancées
        exit_reasons = {"be_stop": 0, "timeout": 0, "hard_stop": 0, "take_profit": 0}
        
        for signal in signals:
            sym = signal["symbol"]
            side = signal["side"]
            price = signal["price"]
            ts = signal["timestamp"]
            
            # Mise à jour du prix courant
            last_px[sym] = price
            
            # Récupération des spécifications du symbole
            symbol_specs = execution_config["symbol_specs"].get(sym, {"tick_size": 0.25, "tick_value": 12.5, "point_value": 50, "enabled": True})
            
            # Vérifier si le symbole est activé
            if not symbol_specs.get("enabled", True):
                continue  # Ignorer ce symbole
                
            tick_value = symbol_specs["tick_value"]
            tick_size = symbol_specs["tick_size"]
            
            # Gestion des positions existantes
            if sym in positions:
                pos = positions[sym]
                # Fermeture si position opposée
                if (pos["side"] == "BUY" and side == "SELL") or (pos["side"] == "SELL" and side == "BUY"):
                    # Calcul PnL avec tick values corrects
                    if pos["side"] == "BUY":
                        pnl_ticks = (price - pos["price"]) / tick_size
                    else:
                        pnl_ticks = (pos["price"] - price) / tick_size
                    
                    # PATCH 1: Sécuriser le PnL par trade (clamp stop/TP)
                    R = execution_config.get("stop_ticks", 8)
                    RR = execution_config.get("takeprofit_rr", 1.6)
                    max_profit_ticks = int(R * RR)
                    
                    # filet de sécurité: borne le PnL par trade
                    pnl_ticks_raw = pnl_ticks
                    pnl_ticks = max(-R, min(pnl_ticks, max_profit_ticks))
                    
                    # PATCH B: Compteur de clamps
                    if pnl_ticks == -R:
                        clamp_hit["neg"] += 1
                    if pnl_ticks == max_profit_ticks:
                        clamp_hit["pos"] += 1
                    
                    pnl = pnl_ticks * tick_value * pos["size"]
                    
                    # Slippage en ticks
                    slippage_ticks = execution_config["slippage_ticks"]
                    slippage_cost = slippage_ticks * tick_value * pos["size"]
                    pnl -= slippage_cost
                    
                    current_capital += pnl
                    fills.append({
                        "ts": ts,
                        "symbol": sym,
                        "side": "CLOSE_" + pos["side"],
                        "price": price,
                        "size": pos["size"],
                        "pnl": pnl,
                        "pnl_ticks": pnl_ticks,
                        "capital": current_capital
                    })
                    del positions[sym]
            
            # Ouverture nouvelle position
            if sym not in positions:
                size = execution_config["position_size"]  # 1 contrat
                positions[sym] = {
                    "side": side,
                    "price": price,
                    "size": size,
                    "open_ts": ts,
                    "be_armed": False,
                    "trail_stop": None
                }
                
                fills.append({
                    "ts": ts,
                    "symbol": sym,
                    "side": side,
                    "price": price,
                    "size": size,
                    "pnl": 0,
                    "pnl_ticks": 0,
                    "capital": current_capital
                })
            
            # --- Sorties intrabar / trailing (activées par flags preset) ---
            intrabar = execution_config.get("intrabar_exits", False)
            be_en = execution_config.get("be_enable", False)
            be_ratio = float(execution_config.get("be_trigger_ratio", 0.8))
            be_ticks = int(execution_config.get("trail_be_ticks", 1))
            
            for psym, pos in list(positions.items()):
                spec = execution_config["symbol_specs"].get(psym, {"tick_size": 0.25, "tick_value": 12.5})
                tick_size = spec["tick_size"]
                
                curr = last_px.get(psym, pos["price"])
                pnl_ticks = (curr - pos["price"]) / tick_size if pos["side"]=="BUY" else (pos["price"] - curr) / tick_size
                pnl_ticks = float(pnl_ticks)
                
                R = execution_config.get("stop_ticks", 8)
                RR = execution_config.get("takeprofit_rr", 1.6)
                max_profit_ticks = int(R * RR)
                
                if intrabar:
                    # Stop dur intrabar
                    if pnl_ticks <= -R:
                        # Fermeture position
                        pnl = -R * spec["tick_value"] * pos["size"]
                        current_capital += pnl
                        fills.append({
                            "ts": ts,
                            "symbol": psym,
                            "side": "CLOSE_" + pos["side"],
                            "price": curr,
                            "size": pos["size"],
                            "pnl": pnl,
                            "pnl_ticks": -R,
                            "capital": current_capital
                        })
                        del positions[psym]
                        clamp_hit["neg"] += 1
                        exit_reasons["hard_stop"] += 1
                        continue
                    # TP anticipé intrabar
                    if pnl_ticks >= max_profit_ticks:
                        # Fermeture position
                        pnl = max_profit_ticks * spec["tick_value"] * pos["size"]
                        current_capital += pnl
                        fills.append({
                            "ts": ts,
                            "symbol": psym,
                            "side": "CLOSE_" + pos["side"],
                            "price": curr,
                            "size": pos["size"],
                            "pnl": pnl,
                            "pnl_ticks": max_profit_ticks,
                            "capital": current_capital
                        })
                        del positions[psym]
                        clamp_hit["pos"] += 1
                        exit_reasons["take_profit"] += 1
                        continue
                
                if be_en:
                    be_trigger = max(1, int(R * be_ratio))
                    if not pos.get("be_armed", False) and pnl_ticks >= be_trigger:
                        pos["be_armed"] = True
                        pos["trail_stop"] = (pos["price"] + be_ticks * tick_size) if pos["side"]=="BUY" else (pos["price"] - be_ticks * tick_size)
                    
                    if pos.get("be_armed", False) and pos.get("trail_stop") is not None:
                        if pos["side"] == "BUY" and curr <= pos["trail_stop"]:
                            # Fermeture BE
                            pnl = (pos["trail_stop"] - pos["price"]) / tick_size * spec["tick_value"] * pos["size"]
                            current_capital += pnl
                            fills.append({
                                "ts": ts,
                                "symbol": psym,
                                "side": "CLOSE_" + pos["side"],
                                "price": curr,
                                "size": pos["size"],
                                "pnl": pnl,
                                "pnl_ticks": (pos["trail_stop"] - pos["price"]) / tick_size,
                                "capital": current_capital
                            })
                            del positions[psym]
                            exit_reasons["be_stop"] += 1
                            continue
                        if pos["side"] == "SELL" and curr >= pos["trail_stop"]:
                            # Fermeture BE
                            pnl = (pos["price"] - pos["trail_stop"]) / tick_size * spec["tick_value"] * pos["size"]
                            current_capital += pnl
                            fills.append({
                                "ts": ts,
                                "symbol": psym,
                                "side": "CLOSE_" + pos["side"],
                                "price": curr,
                                "size": pos["size"],
                                "pnl": pnl,
                                "pnl_ticks": (pos["price"] - pos["trail_stop"]) / tick_size,
                                "capital": current_capital
                            })
                            del positions[psym]
                            exit_reasons["be_stop"] += 1
                            continue
        
        # 9. Fermeture des positions en fin de session
        print("🔚 Fermeture des positions...")
        
        # PATCH 2: Fermer au bon prix par symbole
        last_close_by_sym = merged.groupby("symbol")["close"].last().to_dict()
        
        for sym, pos in positions.items():
            # Prix de fermeture (dernier prix du symbole)
            close_price = float(last_close_by_sym.get(sym, pos["price"]))
            
            # Récupération des spécifications du symbole
            symbol_specs = execution_config["symbol_specs"].get(sym, {"tick_size": 0.25, "tick_value": 12.5, "point_value": 50})
            tick_value = symbol_specs["tick_value"]
            tick_size = symbol_specs["tick_size"]
            
            # Calcul PnL avec tick values corrects
            if pos["side"] == "BUY":
                pnl_ticks = (close_price - pos["price"]) / tick_size
            else:
                pnl_ticks = (pos["price"] - close_price) / tick_size
            
            # PATCH 1: Sécuriser le PnL par trade (clamp stop/TP) - Fermeture finale
            R = execution_config.get("stop_ticks", 8)
            RR = execution_config.get("takeprofit_rr", 1.6)
            max_profit_ticks = int(R * RR)
            
            # filet de sécurité: borne le PnL par trade
            pnl_ticks_raw = pnl_ticks
            pnl_ticks = max(-R, min(pnl_ticks, max_profit_ticks))
            
            # PATCH B: Compteur de clamps
            if pnl_ticks == -R:
                clamp_hit["neg"] += 1
            if pnl_ticks == max_profit_ticks:
                clamp_hit["pos"] += 1
            
            pnl = pnl_ticks * tick_value * pos["size"]
            
            current_capital += pnl
            fills.append({
                "ts": merged["ts"].max(),
                "symbol": sym,
                "side": "CLOSE_" + pos["side"],
                "price": close_price,
                "size": pos["size"],
                "pnl": pnl,
                "pnl_ticks": pnl_ticks,
                "capital": current_capital
            })
        
        # 10. Calcul des métriques
        print(f"\n📈 MÉTRIQUES DE PERFORMANCE:")
        
        df_fills = pd.DataFrame(fills)
        total_pnl = current_capital - initial_capital
        total_return = (total_pnl / initial_capital) * 100
        
        # Trades gagnants/perdants
        trades = df_fills[df_fills["side"].str.startswith("CLOSE")]
        winning_trades = trades[trades["pnl"] > 0]
        losing_trades = trades[trades["pnl"] < 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if len(trades) > 0 else 0
        profit_factor = abs(winning_trades["pnl"].sum() / losing_trades["pnl"].sum()) if len(losing_trades) > 0 and losing_trades["pnl"].sum() != 0 else float('inf')
        
        # Drawdown
        df_fills["cumulative_pnl"] = df_fills["pnl"].cumsum()
        df_fills["equity"] = initial_capital + df_fills["cumulative_pnl"]
        df_fills["peak"] = df_fills["equity"].expanding().max()
        df_fills["drawdown"] = (df_fills["equity"] - df_fills["peak"]) / df_fills["peak"] * 100
        max_drawdown = df_fills["drawdown"].min()
        
        print(f"  Capital initial: ${initial_capital:,.0f}")
        print(f"  Capital final: ${current_capital:,.0f}")
        print(f"  PnL total: ${total_pnl:,.0f} ({total_return:+.2f}%)")
        print(f"  Nombre de trades: {len(trades)}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Profit Factor: {profit_factor:.2f}")
        print(f"  Max Drawdown: {max_drawdown:.2f}%")
        
        # PATCH B: Affichage des clamps
        print(f"  Clamps: -R={clamp_hit['neg']}  +RR={clamp_hit['pos']}")
        
        # DIAGNOSTIC 2: Affichage des rejets
        print(f"  🧾 Rejects: {reject}")
        
        # DIAGNOSTIC 3: Affichage des sorties avancées
        print(f"  🎯 Exits: BE={exit_reasons['be_stop']} TP={exit_reasons['take_profit']} Stop={exit_reasons['hard_stop']} Timeout={exit_reasons['timeout']}")
        
        # 11. Accord avec Ground Truth - PATCH A: Score à l'entrée
        print(f"\n🎯 ACCORD AVEC GROUND TRUTH:")
        
        if len(trades) > 0:
            # PATCH 4: Fix du SettingWithCopyWarning
            trades = trades.copy()
            trades.loc[:, "ts_min"] = (trades["ts"] // 60000) * 60000
            
            # PATCH 3: Corriger la comparaison Ground Truth
            gt = ground_truth.copy()
            gt["ts_min"] = (gt["ts"] // 60000) * 60000
            
            j = trades.merge(gt[["ts_min", "symbol", "side"]], 
                           on=["ts_min", "symbol"], how="left", suffixes=("_trade", "_gt"))
            
            # trade → +1 / -1
            j["side_trade_numeric"] = j["side_trade"].map({"CLOSE_BUY": 1, "CLOSE_SELL": -1}).fillna(0)
            
            # GT → déjà numérique (1, -1, 0)
            j["side_gt_numeric"] = np.sign(j["side_gt"]).fillna(0).astype(int)
            
            agreement = ((j["side_trade_numeric"] == j["side_gt_numeric"]) & 
                        (j["side_gt_numeric"] != 0)).mean()
            
            print(f"  Accord directionnel (clôture): {agreement:.1%}")
        
        # PATCH A: Score vs GT à l'entrée
        df_fills = pd.DataFrame(fills)
        entries = df_fills[df_fills["side"].isin(["BUY", "SELL"])].copy()
        if not entries.empty:
            entries["ts_min"] = (entries["ts"] // 60000) * 60000
            gt2 = ground_truth.copy()
            gt2["ts_min"] = (gt2["ts"] // 60000) * 60000

            j = entries.merge(gt2[["ts_min", "symbol", "side"]], on=["ts_min", "symbol"], how="left",
                             suffixes=("_trade", "_gt"))
            # trade side numérique (+1/-1)
            j["side_trade_numeric"] = j["side_trade"].map({"BUY": 1, "SELL": -1}).fillna(0)
            # GT déjà numérique
            j["side_gt_numeric"] = np.sign(j["side_gt"]).fillna(0).astype(int)

            agreement = ((j["side_trade_numeric"] == j["side_gt_numeric"]) &
                        (j["side_gt_numeric"] != 0)).mean()
            print(f"  Accord directionnel (entrée): {agreement:.1%}")
        
        # DIAGNOSTIC 1: Mesurer pourquoi l'accord GT est bas
        print(f"\n🔍 DIAGNOSTIC GROUND TRUTH:")
        
        # Coverage GT
        gt = ground_truth.copy()
        gt["is_labeled"] = (gt["side"] != 0).astype(int)
        coverage = gt["is_labeled"].mean()
        print(f"  🧭 GT coverage: {coverage:.1%}")
        
        # Entrées vs fenêtres GT (même minute)
        entries = df_fills[df_fills["side"].isin(["BUY", "SELL"])].copy()
        entries["ts_min"] = (entries["ts"] // 60000) * 60000
        gt["ts_min"] = (gt["ts"] // 60000) * 60000
        j = entries.merge(gt[["ts_min", "symbol", "side"]], on=["ts_min", "symbol"], how="left", suffixes=("_trade", "_gt"))
        in_win = (j["side_gt"].fillna(0) != 0).mean()
        print(f"  🎯 Entrées en fenêtre GT (min): {in_win:.1%}")
        
        # Accord à horizon ±60s
        H = 60_000
        def in_horizon(e):
            w = gt[(gt["symbol"] == e.symbol) & (gt["ts"].between(e.ts - H, e.ts + H))]
            if w.empty:
                return np.nan
            sgn = 1 if e.side_trade == "BUY" else -1
            return int((np.sign(w["side"]).abs().max() > 0) and (sgn == int(np.sign(w["side"]).mode().iat[0])))
        
        acc_h = j.apply(lambda r: in_horizon(r), axis=1)
        print(f"  📐 Accord directionnel (±60s): {np.nanmean(acc_h)*100:.1f}%")
        
        # DIAGNOSTIC 3: Cohérence par symbole (ES vs NQ)
        print(f"\n📊 STATISTIQUES PAR SYMBOLE:")
        if len(df_fills) > 0:
            # Filtrer les trades fermés
            closed_trades = df_fills[df_fills["side"].str.startswith("CLOSE")].copy()
            if len(closed_trades) > 0:
                sym_stats = closed_trades.groupby("symbol").agg({
                    "pnl": ["count", lambda s: (s > 0).mean(), lambda s: s[s > 0].sum() / max(1e-9, -s[s < 0].sum())]
                }).round(3)
                sym_stats.columns = ["trades", "winrate", "pf"]
                print(sym_stats)
        
        # 12. Conclusion
        print(f"\n📋 CONCLUSION:")
        if total_return > 0 and win_rate > 50:
            print(f"  ✅ SUCCÈS: Backtest profitable avec {preset}")
            print(f"  🎯 Ratio BUY/SELL équilibré: {buy_count/total_signals*100:.1f}%/{sell_count/total_signals*100:.1f}%")
            success = True
        else:
            print(f"  ⚠️ PERFORMANCE MIXTE: PnL {total_return:+.2f}%, Win Rate {win_rate:.1f}%")
            success = False
        
        # 13) Rapport JSON (robuste, indépendant des noms amont)
        try:
            import json, time

            Path("reports").mkdir(exist_ok=True)

            # Recalcule proprement depuis 'trades' (au cas où 'closes' n'existe pas ici)
            if 'trades' not in locals() or trades is None or trades.empty:
                raise RuntimeError("Impossible de générer un rapport: 'trades' est vide.")
            closed = trades[trades["side"].isin(["CLOSE_BUY","CLOSE_SELL"])].copy()

            # Win rate / PF / PnL total
            wr = float((closed["pnl"] > 0).mean()) if not closed.empty else 0.0
            gross_pos = float(closed.loc[closed["pnl"] > 0, "pnl"].sum()) if not closed.empty else 0.0
            gross_neg = float(-closed.loc[closed["pnl"] < 0, "pnl"].sum()) if not closed.empty else 0.0
            pf_safe = gross_pos / max(1e-9, gross_neg)
            total_pnl = float(closed["pnl"].sum()) if not closed.empty else 0.0

            # Max drawdown (reconstruit au besoin)
            start_capital = 100_000.0
            if "capital" in trades.columns and not trades["capital"].isna().all():
                eq = trades["capital"].dropna().astype(float)
                max_dd_abs = float((eq.cummax() - eq).max()) if not eq.empty else 0.0
            else:
                # Reconstruit l'équité à partir des fermetures
                eq = start_capital + closed["pnl"].cumsum()
                max_dd_abs = float((eq.cummax() - eq).max()) if not eq.empty else 0.0
            max_dd_pct = (max_dd_abs / start_capital) * 100.0

            # Stats par symbole (si dispo)
            es_pf = nq_pf = None
            if not closed.empty:
                sym_stats = closed.groupby("symbol").agg(
                    trades=("pnl","size"),
                    winrate=("pnl", lambda s: float((s>0).mean())),
                    pf=("pnl", lambda s: float(s[s>0].sum() / max(1e-9, -s[s<0].sum())))
                )
                if "ES" in sym_stats.index: es_pf = float(sym_stats.loc["ES","pf"])
                if "NQ" in sym_stats.index: nq_pf = float(sym_stats.loc["NQ","pf"])

            total_signals = int(len(signals)) if 'signals' in locals() else None
            closed_trades = int(len(closed))

            report = {
                "timestamp": int(time.time()),
                "scenario": scenario,
                "leadership": leadership,
                "preset": preset,
                "minutes": 120,  # adapte si tu changes la durée
                "signals": total_signals,
                "trades": closed_trades,
                "winrate_pct": round(wr*100, 3),
                "pf": round(pf_safe, 3),
                "pnl_pct": round((total_pnl / start_capital) * 100.0, 3),
                "maxdd_pct": round(max_dd_pct, 3),
                "clamps": clamp_hit if 'clamp_hit' in locals() else None,
                "es_pf": es_pf,
                "nq_pf": nq_pf,
                "success": bool(total_pnl >= 0.0),
            }

            out = Path("reports") / f"backtest_{preset}_{scenario}_{leadership}_{int(time.time())}.json"
            out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"📄 Rapport sauvegardé: {out}")

        except Exception as e:
            print(f"⚠️ Erreur génération rapport: {e}")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur backtest: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_scenarios(preset: str, strength: float = 0.18, minutes: int = 30):
    """Lance une suite de scénarios avec leadership automatique"""
    plan = [
        ("confluence_breakout", "NQ_leads"),
        ("orderflow_distribution", "ES_leads"),
        ("trend_up", "balanced"),
        ("trend_down", "balanced"),
    ]
    
    print(f"\n🚀 LANCEMENT SUITE MULTI-SCÉNARIOS - Preset: {preset}")
    print("=" * 60)
    
    results = []
    for i, (scenario, leadership) in enumerate(plan, 1):
        print(f"\n📊 SCÉNARIO {i}/4: {scenario} | {leadership}")
        print("-" * 40)
        
        success = run_backtest_robuste(scenario, leadership, strength, preset, minutes)
        results.append({
            "scenario": scenario,
            "leadership": leadership,
            "success": success
        })
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ MULTI-SCÉNARIOS")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"Tests réussis: {successful_tests}/{total_tests}")
    
    if successful_tests >= total_tests * 0.75:
        print("✅ SYSTÈME TRÈS ROBUSTE: 75%+ des tests réussis")
    elif successful_tests >= total_tests * 0.5:
        print("✅ SYSTÈME ROBUSTE: Majorité des tests réussis")
    else:
        print("⚠️ SYSTÈME À AMÉLIORER: Trop d'échecs")
    
    return results

def main():
    """Lancement des tests avec support arguments ligne de commande"""
    parser = argparse.ArgumentParser(description="Backtest robuste MIA_IA")
    parser.add_argument("--scenario", default="confluence_breakout", 
                       choices=["confluence_breakout", "orderflow_distribution", "trend_up", "trend_down", "delta_divergence"],
                       help="Scénario de marché")
    parser.add_argument("--leadership", default="auto",
                       choices=["NQ_leads", "ES_leads", "balanced", "auto"],
                       help="Mode leadership (ou 'auto' selon scénario)")
    parser.add_argument("--preset", default="baseline",
                       choices=["baseline", "stress", "tight-stops", "optimized"],
                       help="Preset d'exécution")
    parser.add_argument("--strength", type=float, default=0.18,
                       help="Force du scénario (0.1-0.3)")
    parser.add_argument("--minutes", type=int, default=30,
                       help="Durée en minutes")
    parser.add_argument("--all-scenarios", action="store_true",
                       help="Exécute une suite de scénarios")
    
    args = parser.parse_args()
    
    if args.all_scenarios:
        # Mode multi-scénarios
        run_all_scenarios(args.preset, args.strength, args.minutes)
    else:
        # Mode single run
        print("🎯 PLAN D'EXÉCUTION - BACKTEST ROBUSTE")
        print("=" * 60)
        
        # leadership auto si demandé
        if args.leadership == "auto":
            auto_map = {
                "confluence_breakout": "NQ_leads",
                "orderflow_distribution": "ES_leads",
                "trend_up": "balanced",
                "trend_down": "balanced",
            }
            lead = auto_map.get(args.scenario, "balanced")
        else:
            lead = args.leadership
            
        print(f"🧪 TEST - {args.scenario} | {lead} | {args.preset}")
        success = run_backtest_robuste(args.scenario, lead, args.strength, args.preset, args.minutes)
        
        if success:
            print("✅ TEST RÉUSSI")
        else:
            print("❌ TEST ÉCHOUÉ")

if __name__ == "__main__":
    main()

