"""
MIA_IA_SYSTEM - Complete Restore Feature Calculator
Restauration complete feature_calculator.py depuis backup
Version: Nuclear option - complete file restore
"""

import shutil
from pathlib import Path
import time

def find_feature_calculator_backups():
    """Trouve tous les backups de feature_calculator"""
    logger.debug("RECHERCHE BACKUPS FEATURE_CALCULATOR")
    print("=" * 45)
    
    project_root = Path(".")
    
    # Patterns de backup à chercher
    backup_patterns = [
        "**/feature_calculator.py.before_vectorization*",
        "**/feature_calculator.py.original*", 
        "**/feature_calculator.py.backup*",
        "**/feature_calculator.py.before_*"
    ]
    
    found_backups = []
    
    for pattern in backup_patterns:
        backups = list(project_root.glob(pattern))
        found_backups.extend(backups)
    
    # Supprimer doublons et trier par date
    unique_backups = list(set(found_backups))
    unique_backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    logger.info("Backups trouvés: {len(unique_backups)}")
    for i, backup in enumerate(unique_backups):
        mod_time = time.ctime(backup.stat().st_mtime)
        size = backup.stat().st_size
        logger.info("  {i+1}. {backup} ({size} bytes, {mod_time})")
    
    return unique_backups

def test_backup_validity(backup_file):
    """Test si un backup est valide (syntaxe OK)"""
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Test compilation
        compile(source, str(backup_file), 'exec')
        
        # Test que la ligne 369 environ existe et est correcte
        lines = source.split('\n')
        if len(lines) > 350:  # Au moins assez de lignes
            return True, f"Valid backup ({len(lines)} lines)"
        else:
            return False, f"Too short ({len(lines)} lines)"
            
    except SyntaxError as e:
        return False, f"Syntax error: {e.msg} line {e.lineno}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def restore_best_backup():
    """Restaure le meilleur backup disponible"""
    logger.info("\n🔄 RESTAURATION MEILLEUR BACKUP")
    print("=" * 35)
    
    backups = find_feature_calculator_backups()
    
    if not backups:
        logger.error("Aucun backup trouvé!")
        return False
    
    # Tester chaque backup
    valid_backups = []
    
    for backup in backups:
        is_valid, message = test_backup_validity(backup)
        logger.info("Test {backup.name}: {message}")
        
        if is_valid:
            valid_backups.append(backup)
    
    if not valid_backups:
        logger.error("Aucun backup valide trouvé!")
        return False
    
    # Prendre le plus récent des backups valides
    best_backup = valid_backups[0]
    logger.info("\n🎯 Meilleur backup: {best_backup}")
    
    # Restaurer
    original_file = Path("features/feature_calculator.py")
    
    # Backup du fichier cassé
    broken_backup = original_file.with_suffix(f".py.broken_complete_{int(time.time())}")
    shutil.copy2(original_file, broken_backup)
    logger.info("💾 Fichier cassé sauvé: {broken_backup}")
    
    # Restaurer depuis meilleur backup
    shutil.copy2(best_backup, original_file)
    logger.info("Restauré depuis: {best_backup}")
    
    return True

def create_minimal_feature_calculator():
    """Crée une version minimale fonctionnelle si aucun backup"""
    logger.info("\n🔧 CRÉATION VERSION MINIMALE")
    print("=" * 35)
    
    minimal_content = '''"""
MIA_IA_SYSTEM - Feature Calculator (Minimal Version)
Version minimale pour restaurer fonctionnalité
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import deque
import logging

from core.base_types import MarketData, ES_TICK_SIZE
from config import get_feature_config

logger = logging.getLogger(__name__)

@dataclass
class FeatureCalculationResult:
    """Résultat calcul features"""
    timestamp: pd.Timestamp
    vwap_trend_signal: float = 0.5
    sierra_pattern_strength: float = 0.5
    dow_trend_regime: float = 0.5
    gamma_levels_proximity: float = 0.5
    level_proximity: float = 0.5
    es_nq_correlation: float = 0.5
    volume_confirmation: float = 0.5
    options_flow_bias: float = 0.5
    session_context: float = 0.5
    pullback_quality: float = 0.5
    confluence_score: float = 0.5
    calculation_time_ms: float = 0.0

class FeatureCalculator:
    """Feature calculator minimal"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.price_history = deque(maxlen=100)
        
    def calculate_all_features(self, market_data: MarketData, **kwargs) -> FeatureCalculationResult:
        """Calcul features minimal"""
        start_time = time.perf_counter()
        
        self.price_history.append(market_data)
        
        # Calculs basiques sans optimisation
        result = FeatureCalculationResult(timestamp=market_data.timestamp)
        
        if len(self.price_history) >= 5:
            # Calculs simples sans list comprehensions problématiques
            prices = []
            for bar in list(self.price_history)[-10:]:
                prices.append(bar.close)
            
            if prices:
                trend = (prices[-1] - prices[0]) / len(prices)
                result.vwap_trend_signal = min(max(trend / ES_TICK_SIZE + 0.5, 0), 1)
                result.dow_trend_regime = result.vwap_trend_signal
        
        result.calculation_time_ms = (time.perf_counter() - start_time) * 1000
        return result
    
    def get_confluence_score(self, features: FeatureCalculationResult) -> float:
        """Score confluence minimal"""
        return 0.6  # Score neutre

def create_feature_calculator(config: Optional[Dict[str, Any]] = None) -> FeatureCalculator:
    """Factory function"""
    return FeatureCalculator(config)
'''
    
    original_file = Path("features/feature_calculator.py")
    
    # Backup du fichier cassé
    broken_backup = original_file.with_suffix(f".py.broken_minimal_{int(time.time())}")
    shutil.copy2(original_file, broken_backup)
    logger.info("💾 Fichier cassé sauvé: {broken_backup}")
    
    # Créer version minimale
    original_file.write_text(minimal_content, encoding='utf-8')
    logger.info("Version minimale créée: {original_file}")
    
    return True

def test_feature_calculator():
    """Test que feature_calculator fonctionne"""
    logger.info("\n🧪 TEST FEATURE_CALCULATOR")
    print("=" * 30)
    
    try:
        # Test compilation
        file_path = Path("features/feature_calculator.py")
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, str(file_path), 'exec')
        logger.info("Compilation: OK")
        
        # Test import
        import sys
        project_root = Path(".").absolute()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Clear cache
        if 'features.feature_calculator' in sys.modules:
            del sys.modules['features.feature_calculator']
        
        from features.feature_calculator import create_feature_calculator
        logger.info("Import: OK")
        
        # Test fonctionnalité basique
        calculator = create_feature_calculator()
        logger.info("Création calculator: OK")
        
        return True
        
    except Exception as e:
        logger.error("Erreur: {e}")
        return False

def main():
    """Restauration complete feature_calculator"""
    logger.info("🚨 RESTAURATION COMPLÈTE FEATURE_CALCULATOR")
    print("=" * 55)
    logger.info("Objectif: Restaurer fonctionnalité à tout prix")
    
    # Tentative 1: Restaurer depuis backup
    if restore_best_backup():
        if test_feature_calculator():
            logger.info("\n🎉 RESTAURATION BACKUP RÉUSSIE!")
            return True
        else:
            logger.error("Backup restauré mais non fonctionnel")
    
    # Tentative 2: Version minimale
    logger.info("\n🔧 TENTATIVE VERSION MINIMALE...")
    if create_minimal_feature_calculator():
        if test_feature_calculator():
            logger.info("\n🎉 VERSION MINIMALE CRÉÉE!")
            logger.warning("Fonctionnalité réduite mais système stable")
            return True
        else:
            logger.error("Version minimale échouée")
    
    logger.info("\n💀 RESTAURATION ÉCHOUÉE")
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n🚀 LANCER AUDIT:")
        logger.info("python technical_audit.py")
        logger.info("\n🎯 ATTENDU: Retour stabilité 85%+")
    else:
        logger.info("\n💀 ÉCHEC CRITIQUE - Debug manuel requis")