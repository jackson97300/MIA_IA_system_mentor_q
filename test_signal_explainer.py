#!/usr/bin/env python3
"""
Test rapide du Signal Explainer
Lancez avec: python test_signal_explainer.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.signal_explainer import SignalExplainer, ExplanationReason
from core.base_types import MarketData
import pandas as pd

def test_signal_explainer():
    """Test simple du Signal Explainer"""
    print("🧪 Test Signal Explainer...")
    
    # Créer le Signal Explainer
    explainer = SignalExplainer()
    
    # Simuler des données de marché
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=5247.0,
        high=5248.0,
        low=5246.0,
        close=5247.5,
        volume=1000
    )
    
    # Test 1: Confluence trop faible
    print("\n📊 Test 1: Confluence insuffisante")
    reasons = explainer.explain_no_signal(
        market_data=market_data,
        confluence_score=0.65,  # < 0.75 requis
        last_signal_time=0
    )
    
    explanation = explainer.format_explanation(reasons)
    print(explanation)
    
    # Test 2: Conditions OK
    print("\n📊 Test 2: Conditions OK")
    reasons = explainer.explain_no_signal(
        market_data=market_data,
        confluence_score=0.85,  # > 0.75 requis
        last_signal_time=0
    )
    
    explanation = explainer.format_explanation(reasons)
    print(explanation)
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    test_signal_explainer()