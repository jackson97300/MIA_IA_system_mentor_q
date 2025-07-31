#!/usr/bin/env python3
"""
DATA COLLECTION MAIN - Point d'entrée principal pour la collection de données
Version: 3.0.0 - Compatible avec Phase 3B

USAGE:
    python data_collection_main.py --start      # Démarre la collection
    python data_collection_main.py --quality    # Analyse qualité données
    python data_collection_main.py --summary    # Génère rapport résumé
    python data_collection_main.py --status     # Statut de la collection
    python data_collection_main.py --export     # Export ML dataset
    python data_collection_main.py --organize   # Organisation des données
    python data_collection_main.py --analyze    # Analytics complet
"""

import argparse
import sys
import os
import json
import logging
import signal
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import time

# === IMPORTS NUMPY ===
import numpy as np

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports locaux
from data.data_collector import DataCollector, DataQuality, DataPeriod
from data.analytics import DataAnalytics, AnalysisType, TimeFrame
from monitoring.performance_tracker import PerformanceTracker
from monitoring.alert_system import AlertSystem, AlertLevel
from config.automation_config import get_automation_config
from core.logger import setup_logging

# Configuration logging
logger = setup_logging(__name__)

# === COLLECTOR MANAGER ===

class DataCollectionManager:
    """Manager principal pour la collection de données"""
    
    def __init__(self):
        """Initialisation du manager"""
        self.config = get_automation_config()
        self.collector = DataCollector(self.config)
        self.analytics = DataAnalytics()
        self.performance_tracker = PerformanceTracker()
        self.alert_system = AlertSystem()
        
        # État de collection
        self.is_collecting = False
        self.collection_start_time = None
        self.snapshots_collected = 0
        self.last_organization_time = datetime.now()
        
        # Configuration signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("DataCollectionManager initialisé")
    
    def _signal_handler(self, sig, frame):
        """Gestion des signaux système"""
        logger.info(f"Signal {sig} reçu, arrêt propre...")
        self.stop_collection()
        sys.exit(0)
    
    # === COMMANDES PRINCIPALES ===
    
    def start_collection(self, duration_hours: Optional[int] = None):
        """
        Démarre la collection de données
        
        Args:
            duration_hours: Durée en heures (None = infini)
        """
        try:
            logger.info(f"Démarrage collection de données (durée: {duration_hours}h)")
            self.is_collecting = True
            self.collection_start_time = datetime.now(timezone.utc)
            end_time = None
            
            if duration_hours:
                end_time = self.collection_start_time + timedelta(hours=duration_hours)
            
            # Boucle de collection
            while self.is_collecting:
                # Vérifier durée
                if end_time and datetime.now(timezone.utc) >= end_time:
                    logger.info("Durée de collection atteinte")
                    break
                
                # Simuler collection depuis trade_snapshotter
                # En production, ceci lirait les vrais snapshots
                self._simulate_snapshot_collection()
                
                # Organisation périodique
                if (datetime.now() - self.last_organization_time).total_seconds() > 3600:  # 1h
                    self._organize_data()
                    self.last_organization_time = datetime.now()
                
                # Pause courte
                time.sleep(1)
            
            # Finalisation
            self._finalize_collection()
            
        except Exception as e:
            logger.error(f"Erreur collection: {e}")
            self.alert_system.send_alert(
                level=AlertLevel.ERROR,
                title="Erreur Collection Données",
                message=str(e)
            )
    
    def stop_collection(self):
        """Arrête la collection de données"""
        logger.info("Arrêt de la collection...")
        self.is_collecting = False
        
        # Sauvegarder données en cours
        self._finalize_collection()
        
        # Générer rapport final
        stats = self.collector.get_collection_statistics()
        logger.info(f"Collection terminée: {stats['collection_stats']['snapshots_processed']} snapshots")
    
    def analyze_data_quality(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyse la qualité des données collectées
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Rapport de qualité
        """
        logger.info(f"Analyse qualité données sur {days} jours...")
        
        # Dates d'analyse
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Chargement données
        snapshots_df = self._load_snapshots_data(start_date, end_date)
        
        if snapshots_df.empty:
            return {
                'status': 'no_data',
                'message': 'Aucune donnée trouvée pour la période'
            }
        
        # Analyses qualité
        quality_report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'data_volume': {
                'total_snapshots': len(snapshots_df),
                'daily_average': len(snapshots_df) / days,
                'unique_trades': snapshots_df['trade_id'].nunique() if 'trade_id' in snapshots_df else 0
            },
            'completeness': self._analyze_completeness(snapshots_df),
            'consistency': self._analyze_consistency(snapshots_df),
            'anomalies': self._detect_anomalies(snapshots_df),
            'recommendations': []
        }
        
        # Score global
        quality_score = self._calculate_quality_score(quality_report)
        quality_report['quality_score'] = quality_score
        quality_report['quality_level'] = self._get_quality_level(quality_score)
        
        # Recommandations
        if quality_score < 0.85:
            quality_report['recommendations'] = self._generate_quality_recommendations(quality_report)
        
        # Sauvegarde rapport
        self._save_quality_report(quality_report)
        
        return quality_report
    
    def generate_summary(self, period: str = "daily") -> Dict[str, Any]:
        """
        Génère un rapport résumé
        
        Args:
            period: Période du rapport (daily/weekly/monthly)
            
        Returns:
            Rapport résumé
        """
        logger.info(f"Génération rapport {period}...")
        
        # Configuration période
        if period == "daily":
            days = 1
            time_frame = TimeFrame.DAILY
        elif period == "weekly":
            days = 7
            time_frame = TimeFrame.WEEKLY
        elif period == "monthly":
            days = 30
            time_frame = TimeFrame.MONTHLY
        else:
            days = 1
            time_frame = TimeFrame.DAILY
        
        # Dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Génération rapport analytics
        report = self.analytics.generate_comprehensive_report(
            start_date=start_date,
            end_date=end_date,
            time_frame=time_frame
        )
        
        # Ajout statistiques collection
        collection_stats = self.collector.get_collection_statistics()
        
        summary = {
            'report_id': report.report_id,
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'data_collection': {
                'snapshots_collected': collection_stats['collection_stats']['snapshots_processed'],
                'storage_usage_mb': collection_stats['storage_usage']['total_mb'],
                'quality_distribution': collection_stats['data_quality_summary']['distribution']
            },
            'performance': {
                'total_trades': report.total_records,
                'win_rate': report.performance.win_rate if report.performance else 0,
                'avg_pnl': report.performance.avg_pnl if report.performance else 0,
                'sharpe_ratio': report.performance.sharpe_ratio if report.performance else 0
            },
            'insights': report.insights[:5] if report.insights else [],
            'warnings': report.warnings[:3] if report.warnings else []
        }
        
        # Sauvegarde
        self._save_summary_report(summary)
        
        return summary
    
    def get_status(self) -> Dict[str, Any]:
        """Obtient le statut actuel de la collection"""
        stats = self.collector.get_collection_statistics()
        
        status = {
            'is_collecting': self.is_collecting,
            'session': {
                'id': stats['session_metadata']['session_id'],
                'start_time': stats['session_metadata']['start_time'].isoformat(),
                'duration_minutes': (datetime.now(timezone.utc) - stats['session_metadata']['start_time']).total_seconds() / 60,
                'snapshots_collected': stats['session_metadata']['snapshots_collected']
            },
            'storage': {
                'total_mb': stats['storage_usage']['total_mb'],
                'daily_mb': stats['storage_usage']['daily_mb'],
                'ml_ready_mb': stats['storage_usage']['ml_mb']
            },
            'quality': stats['data_quality_summary'],
            'recent_activity': stats['recent_activity']
        }
        
        return status
    
    def export_ml_dataset(self, days: int = 30) -> bool:
        """
        Export un dataset ML
        
        Args:
            days: Nombre de jours de données
            
        Returns:
            Succès de l'export
        """
        logger.info(f"Export dataset ML ({days} jours)...")
        
        try:
            # Dates
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Export via collector
            dataset = self.collector.export_ml_training_dataset(start_date, end_date)
            
            if dataset:
                logger.info(f"Dataset ML exporté: {len(dataset.features)} échantillons, {len(dataset.feature_names)} features")
                
                # Notification
                self.alert_system.send_alert(
                    level=AlertLevel.INFO,
                    title="Export ML Dataset",
                    message=f"Dataset exporté avec succès: {len(dataset.features)} échantillons"
                )
                
                return True
            else:
                logger.warning("Aucune donnée ML à exporter")
                return False
                
        except Exception as e:
            logger.error(f"Erreur export ML: {e}")
            return False
    
    def organize_data(self, force: bool = False):
        """
        Organisation des données
        
        Args:
            force: Forcer l'organisation même si récente
        """
        logger.info("Organisation des données...")
        
        # Vérifier si nécessaire
        if not force:
            last_org = self.last_organization_time
            if (datetime.now() - last_org).total_seconds() < 3600:  # 1h
                logger.info("Organisation récente, ignorée (use --force pour forcer)")
                return
        
        # Organisation par période
        today = datetime.now().date()
        
        # Daily
        success_daily = self.collector.organize_daily_data(today)
        logger.info(f"Organisation daily: {'✓' if success_daily else '✗'}")
        
        # Weekly (dimanche)
        if today.weekday() == 6:
            success_weekly = self.collector.organize_weekly_data(today)
            logger.info(f"Organisation weekly: {'✓' if success_weekly else '✗'}")
        
        # Monthly (1er du mois)
        if today.day == 1:
            success_monthly = self.collector.organize_monthly_data(today)
            logger.info(f"Organisation monthly: {'✓' if success_monthly else '✗'}")
        
        # Archivage vieilles données (si la méthode existe)
        if hasattr(self.collector, 'archive_old_data'):
            self.collector.archive_old_data(days_to_keep=30)
        
        self.last_organization_time = datetime.now()
        logger.info("Organisation terminée")
    
    def run_analytics(self, comprehensive: bool = False):
        """
        Lance une analyse complète
        
        Args:
            comprehensive: Analyse approfondie
        """
        logger.info(f"Lancement analytics {'complet' if comprehensive else 'standard'}...")
        
        # Configuration analyse
        if comprehensive:
            days = 30
            analysis_type = AnalysisType.COMPREHENSIVE
        else:
            days = 7
            analysis_type = AnalysisType.PERFORMANCE
        
        # Dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Génération rapport
        report = self.analytics.generate_report(
            start_date=start_date,
            end_date=end_date,
            time_frame=TimeFrame.ALL_TIME
        )
        
        # Affichage résultats
        print("\n" + "="*50)
        print(f"📊 RAPPORT ANALYTICS - {report.report_id}")
        print("="*50)
        
        if report.performance:
            print(f"\n📈 PERFORMANCE:")
            print(f"  • Trades: {report.total_records}")
            print(f"  • Win Rate: {report.performance.win_rate:.1%}")
            print(f"  • PnL Moyen: ${report.performance.avg_pnl:.2f}")
            print(f"  • Sharpe Ratio: {report.performance.sharpe_ratio:.2f}")
        
        if report.patterns:
            print(f"\n🎯 PATTERNS DÉTECTÉS:")
            for pattern in report.patterns[:5]:
                print(f"  • {pattern}")
        
        if report.insights:
            print(f"\n💡 INSIGHTS:")
            for insight in report.insights[:5]:
                print(f"  • {insight}")
        
        if report.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in report.warnings[:3]:
                print(f"  • {warning}")
        
        print("\n" + "="*50)
        
        # Sauvegarde rapport complet
        self.analytics.save_report(report)
        logger.info(f"Rapport sauvegardé: {report.report_id}")
    
    # === MÉTHODES HELPER ===
    
    def _simulate_snapshot_collection(self):
        """Simule la collection de snapshots (pour tests)"""
        # En production, ceci lirait les vrais snapshots depuis trade_snapshotter
        snapshot = {
            # Ajout de champs pour les nouvelles analyses
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'snapshot_type': 'decision',
            'trade_id': f'SIM_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'market_snapshot': {
                'close': 4500.0 + (self.snapshots_collected % 100) * 0.25,
                'atr_14': 15.5 + (self.snapshots_collected % 20) * 0.5,
                'trend_strength': 0.7,
                'volume_relative': 1.0 + (self.snapshots_collected % 10) * 0.1
            },
            'battle_navale_result': {
                'battle_navale_signal': 0.8 if self.snapshots_collected % 5 == 0 else 0.2,
                'battle_strength': 0.6,
                'signal_strength': 0.3 + (self.snapshots_collected % 10) * 0.07
            },
            'execution_metrics': {
                'execution_time_ms': 5 + (self.snapshots_collected % 10),
                'slippage_ticks': 0 if self.snapshots_collected % 3 == 0 else 1
            },
            'pnl': np.random.normal(50, 100) if self.snapshots_collected % 5 == 0 else np.random.normal(-30, 50)
        }
        
        # Collection
        success = self.collector.collect_trade_snapshot(snapshot)
        if success:
            self.snapshots_collected += 1
    
    def _organize_data(self):
        """Organisation périodique des données"""
        today = datetime.now().date()
        self.collector.organize_daily_data(today)
    
    def _finalize_collection(self):
        """Finalise la session de collection"""
        if self.collection_start_time:
            duration = datetime.now(timezone.utc) - self.collection_start_time
            logger.info(f"Session terminée - Durée: {duration}, Snapshots: {self.snapshots_collected}")
    
    def _load_snapshots_data(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Charge les données de snapshots"""
        try:
            all_data = []
            current_date = start_date
            
            while current_date <= end_date:
                file_path = self.collector.daily_path / f"trades_{current_date.strftime('%Y%m%d')}.json"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        all_data.extend(data)
                current_date += timedelta(days=1)
            
            if all_data:
                return pd.DataFrame(all_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Erreur chargement données: {e}")
            return pd.DataFrame()
    
    def _analyze_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyse la complétude des données"""
        required_fields = [
            'timestamp', 'trade_id', 'snapshot_type',
            'market_snapshot', 'battle_navale_result'
        ]
        
        completeness = {}
        for field in required_fields:
            if field in df.columns:
                non_null = df[field].notna().sum()
                completeness[field] = non_null / len(df) if len(df) > 0 else 0
            else:
                completeness[field] = 0.0
        
        completeness['overall'] = sum(completeness.values()) / len(completeness)
        return completeness
    
    def _analyze_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse la cohérence des données"""
        consistency = {
            'timestamp_order': True,
            'duplicate_trades': 0,
            'invalid_values': 0
        }
        
        if not df.empty and 'timestamp' in df.columns:
            # Vérifier ordre temporel
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            consistency['timestamp_order'] = df['timestamp'].is_monotonic_increasing
            
            # Vérifier duplicatas
            if 'trade_id' in df.columns:
                consistency['duplicate_trades'] = df['trade_id'].duplicated().sum()
        
        return consistency
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[str]:
        """Détecte les anomalies dans les données"""
        anomalies = []
        
        if df.empty:
            return anomalies
        
        # Vérifier gaps temporels
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            time_diff = df['timestamp'].diff()
            large_gaps = time_diff[time_diff > pd.Timedelta(hours=1)]
            if len(large_gaps) > 0:
                anomalies.append(f"{len(large_gaps)} gaps temporels > 1h détectés")
        
        # Vérifier valeurs extrêmes
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].std() > 0:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = (z_scores > 3).sum()
                if outliers > 0:
                    anomalies.append(f"{outliers} outliers détectés dans {col}")
        
        return anomalies
    
    def _calculate_quality_score(self, report: Dict[str, Any]) -> float:
        """Calcule un score de qualité global"""
        score = 0.0
        weights = {
            'completeness': 0.4,
            'consistency': 0.3,
            'volume': 0.2,
            'anomalies': 0.1
        }
        
        # Complétude
        if 'completeness' in report:
            score += report['completeness'].get('overall', 0) * weights['completeness']
        
        # Cohérence
        if 'consistency' in report:
            consistency_score = 1.0
            if not report['consistency']['timestamp_order']:
                consistency_score -= 0.3
            if report['consistency']['duplicate_trades'] > 0:
                consistency_score -= 0.2
            score += consistency_score * weights['consistency']
        
        # Volume
        if 'data_volume' in report:
            volume_score = min(report['data_volume']['daily_average'] / 100, 1.0)
            score += volume_score * weights['volume']
        
        # Anomalies
        if 'anomalies' in report:
            anomaly_score = max(0, 1.0 - len(report['anomalies']) * 0.1)
            score += anomaly_score * weights['anomalies']
        
        return min(max(score, 0.0), 1.0)
    
    def _get_quality_level(self, score: float) -> str:
        """Détermine le niveau de qualité"""
        if score >= 0.95:
            return "EXCELLENT"
        elif score >= 0.85:
            return "GOOD"
        elif score >= 0.70:
            return "ACCEPTABLE"
        elif score >= 0.50:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _generate_quality_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        # Complétude
        if report['completeness']['overall'] < 0.9:
            recommendations.append("Améliorer la capture des champs obligatoires")
        
        # Cohérence
        if report['consistency']['duplicate_trades'] > 0:
            recommendations.append("Implémenter la déduplication des trades")
        
        # Volume
        if report['data_volume']['daily_average'] < 50:
            recommendations.append("Augmenter la fréquence de trading pour plus de données")
        
        # Anomalies
        if len(report['anomalies']) > 2:
            recommendations.append("Investiguer et corriger les anomalies détectées")
        
        return recommendations
    
    def _save_quality_report(self, report: Dict[str, Any]):
        """Sauvegarde le rapport qualité"""
        try:
            reports_dir = Path("reports/quality")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = reports_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Rapport qualité sauvegardé: {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde rapport qualité: {e}")
    
    def _save_summary_report(self, summary: Dict[str, Any]):
        """Sauvegarde le rapport résumé"""
        try:
            reports_dir = Path("reports/summary")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"summary_{summary['period']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = reports_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Rapport résumé sauvegardé: {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde rapport résumé: {e}")

# === MAIN FUNCTION ===

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="MIA_IA_SYSTEM - Data Collection Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python data_collection_main.py --start            # Démarre collection continue
  python data_collection_main.py --start --hours 24 # Collection 24h
  python data_collection_main.py --quality          # Analyse qualité
  python data_collection_main.py --summary daily    # Rapport quotidien
  python data_collection_main.py --export --days 30 # Export ML 30 jours
  python data_collection_main.py --analyze          # Analytics complet
        """
    )
    
    # Arguments
    parser.add_argument('--start', action='store_true',
                       help='Démarre la collection de données')
    parser.add_argument('--stop', action='store_true',
                       help='Arrête la collection')
    parser.add_argument('--hours', type=int,
                       help='Durée de collection en heures')
    parser.add_argument('--quality', action='store_true',
                       help='Analyse la qualité des données')
    parser.add_argument('--days', type=int, default=7,
                       help='Nombre de jours pour analyse (défaut: 7)')
    parser.add_argument('--summary', nargs='?', const='daily',
                       choices=['daily', 'weekly', 'monthly'],
                       help='Génère un rapport résumé')
    parser.add_argument('--status', action='store_true',
                       help='Affiche le statut de collection')
    parser.add_argument('--export', action='store_true',
                       help='Export dataset ML')
    parser.add_argument('--organize', action='store_true',
                       help='Organisation des données')
    parser.add_argument('--force', action='store_true',
                       help='Force l\'action même si récente')
    parser.add_argument('--analyze', action='store_true',
                       help='Lance analytics complet')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Analyse approfondie')
    
    args = parser.parse_args()
    
    # Vérification arguments
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Initialisation manager
    manager = DataCollectionManager()
    
    try:
        # Exécution commandes
        if args.start:
            manager.start_collection(duration_hours=args.hours)
        
        elif args.stop:
            manager.stop_collection()
        
        elif args.quality:
            report = manager.analyze_data_quality(days=args.days)
            print(f"\n[RAPPORT QUALITÉ DONNÉES]")
            
            if report.get('status') == 'no_data':
                print(f"Status: {report.get('status')}")
                print(f"Message: {report.get('message', 'Aucune donnée trouvée')}")
            else:
                print(f"Période: {report.get('period', {}).get('start', 'N/A')} à {report.get('period', {}).get('end', 'N/A')}")
                print(f"Score Qualité: {report.get('quality_score', 0):.2%} - {report.get('quality_level', 'N/A')}")
                
                data_volume = report.get('data_volume', {})
                print(f"Snapshots: {data_volume.get('total_snapshots', 0)}")
                
                if report.get('recommendations'):
                    print("\n[Recommandations]:")
                    for rec in report['recommendations']:
                        print(f"  • {rec}")
        
        elif args.summary:
            summary = manager.generate_summary(period=args.summary)
            print(f"\n[RÉSUMÉ {args.summary.upper()}]")
            print(f"Période: {summary.get('period', 'N/A')}")
            
            data_collection = summary.get('data_collection', {})
            print(f"Snapshots: {data_collection.get('snapshots_collected', 0)}")
            
            performance = summary.get('performance', {})
            print(f"Win Rate: {performance.get('win_rate', 0):.1%}")
            print(f"PnL Moyen: ${performance.get('avg_pnl', 0):.2f}")
            print(f"Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        
        elif args.status:
            status = manager.get_status()
            print(f"\n[STATUT COLLECTION]")
            print(f"En cours: {'OUI' if status['is_collecting'] else 'NON'}")
            print(f"Session: {status['session']['id']}")
            print(f"Durée: {status['session']['duration_minutes']:.1f} minutes")
            print(f"Snapshots: {status['session']['snapshots_collected']}")
            print(f"Stockage: {status['storage']['total_mb']:.1f} MB")
            print(f"Qualité: {status['quality']['overall_quality']}")
        
        elif args.export:
            success = manager.export_ml_dataset(days=args.days)
            if success:
                print(f"[OK] Dataset ML exporté avec succès ({args.days} jours)")
            else:
                print("[X] Échec export dataset ML")
        
        elif args.organize:
            manager.organize_data(force=args.force)
            print("[OK] Organisation des données terminée")
        
        elif args.analyze:
            manager.run_analytics(comprehensive=args.comprehensive)
        
    except KeyboardInterrupt:
        print("\n[!] Interruption utilisateur")
        manager.stop_collection()
    except Exception as e:
        print(f"\n[X] Erreur: {e}")
        logger.error(f"Erreur non gérée: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()