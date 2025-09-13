#!/usr/bin/env python3
"""
Test complet du filtre de leadership amélioré
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from features.leadership_zmom import (
    LeadershipZMom, 
    BlockReason, 
    create_leadership_filter_enhanced
)

def test_leadership_filter_enhanced():
    """Test complet du filtre de leadership amélioré"""
    print("🚀 === TEST FILTRE DE LEADERSHIP AMÉLIORÉ ===\n")
    
    # Créer le filtre
    filter_enhanced = create_leadership_filter_enhanced()
    
    # Test 1: Signal aligné avec le leader (doit passer)
    print("🎯 Test 1: Signal aligné avec le leader")
    result1 = filter_enhanced.filter_signal(
        signal_score=0.8,      # Signal bullish fort
        leadership_gate=0.75,  # Leadership fort
        leader="ES",
        leader_trend=0.6,      # Leader bullish
        vix_level=20.0,
        vix_regime="normal"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result1.is_blocked else 'AUTORISÉ'}")
    print(f"   Message: {result1.block_message}")
    print(f"   Confiance: {result1.confidence:.3f}")
    
    # Test 2: Signal contra-trend avec leadership fort (doit être bloqué)
    print("\n🎯 Test 2: Signal contra-trend avec leadership fort")
    result2 = filter_enhanced.filter_signal(
        signal_score=-0.8,     # Signal bearish fort
        leadership_gate=0.75,  # Leadership fort
        leader="ES",
        leader_trend=0.6,      # Leader bullish
        vix_level=20.0,
        vix_regime="normal"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result2.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result2.block_reason.value if result2.block_reason else 'None'}")
    print(f"   Message: {result2.block_message}")
    
    # Test 3: Leadership faible (doit être bloqué)
    print("\n🎯 Test 3: Leadership faible")
    result3 = filter_enhanced.filter_signal(
        signal_score=0.8,
        leadership_gate=0.2,   # Leadership faible
        leader="ES",
        leader_trend=0.6,
        vix_level=20.0,
        vix_regime="normal"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result3.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result3.block_reason.value if result3.block_reason else 'None'}")
    print(f"   Message: {result3.block_message}")
    
    # Test 4: Signal faible (doit être bloqué)
    print("\n🎯 Test 4: Signal faible")
    result4 = filter_enhanced.filter_signal(
        signal_score=0.2,      # Signal faible
        leadership_gate=0.75,
        leader="ES",
        leader_trend=0.6,
        vix_level=20.0,
        vix_regime="normal"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result4.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result4.block_reason.value if result4.block_reason else 'None'}")
    print(f"   Message: {result4.block_message}")
    
    # Test 5: Régime VIX extrême (doit être plus strict)
    print("\n🎯 Test 5: Régime VIX extrême")
    result5 = filter_enhanced.filter_signal(
        signal_score=-0.6,     # Signal bearish modéré
        leadership_gate=0.6,   # Leadership modéré
        leader="ES",
        leader_trend=0.4,      # Leader bullish modéré
        vix_level=45.0,
        vix_regime="extreme"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result5.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result5.block_reason.value if result5.block_reason else 'None'}")
    print(f"   Message: {result5.block_message}")
    
    # Test 6: Pas de leader (doit être bloqué)
    print("\n🎯 Test 6: Pas de leader")
    result6 = filter_enhanced.filter_signal(
        signal_score=0.8,
        leadership_gate=0.75,
        leader=None,           # Pas de leader
        leader_trend=None,
        vix_level=20.0,
        vix_regime="normal"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result6.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result6.block_reason.value if result6.block_reason else 'None'}")
    print(f"   Message: {result6.block_message}")
    
    # Test 7: Tendance du leader inconnue (doit être bloqué)
    print("\n🎯 Test 7: Tendance du leader inconnue")
    result7 = filter_enhanced.filter_signal(
        signal_score=0.8,
        leadership_gate=0.75,
        leader="ES",
        leader_trend=None,     # Tendance inconnue
        vix_level=20.0,
        vix_regime="normal"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result7.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result7.block_reason.value if result7.block_reason else 'None'}")
    print(f"   Message: {result7.block_message}")
    
    # Test 8: Leadership modéré avec contre-tendance (doit être bloqué)
    print("\n🎯 Test 8: Leadership modéré avec contre-tendance")
    result8 = filter_enhanced.filter_signal(
        signal_score=-0.6,     # Signal bearish
        leadership_gate=0.55,  # Leadership modéré
        leader="NQ",
        leader_trend=0.4,      # Leader bullish
        vix_level=25.0,
        vix_regime="high_vix"
    )
    print(f"✅ Résultat: {'BLOQUÉ' if result8.is_blocked else 'AUTORISÉ'}")
    print(f"   Raison: {result8.block_reason.value if result8.block_reason else 'None'}")
    print(f"   Message: {result8.block_message}")
    
    # Statistiques finales
    print("\n📊 STATISTIQUES FINALES")
    stats = filter_enhanced.get_filter_stats()
    print(f"   Total signaux: {stats.total_signals}")
    print(f"   Signaux bloqués: {stats.blocked_signals}")
    print(f"   Taux de blocage: {stats.block_rate:.1%}")
    print(f"   Leadership moyen: {stats.avg_leadership_gate:.3f}")
    print(f"   Score moyen: {stats.avg_signal_score:.3f}")
    
    print("\n📋 Raisons de blocage:")
    for reason, count in stats.block_reasons.items():
        print(f"   {reason}: {count}")
    
    print("\n📋 Distribution du leadership:")
    for level, count in stats.leadership_distribution.items():
        print(f"   {level}: {count}")
    
    print("\n📋 Blocages par régime VIX:")
    for regime, count in stats.vix_regime_blocks.items():
        print(f"   {regime}: {count}")
    
    # Test des blocages récents
    print("\n🔍 Blocages récents:")
    recent_blocks = filter_enhanced.get_recent_blocks(5)
    for i, block in enumerate(recent_blocks, 1):
        print(f"   {i}. {block.block_reason.value if block.block_reason else 'Unknown'}: {block.block_message}")
    
    print(f"\n🎉 Test du filtre de leadership amélioré terminé!")
    print(f"✅ {stats.total_signals - stats.blocked_signals}/{stats.total_signals} signaux autorisés")
    print(f"🛡️ {stats.blocked_signals}/{stats.total_signals} signaux bloqués")

if __name__ == "__main__":
    test_leadership_filter_enhanced()

