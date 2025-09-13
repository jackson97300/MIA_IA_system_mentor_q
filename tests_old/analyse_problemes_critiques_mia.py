#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Analyse Problèmes Critiques
Diagnostic et correction des problèmes OHLC, connexion et volume
"""

import os
import sys
import glob
import time
import json
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyser_problemes_critiques():
    """Analyser les problèmes critiques du système"""
    
    print("MIA_IA_SYSTEM - ANALYSE PROBLÈMES CRITIQUES")
    print("=" * 60)
    print("🔍 Diagnostic des problèmes OHLC, connexion et volume")
    print("⏰ Durée: 1 minute")
    print("🎯 Objectif: Correction des données erronées")
    print("=" * 60)
    
    start_time = datetime.now()
    analysis_duration = timedelta(minutes=1)
    
    # Variables de suivi
    ohlc_issues = []
    connection_issues = []
    volume_issues = []
    price_errors = []
    
    print(f"⏰ Début analyse: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + analysis_duration).strftime('%H:%M:%S')}")
    
    print("\n📊 ANALYSE EN COURS:")
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
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    # Analyser les dernières lignes
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    
                    for line in recent_lines:
                        line = line.strip()
                        
                        # Détecter problèmes OHLC
                        if any(pattern in line.lower() for pattern in ['ohlc', 'o=nan', 'h=nan', 'l=nan', 'c=nan', 'price error']):
                            ohlc_issues.append({
                                'time': datetime.now().strftime('%H:%M:%S'),
                                'line': line[:100] + '...' if len(line) > 100 else line,
                                'file': os.path.basename(log_file)
                            })
                            print(f"   ❌ OHLC incohérent: {line[:80]}...")
                        
                        # Détecter problèmes connexion
                        if any(pattern in line.lower() for pattern in ['timeout', 'connection', 'disconnect', 'reconnect']):
                            connection_issues.append({
                                'time': datetime.now().strftime('%H:%M:%S'),
                                'line': line[:100] + '...' if len(line) > 100 else line,
                                'file': os.path.basename(log_file)
                            })
                            print(f"   🔌 Problème connexion: {line[:80]}...")
                        
                        # Détecter problèmes volume
                        if any(pattern in line.lower() for pattern in ['volume: 192.0', 'volume constant', 'volume unchanged']):
                            volume_issues.append({
                                'time': datetime.now().strftime('%H:%M:%S'),
                                'line': line[:100] + '...' if len(line) > 100 else line,
                                'file': os.path.basename(log_file)
                            })
                            print(f"   ⚠️ Volume constant: {line[:80]}...")
                        
                        # Détecter erreurs de prix spécifiques
                        if '6518' in line or 'price' in line.lower():
                            price_errors.append({
                                'time': datetime.now().strftime('%H:%M:%S'),
                                'line': line[:100] + '...' if len(line) > 100 else line,
                                'file': os.path.basename(log_file)
                            })
                            print(f"   🚨 Erreur prix détectée: {line[:80]}...")
                            
                except Exception as e:
                    continue
            
            # 2. STATISTIQUES ACTUELLES
            print(f"\n📊 STATISTIQUES PROBLÈMES:")
            print(f"   ❌ Problèmes OHLC: {len(ohlc_issues)}")
            print(f"   🔌 Problèmes connexion: {len(connection_issues)}")
            print(f"   ⚠️ Problèmes volume: {len(volume_issues)}")
            print(f"   🚨 Erreurs prix: {len(price_errors)}")
            
            # 3. ANALYSE DES CAUSES
            print(f"\n🔍 ANALYSE DES CAUSES:")
            
            # Analyser les problèmes OHLC
            if len(ohlc_issues) > 0:
                print("   ❌ OHLC - Causes possibles:")
                print("      • Données TWS corrompues")
                print("      • Problème de parsing")
                print("      • Cache de données obsolète")
                print("      • Connexion instable")
            
            # Analyser les problèmes connexion
            if len(connection_issues) > 0:
                print("   🔌 Connexion - Causes possibles:")
                print("      • TWS surchargé")
                print("      • Problème réseau")
                print("      • Client ID en conflit")
                print("      • Port bloqué")
            
            # Analyser les problèmes volume
            if len(volume_issues) > 0:
                print("   ⚠️ Volume - Causes possibles:")
                print("      • Données simulées")
                print("      • Cache de données")
                print("      • Source de données incorrecte")
            
            # Analyser les erreurs de prix
            if len(price_errors) > 0:
                print("   🚨 Prix - Causes possibles:")
                print("      • Prix ES incorrect (6518 vs 6489)")
                print("      • Données obsolètes")
                print("      • Problème de synchronisation")
            
            # Attendre avant prochaine analyse
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Analyse arrêtée par l'utilisateur")
    
    # RÉSUMÉ FINAL
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RAPPORT FINAL")
    print("=" * 40)
    print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
    print(f"❌ Problèmes OHLC: {len(ohlc_issues)}")
    print(f"🔌 Problèmes connexion: {len(connection_issues)}")
    print(f"⚠️ Problèmes volume: {len(volume_issues)}")
    print(f"🚨 Erreurs prix: {len(price_errors)}")
    
    # RECOMMANDATIONS DE CORRECTION
    print("\n🚀 RECOMMANDATIONS DE CORRECTION")
    print("=" * 40)
    
    if len(price_errors) > 0:
        print("🚨 PRIORITÉ MAXIMALE - Erreur prix ES:")
        print("   • Exécuter: python corriger_prix_tws.py")
        print("   • Redémarrer TWS")
        print("   • Vérifier souscription ES")
    
    if len(ohlc_issues) > 50:
        print("❌ PRIORITÉ HAUTE - Problèmes OHLC:")
        print("   • Exécuter: python forcer_donnees_reelles_ibkr.py")
        print("   • Nettoyer cache de données")
        print("   • Vérifier connexion TWS")
    
    if len(connection_issues) > 20:
        print("🔌 PRIORITÉ MOYENNE - Problèmes connexion:")
        print("   • Redémarrer TWS")
        print("   • Vérifier port 7497")
        print("   • Changer Client ID si nécessaire")
    
    if len(volume_issues) > 0:
        print("⚠️ PRIORITÉ BASSE - Problèmes volume:")
        print("   • Vérifier source de données")
        print("   • Nettoyer cache")
    
    # PLAN D'ACTION
    print("\n📋 PLAN D'ACTION RECOMMANDÉ")
    print("=" * 40)
    print("1. 🚨 Corriger prix ES (CRITIQUE)")
    print("2. ❌ Corriger données OHLC")
    print("3. 🔌 Optimiser connexion TWS")
    print("4. ⚠️ Vérifier volumes")
    print("5. ✅ Relancer analyse")

if __name__ == "__main__":
    analyser_problemes_critiques()


