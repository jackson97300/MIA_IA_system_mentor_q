# -*- coding: utf-8 -*-
"""
Diagnostic minimal du freeze 'après init core'
- Force un mode offline (pas de réseau, pas de broker)
- Exécute les phases critiques sous timeout
- Dump les stacks de TOUTES les threads si ça bloque
- N'importe que le minimum, puis lit un Parquet 'bars' et boucle 100 pas

Usage:
  python tools/diag_freeze_min.py --data "/mnt/data" --timeout 20 --speed 0
"""

import os, sys, time, threading, traceback, argparse, importlib, types
from pathlib import Path

# ---- Correction du path pour trouver les modules du projet ----
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(f"📁 Project root ajouté au path: {project_root}")

# ---- Durcissement "offline" avant tout import du projet ----
os.environ.setdefault("MIA_USE_REAL_DATA", "0")
os.environ.setdefault("MIA_SIMULATION_MODE", "1")
os.environ.setdefault("MIA_DISABLE_BROKER", "1")
os.environ.setdefault("MIA_HEADLESS", "1")
os.environ.setdefault("NO_PROXY", "*")
os.environ.setdefault("HTTP_PROXY", "")
os.environ.setdefault("HTTPS_PROXY", "")
os.environ.setdefault("MPLBACKEND", "Agg")

# Si un module tente d'ouvrir des sockets: timeout court
try:
    import socket
    socket.setdefaulttimeout(2.0)
except Exception:
    pass

# Faulthandler pour dump en cas de blocage
try:
    import faulthandler
    faulthandler.enable()
except Exception:
    faulthandler = None

def dump_all_threads(reason="(unknown)"):
    print("\n========= THREAD DUMP (reason:", reason, ") =========", flush=True)
    try:
        frames = sys._current_frames()
        for th in threading.enumerate():
            fid = th.ident
            print(f"\n--- Thread: {th.name} (ident={fid}) ---")
            frame = frames.get(fid)
            if frame:
                stack = traceback.format_stack(frame)
                print("".join(stack).rstrip())
            else:
                print("(no frame)")
    except Exception as e:
        print("dump_all_threads error:", e)
    print("========= END THREAD DUMP =========\n", flush=True)

def run_phase(name, func, timeout_sec=20):
    """
    Exécute 'func' dans un thread avec timeout. Dump les stacks si bloqué.
    """
    print(f"\n▶️  PHASE: {name} (timeout {timeout_sec}s)")
    result = {"ok": False, "error": None, "ret": None}

    def _target():
        try:
            result["ret"] = func()
            result["ok"] = True
        except Exception as e:
            result["error"] = e

    t = threading.Thread(target=_target, name=f"phase:{name}", daemon=True)
    t.start()
    t.join(timeout=timeout_sec)
    if t.is_alive():
        print(f"⏳ Timeout sur la phase: {name}")
        dump_all_threads(reason=f"timeout:{name}")
        raise TimeoutError(f"Phase '{name}' a dépassé {timeout_sec}s")
    if result["error"]:
        raise result["error"]
    print(f"✅ PHASE OK: {name}")
    return result["ret"]

# ---------------------- Phases ----------------------

def phase_import_core():
    # Import très progressif du "core"
    start = time.perf_counter()
    core = importlib.import_module("core")  # doit logger l'init puis rendre la main
    dt = time.perf_counter() - start
    print(f"core importé en {dt:.3f}s ; modules chargés: {len(sys.modules)}")
    return core

def phase_config():
    start = time.perf_counter()
    cfg_mod = importlib.import_module("config.automation_config")
    AutomationConfig = getattr(cfg_mod, "AutomationConfig")
    cfg = AutomationConfig()
    dt = time.perf_counter() - start
    print(f"AutomationConfig OK en {dt:.3f}s")
    # Renforce offline côté code
    setattr(cfg, "simulation_mode", True)
    setattr(cfg, "use_real_data", False)
    # Execution params défensifs
    exe = getattr(cfg, "execution", {}) or {}
    exe.setdefault("slippage_ticks", 1)
    exe.setdefault("latency_ms", 50)
    setattr(cfg, "execution", exe)
    return cfg

def phase_light_modules(cfg):
    # N'importe que le minimum et en mode 'live=False'
    of_mod = importlib.import_module("features.orderflow_analyzer")
    val_mod = importlib.import_module("features.validation_engine")
    risk_mod = importlib.import_module("execution.risk_manager")
    exe_mod = importlib.import_module("execution.trading_executor")

    OrderFlowAnalyzer = getattr(of_mod, "OrderFlowAnalyzer")
    ValidationEngine  = getattr(val_mod, "ValidationEngine")
    RiskManager       = getattr(risk_mod, "RiskManager")
    TradingExecutor   = getattr(exe_mod, "TradingExecutor")

    analyzer = OrderFlowAnalyzer(cfg)
    validator = ValidationEngine(cfg)
    risk      = RiskManager(cfg)
    executor  = TradingExecutor(cfg, live=False)  # <- important

    print("Instances: analyzer/validator/risk/executor créées.")
    return analyzer, validator, risk, executor

def phase_read_bars(data_dir):
    # Lecture d'un seul parquet 'bars' (ultra minimal)
    import pandas as pd
    import os
    p = os.path.join(data_dir, "bars.parquet")
    df = pd.read_parquet(p)
    # Sanity
    need = {"ts","symbol","open","high","low","close"}
    if not need.issubset(df.columns):
        raise RuntimeError(f"Colonnes manquantes dans bars.parquet: {need - set(df.columns)}")
    df = df.sort_values(["ts","symbol"]).reset_index(drop=True)
    print(f"bars: {len(df)} lignes, {df['symbol'].unique().tolist()}")
    return df

def phase_mini_loop(df_bars, analyzer, validator, risk, executor, n_steps=100, sleep_speed=0.0):
    """
    Boucle minimale: on prend close comme price, volumes fictifs,
    on fait passer dans analyzer -> validator -> risk -> executor(sim)
    """
    import random
    seen = 0
    last_ts = None
    for _, row in df_bars.head(n_steps).iterrows():
        ts = int(row.ts)
        if sleep_speed and last_ts is not None:
            dt = max(0, ts - last_ts) / 1000.0
            if dt > 0:
                time.sleep(dt / sleep_speed)
        last_ts = ts

        md = {
            "symbol": str(row.symbol),
            "price": float(row.close),
            "volume": 1000,  # fictif mais constant
            "delta": 0.0,
            "bid_volume": 500,
            "ask_volume": 500,
            "timestamp": ts,
        }
        sig = analyzer.analyze_orderflow(md)
        if not sig:
            continue

        ok, reason, enriched = validator.validate_signal(sig)
        if not ok:
            continue
        if not risk.check_signal_confidence(sig):
            continue
        if not risk.check_daily_loss_limit():
            break
        _ = executor.simulate_orderflow_trade_with_leadership(sig)
        seen += 1

    print(f"Mini-loop: {n_steps} bars lues, {seen} signaux exécutés (sim)")
    return seen

# ---------------------- main ----------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Dossier Parquet (contient bars.parquet)")
    ap.add_argument("--timeout", type=int, default=20, help="Timeout par phase (s)")
    ap.add_argument("--steps", type=int, default=100, help="Nb de barres à rejouer")
    ap.add_argument("--speed", type=float, default=0.0, help=">0 pour rejouer plus vite que le temps réel")
    args = ap.parse_args()

    try:
        core = run_phase("import_core", phase_import_core, timeout_sec=args.timeout)
        cfg  = run_phase("config", lambda: phase_config(), timeout_sec=args.timeout)
        analyzer, validator, risk, executor = run_phase(
            "light_modules", lambda: phase_light_modules(cfg), timeout_sec=args.timeout
        )
        df_bars = run_phase("read_bars", lambda: phase_read_bars(args.data), timeout_sec=args.timeout)
        _ = run_phase("mini_loop", lambda: phase_mini_loop(df_bars, analyzer, validator, risk, executor, args.steps, args.speed), timeout_sec=max(args.timeout, 60))

        print("\n✅ DIAG MINIMAL: TOUTES LES PHASES ONT ABOUTI.")
    except Exception as e:
        print(f"\n❌ DIAG ÉCHEC: {e}")
        dump_all_threads(reason="exception")
        # Propager un code de sortie non 0 pour CI
        sys.exit(2)

if __name__ == "__main__":
    main()
