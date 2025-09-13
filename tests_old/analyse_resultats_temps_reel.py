#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Analyse Résultats Temps Réel
Analyse les résultats du système en cours
"""

import os
import sys
import json
import glob
import time
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyse_resultats_temps_reel():
    """Analyse les résultats en temps réel"""
    
    print("MIA_IA_SYSTEM - ANALYSE RÉSULTATS TEMPS RÉEL")
    print("=" * 60)
    print("🔍 Analyse système en cours")
    print("⏰ Durée: 2 minutes")
    print("🎯 Objectif: Validation avant 2h")
    print("=" * 60)
    
    start_time = datetime.now()
    analysis_duration = timedelta(minutes=2)
    
    print(f"⏰ Début analyse: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + analysis_duration).strftime('%H:%M:%S')}")
    
    # Variables de suivi
    trades_count = 0
    signals_count = 0
    volume_issues = 0
    ohlc_issues = 0
    connection_issues = 0
    last_log_time = None
    
    print("\n📊 MONITORING EN TEMPS RÉEL:")
    print("=" * 40)
    
    try:
        while datetime.now() < start_time + analysis_duration:
            current_time = datetime.now()
            elapsed = current_time - start_time
            remaining = analysis_duration - elapsed
            
            print(f"\n⏰ {current_time.strftime('%H:%M:%S')} | "
                  f"Écoulé: {elapsed.total_seconds():.0f}s | "
                  f"Reste: {remaining.total_seconds():.0f}s")
            
            # 1. ANALYSE LOGS RÉCENTS
            print("📄 Analyse logs récents...")
            
            log_files = []
            for pattern in ["logs/*.log", "*.log"]:
                log_files.extend(glob.glob(pattern))
            
            for log_file in log_files:
                try:
                    # Vérifier si le fichier a été modifié
                    file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                    
                    if last_log_time is None or file_time > last_log_time:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            
                        # Analyser les dernières lignes
                        recent_lines = lines[-20:] if len(lines) > 20 else lines
                        
                        for line in recent_lines:
                            line = line.strip()
                            
                            # Compter les trades
                            if "TRADE" in line or "EXECUTION" in line:
                                trades_count += 1
                                print(f"   🎯 Trade détecté: {line[:100]}...")
                            
                            # Compter les signaux
                            if "SIGNAL" in line or "BUY" in line or "SELL" in line:
                                signals_count += 1
                                print(f"   📊 Signal détecté: {line[:100]}...")
                            
                            # Vérifier volumes constants
                            if "volume: 192.0" in line or "Volume: 192" in line:
                                volume_issues += 1
                                print(f"   ⚠️ Volume constant: {line[:100]}...")
                            
                            # Vérifier OHLC incohérent
                            if "OHLC incohérent" in line or "O=nan" in line:
                                ohlc_issues += 1
                                print(f"   ❌ OHLC incohérent: {line[:100]}...")
                            
                            # Vérifier problèmes connexion
                            if "timeout" in line.lower() or "connection" in line.lower():
                                connection_issues += 1
                                print(f"   🔌 Problème connexion: {line[:100]}...")
                                
                except Exception as e:
                    continue
            
            last_log_time = current_time
            
            # 2. STATISTIQUES ACTUELLES
            print(f"\n📊 STATISTIQUES ACTUELLES:")
            print(f"   🎯 Trades: {trades_count}")
            print(f"   📊 Signaux: {signals_count}")
            print(f"   ⚠️ Problèmes volume: {volume_issues}")
            print(f"   ❌ Problèmes OHLC: {ohlc_issues}")
            print(f"   🔌 Problèmes connexion: {connection_issues}")
            
            # 3. ÉVALUATION QUALITÉ
            print(f"\n💡 ÉVALUATION QUALITÉ:")
            
            if trades_count > 0:
                print("   ✅ Système actif - Trades détectés")
            else:
                print("   ⚠️ Aucun trade détecté")
            
            if signals_count > 0:
                print("   ✅ Signaux générés")
            else:
                print("   ⚠️ Aucun signal détecté")
            
            if volume_issues == 0:
                print("   ✅ Volumes variables")
            else:
                print(f"   ⚠️ {volume_issues} problèmes volume")
            
            if ohlc_issues == 0:
                print("   ✅ OHLC cohérent")
            else:
                print(f"   ❌ {ohlc_issues} problèmes OHLC")
            
            if connection_issues == 0:
                print("   ✅ Connexion stable")
            else:
                print(f"   🔌 {connection_issues} problèmes connexion")
            
            # Attendre avant prochaine analyse
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Analyse arrêtée par l'utilisateur")
    
    # RÉSUMÉ FINAL
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RÉSUMÉ FINAL")
    print("=" * 40)
    print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
    print(f"🎯 Trades détectés: {trades_count}")
    print(f"📊 Signaux détectés: {signals_count}")
    print(f"⚠️ Problèmes volume: {volume_issues}")
    print(f"❌ Problèmes OHLC: {ohlc_issues}")
    print(f"🔌 Problèmes connexion: {connection_issues}")
    
    # RECOMMANDATION FINALE
    print("\n🚀 RECOMMANDATION FINALE")
    print("=" * 40)
    
    if trades_count > 0 and signals_count > 0 and volume_issues == 0 and ohlc_issues == 0 and connection_issues == 0:
        print("✅ SYSTÈME PARFAIT - Prêt pour 2h")
        print("🎯 Tous les critères sont satisfaits")
        print("💡 Vous pouvez lancer le test 2h")
    elif trades_count > 0 and signals_count > 0:
        print("⚠️ SYSTÈME FONCTIONNEL avec quelques problèmes")
        print("🎯 Système actif mais corrections nécessaires")
        print("💡 Corriger avant lancement 2h")
    else:
        print("❌ SYSTÈME NON FONCTIONNEL")
        print("🎯 Problèmes critiques détectés")
        print("💡 Diagnostic approfondi nécessaire")

if __name__ == "__main__":
    analyse_resultats_temps_reel()






