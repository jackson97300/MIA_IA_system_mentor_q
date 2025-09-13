"""
Utilitaires de Nettoyage MIA_IA_SYSTEM
======================================

Fonctions de nettoyage des fichiers et données.
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from core.logger import get_logger

logger = get_logger(__name__)


def cleanup_files(type: str = 'all', older_than: int = 7, confirm: bool = False) -> Dict[str, Any]:
    """
    Nettoie les fichiers anciens
    
    Args:
        type: Type de fichiers à nettoyer ('all', 'logs', 'data', 'cache')
        older_than: Âge minimum en jours
        confirm: Confirmation automatique
    
    Returns:
        Résumé du nettoyage
    """
    logger.info(f"🧹 Début nettoyage - Type: {type}, Plus ancien que: {older_than} jours")
    
    if not confirm:
        logger.warning("⚠️ Nettoyage non confirmé - utilisez --confirm pour exécuter")
        return {'status': 'not_confirmed'}
    
    results = {
        'started_at': datetime.now().isoformat(),
        'type': type,
        'older_than_days': older_than,
        'files_removed': 0,
        'bytes_freed': 0,
        'errors': []
    }
    
    cutoff_date = datetime.now() - timedelta(days=older_than)
    
    try:
        if type in ['all', 'logs']:
            _cleanup_logs(cutoff_date, results)
        
        if type in ['all', 'data']:
            _cleanup_data(cutoff_date, results)
        
        if type in ['all', 'cache']:
            _cleanup_cache(cutoff_date, results)
        
        results['completed_at'] = datetime.now().isoformat()
        results['status'] = 'completed'
        
        logger.info(f"✅ Nettoyage terminé - {results['files_removed']} fichiers, "
                   f"{results['bytes_freed'] / 1024 / 1024:.1f} MB libérés")
        
    except Exception as e:
        logger.error(f"❌ Erreur nettoyage: {e}")
        results['status'] = 'error'
        results['errors'].append(str(e))
    
    return results


def _cleanup_logs(cutoff_date: datetime, results: Dict[str, Any]):
    """Nettoie les fichiers de logs"""
    log_dirs = ['logs', 'log']
    
    for log_dir in log_dirs:
        if Path(log_dir).exists():
            _cleanup_directory(Path(log_dir), cutoff_date, results, ['.log', '.log.*'])


def _cleanup_data(cutoff_date: datetime, results: Dict[str, Any]):
    """Nettoie les fichiers de données"""
    data_patterns = [
        'chart_*.jsonl',
        'mia_unified_*.jsonl',
        '*.backup',
        '*.tmp'
    ]
    
    # Nettoyer les fichiers JSONL anciens
    for pattern in data_patterns:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file():
                _cleanup_file(file_path, cutoff_date, results)


def _cleanup_cache(cutoff_date: datetime, results: Dict[str, Any]):
    """Nettoie les fichiers de cache"""
    cache_dirs = ['.cache', '.pytest_cache', '__pycache__']
    
    for cache_dir in cache_dirs:
        if Path(cache_dir).exists():
            _cleanup_directory(Path(cache_dir), cutoff_date, results, ['.pyc', '.pyo'])


def _cleanup_directory(directory: Path, cutoff_date: datetime, results: Dict[str, Any], extensions: List[str]):
    """Nettoie un répertoire"""
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            # Vérifier l'extension
            if any(file_path.suffix == ext for ext in extensions):
                _cleanup_file(file_path, cutoff_date, results)


def _cleanup_file(file_path: Path, cutoff_date: datetime, results: Dict[str, Any]):
    """Nettoie un fichier individuel"""
    try:
        # Vérifier l'âge du fichier
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        if file_mtime < cutoff_date:
            file_size = file_path.stat().st_size
            
            # Supprimer le fichier
            file_path.unlink()
            
            results['files_removed'] += 1
            results['bytes_freed'] += file_size
            
            logger.debug(f"🗑️ Supprimé: {file_path} ({file_size} bytes)")
    
    except Exception as e:
        logger.warning(f"⚠️ Erreur suppression {file_path}: {e}")
        results['errors'].append(f"{file_path}: {e}")


def get_cleanup_summary() -> Dict[str, Any]:
    """Retourne un résumé des fichiers pouvant être nettoyés"""
    summary = {
        'logs': {'files': 0, 'size': 0},
        'data': {'files': 0, 'size': 0},
        'cache': {'files': 0, 'size': 0}
    }
    
    # Analyser les logs
    for log_dir in ['logs', 'log']:
        if Path(log_dir).exists():
            _analyze_directory(Path(log_dir), summary['logs'], ['.log', '.log.*'])
    
    # Analyser les données
    for pattern in ['chart_*.jsonl', 'mia_unified_*.jsonl', '*.backup']:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file():
                summary['data']['files'] += 1
                summary['data']['size'] += file_path.stat().st_size
    
    # Analyser le cache
    for cache_dir in ['.cache', '.pytest_cache', '__pycache__']:
        if Path(cache_dir).exists():
            _analyze_directory(Path(cache_dir), summary['cache'], ['.pyc', '.pyo'])
    
    return summary


def _analyze_directory(directory: Path, summary: Dict[str, Any], extensions: List[str]):
    """Analyse un répertoire"""
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            if any(file_path.suffix == ext for ext in extensions):
                summary['files'] += 1
                summary['size'] += file_path.stat().st_size


if __name__ == "__main__":
    # Test du nettoyage
    import sys
    
    type_arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    days_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    confirm_arg = '--confirm' in sys.argv
    
    result = cleanup_files(type_arg, days_arg, confirm_arg)
    print(f"Résultat: {result}")

