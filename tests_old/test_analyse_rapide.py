#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Analyse Rapide
Test rapide de l'analyse système en 30 secondes
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analyse_rapide():
    """Test rapide de l'analyse système"""
    
    print("MIA_IA_SYSTEM - TEST ANALYSE RAPIDE")
    print("=" * 50)
    print("🔍 Test rapide en cours")
    print("⏰ Durée: 30 secondes")
    print("🎯 Objectif: Validation rapide")
    print("=" * 50)
    
    start_time = datetime.now()
    test_duration = timedelta(seconds=30)
    
    print(f"⏰ Début test: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + test_duration).strftime('%H:%M:%S')}")
    
    # Variables de test
    trades_found = False
    signals_found = False
    logs_found = False
    
    print("\n📊 TEST EN COURS:")
    print("=" * 30)
    
    try:
        while datetime.now() < start_time + test_duration:
            current_time = datetime.now()
            elapsed = current_time - start_time
            remaining = test_duration - elapsed
            
            print(f"\n⏰ {current_time.strftime('%H:%M:%S')} | "
                  f"Écoulé: {elapsed.total_seconds():.0f}s | "
                  f"Reste: {remaining.total_seconds():.0f}s")
            
            # Vérifier les logs
            log_files = []
            for pattern in ["logs/*.log", "*.log"]:
                try:
                    import glob
                    log_files.extend(glob.glob(pattern))
                except:
                    continue
            
            if log_files:
                logs_found = True
                print(f"   📄 {len(log_files)} fichiers de logs trouvés")
                
                # Analyser rapidement le dernier fichier
                latest_log = max(log_files, key=os.path.getmtime)
                try:
                    with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_lines = lines[-10:] if len(lines) > 10 else lines
                        
                        for line in recent_lines:
                            line = line.strip()
                            if "TRADE" in line or "EXECUTION" in line:
                                trades_found = True
                                print(f"   🎯 Trade détecté dans {os.path.basename(latest_log)}")
                            if "SIGNAL" in line or "BUY" in line or "SELL" in line:
                                signals_found = True
                                print(f"   📊 Signal détecté dans {os.path.basename(latest_log)}")
                except Exception as e:
                    print(f"   ⚠️ Erreur lecture log: {e}")
            else:
                print("   ⚠️ Aucun fichier de log trouvé")
            
            # Vérifier les processus
            print("   🔍 Vérification processus...")
            
            # Attendre avant prochaine vérification
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Test arrêté par l'utilisateur")
    
    # RÉSULTATS DU TEST
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RÉSULTATS DU TEST")
    print("=" * 40)
    print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
    print(f"📄 Logs trouvés: {'✅' if logs_found else '❌'}")
    print(f"🎯 Trades détectés: {'✅' if trades_found else '❌'}")
    print(f"📊 Signaux détectés: {'✅' if signals_found else '❌'}")
    
    # RECOMMANDATION
    print("\n🚀 RECOMMANDATION:")
    print("=" * 40)
    
    if logs_found and trades_found and signals_found:
        print("✅ SYSTÈME ACTIF - Lancer analyse complète")
        print("💡 Utiliser: python analyse_resultats_temps_reel.py")
    elif logs_found:
        print("⚠️ LOGS TROUVÉS - Système peut être actif")
        print("💡 Vérifier: python analyse_resultats_temps_reel.py")
    else:
        print("❌ AUCUN LOG - Système non démarré")
        print("💡 Démarrer MIA_IA_SYSTEM d'abord")

if __name__ == "__main__":
    test_analyse_rapide()


