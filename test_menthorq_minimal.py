#!/usr/bin/env python3
"""Test minimal MenthorQ intégration"""

try:
    from features.confluence_integrator import ConfluenceIntegrator
    print("✅ Import OK")
    
    integrator = ConfluenceIntegrator()
    print("✅ ConfluenceIntegrator créé")
    
    if integrator.menthorq_bias_analyzer:
        print("✅ MenthorQ Bias Analyzer: OK")
    else:
        print("❌ MenthorQ Bias Analyzer: FAILED")
    
    print("🎉 Test terminé")
    
except Exception as e:
    print(f"❌ Erreur: {e}")


