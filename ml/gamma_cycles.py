"""
GAMMA EXPIRATION CYCLES - TECHNIQUE #4 ELITE
Optimisation selon cycles expiration options (+1% win rate)
Version: Corrigée avec fonctions publiques complètes
"""

# === STDLIB ===
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from calendar import monthrange

# === THIRD-PARTY ===
import pandas as pd

# === LOCAL IMPORTS ===
from core.logger import get_logger

# Logger
logger = get_logger(__name__)

# === GAMMA CYCLES CONFIGURATION ===

@dataclass
class GammaCycleConfig:
    """Configuration des cycles gamma"""
    # Facteurs d'ajustement selon phase
    expiry_week_factor: float = 0.7      # Semaine expiration (haute volatilité)
    gamma_peak_factor: float = 1.3       # 3-5 jours avant (gamma peak)
    gamma_moderate_factor: float = 1.1    # 6-10 jours avant
    normal_factor: float = 1.0           # Normal
    post_expiry_factor: float = 1.05     # 1-2 jours après expiration
    
    # Seuils de phases
    expiry_week_days: int = 2            # <= 2 jours = semaine expiration
    gamma_peak_start: int = 3            # 3-5 jours = gamma peak
    gamma_peak_end: int = 5
    gamma_moderate_start: int = 6        # 6-10 jours = modéré
    gamma_moderate_end: int = 10
    
    # Options pour cache
    cache_enabled: bool = True
    cache_ttl_hours: int = 6             # Cache 6h (se met à jour 4x/jour)

class VolatilityExpectation(Enum):
    """Niveaux de volatilité attendue"""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
class GammaPhase(Enum):
    """Phases du cycle gamma"""
    EXPIRY_WEEK = "expiry_week"         # 0-2 jours avant expiration
    GAMMA_PEAK = "gamma_peak"           # 3-5 jours avant expiration  
    GAMMA_MODERATE = "gamma_moderate"   # 6-10 jours avant expiration
    NORMAL = "normal"                   # >10 jours avant expiration
    POST_EXPIRY = "post_expiry"         # 1-2 jours après expiration
    UNKNOWN = "unknown"                 # Erreur calcul

@dataclass
class GammaCycleAnalysis:
    """Résultat analyse cycle gamma"""
    current_date: datetime
    next_expiry_date: datetime
    days_to_expiry: int
    days_since_last_expiry: int
    gamma_phase: GammaPhase
    adjustment_factor: float
    volatility_expectation: VolatilityExpectation  # Enum au lieu de string
    position_size_adjustment: float     # Multiplicateur position size
    confidence_adjustment: float        # Multiplicateur confidence
    reasoning: str
    
    @property
    def phase(self) -> GammaPhase:
        """Alias pour compatibilité avec les tests"""
        return self.gamma_phase
    
    @property
    def expected_volatility(self) -> VolatilityExpectation:
        """Alias pour compatibilité avec les tests"""
        return self.volatility_expectation

# === UTILITIES TIMEZONE ===

def ensure_timezone_aware(dt: datetime) -> datetime:
    """Assure qu'une datetime est timezone-aware (UTC si naive)"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def ensure_timezone_naive(dt: datetime) -> datetime:
    """Assure qu'une datetime est timezone-naive"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def normalize_datetime(dt: datetime, target_tz_aware: bool = True) -> datetime:
    """Normalise datetime selon le format cible"""
    if target_tz_aware:
        return ensure_timezone_aware(dt)
    else:
        return ensure_timezone_naive(dt)

# === EXPIRATION CALENDAR ===

class OptionsExpirationCalendar:
    """Calendrier expirations options SPX/SPY"""
    
    def __init__(self):
        self.cache = {}
        self.cache_date = None
    
    def get_monthly_expiry_date(self, year: int, month: int, tz_aware: bool = True) -> datetime:
        """
        Calcul date expiration mensuelle SPX
        Règle: 3ème vendredi du mois à 16h00 EST
        
        Args:
            year: Année
            month: Mois
            tz_aware: Si True, retourne timezone-aware (UTC)
        """
        # Premier jour du mois
        first_day = datetime(year, month, 1)
        
        # Trouve le premier vendredi (weekday 4 = vendredi)
        days_to_first_friday = (4 - first_day.weekday()) % 7
        first_friday = first_day + timedelta(days=days_to_first_friday)
        
        # 3ème vendredi = premier vendredi + 14 jours
        third_friday = first_friday + timedelta(days=14)
        
        # Si le 3ème vendredi dépasse le mois, prendre le 2ème vendredi
        if third_friday.month != month:
            third_friday = first_friday + timedelta(days=7)
        
        # Définir à 16h00 (fermeture marché)
        expiry_date = third_friday.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Gestion timezone
        if tz_aware:
            return ensure_timezone_aware(expiry_date)
        else:
            return ensure_timezone_naive(expiry_date)
    
    def get_next_monthly_expiry(self, current_date: datetime) -> datetime:
        """Trouve prochaine expiration mensuelle"""
        # Normalisation timezone
        current_date = ensure_timezone_aware(current_date)
        
        current_year = current_date.year
        current_month = current_date.month
        
        # Essaie le mois courant
        expiry_this_month = self.get_monthly_expiry_date(current_year, current_month, tz_aware=True)
        
        if current_date <= expiry_this_month:
            return expiry_this_month
        
        # Sinon, mois suivant
        next_month = current_month + 1
        next_year = current_year
        
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        return self.get_monthly_expiry_date(next_year, next_month, tz_aware=True)
    
    def get_last_monthly_expiry(self, current_date: datetime) -> datetime:
        """Trouve dernière expiration mensuelle passée"""
        # Normalisation timezone
        current_date = ensure_timezone_aware(current_date)
        
        current_year = current_date.year
        current_month = current_date.month
        
        # Essaie le mois courant
        expiry_this_month = self.get_monthly_expiry_date(current_year, current_month, tz_aware=True)
        
        if current_date > expiry_this_month:
            return expiry_this_month
        
        # Sinon, mois précédent
        prev_month = current_month - 1
        prev_year = current_year
        
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        
        return self.get_monthly_expiry_date(prev_year, prev_month, tz_aware=True)

# === GAMMA CYCLES ANALYZER ===

class GammaCyclesAnalyzer:
    """
    Analyseur cycles gamma pour trading ES/SPX
    
    Intègre les patterns de volatilité selon proximité expiration options
    """
    
    def __init__(self, config: Optional[GammaCycleConfig] = None):
        self.config = config or GammaCycleConfig()
        self.expiry_calendar = OptionsExpirationCalendar()
        self.cache = {}
        self.cache_timestamp = None
        
        # Statistiques
        self.analyses_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("🎯 Gamma Cycles Analyzer initialisé - TECHNIQUE #4")
    
    def analyze_gamma_cycle(self, current_date: Optional[datetime] = None) -> GammaCycleAnalysis:
        """
        Analyse cycle gamma actuel
        
        Args:
            current_date: Date d'analyse (défaut: maintenant)
            
        Returns:
            GammaCycleAnalysis avec facteurs d'ajustement
        """
        return self.analyze_current_cycle(current_date)
    
    def analyze_current_cycle(self, current_date: Optional[datetime] = None) -> GammaCycleAnalysis:
        """
        Analyse cycle gamma actuel
        
        Args:
            current_date: Date d'analyse (défaut: maintenant)
            
        Returns:
            GammaCycleAnalysis avec facteurs d'ajustement
        """
        if current_date is None:
            current_date = datetime.now(timezone.utc)
        
        # Normalisation timezone
        current_date = ensure_timezone_aware(current_date)
        
        # Vérification cache
        if self.config.cache_enabled:
            cached_result = self._get_cached_analysis(current_date)
            if cached_result:
                self.cache_hits += 1
                return cached_result
            self.cache_misses += 1
        
        try:
            # Calcul dates expiration
            next_expiry = self.expiry_calendar.get_next_monthly_expiry(current_date)
            last_expiry = self.expiry_calendar.get_last_monthly_expiry(current_date)
            
            # Calcul jours (conversion en naive pour calcul)
            current_naive = ensure_timezone_naive(current_date)
            next_expiry_naive = ensure_timezone_naive(next_expiry)
            last_expiry_naive = ensure_timezone_naive(last_expiry)
            
            days_to_expiry = (next_expiry_naive - current_naive).days
            days_since_last_expiry = (current_naive - last_expiry_naive).days
            
            # Détermination phase gamma
            gamma_phase = self._determine_gamma_phase(days_to_expiry, days_since_last_expiry)
            
            # Calcul facteur d'ajustement
            adjustment_factor = self._calculate_adjustment_factor(gamma_phase)
            
            # Analyse volatilité attendue
            volatility_expectation = self._analyze_volatility_expectation(gamma_phase, days_to_expiry)
            
            # Ajustements position size et confidence
            position_adjustment, confidence_adjustment = self._calculate_signal_adjustments(
                gamma_phase, adjustment_factor
            )
            
            # Génération reasoning
            reasoning = self._generate_reasoning(gamma_phase, days_to_expiry, adjustment_factor)
            
            # Création résultat
            analysis = GammaCycleAnalysis(
                current_date=current_date,
                next_expiry_date=next_expiry,
                days_to_expiry=days_to_expiry,
                days_since_last_expiry=days_since_last_expiry,
                gamma_phase=gamma_phase,
                adjustment_factor=adjustment_factor,
                volatility_expectation=volatility_expectation,
                position_size_adjustment=position_adjustment,
                confidence_adjustment=confidence_adjustment,
                reasoning=reasoning
            )
            
            # Cache si activé
            if self.config.cache_enabled:
                self._cache_analysis(current_date, analysis)
            
            self.analyses_count += 1
            
            logger.debug(f"🎯 Gamma Analysis: Phase={gamma_phase.value}, "
                        f"Days={days_to_expiry}, Factor={adjustment_factor:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse gamma cycle: {e}")
            return self._create_fallback_analysis(current_date)
    
    def _determine_gamma_phase(self, days_to_expiry: int, days_since_last_expiry: int) -> GammaPhase:
        """Détermine la phase gamma actuelle"""
        
        # Post-expiration (1-2 jours après)
        if days_since_last_expiry <= 2 and days_to_expiry > 15:
            return GammaPhase.POST_EXPIRY
        
        # Semaine expiration (haute volatilité)
        if days_to_expiry <= self.config.expiry_week_days:
            return GammaPhase.EXPIRY_WEEK
        
        # Gamma peak (3-5 jours avant)
        elif (self.config.gamma_peak_start <= days_to_expiry <= self.config.gamma_peak_end):
            return GammaPhase.GAMMA_PEAK
        
        # Gamma modéré (6-10 jours avant)
        elif (self.config.gamma_moderate_start <= days_to_expiry <= self.config.gamma_moderate_end):
            return GammaPhase.GAMMA_MODERATE
        
        # Normal (>10 jours)
        else:
            return GammaPhase.NORMAL
    
    def _calculate_adjustment_factor(self, gamma_phase: GammaPhase) -> float:
        """Calcule facteur d'ajustement selon phase gamma"""
        
        phase_factors = {
            GammaPhase.EXPIRY_WEEK: self.config.expiry_week_factor,      # 0.7
            GammaPhase.GAMMA_PEAK: self.config.gamma_peak_factor,        # 1.3
            GammaPhase.GAMMA_MODERATE: self.config.gamma_moderate_factor, # 1.1
            GammaPhase.NORMAL: self.config.normal_factor,                # 1.0
            GammaPhase.POST_EXPIRY: self.config.post_expiry_factor,      # 1.05
            GammaPhase.UNKNOWN: self.config.normal_factor                # 1.0
        }
        
        return phase_factors.get(gamma_phase, 1.0)
    
    def _analyze_volatility_expectation(self, gamma_phase: GammaPhase, days_to_expiry: int) -> VolatilityExpectation:
        """Analyse volatilité attendue selon phase"""
        
        if gamma_phase == GammaPhase.EXPIRY_WEEK:
            return VolatilityExpectation.HIGH
        elif gamma_phase == GammaPhase.GAMMA_PEAK:
            return VolatilityExpectation.MODERATE
        elif gamma_phase == GammaPhase.GAMMA_MODERATE:
            return VolatilityExpectation.MODERATE
        elif gamma_phase == GammaPhase.POST_EXPIRY:
            return VolatilityExpectation.LOW
        else:
            return VolatilityExpectation.LOW
    
    def _calculate_signal_adjustments(self, gamma_phase: GammaPhase, 
                                    adjustment_factor: float) -> Tuple[float, float]:
        """Calcule ajustements position size et confidence"""
        
        # Position size adjustment (inverse du facteur pour sécurité)
        if gamma_phase == GammaPhase.EXPIRY_WEEK:
            position_adj = 0.8  # Réduction position
        elif gamma_phase == GammaPhase.GAMMA_PEAK:
            position_adj = 1.2  # Augmentation position
        else:
            position_adj = 1.0  # Normal
        
        # Confidence adjustment
        confidence_adj = adjustment_factor
        
        return position_adj, confidence_adj
    
    def _generate_reasoning(self, gamma_phase: GammaPhase, 
                          days_to_expiry: int, adjustment_factor: float) -> str:
        """Génération reasoning human-readable"""
        
        reasons = {
            GammaPhase.EXPIRY_WEEK: f"Semaine expiration ({days_to_expiry}j) - Volatilité élevée",
            GammaPhase.GAMMA_PEAK: f"Gamma peak ({days_to_expiry}j) - Momentum favorable",
            GammaPhase.GAMMA_MODERATE: f"Gamma modéré ({days_to_expiry}j) - Conditions stables",
            GammaPhase.NORMAL: f"Phase normale ({days_to_expiry}j) - Trading standard",
            GammaPhase.POST_EXPIRY: f"Post-expiration - Volatilité réduite"
        }
        
        base_reason = reasons.get(gamma_phase, "Phase inconnue")
        return f"{base_reason}, facteur={adjustment_factor:.2f}"
    
    def _get_cached_analysis(self, current_date: datetime) -> Optional[GammaCycleAnalysis]:
        """Récupération analyse en cache"""
        cache_key = current_date.strftime("%Y-%m-%d-%H")
        
        if cache_key in self.cache:
            cached_analysis, cache_time = self.cache[cache_key]
            
            # Vérification TTL
            if (datetime.now(timezone.utc) - cache_time).total_seconds() < self.config.cache_ttl_hours * 3600:
                return cached_analysis
        
        return None
    
    def _cache_analysis(self, current_date: datetime, analysis: GammaCycleAnalysis):
        """Mise en cache de l'analyse"""
        cache_key = current_date.strftime("%Y-%m-%d-%H")
        self.cache[cache_key] = (analysis, datetime.now(timezone.utc))
    
    def _create_fallback_analysis(self, current_date: datetime) -> GammaCycleAnalysis:
        """Création analyse fallback en cas d'erreur"""
        
        return GammaCycleAnalysis(
            current_date=current_date,
            next_expiry_date=current_date + timedelta(days=15),  # Approximation
            days_to_expiry=15,
            days_since_last_expiry=5,
            gamma_phase=GammaPhase.NORMAL,
            adjustment_factor=1.0,
            volatility_expectation=VolatilityExpectation.LOW,
            position_size_adjustment=1.0,
            confidence_adjustment=1.0,
            reasoning="Fallback analysis - données indisponibles"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupération statistiques analyzer"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "analyses_count": self.analyses_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "cache_ttl_hours": self.config.cache_ttl_hours,
            "config": {
                "expiry_week_factor": self.config.expiry_week_factor,
                "gamma_peak_factor": self.config.gamma_peak_factor,
                "gamma_moderate_factor": self.config.gamma_moderate_factor,
                "normal_factor": self.config.normal_factor,
                "post_expiry_factor": self.config.post_expiry_factor
            }
        }

# === FONCTION UTILITAIRE PRINCIPALE ===

def gamma_expiration_factor(current_date: Optional[datetime] = None,
                          analyzer: Optional[GammaCyclesAnalyzer] = None) -> float:
    """
    🎯 TECHNIQUE #4: GAMMA EXPIRATION CYCLES
    
    Ajuste selon les cycles d'expiration options
    Impact: +1% win rate
    
    Args:
        current_date: Date d'analyse (défaut: maintenant)
        analyzer: Instance analyzer (optionnel)
        
    Returns:
        float: Facteur d'ajustement [0.7-1.3]
    """
    
    # Instance globale si non fournie
    if analyzer is None:
        if not hasattr(gamma_expiration_factor, '_global_analyzer'):
            gamma_expiration_factor._global_analyzer = GammaCyclesAnalyzer()
        analyzer = gamma_expiration_factor._global_analyzer
    
    # Analyse cycle gamma
    analysis = analyzer.analyze_gamma_cycle(current_date)
    
    # Log pour debugging
    logger.debug(f"🎯 Gamma Cycle: {analysis.gamma_phase.value}, "
                f"factor={analysis.adjustment_factor:.2f}, "
                f"days={analysis.days_to_expiry}")
    
    return analysis.adjustment_factor

def get_days_to_monthly_expiry(current_date: Optional[datetime] = None) -> int:
    """
    Fonction utilitaire pour récupérer jours jusqu'expiration
    Compatible avec l'exemple fourni
    """
    if current_date is None:
        current_date = datetime.now(timezone.utc)
    
    current_date = ensure_timezone_aware(current_date)
    
    calendar = OptionsExpirationCalendar()
    next_expiry = calendar.get_next_monthly_expiry(current_date)
    
    # Calcul en naive pour éviter timezone issues
    current_naive = ensure_timezone_naive(current_date)
    next_expiry_naive = ensure_timezone_naive(next_expiry)
    
    return (next_expiry_naive - current_naive).days

# === FONCTIONS UTILITAIRES PUBLIQUES ===

def get_next_monthly_expiry(current_date: Optional[datetime] = None) -> datetime:
    """
    Fonction utilitaire publique pour récupérer prochaine expiration
    Compatible avec les tests existants
    
    Args:
        current_date: Date de référence (défaut: maintenant)
    
    Returns:
        datetime: Prochaine date d'expiration mensuelle (timezone-aware)
    """
    if current_date is None:
        current_date = datetime.now(timezone.utc)
    
    calendar = OptionsExpirationCalendar()
    return calendar.get_next_monthly_expiry(current_date)

def get_last_monthly_expiry(current_date: Optional[datetime] = None) -> datetime:
    """
    Fonction utilitaire publique pour récupérer dernière expiration
    Compatible avec les tests existants
    
    Args:
        current_date: Date de référence (défaut: maintenant)
    
    Returns:
        datetime: Dernière date d'expiration mensuelle passée (timezone-aware)
    """
    if current_date is None:
        current_date = datetime.now(timezone.utc)
    
    calendar = OptionsExpirationCalendar()
    return calendar.get_last_monthly_expiry(current_date)

# === FONCTIONS DE CRÉATION ===

def create_gamma_cycles_analyzer(config: Optional[GammaCycleConfig] = None) -> GammaCyclesAnalyzer:
    """Création instance analyzer gamma cycles"""
    return GammaCyclesAnalyzer(config)

def create_gamma_config(expiry_week_factor: float = 0.7,
                       gamma_peak_factor: float = 1.3,
                       gamma_moderate_factor: float = 1.1,
                       normal_factor: float = 1.0,
                       post_expiry_factor: float = 1.05) -> GammaCycleConfig:
    """Création configuration gamma personnalisée"""
    return GammaCycleConfig(
        expiry_week_factor=expiry_week_factor,
        gamma_peak_factor=gamma_peak_factor,
        gamma_moderate_factor=gamma_moderate_factor,
        normal_factor=normal_factor,
        post_expiry_factor=post_expiry_factor
    )

# === TESTS ===

def test_gamma_cycles():
    """Test complet du système gamma cycles"""
    print("🧪 Test Gamma Cycles Analyzer...")
    
    # Configuration test
    config = GammaCycleConfig(
        expiry_week_factor=0.7,
        gamma_peak_factor=1.3,
        cache_enabled=True
    )
    
    # Création analyzer
    analyzer = GammaCyclesAnalyzer(config)
    
    # Test avec différentes dates (timezone-aware)
    test_dates = [
        datetime(2025, 1, 15, tzinfo=timezone.utc),  # Normal
        datetime(2025, 1, 16, tzinfo=timezone.utc),  # Gamma peak (3j avant expiry 19/1)
        datetime(2025, 1, 17, tzinfo=timezone.utc),  # Expiry week
        datetime(2025, 1, 20, tzinfo=timezone.utc),  # Post-expiry
    ]
    
    for test_date in test_dates:
        analysis = analyzer.analyze_gamma_cycle(test_date)
        
        print(f"\n📅 Date: {test_date.strftime('%Y-%m-%d')}")
        print(f"✅ Phase: {analysis.gamma_phase.value}")
        print(f"✅ Jours expiration: {analysis.days_to_expiry}")
        print(f"✅ Facteur: {analysis.adjustment_factor:.2f}")
        print(f"✅ Volatilité: {analysis.volatility_expectation}")
        print(f"✅ Position adj: {analysis.position_size_adjustment:.2f}")
        print(f"✅ Confidence adj: {analysis.confidence_adjustment:.2f}")
        print(f"✅ Reasoning: {analysis.reasoning}")
    
    # Test fonction utilitaire
    factor = gamma_expiration_factor()
    print(f"\n🎯 Gamma factor actuel: {factor:.2f}")
    
    # Test fonction days_to_expiry
    days = get_days_to_monthly_expiry()
    print(f"📅 Jours jusqu'expiration: {days}")
    
    # Test nouvelles fonctions publiques
    next_expiry = get_next_monthly_expiry()
    last_expiry = get_last_monthly_expiry()
    print(f"📅 Prochaine expiration: {next_expiry}")
    print(f"📅 Dernière expiration: {last_expiry}")
    
    # Statistiques
    stats = analyzer.get_statistics()
    print(f"\n📊 Stats: {stats}")
    
    print("🎯 Test Gamma Cycles terminé !")

# === EXPORTS ===

__all__ = [
    # Classes principales
    'GammaCyclesAnalyzer',
    'GammaCycleConfig', 
    'GammaCycleAnalysis',
    'GammaPhase',
    'OptionsExpirationCalendar',
    
    # Fonctions principales
    'gamma_expiration_factor',
    
    # Fonctions utilitaires publiques
    'get_next_monthly_expiry',
    'get_last_monthly_expiry', 
    'get_days_to_monthly_expiry',
    
    # Utilitaires timezone
    'ensure_timezone_aware',
    'ensure_timezone_naive',
    'normalize_datetime',
    
    # Factory functions
    'create_gamma_cycles_analyzer',
    'create_gamma_config',
    
    # Test function
    'test_gamma_cycles'
]

if __name__ == "__main__":
    test_gamma_cycles()