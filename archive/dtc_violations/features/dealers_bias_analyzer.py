# -*- coding: utf-8 -*-
"""
dealers_bias_analyzer.py

Module d'analyse et d'intégration du Dealer's Bias dans MIA_IA
- Lecture des snapshots options
- Calcul du Dealer's Bias en temps réel
- Intégration dans le système de confluence
- Interface avec Sierra Chart DTC
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

# Logger simple intégré
logger = logging.getLogger("dealers_bias_analyzer")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@dataclass
class DealersBiasData:
    """Données structurées du Dealer's Bias"""
    timestamp: datetime
    symbol: str
    underlying_price: float

    # Métriques principales
    dealers_bias_score: float  # -1 à +1
    gamma_flip_strike: Optional[float]
    gamma_pins: List[Dict[str, Any]]

    # Composantes
    pcr_oi: float
    pcr_volume: float
    iv_skew: float
    vix_value: float
    gex_signed: float

    # Interprétation
    direction: str  # BULLISH/BEARISH/NEUTRAL
    strength: str   # STRONG/MODERATE/WEAK

    # Qualité des données
    data_age_seconds: int
    quality_score: float

class DealersBiasAnalyzer:
    """Analyseur du Dealer's Bias pour MIA_IA"""

    def __init__(self, snapshot_dir: str = "data/options_snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Cache pour éviter re-calculs
        self._cache = {}
        self._cache_ttl = 60  # 60 secondes

        # Seuils de qualité
        self.max_data_age = 300  # 5 minutes
        self.min_quality_score = 0.6

        logger.info(f"🎯 DealersBiasAnalyzer initialisé: {self.snapshot_dir}")

    def _extract_snapshot_fields(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Extraction robuste des champs du snapshot enrichi"""
        a = data.get("analysis", {}) or {}
        g = a.get("gex") or {}
        gnorm = g.get("normalized") or {}
        
        # VIX/VXN
        vol_index = a.get("vix")
        if vol_index is None:
            vol_index = a.get("vxn")

        return {
            "underlying_price": a.get("underlying_price") or data.get("underlying_price"),
            "pcr_oi": a.get("put_call_ratio_oi"),
            "pcr_volume": a.get("put_call_ratio_volume"),
            "iv_skew": a.get("iv_skew_puts_minus_calls"),
            "iv_avg": a.get("implied_volatility_avg"),
            "vol_index": vol_index,
            "gex_signed": (g or {}).get("gex_total_signed"),
            "gex_signed_norm": gnorm.get("gex_total_signed_normalized") or gnorm.get("gex_total_signed_per_million"),
            "gamma_flip_strike": (a.get("gamma_flip") or {}).get("gamma_flip_strike"),
            "gamma_pins": a.get("gamma_pins") or [],
            "max_pain": a.get("max_pain"),
        }

    def _json_timestamp(self, path: Path) -> float:
        """Extrait le timestamp JSON ou utilise mtime comme fallback"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            t = payload.get("timestamp") or payload.get("analysis", {}).get("timestamp")
            if t:
                # supporte "...Z" et ISO sans TZ
                ts = datetime.fromisoformat(t.replace("Z", "+00:00"))
                return ts.timestamp()
        except Exception:
            pass
        # fallback: mtime fichier
        return path.stat().st_mtime

    def find_latest_snapshot(self, symbol: str) -> Optional[Path]:
        """Trouve le snapshot le plus récent pour un symbole - VERSION ROBUSTE"""
        try:
            import os
            
            base = self.snapshot_dir
            # Autoriser override par variable d'env
            env_dir = os.getenv("OPTIONS_SNAPSHOTS_DIR")
            if env_dir:
                base = Path(env_dir)

            sym = symbol.lower()
            patterns = [
                f"{sym}_snapshot_*.json",
                f"{sym}_snapshot_test_*.json",    # <- accepte les fichiers de test
                f"{sym}_*snapshot*.json",         # <- filet de sécurité
            ]

            candidates = []
            for pat in patterns:
                candidates.extend(base.glob(pat))
                # chercher aussi dans subdirs connus
                for sub in ("hourly", "final"):
                    d = base / sub
                    if d.is_dir():
                        candidates.extend(d.glob(pat))

            if not candidates:
                logger.warning(f"⚠️ Aucun snapshot candidat pour {symbol} dans {base}")
                return None

            # Choix du plus récent par timestamp JSON (fallback mtime)
            chosen = max(candidates, key=self._json_timestamp)
            logger.info(f"🗂️ Snapshots {symbol}: {len(candidates)} candidats, sélection: {chosen.name}")
            return chosen
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche snapshot {symbol}: {e}")
            return None

    def load_snapshot_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Charge les données du snapshot le plus récent"""
        try:
            snapshot_path = self.find_latest_snapshot(symbol)
            if not snapshot_path:
                return None
            
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"📊 Données chargées: {snapshot_path}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement snapshot {symbol}: {e}")
            return None

    def calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """Calcule un score de qualité des données (0-1) - CORRIGÉ"""
        try:
            score = 0.0
            
            # Vérifier la fraîcheur des données
            timestamp_str = data.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age_seconds = (datetime.now() - timestamp).total_seconds()
                    
                    if age_seconds <= 300:  # 5 minutes
                        score += 0.4
                    elif age_seconds <= 900:  # 15 minutes
                        score += 0.2
                    elif age_seconds <= 1200:  # 20 minutes (adouci pour tests)
                        score += 0.1
                    else:
                        score += 0.05
                        
                except Exception:
                    score += 0.1
            
            # Vérifier la présence des métriques clés - CORRIGÉ
            analysis = data.get("analysis", {})
            required_metrics = [
                # blocs présents dans le snapshot v1
                "dealers_bias", "gamma_flip", "gamma_pins", "gex", "max_pain",
                # nouvelles clés réelles
                "put_call_ratio_oi", "put_call_ratio_volume",
                "implied_volatility_avg", "iv_skew_puts_minus_calls",
                # et underlying price (dans analysis)
                "underlying_price"
            ]
            
            for metric in required_metrics:
                if metric in analysis:
                    score += 0.08  # Réduit pour tenir compte du plus grand nombre de métriques
            
            # Vérifier les options
            options = data.get("options", [])
            if len(options) >= 10:  # Au moins 10 options
                score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul qualité: {e}")
            return 0.0

    def parse_dealers_bias_data(self, data: Dict[str, Any], symbol: str) -> Optional[DealersBiasData]:
        """Parse les données brutes en DealersBiasData - CORRIGÉ"""
        try:
            fields = self._extract_snapshot_fields(data, symbol)
            analysis = data.get("analysis", {}) or {}
            dealers_bias = analysis.get("dealers_bias", {}) or {}

            # Calculer l'âge des données
            timestamp_str = data.get("timestamp", "")
            timestamp = datetime.now()
            data_age_seconds = 0
            
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    data_age_seconds = int((datetime.now() - timestamp).total_seconds())
                except Exception:
                    pass
            
            # Qualité des données
            quality_score = self.calculate_data_quality(data)
            
            # Direction et force - CORRIGÉ
            bias_score = float(dealers_bias.get("dealers_bias_score") or dealers_bias.get("score") or 0.0)
            direction = dealers_bias.get("interpretation", {}).get("direction")
            strength = dealers_bias.get("interpretation", {}).get("strength")
            
            if not direction:
                # fallback simple si l'interprétation n'est pas fournie dans le snapshot
                if bias_score > 0.3:
                    direction, strength = "BULLISH", ("STRONG" if bias_score > 0.6 else "MODERATE")
                elif bias_score < -0.3:
                    direction, strength = "BEARISH", ("STRONG" if bias_score < -0.6 else "MODERATE")
                else:
                    direction, strength = "NEUTRAL", "WEAK"
            
            return DealersBiasData(
                timestamp=timestamp,
                symbol=symbol,
                underlying_price=float(fields["underlying_price"] or 0.0),
                dealers_bias_score=float(bias_score),
                gamma_flip_strike=fields["gamma_flip_strike"],
                gamma_pins=fields["gamma_pins"],
                pcr_oi=float(fields["pcr_oi"] or 0.0),
                pcr_volume=float(fields["pcr_volume"] or 0.0),
                iv_skew=float(fields["iv_skew"] or 0.0),
                vix_value=float(fields["vol_index"] or 0.0),
                gex_signed=float(fields["gex_signed"] or 0.0),
                direction=direction,
                strength=strength,
                data_age_seconds=data_age_seconds,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing DealersBiasData: {e}")
            return None

    def get_dealers_bias(self, symbol: str, use_cache: bool = True) -> Optional[DealersBiasData]:
        """Récupère les données Dealer's Bias pour un symbole"""
        try:
            # Vérifier le cache
            cache_key = f"{symbol}_bias"
            if use_cache and cache_key in self._cache:
                cached_data, cached_time = self._cache[cache_key]
                if (datetime.now() - cached_time).total_seconds() < self._cache_ttl:
                    logger.debug(f"📋 Utilisation cache pour {symbol}")
                    return cached_data
            
            # Charger les données
            raw_data = self.load_snapshot_data(symbol)
            if not raw_data:
                logger.warning(f"⚠️ Pas de données pour {symbol}")
                return None
            
            # Parser les données
            bias_data = self.parse_dealers_bias_data(raw_data, symbol)
            if not bias_data:
                return None
            
            # Vérifier la qualité
            if bias_data.quality_score < self.min_quality_score:
                logger.warning(f"⚠️ Qualité insuffisante pour {symbol}: {bias_data.quality_score:.2f}")
                return None
            
            # Mettre en cache
            if use_cache:
                self._cache[cache_key] = (bias_data, datetime.now())
            
            logger.info(f"🎯 Dealer's Bias {symbol}: {bias_data.dealers_bias_score:+.3f} ({bias_data.direction})")
            return bias_data
            
        except Exception as e:
            logger.error(f"❌ Erreur get_dealers_bias {symbol}: {e}")
            return None

    def get_trading_signals(self, symbol: str) -> Dict[str, Any]:
        """Génère des recommandations de trading basées sur le Dealer's Bias"""
        try:
            bias_data = self.get_dealers_bias(symbol)
            if not bias_data:
                return {
                    "valid": False,
                    "reason": "NO_DATA",
                    "trading_recommendation": "NEUTRAL",
                    "warnings": ["Pas de données Dealer's Bias disponibles"]
                }
            
            # Recommandation de trading
            if bias_data.direction == "BULLISH":
                recommendation = "LONG"
            elif bias_data.direction == "BEARISH":
                recommendation = "SHORT"
            else:
                recommendation = "NEUTRAL"
            
            # Warnings
            warnings = []
            if bias_data.data_age_seconds > 300:
                warnings.append("Données anciennes (>5min)")
            if bias_data.quality_score < 0.8:
                warnings.append("Qualité des données faible")
            if abs(bias_data.dealers_bias_score) < 0.2:
                warnings.append("Signal faible")
            
            return {
                "valid": True,
                "trading_recommendation": recommendation,
                "dealers_bias_score": bias_data.dealers_bias_score,
                "direction": bias_data.direction,
                "strength": bias_data.strength,
                "data_age_seconds": bias_data.data_age_seconds,
                "quality_score": bias_data.quality_score,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur get_trading_signals {symbol}: {e}")
            return {
                "valid": False,
                "reason": "ERROR",
                "trading_recommendation": "NEUTRAL",
                "warnings": [f"Erreur: {e}"]
            }

    def get_sierra_overlay_data(self, symbol: str) -> Dict[str, Any]:
        """Prépare les données pour les overlays Sierra Chart - CORRIGÉ"""
        try:
            bias_data = self.get_dealers_bias(symbol)
            if not bias_data:
                return {
                    "valid": False,
                    "reason": "NO_DATA"
                }
            
            # Lignes horizontales
            horizontal_lines = []
            
            # Gamma Flip
            if bias_data.gamma_flip_strike:
                color = "green" if bias_data.direction == "BULLISH" else "red"
                horizontal_lines.append({
                    "price": bias_data.gamma_flip_strike,
                    "label": f"Gamma Flip {symbol}",
                    "color": color,
                    "style": "solid",
                    "width": 2
                })
            # Fallback: Max Pain si pas de Gamma Flip
            elif hasattr(bias_data, "max_pain") and bias_data.max_pain:
                horizontal_lines.append({
                    "price": bias_data.max_pain,
                    "label": f"Max Pain {symbol}",
                    "color": "orange",
                    "style": "dotted",
                    "width": 1
                })
            
            # Gamma Pins (top 3) - CORRIGÉ
            for i, pin in enumerate(bias_data.gamma_pins[:3]):
                cat = (pin.get("strength_category") or "").upper()
                color = "blue" if cat == "STRONG" else "gray"
                horizontal_lines.append({
                    "price": pin.get("strike", 0),
                    "label": f"Pin {i+1} {symbol}",
                    "color": color,
                    "style": "dashed",
                    "width": 1
                })
            
            # Métriques texte - CORRIGÉ avec GEX
            text_metrics = {
                f"{symbol}_DealersBias": f"{bias_data.dealers_bias_score:+.3f}",
                f"{symbol}_Direction": bias_data.direction,
                f"{symbol}_Strength": bias_data.strength,
                f"{symbol}_PCR": f"{bias_data.pcr_oi:.2f}",
                f"{symbol}_VIX": f"{bias_data.vix_value:.1f}",
                f"{symbol}_GEX_M": f"{bias_data.gex_signed/1e6:+.1f}M",
                f"{symbol}_Quality": f"{bias_data.quality_score:.2f}"
            }
            
            # Ajouter GEX normalisé si disponible
            if hasattr(bias_data, "gex_signed_norm") and bias_data.gex_signed_norm is not None:
                text_metrics[f"{symbol}_GEXn"] = f"{bias_data.gex_signed_norm:+.3f}"
            
            return {
                "valid": True,
                "dealers_bias_score": bias_data.dealers_bias_score,
                "direction": bias_data.direction,
                "strength": bias_data.strength,
                "horizontal_lines": horizontal_lines,
                "text_metrics": text_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur get_sierra_overlay_data {symbol}: {e}")
            return {
                "valid": False,
                "reason": "ERROR"
            }

    def get_confluence_score(self, symbol: str) -> float:
        """Calcule un score de confluence pour intégration dans MIA"""
        try:
            bias_data = self.get_dealers_bias(symbol)
            if not bias_data:
                return 0.5  # Neutre
            
            # Score de base basé sur le Dealer's Bias
            base_score = (bias_data.dealers_bias_score + 1.0) / 2.0  # Normaliser [0,1]
            
            # Moduler par la qualité des données
            quality_modifier = bias_data.quality_score
            
            # Moduler par la force du signal
            strength_modifier = 1.0
            if bias_data.strength == "STRONG":
                strength_modifier = 1.2
            elif bias_data.strength == "WEAK":
                strength_modifier = 0.8
            
            # Score final
            confluence_score = base_score * quality_modifier * strength_modifier
            
            # Limiter à [0,1]
            confluence_score = max(0.0, min(1.0, confluence_score))
            
            logger.debug(f"🎯 Confluence {symbol}: {confluence_score:.3f} (bias={bias_data.dealers_bias_score:+.3f}, quality={bias_data.quality_score:.2f})")
            return confluence_score
            
        except Exception as e:
            logger.error(f"❌ Erreur get_confluence_score {symbol}: {e}")
            return 0.5  # Neutre en cas d'erreur

# Instance globale
dealers_bias_analyzer = DealersBiasAnalyzer()

def get_dealers_bias_analyzer() -> DealersBiasAnalyzer:
    """Retourne l'instance globale de l'analyseur"""
    return dealers_bias_analyzer
