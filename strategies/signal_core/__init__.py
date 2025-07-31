"""
strategies/signal_core/__init__.py

Package signal_core - Re-exports centralisés pour compatibilité parfaite
"""

# ===== IMPORTS DE TOUS LES MODULES =====

# Base types et constantes
from .base_types import *

# Classes principales
from .signal_components import *
from .signal_generator_core import *

# Modules spécialisés
from .technique_analyzers import *
from .confidence_calculator import *
from .quality_validator import *
from .stats_tracker import *

# Factory functions
from .factory_functions import *

# ===== RE-EXPORTS EXPLICITES POUR COMPATIBILITÉ =====

# Classes principales (pour import direct)
from .signal_generator_core import SignalGenerator
from .signal_components import SignalComponents, FinalSignal

# Enums (pour import direct)
from .base_types import SignalDecision, SignalSource, QualityLevel

# Factory functions (pour import direct)
from .factory_functions import create_signal_generator, generate_trading_signal

# Constantes principales (pour import direct)
from .base_types import (
    MIN_BATTLE_NAVALE_SIGNAL_LONG,
    MIN_BATTLE_NAVALE_SIGNAL_SHORT,
    MIN_CONFLUENCE_SCORE,
    MIN_MTF_ELITE_SCORE,
    MIN_MTF_STANDARD_SCORE,
    MIN_SMART_MONEY_CONFIDENCE,
    MIN_SMART_MONEY_INSTITUTIONAL_SCORE,
    SMART_MONEY_ALIGNMENT_BONUS,
    MIN_ML_ENSEMBLE_CONFIDENCE,
    ML_ENSEMBLE_BOOST_FACTOR,
    ML_ENSEMBLE_POSITION_BONUS,
    GAMMA_EXPIRY_WEEK_FACTOR,
    GAMMA_PEAK_FACTOR,
    GAMMA_MODERATE_FACTOR,
    GAMMA_NORMAL_FACTOR,
    GAMMA_POST_EXPIRY_FACTOR
)

# ===== EXPORTS COMPLETS POUR COMPATIBILITÉ TOTALE =====

__all__ = [
    # ===== CLASSES PRINCIPALES =====
    'SignalGenerator',           # Classe principale
    'SignalComponents',          # Composants d'analyse  
    'FinalSignal',              # Signal final
    'TechniqueAnalyzers',       # Analyseur techniques Elite
    'ConfidenceCalculator',     # Calculateur confidence
    'QualityValidator',         # Validateur qualité
    'StatsTracker',            # Tracker statistiques
    
    # ===== ENUMS =====
    'SignalDecision',           # Décisions possibles
    'SignalSource',             # Sources de signal
    'QualityLevel',             # Niveaux de qualité
    
    # ===== FACTORY FUNCTIONS =====
    'create_signal_generator',                    # Factory principale
    'generate_trading_signal',                    # Helper génération rapide
    'create_signal_generator_for_backtesting',    # Factory backtesting
    'create_signal_generator_for_paper_trading',  # Factory paper trading
    'create_signal_generator_for_production',     # Factory production
    
    # ===== CONSTANTES BATTLE NAVALE (PRIORITÉ #2) =====
    'MIN_BATTLE_NAVALE_SIGNAL_LONG',     # 0.25
    'MIN_BATTLE_NAVALE_SIGNAL_SHORT',    # -0.25
    
    # ===== CONSTANTES CONFLUENCE =====
    'MIN_CONFLUENCE_SCORE',              # 0.60
    'MIN_CONFLUENCE_PREMIUM',            # 0.80  
    'MIN_CONFLUENCE_STRONG',             # 0.70
    
    # ===== CONSTANTES MTF ELITE (PHASE 3) =====
    'MIN_MTF_ELITE_SCORE',               # 0.75
    'MIN_MTF_STANDARD_SCORE',            # 0.35
    
    # ===== CONSTANTES SMART MONEY (TECHNIQUE #2) =====
    'MIN_SMART_MONEY_CONFIDENCE',        # 0.6
    'MIN_SMART_MONEY_INSTITUTIONAL_SCORE', # 0.7
    'SMART_MONEY_ALIGNMENT_BONUS',       # 1.15
    
    # ===== CONSTANTES ML ENSEMBLE (TECHNIQUE #3) =====
    'MIN_ML_ENSEMBLE_CONFIDENCE',        # 0.70
    'ML_ENSEMBLE_BOOST_FACTOR',          # 1.08
    'ML_ENSEMBLE_POSITION_BONUS',        # 1.15
    
    # ===== CONSTANTES GAMMA CYCLES (TECHNIQUE #4) =====
    'GAMMA_EXPIRY_WEEK_FACTOR',          # 0.7
    'GAMMA_PEAK_FACTOR',                 # 1.3
    'GAMMA_MODERATE_FACTOR',             # 1.1
    'GAMMA_NORMAL_FACTOR',               # 1.0
    'GAMMA_POST_EXPIRY_FACTOR',          # 1.05
    
    # ===== CLASSES TECHNIQUES AVANCÉES =====
    'MLEnsembleFilter',                   # Classe ML (mock si non disponible)
    'EnsembleConfig',                     # Config ML
    'EnsemblePrediction',                 # Prédiction ML
    'GammaCyclesAnalyzer',                # Classe Gamma (mock si non disponible)
    'GammaCycleConfig',                   # Config Gamma
    'GammaCycleAnalysis',                 # Analyse Gamma
    'GammaPhase',                         # Phases Gamma
    
    # ===== FLAGS DISPONIBILITÉ =====
    'ML_ENSEMBLE_AVAILABLE',              # True si ML disponible
    'GAMMA_CYCLES_AVAILABLE',             # True si Gamma disponible
    
    # ===== HELPER FUNCTIONS =====
    'validate_market_data',               # Validation données
    'get_signal_generator_version',       # Version string
    'get_available_techniques',           # Status techniques
    'create_test_market_data',            # Données test
    'migrate_from_original_signal_generator', # Migration helper
    'get_availability_status',            # Status global
    'get_all_constants',                  # Toutes les constantes
    'create_no_trade_signal',             # Helper NO_TRADE
    'create_empty_components'             # Helper composants vides
]

# ===== MÉTADONNÉES PACKAGE =====

__version__ = "3.6.0_refactored"
__author__ = "MIA_IA_SYSTEM"
__description__ = "Signal Generator refactorisé avec toutes les techniques Elite"

# ===== VALIDATION IMPORTS =====

def _validate_imports():
    """Valide que tous les imports sont disponibles"""
    
    missing_items = []
    
    # Test imports critiques
    critical_items = [
        'SignalGenerator', 'SignalComponents', 'FinalSignal',
        'SignalDecision', 'SignalSource', 'QualityLevel',
        'create_signal_generator', 'generate_trading_signal'
    ]
    
    for item in critical_items:
        if item not in globals():
            missing_items.append(item)
    
    if missing_items:
        raise ImportError(f"Imports critiques manquants: {missing_items}")
    
    return True

# Validation automatique à l'import
try:
    _validate_imports()
except ImportError as e:
    import logging
    logging.error(f"Erreur validation signal_core package: {e}")
    raise

# ===== INFORMATIONS PACKAGE =====

def get_package_info():
    """Retourne les informations du package"""
    
    from .base_types import get_availability_status
    availability = get_availability_status()
    
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules_count': 8,  # Nombre de modules dans le package
        'exports_count': len(__all__),
        'techniques_available': {
            'battle_navale': True,
            'mtf_confluence': True,
            'smart_money': True,
            'ml_ensemble': availability.get('ml_ensemble', False),
            'gamma_cycles': availability.get('gamma_cycles', False)
        },
        'refactored': True,
        'original_file_size': 2788,  # Lignes du fichier original
        'modular_files_count': 8,
        'compatibility': 'Perfect - All original imports work'
    }

def print_package_status():
    """Affiche le statut du package"""
    
    info = get_package_info()
    
    print(f"""
🎯 SIGNAL_CORE PACKAGE STATUS
=============================
Version: {info['version']}
Author: {info['author']}
Description: {info['description']}

📊 STRUCTURE:
- Modules: {info['modules_count']}
- Exports: {info['exports_count']}
- Original file: {info['original_file_size']} lignes
- Refactored: {info['modular_files_count']} fichiers modulaires

🚀 TECHNIQUES DISPONIBLES:
- Battle Navale: {'✅' if info['techniques_available']['battle_navale'] else '❌'}
- MTF Confluence: {'✅' if info['techniques_available']['mtf_confluence'] else '❌'}
- Smart Money: {'✅' if info['techniques_available']['smart_money'] else '❌'}
- ML Ensemble: {'✅' if info['techniques_available']['ml_ensemble'] else '❌'}
- Gamma Cycles: {'✅' if info['techniques_available']['gamma_cycles'] else '❌'}

✅ COMPATIBILITÉ: {info['compatibility']}
    """)

# ===== TESTS RAPIDES =====

def quick_test():
    """Test rapide du package refactorisé"""
    
    print("🧪 Test rapide signal_core...")
    
    try:
        # Test création générateur
        generator = create_signal_generator()
        print("✅ SignalGenerator créé")
        
        # Test données factices
        from .factory_functions import create_test_market_data
        test_data = create_test_market_data()
        print("✅ Données test créées")
        
        # Test génération signal
        signal = generator.generate_signal(test_data)
        print(f"✅ Signal généré: {signal.decision.value}")
        
        # Test techniques
        techniques_status = generator.technique_analyzers.get_techniques_status()
        print(f"✅ Techniques: {sum(techniques_status.values())}/4 actives")
        
        # Test stats
        stats = generator.get_performance_stats()
        print(f"✅ Stats: {stats['signals_generated']} signaux générés")
        
        print("🎉 Test rapide réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Test rapide échoué: {e}")
        return False

# Export de la fonction de test
__all__.append('quick_test')
__all__.append('print_package_status')