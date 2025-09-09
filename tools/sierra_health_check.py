#!/usr/bin/env python3
"""
🏥 SIERRA CHART HEALTH CHECK
============================

Script pour vérifier la santé des connexions DTC Sierra Chart.
Teste les ports ES (11099) et NQ (11100) sans envoyer d'ordres.
"""

import socket
import sys
import time
from datetime import datetime
from typing import Dict, Tuple
from config.sierra_trading_ports import get_sierra_trading_config

def test_port_connection(host: str, port: int, timeout: float = 3.0) -> Tuple[bool, str]:
    """
    Teste la connexion à un port
    
    Returns:
        (success: bool, message: str)
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            return True, f"✅ Connexion réussie: {host}:{port}"
    except socket.timeout:
        return False, f"⏰ Timeout: {host}:{port} (pas de réponse en {timeout}s)"
    except ConnectionRefused:
        return False, f"❌ Connexion refusée: {host}:{port} (Sierra Chart pas démarré?)"
    except Exception as e:
        return False, f"❌ Erreur: {host}:{port} - {e}"

def test_dtc_handshake(host: str, port: int, timeout: float = 5.0) -> Tuple[bool, str]:
    """
    Teste un handshake DTC basique (sans authentification)
    
    Returns:
        (success: bool, message: str)
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            # Envoyer LOGON_REQUEST basique
            logon_request = b"LOGON_REQUEST\x00"
            sock.sendall(logon_request)
            
            # Attendre une réponse (même si on ne la parse pas)
            sock.settimeout(2.0)
            response = sock.recv(1024)
            
            if response:
                return True, f"✅ Handshake DTC réussi: {host}:{port} (réponse: {len(response)} bytes)"
            else:
                return False, f"⚠️ Pas de réponse DTC: {host}:{port}"
                
    except socket.timeout:
        return False, f"⏰ Timeout handshake: {host}:{port}"
    except Exception as e:
        return False, f"❌ Erreur handshake: {host}:{port} - {e}"

def run_health_check() -> Dict[str, Dict[str, any]]:
    """
    Lance le health check complet
    
    Returns:
        Dict avec les résultats pour chaque port
    """
    config = get_sierra_trading_config()
    results = {}
    
    print("🏥 SIERRA CHART HEALTH CHECK")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Host: {config.host}")
    print()
    
    # Test ES
    print("📊 TEST ES (E-mini S&P 500)")
    print("-" * 30)
    
    es_port = config.es_dtc_port
    es_historical = config.es_historical_port
    
    # Test port DTC ES
    success, message = test_port_connection(config.host, es_port)
    print(f"Port DTC {es_port}: {message}")
    results[f"ES_DTC_{es_port}"] = {"success": success, "message": message}
    
    # Test port Historical ES
    success, message = test_port_connection(config.host, es_historical)
    print(f"Port Historical {es_historical}: {message}")
    results[f"ES_HIST_{es_historical}"] = {"success": success, "message": message}
    
    # Test handshake DTC ES
    success, message = test_dtc_handshake(config.host, es_port)
    print(f"Handshake DTC: {message}")
    results[f"ES_HANDSHAKE"] = {"success": success, "message": message}
    
    print()
    
    # Test NQ
    print("📈 TEST NQ (E-mini NASDAQ)")
    print("-" * 30)
    
    nq_port = config.nq_dtc_port
    nq_historical = config.nq_historical_port
    
    # Test port DTC NQ
    success, message = test_port_connection(config.host, nq_port)
    print(f"Port DTC {nq_port}: {message}")
    results[f"NQ_DTC_{nq_port}"] = {"success": success, "message": message}
    
    # Test port Historical NQ
    success, message = test_port_connection(config.host, nq_historical)
    print(f"Port Historical {nq_historical}: {message}")
    results[f"NQ_HIST_{nq_historical}"] = {"success": success, "message": message}
    
    # Test handshake DTC NQ
    success, message = test_dtc_handshake(config.host, nq_port)
    print(f"Handshake DTC: {message}")
    results[f"NQ_HANDSHAKE"] = {"success": success, "message": message}
    
    print()
    
    # Résumé
    print("📋 RÉSUMÉ")
    print("-" * 30)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r["success"])
    
    print(f"Tests réussis: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 TOUS LES TESTS RÉUSSIS - Sierra Chart prêt!")
        return_code = 0
    elif successful_tests >= total_tests // 2:
        print("⚠️ TESTS PARTIELS - Vérifier la configuration Sierra Chart")
        return_code = 1
    else:
        print("❌ TESTS ÉCHOUÉS - Sierra Chart pas configuré ou pas démarré")
        return_code = 2
    
    print()
    print("💡 CONSEILS:")
    if return_code > 0:
        print("1. Vérifier que Sierra Chart est démarré")
        print("2. Vérifier que DTC Protocol Server est activé")
        print("3. Vérifier les ports dans Sierra Chart:")
        print(f"   - ES DTC: {es_port}, Historical: {es_historical}")
        print(f"   - NQ DTC: {nq_port}, Historical: {nq_historical}")
        print("4. Vérifier que 'Allow Trading' est activé")
        print("5. Vérifier le firewall Windows")
    else:
        print("✅ Configuration parfaite! Prêt pour le trading DTC.")
    
    return results

def continuous_monitor(interval: int = 30):
    """
    Monitoring continu des ports
    
    Args:
        interval: Intervalle en secondes entre les checks
    """
    print(f"🔄 Monitoring continu (intervalle: {interval}s)")
    print("Appuyez sur Ctrl+C pour arrêter")
    print()
    
    try:
        while True:
            run_health_check()
            print(f"⏳ Attente {interval}s...")
            time.sleep(interval)
            print()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring arrêté par l'utilisateur")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Health check Sierra Chart DTC")
    parser.add_argument("--monitor", "-m", type=int, metavar="SECONDS",
                       help="Monitoring continu avec intervalle en secondes")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Test rapide (pas de handshake DTC)")
    
    args = parser.parse_args()
    
    if args.monitor:
        continuous_monitor(args.monitor)
    else:
        results = run_health_check()
        
        # Code de sortie pour scripts automatisés
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r["success"])
        
        if successful_tests == total_tests:
            sys.exit(0)  # Tout OK
        elif successful_tests >= total_tests // 2:
            sys.exit(1)  # Partiel
        else:
            sys.exit(2)  # Échec
