"""
Exporteur de Métriques MIA_IA_SYSTEM
====================================

Export des métriques vers différents formats (CSV, JSON, Prometheus).
"""

import json
import csv
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

from .metrics_collector import get_metrics_collector
from core.logger import get_logger

logger = get_logger(__name__)


class MetricsExporter:
    """Exporteur de métriques vers différents formats"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger
        self.metrics_collector = get_metrics_collector()
        
        # Configuration
        self.export_dir = Path(self.config.get('export_dir', 'metrics/exports'))
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Formats supportés
        self.supported_formats = ['csv', 'json', 'prometheus']
    
    def export_csv(self, date: Optional[str] = None, filename: Optional[str] = None) -> str:
        """Exporte les métriques en CSV"""
        if not filename:
            if date:
                filename = f"metrics_{date}.csv"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"metrics_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # En-têtes
                writer.writerow([
                    'timestamp', 'name', 'value', 'labels', 'tags', 'type'
                ])
                
                # Données
                summary = self.metrics_collector.get_summary()
                
                # Compteurs
                for name, value in summary['counters'].items():
                    writer.writerow([
                        summary['timestamp'],
                        name,
                        value,
                        '{}',
                        '{"type": "counter"}',
                        'counter'
                    ])
                
                # Jauges
                for name, value in summary['gauges'].items():
                    writer.writerow([
                        summary['timestamp'],
                        name,
                        value,
                        '{}',
                        '{"type": "gauge"}',
                        'gauge'
                    ])
                
                # Histogrammes
                for name, stats in summary['histograms'].items():
                    writer.writerow([
                        summary['timestamp'],
                        name,
                        stats['avg'],
                        '{}',
                        json.dumps({
                            'type': 'histogram',
                            'count': stats['count'],
                            'min': stats['min'],
                            'max': stats['max']
                        }),
                        'histogram'
                    ])
            
            self.logger.info(f"📊 Métriques exportées en CSV: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erreur export CSV: {e}")
            return ""
    
    def export_json(self, date: Optional[str] = None, filename: Optional[str] = None) -> str:
        """Exporte les métriques en JSON"""
        if not filename:
            if date:
                filename = f"metrics_{date}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"metrics_{timestamp}.json"
        
        filepath = self.export_dir / filename
        
        try:
            # Obtenir le résumé complet
            summary = self.metrics_collector.get_summary()
            
            # Ajouter des métadonnées
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now(timezone.utc).isoformat(),
                    'date': date,
                    'format': 'json',
                    'version': '1.0'
                },
                'summary': summary,
                'counters': summary['counters'],
                'gauges': summary['gauges'],
                'histograms': summary['histograms']
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Métriques exportées en JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erreur export JSON: {e}")
            return ""
    
    def export_prometheus(self, port: int = 9090) -> bool:
        """Exporte les métriques via Prometheus"""
        try:
            # Démarrer le serveur Prometheus
            success = self.metrics_collector.start_prometheus_server(port)
            
            if success:
                self.logger.info(f"📊 Serveur Prometheus démarré sur port {port}")
                self.logger.info(f"📊 Métriques disponibles sur http://localhost:{port}/metrics")
            else:
                self.logger.error("Erreur démarrage serveur Prometheus")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erreur export Prometheus: {e}")
            return False
    
    def export_all_formats(self, date: Optional[str] = None) -> Dict[str, str]:
        """Exporte dans tous les formats supportés"""
        results = {}
        
        # CSV
        csv_file = self.export_csv(date)
        if csv_file:
            results['csv'] = csv_file
        
        # JSON
        json_file = self.export_json(date)
        if json_file:
            results['json'] = json_file
        
        # Prometheus (démarre le serveur)
        if self.export_prometheus():
            results['prometheus'] = f"http://localhost:9090/metrics"
        
        return results
    
    def get_export_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des exports disponibles"""
        try:
            export_files = list(self.export_dir.glob("metrics_*"))
            
            return {
                'export_dir': str(self.export_dir),
                'total_files': len(export_files),
                'formats': {
                    'csv': len(list(self.export_dir.glob("*.csv"))),
                    'json': len(list(self.export_dir.glob("*.json")))
                },
                'latest_files': [
                    {
                        'name': f.name,
                        'size': f.stat().st_size,
                        'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    }
                    for f in sorted(export_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Erreur résumé exports: {e}")
            return {}


def export_metrics(format: str = 'csv', date: Optional[str] = None, port: int = 9090) -> str:
    """
    Fonction utilitaire pour exporter les métriques
    
    Args:
        format: Format d'export ('csv', 'json', 'prometheus')
        date: Date pour le nom de fichier (YYYYMMDD)
        port: Port pour Prometheus
    
    Returns:
        Chemin du fichier exporté ou URL Prometheus
    """
    exporter = MetricsExporter()
    
    if format == 'csv':
        return exporter.export_csv(date)
    elif format == 'json':
        return exporter.export_json(date)
    elif format == 'prometheus':
        if exporter.export_prometheus(port):
            return f"http://localhost:{port}/metrics"
        else:
            return ""
    else:
        logger.error(f"Format non supporté: {format}")
        return ""


async def auto_export_metrics(interval_minutes: int = 60, formats: List[str] = None):
    """
    Export automatique des métriques
    
    Args:
        interval_minutes: Intervalle d'export en minutes
        formats: Formats à exporter (défaut: ['csv', 'json'])
    """
    if formats is None:
        formats = ['csv', 'json']
    
    exporter = MetricsExporter()
    logger.info(f"📊 Export automatique démarré (intervalle: {interval_minutes}min)")
    
    while True:
        try:
            # Export dans tous les formats demandés
            for format_type in formats:
                if format_type == 'csv':
                    exporter.export_csv()
                elif format_type == 'json':
                    exporter.export_json()
                elif format_type == 'prometheus':
                    exporter.export_prometheus()
            
            logger.info(f"📊 Export automatique terminé: {formats}")
            
            # Attendre l'intervalle
            await asyncio.sleep(interval_minutes * 60)
            
        except asyncio.CancelledError:
            logger.info("📊 Export automatique arrêté")
            break
        except Exception as e:
            logger.error(f"Erreur export automatique: {e}")
            await asyncio.sleep(60)  # Attendre 1 minute avant de réessayer


if __name__ == "__main__":
    # Test de l'exporteur
    import sys
    
    format_type = sys.argv[1] if len(sys.argv) > 1 else 'csv'
    date = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = export_metrics(format_type, date)
    print(f"Export {format_type}: {result}")

