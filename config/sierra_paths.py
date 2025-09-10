"""
Configuration des chemins Sierra Chart
Évite les chemins Windows en dur dans le code
"""

from pathlib import Path
import os

# Chemin de base du projet
BASE_DIR = Path(os.getenv("MIA_BASE_DIR", r"D:\MIA_IA_system"))

# Chemins spécifiques
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Vérification que le répertoire existe
if not BASE_DIR.exists():
    BASE_DIR.mkdir(parents=True, exist_ok=True)