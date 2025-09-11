#!/usr/bin/env python3
"""
Test simple de l'interface SPXBiasSource
"""

import asyncio
from features.spx_bias_source import SPXBiasSourceFactory

async def test_spx_interface():
    """Test de l'interface SPXBiasSource"""
    print("🧪 Test de l'interface SPXBiasSource...")
    
    # Test Mock Source
    print("📋 Test MockSPXSource...")
    source = SPXBiasSourceFactory.create_source('mock')
    print(f"✅ Source créée: {type(source).__name__}")
    
    # Test snapshot
    snapshot = await source.get_spx_snapshot_for_es()
    if snapshot:
        print(f"✅ Snapshot mock: {snapshot['dealers_bias']['direction']} {snapshot['dealers_bias']['strength']}")
        print(f"📊 Score: {snapshot['dealers_bias']['score']:.3f}")
        print(f"💰 Prix SPX: {snapshot['underlying_price']}")
    else:
        print("❌ Échec snapshot mock")
    
    # Test Polygon Source (si disponible)
    print("\n📋 Test PolygonSPXSource...")
    polygon_source = SPXBiasSourceFactory.create_source('polygon')
    print(f"✅ Source Polygon créée: {type(polygon_source).__name__}")
    
    # Test entitlements
    entitlements = await polygon_source.test_api_entitlement()
    print(f"🔑 Entitlements: {entitlements}")
    
    if entitlements['options']:
        snapshot = await polygon_source.get_spx_snapshot_for_es()
        if snapshot:
            print(f"✅ Snapshot Polygon: {snapshot['dealers_bias']['direction']} {snapshot['dealers_bias']['strength']}")
        else:
            print("❌ Échec snapshot Polygon")
    else:
        print("⚠️ Options non disponibles - test Polygon SKIPPED")
    
    print("\n🎉 Test interface SPXBiasSource terminé avec succès!")

if __name__ == "__main__":
    asyncio.run(test_spx_interface())


