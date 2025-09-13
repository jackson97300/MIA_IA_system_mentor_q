"""
MIA_IA_SYSTEM - Système de Trading Automatisé
============================================

Système de trading automatisé avec intégration Sierra Chart et MenthorQ.
"""

__version__ = "4.0.0"
__author__ = "MIA_IA_SYSTEM"
__email__ = "mia@example.com"

from .core.logger import get_logger
from .core.config_manager import AutomationConfig

__all__ = [
    "get_logger",
    "AutomationConfig",
    "__version__",
    "__author__",
    "__email__",
]

