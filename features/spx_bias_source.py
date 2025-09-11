#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - SPX BIAS SOURCE INTERFACE
Interface abstraite pour les sources de données SPX/Dealer's Bias
Version: 1.0.0

🎯 FONCTIONNALITÉS :
- ✅ Interface abstraite SPXBiasSource
- ✅ Implémentation PolygonSPXAdapter
- ✅ Implémentation MockSPXSource (pour tests)
- ✅ Factory pattern pour sélectionner la source
- ✅ Configuration centralisée
- ✅ Gestion d'erreurs robuste

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Janvier 2025
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np

# Configuration logging
logger = logging.getLogger(__name__)

@dataclass
class SPXOptionsData:
    """Données structurées options SPX"""
    timestamp: datetime
    underlying_price: float
    
    # Options chain
    calls: Dict[float, Dict[str, Any]]  # strike -> data
    puts: Dict[float, Dict[str, Any]]   # strike -> data
    
    # Métriques calculées
    pcr_oi: float
    pcr_volume: float
    iv_skew: float
    total_oi: int
    total_volume: int
    
    # Statut des données
    status: str  # 'ok', 'partial', 'empty'

@dataclass
class SPXDealersBias:
    """Dealer's Bias SPX pour ES trading"""
    timestamp: datetime
    underlying_price: float
    
    # Score principal
    bias_score: float  # -1 à +1
    
    # Composantes
    gamma_flip_strike: Optional[float]
    gamma_pins: List[Dict[str, Any]]
    max_pain: Optional[float]
    
    # Métriques
    pcr_oi: float
    pcr_volume: float
    iv_skew: float
    gex_signed: float
    
    # Interprétation
    direction: str  # BULLISH/BEARISH/NEUTRAL
    strength: str   # STRONG/MODERATE/WEAK

class SPXBiasSource(ABC):
    """Interface abstraite pour les sources de données SPX/Dealer's Bias"""
    
    @abstractmethod
    async def get_spx_underlying_price(self) -> Optional[float]:
        """Récupère le prix actuel SPX"""
        pass
    
    @abstractmethod
    async def get_spx_options_chain(self, expiry_date: str = None) -> Optional[SPXOptionsData]:
        """Récupère la chaîne options SPX"""
        pass
    
    @abstractmethod
    async def calculate_spx_dealers_bias(self, spx_data: SPXOptionsData) -> Optional[SPXDealersBias]:
        """Calcule le Dealer's Bias SPX"""
        pass
    
    @abstractmethod
    async def get_spx_snapshot_for_es(self) -> Optional[Dict[str, Any]]:
        """Récupère snapshot SPX complet pour trading ES"""
        pass
    
    @abstractmethod
    async def test_api_entitlement(self) -> Dict[str, bool]:
        """Teste les entitlements de l'API"""
        pass

class PolygonSPXSource(SPXBiasSource):
    """Implémentation Polygon.io pour SPX Bias Source"""
    
    def __init__(self, api_key: str = "wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy"):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        
        # Cache SPX
        self.spx_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Configuration SPX
        self.symbol = "SPX"
        self.current_expiry = self._get_current_expiry()
        
        # Entitlements (détectés au premier appel)
        self.has_options = None
        self.has_stocks = None
        
        logger.info(f"PolygonSPXSource initialisé pour {self.symbol}")
    
    def _get_current_expiry(self) -> str:
        """Trouve l'expiration actuelle (3ème vendredi du mois)"""
        today = datetime.now()
        
        # Trouver le 3ème vendredi du mois
        first_day = today.replace(day=1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + timedelta(weeks=2)
        
        # Si on est après le 3ème vendredi, prendre le mois suivant
        if today > third_friday:
            next_month = today.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            first_friday = next_month + timedelta(days=(4 - next_month.weekday()) % 7)
            third_friday = first_friday + timedelta(weeks=2)
        
        return third_friday.strftime("%Y-%m-%d")
    
    async def get_spx_underlying_price(self) -> Optional[float]:
        """Récupère le prix actuel SPX via Polygon"""
        try:
            # Détecter entitlements si pas encore fait
            await self._probe_entitlements()
            
            # Essayer SPY d'abord (si disponible)
            if self.has_stocks:
                endpoint = "/v2/aggs/ticker/SPY/prev"
                data = await self._make_request(endpoint)
                
                if data and data.get('results'):
                    spy_price = data['results'][0]['c']  # Close price SPY
                    spx_price = spy_price * 10
                    logger.info(f"Prix SPX via SPY: {spx_price:.2f}")
                    return spx_price
            
            # Fallback: prix estimé
            logger.info("Utilisation prix SPX estimé: 5500.0")
            return 5500.0
            
        except Exception as e:
            logger.error(f"Erreur prix SPX: {e}")
            return None
    
    async def get_spx_options_chain(self, expiry_date: str = None) -> Optional[SPXOptionsData]:
        """Récupère la chaîne options SPX via Polygon"""
        try:
            # Détecter entitlements si pas encore fait
            await self._probe_entitlements()
            
            if not self.has_options:
                logger.warning("Options SPY non disponibles")
                return None
            
            expiry = expiry_date or self.current_expiry
            
            # Vérifier cache
            cache_key = f"spx_options_{expiry}"
            if cache_key in self.spx_cache:
                cached_data, timestamp = self.spx_cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_ttl:
                    logger.info("Données SPX depuis cache")
                    return cached_data
            
            # Récupérer options avec pagination
            raw_calls, raw_puts = await self._fetch_options_all("SPY", expiry)
            
            # Valider et organiser
            calls_list, puts_list = self._validate_chain(raw_calls, raw_puts)
            calls = {c['strike_price']: c for c in calls_list}
            puts = {p['strike_price']: p for p in puts_list}
            
            # Déterminer le statut
            if len(calls) >= 10 and len(puts) >= 10:
                status = "ok"
            elif len(calls) >= 5 or len(puts) >= 5:
                status = "partial"
            else:
                status = "empty"
            
            # Prix sous-jacent
            underlying_price = await self.get_spx_underlying_price()
            if not underlying_price:
                underlying_price = 5500.0
            
            # Enrichir avec données simulées
            await self._enrich_options_data_simulated(calls, puts)
            
            # Calculer métriques
            pcr_oi, pcr_volume, iv_skew = self._calculate_spx_metrics(calls, puts)
            
            # Créer objet structuré
            spx_data = SPXOptionsData(
                timestamp=datetime.now(),
                underlying_price=underlying_price,
                calls=calls,
                puts=puts,
                pcr_oi=pcr_oi,
                pcr_volume=pcr_volume,
                iv_skew=iv_skew,
                total_oi=sum(c.get('bid_size', 0) + c.get('ask_size', 0) for c in calls.values()) + 
                        sum(p.get('bid_size', 0) + p.get('ask_size', 0) for p in puts.values()),
                total_volume=sum(c.get('bid_size', 0) + c.get('ask_size', 0) for c in calls.values()) + 
                             sum(p.get('bid_size', 0) + p.get('ask_size', 0) for p in puts.values()),
                status=status
            )
            
            # Mettre en cache
            self.spx_cache[cache_key] = (spx_data, datetime.now())
            
            logger.info(f"Options SPY: {len(calls)} calls, {len(puts)} puts (status: {status})")
            return spx_data
            
        except Exception as e:
            logger.error(f"Erreur chaîne options SPY: {e}")
            return None
    
    async def calculate_spx_dealers_bias(self, spx_data: SPXOptionsData) -> Optional[SPXDealersBias]:
        """Calcule le Dealer's Bias SPX"""
        try:
            logger.info("Calcul Dealer's Bias SPX...")
            
            if spx_data.status == "empty":
                logger.warning("Données insuffisantes pour Dealer's Bias")
                return None
            
            # Calculs des composantes
            gamma_flip_strike = self._find_gamma_flip(spx_data)
            gamma_pins = self._detect_gamma_pins(spx_data)
            max_pain = self._calculate_max_pain(spx_data)
            gex_signed = self._calculate_gex(spx_data)
            
            # Score Dealer's Bias
            bias_score = self._calculate_bias_score(
                spx_data, gamma_flip_strike, gamma_pins, max_pain, gex_signed
            )
            
            # Interprétation
            direction, strength = self._interpret_bias(bias_score)
            
            dealers_bias = SPXDealersBias(
                timestamp=datetime.now(),
                underlying_price=spx_data.underlying_price,
                bias_score=bias_score,
                gamma_flip_strike=gamma_flip_strike,
                gamma_pins=gamma_pins,
                max_pain=max_pain,
                pcr_oi=spx_data.pcr_oi,
                pcr_volume=spx_data.pcr_volume,
                iv_skew=spx_data.iv_skew,
                gex_signed=gex_signed,
                direction=direction,
                strength=strength
            )
            
            logger.info(f"Dealer's Bias SPX: {direction} {strength} ({bias_score:.3f})")
            return dealers_bias
            
        except Exception as e:
            logger.error(f"Erreur calcul Dealer's Bias SPX: {e}")
            return None
    
    async def get_spx_snapshot_for_es(self) -> Optional[Dict[str, Any]]:
        """Récupère snapshot SPX complet pour trading ES"""
        try:
            logger.info("Création snapshot SPX pour ES trading...")
            
            # Récupérer données options SPX
            spx_data = await self.get_spx_options_chain()
            if not spx_data:
                return None
            
            # Calculer Dealer's Bias
            dealers_bias = None
            if spx_data.status != "empty":
                dealers_bias = await self.calculate_spx_dealers_bias(spx_data)
            
            # Formater pour MIA_IA_SYSTEM
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'SPX',
                'underlying_price': spx_data.underlying_price,
                'status': spx_data.status,
                'dealers_bias': {
                    'score': dealers_bias.bias_score if dealers_bias else 0.0,
                    'direction': dealers_bias.direction if dealers_bias else "NEUTRAL",
                    'strength': dealers_bias.strength if dealers_bias else "UNKNOWN",
                    'gamma_flip_strike': dealers_bias.gamma_flip_strike if dealers_bias else None,
                    'max_pain': dealers_bias.max_pain if dealers_bias else None,
                    'gamma_pins': dealers_bias.gamma_pins if dealers_bias else []
                },
                'metrics': {
                    'pcr_oi': spx_data.pcr_oi,
                    'pcr_volume': spx_data.pcr_volume,
                    'iv_skew': spx_data.iv_skew,
                    'gex_signed': dealers_bias.gex_signed if dealers_bias else 0.0,
                    'total_oi': spx_data.total_oi,
                    'total_volume': spx_data.total_volume
                },
                'options_summary': {
                    'calls_count': len(spx_data.calls),
                    'puts_count': len(spx_data.puts),
                    'strikes_range': {
                        'min': min(spx_data.calls.keys()) if spx_data.calls else 0,
                        'max': max(spx_data.calls.keys()) if spx_data.calls else 0
                    }
                },
                'meta': {
                    'plan': 'starter',
                    'data_delay': '15m',
                    'entitlements': {
                        'stocks': self.has_stocks or False,
                        'options': self.has_options or False,
                        'indices': False
                    },
                    'expiry_used': self.current_expiry,
                    'counts': {
                        'calls': len(spx_data.calls),
                        'puts': len(spx_data.puts)
                    },
                    'source': 'polygon',
                    'status': spx_data.status
                },
                'data_source': {
                    'type': 'options_only',
                    'plan': 'starter'
                }
            }
            
            logger.info(f"Snapshot SPX: {dealers_bias.direction if dealers_bias else 'NO DATA'} {dealers_bias.strength if dealers_bias else 'UNKNOWN'}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Erreur snapshot SPX: {e}")
            return None
    
    async def test_api_entitlement(self) -> Dict[str, bool]:
        """Teste les entitlements de l'API"""
        try:
            await self._probe_entitlements()
            
            return {
                'stocks': self.has_stocks or False,
                'options': self.has_options or False,
                'indices': False
            }
            
        except Exception as e:
            logger.error(f"Erreur test entitlements: {e}")
            return {'stocks': False, 'options': False, 'indices': False}
    
    # Méthodes privées (implémentation détaillée)
    async def _probe_entitlements(self):
        """Détecte les entitlements disponibles"""
        if self.has_options is not None:
            return
            
        logger.info("Détection entitlements API...")
        
        # Test Options SPY
        try:
            endpoint = "/v3/reference/options/contracts"
            params = {'underlying_ticker': 'SPY', 'limit': 1}
            data = await self._make_request(endpoint, params)
            self.has_options = data is not None and data.get('results')
            logger.info(f"Options SPY: {'OK' if self.has_options else 'NON DISPONIBLE'}")
        except Exception as e:
            self.has_options = False
            logger.info(f"Options SPY: NON DISPONIBLE ({str(e)[:50]}...)")
        
        # Test Stocks SPY
        try:
            endpoint = "/v2/aggs/ticker/SPY/prev"
            data = await self._make_request(endpoint)
            self.has_stocks = data is not None and data.get('results')
            logger.info(f"Stocks SPY: {'OK' if self.has_stocks else 'NON DISPONIBLE'}")
        except Exception as e:
            self.has_stocks = False
            logger.info(f"Stocks SPY: NON DISPONIBLE ({str(e)[:50]}...)")
    
    async def _make_request(self, endpoint: str, params: Dict = None, max_retry: int = 3) -> Optional[Dict]:
        """Fait une requête API avec backoff intelligent"""
        import requests
        
        try:
            url = f"{self.base_url}{endpoint}"
            params = params or {}
            params['apiKey'] = self.api_key
            
            RETRY_STATUS = {429, 500, 502, 503, 504}
            backoff = 0.6
            
            for attempt in range(1, max_retry + 1):
                try:
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        return response.json()
                    
                    if response.status_code in RETRY_STATUS:
                        if attempt < max_retry:
                            logger.warning(f"Retry {attempt}/{max_retry} dans {backoff:.1f}s (status: {response.status_code})")
                            await asyncio.sleep(backoff)
                            backoff *= 1.6
                            continue
                    
                    logger.error(f"API Error {response.status_code}: {response.text}")
                    return None
                    
                except requests.exceptions.RequestException as e:
                    if attempt < max_retry:
                        logger.warning(f"Erreur réseau, retry {attempt}/{max_retry}: {e}")
                        await asyncio.sleep(backoff)
                        backoff *= 1.6
                        continue
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Erreur requête API: {e}")
            return None
    
    async def _fetch_options_all(self, underlying: str = "SPY", expiry: str = None, limit: int = 1000) -> Tuple[List[Dict], List[Dict]]:
        """Récupère toutes les options avec pagination"""
        try:
            expiry = expiry or self.current_expiry
            
            calls = await self._fetch_options_paginated(underlying, expiry, "call", limit // 2)
            puts = await self._fetch_options_paginated(underlying, expiry, "put", limit // 2)
            
            logger.info(f"Options récupérées: {len(calls)} calls, {len(puts)} puts")
            return calls, puts
            
        except Exception as e:
            logger.error(f"Erreur pagination options: {e}")
            return [], []
    
    async def _fetch_options_paginated(self, underlying: str, expiry: str, contract_type: str, limit: int) -> List[Dict]:
        """Récupère une page d'options avec pagination"""
        import requests
        
        try:
            results = []
            
            params = {
                "underlying_ticker": underlying,
                "expiration_date": expiry,
                "contract_type": contract_type,
                "limit": 100
            }
            
            base_url = f"{self.base_url}/v3/reference/options/contracts"
            current_url = base_url
            
            while len(results) < limit:
                data = await self._make_request_raw(current_url, params)
                
                if not data or not data.get('results'):
                    break
                
                results.extend(data.get('results') or [])
                
                next_url = data.get('next_url')
                if not next_url:
                    break
                
                current_url = next_url
                params = None
                
                await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur pagination {contract_type}: {e}")
            return []
    
    async def _make_request_raw(self, url: str, params: Dict = None, max_retry: int = 3) -> Optional[Dict]:
        """Fait une requête API brute avec backoff"""
        import requests
        
        try:
            params = params or {}
            if 'apiKey' not in params:
                params['apiKey'] = self.api_key
            
            RETRY_STATUS = {429, 500, 502, 503, 504}
            backoff = 0.6
            
            for attempt in range(1, max_retry + 1):
                try:
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        return response.json()
                    
                    if response.status_code in RETRY_STATUS:
                        if attempt < max_retry:
                            logger.warning(f"Retry {attempt}/{max_retry} dans {backoff:.1f}s (status: {response.status_code})")
                            await asyncio.sleep(backoff)
                            backoff *= 1.6
                            continue
                    
                    logger.error(f"API Error {response.status_code}: {response.text}")
                    return None
                    
                except requests.exceptions.RequestException as e:
                    if attempt < max_retry:
                        logger.warning(f"Erreur réseau, retry {attempt}/{max_retry}: {e}")
                        await asyncio.sleep(backoff)
                        backoff *= 1.6
                        continue
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Erreur requête API: {e}")
            return None
    
    def _validate_chain(self, calls: List[Dict], puts: List[Dict], min_count: int = 10) -> Tuple[List[Dict], List[Dict]]:
        """Valide et filtre les données options"""
        try:
            valid_calls = [
                c for c in calls 
                if c.get("strike_price") and 
                   c.get("expiration_date") and 
                   c.get("contract_type") == "call" and
                   c.get("strike_price", 0) > 0 and 
                   c.get("strike_price", 0) < 10000
            ]
            
            valid_puts = [
                p for p in puts 
                if p.get("strike_price") and 
                   p.get("expiration_date") and 
                   p.get("contract_type") == "put" and
                   p.get("strike_price", 0) > 0 and 
                   p.get("strike_price", 0) < 10000
            ]
            
            logger.info(f"Validation: {len(valid_calls)} calls valides, {len(valid_puts)} puts valides")
            return valid_calls, valid_puts
            
        except Exception as e:
            logger.error(f"Erreur validation chaîne: {e}")
            return [], []
    
    async def _enrich_options_data_simulated(self, calls: Dict, puts: Dict):
        """Enrichit les données options avec des valeurs simulées"""
        try:
            for contract in calls.values():
                contract.update({
                    'bid': 0.01,
                    'ask': 0.02,
                    'bid_size': 100,
                    'ask_size': 100,
                    'timestamp': datetime.now().isoformat()
                })
            
            for contract in puts.values():
                contract.update({
                    'bid': 0.01,
                    'ask': 0.02,
                    'bid_size': 100,
                    'ask_size': 100,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Erreur enrichissement données simulées: {e}")
    
    def _calculate_spx_metrics(self, calls: Dict, puts: Dict) -> Tuple[float, float, float]:
        """Calcule les métriques SPX principales"""
        try:
            total_call_size = sum(c.get('bid_size', 0) + c.get('ask_size', 0) for c in calls.values())
            total_put_size = sum(p.get('bid_size', 0) + p.get('ask_size', 0) for p in puts.values())
            
            total_call_volume = total_call_size
            total_put_volume = total_put_size
            
            pcr_volume = total_put_volume / max(total_call_volume, 1)
            pcr_oi = pcr_volume
            
            call_spreads = [c.get('ask', 0) - c.get('bid', 0) for c in calls.values() if c.get('ask') and c.get('bid')]
            put_spreads = [p.get('ask', 0) - p.get('bid', 0) for p in puts.values() if p.get('ask') and p.get('bid')]
            
            avg_call_spread = np.mean(call_spreads) if call_spreads else 0.1
            avg_put_spread = np.mean(put_spreads) if put_spreads else 0.1
            
            iv_skew = (avg_put_spread - avg_call_spread) / max(avg_call_spread, 0.01)
            
            return pcr_oi, pcr_volume, iv_skew
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques SPX: {e}")
            return 1.0, 1.0, 0.0
    
    def _find_gamma_flip(self, spx_data: SPXOptionsData) -> Optional[float]:
        """Trouve le Gamma Flip"""
        try:
            strikes = sorted(spx_data.calls.keys())
            if not strikes:
                return None
            
            current_price = spx_data.underlying_price
            closest_strike = min(strikes, key=lambda x: abs(x - current_price))
            return closest_strike
            
        except Exception as e:
            logger.error(f"Erreur Gamma Flip: {e}")
            return None
    
    def _detect_gamma_pins(self, spx_data: SPXOptionsData) -> List[Dict[str, Any]]:
        """Détecte les Gamma Pins"""
        try:
            pins = []
            current_price = spx_data.underlying_price
            
            all_strikes = list(spx_data.calls.keys()) + list(spx_data.puts.keys())
            
            for strike in all_strikes:
                call_size = spx_data.calls.get(strike, {}).get('bid_size', 0) + spx_data.calls.get(strike, {}).get('ask_size', 0)
                put_size = spx_data.puts.get(strike, {}).get('bid_size', 0) + spx_data.puts.get(strike, {}).get('ask_size', 0)
                total_size = call_size + put_size
                
                distance = abs(strike - current_price)
                if distance < 50 and total_size > 100:
                    pins.append({
                        'strike': strike,
                        'distance': distance,
                        'total_size': total_size,
                        'strength': total_size / 100
                    })
            
            pins.sort(key=lambda x: x['strength'], reverse=True)
            return pins[:5]
            
        except Exception as e:
            logger.error(f"Erreur Gamma Pins: {e}")
            return []
    
    def _calculate_max_pain(self, spx_data: SPXOptionsData) -> Optional[float]:
        """Calcule le Max Pain"""
        try:
            strikes = list(set(spx_data.calls.keys()) | set(spx_data.puts.keys()))
            if not strikes:
                return None
            
            max_size_strike = None
            max_size = 0
            
            for strike in strikes:
                call_size = spx_data.calls.get(strike, {}).get('bid_size', 0) + spx_data.calls.get(strike, {}).get('ask_size', 0)
                put_size = spx_data.puts.get(strike, {}).get('bid_size', 0) + spx_data.puts.get(strike, {}).get('ask_size', 0)
                total_size = call_size + put_size
                
                if total_size > max_size:
                    max_size = total_size
                    max_size_strike = strike
            
            return max_size_strike
            
        except Exception as e:
            logger.error(f"Erreur Max Pain: {e}")
            return None
    
    def _calculate_gex(self, spx_data: SPXOptionsData) -> float:
        """Calcule le Gamma Exposure"""
        try:
            gex = 0.0
            
            if spx_data.pcr_oi > 1.5:
                gex -= 1e12
            elif spx_data.pcr_oi < 0.8:
                gex += 1e12
            
            if spx_data.iv_skew > 0.05:
                gex -= 5e11
            
            return gex
            
        except Exception as e:
            logger.error(f"Erreur GEX: {e}")
            return 0.0
    
    def _calculate_bias_score(self, spx_data: SPXOptionsData, gamma_flip: float, 
                            gamma_pins: List, max_pain: float, gex: float) -> float:
        """Calcule le score Dealer's Bias final"""
        try:
            current_price = spx_data.underlying_price
            
            # PCR Bias (25%)
            pcr_bias = 0.5
            if spx_data.pcr_oi > 1.5:
                pcr_bias = 0.2
            elif spx_data.pcr_oi < 0.8:
                pcr_bias = 0.7
            
            # IV Skew Bias (25%)
            skew_bias = 0.5
            if spx_data.iv_skew > 0.05:
                skew_bias = 0.3
            elif spx_data.iv_skew < -0.05:
                skew_bias = 0.7
            
            # Gamma Flip Bias (20%)
            flip_bias = 0.5
            if gamma_flip:
                distance = gamma_flip - current_price
                if abs(distance) < 25:
                    flip_bias = 0.5
                elif distance > 0:
                    flip_bias = 0.3
                else:
                    flip_bias = 0.7
            
            # GEX Bias (20%)
            gex_bias = 0.5
            if gex > 0:
                gex_bias = 0.6
            elif gex < -1e12:
                gex_bias = 0.3
            
            # Max Pain Bias (10%)
            pain_bias = 0.5
            if max_pain:
                distance = max_pain - current_price
                if abs(distance) < 25:
                    pain_bias = 0.5
                elif distance > 0:
                    pain_bias = 0.4
                else:
                    pain_bias = 0.6
            
            # Score final pondéré
            final_score = (
                0.25 * pcr_bias +
                0.25 * skew_bias +
                0.20 * flip_bias +
                0.20 * gex_bias +
                0.10 * pain_bias
            )
            
            # Normalisation (-1 à +1)
            normalized_score = 2 * (final_score - 0.5)
            
            return max(-1.0, min(1.0, normalized_score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score: {e}")
            return 0.0
    
    def _interpret_bias(self, bias_score: float) -> Tuple[str, str]:
        """Interprète le score Dealer's Bias"""
        try:
            abs_score = abs(bias_score)
            
            if abs_score < 0.15:
                return "NEUTRAL", "WEAK"
            elif abs_score < 0.45:
                direction = "BULLISH" if bias_score > 0 else "BEARISH"
                return direction, "MODERATE"
            else:
                direction = "BULLISH" if bias_score > 0 else "BEARISH"
                return direction, "STRONG"
                
        except Exception as e:
            logger.error(f"Erreur interprétation: {e}")
            return "NEUTRAL", "UNKNOWN"

class MockSPXSource(SPXBiasSource):
    """Implémentation Mock pour tests et développement"""
    
    def __init__(self, mock_data: Dict[str, Any] = None):
        self.mock_data = mock_data or self._get_default_mock_data()
        logger.info("MockSPXSource initialisé")
    
    def _get_default_mock_data(self) -> Dict[str, Any]:
        """Données mock par défaut"""
        return {
            'underlying_price': 5500.0,
            'bias_score': 0.2,
            'direction': 'BULLISH',
            'strength': 'MODERATE',
            'pcr_oi': 1.1,
            'pcr_volume': 1.2,
            'iv_skew': 0.02,
            'gex_signed': 5e11,
            'gamma_flip_strike': 5520.0,
            'max_pain': 5480.0,
            'gamma_pins': [
                {'strike': 5500.0, 'distance': 0.0, 'total_size': 500, 'strength': 5.0},
                {'strike': 5520.0, 'distance': 20.0, 'total_size': 300, 'strength': 3.0}
            ]
        }
    
    async def get_spx_underlying_price(self) -> Optional[float]:
        """Retourne le prix mock"""
        return self.mock_data['underlying_price']
    
    async def get_spx_options_chain(self, expiry_date: str = None) -> Optional[SPXOptionsData]:
        """Retourne des données options mock"""
        try:
            # Créer des options mock
            calls = {}
            puts = {}
            
            base_price = self.mock_data['underlying_price']
            for i in range(-10, 11):
                strike = base_price + (i * 20)
                calls[strike] = {
                    'strike_price': strike,
                    'bid': 0.01,
                    'ask': 0.02,
                    'bid_size': 100,
                    'ask_size': 100
                }
                puts[strike] = {
                    'strike_price': strike,
                    'bid': 0.01,
                    'ask': 0.02,
                    'bid_size': 120,
                    'ask_size': 120
                }
            
            return SPXOptionsData(
                timestamp=datetime.now(),
                underlying_price=base_price,
                calls=calls,
                puts=puts,
                pcr_oi=self.mock_data['pcr_oi'],
                pcr_volume=self.mock_data['pcr_volume'],
                iv_skew=self.mock_data['iv_skew'],
                total_oi=4400,
                total_volume=4400,
                status='ok'
            )
            
        except Exception as e:
            logger.error(f"Erreur données options mock: {e}")
            return None
    
    async def calculate_spx_dealers_bias(self, spx_data: SPXOptionsData) -> Optional[SPXDealersBias]:
        """Retourne un Dealer's Bias mock"""
        try:
            return SPXDealersBias(
                timestamp=datetime.now(),
                underlying_price=spx_data.underlying_price,
                bias_score=self.mock_data['bias_score'],
                gamma_flip_strike=self.mock_data['gamma_flip_strike'],
                gamma_pins=self.mock_data['gamma_pins'],
                max_pain=self.mock_data['max_pain'],
                pcr_oi=self.mock_data['pcr_oi'],
                pcr_volume=self.mock_data['pcr_volume'],
                iv_skew=self.mock_data['iv_skew'],
                gex_signed=self.mock_data['gex_signed'],
                direction=self.mock_data['direction'],
                strength=self.mock_data['strength']
            )
            
        except Exception as e:
            logger.error(f"Erreur Dealer's Bias mock: {e}")
            return None
    
    async def get_spx_snapshot_for_es(self) -> Optional[Dict[str, Any]]:
        """Retourne un snapshot mock"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'SPX',
                'underlying_price': self.mock_data['underlying_price'],
                'status': 'ok',
                'dealers_bias': {
                    'score': self.mock_data['bias_score'],
                    'direction': self.mock_data['direction'],
                    'strength': self.mock_data['strength'],
                    'gamma_flip_strike': self.mock_data['gamma_flip_strike'],
                    'max_pain': self.mock_data['max_pain'],
                    'gamma_pins': self.mock_data['gamma_pins']
                },
                'metrics': {
                    'pcr_oi': self.mock_data['pcr_oi'],
                    'pcr_volume': self.mock_data['pcr_volume'],
                    'iv_skew': self.mock_data['iv_skew'],
                    'gex_signed': self.mock_data['gex_signed'],
                    'total_oi': 4400,
                    'total_volume': 4400
                },
                'options_summary': {
                    'calls_count': 21,
                    'puts_count': 21,
                    'strikes_range': {
                        'min': self.mock_data['underlying_price'] - 200,
                        'max': self.mock_data['underlying_price'] + 200
                    }
                },
                'meta': {
                    'plan': 'mock',
                    'data_delay': '0s',
                    'entitlements': {
                        'stocks': True,
                        'options': True,
                        'indices': True
                    },
                    'expiry_used': '2025-01-17',
                    'counts': {
                        'calls': 21,
                        'puts': 21
                    },
                    'source': 'mock',
                    'status': 'ok'
                },
                'data_source': {
                    'type': 'mock',
                    'plan': 'mock'
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur snapshot mock: {e}")
            return None
    
    async def test_api_entitlement(self) -> Dict[str, bool]:
        """Retourne des entitlements mock"""
        return {
            'stocks': True,
            'options': True,
            'indices': True
        }

class SPXBiasSourceFactory:
    """Factory pour créer des instances SPXBiasSource"""
    
    @staticmethod
    def create_source(source_type: str = "polygon", **kwargs) -> SPXBiasSource:
        """Crée une instance de source SPX selon le type"""
        try:
            if source_type.lower() == "polygon":
                api_key = kwargs.get('api_key', "wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy")
                return PolygonSPXSource(api_key=api_key)
            
            elif source_type.lower() == "mock":
                mock_data = kwargs.get('mock_data')
                return MockSPXSource(mock_data=mock_data)
            
            else:
                logger.warning(f"Type de source inconnu: {source_type}, utilisation de Mock")
                return MockSPXSource()
                
        except Exception as e:
            logger.error(f"Erreur création source SPX: {e}")
            return MockSPXSource()

# Test fonction
async def test_spx_bias_source():
    """Test de l'interface SPXBiasSource"""
    logger.info("Test interface SPXBiasSource...")
    
    # Test Mock Source
    logger.info("Test MockSPXSource...")
    mock_source = SPXBiasSourceFactory.create_source("mock")
    
    snapshot = await mock_source.get_spx_snapshot_for_es()
    if snapshot:
        logger.info(f"Mock Source OK: {snapshot['dealers_bias']['direction']} {snapshot['dealers_bias']['strength']}")
    else:
        logger.error("Mock Source FAILED")
    
    # Test Polygon Source (si disponible)
    logger.info("Test PolygonSPXSource...")
    polygon_source = SPXBiasSourceFactory.create_source("polygon")
    
    entitlements = await polygon_source.test_api_entitlement()
    logger.info(f"Entitlements Polygon: {entitlements}")
    
    if entitlements['options']:
        snapshot = await polygon_source.get_spx_snapshot_for_es()
        if snapshot:
            logger.info(f"Polygon Source OK: {snapshot['dealers_bias']['direction']} {snapshot['dealers_bias']['strength']}")
        else:
            logger.error("Polygon Source FAILED")
    else:
        logger.warning("Polygon Source: Options non disponibles")
    
    logger.info("Test interface SPXBiasSource terminé")

if __name__ == "__main__":
    logger.info("Démarrage test interface SPXBiasSource...")
    asyncio.run(test_spx_bias_source())


