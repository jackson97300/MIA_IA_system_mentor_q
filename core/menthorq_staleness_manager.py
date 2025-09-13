#!/usr/bin/env python3
"""
🔍 MENTHORQ STALENESS MANAGER - MIA_IA_SYSTEM
==============================================

Gestionnaire centralisé de la staleness des données MenthorQ.
Utilise la configuration centralisée pour les seuils d'âge selon le régime VIX.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

# Import configuration centralisée
try:
    from config.menthorq_rules_loader import get_menthorq_rules, get_staleness_threshold
    MENTHORQ_RULES_AVAILABLE = True
except ImportError:
    MENTHORQ_RULES_AVAILABLE = False

logger = get_logger(__name__)

class VIXRegime(Enum):
    """Régimes VIX pour ajustement des seuils de staleness"""
    NORMAL = "normal"
    HIGH_VIX = "high_vix"
    EXTREME = "extreme"

@dataclass
class StalenessResult:
    """Résultat d'analyse de staleness"""
    is_stale: bool
    age_seconds: float
    max_age_seconds: int
    vix_regime: VIXRegime
    staleness_ratio: float  # age_seconds / max_age_seconds
    severity: str  # "OK", "WARNING", "CRITICAL"
    message: str

@dataclass
class DataSource:
    """Source de données avec timestamp"""
    name: str
    last_update: datetime
    symbol: str
    data_type: str  # "gamma_levels", "blind_spots", "swing_levels", "vix", "market_data"
    expected_frequency_seconds: int = 60  # Fréquence attendue par défaut

class MenthorQStalenessManager:
    """Gestionnaire centralisé de la staleness MenthorQ"""
    
    def __init__(self):
        """Initialisation du gestionnaire de staleness"""
        self.data_sources: Dict[str, DataSource] = {}
        
        # Seuils par défaut (fallback si config non disponible)
        self.default_thresholds = {
            VIXRegime.NORMAL: 30 * 60,    # 30 minutes
            VIXRegime.HIGH_VIX: 15 * 60,  # 15 minutes
            VIXRegime.EXTREME: 5 * 60     # 5 minutes
        }
        
        # Seuils de sévérité (en ratio du seuil max)
        self.severity_thresholds = {
            "WARNING": 0.8,    # 80% du seuil max
            "CRITICAL": 1.0    # 100% du seuil max
        }
        
        logger.info(f"🔍 MenthorQStalenessManager initialisé (config_available: {MENTHORQ_RULES_AVAILABLE})")
    
    def register_data_source(self, name: str, symbol: str, data_type: str, 
                           expected_frequency_seconds: int = 60) -> None:
        """
        Enregistre une source de données pour monitoring
        
        Args:
            name: Nom unique de la source (ex: "ES_gamma_levels")
            symbol: Symbole (ES, NQ, etc.)
            data_type: Type de données
            expected_frequency_seconds: Fréquence attendue en secondes
        """
        source = DataSource(
            name=name,
            last_update=datetime.now(timezone.utc),
            symbol=symbol,
            data_type=data_type,
            expected_frequency_seconds=expected_frequency_seconds
        )
        
        self.data_sources[name] = source
        logger.debug(f"📊 Source enregistrée: {name} ({symbol} - {data_type})")
    
    def update_data_source(self, name: str, timestamp: Optional[datetime] = None) -> bool:
        """
        Met à jour le timestamp d'une source de données
        
        Args:
            name: Nom de la source
            timestamp: Timestamp de mise à jour (défaut: maintenant)
            
        Returns:
            bool: True si mise à jour réussie
        """
        if name not in self.data_sources:
            logger.warning(f"⚠️ Source inconnue: {name}")
            return False
        
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        # S'assurer que le timestamp est timezone-aware
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        self.data_sources[name].last_update = timestamp
        logger.debug(f"🔄 Source mise à jour: {name} ({timestamp.isoformat()})")
        return True
    
    def check_staleness(self, name: str, vix_level: float = 20.0, 
                       current_time: Optional[datetime] = None) -> StalenessResult:
        """
        Vérifie la staleness d'une source de données
        
        Args:
            name: Nom de la source
            vix_level: Niveau VIX actuel pour déterminer le régime
            current_time: Temps actuel (défaut: maintenant)
            
        Returns:
            StalenessResult: Résultat de l'analyse
        """
        if name not in self.data_sources:
            return StalenessResult(
                is_stale=True,
                age_seconds=float('inf'),
                max_age_seconds=0,
                vix_regime=VIXRegime.NORMAL,
                staleness_ratio=float('inf'),
                severity="CRITICAL",
                message=f"Source inconnue: {name}"
            )
        
        source = self.data_sources[name]
        
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        elif current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        
        # Calculer l'âge des données
        age_seconds = (current_time - source.last_update).total_seconds()
        
        # Déterminer le régime VIX
        vix_regime = self._determine_vix_regime(vix_level)
        
        # Récupérer le seuil maximum selon le régime VIX
        max_age_seconds = self._get_staleness_threshold(vix_regime)
        
        # Calculer le ratio de staleness
        staleness_ratio = age_seconds / max_age_seconds if max_age_seconds > 0 else float('inf')
        
        # Déterminer si les données sont stale
        is_stale = age_seconds > max_age_seconds
        
        # Déterminer la sévérité
        severity = self._determine_severity(staleness_ratio)
        
        # Créer le message
        message = self._create_staleness_message(source, age_seconds, max_age_seconds, vix_regime, severity)
        
        result = StalenessResult(
            is_stale=is_stale,
            age_seconds=age_seconds,
            max_age_seconds=max_age_seconds,
            vix_regime=vix_regime,
            staleness_ratio=staleness_ratio,
            severity=severity,
            message=message
        )
        
        if is_stale:
            logger.warning(f"⚠️ Staleness détectée: {message}")
        else:
            logger.debug(f"✅ Données fraîches: {name} ({age_seconds:.1f}s / {max_age_seconds}s)")
        
        return result
    
    def check_all_sources(self, vix_level: float = 20.0) -> Dict[str, StalenessResult]:
        """
        Vérifie la staleness de toutes les sources enregistrées
        
        Args:
            vix_level: Niveau VIX actuel
            
        Returns:
            Dict des résultats par source
        """
        results = {}
        current_time = datetime.now(timezone.utc)
        
        for name in self.data_sources.keys():
            results[name] = self.check_staleness(name, vix_level, current_time)
        
        # Log résumé
        stale_count = sum(1 for r in results.values() if r.is_stale)
        total_count = len(results)
        
        if stale_count > 0:
            logger.warning(f"⚠️ {stale_count}/{total_count} sources stale (VIX: {vix_level})")
        else:
            logger.info(f"✅ Toutes les sources fraîches ({total_count} sources, VIX: {vix_level})")
        
        return results
    
    def get_staleness_summary(self, vix_level: float = 20.0) -> Dict[str, Any]:
        """
        Retourne un résumé de la staleness de toutes les sources
        
        Args:
            vix_level: Niveau VIX actuel
            
        Returns:
            Dict avec résumé de la staleness
        """
        results = self.check_all_sources(vix_level)
        
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vix_level": vix_level,
            "vix_regime": self._determine_vix_regime(vix_level).value,
            "total_sources": len(results),
            "stale_sources": sum(1 for r in results.values() if r.is_stale),
            "critical_sources": sum(1 for r in results.values() if r.severity == "CRITICAL"),
            "warning_sources": sum(1 for r in results.values() if r.severity == "WARNING"),
            "avg_age_seconds": sum(r.age_seconds for r in results.values()) / len(results) if results else 0,
            "max_age_seconds": max((r.age_seconds for r in results.values()), default=0),
            "sources_detail": {
                name: {
                    "is_stale": result.is_stale,
                    "age_seconds": result.age_seconds,
                    "max_age_seconds": result.max_age_seconds,
                    "staleness_ratio": result.staleness_ratio,
                    "severity": result.severity,
                    "message": result.message
                }
                for name, result in results.items()
            }
        }
        
        return summary
    
    def _determine_vix_regime(self, vix_level: float) -> VIXRegime:
        """Détermine le régime VIX selon le niveau"""
        if MENTHORQ_RULES_AVAILABLE:
            try:
                rules = get_menthorq_rules()
                vix_thresholds = rules.thresholds.get('vix_regime', {})
                
                high_threshold = vix_thresholds.get('high', 35.0)
                extreme_threshold = vix_thresholds.get('extreme', 50.0)
                
                if vix_level >= extreme_threshold:
                    return VIXRegime.EXTREME
                elif vix_level >= high_threshold:
                    return VIXRegime.HIGH_VIX
                else:
                    return VIXRegime.NORMAL
            except Exception as e:
                logger.warning(f"⚠️ Erreur lecture seuils VIX config: {e}")
        
        # Fallback seuils par défaut
        if vix_level >= 50.0:
            return VIXRegime.EXTREME
        elif vix_level >= 35.0:
            return VIXRegime.HIGH_VIX
        else:
            return VIXRegime.NORMAL
    
    def _get_staleness_threshold(self, vix_regime: VIXRegime) -> int:
        """Récupère le seuil de staleness selon le régime VIX"""
        if MENTHORQ_RULES_AVAILABLE:
            try:
                threshold_minutes = get_staleness_threshold(vix_regime.value)
                return threshold_minutes * 60  # Convertir en secondes
            except Exception as e:
                logger.warning(f"⚠️ Erreur lecture seuil staleness config: {e}")
        
        # Fallback seuils par défaut
        return self.default_thresholds.get(vix_regime, 30 * 60)
    
    def _determine_severity(self, staleness_ratio: float) -> str:
        """Détermine la sévérité selon le ratio de staleness"""
        if staleness_ratio >= self.severity_thresholds["CRITICAL"]:
            return "CRITICAL"
        elif staleness_ratio >= self.severity_thresholds["WARNING"]:
            return "WARNING"
        else:
            return "OK"
    
    def _create_staleness_message(self, source: DataSource, age_seconds: float, 
                                max_age_seconds: int, vix_regime: VIXRegime, 
                                severity: str) -> str:
        """Crée un message descriptif de staleness"""
        age_minutes = age_seconds / 60
        max_age_minutes = max_age_seconds / 60
        
        return (f"{source.name} ({source.symbol}): {age_minutes:.1f}min "
                f"(max: {max_age_minutes:.0f}min, VIX: {vix_regime.value}, "
                f"severity: {severity})")
    
    def get_registered_sources(self) -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des sources enregistrées"""
        return {
            name: {
                "symbol": source.symbol,
                "data_type": source.data_type,
                "expected_frequency_seconds": source.expected_frequency_seconds,
                "last_update": source.last_update.isoformat()
            }
            for name, source in self.data_sources.items()
        }
    
    def clear_sources(self) -> None:
        """Vide toutes les sources enregistrées"""
        self.data_sources.clear()
        logger.info("🔄 Toutes les sources de staleness ont été vidées")

# === INSTANCE GLOBALE ===

_global_staleness_manager: Optional[MenthorQStalenessManager] = None

def get_staleness_manager() -> MenthorQStalenessManager:
    """Retourne l'instance globale du gestionnaire de staleness"""
    global _global_staleness_manager
    if _global_staleness_manager is None:
        _global_staleness_manager = MenthorQStalenessManager()
    return _global_staleness_manager

# === FONCTIONS UTILITAIRES ===

def register_menthorq_source(symbol: str, data_type: str, 
                            expected_frequency_seconds: int = 60) -> None:
    """Enregistre une source MenthorQ pour monitoring de staleness"""
    manager = get_staleness_manager()
    name = f"{symbol}_{data_type}"
    manager.register_data_source(name, symbol, data_type, expected_frequency_seconds)

def update_menthorq_source(symbol: str, data_type: str, 
                          timestamp: Optional[datetime] = None) -> bool:
    """Met à jour le timestamp d'une source MenthorQ"""
    manager = get_staleness_manager()
    name = f"{symbol}_{data_type}"
    return manager.update_data_source(name, timestamp)

def check_menthorq_staleness(symbol: str, data_type: str, 
                           vix_level: float = 20.0) -> StalenessResult:
    """Vérifie la staleness d'une source MenthorQ spécifique"""
    manager = get_staleness_manager()
    name = f"{symbol}_{data_type}"
    return manager.check_staleness(name, vix_level)

def get_menthorq_staleness_summary(vix_level: float = 20.0) -> Dict[str, Any]:
    """Retourne un résumé de la staleness de toutes les sources MenthorQ"""
    manager = get_staleness_manager()
    return manager.get_staleness_summary(vix_level)

# === TEST ===

def test_staleness_manager():
    """Test du gestionnaire de staleness"""
    logger.info("=== TEST MENTHORQ STALENESS MANAGER ===")
    
    try:
        manager = MenthorQStalenessManager()
        
        # Test 1: Enregistrement de sources
        manager.register_data_source("ES_gamma_levels", "ES", "gamma_levels", 60)
        manager.register_data_source("ES_blind_spots", "ES", "blind_spots", 60)
        manager.register_data_source("NQ_gamma_levels", "NQ", "gamma_levels", 60)
        
        sources = manager.get_registered_sources()
        assert len(sources) == 3, f"Expected 3 sources, got {len(sources)}"
        logger.info("✅ Test 1 OK: Enregistrement de sources")
        
        # Test 2: Vérification staleness (données fraîches)
        result = manager.check_staleness("ES_gamma_levels", vix_level=20.0)
        assert not result.is_stale, "Fresh data should not be stale"
        assert result.severity == "OK", f"Expected OK, got {result.severity}"
        logger.info("✅ Test 2 OK: Données fraîches")
        
        # Test 3: Simulation données stale
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        manager.update_data_source("ES_gamma_levels", old_time)
        
        result = manager.check_staleness("ES_gamma_levels", vix_level=20.0)
        assert result.is_stale, "Old data should be stale"
        assert result.severity in ["WARNING", "CRITICAL"], f"Expected WARNING/CRITICAL, got {result.severity}"
        logger.info("✅ Test 3 OK: Données stale détectées")
        
        # Test 4: Régime VIX extrême
        result = manager.check_staleness("ES_gamma_levels", vix_level=60.0)
        assert result.vix_regime == VIXRegime.EXTREME, f"Expected EXTREME, got {result.vix_regime}"
        logger.info("✅ Test 4 OK: Régime VIX extrême")
        
        # Test 5: Résumé de staleness
        summary = manager.get_staleness_summary(vix_level=25.0)
        assert summary["total_sources"] == 3, f"Expected 3 sources, got {summary['total_sources']}"
        assert summary["stale_sources"] >= 1, f"Expected at least 1 stale source"
        logger.info("✅ Test 5 OK: Résumé de staleness")
        
        # Test 6: Fonctions utilitaires
        register_menthorq_source("ES", "vix_data", 30)
        update_result = update_menthorq_source("ES", "vix_data")
        assert update_result, "Update should succeed"
        
        staleness_result = check_menthorq_staleness("ES", "vix_data", 15.0)
        assert not staleness_result.is_stale, "Fresh VIX data should not be stale"
        logger.info("✅ Test 6 OK: Fonctions utilitaires")
        
        logger.info("🎉 Tous les tests Staleness Manager réussis!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_staleness_manager()

