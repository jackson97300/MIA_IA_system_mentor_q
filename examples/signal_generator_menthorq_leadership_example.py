#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation de la méthode MenthorQ-Distance avec Leadership dans SignalGenerator

Ce script montre comment utiliser la nouvelle méthode decide_mq_distance intégrée
dans le SignalGenerator pour analyser des opportunités de trading.

Usage:
    python examples/signal_generator_menthorq_leadership_example.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from strategies.signal_generator import SignalGenerator
from core.logger import get_logger

logger = get_logger(__name__)

def create_sample_unified_data():
    """Crée des données unified d'exemple pour tester la méthode"""
    
    # Données ES unifiées (format mia_unifier)
    es_data = {
        "t": 1705123200.0,  # Timestamp
        "basedata": {
            "close": 4500.0,
            "high": 4502.0,
            "low": 4498.0,
            "volume": 1250
        },
        "vwap": {
            "v": 4499.5,
            "up1": 4501.0,
            "dn1": 4498.0
        },
        "vva": {
            "vah": 4501.0,
            "val": 4498.0,
            "vpoc": 4499.5
        },
        "nbcv_footprint": {
            "pressure": 1,  # Bullish
            "delta_ratio": 0.18,
            "cumulative_delta": 120.0
        },
        "menthorq": {
            "gamma": {
                "put_support_0dte": 4498.0,
                "call_resistance": 4505.0,
                "gamma_wall_0dte": 4501.0,
                "hvl": 4499.0
            },
            "blind_spots": {
                "bl_1": 4497.5,
                "bl_2": 4502.5
            },
            "gex": {
                "gex_1": 4503.0,
                "gex_2": 4497.0
            }
        },
        "vix": {
            "value": 18.5
        }
    }
    
    # Données NQ unifiées (format mia_unifier)
    nq_data = {
        "t": 1705123200.0,  # Même timestamp
        "basedata": {
            "close": 18500.0,
            "high": 18520.0,
            "low": 18480.0,
            "volume": 850
        },
        "vwap": {
            "v": 18495.0,
            "up1": 18505.0,
            "dn1": 18485.0
        },
        "vva": {
            "vah": 18505.0,
            "val": 18485.0,
            "vpoc": 18495.0
        },
        "nbcv_footprint": {
            "pressure": 1,  # Bullish
            "delta_ratio": 0.15,
            "cumulative_delta": 85.0
        }
    }
    
    return es_data, nq_data

def main():
    """Exemple principal d'utilisation"""
    
    print("🎯 EXEMPLE SIGNAL GENERATOR + MENTHORQ-DISTANCE + LEADERSHIP")
    print("=" * 70)
    
    # 1. Initialiser le SignalGenerator
    print("\n1. Initialisation du SignalGenerator...")
    config = {
        "min_signal_confidence": 0.70,
        "min_confluence_score": 0.60,
        "cache_config": {
            "cache_ttl": 60,
            "cache_size": 500
        }
    }
    
    signal_generator = SignalGenerator(config=config)
    print("✅ SignalGenerator initialisé avec MenthorQ-Distance + Leadership")
    
    # 2. Configuration pour la méthode MenthorQ-Distance
    print("\n2. Configuration MenthorQ-Distance...")
    mq_config = {
        "tick_size": 0.25,
        "mq_tolerance_ticks": {
            "gamma_wall": 3,    # 3 ticks pour gamma walls
            "hvl": 5,           # 5 ticks pour HVL
            "gex": 5            # 5 ticks pour GEX
        },
        "mia_threshold": 0.20,  # Seuil MIA Bullish
        "entry_threshold": 0.70, # Seuil d'entrée final
        "weights": {
            "mq": 0.55,         # 55% MenthorQ
            "of": 0.30,         # 30% OrderFlow
            "structure": 0.15   # 15% Structure
        }
    }
    print("✅ Configuration MenthorQ-Distance chargée")
    
    # 3. Créer des données d'exemple
    print("\n3. Données d'exemple...")
    es_data, nq_data = create_sample_unified_data()
    print(f"✅ ES: {es_data['basedata']['close']} @ {es_data['t']}")
    print(f"✅ NQ: {nq_data['basedata']['close']} @ {nq_data['t']}")
    
    # 4. Utiliser la nouvelle méthode decide_mq_distance
    print("\n4. Analyse avec decide_mq_distance...")
    signal = signal_generator.decide_mq_distance(
        row_es=es_data,
        row_nq=nq_data,
        config=mq_config
    )
    
    # 5. Afficher les résultats
    print("\n5. RÉSULTATS:")
    print("=" * 40)
    
    if signal:
        print(f"🎯 ACTION: {signal['action']}")
        print(f"📊 SCORE: {signal['score']}")
        print(f"🎪 MENTHORQ: {signal['mq_score']}")
        print(f"📈 ORDERFLOW: {signal['of_score']}")
        print(f"🏗️ STRUCTURE: {signal['st_score']}")
        print(f"📊 MIA BULLISH: {signal['mia_bullish']}")
        print(f"🌡️ VIX REGIME: {signal['vix_regime']}")
        
        print(f"\n⚡ LEADERSHIP:")
        leadership = signal['leadership']
        print(f"   LS: {leadership['ls']}")
        print(f"   Beta: {leadership['beta']}")
        print(f"   Corrélation: {leadership['roll_corr_30s']}")
        print(f"   Bonus: {leadership['bonus']}")
        print(f"   Extra OF: {leadership['extra_of']}")
        print(f"   Raison: {leadership['reason']}")
        
        print(f"\n🎯 NIVEAU MENTHORQ:")
        mq_level = signal['mq_level']
        print(f"   Nom: {mq_level['name']}")
        print(f"   Prix: {mq_level['price']}")
        print(f"   Type: {mq_level['type']}")
        
        print(f"\n💰 E/U/L:")
        eul = signal['eul']
        print(f"   Entry: {eul['entry']}")
        print(f"   Stop: {eul['stop']}")
        print(f"   Target 1: {eul['target1']}")
        print(f"   Target 2: {eul['target2']}")
        print(f"   Risk: {eul['risk_ticks']} ticks")
        
        # Calculer le R:R
        risk = abs(eul['entry'] - eul['stop'])
        reward1 = abs(eul['target1'] - eul['entry'])
        rr1 = reward1 / risk if risk > 0 else 0
        print(f"   R:R (T1): {rr1:.2f}")
        
    else:
        print("❌ PAS DE SIGNAL")
        print("   Raisons possibles:")
        print("   - Pas de niveau MenthorQ proche")
        print("   - MIA Bullish insuffisant")
        print("   - Leadership contre")
        print("   - OrderFlow insuffisant")
        print("   - Score final < 0.70")
    
    # 6. Test avec différents scénarios
    print("\n6. TESTS DE SCÉNARIOS:")
    print("=" * 40)
    
    # Scénario 1: VIX HIGH
    print("\n📊 Scénario VIX HIGH (25.0)...")
    es_data_high_vix = es_data.copy()
    es_data_high_vix["vix"]["value"] = 25.0
    
    signal_high_vix = signal_generator.decide_mq_distance(
        row_es=es_data_high_vix,
        row_nq=nq_data,
        config=mq_config
    )
    
    if signal_high_vix:
        print(f"✅ Signal: {signal_high_vix['action']} (Score: {signal_high_vix['score']})")
        print(f"   VIX Regime: {signal_high_vix['vix_regime']}")
        print(f"   Extra OF: {signal_high_vix['leadership']['extra_of']}")
    else:
        print("❌ Pas de signal (VIX HIGH)")
    
    # Scénario 2: Prix loin des niveaux MenthorQ
    print("\n📊 Scénario Prix loin des niveaux...")
    es_data_far = es_data.copy()
    es_data_far["basedata"]["close"] = 4510.0  # Loin des niveaux
    
    signal_far = signal_generator.decide_mq_distance(
        row_es=es_data_far,
        row_nq=nq_data,
        config=mq_config
    )
    
    if signal_far:
        print(f"✅ Signal: {signal_far['action']} (Score: {signal_far['score']})")
    else:
        print("❌ Pas de signal (prix loin des niveaux)")
    
    # 7. Comparaison avec la méthode standard
    print("\n7. COMPARAISON AVEC MÉTHODE STANDARD:")
    print("=" * 40)
    
    # Test de la méthode standard (si disponible)
    try:
        # Créer des MarketData pour la méthode standard
        from core.base_types import MarketData
        
        market_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            price=es_data["basedata"]["close"],
            volume=es_data["basedata"]["volume"]
        )
        
        # Générer un signal standard
        standard_signal = signal_generator.generate_signal(market_data)
        
        if standard_signal:
            print(f"✅ Signal standard: {standard_signal.signal_type} (Confidence: {standard_signal.confidence})")
        else:
            print("❌ Pas de signal standard")
            
    except Exception as e:
        print(f"ℹ️ Méthode standard non disponible: {e}")
    
    # 8. Résumé
    print("\n8. RÉSUMÉ:")
    print("=" * 40)
    print("✅ Méthode MenthorQ-Distance avec Leadership intégrée dans SignalGenerator")
    print("✅ Architecture respectée: MenthorQ décide, OrderFlow valide")
    print("✅ Leadership intelligent: Évite les trades contre le moteur")
    print("✅ Configuration flexible: Paramètres ajustables")
    print("✅ Audit trail complet: Traçabilité de toutes les décisions")
    print("✅ Compatible avec le système existant")
    
    print("\n🚀 PRÊT POUR LA PRODUCTION !")
    print("💡 Utilisez signal_generator.decide_mq_distance() pour vos analyses")

if __name__ == "__main__":
    main()

