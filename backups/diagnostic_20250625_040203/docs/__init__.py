#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Documentation Package
Documentation complète du système de trading Battle Navale automatisé

VERSION: 3.0.0 - Production Ready
DATE: Juin 2025
AUTHOR: MIA Trading System Team

DOCUMENTATION DISPONIBLE :
├── architecture.md         # Architecture technique complète  
├── automation_guide.md     # Guide automation Battle Navale
├── data_collection_guide.md # Guide collection données pour ML
├── ml_strategy.md          # Stratégie ML progressive 2025-2026
└── deployment_guide.md     # Guide déploiement live trading

USAGE :
```python
from docs import get_doc_info, validate_docs, get_doc_content
info = get_doc_info()
content = get_doc_content('ml_strategy')
```
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


# === MÉTADONNÉES DOCUMENTATION ===

__version__ = "3.0.0"
__author__ = "MIA Trading System Team"  
__email__ = "team@mia-trading.com"
__status__ = "Production"
__last_updated__ = "2025-06-25"

# === STRUCTURE DOCUMENTATION ===

DOCUMENTATION_STRUCTURE = {
    'architecture.md': {
        'title': 'Architecture MIA_IA_SYSTEM',
        'description': 'Documentation architecture technique complète',
        'version': '3.0.0',
        'topics': [
            'Vue d\'ensemble système',
            'Architecture modulaire', 
            'Flux données',
            'Méthode Battle Navale',
            'Pipeline automation',
            'Architecture ML',
            'Sécurité & robustesse'
        ],
        'audience': ['Développeurs', 'Architectes', 'DevOps'],
        'maintenance_frequency': 'Mensuelle'
    },
    
    'automation_guide.md': {
        'title': 'Guide Automation Battle Navale',
        'description': 'Guide complet automation du trading',
        'version': '3.0.0',
        'topics': [
            'Installation automation',
            'Configuration SimpleBattleNavaleTrader',
            'Monitoring temps réel',
            'Troubleshooting',
            'Optimisation performance'
        ],
        'audience': ['Traders', 'Opérateurs', 'Support'],
        'maintenance_frequency': 'Hebdomadaire'
    },
    
    'data_collection_guide.md': {
        'title': 'Guide Collection Données',
        'description': 'Guide collection données pour ML et analytics',
        'version': '3.0.0', 
        'topics': [
            'TradeSnapshotter setup',
            'Formats données',
            'Pipeline ETL',
            'Qualité données',
            'Export ML datasets'
        ],
        'audience': ['Data Scientists', 'ML Engineers', 'Analysts'],
        'maintenance_frequency': 'Bi-mensuelle'
    },
    
    'ml_strategy.md': {
        'title': 'Stratégie Machine Learning',
        'description': 'Stratégie ML progressive 2025-2026',
        'version': '3.0.0',
        'topics': [
            'Philosophie ML',
            'Approche progressive',
            'Architecture ML',
            'Pipeline données',
            'Modèles & objectifs',
            'Validation & sécurité',
            'Roadmap 2026'
        ],
        'audience': ['ML Engineers', 'Data Scientists', 'Management'],
        'maintenance_frequency': 'Trimestrielle'
    },
    
    'deployment_guide.md': {
        'title': 'Guide Déploiement Live',
        'description': 'Guide déploiement production live trading',
        'version': '3.0.0',
        'topics': [
            'Prérequis live trading',
            'Configuration production',
            'Procédures déploiement',
            'Monitoring production',
            'Incident response'
        ],
        'audience': ['DevOps', 'SRE', 'Operations'],
        'maintenance_frequency': 'Mensuelle'
    }
}

# === FONCTIONS UTILITAIRES ===

def get_docs_directory() -> Path:
    """Retourne le chemin du dossier docs"""
    return Path(__file__).parent

def get_doc_info() -> Dict[str, Any]:
    """Informations sur la documentation disponible"""
    return {
        'version': __version__,
        'author': __author__,
        'last_updated': __last_updated__,
        'status': __status__,
        'total_documents': len(DOCUMENTATION_STRUCTURE),
        'documents': list(DOCUMENTATION_STRUCTURE.keys()),
        'structure': DOCUMENTATION_STRUCTURE
    }

def validate_docs() -> Dict[str, Any]:
    """Valide que tous les documents existent et sont à jour"""
    docs_dir = get_docs_directory()
    validation_results = {
        'valid': True,
        'missing_files': [],
        'file_sizes': {},
        'last_modified': {},
        'validation_timestamp': datetime.now().isoformat()
    }
    
    for doc_name in DOCUMENTATION_STRUCTURE.keys():
        doc_path = docs_dir / doc_name
        
        if not doc_path.exists():
            validation_results['valid'] = False
            validation_results['missing_files'].append(doc_name)
        else:
            # File size
            validation_results['file_sizes'][doc_name] = doc_path.stat().st_size
            
            # Last modified
            mod_time = datetime.fromtimestamp(doc_path.stat().st_mtime)
            validation_results['last_modified'][doc_name] = mod_time.isoformat()
    
    return validation_results

def get_doc_content(doc_name: str) -> Optional[str]:
    """Lit le contenu d'un document"""
    docs_dir = get_docs_directory()
    
    # Ajouter .md si pas présent
    if not doc_name.endswith('.md'):
        doc_name += '.md'
    
    doc_path = docs_dir / doc_name
    
    if not doc_path.exists():
        return None
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.info("Erreur lecture {doc_name}: {e}")
        return None

def get_doc_summary(doc_name: str) -> Optional[Dict[str, Any]]:
    """Résumé d'un document spécifique"""
    if doc_name not in DOCUMENTATION_STRUCTURE:
        return None
    
    docs_dir = get_docs_directory()
    doc_path = docs_dir / doc_name
    
    summary = DOCUMENTATION_STRUCTURE[doc_name].copy()
    
    if doc_path.exists():
        stat = doc_path.stat()
        summary.update({
            'file_exists': True,
            'file_size_bytes': stat.st_size,
            'file_size_kb': round(stat.st_size / 1024, 2),
            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'path': str(doc_path)
        })
    else:
        summary.update({
            'file_exists': False,
            'error': f'File {doc_name} not found'
        })
    
    return summary

def generate_docs_index() -> str:
    """Génère un index de toute la documentation"""
    index = f"""# MIA_IA_SYSTEM - Documentation Index

**Version:** {__version__}  
**Dernière mise à jour:** {__last_updated__}  
**Statut:** {__status__}

## 📚 Documentation Disponible

"""
    
    for doc_name, info in DOCUMENTATION_STRUCTURE.items():
        index += f"""### [{info['title']}](./{doc_name})

**Description:** {info['description']}  
**Audience:** {', '.join(info['audience'])}  
**Maintenance:** {info['maintenance_frequency']}

**Sujets couverts:**
"""
        for topic in info['topics']:
            index += f"- {topic}\n"
        
        index += "\n---\n\n"
    
    return index

def export_docs_metadata() -> str:
    """Export métadonnées en JSON pour outils externes"""
    metadata = {
        'package_info': {
            'version': __version__,
            'author': __author__,
            'status': __status__,
            'last_updated': __last_updated__
        },
        'structure': DOCUMENTATION_STRUCTURE,
        'validation': validate_docs()
    }
    
    return json.dumps(metadata, indent=2, ensure_ascii=False)

def get_maintenance_schedule() -> Dict[str, List[str]]:
    """Planning maintenance documentation"""
    schedule = {
        'Hebdomadaire': [],
        'Bi-mensuelle': [],
        'Mensuelle': [],
        'Trimestrielle': []
    }
    
    for doc_name, info in DOCUMENTATION_STRUCTURE.items():
        frequency = info['maintenance_frequency']
        if frequency in schedule:
            schedule[frequency].append(doc_name)
    
    return schedule

# === API DOCUMENTATION ===

def get_all_topics() -> List[str]:
    """Liste tous les sujets couverts dans la documentation"""
    all_topics = []
    for info in DOCUMENTATION_STRUCTURE.values():
        all_topics.extend(info['topics'])
    return sorted(set(all_topics))

def search_docs(query: str) -> List[Dict[str, Any]]:
    """Recherche dans les titres et descriptions"""
    results = []
    query_lower = query.lower()
    
    for doc_name, info in DOCUMENTATION_STRUCTURE.items():
        relevance_score = 0
        
        # Check title
        if query_lower in info['title'].lower():
            relevance_score += 3
        
        # Check description  
        if query_lower in info['description'].lower():
            relevance_score += 2
        
        # Check topics
        for topic in info['topics']:
            if query_lower in topic.lower():
                relevance_score += 1
        
        if relevance_score > 0:
            result = info.copy()
            result['document'] = doc_name
            result['relevance_score'] = relevance_score
            results.append(result)
    
    # Sort by relevance
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)

# === EXPORTS ===

__all__ = [
    # Métadonnées
    '__version__',
    '__author__',
    '__status__',
    
    # Fonctions principales
    'get_doc_info',
    'validate_docs', 
    'get_doc_content',
    'get_doc_summary',
    
    # Utilitaires
    'generate_docs_index',
    'export_docs_metadata',
    'get_maintenance_schedule',
    'get_all_topics',
    'search_docs',
    
    # Structure
    'DOCUMENTATION_STRUCTURE'
]

# === TESTING ===

def test_docs_package():
    """Test rapide du package documentation"""
    logger.info("=== TEST DOCS PACKAGE ===")
    
    # Test 1: Info générale
    info = get_doc_info()
    logger.info("Documentation version {info['version']}")
    logger.info("{info['total_documents']} documents disponibles")
    
    # Test 2: Validation
    validation = validate_docs()
    if validation['valid']:
        logger.info("Tous les documents existent")
    else:
        logger.error("Documents manquants: {validation['missing_files']}")
    
    # Test 3: Test lecture
    ml_content = get_doc_content('ml_strategy')
    if ml_content:
        logger.info("ml_strategy.md lu: {len(ml_content)} caractères")
    else:
        logger.error("Impossible de lire ml_strategy.md")
    
    # Test 4: Recherche
    search_results = search_docs('ML')
    logger.info("Recherche 'ML': {len(search_results)} résultats")
    
    logger.info("=== TEST TERMINÉ ===")
    return True

if __name__ == "__main__":
    test_docs_package()