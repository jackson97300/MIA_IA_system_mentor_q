#!/usr/bin/env python3
"""
📁 CONFIGURATION CHEMINS SIERRA - MIA_IA_SYSTEM
===============================================

Configuration centralisée des chemins pour les fichiers Sierra JSONL
- Charts individuels: chart_{n}_{YYYYMMDD}.jsonl
- Fichier unifié: mia_unified_{YYYYMMDD}.jsonl
"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional

# === CHEMINS DE BASE ===
CHART_OUT_DIR = Path(r"D:\MIA_IA_system")
DEFAULT_CHARTS = [3, 4, 8, 10]  # Charts par défaut

# === FONCTIONS DE CHEMINS ===

def per_chart_daily_path(chart_number: int, date_str: Optional[str] = None) -> Path:
    """
    Génère le chemin pour un fichier chart individuel
    
    Args:
        chart_number: Numéro du chart (3, 4, 8, 10)
        date_str: Date au format YYYYMMDD (défaut: aujourd'hui)
    
    Returns:
        Path vers le fichier chart_{n}_{YYYYMMDD}.jsonl
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    
    filename = f"chart_{chart_number}_{date_str}.jsonl"
    return CHART_OUT_DIR / filename

def unified_daily_path(date_str: Optional[str] = None) -> Path:
    """
    Génère le chemin pour le fichier unifié
    
    Args:
        date_str: Date au format YYYYMMDD (défaut: aujourd'hui)
    
    Returns:
        Path vers le fichier mia_unified_{YYYYMMDD}.jsonl
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    
    filename = f"mia_unified_{date_str}.jsonl"
    return CHART_OUT_DIR / filename

def get_chart_paths(charts: List[int], date_str: Optional[str] = None) -> List[Path]:
    """
    Génère les chemins pour plusieurs charts
    
    Args:
        charts: Liste des numéros de charts
        date_str: Date au format YYYYMMDD (défaut: aujourd'hui)
    
    Returns:
        Liste des Path vers les fichiers charts
    """
    return [per_chart_daily_path(chart, date_str) for chart in charts]

def ensure_chart_dir() -> Path:
    """
    S'assure que le répertoire de sortie existe
    
    Returns:
        Path vers le répertoire de sortie
    """
    CHART_OUT_DIR.mkdir(parents=True, exist_ok=True)
    return CHART_OUT_DIR

# === CONFIGURATION AVANCÉE ===

class SierraConfig:
    """Configuration Sierra avec chemins et paramètres"""
    
    def __init__(self, 
                 output_dir: Optional[Path] = None,
                 charts: Optional[List[int]] = None,
                 unified_filename_template: str = "mia_unified_{date}.jsonl",
                 chart_filename_template: str = "chart_{n}_{date}.jsonl"):
        
        self.output_dir = output_dir or CHART_OUT_DIR
        self.charts = charts or DEFAULT_CHARTS.copy()
        self.unified_template = unified_filename_template
        self.chart_template = chart_filename_template
    
    def get_unified_path(self, date_str: Optional[str] = None) -> Path:
        """Chemin du fichier unifié pour cette config"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        filename = self.unified_template.format(date=date_str)
        return self.output_dir / filename
    
    def get_chart_paths(self, date_str: Optional[str] = None) -> List[Path]:
        """Chemins des fichiers charts pour cette config"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        paths = []
        for chart in self.charts:
            filename = self.chart_template.format(n=chart, date=date_str)
            paths.append(self.output_dir / filename)
        
        return paths
    
    def ensure_dirs(self) -> Path:
        """S'assure que les répertoires existent"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

# === INSTANCE PAR DÉFAUT ===
DEFAULT_SIERRA_CONFIG = SierraConfig()

# === FONCTIONS UTILITAIRES ===

def get_today_date_str() -> str:
    """Retourne la date d'aujourd'hui au format YYYYMMDD"""
    return datetime.now().strftime("%Y%m%d")

def parse_date_str(date_str: str) -> datetime:
    """Parse une date au format YYYYMMDD"""
    return datetime.strptime(date_str, "%Y%m%d")

def is_valid_date_str(date_str: str) -> bool:
    """Vérifie si une date est au format YYYYMMDD valide"""
    try:
        parse_date_str(date_str)
        return True
    except ValueError:
        return False

# === EXPORTS ===
__all__ = [
    'CHART_OUT_DIR',
    'DEFAULT_CHARTS',
    'per_chart_daily_path',
    'unified_daily_path',
    'get_chart_paths',
    'ensure_chart_dir',
    'SierraConfig',
    'DEFAULT_SIERRA_CONFIG',
    'get_today_date_str',
    'parse_date_str',
    'is_valid_date_str'
]
