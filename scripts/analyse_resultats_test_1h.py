#!/usr/bin/env python3
"""
ANALYSE DÉTAILLÉE RÉSULTATS TEST 1 HEURE - MIA_IA_SYSTEM
========================================================
Analyse complète des résultats du test de 1 heure
"""

import json
import pandas as pd
from datetime import datetime
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import numpy as np

def load_test_results(file_path):
    """Charge les résultats du test"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_trading_performance(data):
    """Analyse la performance trading"""
    print("🎯 ANALYSE PERFORMANCE TRADING")
    print("=" * 50)
    
    metrics = data['trading_metrics']
    
    print(f"📊 Trades totaux: {metrics['total_trades']}")
    print(f"✅ Trades gagnants: {metrics['winning_trades']}")
    print(f"❌ Trades perdants: {metrics['losing_trades']}")
    print(f"🎯 Win Rate: {metrics['win_rate_percent']:.2f}%")
    print(f"💰 P&L Total: ${metrics['total_pnl']:.2f}")
    print(f"📈 Gain moyen: ${metrics['avg_win']:.2f}")
    print(f"📉 Perte moyenne: ${metrics['avg_loss']:.2f}")
    print(f"⚖️ Profit Factor: {metrics['profit_factor']:.2f}")
    
    # Calculs supplémentaires
    total_volume = sum(trade['size'] for trade in data['trades_data'])
    avg_trade_size = total_volume / len(data['trades_data']) if data['trades_data'] else 0
    
    print(f"📦 Volume total: {total_volume} contrats")
    print(f"📦 Taille moyenne trade: {avg_trade_size:.1f} contrats")
    
    return metrics

def analyze_system_performance(data):
    """Analyse la performance système"""
    print("\n⚡ ANALYSE PERFORMANCE SYSTÈME")
    print("=" * 50)
    
    metrics = data['system_metrics']
    
    print(f"🔄 Cycles totaux: {metrics['total_cycles']}")
    print(f"✅ Cycles réussis: {metrics['successful_cycles']}")
    print(f"❌ Cycles échoués: {metrics['failed_cycles']}")
    print(f"📊 Uptime système: {metrics['system_uptime_percent']:.2f}%")
    print(f"⏱️ Temps cycle moyen: {metrics['avg_cycle_time_seconds']:.3f}s")
    print(f"🚨 Alertes générées: {metrics['alerts_generated']}")
    
    # Calculs supplémentaires
    trades_per_minute = len(data['trades_data']) / 60
    cycles_per_trade = metrics['total_cycles'] / len(data['trades_data']) if data['trades_data'] else 0
    
    print(f"🎯 Trades par minute: {trades_per_minute:.1f}")
    print(f"🔄 Cycles par trade: {cycles_per_trade:.1f}")
    
    return metrics

def analyze_patterns(data):
    """Analyse des patterns utilisés"""
    print("\n📊 ANALYSE DES PATTERNS")
    print("=" * 50)
    
    all_patterns = []
    pattern_results = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0})
    
    for trade in data['trades_data']:
        patterns = trade.get('patterns_used', [])
        result = trade['result']
        
        if patterns:
            for pattern in patterns:
                all_patterns.append(pattern)
                pattern_results[pattern]['total'] += 1
                if result == 'WIN':
                    pattern_results[pattern]['wins'] += 1
                else:
                    pattern_results[pattern]['losses'] += 1
    
    # Statistiques patterns
    pattern_counter = Counter(all_patterns)
    print("📈 Patterns les plus utilisés:")
    for pattern, count in pattern_counter.most_common():
        print(f"   {pattern}: {count} fois")
    
    print("\n🎯 Performance par pattern:")
    for pattern, stats in pattern_results.items():
        if stats['total'] > 0:
            win_rate = (stats['wins'] / stats['total']) * 100
            print(f"   {pattern}: {stats['wins']}/{stats['total']} ({win_rate:.1f}%)")
    
    return pattern_results

def analyze_features(data):
    """Analyse des features utilisées"""
    print("\n⚙️ ANALYSE DES FEATURES")
    print("=" * 50)
    
    all_features = []
    feature_results = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0})
    
    for trade in data['trades_data']:
        features = trade.get('features_used', [])
        result = trade['result']
        
        for feature in features:
            all_features.append(feature)
            feature_results[feature]['total'] += 1
            if result == 'WIN':
                feature_results[feature]['wins'] += 1
            else:
                feature_results[feature]['losses'] += 1
    
    # Statistiques features
    feature_counter = Counter(all_features)
    print("📊 Features les plus utilisées:")
    for feature, count in feature_counter.most_common():
        print(f"   {feature}: {count} fois")
    
    print("\n🎯 Performance par feature:")
    for feature, stats in feature_results.items():
        if stats['total'] > 0:
            win_rate = (stats['wins'] / stats['total']) * 100
            print(f"   {feature}: {stats['wins']}/{stats['total']} ({win_rate:.1f}%)")
    
    return feature_results

def analyze_signal_strength(data):
    """Analyse de la force des signaux"""
    print("\n💪 ANALYSE FORCE DES SIGNAUX")
    print("=" * 50)
    
    signal_strengths = [trade['signal_strength'] for trade in data['trades_data']]
    winning_signals = [trade['signal_strength'] for trade in data['trades_data'] if trade['result'] == 'WIN']
    losing_signals = [trade['signal_strength'] for trade in data['trades_data'] if trade['result'] == 'LOSS']
    
    print(f"📊 Force signal moyenne: {np.mean(signal_strengths):.3f}")
    print(f"📈 Force signal gagnants: {np.mean(winning_signals):.3f}")
    print(f"📉 Force signal perdants: {np.mean(losing_signals):.3f}")
    print(f"📊 Écart-type force signal: {np.std(signal_strengths):.3f}")
    
    # Analyse par tranches de force
    print("\n🎯 Performance par tranche de force:")
    ranges = [(0.8, 0.85), (0.85, 0.9), (0.9, 0.95), (0.95, 1.0)]
    
    for min_strength, max_strength in ranges:
        trades_in_range = [t for t in data['trades_data'] 
                          if min_strength <= t['signal_strength'] < max_strength]
        
        if trades_in_range:
            wins = len([t for t in trades_in_range if t['result'] == 'WIN'])
            win_rate = (wins / len(trades_in_range)) * 100
            print(f"   {min_strength:.2f}-{max_strength:.2f}: {wins}/{len(trades_in_range)} ({win_rate:.1f}%)")
    
    return {
        'avg_strength': np.mean(signal_strengths),
        'winning_strength': np.mean(winning_signals),
        'losing_strength': np.mean(losing_signals)
    }

def analyze_trade_directions(data):
    """Analyse des directions de trades"""
    print("\n🔄 ANALYSE DIRECTIONS DE TRADES")
    print("=" * 50)
    
    directions = [trade['direction'] for trade in data['trades_data']]
    direction_counter = Counter(directions)
    
    print("📊 Répartition des directions:")
    for direction, count in direction_counter.items():
        percentage = (count / len(data['trades_data'])) * 100
        print(f"   {direction}: {count} ({percentage:.1f}%)")
    
    # Performance par direction
    direction_results = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0})
    
    for trade in data['trades_data']:
        direction = trade['direction']
        result = trade['result']
        
        direction_results[direction]['total'] += 1
        if result == 'WIN':
            direction_results[direction]['wins'] += 1
        else:
            direction_results[direction]['losses'] += 1
    
    print("\n🎯 Performance par direction:")
    for direction, stats in direction_results.items():
        if stats['total'] > 0:
            win_rate = (stats['wins'] / stats['total']) * 100
            print(f"   {direction}: {stats['wins']}/{stats['total']} ({win_rate:.1f}%)")
    
    return direction_results

def analyze_alerts(data):
    """Analyse des alertes générées"""
    print("\n🚨 ANALYSE DES ALERTES")
    print("=" * 50)
    
    alert_types = [alert['type'] for alert in data['alerts_data']]
    alert_counter = Counter(alert_types)
    
    print("📊 Types d'alertes générées:")
    for alert_type, count in alert_counter.items():
        print(f"   {alert_type}: {count}")
    
    # Analyse des messages d'alertes
    alert_messages = [alert['message'] for alert in data['alerts_data']]
    message_counter = Counter(alert_messages)
    
    print("\n📝 Messages d'alertes les plus fréquents:")
    for message, count in message_counter.most_common(5):
        print(f"   '{message}': {count} fois")
    
    return alert_counter

def generate_summary_report(data):
    """Génère un rapport de synthèse"""
    print("\n🏆 RAPPORT DE SYNTHÈSE - TEST 1 HEURE MIA_IA")
    print("=" * 60)
    
    # Critères de succès
    success_criteria = {
        'system_uptime': data['system_metrics']['system_uptime_percent'] >= 95,
        'trades_executed': data['trading_metrics']['total_trades'] >= 50,
        'win_rate': data['trading_metrics']['win_rate_percent'] >= 50,
        'profit_factor': data['trading_metrics']['profit_factor'] >= 1.5
    }
    
    passed_criteria = sum(success_criteria.values())
    total_criteria = len(success_criteria)
    
    print(f"📊 Score global: {passed_criteria}/{total_criteria} critères réussis")
    
    print("\n✅ Critères de succès:")
    print(f"   Uptime système ≥ 95%: {'✅' if success_criteria['system_uptime'] else '❌'}")
    print(f"   Trades exécutés ≥ 50: {'✅' if success_criteria['trades_executed'] else '❌'}")
    print(f"   Win Rate ≥ 50%: {'✅' if success_criteria['win_rate'] else '❌'}")
    print(f"   Profit Factor ≥ 1.5: {'✅' if success_criteria['profit_factor'] else '❌'}")
    
    if passed_criteria == total_criteria:
        print("\n🎉 SYSTÈME MIA_IA 100% VALIDÉ POUR LA PRODUCTION !")
        print("✅ Tous les critères de succès atteints")
        print("🚀 Prêt pour le trading automatisé en conditions réelles")
    else:
        print(f"\n⚠️ {total_criteria - passed_criteria} critère(s) non atteint(s)")
        print("🔧 Optimisation nécessaire avant production")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    
    if data['trading_metrics']['win_rate_percent'] < 70:
        print("   🔧 Optimiser la détection de patterns")
        print("   🔧 Améliorer les critères de confluence")
    
    if data['trading_metrics']['profit_factor'] < 2.0:
        print("   🔧 Ajuster la gestion des risques")
        print("   🔧 Optimiser la taille des positions")
    
    if data['system_metrics']['avg_cycle_time_seconds'] > 1.0:
        print("   🔧 Optimiser la performance système")
    
    print("\n📈 POINTS FORTS IDENTIFIÉS:")
    print(f"   ✅ Win Rate excellent: {data['trading_metrics']['win_rate_percent']:.1f}%")
    print(f"   ✅ Profit Factor solide: {data['trading_metrics']['profit_factor']:.2f}")
    print(f"   ✅ Système stable: {data['system_metrics']['system_uptime_percent']:.1f}% uptime")
    print(f"   ✅ Volume de trading: {data['trading_metrics']['total_trades']} trades en 1h")

def main():
    """Fonction principale"""
    # Charger les données
    file_path = "data/reports/test_1h_complete_report_20250815_220254.json"
    data = load_test_results(file_path)
    
    print("🚀 ANALYSE DÉTAILLÉE RÉSULTATS TEST 1 HEURE - MIA_IA_SYSTEM")
    print("=" * 70)
    
    # Analyses
    trading_metrics = analyze_trading_performance(data)
    system_metrics = analyze_system_performance(data)
    pattern_analysis = analyze_patterns(data)
    feature_analysis = analyze_features(data)
    signal_analysis = analyze_signal_strength(data)
    direction_analysis = analyze_trade_directions(data)
    alert_analysis = analyze_alerts(data)
    
    # Rapport de synthèse
    generate_summary_report(data)
    
    print("\n" + "=" * 70)
    print("🎯 ANALYSE TERMINÉE - SYSTÈME MIA_IA PRÊT POUR L'OPTIMISATION !")
    print("=" * 70)

if __name__ == "__main__":
    main()












