#!/usr/bin/env python3
"""
Lancement parallèle des tests
MIA_IA_SYSTEM - Tests simultanés avec monitoring
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import threading
import signal

def create_logs_directory():
    """Crée le dossier logs s'il n'existe pas"""
    Path("logs").mkdir(exist_ok=True)
    print("✅ Dossier logs créé/vérifié")

def monitor_process(config, process, results):
    """Monitore un processus et capture sa sortie"""
    stdout, stderr = process.communicate()
    results[config] = {
        'returncode': process.returncode,
        'stdout': stdout.decode('utf-8', errors='ignore'),
        'stderr': stderr.decode('utf-8', errors='ignore')
    }

def launch_parallel_tests():
    """Lance les 3 tests en parallèle avec monitoring"""
    
    print("🚀 === LANCEMENT TESTS PARALLÈLES MIA_IA_SYSTEM ===")
    print("📊 3 configurations testées simultanément")
    print("⏱️ Durée recommandée: 2-3 heures")
    print("🎯 Objectif: Comparer les performances des paramètres")
    print()
    
    # Créer dossier logs
    create_logs_directory()
    
    # Configuration des tests
    test_configs = {
        "CONSERVATEUR": "test_conservateur.py",
        "MODÉRÉ": "test_modéré.py", 
        "AGRESSIF": "test_agressif.py"
    }
    
    # Lancer les processus
    processes = {}
    results = {}
    monitor_threads = []
    
    print("🔄 Lancement des tests...")
    for config, script in test_configs.items():
        if not os.path.exists(script):
            print(f"❌ Erreur: {script} n'existe pas")
            continue
            
        cmd = [sys.executable, script]
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        processes[config] = process
        
        # Créer thread de monitoring
        thread = threading.Thread(
            target=monitor_process, 
            args=(config, process, results)
        )
        thread.start()
        monitor_threads.append(thread)
        
        print(f"✅ Test {config} lancé (PID: {process.pid})")
    
    print()
    print("📊 === MONITORING EN TEMPS RÉEL ===")
    print("Les tests s'exécutent en parallèle...")
    print("Logs disponibles dans le dossier 'logs/'")
    print("Appuyez sur Ctrl+C pour arrêter tous les tests")
    print()
    
    try:
        # Monitoring en temps réel
        start_time = time.time()
        while any(p.poll() is None for p in processes.values()):
            elapsed = time.time() - start_time
            print(f"\r⏱️ Temps écoulé: {elapsed:.0f}s | Tests actifs: {sum(1 for p in processes.values() if p.poll() is None)}/3", end="")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Arrêt des tests...")
        for config, process in processes.items():
            if process.poll() is None:
                process.terminate()
                print(f"⏹️ Test {config} arrêté")
    
    # Attendre que tous les threads de monitoring se terminent
    for thread in monitor_threads:
        thread.join()
    
    print("\n📊 === RÉSULTATS DES TESTS ===")
    for config, result in results.items():
        status = "✅ SUCCÈS" if result['returncode'] == 0 else "❌ ÉCHEC"
        print(f"{config}: {status} (Code: {result['returncode']})")
    
    print("\n📈 === ANALYSE DES RÉSULTATS ===")
    print("Consultez les logs dans le dossier 'logs/' pour comparer les performances:")
    print("  📄 logs/test_conservateur.log")
    print("  📄 logs/test_modéré.log") 
    print("  📄 logs/test_agressif.log")
    print()
    print("🎯 Prochaines étapes:")
    print("  1. Analyser les logs pour identifier la meilleure configuration")
    print("  2. Comparer les métriques de performance")
    print("  3. Ajuster les paramètres selon les résultats")

if __name__ == "__main__":
    launch_parallel_tests()
