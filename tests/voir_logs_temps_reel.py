#!/usr/bin/env python3
"""
Voir les logs en temps réel
MIA_IA_SYSTEM - Affichage simple des logs
"""

import os
import time
from pathlib import Path

def voir_logs_temps_reel():
    """Affiche les logs en temps réel"""
    
    print("📊 === LOGS EN TEMPS RÉEL ===")
    print("Appuyez sur Ctrl+C pour arrêter")
    print()
    
    log_files = {
        'CONSERVATEUR': 'logs/test_conservateur.log',
        'MODÉRÉ': 'logs/test_modéré.log',
        'AGRESSIF': 'logs/test_agressif.log'
    }
    
    # Stocker les tailles précédentes
    previous_sizes = {}
    for config, log_path in log_files.items():
        if os.path.exists(log_path):
            previous_sizes[config] = os.path.getsize(log_path)
        else:
            previous_sizes[config] = 0
    
    try:
        while True:
            print(f"\n⏰ {time.strftime('%H:%M:%S')} - État des logs:")
            print("-" * 50)
            
            for config, log_path in log_files.items():
                if os.path.exists(log_path):
                    current_size = os.path.getsize(log_path)
                    size_kb = current_size / 1024
                    
                    # Vérifier si le fichier a grandi
                    if current_size > previous_sizes[config]:
                        status = "🟢 ACTIF"
                        previous_sizes[config] = current_size
                    else:
                        status = "⚪ EN ATTENTE"
                    
                    print(f"{config:<12} {status} | {size_kb:.1f} KB")
                else:
                    print(f"{config:<12} ❌ FICHIER MANQUANT")
            
            print("\n🔄 Mise à jour dans 10 secondes...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Arrêt de la surveillance")

if __name__ == "__main__":
    voir_logs_temps_reel()
