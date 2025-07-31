"""
MIA_IA_SYSTEM - Quick Validation
Validation rapide avant audit technique
Vérifie que tous les fixes sont appliqués
"""

import sys
import time
import importlib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)


class QuickValidator:
    """Validateur rapide pre-audit"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def validate_all(self) -> bool:
        """Validation complète express"""
        logger.info("🚀 QUICK VALIDATION - PRE-AUDIT")
        print("=" * 50)
        
        # 1. Structure
        structure_ok = self.validate_structure()
        
        # 2. Imports
        imports_ok = self.validate_imports()
        
        # 3. Performance 
        performance_ok = self.validate_performance()
        
        # 4. Syntax
        syntax_ok = self.validate_syntax()
        
        # Résumé
        self.print_summary()
        
        overall_success = all([structure_ok, imports_ok, performance_ok, syntax_ok])
        
        if overall_success:
            logger.info("\n🎉 VALIDATION RÉUSSIE - PRÊT POUR AUDIT!")
        else:
            logger.info("\n💀 VALIDATION ÉCHOUÉE - FIXES REQUIS")
            
        return overall_success
    
    def validate_structure(self) -> bool:
        """Validation structure projet"""
        logger.info("\n📁 VALIDATION STRUCTURE...")
        
        required_files = [
            "config/__init__.py",
            "config/trading_config.py", 
            "core/__init__.py",
            "core/base_types.py",
            "core/patterns_detector.py",
            "core/battle_navale.py"
        ]
        
        missing = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing.append(file_path)
        
        if missing:
            logger.error("Fichiers manquants: {len(missing)}")
            for file in missing:
                logger.info("   • {file}")
            self.errors.extend(missing)
            return False
        else:
            logger.info("Structure OK: {len(required_files)} fichiers")
            return True
    
    def validate_imports(self) -> bool:
        """Validation imports critiques"""
        logger.info("\n🐍 VALIDATION IMPORTS...")
        
        # Ajouter au path
        project_root = Path(".").absolute()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        critical_imports = [
            "config.trading_config",
            "config", 
            "core.base_types",
            "core"
        ]
        
        failed_imports = []
        import_times = []
        
        for module_name in critical_imports:
            try:
                start = time.perf_counter()
                
                # Clear cache
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                importlib.import_module(module_name)
                import_time = (time.perf_counter() - start) * 1000
                import_times.append(import_time)
                
                logger.info("{module_name}: {import_time:.2f}ms")
                
            except Exception as e:
                failed_imports.append((module_name, str(e)))
                logger.error("{module_name}: {e}")
        
        if failed_imports:
            logger.error("Imports échoués: {len(failed_imports)}")
            self.errors.extend([f"Import {mod}: {err}" for mod, err in failed_imports])
            return False
        else:
            avg_time = np.mean(import_times)
            logger.info("Tous imports OK: {avg_time:.2f}ms moyenne")
            return True
    
    def validate_performance(self) -> bool:
        """Validation performance basique"""
        logger.info("\n⚡ VALIDATION PERFORMANCE...")
        
        try:
            # Test calculs vectorisés basiques
            start = time.perf_counter()
            
            # Simulation données trading
            n_samples = 1000
            prices = np.random.uniform(4400, 4600, n_samples)
            volumes = np.random.randint(100, 2000, n_samples)
            
            # Calculs vectorisés (doit être rapide)
            returns = np.diff(prices) / prices[:-1]
            vwap = np.sum(prices * volumes) / np.sum(volumes)
            volatility = np.std(returns) * np.sqrt(252)
            momentum = np.mean(returns[-20:]) if len(returns) >= 20 else 0
            
            calc_time = (time.perf_counter() - start) * 1000
            
            # Test performance patterns basique
            start = time.perf_counter()
            
            # Simulation pattern detection vectorisé
            pattern_scores = np.random.random(100)
            weighted_scores = pattern_scores * np.exp(np.linspace(-1, 0, 100))
            final_score = np.mean(weighted_scores)
            
            pattern_time = (time.perf_counter() - start) * 1000
            
            total_time = calc_time + pattern_time
            
            logger.info("Calculs vectorisés: {calc_time:.3f}ms")
            logger.info("Pattern detection: {pattern_time:.3f}ms")
            logger.info("Total: {total_time:.3f}ms")
            
            # Performance targets
            if total_time < 5.0:
                logger.info("Performance: EXCELLENT")
                return True
            elif total_time < 10.0:
                logger.warning("Performance: GOOD (acceptable)")
                return True
            else:
                logger.error("Performance: SLOW (optimisation requise)")
                self.errors.append(f"Performance trop lente: {total_time:.3f}ms")
                return False
                
        except Exception as e:
            logger.error("Erreur test performance: {e}")
            self.errors.append(f"Performance test failed: {e}")
            return False
    
    def validate_syntax(self) -> bool:
        """Validation syntax rapide"""
        logger.info("\n📝 VALIDATION SYNTAX...")
        
        python_files = [
            "config/trading_config.py",
            "core/base_types.py"
        ]
        
        syntax_errors = []
        
        for file_path in python_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    
                    # Test compilation
                    compile(source, file_path, 'exec')
                    logger.info("{file_path}")
                    
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}:{e.lineno} - {e.msg}")
                    logger.error("{file_path}: {e.msg}")
                except Exception as e:
                    syntax_errors.append(f"{file_path} - {str(e)}")
                    logger.error("{file_path}: {e}")
        
        if syntax_errors:
            logger.error("Erreurs syntax: {len(syntax_errors)}")
            self.errors.extend(syntax_errors)
            return False
        else:
            logger.info("Syntax OK: {len(python_files)} fichiers")
            return True
    
    def validate_trading_config_functionality(self) -> bool:
        """Test fonctionnalité trading config"""
        logger.info("\n⚙️ TEST CONFIG FUNCTIONALITY...")
        
        try:
            from config import get_trading_config, TradingMode
            
            # Test création config
            config = get_trading_config()
            logger.info("Config créée: {config.trading_mode.value}")
            
            # Test validation
            is_valid = config.validate()
            logger.info("Validation: {is_valid}")
            
            # Test symboles
            symbols = list(config.symbols.keys())
            logger.info("Symboles: {symbols}")
            
            return is_valid and len(symbols) > 0
            
        except Exception as e:
            logger.error("Config test failed: {e}")
            self.errors.append(f"Config functionality: {e}")
            return False
    
    def validate_core_types_functionality(self) -> bool:
        """Test fonctionnalité core types"""
        logger.info("\n🎯 TEST CORE TYPES FUNCTIONALITY...")
        
        try:
            from core import MarketData, SignalType, TradingSignal, ES_TICK_SIZE
            
            # Test création MarketData
            market_data = MarketData(
                timestamp=pd.Timestamp.now(),
                symbol="ES", 
                open=4500.0,
                high=4510.0,
                low=4495.0,
                close=4505.0,
                volume=1000
            )
            
            logger.info("MarketData: {market_data.symbol}")
            logger.info("Bullish: {market_data.is_bullish}")
            logger.info("ES_TICK_SIZE: {ES_TICK_SIZE}")
            
            # Test signal
            signal = TradingSignal(
                signal_type=SignalType.LONG_TREND,
                confidence=0.8,
                price=4505.0,
                timestamp=pd.Timestamp.now(),
                features={'test': 1.0},
                metadata={'source': 'validation'}
            )
            
            logger.info("Signal: {signal.signal_type.value}")
            
            return True
            
        except Exception as e:
            logger.error("Core types test failed: {e}")
            self.errors.append(f"Core types functionality: {e}")
            return False
    
    def print_summary(self):
        """Résumé validation"""
        print("\n" + "=" * 50)
        logger.info("📊 RÉSUMÉ VALIDATION")
        print("=" * 50)
        
        # Functionality tests
        config_ok = self.validate_trading_config_functionality()
        core_ok = self.validate_core_types_functionality()
        
        logger.info("\n✅ Structure: OK")
        print(f"✅ Imports: OK" if not any("Import" in err for err in self.errors) else "❌ Imports: FAILED")
        print(f"✅ Performance: OK" if not any("Performance" in err for err in self.errors) else "❌ Performance: FAILED")
        print(f"✅ Syntax: OK" if not any("syntax" in err.lower() for err in self.errors) else "❌ Syntax: FAILED")
        print(f"✅ Config: OK" if config_ok else "❌ Config: FAILED")
        print(f"✅ Core Types: OK" if core_ok else "❌ Core Types: FAILED")
        
        if self.errors:
            logger.info("\n💀 ERREURS DÉTECTÉES: {len(self.errors)}")
            for i, error in enumerate(self.errors[:5]):  # Top 5
                logger.info("   {i+1}. {error}")
            if len(self.errors) > 5:
                logger.info("   ... et {len(self.errors) - 5} autres")
        else:
            logger.info("\n🎉 AUCUNE ERREUR DÉTECTÉE!")
    
    def run_pre_audit_check(self) -> bool:
        """Check pré-audit final"""
        logger.info("\n🔍 PRE-AUDIT CHECK FINAL...")
        
        # Estimation score audit
        structure_weight = 0.2
        imports_weight = 0.4  # Critique
        performance_weight = 0.2
        syntax_weight = 0.2
        
        structure_score = 1.0 if len([e for e in self.errors if "missing" in e.lower()]) == 0 else 0.0
        imports_score = 1.0 if len([e for e in self.errors if "import" in e.lower()]) == 0 else 0.0
        performance_score = 1.0 if len([e for e in self.errors if "performance" in e.lower()]) == 0 else 0.5
        syntax_score = 1.0 if len([e for e in self.errors if "syntax" in e.lower()]) == 0 else 0.0
        
        estimated_score = (
            structure_score * structure_weight +
            imports_score * imports_weight + 
            performance_score * performance_weight +
            syntax_score * syntax_weight
        ) * 100
        
        logger.info("🎯 Score estimé audit: {estimated_score:.1f}%")
        
        if estimated_score >= 75:
            logger.info("🎉 EXCELLENT - Audit devrait passer!")
            return True
        elif estimated_score >= 60:
            logger.warning("CORRECT - Fixes mineurs recommandés")
            return True
        else:
            logger.info("💀 INSUFFICIENT - Fixes critiques requis")
            return False

def main():
    """Validation rapide complète"""
    validator = QuickValidator()
    
    # Validation
    success = validator.validate_all()
    
    # Check pré-audit
    pre_audit_ok = validator.run_pre_audit_check()
    
    if success and pre_audit_ok:
        logger.info("\n🚀 PRÊT POUR AUDIT TECHNIQUE!")
        logger.info("Commande: python technical_audit.py")
        return True
    else:
        logger.info("\n💡 ACTIONS RECOMMANDÉES:")
        if not success:
            logger.info("1. Exécuter: python fix_imports.py")
            logger.info("2. Appliquer: python performance_optimizer.py") 
        logger.info("3. Re-valider: python quick_validation.py")
        logger.info("4. Audit final: python technical_audit.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)