#!/usr/bin/env python3
"""
État Instantané des Tests Robustes
MIA_IA_SYSTEM - Vérification des tests robustes actuels
"""

import os
import time
from datetime import datetime

def etat_tests_robustes_instant():
    """Vérifie l'état des tests robustes actuels"""
    print("📊 === ÉTAT INSTANTANÉ TESTS ROBUSTES ===")
    print(f"⏰ Heure actuelle: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    log_files = {
        'CONSERVATEUR_ROBUSTE': 'logs/test_robuste_conservateur.log',
        'MODÉRÉ_ROBUSTE': 'logs/test_robuste_modéré.log',
        'AGRESSIF_ROBUSTE': 'logs/test_robuste_agressif.log'
    }
    
    for config, log_path in log_files.items():
        if os.path.exists(log_path):
            size_kb = os.path.getsize(log_path) / 1024
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    if ' - ' in last_line:
                        timestamp_str = last_line.split(' - ')[0]
                        try:
                            last_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            time_diff = datetime.now() - last_time
                            minutes_ago = int(time_diff.total_seconds() / 60)
                            
                            if minutes_ago < 2:
                                status = "🟢 ACTIF"
                            elif minutes_ago < 5:
                                status = "🟡 RALENTI"
                            else:
                                status = "🔴 ARRÊTÉ"
                                
                            print(f"{config:<20} {status} | {size_kb:.1f} KB | Dernière activité: {minutes_ago} min")
                            
                            # Afficher la dernière ligne pour debug
                            if minutes_ago < 5:
                                print(f"   📄 Dernière ligne: {last_line.strip()}")
                                
                        except Exception as e:
                            print(f"{config:<20} ⚪ ERREUR TIMESTAMP | {size_kb:.1f} KB | Erreur: {e}")
                    else:
                        print(f"{config:<20} ⚪ FORMAT INCONNU | {size_kb:.1f} KB")
                else:
                    print(f"{config:<20} ❌ VIDE | 0 KB")
        else:
            print(f"{config:<20} ❌ MANQUANT | 0 KB")
    
    print()
    print("💡 Pour vérifier à nouveau: python etat_tests_robustes_instant.py")
    print("📈 Pour analyser les résultats: python analyze_test_results.py")

if __name__ == "__main__":
    etat_tests_robustes_instant()
