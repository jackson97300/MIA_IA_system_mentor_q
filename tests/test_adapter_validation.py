# -*- coding: utf-8 -*-
"""
Tests de validation pour l'adaptateur Polygon SPX
"""
import asyncio
import pytest
from data.polygon_spx_adapter import PolygonSPXAdapter

@pytest.mark.asyncio
async def test_snapshot_status():
    """Test que le snapshot a un statut valide"""
    adapter = PolygonSPXAdapter()
    snap = await adapter.get_spx_snapshot_for_es()
    
    assert snap is not None, "Le snapshot ne devrait pas être None"
    assert snap["status"] in ("ok", "partial", "empty"), f"Statut invalide: {snap['status']}"
    
    if snap["status"] != "empty":
        assert "dealers_bias" in snap, "Dealer's Bias manquant pour un snapshot non-vide"

@pytest.mark.asyncio
async def test_snapshot_structure():
    """Test la structure complète du snapshot"""
    adapter = PolygonSPXAdapter()
    snap = await adapter.get_spx_snapshot_for_es()
    
    # Champs obligatoires
    required_fields = ["timestamp", "symbol", "underlying_price", "status", "dealers_bias", "meta"]
    for field in required_fields:
        assert field in snap, f"Champ obligatoire manquant: {field}"
    
    # Validation du dealers_bias
    bias = snap["dealers_bias"]
    bias_fields = ["score", "direction", "strength"]
    for field in bias_fields:
        assert field in bias, f"Champ dealers_bias manquant: {field}"
    
    # Validation des valeurs
    assert snap["symbol"] == "SPX"
    assert snap["status"] in ("ok", "partial", "empty")
    assert bias["direction"] in ("BULLISH", "BEARISH", "NEUTRAL")
    assert bias["strength"] in ("STRONG", "MODERATE", "WEAK", "UNKNOWN")
    assert isinstance(bias["score"], (int, float))

@pytest.mark.asyncio
async def test_entitlements_detection():
    """Test la détection des entitlements"""
    adapter = PolygonSPXAdapter()
    entitlements = await adapter.test_api_entitlement()
    
    assert isinstance(entitlements, dict), "Entitlements devrait être un dictionnaire"
    assert "stocks" in entitlements, "Champ stocks manquant"
    assert "options" in entitlements, "Champ options manquant"
    assert "indices" in entitlements, "Champ indices manquant"
    
    # Tous les champs doivent être des booléens
    for key, value in entitlements.items():
        assert isinstance(value, bool), f"Entitlement {key} devrait être un booléen"

@pytest.mark.asyncio
async def test_options_chain_validation():
    """Test la validation de la chaîne d'options"""
    adapter = PolygonSPXAdapter()
    
    # Détecter entitlements d'abord
    await adapter._probe_entitlements()
    
    if adapter.has_options:
        spx_data = await adapter.get_spx_options_chain()
        if spx_data:
            # Validation des données structurées
            assert hasattr(spx_data, 'calls'), "SPXOptionsData devrait avoir calls"
            assert hasattr(spx_data, 'puts'), "SPXOptionsData devrait avoir puts"
            assert hasattr(spx_data, 'status'), "SPXOptionsData devrait avoir status"
            assert spx_data.status in ("ok", "partial", "empty"), f"Statut invalide: {spx_data.status}"
            
            # Validation des métriques
            assert isinstance(spx_data.pcr_oi, (int, float)), "PCR OI devrait être numérique"
            assert isinstance(spx_data.pcr_volume, (int, float)), "PCR Volume devrait être numérique"
            assert isinstance(spx_data.iv_skew, (int, float)), "IV Skew devrait être numérique"

@pytest.mark.asyncio
async def test_dealers_bias_calculation():
    """Test le calcul du Dealer's Bias"""
    adapter = PolygonSPXAdapter()
    
    # Détecter entitlements d'abord
    await adapter._probe_entitlements()
    
    if adapter.has_options:
        spx_data = await adapter.get_spx_options_chain()
        if spx_data and spx_data.status != "empty":
            dealers_bias = await adapter.calculate_spx_dealers_bias(spx_data)
            
            if dealers_bias:
                # Validation de la structure
                assert hasattr(dealers_bias, 'bias_score'), "Dealer's Bias devrait avoir bias_score"
                assert hasattr(dealers_bias, 'direction'), "Dealer's Bias devrait avoir direction"
                assert hasattr(dealers_bias, 'strength'), "Dealer's Bias devrait avoir strength"
                
                # Validation des valeurs
                assert isinstance(dealers_bias.bias_score, (int, float)), "Score devrait être numérique"
                assert -1.0 <= dealers_bias.bias_score <= 1.0, "Score devrait être entre -1 et 1"
                assert dealers_bias.direction in ("BULLISH", "BEARISH", "NEUTRAL"), f"Direction invalide: {dealers_bias.direction}"
                assert dealers_bias.strength in ("STRONG", "MODERATE", "WEAK"), f"Force invalide: {dealers_bias.strength}"

if __name__ == "__main__":
    # Tests rapides en ligne de commande
    async def run_tests():
        print("Tests de validation de l'adaptateur...")
        
        adapter = PolygonSPXAdapter()
        
        # Test entitlements
        entitlements = await adapter.test_api_entitlement()
        print(f"Entitlements: {entitlements}")
        
        # Test snapshot
        snap = await adapter.get_spx_snapshot_for_es()
        if snap:
            print(f"Snapshot status: {snap['status']}")
            print(f"Dealer's Bias: {snap['dealers_bias']['direction']} {snap['dealers_bias']['strength']}")
            print("✅ Tests de validation réussis")
        else:
            print("❌ Échec de création du snapshot")
    
    asyncio.run(run_tests())











