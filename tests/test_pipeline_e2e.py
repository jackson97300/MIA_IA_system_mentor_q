import pytest

# On autorise le skip si le micro-pipeline n'a pas encore été copié
try:
    from build_pipeline import build_default_pipeline
except Exception as e:
    pytest.skip(f"Pipeline indisponible: {e}", allow_module_level=True)

def test_block_on_latency_and_send_order_when_ok():
    pipe = build_default_pipeline()

    # Cas 1: lag élevé -> BLOCK -> NO_ORDER
    ctx1 = {
        "snapshot": {"lag_ms": 2000},
        "price": 6534.25,
        "levels": {"put_support": 6533.0, "call_resistance": 6536.0},
        "cfg_max_lag": 1500,
    }
    out1 = pipe.run(ctx1)
    assert out1.get("decision", {}).get("action") == "NO_ORDER"

    # Cas 2: lag OK + put_support proche -> signal LONG -> SEND_ORDER
    ctx2 = {
        "snapshot": {"lag_ms": 100},
        "price": 6534.0,
        "levels": {"put_support": 6533.5},
        "cfg_dist_thresh": 1.0,
        "cfg_base_qty": 2,
    }
    out2 = pipe.run(ctx2)
    assert out2.get("decision", {}).get("action") == "SEND_ORDER"
    assert out2["decision"]["side"] == "LONG"
    # sizing par défaut (pas de DEGRADE)
    assert out2.get("order_qty") == 2

