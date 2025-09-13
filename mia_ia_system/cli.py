"""
MIA_IA_SYSTEM - Interface en ligne de commande
=============================================

CLI principal pour le système de trading automatisé.
"""

import click
import asyncio
import sys
from pathlib import Path
from typing import Optional

from .core.logger import get_logger
from .core.config_manager import AutomationConfig

logger = get_logger(__name__)


@click.group()
@click.version_option(version="4.0.0")
@click.option('--verbose', '-v', is_flag=True, help='Mode verbeux')
@click.option('--config', '-c', type=click.Path(exists=True), help='Fichier de configuration')
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """MIA_IA_SYSTEM - Système de Trading Automatisé"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    if verbose:
        click.echo("🔍 Mode verbeux activé")


@cli.command()
@click.option('--charts', default='3,4,8,10', help='Charts à collecter (ex: 3,4,8,10)')
@click.option('--mode', type=click.Choice(['development', 'production']), default='development')
@click.option('--once', is_flag=True, help='Exécution unique (pas de boucle)')
@click.pass_context
def collector(ctx, charts: str, mode: str, once: bool):
    """Lance le collecteur de données Sierra Chart"""
    click.echo(f"📊 Lancement du collecteur - Charts: {charts}, Mode: {mode}")
    
    if once:
        click.echo("🔄 Exécution unique activée")
    
    # Import et lancement du collecteur
    try:
        from .launchers.collector import main as collector_main
        asyncio.run(collector_main(charts=charts, mode=mode, once=once))
    except ImportError:
        click.echo("❌ Module collecteur non disponible")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Erreur collecteur: {e}")
        sys.exit(1)


@cli.command()
@click.option('--mode', type=click.Choice(['simulation', 'paper', 'live']), default='simulation')
@click.option('--strategy', default='battle_navale', help='Stratégie à utiliser')
@click.option('--max-position', type=int, default=1, help='Position maximale')
@click.pass_context
def trading(ctx, mode: str, strategy: str, max_position: int):
    """Lance le système de trading"""
    click.echo(f"📈 Lancement trading - Mode: {mode}, Stratégie: {strategy}")
    
    if mode == 'live':
        click.confirm("⚠️ Mode LIVE activé - Continuer ?", abort=True)
    
    # Import et lancement du trading
    try:
        from .launchers.launch_24_7 import main as trading_main
        asyncio.run(trading_main(mode=mode, strategy=strategy, max_position=max_position))
    except ImportError:
        click.echo("❌ Module trading non disponible")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Erreur trading: {e}")
        sys.exit(1)


@cli.command()
@click.option('--component', type=click.Choice(['all', 'collector', 'trading', 'safety']), default='all')
@click.option('--level', type=click.Choice(['INFO', 'WARNING', 'ERROR']), default='INFO')
@click.pass_context
def logs(ctx, component: str, level: str):
    """Affiche les logs du système"""
    click.echo(f"📋 Logs - Composant: {component}, Niveau: {level}")
    
    log_dir = Path("logs")
    if not log_dir.exists():
        click.echo("❌ Dossier logs non trouvé")
        return
    
    # Affichage des logs
    for log_file in log_dir.glob("*.log"):
        if component == 'all' or component in log_file.name:
            click.echo(f"\n📄 {log_file.name}:")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-50:]:  # Dernières 50 lignes
                        if level in line or level == 'INFO':
                            click.echo(line.strip())
            except Exception as e:
                click.echo(f"❌ Erreur lecture {log_file}: {e}")


@cli.command()
@click.option('--format', type=click.Choice(['csv', 'json', 'prometheus']), default='csv')
@click.option('--date', help='Date (YYYYMMDD)')
@click.option('--port', type=int, default=9090, help='Port pour Prometheus')
@click.pass_context
def metrics(ctx, format: str, date: Optional[str], port: int):
    """Exporte les métriques du système"""
    click.echo(f"📊 Export métriques - Format: {format}")
    
    if format == 'prometheus':
        click.echo(f"🌐 Serveur Prometheus sur port {port}")
    
    # Import et export des métriques
    try:
        from .monitoring.metrics_exporter import export_metrics
        export_metrics(format=format, date=date, port=port)
    except ImportError:
        click.echo("❌ Module métriques non disponible")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Erreur export: {e}")
        sys.exit(1)


@cli.command()
@click.option('--component', type=click.Choice(['all', 'collector', 'trading', 'safety']), default='all')
@click.option('--full', is_flag=True, help='Test complet')
@click.pass_context
def test(ctx, component: str, full: bool):
    """Lance les tests du système"""
    click.echo(f"🧪 Tests - Composant: {component}")
    
    if full:
        click.echo("🔄 Test complet activé")
    
    # Import et lancement des tests
    try:
        import subprocess
        cmd = ["python", "-m", "pytest", "tests/"]
        if component != 'all':
            cmd.extend([f"tests/test_{component}.py"])
        if full:
            cmd.extend(["-v", "--tb=short"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        click.echo(result.stdout)
        if result.stderr:
            click.echo(f"⚠️ Erreurs: {result.stderr}")
        
        if result.returncode == 0:
            click.echo("✅ Tests passés")
        else:
            click.echo("❌ Tests échoués")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Erreur tests: {e}")
        sys.exit(1)


@cli.command()
@click.option('--type', type=click.Choice(['all', 'logs', 'data', 'cache']), default='all')
@click.option('--older-than', type=int, default=7, help='Jours')
@click.option('--confirm', is_flag=True, help='Confirmation automatique')
@click.pass_context
def cleanup(ctx, type: str, older_than: int, confirm: bool):
    """Nettoie les fichiers anciens"""
    click.echo(f"🧹 Nettoyage - Type: {type}, Plus ancien que: {older_than} jours")
    
    if not confirm:
        click.confirm("⚠️ Continuer le nettoyage ?", abort=True)
    
    # Import et nettoyage
    try:
        from .utils.cleanup import cleanup_files
        cleanup_files(type=type, older_than=older_than)
        click.echo("✅ Nettoyage terminé")
    except ImportError:
        click.echo("❌ Module nettoyage non disponible")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Erreur nettoyage: {e}")
        sys.exit(1)


@cli.command()
@click.option('--component', type=click.Choice(['all', 'collector', 'trading', 'safety']), default='all')
@click.option('--reset-cache', is_flag=True, help='Reset du cache')
@click.pass_context
def restart(ctx, component: str, reset_cache: bool):
    """Redémarre les composants du système"""
    click.echo(f"🔄 Redémarrage - Composant: {component}")
    
    if reset_cache:
        click.echo("🗑️ Reset du cache activé")
    
    # Import et redémarrage
    try:
        from .utils.restart import restart_component
        restart_component(component=component, reset_cache=reset_cache)
        click.echo("✅ Redémarrage terminé")
    except ImportError:
        click.echo("❌ Module redémarrage non disponible")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Erreur redémarrage: {e}")
        sys.exit(1)


def main():
    """Point d'entrée principal du CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n🛑 Arrêt demandé par utilisateur")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Erreur CLI: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

