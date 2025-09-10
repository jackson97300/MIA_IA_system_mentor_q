#!/usr/bin/env python3
"""
ANALYSE ALTERNATIVES IBKR - MIA_IA_SYSTEM
Évaluation DXFeed vs IQFeed selon les besoins du bot
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class AlternativeIBKRAnalyzer:
    """Analyseur des alternatives à IBKR pour MIA_IA_SYSTEM"""
    
    def __init__(self):
        self.bot_requirements = self._load_bot_requirements()
        self.dxfeed_capabilities = self._load_dxfeed_capabilities()
        self.iqfeed_capabilities = self._load_iqfeed_capabilities()
        
    def _load_bot_requirements(self) -> Dict[str, Any]:
        """Charger les besoins du bot depuis le document de référence"""
        
        return {
            "données_critiques": {
                "ohlc_data": {
                    "symbols": ["ES", "SPY", "VIX"],
                    "timeframes": ["1min", "5min", "15min", "1hour"],
                    "data_points": ["open", "high", "low", "close", "volume", "vwap", "tick_count"],
                    "frequency": "real_time",
                    "session_coverage": "24/7"
                },
                "orderflow_data": {
                    "level2_data": {
                        "bid_ask_spreads": True,
                        "order_book_depth": 10,
                        "volume_imbalance": True,
                        "aggressive_buys_sells": True
                    },
                    "tick_data": {
                        "price_ticks": True,
                        "volume_ticks": True,
                        "timestamp_precision": "microsecond",
                        "cumulative_delta": True
                    },
                    "smart_money_detection": {
                        "large_orders": ">100_contracts",
                        "institutional_flow": True,
                        "absorption_patterns": True
                    }
                },
                "options_data": {
                    "spx_options_chains": {
                        "all_strikes": True,
                        "all_expirations": True,
                        "greeks": ["delta", "gamma", "theta", "vega"],
                        "implied_volatility": True,
                        "open_interest": True,
                        "volume": True
                    },
                    "gamma_exposure": {
                        "total_gamma": True,
                        "dealer_gamma": True,
                        "gamma_flip_levels": True,
                        "gamma_hedging_flow": True
                    }
                }
            },
            "techniques_élites": {
                "mtf_confluence": "Multi-timeframe analysis",
                "smart_money_tracker": "Institutional flow detection",
                "ml_ensemble_filter": "Machine learning models",
                "gamma_cycles_analyzer": "Options gamma analysis",
                "order_book_imbalance": "Level 2 order book analysis",
                "tick_momentum_analysis": "Microstructure analysis"
            },
            "patterns_trading": {
                "sierra_chart_patterns": ["Long Down Up Bar", "Long Up Down Bar", "Color Down Setting"],
                "patterns_élites": ["Headfake", "Gamma Pin", "Microstructure Anomaly"]
            },
            "volume_profiles": {
                "market_profile": "VAH/VAL/POC analysis",
                "volume_profile_imbalance": "Smart money detection via volume",
                "value_area_analysis": "Price distribution analysis"
            },
            "performance_requirements": {
                "latency_target": "<50ms",
                "data_completeness": ">99.5%",
                "accuracy_target": ">99.9%",
                "calculation_speed": "<2ms",
                "feature_coverage": "25+ features"
            }
        }
    
    def _load_dxfeed_capabilities(self) -> Dict[str, Any]:
        """Capacités DXFeed"""
        
        return {
            "nom": "DXFeed",
            "type": "Market Data Provider",
            "capabilities": {
                "market_data": {
                    "symbols_supportés": ["ES", "SPY", "VIX", "SPX", "NQ", "YM", "RTY"],
                    "timeframes": ["1min", "5min", "15min", "1hour", "daily"],
                    "data_types": ["OHLC", "tick_data", "level2", "volume_profile"],
                    "latence": "<10ms",
                    "couverture": "24/7"
                },
                "orderflow": {
                    "level2_data": True,
                    "order_book_depth": 20,
                    "volume_imbalance": True,
                    "aggressive_orders": True,
                    "cumulative_delta": True
                },
                "options": {
                    "options_chains": True,
                    "greeks": ["delta", "gamma", "theta", "vega"],
                    "implied_volatility": True,
                    "open_interest": True,
                    "gamma_exposure": "Partiel"
                },
                "smart_money": {
                    "large_orders_detection": True,
                    "institutional_flow": True,
                    "absorption_patterns": True
                },
                "api": {
                    "protocols": ["Java", "C++", "C#", "Python"],
                    "websocket": True,
                    "rest_api": True,
                    "file_feed": True
                }
            },
            "avantages": [
                "Latence ultra-faible (<10ms)",
                "Données Level 2 complètes",
                "Support options avancé",
                "API Python native",
                "Couverture mondiale",
                "Données historiques complètes"
            ],
            "inconvénients": [
                "Coût élevé",
                "Complexité d'intégration",
                "Support limité pour gamma exposure complet",
                "Pas d'exécution d'ordres"
            ],
            "coût": "Élevé (500-2000$/mois selon volume)",
            "intégration": "Complexe mais possible"
        }
    
    def _load_iqfeed_capabilities(self) -> Dict[str, Any]:
        """Capacités IQFeed"""
        
        return {
            "nom": "IQFeed",
            "type": "Market Data Provider",
            "capabilities": {
                "market_data": {
                    "symbols_supportés": ["ES", "SPY", "VIX", "SPX", "NQ", "YM", "RTY"],
                    "timeframes": ["1min", "5min", "15min", "1hour", "daily"],
                    "data_types": ["OHLC", "tick_data", "level2", "volume_profile"],
                    "latence": "<50ms",
                    "couverture": "24/7"
                },
                "orderflow": {
                    "level2_data": True,
                    "order_book_depth": 10,
                    "volume_imbalance": True,
                    "aggressive_orders": True,
                    "cumulative_delta": "Partiel"
                },
                "options": {
                    "options_chains": True,
                    "greeks": ["delta", "gamma", "theta", "vega"],
                    "implied_volatility": True,
                    "open_interest": True,
                    "gamma_exposure": "Limité"
                },
                "smart_money": {
                    "large_orders_detection": "Partiel",
                    "institutional_flow": True,
                    "absorption_patterns": "Limité"
                },
                "api": {
                    "protocols": ["C++", "C#", "Java", "Python"],
                    "websocket": True,
                    "rest_api": False,
                    "file_feed": True
                }
            },
            "avantages": [
                "Coût modéré",
                "API stable et mature",
                "Données historiques complètes",
                "Support technique bon",
                "Intégration relativement simple"
            ],
            "inconvénients": [
                "Latence plus élevée que DXFeed",
                "Options gamma exposure limité",
                "Smart money detection partielle",
                "Pas d'exécution d'ordres",
                "API moins moderne"
            ],
            "coût": "Modéré (100-500$/mois selon volume)",
            "intégration": "Modérée"
        }
    
    def analyze_coverage(self, provider: str) -> Dict[str, Any]:
        """Analyser la couverture des besoins par provider"""
        
        if provider.lower() == "dxfeed":
            capabilities = self.dxfeed_capabilities
        elif provider.lower() == "iqfeed":
            capabilities = self.iqfeed_capabilities
        else:
            return {"error": "Provider non reconnu"}
        
        coverage_analysis = {
            "provider": provider,
            "couverture_globale": 0,
            "détails_par_catégorie": {},
            "gaps_critiques": [],
            "recommandations": []
        }
        
        # Analyser OHLC Data
        ohlc_coverage = self._analyze_ohlc_coverage(capabilities)
        coverage_analysis["détails_par_catégorie"]["ohlc_data"] = ohlc_coverage
        
        # Analyser Orderflow Data
        orderflow_coverage = self._analyze_orderflow_coverage(capabilities)
        coverage_analysis["détails_par_catégorie"]["orderflow_data"] = orderflow_coverage
        
        # Analyser Options Data
        options_coverage = self._analyze_options_coverage(capabilities)
        coverage_analysis["détails_par_catégorie"]["options_data"] = options_coverage
        
        # Analyser Techniques Élites
        techniques_coverage = self._analyze_techniques_coverage(capabilities)
        coverage_analysis["détails_par_catégorie"]["techniques_élites"] = techniques_coverage
        
        # Analyser Performance Requirements
        performance_coverage = self._analyze_performance_coverage(capabilities)
        coverage_analysis["détails_par_catégorie"]["performance"] = performance_coverage
        
        # Calculer couverture globale
        total_coverage = (
            ohlc_coverage["score"] * 0.3 +
            orderflow_coverage["score"] * 0.3 +
            options_coverage["score"] * 0.2 +
            techniques_coverage["score"] * 0.15 +
            performance_coverage["score"] * 0.05
        )
        
        coverage_analysis["couverture_globale"] = total_coverage
        
        return coverage_analysis
    
    def _analyze_ohlc_coverage(self, capabilities: Dict) -> Dict[str, Any]:
        """Analyser couverture OHLC"""
        
        requirements = self.bot_requirements["données_critiques"]["ohlc_data"]
        provider_cap = capabilities["capabilities"]["market_data"]
        
        score = 0
        gaps = []
        covered = []
        
        # Symboles
        required_symbols = set(requirements["symbols"])
        provided_symbols = set(provider_cap["symbols_supportés"])
        symbol_coverage = len(required_symbols.intersection(provided_symbols)) / len(required_symbols)
        
        if symbol_coverage == 1.0:
            score += 25
            covered.append("Tous symboles supportés")
        else:
            gaps.append(f"Symboles manquants: {required_symbols - provided_symbols}")
            score += symbol_coverage * 25
        
        # Timeframes
        required_timeframes = set(requirements["timeframes"])
        provided_timeframes = set(provider_cap["timeframes"])
        timeframe_coverage = len(required_timeframes.intersection(provided_timeframes)) / len(required_timeframes)
        
        if timeframe_coverage == 1.0:
            score += 25
            covered.append("Tous timeframes supportés")
        else:
            gaps.append(f"Timeframes manquants: {required_timeframes - provided_timeframes}")
            score += timeframe_coverage * 25
        
        # Data points
        if "OHLC" in provider_cap["data_types"]:
            score += 25
            covered.append("OHLC complet")
        else:
            gaps.append("OHLC incomplet")
        
        # 24/7 coverage
        if provider_cap["couverture"] == "24/7":
            score += 25
            covered.append("Couverture 24/7")
        else:
            gaps.append("Pas de couverture 24/7")
        
        return {
            "score": score,
            "gaps": gaps,
            "covered": covered,
            "coverage_percentage": score
        }
    
    def _analyze_orderflow_coverage(self, capabilities: Dict) -> Dict[str, Any]:
        """Analyser couverture Orderflow"""
        
        requirements = self.bot_requirements["données_critiques"]["orderflow_data"]
        provider_cap = capabilities["capabilities"]["orderflow"]
        
        score = 0
        gaps = []
        covered = []
        
        # Level 2 Data
        if provider_cap["level2_data"]:
            score += 20
            covered.append("Level 2 data")
            
            # Order book depth
            if provider_cap["order_book_depth"] >= requirements["level2_data"]["order_book_depth"]:
                score += 15
                covered.append("Order book depth suffisant")
            else:
                gaps.append(f"Order book depth insuffisant: {provider_cap['order_book_depth']} vs {requirements['level2_data']['order_book_depth']}")
        else:
            gaps.append("Pas de Level 2 data")
        
        # Volume imbalance
        if provider_cap["volume_imbalance"]:
            score += 20
            covered.append("Volume imbalance")
        else:
            gaps.append("Pas de volume imbalance")
        
        # Aggressive orders
        if provider_cap["aggressive_orders"]:
            score += 20
            covered.append("Aggressive orders detection")
        else:
            gaps.append("Pas de detection aggressive orders")
        
        # Cumulative delta
        if provider_cap["cumulative_delta"] == True:
            score += 25
            covered.append("Cumulative delta complet")
        elif provider_cap["cumulative_delta"] == "Partiel":
            score += 15
            covered.append("Cumulative delta partiel")
            gaps.append("Cumulative delta limité")
        else:
            gaps.append("Pas de cumulative delta")
        
        return {
            "score": score,
            "gaps": gaps,
            "covered": covered,
            "coverage_percentage": score
        }
    
    def _analyze_options_coverage(self, capabilities: Dict) -> Dict[str, Any]:
        """Analyser couverture Options"""
        
        requirements = self.bot_requirements["données_critiques"]["options_data"]
        provider_cap = capabilities["capabilities"]["options"]
        
        score = 0
        gaps = []
        covered = []
        
        # Options chains
        if provider_cap["options_chains"]:
            score += 20
            covered.append("Options chains")
        else:
            gaps.append("Pas d'options chains")
        
        # Greeks
        required_greeks = set(requirements["spx_options_chains"]["greeks"])
        provided_greeks = set(provider_cap["greeks"])
        greeks_coverage = len(required_greeks.intersection(provided_greeks)) / len(required_greeks)
        
        if greeks_coverage == 1.0:
            score += 25
            covered.append("Tous Greeks supportés")
        else:
            gaps.append(f"Greeks manquants: {required_greeks - provided_greeks}")
            score += greeks_coverage * 25
        
        # Implied volatility
        if provider_cap["implied_volatility"]:
            score += 15
            covered.append("Implied volatility")
        else:
            gaps.append("Pas d'implied volatility")
        
        # Gamma exposure
        if provider_cap["gamma_exposure"] == True:
            score += 40
            covered.append("Gamma exposure complet")
        elif provider_cap["gamma_exposure"] == "Partiel":
            score += 20
            covered.append("Gamma exposure partiel")
            gaps.append("Gamma exposure limité")
        else:
            gaps.append("Pas de gamma exposure")
        
        return {
            "score": score,
            "gaps": gaps,
            "covered": covered,
            "coverage_percentage": score
        }
    
    def _analyze_techniques_coverage(self, capabilities: Dict) -> Dict[str, Any]:
        """Analyser couverture Techniques Élites"""
        
        score = 0
        gaps = []
        covered = []
        
        # MTF Confluence - possible avec données multi-timeframe
        if "1min" in capabilities["capabilities"]["market_data"]["timeframes"] and "1hour" in capabilities["capabilities"]["market_data"]["timeframes"]:
            score += 20
            covered.append("MTF Confluence possible")
        else:
            gaps.append("MTF Confluence limité - timeframes manquants")
        
        # Smart Money Tracker
        if capabilities["capabilities"]["smart_money"]["large_orders_detection"]:
            score += 20
            covered.append("Smart Money Tracker possible")
        else:
            gaps.append("Smart Money Tracker limité")
        
        # Order Book Imbalance
        if capabilities["capabilities"]["orderflow"]["level2_data"]:
            score += 20
            covered.append("Order Book Imbalance possible")
        else:
            gaps.append("Order Book Imbalance impossible")
        
        # Tick Momentum Analysis
        if "tick_data" in capabilities["capabilities"]["market_data"]["data_types"]:
            score += 20
            covered.append("Tick Momentum Analysis possible")
        else:
            gaps.append("Tick Momentum Analysis impossible")
        
        # Gamma Cycles Analyzer
        if capabilities["capabilities"]["options"]["gamma_exposure"]:
            score += 20
            covered.append("Gamma Cycles Analyzer possible")
        else:
            gaps.append("Gamma Cycles Analyzer limité")
        
        return {
            "score": score,
            "gaps": gaps,
            "covered": covered,
            "coverage_percentage": score
        }
    
    def _analyze_performance_coverage(self, capabilities: Dict) -> Dict[str, Any]:
        """Analyser couverture Performance Requirements"""
        
        requirements = self.bot_requirements["performance_requirements"]
        provider_cap = capabilities["capabilities"]["market_data"]
        
        score = 0
        gaps = []
        covered = []
        
        # Latency
        if provider_cap["latence"] == "<10ms":
            score += 40
            covered.append("Latence excellente (<10ms)")
        elif provider_cap["latence"] == "<50ms":
            score += 20
            covered.append("Latence acceptable (<50ms)")
        else:
            gaps.append("Latence insuffisante")
        
        # 24/7 coverage
        if provider_cap["couverture"] == "24/7":
            score += 30
            covered.append("Couverture 24/7")
        else:
            gaps.append("Pas de couverture 24/7")
        
        # API Python
        if "Python" in capabilities["capabilities"]["api"]["protocols"]:
            score += 30
            covered.append("API Python supportée")
        else:
            gaps.append("API Python non supportée")
        
        return {
            "score": score,
            "gaps": gaps,
            "covered": covered,
            "coverage_percentage": score
        }
    
    def generate_recommendation(self) -> Dict[str, Any]:
        """Générer recommandation finale"""
        
        dxfeed_analysis = self.analyze_coverage("dxfeed")
        iqfeed_analysis = self.analyze_coverage("iqfeed")
        
        recommendation = {
            "analyse_comparative": {
                "dxfeed": {
                    "couverture": dxfeed_analysis["couverture_globale"],
                    "coût": self.dxfeed_capabilities["coût"],
                    "intégration": self.dxfeed_capabilities["intégration"]
                },
                "iqfeed": {
                    "couverture": iqfeed_analysis["couverture_globale"],
                    "coût": self.iqfeed_capabilities["coût"],
                    "intégration": self.iqfeed_capabilities["intégration"]
                }
            },
            "recommandation": "",
            "justification": [],
            "plan_migration": {},
            "risques": []
        }
        
        # Recommandation basée sur couverture
        if dxfeed_analysis["couverture_globale"] > iqfeed_analysis["couverture_globale"]:
            recommendation["recommandation"] = "DXFeed"
            recommendation["justification"].append(f"Meilleure couverture: {dxfeed_analysis['couverture_globale']:.1f}% vs {iqfeed_analysis['couverture_globale']:.1f}%")
        else:
            recommendation["recommandation"] = "IQFeed"
            recommendation["justification"].append(f"Couverture similaire mais coût inférieur")
        
        # Justifications supplémentaires
        if recommendation["recommandation"] == "DXFeed":
            recommendation["justification"].extend([
                "Latence ultra-faible (<10ms) vs IQFeed (<50ms)",
                "Gamma exposure plus complet",
                "Smart money detection avancée",
                "API Python native"
            ])
        else:
            recommendation["justification"].extend([
                "Coût 3-4x inférieur à DXFeed",
                "Intégration plus simple",
                "Support technique excellent",
                "Stabilité éprouvée"
            ])
        
        # Plan de migration
        recommendation["plan_migration"] = {
            "phase_1": "Test avec données historiques",
            "phase_2": "Intégration API et tests temps réel",
            "phase_3": "Migration progressive des symboles",
            "phase_4": "Optimisation performance",
            "durée_estimée": "4-8 semaines"
        }
        
        # Risques
        recommendation["risques"] = [
            "Coût élevé (DXFeed)",
            "Complexité d'intégration",
            "Dépendance externe",
            "Latence réseau",
            "Support gamma exposure limité (IQFeed)"
        ]
        
        return recommendation

def main():
    """Fonction principale d'analyse"""
    
    print("🔍 ANALYSE ALTERNATIVES IBKR - MIA_IA_SYSTEM")
    print("=" * 60)
    
    analyzer = AlternativeIBKRAnalyzer()
    
    # Analyser DXFeed
    print("\n📊 ANALYSE DXFeed")
    print("-" * 30)
    dxfeed_analysis = analyzer.analyze_coverage("dxfeed")
    print(f"Couverture globale: {dxfeed_analysis['couverture_globale']:.1f}%")
    
    for catégorie, détails in dxfeed_analysis["détails_par_catégorie"].items():
        print(f"  {catégorie}: {détails['score']:.0f}%")
        if détails["gaps"]:
            print(f"    Gaps: {', '.join(détails['gaps'][:2])}")
    
    # Analyser IQFeed
    print("\n📊 ANALYSE IQFeed")
    print("-" * 30)
    iqfeed_analysis = analyzer.analyze_coverage("iqfeed")
    print(f"Couverture globale: {iqfeed_analysis['couverture_globale']:.1f}%")
    
    for catégorie, détails in iqfeed_analysis["détails_par_catégorie"].items():
        print(f"  {catégorie}: {détails['score']:.0f}%")
        if détails["gaps"]:
            print(f"    Gaps: {', '.join(détails['gaps'][:2])}")
    
    # Recommandation finale
    print("\n🎯 RECOMMANDATION FINALE")
    print("-" * 30)
    recommendation = analyzer.generate_recommendation()
    
    print(f"Recommandation: {recommendation['recommandation']}")
    print("\nJustifications:")
    for justification in recommendation["justification"]:
        print(f"  ✅ {justification}")
    
    print(f"\nCoût estimé: {recommendation['analyse_comparative'][recommendation['recommandation'].lower()]['coût']}")
    print(f"Complexité intégration: {recommendation['analyse_comparative'][recommendation['recommandation'].lower()]['intégration']}")
    
    print("\n⚠️ Risques identifiés:")
    for risque in recommendation["risques"]:
        print(f"  ⚠️ {risque}")
    
    # Sauvegarder analyse
    with open("analyse_alternatives_ibkr.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "dxfeed_analysis": dxfeed_analysis,
            "iqfeed_analysis": iqfeed_analysis,
            "recommendation": recommendation
        }, f, indent=2)
    
    print(f"\n💾 Analyse sauvegardée: analyse_alternatives_ibkr.json")

if __name__ == "__main__":
    main()

