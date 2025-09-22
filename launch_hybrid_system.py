#!/usr/bin/env python3
"""
Lanceur du système MIA IA v2.1-Hybrid
Version améliorée avec validation automatique et monitoring
"""

import subprocess
import sys
import os
import time
import argparse
import datetime
import json
import signal
from typing import Optional, Dict, Any

# Variables globales pour le monitoring
trading_process: Optional[subprocess.Popen] = None
unifier_process: Optional[subprocess.Popen] = None

def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêt propre"""
    print(f"\n🛑 Signal {signum} reçu - Arrêt en cours...")
    cleanup_processes()
    sys.exit(0)

def cleanup_processes():
    """Nettoie les processus en cours"""
    global trading_process, unifier_process
    
    if trading_process:
        print("🛑 Arrêt du système de trading...")
        trading_process.terminate()
        try:
            trading_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            trading_process.kill()
        trading_process = None
    
    if unifier_process:
        print("🛑 Arrêt du unifier...")
        unifier_process.terminate()
        try:
            unifier_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            unifier_process.kill()
        unifier_process = None

def validate_data_files(date: str = None) -> bool:
    """Valide les fichiers de données avant lancement"""
    if not date:
        date = datetime.datetime.now().strftime("%Y%m%d")
    
    print(f"=== VALIDATION DES DONNÉES ({date}) ===")
    
    try:
        cmd = ["python", "utils/enhanced_data_validator.py", "--date", date]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Validation des données réussie")
            return True
        else:
            print("❌ Validation des données échouée:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def get_system_status() -> Dict[str, Any]:
    """Récupère le statut du système"""
    status = {
        "timestamp": datetime.datetime.now().isoformat(),
        "trading_running": trading_process is not None and trading_process.poll() is None,
        "unifier_running": unifier_process is not None and unifier_process.poll() is None,
        "trading_pid": trading_process.pid if trading_process else None,
        "unifier_pid": unifier_process.pid if unifier_process else None
    }
    return status

def monitor_system():
    """Monitore le système en cours d'exécution"""
    print("=== MONITORING SYSTÈME ===")
    print("Appuyez sur Ctrl+C pour arrêter")
    
    try:
        while True:
            status = get_system_status()
            
            if status["trading_running"]:
                print(f"✅ Trading actif (PID: {status['trading_pid']})")
            else:
                print("❌ Trading arrêté")
                
            if status["unifier_running"]:
                print(f"✅ Unifier actif (PID: {status['unifier_pid']})")
            else:
                print("❌ Unifier arrêté")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring arrêté")

def launch_unifier(date: str = None, background: bool = False) -> bool:
    """Lance le unifier avec les paramètres optimaux et structure organisée"""
    global unifier_process
    
    if not date:
        date = "today"
    
    print("=== LANCEMENT MIA UNIFIER v2.1-HYBRID ===")
    print(f"  - Date: {date}")
    print("  - Structure organisée: DATA_SIERRA_CHART/DATA_YYYY/MONTH_NAME/YYYYMMDD/")
    print("  - Création automatique des dossiers")
    print("  - Fallback vers ancienne structure si nécessaire")
    print()
    
    cmd = [
        "python", "features/mia_unifier.py",
        "--indir", ".",
        "--date", date,
        "--minute-mode",
        "--max_depth_levels", "20",
        "--append-stream",
        "--watch-seconds", "55",
        "--ttl-seconds", "7200",
        "--correlation-ttl-seconds", "600",
        "--rollover-bytes", "134217728",
        "--timezone-offset", "-6",
        "--pg-distance", "2.5",
        "--touch-thr", "1.0",
        "--zone-cooldown", "300", 
        "--menthorq-decisions",
        "--mia-optimal",
        "--verbose"
    ]
    
    print(f"Commande: {' '.join(cmd)}")
    print()
    
    try:
        if background:
            # Lancer en arrière-plan
            unifier_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"✅ Unifier lancé en arrière-plan (PID: {unifier_process.pid})")
            return True
        else:
            # Lancer en mode synchrone
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Unifier terminé avec succès")
                print("Sortie:")
                print(result.stdout)
                return True
            else:
                print("❌ Erreur unifier:")
                print(result.stderr)
                return False
            
    except Exception as e:
        print(f"❌ Erreur lancement unifier: {e}")
        return False

def launch_trading_system(paper_trading=True, background: bool = False):
    """Lance le système de trading COMPLET (16 stratégies + Risk Manager + Sierra Chart)"""
    global trading_process
    
    print("=== LANCEMENT SYSTÈME DE TRADING COMPLET ===")
    print("  - 16 stratégies de trading")
    print("  - Risk Manager avancé")
    print("  - Trading Executor avec Sierra Chart")
    print("  - Advanced Metrics calculator")
    print("  - Market Regime Detector")
    print("  - Performance Tracker")
    print("  - Validation automatique des données")
    print()
    
    cmd = [
        "python", "LAUNCH/launch_24_7_menthorq_final.py"
    ]
    
    if paper_trading:
        cmd.extend(["--paper-trading"])
        print("  - Mode: PAPER TRADING")
    else:
        print("  - Mode: LIVE TRADING")
    
    print(f"Commande: {' '.join(cmd)}")
    print()
    
    try:
        if background:
            # Lancer en arrière-plan
            trading_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"✅ Système de trading COMPLET lancé en arrière-plan (PID: {trading_process.pid})")
            return True
        else:
            # Lancer en mode synchrone
            trading_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print(f"✅ Système de trading COMPLET lancé (PID: {trading_process.pid})")
            print("Appuyez sur Ctrl+C pour arrêter")
            
            # Attendre l'interruption
            try:
                trading_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé...")
                cleanup_processes()
                print("✅ Système arrêté")
            
    except Exception as e:
        print(f"❌ Erreur lancement système: {e}")
        return False

def main():
    # Configuration des gestionnaires de signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Lanceur système MIA IA v2.1-Hybrid amélioré")
    parser.add_argument("--unifier-only", action="store_true", help="Lancer seulement le unifier")
    parser.add_argument("--trading-only", action="store_true", help="Lancer seulement le système de trading")
    parser.add_argument("--live", action="store_true", help="Mode live (pas paper trading)")
    parser.add_argument("--date", type=str, default="today", help="Date à traiter (YYYYMMDD ou 'today')")
    parser.add_argument("--validate-only", action="store_true", help="Valider seulement les données")
    parser.add_argument("--monitor", action="store_true", help="Mode monitoring seulement")
    parser.add_argument("--background", action="store_true", help="Lancer en arrière-plan")
    parser.add_argument("--no-validation", action="store_true", help="Passer la validation des données")
    
    args = parser.parse_args()
    
    print("=== MIA IA SYSTEM v2.1-HYBRID LANCER ===")
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print(f"Date cible: {args.date}")
    print()
    
    # Mode validation seulement
    if args.validate_only:
        validate_data_files(args.date)
        return
    
    # Mode monitoring seulement
    if args.monitor:
        monitor_system()
        return
    
    # Validation des données (sauf si désactivée)
    if not args.no_validation:
        if not validate_data_files(args.date):
            print("❌ Validation échouée - Arrêt du système")
            return
    
    # Mode unifier seulement
    if args.unifier_only:
        launch_unifier(args.date, background=args.background)
        if not args.background:
            print("✅ Unifier terminé")
        return
    
    # Mode trading seulement
    if args.trading_only:
        launch_trading_system(paper_trading=not args.live, background=args.background)
        if not args.background:
            print("✅ Système de trading terminé")
        return
    
    # Mode complet: unifier puis trading
    print("=== MODE COMPLET ===")
    
    # 1. Lancer le unifier
    if launch_unifier(args.date, background=args.background):
        print("\n" + "="*50)
        time.sleep(2)
        
        # 2. Lancer le système de trading
        if launch_trading_system(paper_trading=not args.live, background=args.background):
            if args.background:
                print("✅ Système complet lancé en arrière-plan")
                monitor_system()
            else:
                print("✅ Système complet terminé")
        else:
            print("❌ Erreur lancement système de trading")
    else:
        print("❌ Impossible de continuer sans unifier")

if __name__ == "__main__":
    main()
