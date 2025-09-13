import math
import pytest

try:
    from policies import (
        policy_latency, policy_drawdown, policy_vix_cap, policy_leadership_guard
    )
except Exception as e:
    pytest.skip(f"Policies indisponibles: {e}", allow_module_level=True)

def test_policy_latency_block():
    ctx = {"lag_ms": 2000}
    out = policy_latency(ctx, max_lag_ms=1500)
    assert out.status == "BLOCK"
    assert "Lag" in (out.reason or "")

def test_policy_latency_degrade():
    ctx = {"lag_ms": 1200}
    out = policy_latency(ctx, max_lag_ms=1000)
    assert out.status == "DEGRADE"
    assert ctx.get("latency_degrade") is None  # flag est renvoyé via out.data
    # On vérifie que la donnée est bien dans out.data
    assert out.data.get("latency_degrade") is True

def test_policy_drawdown_block():
    ctx = {"session_dd": -2.0}
    out = policy_drawdown(ctx, max_dd=-1.5)
    assert out.status == "BLOCK"

def test_policy_vix_cap_block():
    ctx = {"vix": 30.0}
    out = policy_vix_cap(ctx, vix_cap=28.0)
    assert out.status == "BLOCK"

def test_policy_leadership_guard_ok():
    ctx = {"leader": "NQ", "leader_bias": "BULL", "intended_side": "LONG"}
    out = policy_leadership_guard(ctx)
    assert out.status == "OK"

def test_policy_leadership_guard_block_short_against_bull():
    ctx = {"leader": "NQ", "leader_bias": "BULL", "intended_side": "SHORT"}
    out = policy_leadership_guard(ctx)
    assert out.status == "BLOCK"

