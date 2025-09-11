# -*- coding: utf-8 -*-
"""
Compat shim pour l'ancien chemin: features.confluence_calculator
Il redirige vers la nouvelle implémentation.

Ce module était un "pont" de l'ancienne architecture vers la nouvelle.
Toute la logique de confluence est maintenant dans confluence_analyzer 
et feature_calculator_optimized.
"""

try:
    # Nouvelle implémentation canonique
    from .confluence_analyzer import ConfluenceAnalyzer as _CA, ConfluenceZone
except ImportError:
    try:
        # Fallback vers feature_calculator_optimized si confluence_analyzer n'existe pas
        from .feature_calculator_optimized import ConfluenceAnalyzer as _CA, ConfluenceZone  # type: ignore
    except ImportError:
        # Dernier fallback - créer des stubs temporaires
        from typing import Any
        
        class _CA:
            """Stub temporaire pour ConfluenceAnalyzer"""
            def __init__(self, *args, **kwargs):
                pass
        
        class ConfluenceZone:
            """Stub temporaire pour ConfluenceZone"""
            def __init__(self, *args, **kwargs):
                pass

# Compat: certains anciens codes importaient ConfluenceCalculator
class ConfluenceCalculator(_CA):
    """Alias 100% compatible de ConfluenceAnalyzer (hérite sans rien changer)."""
    pass

# API exposée (anciens et nouveaux noms)
ConfluenceAnalyzer = _CA

# Compat: certains codes importent EnhancedConfluenceCalculator
class EnhancedConfluenceCalculator(_CA):
    """Alias pour EnhancedConfluenceCalculator (hérite de ConfluenceAnalyzer)."""
    pass

# Export principal
__all__ = ["ConfluenceAnalyzer", "ConfluenceCalculator", "ConfluenceZone", "EnhancedConfluenceCalculator"]
