#!/usr/bin/env python3
"""
Arrêt des tests parallèles
MIA_IA_SYSTEM - Arrêt propre des processus
"""

import os
import psutil
import signal
import time

def stop_parallel_tests():
    """Arrête tous les processus de test parallèles"""
    
    print("⏹️ === ARRÊT DES TESTS PARALLÈLES ===")
    
    # Chercher les processus Python qui exécutent nos tests
    test_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('test_' in arg for arg in cmdline):
                if any(config in ' '.join(cmdline) for config in ['conservateur', 'modéré', 'agressif']):
                    test_processes.append(proc)
                    print(f"🔍 Processus trouvé: PID {proc.info['pid']} - {' '.join(cmdline)}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not test_processes:
        print("✅ Aucun processus de test trouvé")
        return
    
    print(f"\n🛑 Arrêt de {len(test_processes)} processus...")
    
    # Arrêter chaque processus
    for proc in test_processes:
        try:
            print(f"⏹️ Arrêt PID {proc.info['pid']}...")
            proc.terminate()
        except psutil.NoSuchProcess:
            print(f"⚠️ Processus {proc.info['pid']} déjà terminé")
    
    # Attendre que les processus se terminent
    print("\n⏳ Attente de la terminaison...")
    time.sleep(3)
    
    # Vérifier si des processus sont encore actifs
    still_running = []
    for proc in test_processes:
        try:
            if proc.is_running():
                still_running.append(proc)
        except psutil.NoSuchProcess:
            continue
    
    # Forcer l'arrêt si nécessaire
    if still_running:
        print(f"⚠️ {len(still_running)} processus encore actifs, arrêt forcé...")
        for proc in still_running:
            try:
                proc.kill()
                print(f"💀 Processus {proc.info['pid']} arrêté de force")
            except psutil.NoSuchProcess:
                continue
    
    print("\n✅ Tous les tests parallèles ont été arrêtés")
    print("📊 Consultez les logs pour analyser les résultats")

if __name__ == "__main__":
    stop_parallel_tests()
