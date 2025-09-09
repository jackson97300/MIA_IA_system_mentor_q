#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - POST-MORTEM ANALYSIS
Script d'analyse complète des causes d'échec des trades

Problème identifié:
- 9 trades → 0% win rate
- P&L: -2,359.24$
- Performance catastrophique

Objectifs:
1. Analyser chaque trade perdu
2. Identifier patterns d'échec
3. Proposer solutions concrètes
4. Optimiser paramètres
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostMortemAnalyzer:
    def __init__(self):
        self.trades_data = []
        self.analysis_results = {}
        
    def analyze_log_file(self, log_file_path: str):
        """Analyse le fichier de log pour extraire les trades"""
        logger.info("🔍 Analyse du fichier de log...")
        
        trades = []
        current_trade = {}
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                # Détecter nouveau trade
                if "SIMULATION ORDERFLOW TRADE: BUY" in line:
                    if current_trade:
                        trades.append(current_trade)
                    
                    current_trade = {
                        'timestamp': line.split(' - ')[0],
                        'type': 'BUY',
                        'price': float(line.split('@ ')[1].strip()),
                        'order_id': '',
                        'confidence': 0.0,
                        'confluence_score': 0.0,
                        'volume': 0.0,
                        'delta': 0.0,
                        'pnl': 0.0,
                        'win': False
                    }
                
                # Extraire Order ID
                elif "Order ID:" in line:
                    current_trade['order_id'] = line.split('Order ID: ')[1].strip()
                
                # Extraire confiance
                elif "Confiance:" in line:
                    current_trade['confidence'] = float(line.split('Confiance: ')[1].strip())
                
                # Extraire Confluence Score
                elif "Confluence Score:" in line:
                    current_trade['confluence_score'] = float(line.split('Confluence Score: ')[1].strip())
                
                # Extraire données OrderFlow
                elif "Volume:" in line and "Delta:" in line:
                    parts = line.split(' - ')
                    for part in parts:
                        if "Volume:" in part:
                            current_trade['volume'] = float(part.split('Volume: ')[1].strip())
                        elif "Delta:" in part:
                            current_trade['delta'] = float(part.split('Delta: ')[1].strip())
                
                # Extraire P&L
                elif "Trade perdu - Perte:" in line:
                    pnl_str = line.split('Perte: ')[1].split('$')[0].strip()
                    current_trade['pnl'] = -float(pnl_str)
                    current_trade['win'] = False
                
                elif "Trade gagné - Gain:" in line:
                    pnl_str = line.split('Gain: ')[1].split('$')[0].strip()
                    current_trade['pnl'] = float(pnl_str)
                    current_trade['win'] = True
            
            # Ajouter le dernier trade
            if current_trade:
                trades.append(current_trade)
                
            self.trades_data = trades
            logger.info(f"✅ {len(trades)} trades extraits")
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture fichier: {e}")
    
    def analyze_trades(self):
        """Analyse détaillée des trades"""
        logger.info("📊 Analyse détaillée des trades...")
        
        if not self.trades_data:
            logger.error("❌ Aucune donnée de trade disponible")
            return
        
        df = pd.DataFrame(self.trades_data)
        
        # Statistiques générales
        total_trades = len(df)
        winning_trades = len(df[df['win'] == True])
        losing_trades = len(df[df['win'] == False])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_pnl = df['pnl'].sum()
        avg_pnl = df['pnl'].mean()
        max_loss = df['pnl'].min()
        max_gain = df['pnl'].max()
        
        # Analyse des signaux
        avg_confidence = df['confidence'].mean()
        avg_confluence = df['confluence_score'].mean()
        avg_volume = df['volume'].mean()
        avg_delta = df['delta'].mean()
        
        # Analyse des seuils
        strong_signals = len(df[df['confluence_score'] >= 0.28])
        good_signals = len(df[df['confluence_score'] >= 0.25])
        weak_signals = len(df[df['confluence_score'] < 0.25])
        
        self.analysis_results = {
            'general_stats': {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl': avg_pnl,
                'max_loss': max_loss,
                'max_gain': max_gain
            },
            'signal_analysis': {
                'avg_confidence': avg_confidence,
                'avg_confluence': avg_confluence,
                'avg_volume': avg_volume,
                'avg_delta': avg_delta,
                'strong_signals': strong_signals,
                'good_signals': good_signals,
                'weak_signals': weak_signals
            },
            'trades_details': df.to_dict('records')
        }
    
    def identify_problems(self):
        """Identifie les problèmes principaux"""
        logger.info("🔍 Identification des problèmes...")
        
        problems = []
        
        # Problème 1: Win Rate 0%
        if self.analysis_results['general_stats']['win_rate'] == 0:
            problems.append({
                'severity': 'CRITICAL',
                'issue': 'Win Rate 0%',
                'description': 'Aucun trade gagnant - stratégie défaillante',
                'impact': 'Perte massive de capital',
                'solution': 'Revoir complètement la stratégie de trading'
            })
        
        # Problème 2: Seuils trop bas
        avg_confluence = self.analysis_results['signal_analysis']['avg_confluence']
        if avg_confluence < 0.35:
            problems.append({
                'severity': 'HIGH',
                'issue': 'Seuils trop bas',
                'description': f'Confluence moyenne: {avg_confluence:.1%} (cible: 35%)',
                'impact': 'Signaux de mauvaise qualité',
                'solution': 'Augmenter seuil minimum à 35%'
            })
        
        # Problème 3: Perte moyenne élevée
        avg_pnl = self.analysis_results['general_stats']['avg_pnl']
        if avg_pnl < -100:
            problems.append({
                'severity': 'HIGH',
                'issue': 'Perte moyenne élevée',
                'description': f'Perte moyenne: ${avg_pnl:.2f}',
                'impact': 'Drawdown rapide',
                'solution': 'Réduire position size et améliorer stop loss'
            })
        
        # Problème 4: Pas de signaux forts
        strong_signals = self.analysis_results['signal_analysis']['strong_signals']
        if strong_signals == 0:
            problems.append({
                'severity': 'MEDIUM',
                'issue': 'Aucun signal fort',
                'description': f'Signaux forts: {strong_signals}/{self.analysis_results["general_stats"]["total_trades"]}',
                'impact': 'Qualité des trades médiocre',
                'solution': 'Attendre signaux ≥28% confluence'
            })
        
        return problems
    
    def generate_recommendations(self):
        """Génère des recommandations concrètes"""
        logger.info("💡 Génération des recommandations...")
        
        recommendations = []
        
        # Recommandation 1: Seuils optimisés
        recommendations.append({
            'priority': 'CRITICAL',
            'action': 'Optimiser seuils de trading',
            'current': '25% (GOOD)',
            'target': '35% (PREMIUM)',
            'impact': 'Améliorer qualité des signaux',
            'implementation': 'Modifier config/automation_config.py'
        })
        
        # Recommandation 2: Risk Management
        recommendations.append({
            'priority': 'HIGH',
            'action': 'Implémenter Risk Management strict',
            'current': 'Aucun stop loss',
            'target': 'Stop Loss -50$, Take Profit +100$',
            'impact': 'Limiter les pertes',
            'implementation': 'Ajouter dans execution/risk_manager.py'
        })
        
        # Recommandation 3: Position Sizing
        recommendations.append({
            'priority': 'HIGH',
            'action': 'Réduire taille des positions',
            'current': '1.0x (trop élevé)',
            'target': '0.3x (conservateur)',
            'impact': 'Réduire exposition au risque',
            'implementation': 'Modifier position multiplier'
        })
        
        # Recommandation 4: Filtres additionnels
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Ajouter filtres de qualité',
            'current': 'Seulement OrderFlow',
            'target': 'OrderFlow + Volume + Delta + Confluence',
            'impact': 'Améliorer précision',
            'implementation': 'Enhancer signal validation'
        })
        
        # Recommandation 5: Session Management
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Limiter trades par session',
            'current': 'Illimité',
            'target': 'Max 3 trades/session',
            'impact': 'Éviter overtrading',
            'implementation': 'Ajouter session limits'
        })
        
        return recommendations
    
    def generate_report(self):
        """Génère le rapport complet"""
        logger.info("📋 Génération du rapport...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'status': 'CRITICAL FAILURE',
                'message': 'Système de trading défaillant - Action immédiate requise'
            },
            'performance': self.analysis_results['general_stats'],
            'signals': self.analysis_results['signal_analysis'],
            'problems': self.identify_problems(),
            'recommendations': self.generate_recommendations(),
            'trades': self.analysis_results['trades_details']
        }
        
        return report
    
    def save_report(self, report: Dict, filename: str = None):
        """Sauvegarde le rapport"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"post_mortem_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Rapport sauvegardé: {filename}")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
    
    def print_summary(self, report: Dict):
        """Affiche un résumé du rapport"""
        print("\n" + "="*80)
        print("🚨 RAPPORT POST-MORTEM - MIA_IA_SYSTEM")
        print("="*80)
        
        # Statut général
        print(f"\n📊 STATUT: {report['summary']['status']}")
        print(f"💬 MESSAGE: {report['summary']['message']}")
        
        # Performance
        perf = report['performance']
        print(f"\n📈 PERFORMANCE:")
        print(f"   • Trades: {perf['total_trades']}")
        print(f"   • Win Rate: {perf['win_rate']:.1f}%")
        print(f"   • P&L Total: ${perf['total_pnl']:.2f}")
        print(f"   • P&L Moyen: ${perf['avg_pnl']:.2f}")
        print(f"   • Perte Max: ${perf['max_loss']:.2f}")
        
        # Signaux
        sig = report['signals']
        print(f"\n🎯 SIGNALS:")
        print(f"   • Confiance Moyenne: {sig['avg_confidence']:.1%}")
        print(f"   • Confluence Moyenne: {sig['avg_confluence']:.1%}")
        print(f"   • Signaux Forts: {sig['strong_signals']}/{perf['total_trades']}")
        
        # Problèmes
        print(f"\n🚨 PROBLÈMES IDENTIFIÉS:")
        for i, problem in enumerate(report['problems'], 1):
            print(f"   {i}. [{problem['severity']}] {problem['issue']}")
            print(f"      {problem['description']}")
            print(f"      Solution: {problem['solution']}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS PRIORITAIRES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. [{rec['priority']}] {rec['action']}")
            print(f"      {rec['current']} → {rec['target']}")
            print(f"      Impact: {rec['impact']}")
        
        print("\n" + "="*80)

def main():
    """Fonction principale"""
    analyzer = PostMortemAnalyzer()
    
    # Analyser le fichier de log
    log_file = r"c:\Users\LILJACKS\OneDrive\Bureau\jackson.txt"
    analyzer.analyze_log_file(log_file)
    
    # Analyser les trades
    analyzer.analyze_trades()
    
    # Générer le rapport
    report = analyzer.generate_report()
    
    # Sauvegarder le rapport
    analyzer.save_report(report)
    
    # Afficher le résumé
    analyzer.print_summary(report)
    
    return report

if __name__ == "__main__":
    main()

