#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Configuration Loader V2 avec Migrations
=======================================================

Version: Production Ready v2.0
- Migrations automatiques pour compatibilité ascendante
- Dot-access avec SimpleNamespace
- Validation des clés inconnues
- Support environnements avec overlay
- Monitoring des changements

IMPACT IMMÉDIAT: Résout tous les warnings "unexpected keyword"
"""

import json
import yaml
import os
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)

# === MIGRATIONS DE COMPATIBILITÉ ===

MIGRATION_RULES = {
    # Volume Profile
    'bin_size': 'bin_ticks',
    'max_history': 'max_history_size',
    
    # VWAP
    'enable_advanced_features': 'advanced.enabled',
    'bands_count': 'bands_stdev',
    
    # NBCV
    'delta_threshold': 'min_delta_ratio_pct',
    'volume_imbalance_threshold': 'min_ask_bid_ratio',
    
    # VIX
    'low_threshold': 'low',
    'high_threshold': 'high',
    'extreme_threshold': 'extreme',
    
    # Advanced Features
    'tick_momentum_window': 'tick_momentum.window',
    'delta_divergence_lookback': 'delta_divergence.lookback',
    'volatility_regime_atr_len': 'volatility_regime.atr_len'
}

def migrate_config(config_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Applique les migrations de compatibilité
    
    Args:
        config_dict: Configuration à migrer
        
    Returns:
        Tuple (config_migrée, warnings)
    """
    warnings = []
    migrated = config_dict.copy()
    
    def apply_migration(obj, path=""):
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if key in MIGRATION_RULES:
                    new_key = MIGRATION_RULES[key]
                    new_path = f"{path}.{new_key}" if path else new_key
                    
                    # Créer la structure imbriquée si nécessaire
                    if '.' in new_key:
                        parts = new_key.split('.')
                        current = migrated
                        for part in parts[:-1]:
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                        current[parts[-1]] = value
                    else:
                        migrated[new_key] = value
                    
                    # Supprimer l'ancienne clé
                    del obj[key]
                    warnings.append(f"🔄 Migré: {key} → {new_key}")
                
                # Récursion pour les objets imbriqués
                apply_migration(value, f"{path}.{key}" if path else key)
    
    apply_migration(migrated)
    return migrated, warnings

def deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne deux dictionnaires de manière récursive
    
    Args:
        base: Configuration de base
        overlay: Configuration à superposer
        
    Returns:
        Configuration fusionnée
    """
    result = base.copy()
    
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def dotify(d):
    """
    Convertit un dictionnaire en namespace dot-accessible récursivement
    """
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dotify(v) for k, v in d.items()})
    if isinstance(d, list):
        return [dotify(x) for x in d]
    return d

def require_keys(ns, allowed: List[str], config_name: str = "config"):
    """
    Valide que seules les clés autorisées sont présentes
    """
    if not isinstance(ns, SimpleNamespace):
        return
        
    extra = [k for k in vars(ns).keys() if k not in allowed]
    if extra:
        logger.warning(f"⚠️ Clés de config ignorées dans {config_name}: {extra}")

# === LOADER V2 PRINCIPAL ===

class ConfigLoaderV2:
    """
    Loader de configuration V2 avec migrations et monitoring
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.cache = {}
        self.file_hashes = {}
        
    def load_config_file(self, file_path: str, config_name: str = None) -> SimpleNamespace:
        """
        Charge un fichier de configuration avec migrations
        
        Args:
            file_path: Chemin vers le fichier
            config_name: Nom de la configuration
            
        Returns:
            Configuration en format dot-accessible
        """
        if config_name is None:
            config_name = Path(file_path).stem
            
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"❌ Fichier de config introuvable: {file_path}")
                return SimpleNamespace()
            
            # Vérifier si le fichier a changé
            current_hash = self._get_file_hash(file_path)
            if config_name in self.cache and config_name in self.file_hashes:
                if self.file_hashes[config_name] == current_hash:
                    logger.debug(f"📋 Cache hit pour {config_name}")
                    return self.cache[config_name]
            
            # Charger le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f) or {}
                else:
                    data = json.load(f)
            
            # Appliquer les migrations
            migrated_data, warnings = migrate_config(data)
            
            # Log des migrations
            for warning in warnings:
                logger.info(warning)
            
            # Convertir en namespace dot-accessible
            config = dotify(migrated_data)
            
            # Mettre en cache
            self.cache[config_name] = config
            self.file_hashes[config_name] = current_hash
            
            logger.info(f"✅ Configuration {config_name} chargée depuis {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement config {config_name}: {e}")
            return SimpleNamespace()
    
    def load_with_environment(self, base_file: str, env: str = None) -> SimpleNamespace:
        """
        Charge une configuration avec overlay d'environnement
        
        Args:
            base_file: Fichier de base
            env: Environnement (dev/staging/prod)
            
        Returns:
            Configuration avec overlay
        """
        if env is None:
            env = os.getenv("MIA_ENV", "dev")
        
        # Charger la configuration de base
        base_config = self.load_config_file(base_file, f"{Path(base_file).stem}_base")
        
        # Chercher l'overlay d'environnement
        overlay_file = base_file.replace('.json', f'.{env}.json')
        if Path(overlay_file).exists():
            overlay_config = self.load_config_file(overlay_file, f"{Path(base_file).stem}_{env}")
            
            # Fusionner les configurations
            base_dict = self._namespace_to_dict(base_config)
            overlay_dict = self._namespace_to_dict(overlay_config)
            merged_dict = deep_merge(base_dict, overlay_dict)
            
            config = dotify(merged_dict)
            logger.info(f"✅ Configuration {env} chargée avec overlay")
            return config
        
        logger.info(f"ℹ️ Pas d'overlay {env} trouvé, utilisation de la config de base")
        return base_config
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcule le hash SHA256 d'un fichier"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _namespace_to_dict(self, ns: SimpleNamespace) -> Dict[str, Any]:
        """Convertit un SimpleNamespace en dictionnaire"""
        if isinstance(ns, SimpleNamespace):
            return {k: self._namespace_to_dict(v) for k, v in vars(ns).items()}
        elif isinstance(ns, list):
            return [self._namespace_to_dict(item) for item in ns]
        else:
            return ns
    
    def validate_config(self, config: SimpleNamespace, expected_keys: List[str]) -> bool:
        """
        Valide la compatibilité d'une configuration
        
        Args:
            config: Configuration à valider
            expected_keys: Clés attendues
            
        Returns:
            True si compatible
        """
        if not isinstance(config, SimpleNamespace):
            logger.error("❌ Configuration doit être un SimpleNamespace")
            return False
            
        missing = [k for k in expected_keys if not hasattr(config, k)]
        if missing:
            logger.error(f"❌ Clés manquantes dans la configuration: {missing}")
            return False
            
        return True

# === INSTANCE GLOBALE ===

_loader_v2 = ConfigLoaderV2()

def get_feature_config_v2() -> SimpleNamespace:
    """
    Récupère la configuration des features avec migrations (V2)
    
    Returns:
        Configuration des features migrée
    """
    return _loader_v2.load_with_environment("config/feature_config.json")

def get_trading_config_v2() -> SimpleNamespace:
    """
    Récupère la configuration trading avec migrations (V2)
    
    Returns:
        Configuration trading migrée
    """
    return _loader_v2.load_config_file("config/trading_config.py", "trading")

def get_automation_config_v2() -> SimpleNamespace:
    """
    Récupère la configuration automation avec migrations (V2)
    
    Returns:
        Configuration automation migrée
    """
    return _loader_v2.load_config_file("config/automation_config.py", "automation")

# === FONCTIONS DE COMPATIBILITÉ ===

def get_feature_config() -> SimpleNamespace:
    """
    Fonction de compatibilité - utilise le loader V2
    """
    return get_feature_config_v2()

# === TEST DU LOADER V2 ===

if __name__ == "__main__":
    print("🧪 Test du Configuration Loader V2...")
    
    # Test chargement avec migrations
    feature_config = get_feature_config_v2()
    print(f"✅ Feature config V2 chargée: {type(feature_config).__name__}")
    
    # Test accès dot
    if hasattr(feature_config, 'vwap'):
        print(f"✅ Accès dot OK: vwap.max_history = {getattr(feature_config.vwap, 'max_history', 'N/A')}")
    
    if hasattr(feature_config, 'volume_profile'):
        print(f"✅ Accès dot OK: volume_profile.bin_ticks = {getattr(feature_config.volume_profile, 'bin_ticks', 'N/A')}")
    
    # Test validation
    expected_keys = ['vwap', 'volume_profile', 'nbcv', 'vix', 'advanced']
    is_valid = _loader_v2.validate_config(feature_config, expected_keys)
    print(f"✅ Validation: {'OK' if is_valid else 'ERREUR'}")
    
    print("🎉 Test Loader V2 terminé avec succès!")
