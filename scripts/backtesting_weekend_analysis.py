#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtesting Weekend Analysis - MIA_IA System
Analyse et utilise les données de backtesting récupérées
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import glob

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BacktestingWeekendAnalysis:
    def __init__(self):
        self.backtesting_data = None
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'market_analysis': {},
            'strategy_analysis': {},
            'risk_analysis': {},
            'recommendations': {},
            'success': False
        }
    
    def load_latest_backtesting_data(self):
        """Charger les dernières données de backtesting"""
        print("📂 Chargement données backtesting...")
        
        try:
            # Chercher le fichier le plus récent
            pattern = "data/backtesting/weekend_backtesting_data_*.json"
            files = glob.glob(pattern)
            
            if not files:
                print("❌ Aucun fichier de données backtesting trouvé")
                return False
            
            # Prendre le plus récent
            latest_file = max(files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.backtesting_data = json.load(f)
            
            print(f"✅ Données chargées: {latest_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False
    
    def analyze_market_conditions(self):
        """Analyser les conditions de marché"""
        print("📊 Analyse conditions marché...")
        
        try:
            if not self.backtesting_data:
                return False
            
            es_data = self.backtesting_data.get('es_historical_data', {})
            spx_data = self.backtesting_data.get('spx_historical_data', {})
            market_analysis = self.backtesting_data.get('market_analysis', {})
            
            # Analyser tendance
            trend = market_analysis.get('trend', 'NEUTRAL')
            current_price = market_analysis.get('current_price', 0)
            volatility = market_analysis.get('volatility', 0)
            
            # Analyser momentum
            es_closes = [bar['close'] for bar in es_data.get('data', [])]
            if len(es_closes) >= 5:
                recent_momentum = (es_closes[-1] - es_closes[-5]) / es_closes[-5] * 100
            else:
                recent_momentum = 0
            
            # Analyser volatilité
            volatility_status = "FAIBLE" if volatility < 15 else "MODÉRÉE" if volatility < 25 else "ÉLEVÉE"
            
            market_conditions = {
                'trend': trend,
                'current_price': current_price,
                'volatility': volatility,
                'volatility_status': volatility_status,
                'recent_momentum': recent_momentum,
                'es_price': es_data.get('last_close', 0),
                'spx_price': spx_data.get('last_close', 0),
                'support_levels': market_analysis.get('support_levels', []),
                'resistance_levels': market_analysis.get('resistance_levels', [])
            }
            
            self.analysis_results['market_analysis'] = market_conditions
            
            print("✅ Analyse marché complétée")
            print(f"   - Tendance: {trend}")
            print(f"   - Volatilité: {volatility:.1f}% ({volatility_status})")
            print(f"   - Momentum récent: {recent_momentum:.2f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur analyse marché: {e}")
            return False
    
    def analyze_strategy_performance(self):
        """Analyser performance des stratégies"""
        print("🎯 Analyse performance stratégies...")
        
        try:
            if not self.backtesting_data:
                return False
            
            scenarios = self.backtesting_data.get('backtesting_scenarios', {})
            options_levels = self.backtesting_data.get('options_levels', {})
            
            strategy_analysis = {}
            
            # Analyser chaque scénario
            for scenario_name, scenario_data in scenarios.items():
                entry_price = scenario_data.get('entry_price', 0)
                stop_loss = scenario_data.get('stop_loss', 0)
                take_profit = scenario_data.get('take_profit', 0)
                
                # Calculer ratios risque/récompense
                risk = abs(entry_price - stop_loss)
                reward = abs(take_profit - entry_price)
                risk_reward_ratio = reward / risk if risk > 0 else 0
                
                # Évaluer probabilité de succès basée sur la tendance
                trend = self.analysis_results['market_analysis'].get('trend', 'NEUTRAL')
                if scenario_name == 'scenario_1' and trend == 'BULLISH':
                    success_probability = 0.7
                elif scenario_name == 'scenario_2' and trend == 'BEARISH':
                    success_probability = 0.7
                else:
                    success_probability = 0.5
                
                strategy_analysis[scenario_name] = {
                    'name': scenario_data.get('name', ''),
                    'risk_reward_ratio': risk_reward_ratio,
                    'success_probability': success_probability,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'risk': risk,
                    'reward': reward
                }
            
            # Analyser niveaux options
            gex1 = options_levels.get('gamma_exposure', {}).get('gex1', 0)
            gex2 = options_levels.get('gamma_exposure', {}).get('gex2', 0)
            current_price = self.analysis_results['market_analysis'].get('current_price', 0)
            
            options_analysis = {
                'gex1_distance': abs(current_price - gex1),
                'gex2_distance': abs(current_price - gex2),
                'put_call_ratio': options_levels.get('put_call_ratio', 1.0),
                'implied_volatility': options_levels.get('implied_volatility', 0)
            }
            
            strategy_analysis['options_analysis'] = options_analysis
            self.analysis_results['strategy_analysis'] = strategy_analysis
            
            print("✅ Analyse stratégies complétée")
            print(f"   - Scénarios analysés: {len(scenarios)}")
            print(f"   - Distance GEX1: {options_analysis['gex1_distance']:.1f}")
            print(f"   - Distance GEX2: {options_analysis['gex2_distance']:.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur analyse stratégies: {e}")
            return False
    
    def analyze_risk_management(self):
        """Analyser gestion des risques"""
        print("⚠️ Analyse gestion risques...")
        
        try:
            if not self.backtesting_data:
                return False
            
            market_analysis = self.analysis_results['market_analysis']
            strategy_analysis = self.analysis_results['strategy_analysis']
            
            # Calculer position sizing recommandé
            volatility = market_analysis.get('volatility', 0)
            current_price = market_analysis.get('current_price', 0)
            
            # Position sizing basé sur volatilité
            if volatility < 15:
                position_size = 0.05  # 5% du capital
            elif volatility < 25:
                position_size = 0.03  # 3% du capital
            else:
                position_size = 0.02  # 2% du capital
            
            # Calculer stop loss recommandé
            atr_multiplier = 2.0
            stop_loss_distance = (volatility / 100) * current_price * atr_multiplier
            
            # Analyser drawdown potentiel
            max_drawdown = volatility * 0.5  # Estimation basée sur volatilité
            
            risk_analysis = {
                'position_size': position_size,
                'stop_loss_distance': stop_loss_distance,
                'max_drawdown': max_drawdown,
                'volatility_risk': "FAIBLE" if volatility < 15 else "MODÉRÉ" if volatility < 25 else "ÉLEVÉ",
                'risk_per_trade': position_size * 100,  # Pourcentage
                'max_concurrent_trades': 3 if volatility < 20 else 2
            }
            
            self.analysis_results['risk_analysis'] = risk_analysis
            
            print("✅ Analyse risques complétée")
            print(f"   - Taille position: {position_size*100:.1f}%")
            print(f"   - Distance stop loss: {stop_loss_distance:.1f}")
            print(f"   - Drawdown max: {max_drawdown:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur analyse risques: {e}")
            return False
    
    def generate_recommendations(self):
        """Générer recommandations de trading"""
        print("💡 Génération recommandations...")
        
        try:
            market_analysis = self.analysis_results['market_analysis']
            strategy_analysis = self.analysis_results['strategy_analysis']
            risk_analysis = self.analysis_results['risk_analysis']
            
            recommendations = {
                'market_outlook': '',
                'best_strategy': '',
                'entry_points': [],
                'risk_warnings': [],
                'weekend_preparation': []
            }
            
            # Analyse outlook marché
            trend = market_analysis.get('trend', 'NEUTRAL')
            volatility_status = market_analysis.get('volatility_status', 'MODÉRÉE')
            
            if trend == 'BULLISH':
                recommendations['market_outlook'] = "Marché haussier - Favoriser les stratégies longues"
            elif trend == 'BEARISH':
                recommendations['market_outlook'] = "Marché baissier - Favoriser les stratégies courtes"
            else:
                recommendations['market_outlook'] = "Marché neutre - Privilégier le range trading"
            
            # Meilleure stratégie
            best_scenario = None
            best_score = 0
            
            for scenario_name, scenario_data in strategy_analysis.items():
                if scenario_name == 'options_analysis':
                    continue
                
                score = scenario_data.get('risk_reward_ratio', 0) * scenario_data.get('success_probability', 0)
                if score > best_score:
                    best_score = score
                    best_scenario = scenario_name
            
            if best_scenario:
                recommendations['best_strategy'] = strategy_analysis[best_scenario]['name']
            
            # Points d'entrée recommandés
            current_price = market_analysis.get('current_price', 0)
            support_levels = market_analysis.get('support_levels', [])
            resistance_levels = market_analysis.get('resistance_levels', [])
            
            if trend == 'BULLISH':
                recommendations['entry_points'].append(f"Long sur pullback vers {support_levels[0]:.1f}")
                recommendations['entry_points'].append(f"Breakout au-dessus de {resistance_levels[0]:.1f}")
            elif trend == 'BEARISH':
                recommendations['entry_points'].append(f"Short sur rally vers {resistance_levels[0]:.1f}")
                recommendations['entry_points'].append(f"Breakdown en-dessous de {support_levels[0]:.1f}")
            
            # Avertissements risques
            if market_analysis.get('volatility_status') == 'ÉLEVÉE':
                recommendations['risk_warnings'].append("Volatilité élevée - Réduire taille des positions")
            
            if market_analysis.get('recent_momentum', 0) > 5:
                recommendations['risk_warnings'].append("Momentum fort - Risque de correction")
            
            # Préparation weekend
            recommendations['weekend_preparation'].append("Analyser niveaux options GEX1/GEX2")
            recommendations['weekend_preparation'].append("Préparer ordres pour lundi")
            recommendations['weekend_preparation'].append("Vérifier news économiques")
            
            self.analysis_results['recommendations'] = recommendations
            
            print("✅ Recommandations générées")
            print(f"   - Outlook: {recommendations['market_outlook']}")
            print(f"   - Meilleure stratégie: {recommendations['best_strategy']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur recommandations: {e}")
            return False
    
    def save_analysis_results(self):
        """Sauvegarder résultats d'analyse"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/backtesting/weekend_analysis_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analyse sauvegardée: {filename}")
        return filename
    
    def display_summary(self):
        """Afficher résumé de l'analyse"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ ANALYSE BACKTESTING WEEKEND")
        print("=" * 60)
        
        market = self.analysis_results.get('market_analysis', {})
        strategy = self.analysis_results.get('strategy_analysis', {})
        risk = self.analysis_results.get('risk_analysis', {})
        recommendations = self.analysis_results.get('recommendations', {})
        
        print(f"📈 MARCHÉ:")
        print(f"   - Tendance: {market.get('trend', 'N/A')}")
        print(f"   - Prix ES: {market.get('es_price', 'N/A')}")
        print(f"   - Volatilité: {market.get('volatility', 'N/A'):.1f}% ({market.get('volatility_status', 'N/A')})")
        print(f"   - Momentum: {market.get('recent_momentum', 'N/A'):.2f}%")
        
        print(f"\n🎯 STRATÉGIES:")
        print(f"   - Meilleure: {recommendations.get('best_strategy', 'N/A')}")
        print(f"   - Scénarios analysés: {len([k for k in strategy.keys() if k != 'options_analysis'])}")
        
        print(f"\n⚠️ RISQUES:")
        print(f"   - Taille position: {risk.get('position_size', 'N/A')*100:.1f}%")
        print(f"   - Stop loss: {risk.get('stop_loss_distance', 'N/A'):.1f} points")
        print(f"   - Drawdown max: {risk.get('max_drawdown', 'N/A'):.1f}%")
        
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   - Outlook: {recommendations.get('market_outlook', 'N/A')}")
        for i, entry in enumerate(recommendations.get('entry_points', []), 1):
            print(f"   - Entrée {i}: {entry}")
        
        print(f"\n📋 PRÉPARATION WEEKEND:")
        for prep in recommendations.get('weekend_preparation', []):
            print(f"   - {prep}")
    
    def run_weekend_analysis(self):
        """Exécuter analyse weekend complète"""
        print("🏆 ANALYSE BACKTESTING WEEKEND - MIA_IA SYSTEM")
        print("=" * 60)
        
        # 1. Charger données
        if not self.load_latest_backtesting_data():
            return False
        
        # 2. Analyses
        success_count = 0
        analyses = [
            ('Market Analysis', self.analyze_market_conditions),
            ('Strategy Analysis', self.analyze_strategy_performance),
            ('Risk Analysis', self.analyze_risk_management),
            ('Recommendations', self.generate_recommendations)
        ]
        
        for analysis_name, analysis_func in analyses:
            print(f"\n🔍 {analysis_name}...")
            if analysis_func():
                success_count += 1
            time.sleep(1)
        
        # 3. Sauvegarder et afficher
        filename = self.save_analysis_results()
        self.display_summary()
        
        # 4. Résultats finaux
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS ANALYSE WEEKEND")
        print("=" * 60)
        
        success_rate = (success_count / len(analyses)) * 100
        print(f"✅ Analyses réussies: {success_count}/{len(analyses)}")
        print(f"📊 Taux de succès: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 ANALYSE WEEKEND RÉUSSIE !")
            self.analysis_results['success'] = True
        else:
            print("⚠️ Analyse incomplète")
        
        return self.analysis_results['success']

def main():
    """Fonction principale"""
    print("🏆 ANALYSE BACKTESTING WEEKEND - MIA_IA SYSTEM")
    print("=" * 60)
    
    analyzer = BacktestingWeekendAnalysis()
    success = analyzer.run_weekend_analysis()
    
    if success:
        print("\n🎉 ANALYSE WEEKEND COMPLÈTE !")
        print("📋 Prêt pour la préparation trading lundi")
    else:
        print("\n⚠️ Analyse incomplète")
    
    return success

if __name__ == "__main__":
    main()










