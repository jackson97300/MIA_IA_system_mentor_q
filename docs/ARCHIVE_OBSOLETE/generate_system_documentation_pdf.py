#!/usr/bin/env python3
"""
Générateur de Documentation PDF - MIA_IA_SYSTEM
Génère les PDF de l'architecture et des fonctionnalités
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

def create_architecture_pdf():
    """Créer le PDF de l'architecture du système"""
    
    # Nom du fichier PDF
    pdf_filename = f"ARCHITECTURE_DETAILLEE_MIA_IA_SYSTEM_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Créer le document PDF
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Style sous-titre
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkgreen
    )
    
    # Style normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12
    )
    
    # Style liste
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leftIndent=20
    )
    
    # Titre principal
    story.append(Paragraph("🏗️ ARCHITECTURE DÉTAILLÉE MIA_IA_SYSTEM", title_style))
    story.append(Paragraph("📋 DOCUMENTATION COMPLÈTE DES FICHIERS", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Vue d'ensemble
    story.append(Paragraph("🎯 VUE D'ENSEMBLE DU SYSTÈME", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    overview_data = [
        ["Version", "3.1.0"],
        ["Architecture", "Modulaire et Scalable"],
        ["Langage", "Python 3.8+"],
        ["Framework", "Asyncio + Multi-threading"],
        ["Broker", "Interactive Brokers (IBKR)"],
        ["Plateforme", "Sierra Chart + IB Gateway"]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 3*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
    ]))
    
    story.append(overview_table)
    story.append(Spacer(1, 20))
    
    # Structure des dossiers
    story.append(Paragraph("📁 STRUCTURE DES DOSSIERS PRINCIPAUX", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Core
    story.append(Paragraph("🔧 CORE/ - Cœur du Système", styles['Heading3']))
    story.append(Paragraph("Fichiers Principaux :", normal_style))
    
    core_files = [
        ["battle_navale.py", "67KB, 3169 lignes", "Moteur principal du système de trading"],
        ["ibkr_connector.py", "61KB, 1699 lignes", "Connecteur principal vers Interactive Brokers"],
        ["sierra_connector.py", "36KB, 1091 lignes", "Interface avec Sierra Chart"],
        ["patterns_detector.py", "31KB, 842 lignes", "Détection de patterns de marché"],
        ["mentor_system.py", "37KB, 828 lignes", "Système d'apprentissage et optimisation"],
        ["catastrophe_monitor.py", "14KB, 340 lignes", "Surveillance et sécurité"],
        ["safety_kill_switch.py", "5.7KB, 149 lignes", "Système de sécurité"],
        ["logger.py", "12KB, 375 lignes", "Système de logging"],
        ["base_types.py", "34KB, 1076 lignes", "Types de données de base"],
        ["structure_data.py", "37KB, 1049 lignes", "Gestion des structures de données"]
    ]
    
    core_table = Table(core_files, colWidths=[2*inch, 1*inch, 3*inch])
    core_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(core_table)
    story.append(Spacer(1, 20))
    
    # Execution
    story.append(Paragraph("⚡ EXECUTION/ - Exécution des Ordres", styles['Heading3']))
    story.append(Paragraph("Fichiers Principaux :", normal_style))
    
    execution_files = [
        ["simple_trader.py", "90KB, 3917 lignes", "Trader principal du système"],
        ["order_manager.py", "67KB, 3219 lignes", "Gestion des ordres"],
        ["risk_manager.py", "31KB, 852 lignes", "Gestion des risques"],
        ["trade_snapshotter.py", "63KB, 1582 lignes", "Capture des trades"],
        ["post_mortem_analyzer.py", "25KB, 634 lignes", "Analyse post-mortem"]
    ]
    
    execution_table = Table(execution_files, colWidths=[2*inch, 1*inch, 3*inch])
    execution_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(execution_table)
    story.append(Spacer(1, 20))
    
    # ML
    story.append(Paragraph("🧠 ML/ - Machine Learning", styles['Heading3']))
    story.append(Paragraph("Fichiers Principaux :", normal_style))
    
    ml_files = [
        ["ensemble_filter.py", "29KB, 1494 lignes", "Filtre d'ensemble ML"],
        ["model_trainer.py", "47KB, 1227 lignes", "Entraînement des modèles"],
        ["model_validator.py", "48KB, 1233 lignes", "Validation des modèles"],
        ["data_processor.py", "43KB, 1116 lignes", "Traitement des données"],
        ["simple_model.py", "27KB, 699 lignes", "Modèles simples"],
        ["gamma_cycles.py", "24KB, 649 lignes", "Cycles gamma"]
    ]
    
    ml_table = Table(ml_files, colWidths=[2*inch, 1*inch, 3*inch])
    ml_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(ml_table)
    story.append(Spacer(1, 20))
    
    # Features
    story.append(Paragraph("📊 FEATURES/ - Analyse des Features", styles['Heading3']))
    story.append(Paragraph("Fichiers Principaux :", normal_style))
    
    features_files = [
        ["confluence_analyzer.py", "52KB, 1301 lignes", "Analyse de confluence"],
        ["feature_calculator.py", "58KB, 1364 lignes", "Calcul des features"],
        ["mtf_confluence_elite.py", "24KB, 1168 lignes", "Confluence multi-timeframe"],
        ["smart_money_tracker.py", "36KB, 888 lignes", "Suivi smart money"],
        ["market_regime.py", "48KB, 1308 lignes", "Régimes de marché"],
        ["order_book_imbalance.py", "21KB, 584 lignes", "Déséquilibre order book"]
    ]
    
    features_table = Table(features_files, colWidths=[2*inch, 1*inch, 3*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(features_table)
    story.append(Spacer(1, 20))
    
    # Monitoring
    story.append(Paragraph("📡 MONITORING/ - Surveillance", styles['Heading3']))
    story.append(Paragraph("Fichiers Principaux :", normal_style))
    
    monitoring_files = [
        ["health_checker.py", "88KB, 2173 lignes", "Vérification de santé"],
        ["alert_system.py", "61KB, 1541 lignes", "Système d'alertes"],
        ["discord_notifier.py", "42KB, 898 lignes", "Notifications Discord"],
        ["live_monitor.py", "45KB, 1117 lignes", "Monitoring en temps réel"],
        ["performance_tracker.py", "44KB, 1118 lignes", "Suivi des performances"],
        ["session_replay.py", "22KB, 568 lignes", "Replay de sessions"],
        ["ib_gateway_monitor.py", "7.7KB, 205 lignes", "Monitoring IB Gateway"]
    ]
    
    monitoring_table = Table(monitoring_files, colWidths=[2*inch, 1*inch, 3*inch])
    monitoring_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkpurple),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(monitoring_table)
    story.append(Spacer(1, 20))
    
    # Métriques du système
    story.append(Paragraph("📈 MÉTRIQUES DU SYSTÈME", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    metrics_data = [
        ["Métrique", "Valeur", "Description"],
        ["Lignes de code", "~150,000", "Code total du système"],
        ["Fichiers Python", "~200", "Nombre de fichiers"],
        ["Modules principaux", "15", "Modules principaux"],
        ["Classes principales", "~100", "Classes principales"],
        ["Architecture", "Modulaire", "Type d'architecture"],
        ["Scalabilité", "Haute", "Capacité de scalabilité"],
        ["Maintenabilité", "Excellente", "Facilité de maintenance"],
        ["Extensibilité", "Très bonne", "Capacité d'extension"]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2*inch, 1*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    story.append(Paragraph("Document généré automatiquement par MIA_IA_SYSTEM", footer_style))
    story.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))
    story.append(Paragraph("Version : 3.1.0", footer_style))
    
    # Générer le PDF
    doc.build(story)
    
    print(f"✅ Architecture PDF généré : {pdf_filename}")
    return pdf_filename

def create_functionalities_pdf():
    """Créer le PDF des fonctionnalités du système"""
    
    # Nom du fichier PDF
    pdf_filename = f"FONCTIONNALITES_DETAILLEES_MIA_IA_SYSTEM_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Créer le document PDF
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Style sous-titre
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkgreen
    )
    
    # Style normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12
    )
    
    # Style liste
    list_style = ParagraphStyle(
        'CustomList',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leftIndent=20
    )
    
    # Titre principal
    story.append(Paragraph("🤖 FONCTIONNALITÉS DÉTAILLÉES MIA_IA_SYSTEM", title_style))
    story.append(Paragraph("📋 DOCUMENTATION COMPLÈTE DES FEATURES ET STRATÉGIES", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Vue d'ensemble
    story.append(Paragraph("🎯 VUE D'ENSEMBLE DES FONCTIONNALITÉS", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    overview_data = [
        ["Système", "MIA_IA_SYSTEM v3.1.0"],
        ["Type", "Bot de Trading Automatisé"],
        ["Instruments", "Futures ES/NQ, Options, Actions"],
        ["Timeframes", "1min à 4H"],
        ["Brokers", "Interactive Brokers (IBKR)"],
        ["Plateformes", "Sierra Chart + IB Gateway"]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 3*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
    ]))
    
    story.append(overview_table)
    story.append(Spacer(1, 20))
    
    # Fonctionnalités Core
    story.append(Paragraph("🔧 FONCTIONNALITÉS CORE", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🧠 Système d'Intelligence Artificielle", styles['Heading3']))
    story.append(Paragraph("1. Mentor System (mentor_system.py)", normal_style))
    story.append(Paragraph("• Apprentissage automatique", list_style))
    story.append(Paragraph("• Optimisation des stratégies", list_style))
    story.append(Paragraph("• Analyse de performance", list_style))
    story.append(Paragraph("• Adaptation continue", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("2. Pattern Detector (patterns_detector.py)", normal_style))
    story.append(Paragraph("• Patterns de prix (triangles, flags, H&S)", list_style))
    story.append(Paragraph("• Patterns de volume", list_style))
    story.append(Paragraph("• Patterns de momentum", list_style))
    story.append(Paragraph("• Reconnaissance automatique", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3. Catastrophe Monitor (catastrophe_monitor.py)", normal_style))
    story.append(Paragraph("• Surveillance continue", list_style))
    story.append(Paragraph("• Gestion des catastrophes", list_style))
    story.append(Paragraph("• Système de sécurité", list_style))
    story.append(Paragraph("• Recovery automatique", list_style))
    story.append(Spacer(1, 20))
    
    # Features d'analyse
    story.append(Paragraph("📊 FEATURES D'ANALYSE AVANCÉES", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🎯 Confluence Analyzer (confluence_analyzer.py)", styles['Heading3']))
    story.append(Paragraph("• Analyse de confluence multi-timeframe", list_style))
    story.append(Paragraph("• Support/Résistance automatique", list_style))
    story.append(Paragraph("• Smart money zones", list_style))
    story.append(Paragraph("• Scoring de probabilité", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🧮 Feature Calculator (feature_calculator.py)", styles['Heading3']))
    story.append(Paragraph("• Indicateurs techniques (RSI, MACD, Bollinger)", list_style))
    story.append(Paragraph("• Price action analysis", list_style))
    story.append(Paragraph("• Market structure", list_style))
    story.append(Paragraph("• Volume analysis", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🎯 Smart Money Tracker (smart_money_tracker.py)", styles['Heading3']))
    story.append(Paragraph("• Détection smart money", list_style))
    story.append(Paragraph("• Flux institutionnels", list_style))
    story.append(Paragraph("• Patterns Wyckoff", list_style))
    story.append(Paragraph("• Order flow analysis", list_style))
    story.append(Spacer(1, 20))
    
    # Stratégies de trading
    story.append(Paragraph("🎯 STRATÉGIES DE TRADING", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("📈 Trend Strategy (trend_strategy.py)", styles['Heading3']))
    story.append(Paragraph("• Détection de tendance", list_style))
    story.append(Paragraph("• Entrées pullback/breakout", list_style))
    story.append(Paragraph("• Stop-loss ATR-based", list_style))
    story.append(Paragraph("• Take-profit dynamique", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("📊 Range Strategy (range_strategy.py)", styles['Heading3']))
    story.append(Paragraph("• Trading en range", list_style))
    story.append(Paragraph("• Entrées bounce/fade", list_style))
    story.append(Paragraph("• Position sizing Kelly", list_style))
    story.append(Paragraph("• Mean reversion", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🎲 Strategy Selector (strategy_selector.py)", styles['Heading3']))
    story.append(Paragraph("• Sélection automatique", list_style))
    story.append(Paragraph("• Adaptation au marché", list_style))
    story.append(Paragraph("• Optimisation continue", list_style))
    story.append(Paragraph("• Performance tracking", list_style))
    story.append(Spacer(1, 20))
    
    # Machine Learning
    story.append(Paragraph("🧠 MACHINE LEARNING", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🤖 Ensemble Filter (ensemble_filter.py)", styles['Heading3']))
    story.append(Paragraph("• Random Forest", list_style))
    story.append(Paragraph("• Gradient Boosting (XGBoost, LightGBM)", list_style))
    story.append(Paragraph("• Neural Networks (LSTM, CNN)", list_style))
    story.append(Paragraph("• Filtrage de signaux", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🎯 Model Trainer (model_trainer.py)", styles['Heading3']))
    story.append(Paragraph("• Entraînement avancé", list_style))
    story.append(Paragraph("• Hyperparameter optimization", list_style))
    story.append(Paragraph("• Validation croisée", list_style))
    story.append(Paragraph("• Performance metrics", list_style))
    story.append(Spacer(1, 20))
    
    # Monitoring
    story.append(Paragraph("📡 SYSTÈME DE MONITORING", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🏥 Health Checker (health_checker.py)", styles['Heading3']))
    story.append(Paragraph("• Surveillance système", list_style))
    story.append(Paragraph("• Connexions IBKR/Sierra", list_style))
    story.append(Paragraph("• Performance monitoring", list_style))
    story.append(Paragraph("• Alertes automatiques", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🚨 Alert System (alert_system.py)", styles['Heading3']))
    story.append(Paragraph("• Alertes trading", list_style))
    story.append(Paragraph("• Alertes risque", list_style))
    story.append(Paragraph("• Alertes système", list_style))
    story.append(Paragraph("• Channels Discord/Email", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("📱 Discord Notifier (discord_notifier.py)", styles['Heading3']))
    story.append(Paragraph("• Intégration Discord", list_style))
    story.append(Paragraph("• Messages riches", list_style))
    story.append(Paragraph("• Channels spécialisés", list_style))
    story.append(Paragraph("• Notifications push", list_style))
    story.append(Spacer(1, 20))
    
    # Exécution
    story.append(Paragraph("⚡ SYSTÈME D'EXÉCUTION", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🎯 Simple Trader (simple_trader.py)", styles['Heading3']))
    story.append(Paragraph("• Exécution automatique", list_style))
    story.append(Paragraph("• Gestion des stratégies", list_style))
    story.append(Paragraph("• Interface utilisateur", list_style))
    story.append(Paragraph("• Dashboard temps réel", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("📋 Order Manager (order_manager.py)", styles['Heading3']))
    story.append(Paragraph("• Types d'ordres avancés", list_style))
    story.append(Paragraph("• Validation et contrôles", list_style))
    story.append(Paragraph("• Risk checks", list_style))
    story.append(Paragraph("• Order validation", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🛡️ Risk Manager (risk_manager.py)", styles['Heading3']))
    story.append(Paragraph("• Position sizing", list_style))
    story.append(Paragraph("• Stop-loss management", list_style))
    story.append(Paragraph("• Contrôles de risque", list_style))
    story.append(Paragraph("• Drawdown protection", list_style))
    story.append(Spacer(1, 20))
    
    # Sécurité
    story.append(Paragraph("🔒 SÉCURITÉ ET FIABILITÉ", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🛡️ Systèmes de Sécurité", styles['Heading3']))
    story.append(Paragraph("• Kill switch automatique", list_style))
    story.append(Paragraph("• Protection du capital", list_style))
    story.append(Paragraph("• Limites de risque", list_style))
    story.append(Paragraph("• Arrêt d'urgence", list_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("🔄 Redundancy Systems", styles['Heading3']))
    story.append(Paragraph("• Backup systems", list_style))
    story.append(Paragraph("• System redundancy", list_style))
    story.append(Paragraph("• Failover procedures", list_style))
    story.append(Paragraph("• Recovery protocols", list_style))
    story.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    story.append(Paragraph("Document généré automatiquement par MIA_IA_SYSTEM", footer_style))
    story.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))
    story.append(Paragraph("Version : 3.1.0", footer_style))
    
    # Générer le PDF
    doc.build(story)
    
    print(f"✅ Fonctionnalités PDF généré : {pdf_filename}")
    return pdf_filename

def main():
    """Fonction principale"""
    try:
        print("🚀 Génération de la documentation MIA_IA_SYSTEM...")
        
        # Générer les deux PDF
        arch_pdf = create_architecture_pdf()
        func_pdf = create_functionalities_pdf()
        
        print(f"🎉 Documentation générée avec succès !")
        print(f"📄 Architecture : {arch_pdf}")
        print(f"📄 Fonctionnalités : {func_pdf}")
        print("✅ Documentation complète du système MIA_IA_SYSTEM créée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")

if __name__ == "__main__":
    main()
