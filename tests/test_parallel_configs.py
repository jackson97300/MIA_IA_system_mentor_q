#!/usr/bin/env python3
"""
Tests parallèles avec différentes configurations
MIA_IA_SYSTEM - Comparaison rapide de paramètres
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = get_logger(__name__)

def create_test_configs():
    """Crée 3 configurations de test différentes"""
    
    configs = {
        "CONSERVATEUR": {
            "name": "CONSERVATEUR",
            "description": "Win Rate 40-50% - Paramètres prudents",
            "orderflow": {
                "min_confidence_threshold": 0.150,
                "footprint_threshold": 0.050,
                "volume_threshold": 10,
                "delta_threshold": 0.06
            },
            "confluence": {
                "PREMIUM_SIGNAL": 0.35,
                "STRONG_SIGNAL": 0.28,
                "GOOD_SIGNAL": 0.22,
                "WEAK_SIGNAL": 0.15
            },
            "expected_win_rate": "40-50%",
            "risk_level": "FAIBLE"
        },
        
        "MODÉRÉ": {
            "name": "MODÉRÉ",
            "description": "Win Rate 45-55% - Paramètres équilibrés",
            "orderflow": {
                "min_confidence_threshold": 0.180,
                "footprint_threshold": 0.060,
                "volume_threshold": 12,
                "delta_threshold": 0.08
            },
            "confluence": {
                "PREMIUM_SIGNAL": 0.38,
                "STRONG_SIGNAL": 0.30,
                "GOOD_SIGNAL": 0.25,
                "WEAK_SIGNAL": 0.18
            },
            "expected_win_rate": "45-55%",
            "risk_level": "MOYEN"
        },
        
        "AGRESSIF": {
            "name": "AGRESSIF", 
            "description": "Win Rate 50-60% - Paramètres optimistes",
            "orderflow": {
                "min_confidence_threshold": 0.220,
                "footprint_threshold": 0.080,
                "volume_threshold": 15,
                "delta_threshold": 0.12
            },
            "confluence": {
                "PREMIUM_SIGNAL": 0.42,
                "STRONG_SIGNAL": 0.35,
                "GOOD_SIGNAL": 0.28,
                "WEAK_SIGNAL": 0.20
            },
            "expected_win_rate": "50-60%",
            "risk_level": "ÉLEVÉ"
        }
    }
    
    return configs

def create_launcher_script(config_name, config_data):
    """Crée un script de lancement pour chaque configuration"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Lanceur Test {config_name}
MIA_IA_SYSTEM - Configuration {config_data['description']}
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - {config_name} - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_{config_name.lower()}.log'),
        logging.StreamHandler()
    ]
)
logger = get_logger(__name__)

class TestConfig:
    """Configuration de test {config_name}"""
    
    def get_orderflow_config(self):
        return {{
            "min_confidence_threshold": {config_data['orderflow']['min_confidence_threshold']},
            "footprint_threshold": {config_data['orderflow']['footprint_threshold']},
            "volume_threshold": {config_data['orderflow']['volume_threshold']},
            "delta_threshold": {config_data['orderflow']['delta_threshold']},
            "lookback_periods": 10
        }}
    
    def get_level2_config(self):
        return {{
            "depth": 10,
            "update_frequency": 0.1
        }}

async def main():
    """Lancement test {config_name}"""
    
    logger.info("🚀 === TEST {config_name} DÉMARRÉ ===")
    logger.info(f"📊 Configuration: {{config_data['description']}}")
    logger.info(f"🎯 Win Rate attendu: {{config_data['expected_win_rate']}}")
    logger.info(f"⚠️ Niveau de risque: {{config_data['risk_level']}}")
    
    # Créer dossier logs
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    
    # Importer et lancer le système
    from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
    
    launcher = OrderFlow24_7Launcher(live_trading=False)
    
    # Override configuration
    config = launcher._create_24_7_orderflow_config()
    
    # Appliquer paramètres de test
    config.min_confidence_threshold = {config_data['orderflow']['min_confidence_threshold']}
    config.footprint_threshold = {config_data['orderflow']['footprint_threshold']}
    config.volume_threshold = {config_data['orderflow']['volume_threshold']}
    config.delta_threshold = {config_data['orderflow']['delta_threshold']}
    
    logger.info("✅ Configuration appliquée")
    logger.info(f"   📊 min_confidence_threshold: {{config.min_confidence_threshold}}")
    logger.info(f"   🎯 footprint_threshold: {{config.footprint_threshold}}")
    logger.info(f"   📈 volume_threshold: {{config.volume_threshold}}")
    logger.info(f"   💰 delta_threshold: {{config.delta_threshold}}")
    
    # Lancer le système
    try:
        await launcher.start_24_7_trading()
    except KeyboardInterrupt:
        logger.info("⏹️ Test {config_name} arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test {config_name}: {{e}}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return script_content

async def generate_test_scripts():
    """Génère les scripts de test pour chaque configuration"""
    
    logger.info("🔧 === GÉNÉRATION SCRIPTS DE TEST PARALLÈLES ===")
    
    configs = create_test_configs()
    
    # Créer dossier logs
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    
    for config_name, config_data in configs.items():
        script_content = create_launcher_script(config_name, config_data)
        
        filename = f"test_{config_name.lower()}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"✅ Script généré: {{filename}}")
        logger.info(f"   📊 {{config_data['description']}}")
        logger.info(f"   🎯 Win Rate attendu: {{config_data['expected_win_rate']}}")
    
    # Créer script de lancement parallèle
    parallel_script = '''#!/usr/bin/env python3
"""
Lancement parallèle des tests
MIA_IA_SYSTEM - Tests simultanés
"""

import subprocess
import sys
import time
from pathlib import Path

def launch_parallel_tests():
    """Lance les 3 tests en parallèle"""
    
    print("🚀 === LANCEMENT TESTS PARALLÈLES ===")
    print("📊 3 configurations testées simultanément")
    print("⏱️ Durée recommandée: 2-3 heures")
    print()
    
    # Lancer les 3 processus
    processes = []
    
    for config in ["CONSERVATEUR", "MODÉRÉ", "AGRESSIF"]:
        cmd = [sys.executable, f"test_{{config.lower()}}.py"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append((config, process))
        print(f"✅ Test {{config}} lancé (PID: {{process.pid}})")
    
    print()
    print("📊 === MONITORING ===")
    print("Les tests s'exécutent en parallèle...")
    print("Logs disponibles dans le dossier 'logs/'")
    print("Appuyez sur Ctrl+C pour arrêter tous les tests")
    print()
    
    try:
        # Attendre que tous les processus se terminent
        for config, process in processes:
            process.wait()
            print(f"✅ Test {{config}} terminé")
            
    except KeyboardInterrupt:
        print("\\n⏹️ Arrêt des tests...")
        for config, process in processes:
            process.terminate()
            print(f"⏹️ Test {{config}} arrêté")
    
    print("\\n📊 === ANALYSE DES RÉSULTATS ===")
    print("Consultez les logs dans le dossier 'logs/' pour comparer les performances")

if __name__ == "__main__":
    launch_parallel_tests()
'''
    
    with open("launch_parallel_tests.py", 'w', encoding='utf-8') as f:
        f.write(parallel_script)
    
    logger.info("✅ Script de lancement parallèle généré: launch_parallel_tests.py")
    
    # Créer script d'analyse des résultats
    analysis_script = '''#!/usr/bin/env python3
"""
Analyse des résultats des tests parallèles
MIA_IA_SYSTEM - Comparaison des performances
"""

import re
import glob
from pathlib import Path

def analyze_test_results():
    """Analyse les résultats des tests"""
    
    print("📊 === ANALYSE DES RÉSULTATS DES TESTS ===")
    
    log_files = glob.glob("logs/test_*.log")
    
    results = {}
    
    for log_file in log_files:
        config_name = Path(log_file).stem.replace("test_", "").upper()
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire métriques
        win_rate_match = re.search(r"Win Rate: (\\d+\\.\\d+)%", content)
        pnl_match = re.search(r"P&L: ([+-]?\\d+\\.\\d+)\\$", content)
        trades_match = re.search(r"(\\d+) trades", content)
        
        if win_rate_match and pnl_match and trades_match:
            results[config_name] = {{
                "win_rate": float(win_rate_match.group(1)),
                "pnl": float(pnl_match.group(1)),
                "trades": int(trades_match.group(1))
            }}
    
    # Afficher comparaison
    print("\\n🎯 === COMPARAISON DES PERFORMANCES ===")
    print(f"{'Configuration':<15} {'Win Rate':<10} {'P&L':<10} {'Trades':<8}")
    print("-" * 50)
    
    for config, metrics in results.items():
        print(f"{{config:<15}} {{metrics['win_rate']:<10.1f}% {{metrics['pnl']:<10.2f}$ {{metrics['trades']:<8}}")
    
    # Recommandation
    if results:
        best_config = max(results.items(), key=lambda x: x[1]['win_rate'])
        print(f"\\n🏆 Configuration recommandée: {{best_config[0]}}")
        print(f"   Win Rate: {{best_config[1]['win_rate']:.1f}}%")
        print(f"   P&L: {{best_config[1]['pnl']:.2f}}$")

if __name__ == "__main__":
    analyze_test_results()
'''
    
    with open("analyze_test_results.py", 'w', encoding='utf-8') as f:
        f.write(analysis_script)
    
    logger.info("✅ Script d'analyse généré: analyze_test_results.py")
    
    logger.info("\\n🎯 === RÉSUMÉ DES SCRIPTS GÉNÉRÉS ===")
    logger.info("📊 test_conservateur.py - Paramètres prudents")
    logger.info("📊 test_modéré.py - Paramètres équilibrés") 
    logger.info("📊 test_agressif.py - Paramètres optimistes")
    logger.info("🚀 launch_parallel_tests.py - Lancement simultané")
    logger.info("📈 analyze_test_results.py - Analyse des résultats")
    
    return True

if __name__ == "__main__":
    asyncio.run(generate_test_scripts())
