import os
import sys
import types
import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# 1) Désactiver l'autoload de plugins tiers (cause fréquente du crash capture sous Py3.13/Windows)
# NOTE: idéalement à poser dans l'environnement avant pytest, mais on sécurise ici aussi.
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

# 2) Neutraliser les imports "live" (IBKR/TWS, etc.)
os.environ.setdefault("MIA_DISABLE_LIVE_IMPORTS", "1")

# 3) Stubs légers si certains modules externes sont importés pendant la découverte
STUBS = [
    "ibapi", "ibapi.client", "ibapi.wrapper",
    "ibkr_connector",  # si ton code importe ce nom directement
]
for name in STUBS:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

# 4) Marqueur commun pour skipper clean si certains modules internes n'ont pas encore été copiés
def require_module(modname: str):
    try:
        __import__(modname)
        return pytest.mark.skipif(False, reason="")
    except Exception as e:
        return pytest.mark.skip(reason=f"Module '{modname}' introuvable ou invalide: {e}")

# === FIXTURES POUR LES TESTS ===

@pytest.fixture
def sample_basedata_event() -> Dict[str, Any]:
    """Événement de données de base d'exemple"""
    return {
        "ts": "2025-01-07T10:30:00Z",
        "sym": "ESU25_FUT_CME",
        "chart": "3",
        "type": "basedata",
        "open": 5295.0,
        "high": 5297.0,
        "low": 5293.0,
        "close": 5295.5,
        "volume": 1000
    }

@pytest.fixture
def sample_vwap_event() -> Dict[str, Any]:
    """Événement VWAP d'exemple"""
    return {
        "ts": "2025-01-07T10:30:00Z",
        "sym": "ESU25_FUT_CME",
        "chart": "3",
        "type": "vwap",
        "vwap": 5294.5,
        "volume": 1000,
        "sd1_up": 5296.0,
        "sd1_dn": 5293.0
    }

@pytest.fixture
def sample_vix_event() -> Dict[str, Any]:
    """Événement VIX d'exemple"""
    return {
        "ts": "2025-01-07T10:30:00Z",
        "sym": "VIX",
        "chart": "8",
        "type": "vix",
        "last": 15.2,
        "policy": "normal"
    }

@pytest.fixture
def sample_menthorq_event() -> Dict[str, Any]:
    """Événement MenthorQ d'exemple"""
    return {
        "ts": "2025-01-07T10:30:00Z",
        "sym": "ESU25_FUT_CME",
        "chart": "10",
        "type": "menthorq_gamma_levels",
        "levels": [
            {
                "label": "SG1",
                "price": 5300.0,
                "type": "CALL",
                "strength": 0.8,
                "distance_ticks": 20
            },
            {
                "label": "SG2",
                "price": 5290.0,
                "type": "PUT",
                "strength": 0.6,
                "distance_ticks": 15
            }
        ]
    }

@pytest.fixture
def sample_jsonl_file(sample_basedata_event, sample_vwap_event, sample_vix_event) -> Path:
    """Fichier JSONL d'exemple avec plusieurs événements"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        events = [sample_basedata_event, sample_vwap_event, sample_vix_event]
        for event in events:
            f.write(json.dumps(event) + '\n')
        return Path(f.name)

@pytest.fixture
def sample_unified_events(
    sample_basedata_event,
    sample_vwap_event,
    sample_vix_event,
    sample_menthorq_event
) -> List[Dict[str, Any]]:
    """Liste d'événements unifiés d'exemple"""
    return [
        sample_basedata_event,
        sample_vwap_event,
        sample_vix_event,
        sample_menthorq_event
    ]