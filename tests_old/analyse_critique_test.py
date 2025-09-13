#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Analyse Critique Test
Analyse détaillée des volumes, trades et données OHLC
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyse_critique():
    """Analyse critique des résultats du test"""
    
    print("MIA_IA_SYSTEM - ANALYSE CRITIQUE TEST")
    print("=" * 60)
    print("🔍 Vérification volumes, trades et données OHLC")
    print("🎯 Objectif: Validation avant lancement 2h")
    print("=" * 60)
    
    # 1. ANALYSE DES LOGS
    print("\n📊 1. ANALYSE DES LOGS")
    print("=" * 40)
    
    log_files = []
    for pattern in ["logs/*.log", "*.log", "data/logs/*.log"]:
        log_files.extend(glob.glob(pattern))
    
    if not log_files:
        print("❌ Aucun fichier log trouvé")
        return
    
    print(f"✅ {len(log_files)} fichiers logs trouvés")
    
    # Analyser chaque log
    trades_count = 0
    signals_count = 0
    volume_issues = 0
    ohlc_issues = 0
    
    for log_file in log_files:
        try:
            print(f"\n📄 Analyse: {log_file}")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Analyser les dernières lignes (dernières 50)
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            for line in recent_lines:
                line = line.strip()
                
                # Compter les trades
                if "TRADE" in line or "EXECUTION" in line:
                    trades_count += 1
                    print(f"   🎯 Trade détecté: {line}")
                
                # Compter les signaux
                if "SIGNAL" in line or "BUY" in line or "SELL" in line:
                    signals_count += 1
                    print(f"   📊 Signal détecté: {line}")
                
                # Vérifier volumes constants
                if "volume: 192.0" in line or "Volume: 192" in line:
                    volume_issues += 1
                    print(f"   ⚠️ Volume constant détecté: {line}")
                
                # Vérifier OHLC incohérent
                if "OHLC incohérent" in line or "O=nan" in line:
                    ohlc_issues += 1
                    print(f"   ❌ OHLC incohérent: {line}")
                    
        except Exception as e:
            print(f"   ❌ Erreur lecture {log_file}: {e}")
    
    # 2. ANALYSE DES DONNÉES RÉCENTES
    print("\n📊 2. ANALYSE DONNÉES RÉCENTES")
    print("=" * 40)
    
    try:
        # Vérifier les fichiers de données récents
        data_files = glob.glob("data/*.json") + glob.glob("data/live/*.json")
        
        if data_files:
            print(f"✅ {len(data_files)} fichiers de données trouvés")
            
            for data_file in data_files[-3:]:  # 3 derniers fichiers
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                    
                    print(f"\n📄 Données: {data_file}")
                    
                    # Analyser la structure des données
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if "volume" in key.lower():
                                print(f"   📊 {key}: {value}")
                            elif "price" in key.lower() or "ohlc" in key.lower():
                                print(f"   💰 {key}: {value}")
                                
                except Exception as e:
                    print(f"   ❌ Erreur lecture données: {e}")
        else:
            print("⚠️ Aucun fichier de données récent trouvé")
            
    except Exception as e:
        print(f"❌ Erreur analyse données: {e}")
    
    # 3. VÉRIFICATION CONNEXION IBKR
    print("\n📊 3. VÉRIFICATION CONNEXION IBKR")
    print("=" * 40)
    
    try:
        # Vérifier si IBKR est connecté
        import socket
        
        # Test connexion TWS
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 7497))
            sock.close()
            
            if result == 0:
                print("✅ TWS connecté (port 7497)")
            else:
                print("❌ TWS non connecté (port 7497)")
        except:
            print("❌ Erreur test connexion TWS")
            
        # Test connexion Gateway
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 4002))
            sock.close()
            
            if result == 0:
                print("✅ Gateway connecté (port 4002)")
            else:
                print("❌ Gateway non connecté (port 4002)")
        except:
            print("❌ Erreur test connexion Gateway")
            
    except Exception as e:
        print(f"❌ Erreur vérification IBKR: {e}")
    
    # 4. RÉSUMÉ CRITIQUE
    print("\n📊 4. RÉSUMÉ CRITIQUE")
    print("=" * 40)
    
    print(f"🎯 Trades détectés: {trades_count}")
    print(f"📊 Signaux détectés: {signals_count}")
    print(f"⚠️ Problèmes volume: {volume_issues}")
    print(f"❌ Problèmes OHLC: {ohlc_issues}")
    
    # Évaluation
    print("\n💡 ÉVALUATION FINALE")
    print("=" * 40)
    
    if trades_count > 0:
        print("✅ Trades détectés - Système actif")
    else:
        print("❌ Aucun trade détecté - Problème possible")
    
    if signals_count > 0:
        print("✅ Signaux générés - Système fonctionnel")
    else:
        print("❌ Aucun signal détecté - Problème possible")
    
    if volume_issues == 0:
        print("✅ Volumes variables - Données réelles")
    else:
        print(f"⚠️ {volume_issues} problèmes de volume détectés")
    
    if ohlc_issues == 0:
        print("✅ OHLC cohérent - Données valides")
    else:
        print(f"❌ {ohlc_issues} problèmes OHLC détectés")
    
    # Recommandation finale
    print("\n🚀 RECOMMANDATION FINALE")
    print("=" * 40)
    
    if trades_count > 0 and signals_count > 0 and volume_issues == 0 and ohlc_issues == 0:
        print("✅ SYSTÈME VALIDÉ - Prêt pour lancement 2h")
        print("🎯 Tous les critères sont satisfaits")
    elif trades_count > 0 and signals_count > 0:
        print("⚠️ SYSTÈME PARTIELLEMENT VALIDÉ")
        print("🎯 Système fonctionnel mais quelques problèmes détectés")
        print("💡 Recommandation: Corriger avant lancement 2h")
    else:
        print("❌ SYSTÈME NON VALIDÉ")
        print("🎯 Problèmes critiques détectés")
        print("💡 Recommandation: Diagnostic approfondi nécessaire")

if __name__ == "__main__":
    analyse_critique()






