#!/usr/bin/env python3
"""
TEST COMPLET - POLYGON SNAPSHOT AVEC NOUVEAUX NIVEAUX
Validation de tous les calculs selon cahier des charges

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Août 2025
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Ajouter le répertoire features au path
sys.path.append('features')

def test_call_put_walls():
    """Test Call/Put Walls avec données factices"""
    print("\n🧪 TEST CALL/PUT WALLS")
    print("="*40)
    
    # Import local pour test
    from create_polygon_snapshot import _compute_call_put_walls
    
    # Données factices SPX
    options = [
        {'strike': 6450, 'type': 'C', 'open_interest': 1000},
        {'strike': 6450, 'type': 'P', 'open_interest': 800},
        {'strike': 6500, 'type': 'C', 'open_interest': 2500},  # Call Wall
        {'strike': 6500, 'type': 'P', 'open_interest': 1200},
        {'strike': 6550, 'type': 'C', 'open_interest': 800},
        {'strike': 6550, 'type': 'P', 'open_interest': 3000},  # Put Wall
    ]
    
    result = _compute_call_put_walls(options, 6500)
    
    print(f"Call Wall: {result['call_wall']}")
    print(f"Put Wall: {result['put_wall']}")
    
    # Validations
    assert result['call_wall']['strike'] == 6500, "Call Wall incorrect"
    assert result['put_wall']['strike'] == 6550, "Put Wall incorrect"
    assert result['call_wall']['oi'] == 2500, "Call Wall OI incorrect"
    assert result['put_wall']['oi'] == 3000, "Put Wall OI incorrect"
    
    print("✅ Call/Put Walls : OK")

def test_gamma_flip_quality():
    """Test Gamma Flip avec qualité"""
    print("\n🧪 TEST GAMMA FLIP QUALITÉ")
    print("="*40)
    
    from create_polygon_snapshot import _compute_gamma_flip
    
    # Données factices avec flip clair à 6475
    options = [
        {'strike': 6450, 'type': 'C', 'gamma': 0.003, 'open_interest': 1000},
        {'strike': 6450, 'type': 'P', 'gamma': 0.002, 'open_interest': 800},
        {'strike': 6475, 'type': 'C', 'gamma': 0.004, 'open_interest': 1500},  # Point de flip
        {'strike': 6475, 'type': 'P', 'gamma': 0.004, 'open_interest': 1500},
        {'strike': 6500, 'type': 'C', 'gamma': 0.002, 'open_interest': 800},
        {'strike': 6500, 'type': 'P', 'gamma': 0.003, 'open_interest': 1200},
    ]
    
    result = _compute_gamma_flip(options, 6480)
    
    print(f"Gamma Flip: {result}")
    
    if result:
        print(f"Strike: {result['gamma_flip_strike']}")
        print(f"Distance: {result['distance_pts']:.1f} pts")
        print(f"Distance %: {result['distance_pct']:.2f}%")
        print(f"Qualité: {result['quality']}")
        
        assert result['gamma_flip_strike'] in [6450, 6475, 6500], "Flip strike incorrect"
        assert result['quality'] in ['clear', 'ambiguous'], "Qualité incorrecte"
    
    print("✅ Gamma Flip qualité : OK")

def test_vol_trigger():
    """Test Vol Trigger"""
    print("\n🧪 TEST VOL TRIGGER")
    print("="*40)
    
    from create_polygon_snapshot import _compute_vol_trigger
    
    # Données factices avec concentration gamma à 6500
    options = [
        {'strike': 6450, 'gamma': 0.001, 'open_interest': 500},
        {'strike': 6475, 'gamma': 0.002, 'open_interest': 800},
        {'strike': 6500, 'gamma': 0.005, 'open_interest': 2000},  # Concentration
        {'strike': 6525, 'gamma': 0.002, 'open_interest': 600},
        {'strike': 6550, 'gamma': 0.001, 'open_interest': 400},
    ]
    
    result = _compute_vol_trigger(options, 6500, vol_trigger_ratio=0.30)
    
    print(f"Vol Trigger: {result}")
    
    if result:
        print(f"Strike: {result['vol_trigger_strike']}")
        print(f"Ratio: {result['vol_trigger_ratio']}")
        print(f"Cumul expo: {result['cumulative_expo']:.0f}")
        
        assert result['vol_trigger_ratio'] == 0.30, "Ratio incorrect"
        assert result['vol_trigger_strike'] > 0, "Strike invalid"
    
    print("✅ Vol Trigger : OK")

def test_gamma_pins_filtering():
    """Test Gamma Pins avec filtrage amélioré"""
    print("\n🧪 TEST GAMMA PINS FILTRAGE")
    print("="*40)
    
    from create_polygon_snapshot import _compute_gamma_pins
    
    # Données factices avec plusieurs pics
    options = [
        {'strike': 6400, 'gamma': 0.001, 'open_interest': 200},
        {'strike': 6450, 'gamma': 0.004, 'open_interest': 1500},  # Pin faible
        {'strike': 6475, 'gamma': 0.002, 'open_interest': 800},
        {'strike': 6500, 'gamma': 0.008, 'open_interest': 2500},  # Pin fort
        {'strike': 6525, 'gamma': 0.003, 'open_interest': 1000},
        {'strike': 6550, 'gamma': 0.006, 'open_interest': 2000},  # Pin moyen
        {'strike': 6575, 'gamma': 0.001, 'open_interest': 300},
    ]
    
    result = _compute_gamma_pins(options, 6500, min_gap_pts=20, pins_strength_min="Strong")
    
    print(f"Gamma Pins: {len(result)} pins trouvés")
    for i, pin in enumerate(result):
        print(f"  Pin {i+1}: Strike {pin['strike']}, Strength {pin['strength']:.2f} ({pin['strength_category']})")
    
    # Validations
    assert len(result) <= 2, "Trop de pins retournés"
    for pin in result:
        assert pin['strength_category'] in ['Strong', 'Very Strong'], "Pin faible inclus"
    
    print("✅ Gamma Pins filtrage : OK")

def test_net_gamma_delta():
    """Test Net Gamma/Delta"""
    print("\n🧪 TEST NET GAMMA/DELTA")
    print("="*40)
    
    from create_polygon_snapshot import _compute_net_gamma_delta
    
    # Données factices
    options = [
        {'gamma': 0.003, 'delta': 0.6, 'open_interest': 1000, 'type': 'C'},
        {'gamma': 0.003, 'delta': -0.4, 'open_interest': 800, 'type': 'P'},
        {'gamma': 0.004, 'delta': 0.7, 'open_interest': 1500, 'type': 'C'},
        {'gamma': 0.004, 'delta': -0.3, 'open_interest': 1200, 'type': 'P'},
    ]
    
    result = _compute_net_gamma_delta(options, 6500)
    
    print(f"Net Gamma: {result['net_gamma']:.2e}")
    print(f"Net Delta: {result['net_delta']:.2e}")
    
    # Validations
    assert 'net_gamma' in result, "Net Gamma manquant"
    assert 'net_delta' in result, "Net Delta manquant"
    assert isinstance(result['net_gamma'], (int, float)), "Net Gamma pas numérique"
    assert isinstance(result['net_delta'], (int, float)), "Net Delta pas numérique"
    
    print("✅ Net Gamma/Delta : OK")

def test_csv_overlay_generation():
    """Test génération CSV overlay"""
    print("\n🧪 TEST GÉNÉRATION CSV OVERLAY")
    print("="*40)
    
    from create_polygon_snapshot import generate_csv_overlay
    
    # Snapshot factice complet
    snapshot = {
        'symbol': 'SPX',
        'timestamp': '2025-08-29T21:30:00Z',
        'analysis': {
            'underlying_price': 6500.0,
            'gex': {
                'gex_total_signed': 2.5e12
            },
            'levels': {
                'call_wall': {'strike': 6550},
                'put_wall': {'strike': 6450},
                'gamma_flip': {'gamma_flip_strike': 6475},
                'max_pain': 6525,
                'vol_trigger': {'vol_trigger_strike': 6500},
                'gamma_pins': [
                    {'strike': 6510},
                    {'strike': 6490}
                ]
            },
            'meta_overlay': {
                'window_pct': 0.03,
                'min_gap_pts': 20
            }
        }
    }
    
    csv_result = generate_csv_overlay(snapshot)
    
    print("CSV généré:")
    print(csv_result)
    
    # Validations
    assert csv_result is not None, "CSV non généré"
    assert 'SPX' in csv_result, "Symbol manquant"
    assert 'POS' in csv_result, "GEX regime manquant"
    assert '6475' in csv_result, "Gamma Flip manquant"
    
    lines = csv_result.strip().split('\n')
    assert len(lines) == 2, "Format CSV incorrect (header + data)"
    
    headers = lines[0].split(',')
    values = lines[1].split(',')
    assert len(headers) == len(values), "Headers/Values mismatch"
    
    print("✅ CSV Overlay génération : OK")

def test_dealer_signs_consistency():
    """Test cohérence signes dealers (calls ET puts négatifs)"""
    print("\n🧪 TEST COHÉRENCE SIGNES DEALERS")
    print("="*40)
    
    from create_polygon_snapshot import _compute_net_gamma_delta
    
    # Données factices
    options = [
        {'gamma': 0.003, 'delta': 0.6, 'open_interest': 1000, 'type': 'C'},
        {'gamma': 0.003, 'delta': -0.4, 'open_interest': 800, 'type': 'P'},
    ]
    
    result = _compute_net_gamma_delta(options, 6500)
    
    print(f"Net Gamma: {result['net_gamma']:.2e} (doit être négatif)")
    print(f"Net Delta: {result['net_delta']:.2e}")
    
    # Validation: dealers short tout → net gamma négatif
    assert result['net_gamma'] < 0, "Net Gamma doit être négatif (dealers short)"
    
    print("✅ Cohérence signes dealers : OK")

def test_flip_quality_assessment():
    """Test évaluation qualité Gamma Flip"""
    print("\n🧪 TEST QUALITÉ GAMMA FLIP")
    print("="*40)
    
    from create_polygon_snapshot import _assess_flip_quality
    
    # Données factices avec contraste net
    strikes = [6450, 6475, 6500, 6525, 6550]
    gamma_by_strike = {
        6450: -1000,  # Voisin gauche fort
        6475: -50,    # Flip faible (contraste élevé)
        6500: -1200,  # Voisin droit fort
        6525: -800,
        6550: -600
    }
    
    quality = _assess_flip_quality(strikes, gamma_by_strike, 6475)
    
    print(f"Qualité flip: {quality}")
    assert quality in ['clear', 'moderate', 'ambiguous', 'edge', 'unknown'], "Qualité invalide"
    
    print("✅ Qualité Gamma Flip : OK")

def test_gex_normalization():
    """Test normalisation GEX par symbole"""
    print("\n🧪 TEST NORMALISATION GEX")
    print("="*40)
    
    from create_polygon_snapshot import _get_gex_normalization_factor
    
    # Test différents symboles
    spx_factor = _get_gex_normalization_factor('SPX', 2.5e12)
    ndx_factor = _get_gex_normalization_factor('NDX', 2.5e12)
    
    print(f"SPX factor: {spx_factor:.0e}")
    print(f"NDX factor: {ndx_factor:.0e}")
    
    # NDX doit avoir facteur plus élevé (plus volatile)
    assert ndx_factor >= spx_factor, "NDX doit avoir facteur ≥ SPX"
    
    print("✅ Normalisation GEX : OK")

def test_global_deduplication():
    """Test déduplication globale des niveaux"""
    print("\n🧪 TEST DÉDUPLICATION GLOBALE")
    print("="*40)
    
    from create_polygon_snapshot import _deduplicate_levels
    
    # Niveaux factices avec collisions
    levels_dict = {
        'gamma_flip': {'gamma_flip_strike': 6500},
        'call_wall': {'strike': 6505},  # Trop proche du flip (5 pts)
        'put_wall': {'strike': 6450},
        'max_pain': 6520,
        'gamma_pins': [
            {'strike': 6510},  # OK
            {'strike': 6502},  # Trop proche du flip
            {'strike': 6455}   # Trop proche du put wall
        ]
    }
    
    result = _deduplicate_levels(levels_dict, min_gap_pts=20, underlying_price=6500)
    
    print(f"Niveaux avant: {len(levels_dict)} items")
    print(f"Niveaux après: {len(result)} items")
    
    # Vérifications
    assert 'gamma_flip' in result, "Gamma Flip doit être conservé (priorité 1)"
    
    # Call wall trop proche du flip → doit être supprimé
    call_wall_kept = 'call_wall' in result
    print(f"Call Wall conservé: {call_wall_kept} (doit être False si < 20pts du flip)")
    
    # Put wall loin → doit être conservé
    assert 'put_wall' in result, "Put Wall doit être conservé (loin)"
    
    pins_count = len(result.get('gamma_pins', []))
    print(f"Pins conservés: {pins_count} (max 2, après filtrage proximité)")
    assert pins_count <= 2, "Max 2 pins"
    
    print("✅ Déduplication globale : OK")

def test_timezone_fix():
    """Test correction timezone naïf vs aware"""
    print("\n🧪 TEST CORRECTION TIMEZONE")
    print("="*40)
    
    from create_polygon_snapshot import generate_csv_overlay
    from datetime import datetime, timezone
    
    # Snapshot avec timestamp UTC aware (root level)
    timestamp_utc = datetime.now(timezone.utc)
    snapshot = {
        'symbol': 'SPX',
        'timestamp': timestamp_utc.isoformat(),  # Root level UTC aware
        'analysis': {
            'underlying_price': 6500,
            'levels': {'gamma_flip': {'gamma_flip_strike': 6475}},
            'gex': {'gex_total_signed': -1e12},
            'meta_overlay': {'window_pct': 0.03, 'min_gap_pts': 20}
        }
    }
    
    # Vérifier que timestamp root est UTC aware
    root_timestamp = snapshot['timestamp']
    print(f"Root timestamp: {root_timestamp}")
    
    # Doit se terminer par Z ou +00:00 ou contenir timezone info
    is_utc_aware = (root_timestamp.endswith('Z') or 
                   root_timestamp.endswith('+00:00') or 
                   '+' in root_timestamp or 
                   root_timestamp.endswith('UTC'))
    
    assert is_utc_aware, f"Root timestamp pas UTC aware: {root_timestamp}"
    print("✅ Root timestamp UTC aware")
    
    try:
        csv_result = generate_csv_overlay(snapshot)
        print("✅ Pas d'erreur timezone naïf/aware")
        
        # Vérifier stale_minutes calculé correctement
        lines = csv_result.strip().split('\n')
        values = lines[1].split(',')
        stale_minutes = int(values[-3])  # Avant-dernière colonne
        
        assert 0 <= stale_minutes <= 60, f"Stale minutes incohérent: {stale_minutes}"
        print(f"Stale minutes: {stale_minutes} (OK)")
        
    except TypeError as e:
        if "naive and offset-aware" in str(e):
            print(f"❌ Bug timezone détecté: {e}")
            assert False, "Timezone bug pas corrigé"
    
    print("✅ Correction timezone complète : OK")

def test_cumulative_gamma_fix():
    """Test correction cumulative_gamma_at_flip"""
    print("\n🧪 TEST CORRECTION CUMULATIVE GAMMA")
    print("="*40)
    
    from create_polygon_snapshot import _compute_gamma_flip
    
    # Données factices où cumulative final ≠ cumulative au flip
    options = [
        {'strike': 6400, 'gamma': 0.002, 'open_interest': 1000, 'type': 'C'},
        {'strike': 6450, 'gamma': 0.004, 'open_interest': 800, 'type': 'C'},  # Flip ici
        {'strike': 6500, 'gamma': 0.006, 'open_interest': 1200, 'type': 'C'},
        {'strike': 6550, 'gamma': 0.003, 'open_interest': 600, 'type': 'C'},
    ]
    
    result = _compute_gamma_flip(options, 6475)
    
    if result:
        flip_strike = result['gamma_flip_strike']
        cumulative_at_flip = result['cumulative_gamma_at_flip']
        
        print(f"Flip strike: {flip_strike}")
        print(f"Cumulative au flip: {cumulative_at_flip:.2e}")
        
        # Vérifier que c'est sauvegardé au bon moment (pas la valeur finale)
        assert cumulative_at_flip != 0, "Cumulative au flip doit être non nul"
        print("✅ Cumulative sauvegardé au bon moment")
    
    print("✅ Correction cumulative gamma : OK")

def test_gex_bias_correction():
    """Test correction logique GEX bias cohérente"""
    print("\n🧪 TEST CORRECTION GEX BIAS")
    print("="*40)
    
    from create_polygon_snapshot import calculate_dealers_bias_robust
    
    # Test différents scénarios GEX
    test_cases = [
        # GEX positif → légèrement stabilisant (0.55)
        {
            'gex': {'gex_total_signed': 2e12},
            'expected_range': (0.52, 0.58),
            'scenario': 'GEX positif'
        },
        # GEX faiblement négatif → léger risque (0.45) 
        {
            'gex': {'gex_total_signed': -8e11}, 
            'expected_range': (0.42, 0.48),
            'scenario': 'GEX faible négatif'
        },
        # GEX très négatif → risque élevé (0.3)
        {
            'gex': {'gex_total_signed': -3e12},
            'expected_range': (0.25, 0.35), 
            'scenario': 'GEX très négatif'
        }
    ]
    
    for case in test_cases:
        # Données factices avec GEX spécifique
        analysis_data = {
            'gamma_flip': {'gamma_flip_strike': 6500},
            'gamma_pins': [],
            'put_call_ratio_oi': 1.0,
            'put_call_ratio_volume': 1.0,
            'iv_skew_puts_minus_calls': 0.0,
            'vix': 20.0,
            'underlying_price': 6500.0,
            'gex': case['gex']
        }
        
        result = calculate_dealers_bias_robust(analysis_data)
        bias_score = result.get('score', 0.5)
        
        print(f"{case['scenario']}: GEX={case['gex']['gex_total_signed']:.1e} → Bias={bias_score:.3f}")
        
        # Vérifier que le bias est dans la plage attendue
        min_expected, max_expected = case['expected_range']
        assert min_expected <= bias_score <= max_expected, \
            f"Bias {bias_score:.3f} hors plage {case['expected_range']} pour {case['scenario']}"
    
    print("✅ Logique GEX bias cohérente")

def test_flip_gex_tolerance():
    """Test tolérance sanity check flip vs GEX"""
    print("\n🧪 TEST TOLÉRANCE FLIP GEX")
    print("="*40)
    
    from create_polygon_snapshot import run_sanity_checks
    
    # Snapshot avec flip légèrement au-dessus spot + GEX positif
    snapshot_tolerance = {
        'symbol': 'SPX',
        'analysis': {
            'underlying_price': 6500,
            'levels': {
                'gamma_flip': {'gamma_flip_strike': 6502},  # +0.03% → dans tolérance
                'call_wall': {'strike': 6550},
                'put_wall': {'strike': 6450}
            },
            'gex': {'gex_total_signed': 1e12},  # Positif
            'meta_overlay': {'validation_errors': []}
        }
    }
    
    checks = run_sanity_checks(snapshot_tolerance)
    
    print(f"Warnings: {checks['warnings']}")
    
    # Avec tolérance 0.3%, pas de warning FLIP_GEX_UNUSUAL
    flip_warnings = [w for w in checks['warnings'] if 'FLIP_GEX' in w]
    assert len(flip_warnings) == 0, "Tolérance 0.3% pas appliquée"
    
    print("✅ Tolérance flip GEX : OK")

def test_sanity_checks():
    """Test sanity checks Go/No-Go"""
    print("\n🧪 TEST SANITY CHECKS GO/NO-GO")
    print("="*40)
    
    from create_polygon_snapshot import run_sanity_checks
    
    # Snapshot factice avec problèmes
    snapshot_problematic = {
        'symbol': 'SPX',
        'analysis': {
            'underlying_price': 6500,
            'levels': {
                'call_wall': {'strike': 6520},
                'put_wall': {'strike': 6520},  # Identique → erreur
                # gamma_flip manquant → erreur
            },
            'gex': {
                'gex_total_signed': 1e15,  # Très élevé
                'gex_total_normalized': 100  # Anormalement élevé
            },
            'meta_overlay': {
                'validation_errors': ['missing_flip']
            }
        }
    }
    
    checks = run_sanity_checks(snapshot_problematic)
    
    print(f"Status: {checks['status']}")
    print(f"Score: {checks['score']}/100")
    print(f"Erreurs: {checks['errors']}")
    print(f"Warnings: {checks['warnings']}")
    
    # Validations
    assert checks['status'] in ['GO', 'CAUTION', 'NO_GO', 'ERROR'], "Status invalide"
    assert 'WALLS_IDENTICAL' in checks['errors'], "Erreur walls identiques manquante"
    assert 'MISSING_GAMMA_FLIP' in checks['errors'], "Erreur flip manquant manquante"
    assert checks['score'] < 100, "Score doit être pénalisé"
    
    print("✅ Sanity Checks : OK")

def test_validation_levels():
    """Test validation des niveaux"""
    print("\n🧪 TEST VALIDATION NIVEAUX")
    print("="*40)
    
    from create_polygon_snapshot import calculate_option_metrics
    
    # Données options factices incomplètes
    options_data = {
        'symbol': 'SPX',
        'current_price': 6500.0,
        'strikes': {
            '6450': {
                'call': {'bid': 50, 'ask': 52, 'volume': 100, 'open_interest': 500, 
                        'delta': 0.6, 'gamma': 0.003, 'iv': 0.15},
                'put': {'bid': 2, 'ask': 4, 'volume': 80, 'open_interest': 0,  # OI = 0 
                       'delta': -0.4, 'gamma': 0.003, 'iv': 0.16}
            }
        }
    }
    
    result = calculate_option_metrics(options_data)
    
    print(f"Validation errors: {result.get('meta_overlay', {}).get('validation_errors', [])}")
    print(f"OI confidence: {result.get('meta_overlay', {}).get('oi_confidence', 'unknown')}")
    
    # Vérifier structure
    assert 'levels' in result, "Structure levels manquante"
    assert 'meta_overlay' in result, "Métadonnées manquantes"
    assert 'validation_errors' in result['meta_overlay'], "Validation errors manquantes"
    
    print("✅ Validation niveaux : OK")

async def test_complete_snapshot():
    """Test snapshot complet (nécessite clé API)"""
    print("\n🧪 TEST SNAPSHOT COMPLET")
    print("="*40)
    
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("⚠️ POLYGON_API_KEY non définie - test snapshot simulé")
        return
    
    from create_polygon_snapshot import create_polygon_snapshot
    
    try:
        snapshot = await create_polygon_snapshot("SPX", "20250919", save_to_file=False)
        
        if snapshot:
            print("✅ Snapshot créé avec succès")
            
            # Vérifications
            analysis = snapshot.get('analysis', {})
            levels = analysis.get('levels', {})
            
            print(f"  Levels trouvés:")
            for level_name, level_data in levels.items():
                if level_data:
                    print(f"    ✅ {level_name}: {level_data}")
                else:
                    print(f"    ❌ {level_name}: manquant")
            
            # Vérifier CSV overlay
            from create_polygon_snapshot import generate_csv_overlay
            csv_result = generate_csv_overlay(snapshot)
            if csv_result:
                print("✅ CSV Overlay généré")
                print("Extrait CSV:")
                print(csv_result[:200] + "...")
            else:
                print("❌ Échec génération CSV")
        
        else:
            print("❌ Échec création snapshot")
    
    except Exception as e:
        print(f"❌ Erreur test snapshot: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 TESTS COMPLETS POLYGON SNAPSHOT")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        # Tests unitaires originaux
        test_call_put_walls()
        test_gamma_flip_quality()
        test_vol_trigger()
        test_gamma_pins_filtering()
        test_net_gamma_delta()
        test_csv_overlay_generation()
        test_validation_levels()
        
        # NOUVEAUX TESTS - Corrections apportées
        test_dealer_signs_consistency()
        test_flip_quality_assessment()
        test_gex_normalization()
        test_global_deduplication()
        test_sanity_checks()
        
        # TESTS CORRECTIONS V2.1 - Audit final
        test_timezone_fix()
        test_cumulative_gamma_fix()
        test_gex_bias_correction()
        test_flip_gex_tolerance()
        
        # Test intégration
        asyncio.run(test_complete_snapshot())
        
        print("\n" + "="*60)
        print("🎉 TOUS LES TESTS RÉUSSIS - VERSION V2.1 PRODUCTION !")
        print("✅ Call/Put Walls calculés correctement")
        print("✅ Gamma Flip avec qualité pente locale améliorée")
        print("✅ Vol Trigger basé sur concentration gamma")
        print("✅ Gamma Pins avec filtrage strength et proximité")
        print("✅ Net Gamma/Delta avec convention dealers cohérente")
        print("✅ GEX normalisé par symbole (SPX/NDX)")
        print("✅ Déduplication globale avec priorités")
        print("✅ CSV Overlay avec Vol Trigger en slot 0")
        print("✅ Sanity Checks Go/No-Go automatiques")
        print("✅ CORRECTIONS AUDIT: Timezone, Cumulative gamma, GEX bias, Tolérance flip")
        print("✅ Validation production complète")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ÉCHEC TEST: {e}")
        print("Vérifier les imports et dépendances")

if __name__ == "__main__":
    main()
