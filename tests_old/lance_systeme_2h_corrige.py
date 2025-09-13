#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Système 2h avec Corrections Critiques
Lance le système pour test 2h avec toutes les corrections appliquées
"""

import os
import sys
import json
import asyncio
import signal
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Variable globale pour arrêter le système
stop_system = False

def signal_handler(signum, frame):
    """Gestionnaire pour arrêter le système proprement"""
    global stop_system
    print("\n🛑 Signal d'arrêt reçu - Arrêt propre du système...")
    stop_system = True

async def lance_systeme_2h_corrige():
    """Lance le système pour test 2h avec corrections critiques"""

    global stop_system

    print("MIA_IA_SYSTEM - LANCEMENT SYSTÈME 2H AVEC CORRECTIONS")
    print("=" * 60)
    print("🎯 MODE: Test 2 heures avec corrections critiques")
    print("⏰ Durée: 2 heures maximum")
    print("📊 Objectif: Validation performance optimisée")
    print("🔧 Corrections: OHLC, connexion IBKR, volume")
    print("=" * 60)

    try:
        # Vérifier que les corrections ont été appliquées
        print("🔧 VÉRIFICATION CORRECTIONS APPLIQUÉES")
        print("=" * 40)

        config_file = "config/critical_fixes_session.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("✅ Configuration corrections trouvée")
            print(f"   📅 Timestamp: {config.get('timestamp', 'N/A')}")
            print(f"   🔧 Corrections: {config.get('critical_fixes', {})}")
        else:
            print("⚠️ Configuration corrections non trouvée")
            print("💡 Exécutez d'abord: python corriger_problemes_critiques_complet.py")

        # Appliquer les optimisations finales
        import config.automation_config as auto_config

        print("\n🔧 OPTIMISATIONS FINALES")
        print("=" * 40)

        # Configuration pour test 2h optimisé
        auto_config.TEST_MODE = False  # Mode production
        auto_config.TEST_DURATION_MINUTES = 120  # 2 heures
        auto_config.MAX_TRADES_PER_HOUR = 15  # Limite raisonnable
        auto_config.MIN_SIGNAL_INTERVAL = 60  # 1 minute entre signaux
        auto_config.TRADING_CYCLE_DELAY = 30  # 30 secondes entre cycles

        # Gestion des risques renforcée
        auto_config.MAX_DAILY_LOSS = 800.0  # Limite perte quotidienne
        auto_config.MAX_POSITION_SIZE = 1     # 1 contrat max
        auto_config.STOP_LOSS_TICKS = 8       # Stop loss conservateur
        auto_config.TAKE_PROFIT_RATIO = 1.8   # Take profit équilibré

        # Validation données renforcée
        auto_config.VOLUME_VARIABILITY_CHECK = True
        auto_config.DELTA_VARIABILITY_CHECK = True
        auto_config.PRICE_VARIABILITY_CHECK = True
        auto_config.VALIDATE_OHLC_DATA = True
        auto_config.MIN_OHLC_QUALITY = 0.8
        auto_config.REJECT_INVALID_OHLC = True

        print(f"✅ Durée test: {auto_config.TEST_DURATION_MINUTES} minutes")
        print(f"✅ Max trades/heure: {auto_config.MAX_TRADES_PER_HOUR}")
        print(f"✅ Interval signaux: {auto_config.MIN_SIGNAL_INTERVAL}s")
        print(f"✅ Délai cycle: {auto_config.TRADING_CYCLE_DELAY}s")
        print(f"✅ Perte max/jour: ${auto_config.MAX_DAILY_LOSS}")
        print(f"✅ Position max: {auto_config.MAX_POSITION_SIZE} contrat(s)")
        print(f"✅ Validation OHLC: {'Activée' if auto_config.VALIDATE_OHLC_DATA else 'Désactivée'}")

        # Enregistrer le signal handler
        signal.signal(signal.SIGINT, signal_handler)

        print("\n🚀 LANCEMENT SYSTÈME 2H...")
        print("=" * 40)

        # Démarrer le système principal
        from launch_24_7_orderflow_trading import main

        # Créer une tâche pour le système principal
        system_task = asyncio.create_task(main())

        # Attendre 2 heures ou signal d'arrêt
        start_time = datetime.now()
        test_duration = timedelta(hours=2)

        print(f"⏰ Démarrage: {start_time.strftime('%H:%M:%S')}")
        print(f"⏰ Fin prévue: {(start_time + test_duration).strftime('%H:%M:%S')}")
        print("\n📊 MONITORING EN TEMPS RÉEL:")
        print("=" * 40)

        # Monitoring toutes les 5 minutes
        monitoring_interval = 300  # 5 minutes
        last_monitoring = start_time

        while datetime.now() < start_time + test_duration and not stop_system:
            current_time = datetime.now()
            elapsed = current_time - start_time
            remaining = test_duration - elapsed

            # Monitoring détaillé toutes les 5 minutes
            if (current_time - last_monitoring).total_seconds() >= monitoring_interval:
                print(f"\n⏰ {current_time.strftime('%H:%M:%S')} | "
                      f"Écoulé: {elapsed.total_seconds()/3600:.1f}h | "
                      f"Reste: {remaining.total_seconds()/3600:.1f}h | "
                      f"Status: {'🟢 ACTIF' if not stop_system else '🔴 ARRÊT'}")

                # Vérifier les logs récents pour détecter les problèmes
                try:
                    log_files = []
                    for pattern in ["logs/*.log", "*.log"]:
                        import glob
                        log_files.extend(glob.glob(pattern))

                    recent_errors = 0
                    recent_trades = 0
                    recent_signals = 0

                    for log_file in log_files:
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                            
                            # Analyser les dernières 50 lignes
                            recent_lines = lines[-50:] if len(lines) > 50 else lines
                            
                            for line in recent_lines:
                                line = line.strip()
                                
                                # Compter les erreurs récentes
                                if "ERROR" in line or "timeout" in line.lower():
                                    recent_errors += 1
                                
                                # Compter les trades récents
                                if "TRADE" in line or "EXECUTION" in line:
                                    recent_trades += 1
                                
                                # Compter les signaux récents
                                if "SIGNAL" in line:
                                    recent_signals += 1

                        except Exception:
                            continue

                    print(f"   📊 Erreurs récentes: {recent_errors}")
                    print(f"   🎯 Trades récents: {recent_trades}")
                    print(f"   📈 Signaux récents: {recent_signals}")

                    # Alerte si trop d'erreurs
                    if recent_errors > 5:
                        print(f"   ⚠️ ALERTE: {recent_errors} erreurs détectées")

                except Exception as e:
                    print(f"   ❌ Erreur monitoring: {e}")

                last_monitoring = current_time

            await asyncio.sleep(60)  # Check toutes les minutes

        # Arrêter le système
        print("\n🛑 ARRÊT SYSTÈME TEST 2H...")
        stop_system = True

        # Annuler la tâche système
        if not system_task.done():
            system_task.cancel()
            try:
                await system_task
            except asyncio.CancelledError:
                pass

        # Résumé du test
        end_time = datetime.now()
        total_duration = end_time - start_time

        print("\n📊 RÉSUMÉ TEST 2 HEURES")
        print("=" * 40)
        print(f"⏰ Début: {start_time.strftime('%H:%M:%S')}")
        print(f"⏰ Fin: {end_time.strftime('%H:%M:%S')}")
        print(f"⏰ Durée totale: {total_duration.total_seconds()/3600:.1f} heures")
        print(f"🎯 Mode: Test 2h avec corrections")
        print(f"✅ Status: Terminé proprement")

        # Analyse finale des résultats
        print("\n💡 ANALYSE FINALE")
        print("=" * 40)

        try:
            # Compter les trades totaux
            total_trades = 0
            total_signals = 0
            total_errors = 0

            log_files = []
            for pattern in ["logs/*.log", "*.log"]:
                import glob
                log_files.extend(glob.glob(pattern))

            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        line = line.strip()
                        
                        if "TRADE" in line or "EXECUTION" in line:
                            total_trades += 1
                        elif "SIGNAL" in line:
                            total_signals += 1
                        elif "ERROR" in line:
                            total_errors += 1

                except Exception:
                    continue

            print(f"📊 Trades totaux: {total_trades}")
            print(f"📈 Signaux totaux: {total_signals}")
            print(f"❌ Erreurs totales: {total_errors}")

            # Calculer les métriques
            if total_duration.total_seconds() > 0:
                trades_per_hour = total_trades / (total_duration.total_seconds() / 3600)
                signals_per_hour = total_signals / (total_duration.total_seconds() / 3600)
                
                print(f"📊 Trades/heure: {trades_per_hour:.1f}")
                print(f"📈 Signaux/heure: {signals_per_hour:.1f}")

            # Évaluation finale
            print("\n🎯 ÉVALUATION FINALE")
            print("=" * 40)

            if total_trades > 0:
                print("✅ Système actif - Trades effectués")
            else:
                print("❌ Aucun trade effectué")

            if total_signals > 0:
                print("✅ Signaux générés")
            else:
                print("❌ Aucun signal généré")

            if total_errors < 10:
                print("✅ Peu d'erreurs - Système stable")
            elif total_errors < 50:
                print("⚠️ Erreurs modérées - Surveillance nécessaire")
            else:
                print("❌ Trop d'erreurs - Correction nécessaire")

            # Recommandation finale
            print("\n🚀 RECOMMANDATION FINALE")
            print("=" * 40)

            if total_trades > 0 and total_signals > 0 and total_errors < 20:
                print("✅ SYSTÈME VALIDÉ - Prêt pour production")
                print("🎯 Performance satisfaisante")
                print("💡 Vous pouvez lancer en mode production")
            elif total_trades > 0 and total_signals > 0:
                print("⚠️ SYSTÈME PARTIELLEMENT VALIDÉ")
                print("🎯 Fonctionnel mais quelques problèmes")
                print("💡 Optimisations supplémentaires recommandées")
            else:
                print("❌ SYSTÈME NON VALIDÉ")
                print("🎯 Problèmes critiques détectés")
                print("💡 Diagnostic approfondi nécessaire")

        except Exception as e:
            print(f"❌ Erreur analyse finale: {e}")

        print("\n✅ Test 2h terminé")

    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
    finally:
        print("\n✅ Lancement terminé")

if __name__ == "__main__":
    asyncio.run(lance_systeme_2h_corrige())






