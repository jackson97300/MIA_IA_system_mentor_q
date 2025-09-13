"""
Utilitaires de Redémarrage MIA_IA_SYSTEM
=========================================

Fonctions de redémarrage des composants système.
"""

import os
import signal
import subprocess
import time
from typing import Dict, Any, Optional
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)


def restart_component(component: str = 'all', reset_cache: bool = False) -> Dict[str, Any]:
    """
    Redémarre un composant du système
    
    Args:
        component: Composant à redémarrer ('all', 'collector', 'trading', 'safety')
        reset_cache: Reset du cache
    
    Returns:
        Résumé du redémarrage
    """
    logger.info(f"🔄 Redémarrage - Composant: {component}, Reset cache: {reset_cache}")
    
    results = {
        'started_at': time.time(),
        'component': component,
        'reset_cache': reset_cache,
        'actions': [],
        'errors': []
    }
    
    try:
        if component in ['all', 'collector']:
            _restart_collector(results)
        
        if component in ['all', 'trading']:
            _restart_trading(results)
        
        if component in ['all', 'safety']:
            _restart_safety(results)
        
        if reset_cache:
            _reset_cache(results)
        
        results['completed_at'] = time.time()
        results['status'] = 'completed'
        
        logger.info(f"✅ Redémarrage terminé - {len(results['actions'])} actions")
        
    except Exception as e:
        logger.error(f"❌ Erreur redémarrage: {e}")
        results['status'] = 'error'
        results['errors'].append(str(e))
    
    return results


def _restart_collector(results: Dict[str, Any]):
    """Redémarre le collecteur"""
    try:
        # Arrêter les processus existants
        _stop_processes(['collector', 'sierra_tail'], results)
        
        # Redémarrer le collecteur
        cmd = ['python', '-m', 'mia_ia_system.launchers.collector', '--restart']
        _run_command(cmd, results, 'collector_restart')
        
    except Exception as e:
        results['errors'].append(f"collector_restart: {e}")


def _restart_trading(results: Dict[str, Any]):
    """Redémarre le système de trading"""
    try:
        # Arrêter les processus existants
        _stop_processes(['trading', 'launch_24_7'], results)
        
        # Redémarrer le trading
        cmd = ['python', '-m', 'mia_ia_system.launchers.launch_24_7', '--restart']
        _run_command(cmd, results, 'trading_restart')
        
    except Exception as e:
        results['errors'].append(f"trading_restart: {e}")


def _restart_safety(results: Dict[str, Any]):
    """Redémarre le système de sécurité"""
    try:
        # Reset du kill switch
        from core.safety_kill_switch import get_safety_kill_switch
        
        kill_switch = get_safety_kill_switch()
        kill_switch.reset("system_restart")
        
        results['actions'].append('kill_switch_reset')
        
    except Exception as e:
        results['errors'].append(f"safety_restart: {e}")


def _reset_cache(results: Dict[str, Any]):
    """Reset du cache"""
    try:
        cache_dirs = ['.cache', '.pytest_cache', '__pycache__']
        
        for cache_dir in cache_dirs:
            if Path(cache_dir).exists():
                import shutil
                shutil.rmtree(cache_dir)
                results['actions'].append(f'cache_cleared: {cache_dir}')
        
        # Nettoyer les fichiers .pyc
        for pyc_file in Path('.').rglob('*.pyc'):
            pyc_file.unlink()
            results['actions'].append(f'pyc_cleared: {pyc_file}')
        
    except Exception as e:
        results['errors'].append(f"cache_reset: {e}")


def _stop_processes(process_names: list, results: Dict[str, Any]):
    """Arrête les processus par nom"""
    try:
        # Trouver les processus
        for proc_name in process_names:
            cmd = ['tasklist', '/FI', f'IMAGENAME eq python.exe', '/FO', 'CSV']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if proc_name in line:
                        # Extraire le PID (simplifié)
                        parts = line.split(',')
                        if len(parts) > 1:
                            pid = parts[1].strip('"')
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                results['actions'].append(f'process_stopped: {proc_name} (PID: {pid})')
                            except (ValueError, ProcessLookupError):
                                pass
    
    except Exception as e:
        results['errors'].append(f"stop_processes: {e}")


def _run_command(cmd: list, results: Dict[str, Any], action_name: str):
    """Exécute une commande"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            results['actions'].append(f'{action_name}: success')
        else:
            results['errors'].append(f'{action_name}: {result.stderr}')
    
    except subprocess.TimeoutExpired:
        results['errors'].append(f'{action_name}: timeout')
    except Exception as e:
        results['errors'].append(f'{action_name}: {e}')


def get_system_status() -> Dict[str, Any]:
    """Retourne le statut du système"""
    status = {
        'timestamp': time.time(),
        'components': {},
        'processes': [],
        'health': 'unknown'
    }
    
    try:
        # Vérifier les composants
        from core.safety_kill_switch import get_safety_kill_switch
        
        kill_switch = get_safety_kill_switch()
        kill_switch_state = kill_switch.get_state()
        
        status['components']['kill_switch'] = {
            'state': kill_switch_state['state'],
            'can_trade': kill_switch_state['can_trade'],
            'reason': kill_switch_state['reason']
        }
        
        # Vérifier les processus
        cmd = ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                if 'python.exe' in line:
                    parts = line.split(',')
                    if len(parts) > 1:
                        pid = parts[1].strip('"')
                        status['processes'].append({'pid': pid, 'name': 'python.exe'})
        
        # Déterminer la santé globale
        if kill_switch_state['can_trade'] and len(status['processes']) > 0:
            status['health'] = 'healthy'
        elif not kill_switch_state['can_trade']:
            status['health'] = 'halted'
        else:
            status['health'] = 'degraded'
    
    except Exception as e:
        status['health'] = 'error'
        status['error'] = str(e)
    
    return status


if __name__ == "__main__":
    # Test du redémarrage
    import sys
    
    component_arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    reset_cache_arg = '--reset-cache' in sys.argv
    
    result = restart_component(component_arg, reset_cache_arg)
    print(f"Résultat: {result}")

