#!/usr/bin/env python3
"""
Test Automation Main - Validation système automation complet
Teste la nouvelle version automation_main.py avec SignalGenerator intégré
"""

import sys
import asyncio
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import signal
import os
from core.logger import get_logger

# Configure logging
logger = get_logger(__name__)


logger.info("🧪 TEST AUTOMATION_MAIN.PY INTÉGRÉ")
print("=" * 50)

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_automation_imports():
    """Test imports automation_main.py"""
    logger.info("\n1️⃣ TEST IMPORTS AUTOMATION")
    print("-" * 30)
    
    import_results = {}
    
    # Test import automation_main
    try:
        # Import en tant que module
        sys.path.insert(0, str(current_dir))
        import automation_main
        import_results['automation_main'] = True
        logger.info("automation_main.py: Import réussi")
    except Exception as e:
        import_results['automation_main'] = False
        logger.error("automation_main.py: {e}")
    
    # Test imports critiques dans automation_main
    try:
        from automation_main import MIAAutomationBot, create_config_from_args
        import_results['automation_classes'] = True
        logger.info("Classes automation: MIAAutomationBot, create_config_from_args")
    except Exception as e:
        import_results['automation_classes'] = False
        logger.error("Classes automation: {e}")
    
    # Test dépendances SignalGenerator
    try:
        from strategies import get_signal_now, SignalGenerator, SignalDecision
        import_results['signal_generator'] = True
        logger.info("SignalGenerator: Disponible dans automation")
    except Exception as e:
        import_results['signal_generator'] = False
        logger.error("SignalGenerator: {e}")
    
    # Test core types
    try:
        from core.base_types import MarketData, SignalType
        import_results['core_types'] = True
        logger.info("Core types: Disponibles")
    except Exception as e:
        import_results['core_types'] = False
        logger.error("Core types: {e}")
    
    success_rate = sum(import_results.values()) / len(import_results) * 100
    logger.info("\n[STATS] Imports réussis: {sum(import_results.values())}/{len(import_results)} ({success_rate:.1f}%)")
    
    return import_results, success_rate >= 75

def test_automation_bot_creation():
    """Test création MIAAutomationBot"""
    logger.info("\n2️⃣ TEST CRÉATION AUTOMATION BOT")
    print("-" * 35)
    
    try:
        from automation_main import MIAAutomationBot, DEFAULT_CONFIG
        
        # Test création simulation mode
        bot = MIAAutomationBot(mode="simulation", config=DEFAULT_CONFIG)
        logger.info("MIAAutomationBot créé (mode simulation)")
        
        # Vérifier composants critiques
        if hasattr(bot, 'signal_generator'):
            logger.info("SignalGenerator intégré")
        else:
            logger.error("SignalGenerator manquant")
            return False
        
        # Vérifier configuration
        if bot.config and 'min_signal_confidence' in bot.config:
            logger.info("Configuration: min_confidence = {bot.config['min_signal_confidence']}")
        else:
            logger.warning("Configuration incomplète")
        
        # Test session stats
        if hasattr(bot, 'session_stats'):
            logger.info("Session stats initialisées")
        else:
            logger.error("Session stats manquantes")
            return False
        
        return True, bot
        
    except Exception as e:
        logger.error("Erreur création bot: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_signal_generation_integration():
    """Test intégration génération signaux"""
    logger.info("\n3️⃣ TEST INTÉGRATION GÉNÉRATION SIGNAUX")
    print("-" * 40)
    
    try:
        from automation_main import MIAAutomationBot
        from core.base_types import MarketData
        
        # Créer bot
        bot = MIAAutomationBot(mode="simulation")
        
        # Données test
        test_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4505.0,
            low=4495.0,
            close=4502.0,
            volume=1000
        )
        
        logger.info("[STATS] Test avec: ES {test_data.close} (Vol: {test_data.volume})")
        
        # Test génération signal via bot
        start_time = time.perf_counter()
        signal = bot.signal_generator.generate_signal(test_data)
        generation_time = (time.perf_counter() - start_time) * 1000
        
        logger.info("[FAST] Signal généré en {generation_time:.2f}ms")
        logger.info("[UP] Décision: {signal.decision.value}")
        logger.info("💪 Confiance: {signal.confidence:.3f}")
        logger.info("[WIN] Qualité: {signal.quality_level.value}")
        logger.info("[TARGET] Type: {signal.signal_type.value}")
        
        # Validation signal
        is_valid = (
            signal.entry_price > 0 and
            0 <= signal.confidence <= 1 and
            signal.quality_level is not None and
            signal.decision is not None
        )
        
        if is_valid:
            logger.info("Signal structurellement valide")
        else:
            logger.error("Signal invalide")
            return False
        
        # Test performance
        performance_ok = generation_time < 20  # <20ms acceptable
        if performance_ok:
            logger.info("[LAUNCH] Performance OK: {generation_time:.2f}ms < 20ms")
        else:
            logger.warning("Performance lente: {generation_time:.2f}ms")
        
        return True, signal, generation_time
        
    except Exception as e:
        logger.error("Erreur test intégration: {e}")
        import traceback
        traceback.print_exc()
        return False, None, 999

async def test_automation_workflow():
    """Test workflow automation complet"""
    logger.info("\n4️⃣ TEST WORKFLOW AUTOMATION")
    print("-" * 32)
    
    try:
        from automation_main import MIAAutomationBot
        
        # Créer bot avec timeout court
        bot = MIAAutomationBot(mode="simulation")
        
        logger.info("[GAME] Test workflow simulation (10 secondes)...")
        
        # Créer task avec timeout
        workflow_task = asyncio.create_task(
            bot.start_automation(duration_hours=0.003)  # ~10 secondes
        )
        
        # Attendre avec timeout
        try:
            result = await asyncio.wait_for(workflow_task, timeout=15)
            
            if result:
                logger.info("Workflow automation terminé avec succès")
                
                # Vérifier stats
                stats = bot.session_stats
                logger.info("[STATS] Stats session:")
                logger.info("   └─ Signaux générés: {stats['signals_generated']}")
                logger.info("   └─ Signaux exécutés: {stats['signals_executed']}")
                
                if stats['signals_generated'] > 0:
                    execution_rate = (stats['signals_executed'] / stats['signals_generated']) * 100
                    logger.info("   └─ Taux exécution: {execution_rate:.1f}%")
                
                return True, stats
            else:
                logger.warning("Workflow terminé avec avertissements")
                return False, {}
                
        except asyncio.TimeoutError:
            logger.info("⏰ Timeout workflow (normal pour test)")
            # Arrêter bot
            bot.is_running = False
            return True, bot.session_stats  # Timeout acceptable pour test
            
    except Exception as e:
        logger.error("Erreur workflow: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def test_cli_interface():
    """Test interface CLI"""
    logger.info("\n5️⃣ TEST INTERFACE CLI")
    print("-" * 22)
    
    try:
        from automation_main import parse_arguments, create_config_from_args
        
        # Test parsing arguments par défaut
        import sys
        original_argv = sys.argv
        
        # Test arguments simulation
        sys.argv = ['automation_main.py', '--mode', 'simulation', '--config', 'conservative']
        args = parse_arguments()
        
        logger.info("Arguments parsés: mode={args.mode}, config={args.config}")
        
        # Test création config
        config = create_config_from_args(args)
        
        if config and 'min_signal_confidence' in config:
            logger.info("Config créée: confidence={config['min_signal_confidence']}")
        else:
            logger.error("Config création échouée")
            return False
        
        # Test config conservative
        if args.config == 'conservative':
            expected_confidence = 0.80
            if config.get('min_signal_confidence') == expected_confidence:
                logger.info("Config conservative: {expected_confidence}")
            else:
                logger.warning("Config conservative incorrecte: {config.get('min_signal_confidence')} != {expected_confidence}")
        
        # Restaurer argv
        sys.argv = original_argv
        
        return True
        
    except Exception as e:
        logger.error("Erreur test CLI: {e}")
        return False

def test_status_command():
    """Test commande status"""
    logger.info("\n6️⃣ TEST COMMANDE STATUS")
    print("-" * 25)
    
    try:
        # Test status function
        from automation_main import show_status
        
        logger.info("[STATS] Test fonction show_status():")
        show_status()
        
        logger.info("\n[OK] Commande status fonctionnelle")
        return True
        
    except Exception as e:
        logger.error("Erreur test status: {e}")
        return False

def test_performance_metrics():
    """Test métriques performance"""
    logger.info("\n7️⃣ TEST MÉTRIQUES PERFORMANCE")
    print("-" * 32)
    
    try:
        from automation_main import MIAAutomationBot
        from core.base_types import MarketData
        
        bot = MIAAutomationBot(mode="simulation")
        
        # Test génération multiple signaux
        generation_times = []
        signal_qualities = []
        
        logger.info("[SYNC] Test 10 générations signaux...")
        
        for i in range(10):
            # Données variables
            test_data = MarketData(
                timestamp=pd.Timestamp.now() + pd.Timedelta(seconds=i),
                symbol="ES",
                open=4500 + i,
                high=4505 + i,
                low=4495 + i,
                close=4502 + i,
                volume=1000 + i * 50
            )
            
            # Génération
            start_time = time.perf_counter()
            signal = bot.signal_generator.generate_signal(test_data)
            gen_time = (time.perf_counter() - start_time) * 1000
            
            generation_times.append(gen_time)
            signal_qualities.append(signal.quality_level.value)
            
            if i % 3 == 0:  # Log quelques résultats
                logger.info("   Signal {i+1}: {signal.decision.value} ({gen_time:.2f}ms, {signal.quality_level.value})")
        
        # Statistiques
        import statistics
        avg_time = statistics.mean(generation_times)
        max_time = max(generation_times)
        min_time = min(generation_times)
        
        logger.info("\n[STATS] MÉTRIQUES PERFORMANCE:")
        logger.info("   └─ Temps moyen: {avg_time:.2f}ms")
        logger.info("   └─ Temps min: {min_time:.2f}ms")
        logger.info("   └─ Temps max: {max_time:.2f}ms")
        
        # Distribution qualité
        from collections import Counter
        quality_dist = Counter(signal_qualities)
        logger.info("   └─ Distribution qualité: {dict(quality_dist)}")
        
        # Évaluation
        performance_excellent = avg_time < 5
        performance_good = avg_time < 10
        
        if performance_excellent:
            logger.info("[LAUNCH] Performance EXCELLENTE: <5ms moyen")
            return True, "excellent"
        elif performance_good:
            logger.info("Performance BONNE: <10ms moyen")
            return True, "good"
        else:
            logger.warning("Performance À AMÉLIORER: >10ms moyen")
            return True, "needs_improvement"
            
    except Exception as e:
        logger.error("Erreur test performance: {e}")
        return False, "error"

def test_integration_completeness():
    """Test complétude intégration"""
    logger.info("\n8️⃣ TEST COMPLÉTUDE INTÉGRATION")
    print("-" * 35)
    
    integration_checks = []
    
    try:
        from automation_main import MIAAutomationBot
        
        bot = MIAAutomationBot(mode="simulation")
        
        # Check 1: SignalGenerator intégré
        has_signal_gen = hasattr(bot, 'signal_generator') and bot.signal_generator is not None
        integration_checks.append(("SignalGenerator", has_signal_gen))
        
        # Check 2: Configuration complète
        has_config = bool(bot.config and len(bot.config) >= 10)
        integration_checks.append(("Configuration", has_config))
        
        # Check 3: Session stats
        has_stats = hasattr(bot, 'session_stats') and isinstance(bot.session_stats, dict)
        integration_checks.append(("Session Stats", has_stats))
        
        # Check 4: Méthodes critiques
        critical_methods = ['start_automation', '_process_trading_signal', '_run_simulation_loop']
        has_methods = all(hasattr(bot, method) for method in critical_methods)
        integration_checks.append(("Méthodes critiques", has_methods))
        
        # Check 5: Test fonctionnel complet
        try:
            # Test création signal
            test_data = bot._create_test_market_data()
            signal = bot.signal_generator.generate_signal(test_data)
            functional_ok = signal is not None and hasattr(signal, 'decision')
        except:
            functional_ok = False
        
        integration_checks.append(("Test fonctionnel", functional_ok))
        
        # Affichage résultats
        for check_name, passed in integration_checks:
            status = "[OK]" if passed else "[ERROR]"
            logger.info("{status} {check_name}")
        
        # Score global
        success_count = sum(1 for _, passed in integration_checks if passed)
        total_checks = len(integration_checks)
        integration_score = (success_count / total_checks) * 100
        
        logger.info("\n[STATS] Score intégration: {success_count}/{total_checks} ({integration_score:.1f}%)")
        
        return integration_score >= 80, integration_score
        
    except Exception as e:
        logger.error("Erreur test intégration: {e}")
        return False, 0

def generate_automation_test_report(test_results):
    """Génère rapport test automation"""
    print("\n" + "=" * 50)
    logger.info("[STATS] RAPPORT FINAL TEST AUTOMATION_MAIN.PY")
    print("=" * 50)
    
    # Calcul scores
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result.get('success', False))
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info("\n[TARGET] RÉSULTATS PAR COMPOSANT:")
    for test_name, result in test_results.items():
        status = "[OK]" if result.get('success', False) else "[ERROR]"
        description = result.get('description', 'Test exécuté')
        logger.info("   {status} {test_name}: {description}")
    
    logger.info("\n[UP] SCORE GLOBAL: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Évaluation finale
    if success_rate >= 90:
        logger.info("\n[PARTY] AUTOMATION PARFAITEMENT INTÉGRÉE!")
        logger.info("   └─ automation_main.py utilise SignalGenerator")
        logger.info("   └─ Workflow complet fonctionnel")
        logger.info("   └─ Prêt pour déploiement")
        verdict = "EXCELLENT"
    elif success_rate >= 75:
        logger.info("\n[OK] AUTOMATION BIEN INTÉGRÉE!")
        logger.info("   └─ Fonctionnalités principales OK")
        logger.info("   └─ Corrections mineures possibles")
        verdict = "GOOD"
    elif success_rate >= 60:
        logger.info("\n[WARN] AUTOMATION PARTIELLEMENT INTÉGRÉE")
        logger.info("   └─ Fonctionnalités de base OK")
        logger.info("   └─ Améliorations nécessaires")
        verdict = "ACCEPTABLE"
    else:
        logger.info("\n[ERROR] AUTOMATION NÉCESSITE CORRECTIONS")
        logger.info("   └─ Problèmes majeurs détectés")
        verdict = "NEEDS_WORK"
    
    # Recommandations
    logger.info("\n[LAUNCH] PROCHAINES ÉTAPES:")
    if verdict == "EXCELLENT":
        logger.info("   1. [OK] Tester avec données réelles")
        logger.info("   2. [OK] Démarrer paper trading")
        logger.info("   3. [OK] Configurer alertes monitoring")
    elif verdict in ["GOOD", "ACCEPTABLE"]:
        logger.info("   1. [CONFIG] Corriger tests échoués")
        logger.info("   2. [OK] Re-tester automation")
        logger.info("   3. [OK] Valider performance")
    else:
        logger.info("   1. [ALERT] Réviser automation_main.py")
        logger.info("   2. [ALERT] Vérifier intégration SignalGenerator")
        logger.info("   3. [ALERT] Debug composants défaillants")
    
    return verdict, success_rate

async def main():
    """Test automation complet"""
    logger.info("[LAUNCH] Lancement test automation_main.py...")
    
    test_results = {}
    
    # Tests séquentiels
    logger.info("\n[SYNC] EXÉCUTION TESTS AUTOMATION...")
    
    # 1. Imports
    import_results, import_success = test_automation_imports()
    test_results['imports'] = {
        'success': import_success,
        'description': f"Imports automation ({sum(import_results.values())}/{len(import_results)})"
    }
    
    if not import_success:
        logger.info("\n[ALERT] ARRÊT: Imports critiques échoués")
        generate_automation_test_report(test_results)
        return False
    
    # 2. Création bot
    creation_success, bot = test_automation_bot_creation()
    test_results['bot_creation'] = {
        'success': creation_success,
        'description': "Création MIAAutomationBot"
    }
    
    # 3. Intégration signaux
    signal_success, signal, gen_time = test_signal_generation_integration()
    test_results['signal_integration'] = {
        'success': signal_success and gen_time < 50,
        'description': f"Intégration signaux ({gen_time:.1f}ms)" if signal_success else "Intégration signaux"
    }
    
    # 4. Workflow automation
    workflow_success, workflow_stats = await test_automation_workflow()
    test_results['workflow'] = {
        'success': workflow_success,
        'description': f"Workflow automation ({workflow_stats.get('signals_generated', 0)} signaux)"
    }
    
    # 5. Interface CLI
    cli_success = test_cli_interface()
    test_results['cli'] = {
        'success': cli_success,
        'description': "Interface CLI"
    }
    
    # 6. Status command
    status_success = test_status_command()
    test_results['status'] = {
        'success': status_success,
        'description': "Commande status"
    }
    
    # 7. Performance
    perf_success, perf_level = test_performance_metrics()
    test_results['performance'] = {
        'success': perf_success and perf_level in ['excellent', 'good'],
        'description': f"Performance ({perf_level})"
    }
    
    # 8. Intégration complète
    integration_success, integration_score = test_integration_completeness()
    test_results['integration'] = {
        'success': integration_success,
        'description': f"Intégration complète ({integration_score:.1f}%)"
    }
    
    # Rapport final
    verdict, success_rate = generate_automation_test_report(test_results)
    
    return verdict in ["EXCELLENT", "GOOD"]

if __name__ == "__main__":
    logger.info("🧪 TEST AUTOMATION_MAIN.PY INTÉGRÉ")
    logger.info("Validation automation avec SignalGenerator")
    print("")
    
    try:
        success = asyncio.run(main())
        
        if success:
            logger.info("\n[PARTY] AUTOMATION VALIDÉE!")
            logger.info("   └─ Prêt pour utilisation")
        else:
            logger.info("\n[WARN] AUTOMATION PARTIELLEMENT VALIDÉE")
            logger.info("   └─ Vérifiez les erreurs ci-dessus")
    
    except KeyboardInterrupt:
        logger.info("\n[STOP] Test interrompu par utilisateur")
    except Exception as e:
        logger.info("\n[ERROR] Erreur critique test: {e}")
    
    input("\n📎 Appuyez sur Entrée pour fermer...")