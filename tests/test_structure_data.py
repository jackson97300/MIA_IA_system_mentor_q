import json
import pytest
from datetime import datetime, timezone

try:
    from structure_data import create_structure_data_processor, to_internal, TradeTick
except Exception as e:
    pytest.skip(f"'structure_data.py' manquant ou invalide: {e}", allow_module_level=True)

def test_prev_mapping_and_trade_conversion():
    proc = create_structure_data_processor()
    line = json.dumps({
        "type": "vva", "graph": 3, "sym": "ESU25_FUT_CME",
        "ts": datetime.now(timezone.utc).isoformat(),
        "vah": 6530.0, "val": 6520.0, "vpoc": 6526.0,
        "pvah": 6518.0, "pval": 6510.0, "ppoc": 6515.0,
    })
    evt = proc.process_line(line)
    assert evt is not None
    assert evt.get("prev_vah") == 6518.0
    assert evt.get("prev_vpoc") == 6515.0

    rec = to_internal({
        "type": "trade", "graph": 3, "sym": "ESU25_FUT_CME",
        "ts": datetime.now(timezone.utc).isoformat(),
        "px": 6534.25, "vol": 5,
    })
    assert isinstance(rec, TradeTick)
    assert rec.price == 6534.25
    assert rec.volume == 5

