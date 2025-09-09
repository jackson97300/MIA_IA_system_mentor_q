# -*- coding: utf-8 -*-
"""
Tests de non-régression pour le bridge ES
"""
import json
import subprocess
import sys
import pytest

def run_bridge():
    """Exécute le bridge ES et retourne le code de sortie et la sortie"""
    proc = subprocess.run([sys.executable, "features/es_bias_bridge.py"], 
                         capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def test_bridge_exit_code():
    """Test que le bridge retourne un code de sortie valide (0 ou 2)"""
    code, out, err = run_bridge()
    assert code in (0, 2), f"Code de sortie inattendu {code}, out={out}, err={err}"

def test_bridge_payload_minimal():
    """Test que le bridge retourne un JSON valide avec les champs requis"""
    code, out, _ = run_bridge()
    data = json.loads(out)
    assert "status" in data
    
    if code == 0:
        assert data["ok"] is True
        assert set(["direction", "strength", "score"]) <= set(data.keys())
    else:
        assert data["ok"] is False

def test_bridge_json_structure():
    """Test la structure complète du JSON retourné"""
    code, out, _ = run_bridge()
    data = json.loads(out)
    
    # Champs obligatoires
    required_fields = ["ok", "status", "ts"]
    for field in required_fields:
        assert field in data, f"Champ manquant: {field}"
    
    # Si succès, champs supplémentaires requis
    if data["ok"]:
        success_fields = ["direction", "strength", "score", "underlying_price", "meta"]
        for field in success_fields:
            assert field in data, f"Champ de succès manquant: {field}"
        
        # Validation des valeurs
        assert data["status"] in ["ok", "partial"]
        assert data["direction"] in ["BULLISH", "BEARISH", "NEUTRAL"]
        assert data["strength"] in ["STRONG", "MODERATE", "WEAK", "UNKNOWN"]
        assert isinstance(data["score"], (int, float))
        assert isinstance(data["underlying_price"], (int, float))

def test_bridge_error_handling():
    """Test la gestion d'erreur du bridge"""
    # Le bridge devrait toujours retourner un JSON valide même en cas d'erreur
    code, out, _ = run_bridge()
    
    try:
        data = json.loads(out)
        assert "ok" in data
        assert "status" in data
    except json.JSONDecodeError:
        pytest.fail("Le bridge devrait toujours retourner un JSON valide")

if __name__ == "__main__":
    # Tests rapides en ligne de commande
    print("Tests du bridge ES...")
    
    code, out, err = run_bridge()
    print(f"Code de sortie: {code}")
    print(f"Sortie: {out}")
    if err:
        print(f"Erreur: {err}")
    
    if code == 0:
        print("✅ Bridge fonctionne correctement")
    else:
        print("⚠️ Bridge retourne une erreur (normal si pas de données)")











