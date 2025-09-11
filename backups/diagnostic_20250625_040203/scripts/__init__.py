#!/usr/bin/env python3
"""
scripts/train_models.py

SCRIPT UTILITAIRE - TRAINING MODÈLES ML BATTLE NAVALE
Script CLI pour entraînement automatisé des modèles via ModelTrainer
Interface simple pour automation et développement

FONCTIONNALITÉS :
- Training depuis snapshots avec paramètres configurables
- Mode développement avec données simulées  
- Training incrémental et re-training automatique
- Configuration apprentissage continu
- Déploiement modèles en staging/production
- Monitoring et statuts détaillés
- Interface CLI friendly pour développeurs

USAGE :
python scripts/train_models.py --mode initial --days 30
python scripts/train_models.py --deploy version_id
python scripts/train_models.py --status --continuous-setup
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Ajout du répertoire racine au Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# === LOCAL IMPORTS ===
try:
    from ml.model_trainer import (
        ModelTrainer, TrainingConfig, TrainingMode, ModelStage,
        TrainingStatus, PerformanceThreshold, ValidationLevel,
        create_model_trainer, create_battle_navale_trainer,
        train_model_from_recent_data
    )
    from ml.simple_model import ModelType
    from config import get_automation_config
except ImportError as e:
    logger.error("Erreur import modules ML: {e}")
    logger.info("Assurez-vous que le module ML est correctement configuré")
    sys.exit(1)

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/train_models.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrainingScriptManager:
    """Gestionnaire script training avec interface CLI"""
    
    def __init__(self):
        """Initialisation gestionnaire"""
        self.trainer: Optional[ModelTrainer] = None
        self.config: Optional[TrainingConfig] = None
        
        # Assurer dossiers logs
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("TrainingScriptManager initialisé")
    
    def setup_training_config(self,
                            min_samples: int = 100,
                            max_samples: int = 5000,
                            model_type: str = "SIGNAL_CLASSIFIER",
                            validation_level: str = "RIGOROUS",
                            auto_deploy: bool = False) -> TrainingConfig:
        """
        Configuration training personnalisée
        
        Args:
            min_samples: Minimum échantillons requis
            max_samples: Maximum échantillons par training
            model_type: Type de modèle (SIGNAL_CLASSIFIER, PROFITABILITY_PREDICTOR)
            validation_level: Niveau validation (BASIC, RIGOROUS, COMPREHENSIVE)
            auto_deploy: Déploiement automatique si meilleur
            
        Returns:
            Configuration training
        """
        try:
            # Conversion enum
            model_type_enum = ModelType[model_type.upper()]
            validation_level_enum = ValidationLevel[validation_level.upper()]
            
            config = TrainingConfig(
                min_samples_required=min_samples,
                max_samples_per_training=max_samples,
                model_type=model_type_enum,
                validation_level=validation_level_enum,
                auto_deploy_if_better=auto_deploy,
                performance_thresholds={
                    "min_accuracy": PerformanceThreshold.MINIMUM_ACCURACY.value,
                    "target_accuracy": PerformanceThreshold.TARGET_ACCURACY.value,
                    "min_precision": PerformanceThreshold.MINIMUM_PRECISION.value,
                    "min_f1_score": PerformanceThreshold.MINIMUM_F1_SCORE.value
                }
            )
            
            self.config = config
            logger.info(f"Configuration training créée:")
            logger.info(f"  - Min samples: {min_samples}")
            logger.info(f"  - Model type: {model_type}")
            logger.info(f"  - Validation: {validation_level}")
            logger.info(f"  - Auto deploy: {auto_deploy}")
            
            return config
            
        except Exception as e:
            logger.error(f"Erreur création config: {e}")
            raise
    
    def train_from_snapshots(self,
                           days_back: int = 30,
                           training_mode: str = "INITIAL",
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> bool:
        """
        Training depuis snapshots Battle Navale
        
        Args:
            days_back: Nombre de jours en arrière pour les données
            training_mode: Mode training (INITIAL, INCREMENTAL, RETRAIN)
            start_date: Date début (format YYYY-MM-DD)
            end_date: Date fin (format YYYY-MM-DD)
            
        Returns:
            True si training réussi, False sinon
        """
        try:
            print("=" * 60)
            logger.info("🚀 DÉBUT TRAINING MODÈLE BATTLE NAVALE")
            print("=" * 60)
            
            # Création trainer
            if not self.trainer:
                self.trainer = create_battle_navale_trainer()
                if self.config:
                    self.trainer.config = self.config
            
            # Préparation dates
            if start_date:
                start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            else:
                start_dt = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            else:
                end_dt = datetime.now(timezone.utc)
            
            # Mode training
            mode_enum = TrainingMode[training_mode.upper()]
            
            logger.info("📅 Période données: {start_dt.date()} → {end_dt.date()}")
            logger.info("🔧 Mode training: {training_mode}")
            logger.info("🎯 Type modèle: {self.trainer.config.model_type.value}")
            print()
            
            # Lancement training
            session = self.trainer.train_model_from_snapshots(
                start_date=start_dt,
                end_date=end_dt,
                training_mode=mode_enum
            )
            
            # Résultats
            print("=" * 60)
            logger.info("📊 RÉSULTATS TRAINING")
            print("=" * 60)
            
            logger.info("Session ID: {session.session_id}")
            logger.info("Status: {session.status.value}")
            logger.info("Échantillons: {session.samples_count}")
            logger.info("Features: {session.features_count}")
            
            if session.training_duration_seconds > 0:
                logger.info("Durée: {session.training_duration_seconds:.1f}s")
            
            if session.model_performance:
                perf = session.model_performance
                logger.info("\n🎯 PERFORMANCE:")
                logger.info("  Accuracy:  {perf['accuracy']:.3f}")
                logger.info("  Precision: {perf['precision']:.3f}")
                logger.info("  Recall:    {perf['recall']:.3f}")
                logger.info("  F1-Score:  {perf['f1_score']:.3f}")
                
                # Validation seuils
                min_f1 = PerformanceThreshold.MINIMUM_F1_SCORE.value
                target_acc = PerformanceThreshold.TARGET_ACCURACY.value
                
                if perf['f1_score'] >= min_f1:
                    logger.info("F1-Score supérieur au minimum ({min_f1:.2f})")
                else:
                    logger.warning("F1-Score sous le minimum requis ({min_f1:.2f})")
                
                if perf['accuracy'] >= target_acc:
                    logger.info("🎯 Accuracy atteint la cible ({target_acc:.2f})")
                else:
                    logger.info("📈 Accuracy sous la cible ({target_acc:.2f})")
            
            if session.validation_results:
                val_results = session.validation_results
                logger.info("\n🔍 VALIDATION:")
                logger.info("  Overall Score: {val_results.get('overall_score', 'N/A')}")
                logger.info("  Production Ready: {'✅' if val_results.get('production_readiness', False) else '❌'}")
            
            if session.warnings:
                logger.info("\n⚠️  AVERTISSEMENTS:")
                for warning in session.warnings:
                    logger.info("  - {warning}")
            
            if session.notes:
                logger.info("\n📝 NOTES:")
                for note in session.notes:
                    logger.info("  - {note}")
            
            # Status final
            success = session.status == TrainingStatus.COMPLETED
            
            print("\n" + "=" * 60)
            if success:
                logger.info("TRAINING TERMINÉ AVEC SUCCÈS")
                if session.model_path:
                    logger.info("📁 Modèle sauvegardé: {session.model_path}")
            else:
                logger.error("TRAINING ÉCHOUÉ")
                if session.error_message:
                    logger.info("Erreur: {session.error_message}")
            print("=" * 60)
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur training: {e}")
            logger.error("Erreur training: {e}")
            return False
    
    def setup_continuous_learning(self,
                                check_interval_hours: int = 24,
                                retrain_threshold: float = 0.05) -> bool:
        """
        Configuration apprentissage continu
        
        Args:
            check_interval_hours: Vérification toutes les X heures
            retrain_threshold: Seuil dégradation pour re-training (5% = 0.05)
            
        Returns:
            True si configuré avec succès
        """
        try:
            logger.info("🔄 CONFIGURATION APPRENTISSAGE CONTINU")
            print("=" * 50)
            
            if not self.trainer:
                self.trainer = create_battle_navale_trainer()
            
            success = self.trainer.setup_continuous_learning(
                check_interval_hours=check_interval_hours,
                retrain_threshold=retrain_threshold
            )
            
            if success:
                logger.info("Apprentissage continu configuré:")
                logger.info("  - Vérification: toutes les {check_interval_hours}h")
                logger.info("  - Seuil re-training: {retrain_threshold*100:.1f}%")
                logger.info("  - Re-training auto: Dimanche 02:00")
                logger.info("  - Thread monitoring: Actif")
            else:
                logger.error("Échec configuration apprentissage continu")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur configuration continue: {e}")
            logger.error("Erreur: {e}")
            return False
    
    def deploy_model(self, version_id: str, stage: str = "production") -> bool:
        """
        Déploiement modèle vers stage spécifique
        
        Args:
            version_id: ID version à déployer
            stage: Stage cible (staging, production)
            
        Returns:
            True si déploiement réussi
        """
        try:
            logger.info("🚀 DÉPLOIEMENT MODÈLE → {stage.upper()}")
            print("=" * 50)
            
            if not self.trainer:
                self.trainer = create_battle_navale_trainer()
            
            if stage.lower() == "production":
                success = self.trainer.deploy_model_to_production(version_id)
            else:
                logger.error("Stage '{stage}' non supporté. Utilisez 'production'")
                return False
            
            if success:
                logger.info("Modèle {version_id} déployé en {stage}")
            else:
                logger.error("Échec déploiement {version_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur déploiement: {e}")
            logger.error("Erreur déploiement: {e}")
            return False
    
    def show_training_status(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Affichage statut système training
        
        Args:
            detailed: Affichage détaillé
            
        Returns:
            Statut système
        """
        try:
            logger.info("📊 STATUT SYSTÈME TRAINING ML")
            print("=" * 50)
            
            if not self.trainer:
                self.trainer = create_battle_navale_trainer()
            
            status = self.trainer.get_training_status()
            
            # Système global
            sys_status = status.get('system_status', {})
            logger.info("🔧 Trainer actif: {'✅' if sys_status.get('trainer_active', False) else '❌'}")
            logger.info("🔄 Apprentissage continu: {'✅' if sys_status.get('continuous_learning', False) else '❌'}")
            logger.info("📈 Modèles total: {sys_status.get('models_total', 0)}")
            logger.info("🚀 Modèles production: {sys_status.get('models_in_production', 0)}")
            
            # Session actuelle
            current = status.get('current_session')
            if current:
                logger.info("\n⏳ SESSION ACTUELLE:")
                logger.info("  ID: {current['session_id']}")
                logger.info("  Status: {current['status']}")
                logger.info("  Échantillons: {current['samples_count']}")
                logger.info("  Features: {current['features_count']}")
            else:
                logger.info("\n💤 Aucune session en cours")
            
            # Modèle actif
            active = status.get('active_model')
            if active:
                logger.info("\n🎯 MODÈLE ACTIF:")
                logger.info("  Version: {active['version_id']}")
                logger.info("  Accuracy: {active['accuracy']:.3f}")
                logger.info("  F1-Score: {active['f1_score']:.3f}")
                logger.info("  Échantillons training: {active['training_samples']}")
                if active['deployment_date']:
                    dep_date = datetime.fromisoformat(active['deployment_date']).strftime('%Y-%m-%d %H:%M')
                    logger.info("  Déployé: {dep_date}")
            else:
                logger.info("\n🚫 Aucun modèle actif")
            
            # Configuration
            config = status.get('configuration', {})
            logger.info("\n⚙️  CONFIGURATION:")
            logger.info("  Min samples: {config.get('min_samples_required', 'N/A')}")
            logger.info("  Auto deploy: {'✅' if config.get('auto_deploy', False) else '❌'}")
            logger.info("  Validation: {config.get('validation_level', 'N/A')}")
            
            # Seuils performance
            thresholds = config.get('performance_thresholds', {})
            if thresholds:
                logger.info("  Seuils performance:")
                logger.info("    - Min accuracy: {thresholds.get('min_accuracy', 'N/A')}")
                logger.info("    - Min precision: {thresholds.get('min_precision', 'N/A')}")
                logger.info("    - Min F1-score: {thresholds.get('min_f1_score', 'N/A')}")
            
            # Sessions récentes (si detailed)
            if detailed:
                recent = status.get('recent_sessions', [])
                if recent:
                    logger.info("\n📋 SESSIONS RÉCENTES:")
                    for session in recent[-3:]:  # 3 dernières
                        perf = session.get('performance', {})
                        perf_str = f"Acc:{perf.get('accuracy', 0):.2f}" if perf else "N/A"
                        logger.info("  {session['session_id']}: {session['status']} - {perf_str}")
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur statut: {e}")
            logger.error("Erreur récupération statut: {e}")
            return {}
    
    def retrain_if_needed(self) -> bool:
        """
        Check et re-training automatique si nécessaire
        
        Returns:
            True si re-training lancé, False sinon
        """
        try:
            logger.debug("VÉRIFICATION BESOIN RE-TRAINING")
            print("=" * 50)
            
            if not self.trainer:
                self.trainer = create_battle_navale_trainer()
            
            session = self.trainer.retrain_if_needed()
            
            if session:
                logger.info("🔄 Re-training automatique lancé:")
                logger.info("  Session: {session.session_id}")
                logger.info("  Status: {session.status.value}")
                
                # Attendre fin training
                while session.status in [TrainingStatus.PREPARING_DATA, TrainingStatus.TRAINING, TrainingStatus.VALIDATING]:
                    logger.info("  ⏳ En cours... {session.status.value}")
                    import time
                    time.sleep(5)
                    
                    # Refresh status
                    status = self.trainer.get_training_status()
                    current = status.get('current_session')
                    if current and current['session_id'] == session.session_id:
                        try:
                            session.status = TrainingStatus[current['status'].upper()]
                        except:
                            break
                    else:
                        break
                
                logger.info("Re-training terminé: {session.status.value}")
                return True
            else:
                logger.info("Performance stable - Pas de re-training nécessaire")
                return False
                
        except Exception as e:
            logger.error(f"Erreur re-training check: {e}")
            logger.error("Erreur: {e}")
            return False

def main():
    """Interface CLI principale"""
    parser = argparse.ArgumentParser(
        description="Script training modèles ML Battle Navale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python scripts/train_models.py --train --days 30
  python scripts/train_models.py --train --mode incremental
  python scripts/train_models.py --retrain-check
  python scripts/train_models.py --status --detailed
  python scripts/train_models.py --continuous-setup --interval 12
  python scripts/train_models.py --deploy v_training_20231215_143022
        """
    )
    
    # Groupe actions principales
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--train', action='store_true',
                             help='Lancer training depuis snapshots')
    action_group.add_argument('--retrain-check', action='store_true',
                             help='Vérifier si re-training nécessaire')
    action_group.add_argument('--status', action='store_true',
                             help='Afficher statut système')
    action_group.add_argument('--continuous-setup', action='store_true',
                             help='Configurer apprentissage continu')
    action_group.add_argument('--deploy', type=str, metavar='VERSION_ID',
                             help='Déployer modèle en production')
    
    # Paramètres training
    parser.add_argument('--days', type=int, default=30,
                       help='Nombre de jours de données (défaut: 30)')
    parser.add_argument('--mode', choices=['initial', 'incremental', 'retrain'],
                       default='initial', help='Mode training (défaut: initial)')
    parser.add_argument('--start-date', type=str,
                       help='Date début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='Date fin (YYYY-MM-DD)')
    
    # Paramètres configuration
    parser.add_argument('--min-samples', type=int, default=100,
                       help='Minimum échantillons requis (défaut: 100)')
    parser.add_argument('--max-samples', type=int, default=5000,
                       help='Maximum échantillons (défaut: 5000)')
    parser.add_argument('--model-type', choices=['signal_classifier', 'profitability_predictor'],
                       default='signal_classifier', help='Type de modèle')
    parser.add_argument('--validation', choices=['basic', 'rigorous', 'comprehensive'],
                       default='rigorous', help='Niveau validation')
    parser.add_argument('--auto-deploy', action='store_true',
                       help='Déploiement automatique si meilleur')
    
    # Paramètres apprentissage continu
    parser.add_argument('--interval', type=int, default=24,
                       help='Intervalle vérification (heures, défaut: 24)')
    parser.add_argument('--threshold', type=float, default=0.05,
                       help='Seuil re-training (défaut: 0.05)')
    
    # Options affichage
    parser.add_argument('--detailed', action='store_true',
                       help='Affichage détaillé pour --status')
    parser.add_argument('--quiet', action='store_true',
                       help='Mode silencieux (logs seulement)')
    
    args = parser.parse_args()
    
    # Configuration logging
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Création gestionnaire
    manager = TrainingScriptManager()
    
    try:
        # Configuration training si nécessaire
        if args.train or args.retrain_check:
            manager.setup_training_config(
                min_samples=args.min_samples,
                max_samples=args.max_samples,
                model_type=args.model_type,
                validation_level=args.validation,
                auto_deploy=args.auto_deploy
            )
        
        # Exécution action demandée
        success = False
        
        if args.train:
            success = manager.train_from_snapshots(
                days_back=args.days,
                training_mode=args.mode,
                start_date=args.start_date,
                end_date=args.end_date
            )
        
        elif args.retrain_check:
            success = manager.retrain_if_needed()
        
        elif args.status:
            status = manager.show_training_status(detailed=args.detailed)
            success = 'system_status' in status
        
        elif args.continuous_setup:
            success = manager.setup_continuous_learning(
                check_interval_hours=args.interval,
                retrain_threshold=args.threshold
            )
        
        elif args.deploy:
            success = manager.deploy_model(args.deploy, "production")
        
        # Code de sortie
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Arrêt demandé par utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur script: {e}")
        logger.error("Erreur script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()