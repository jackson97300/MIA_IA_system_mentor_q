#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Configuration Analyse Temps Réel
Configuration personnalisable pour l'analyse des résultats
"""

# Configuration générale
ANALYSIS_CONFIG = {
    'duration_minutes': 2,  # Durée d'analyse
    'check_interval_seconds': 10,  # Intervalle entre les vérifications
    'max_log_lines_per_check': 100,  # Nombre max de lignes à analyser par vérification
    'enable_real_time_display': True,  # Affichage en temps réel
    'save_report': True,  # Sauvegarder le rapport final
}

# Patterns de détection personnalisables
DETECTION_PATTERNS = {
    'trades': [
        'TRADE',
        'EXECUTION', 
        'FILL',
        'ORDER_FILLED',
        'TRADE_EXECUTED',
        'POSITION_OPENED',
        'POSITION_CLOSED'
    ],
    
    'signals': [
        'SIGNAL',
        'BUY',
        'SELL', 
        'LONG',
        'SHORT',
        'ENTRY_SIGNAL',
        'EXIT_SIGNAL',
        'STRATEGY_SIGNAL'
    ],
    
    'volume_issues': [
        'volume: 192.0',
        'Volume: 192',
        'volume constant',
        'volume unchanged',
        'volume static'
    ],
    
    'ohlc_issues': [
        'OHLC incohérent',
        'O=nan',
        'H=nan', 
        'L=nan',
        'C=nan',
        'OHLC invalid',
        'price data error',
        'market data error'
    ],
    
    'connection_issues': [
        'timeout',
        'connection',
        'disconnect',
        'reconnect',
        'connection lost',
        'network error',
        'api error',
        'gateway error'
    ],
    
    'performance_issues': [
        'slow',
        'latency',
        'delay',
        'timeout',
        'performance issue',
        'slow response',
        'high latency'
    ],
    
    'data_quality_issues': [
        'data quality',
        'invalid data',
        'corrupted data',
        'missing data',
        'data error'
    ]
}

# Seuils de qualité
QUALITY_THRESHOLDS = {
    'excellent_score': 90,
    'good_score': 70,
    'acceptable_score': 50,
    'poor_score': 25,
    
    'max_volume_issues': 5,
    'max_ohlc_issues': 3,
    'max_connection_issues': 2,
    'max_performance_issues': 3
}

# Fichiers de logs à surveiller
LOG_PATTERNS = [
    "logs/*.log",
    "*.log",
    "data/logs/*.log", 
    "monitoring/logs/*.log",
    "core/*.log",
    "execution/*.log",
    "strategies/*.log"
]

# Critères de validation pour le test 2h
VALIDATION_CRITERIA = {
    'min_trades': 1,
    'min_signals': 1,
    'max_volume_issues': 0,
    'max_ohlc_issues': 0,
    'max_connection_issues': 0,
    'min_quality_score': 90
}

# Messages personnalisés
MESSAGES = {
    'system_perfect': "✅ SYSTÈME PARFAIT - Prêt pour 2h",
    'system_functional': "⚠️ SYSTÈME FONCTIONNEL - Corrections mineures",
    'system_non_functional': "❌ SYSTÈME NON FONCTIONNEL",
    
    'ready_for_2h': "🎯 Tous les critères sont excellents",
    'needs_optimization': "🎯 Système actif mais optimisations recommandées",
    'needs_diagnosis': "🎯 Problèmes critiques détectés"
}

# Configuration d'affichage
DISPLAY_CONFIG = {
    'show_timestamps': True,
    'show_file_sources': True,
    'max_line_length': 80,
    'use_emojis': True,
    'color_output': True,
    'progress_bar': True
}

# Configuration de sauvegarde
SAVE_CONFIG = {
    'save_detailed_logs': True,
    'save_metrics_json': True,
    'save_report_html': False,
    'backup_previous_reports': True,
    'max_backup_files': 10
}


