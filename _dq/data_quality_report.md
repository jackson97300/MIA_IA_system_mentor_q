# MIA Data Quality Report

- Root: `D:\MIA_IA_system`
- Generated: `2025-09-12T15:57:28.913545Z`
- Files scanned: **50**

## Aggregate

- **lines_total**: 9304939
- **lines_valid_json**: 9304939
- **invalid_json**: 0
- **lines_with_ts**: 0
- **lines_with_symbol**: 0
- **monotonic_ts_violations**: 0
- **dupe_keys**: 3125258

## Per-Chart Aggregate

### Chart 10
- lines_total: 51778
- lines_valid_json: 51778
- invalid_json: 0
- lines_with_ts: 0
- lines_with_symbol: 0
- monotonic_ts_violations: 0
- dupe_keys: 51775

### Chart 3
- lines_total: 7984659
- lines_valid_json: 7984659
- invalid_json: 0
- lines_with_ts: 0
- lines_with_symbol: 0
- monotonic_ts_violations: 0
- dupe_keys: 1810811

### Chart 4
- lines_total: 1088792
- lines_valid_json: 1088792
- invalid_json: 0
- lines_with_ts: 0
- lines_with_symbol: 0
- monotonic_ts_violations: 0
- dupe_keys: 1082965

### Chart 8
- lines_total: 179710
- lines_valid_json: 179710
- invalid_json: 0
- lines_with_ts: 0
- lines_with_symbol: 0
- monotonic_ts_violations: 0
- dupe_keys: 179707


## Files

### chart_10_20250910.jsonl (chart 10)
- lines_total: 1184 | valid_json: 1184 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 1183
- missing_keys (top): {"blind_spots": 1184, "gex": 1184, "ts": 1184, "symbol": 1184, "hvl": 1184, "dealers_bias": 1184, "gamma_resistance": 1184, "gamma_support": 1184}
- price_summary: {'count': 832, 'min': 6261.25, 'p25': 6500.0, 'median': 6530.75, 'p75': 6570.0, 'max': 6778.75}

### chart_10_menthorq_20250911.jsonl (chart 10)
- lines_total: 50424 | valid_json: 50424 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 50423
- missing_keys (top): {"blind_spots": 50424, "gex": 50424, "ts": 50424, "symbol": 50424, "hvl": 50424, "dealers_bias": 50424, "gamma_resistance": 50424, "gamma_support": 50424}
- price_summary: {'count': 14898, 'min': 6416.75, 'p25': 6500.0, 'median': 6555.0, 'p75': 6585.75, 'max': 6634.0}

### chart_10_menthorq_20250912.jsonl (chart 10)
- lines_total: 170 | valid_json: 170 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 169
- missing_keys (top): {"blind_spots": 170, "gex": 170, "ts": 170, "symbol": 170, "hvl": 170, "dealers_bias": 170, "gamma_resistance": 170, "gamma_support": 170}
- price_summary: {'count': 34, 'min': 6400.0, 'p25': 6545.0, 'median': 6575.0, 'p75': 6625.0, 'max': 6675.0}

### chart_3_20250910.jsonl (chart 3)
- lines_total: 32 | valid_json: 32 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 31
- missing_keys (top): {"delta": 32, "ts": 32, "symbol": 32, "ask_volume": 32, "last_price": 32, "ask": 32, "bid_volume": 32, "bid": 32}

### chart_3_basedata_20250911.jsonl (chart 3)
- lines_total: 91060 | valid_json: 91060 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91059
- missing_keys (top): {"delta": 91060, "ts": 91060, "symbol": 91060, "ask_volume": 91060, "last_price": 91060, "ask": 91060, "bid_volume": 91060, "bid": 91060}

### chart_3_basedata_20250912.jsonl (chart 3)
- lines_total: 310 | valid_json: 310 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 309
- missing_keys (top): {"delta": 310, "ts": 310, "symbol": 310, "ask_volume": 310, "last_price": 310, "ask": 310, "bid_volume": 310, "bid": 310}

### chart_3_bull_20250911.jsonl (chart 3)
- lines_total: 44036 | valid_json: 44036 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 44035
- missing_keys (top): {"delta": 44036, "ts": 44036, "symbol": 44036, "ask_volume": 44036, "last_price": 44036, "ask": 44036, "bid_volume": 44036, "bid": 44036}

### chart_3_combined_20250911.jsonl (chart 3)
- lines_total: 49981 | valid_json: 49981 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 49980
- missing_keys (top): {"ts": 49981, "symbol": 49981, "last_price": 49981, "ask": 49981, "bid": 49981, "seq": 49981, "delta": 49926, "ask_volume": 49926}

### chart_3_combined_full.jsonl (chart 3)
- lines_total: 127588 | valid_json: 127588 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 127587
- missing_keys (top): {"ts": 127588, "symbol": 127588, "last_price": 127588, "ask": 127588, "bid": 127588, "seq": 127588, "delta": 127402, "ask_volume": 127402}

### chart_3_combined_rebuilt_20250911.jsonl (chart 3)
- lines_total: 846741 | valid_json: 846741 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 215369
- issues: {"bid_gt_ask": 70}
- missing_keys (top): {"ts": 846741, "symbol": 846741, "last_price": 846741, "delta": 846676, "ask_volume": 846676, "bid_volume": 846676, "ask": 210370, "bid": 210370}
- price_summary: {'count': 151178, 'min': 6532.25, 'p25': 6548.25, 'median': 6552.5, 'p75': 6555.5, 'max': 6566.5}

### chart_3_cumulative_delta_20250911.jsonl (chart 3)
- lines_total: 91026 | valid_json: 91026 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91025
- missing_keys (top): {"delta": 91026, "ts": 91026, "symbol": 91026, "ask_volume": 91026, "last_price": 91026, "ask": 91026, "bid_volume": 91026, "bid": 91026}

### chart_3_cumulative_delta_20250912.jsonl (chart 3)
- lines_total: 336 | valid_json: 336 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 335
- missing_keys (top): {"delta": 336, "ts": 336, "symbol": 336, "ask_volume": 336, "last_price": 336, "ask": 336, "bid_volume": 336, "bid": 336}

### chart_3_depth_20250911.jsonl (chart 3)
- lines_total: 998742 | valid_json: 998742 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 998741
- missing_keys (top): {"delta": 998742, "ts": 998742, "symbol": 998742, "ask_volume": 998742, "last_price": 998742, "ask": 998742, "bid_volume": 998742, "bid": 998742}
- price_summary: {'count': 998742, 'min': 6532.25, 'p25': 6567.5, 'median': 6586.25, 'p75': 6591.0, 'max': 6604.5}

### chart_3_depth_20250912.jsonl (chart 3)
- lines_total: 3263 | valid_json: 3263 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 3262
- missing_keys (top): {"delta": 3263, "ts": 3263, "symbol": 3263, "ask_volume": 3263, "last_price": 3263, "ask": 3263, "bid_volume": 3263, "bid": 3263}
- price_summary: {'count': 3263, 'min': 6582.25, 'p25': 6586.25, 'median': 6588.0, 'p75': 6589.5, 'max': 6593.5}

### chart_3_nbcv_20250911.jsonl (chart 3)
- lines_total: 310 | valid_json: 310 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 309
- missing_keys (top): {"ts": 310, "symbol": 310, "last_price": 310, "ask": 310, "bid": 310, "seq": 310}

### chart_3_nbcv_20250912.jsonl (chart 3)
- lines_total: 358 | valid_json: 358 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 357
- missing_keys (top): {"ts": 358, "symbol": 358, "last_price": 358, "ask": 358, "bid": 358, "seq": 358}

### chart_3_pvwap_20250911.jsonl (chart 3)
- lines_total: 241 | valid_json: 241 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 240
- missing_keys (top): {"delta": 241, "ts": 241, "symbol": 241, "ask_volume": 241, "last_price": 241, "ask": 241, "bid_volume": 241, "bid": 241}

### chart_3_pvwap_20250912.jsonl (chart 3)
- lines_total: 3 | valid_json: 3 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 2
- missing_keys (top): {"delta": 3, "ts": 3, "symbol": 3, "ask_volume": 3, "last_price": 3, "ask": 3, "bid_volume": 3, "bid": 3}

### chart_3_quote_20250911.jsonl (chart 3)
- lines_total: 5520573 | valid_json: 5520573 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 5000
- issues: {"bid_gt_ask": 134}
- missing_keys (top): {"delta": 5520573, "ts": 5520573, "symbol": 5520573, "ask_volume": 5520573, "last_price": 5520573, "bid_volume": 5520573}

### chart_3_quote_20250912.jsonl (chart 3)
- lines_total: 26885 | valid_json: 26885 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- missing_keys (top): {"delta": 26885, "ts": 26885, "symbol": 26885, "ask_volume": 26885, "last_price": 26885, "bid_volume": 26885}

### chart_3_vva_20250911.jsonl (chart 3)
- lines_total: 91060 | valid_json: 91060 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91059
- missing_keys (top): {"delta": 91060, "ts": 91060, "symbol": 91060, "ask_volume": 91060, "last_price": 91060, "ask": 91060, "bid_volume": 91060, "bid": 91060}

### chart_3_vva_20250912.jsonl (chart 3)
- lines_total: 515 | valid_json: 515 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 514
- missing_keys (top): {"delta": 515, "ts": 515, "symbol": 515, "ask_volume": 515, "last_price": 515, "ask": 515, "bid_volume": 515, "bid": 515}

### chart_3_vwap_20250911.jsonl (chart 3)
- lines_total: 91060 | valid_json: 91060 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91059
- missing_keys (top): {"delta": 91060, "ts": 91060, "symbol": 91060, "ask_volume": 91060, "last_price": 91060, "ask": 91060, "bid_volume": 91060, "bid": 91060}

### chart_3_vwap_20250912.jsonl (chart 3)
- lines_total: 539 | valid_json: 539 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 538
- missing_keys (top): {"delta": 539, "ts": 539, "symbol": 539, "ask_volume": 539, "last_price": 539, "ask": 539, "bid_volume": 539, "bid": 539}

### chart_4_20250909.jsonl (chart 4)
- lines_total: 176426 | valid_json: 176426 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 174777
- missing_keys (top): {"VAH": 176426, "session": 176426, "ts": 176426, "VAL": 176426, "symbol": 176426, "POC": 176426, "vwap": 176426}
- price_summary: {'count': 1336, 'min': 6525.25, 'p25': 6529.25, 'median': 6532.0, 'p75': 6534.5, 'max': 6538.25}

### chart_4_20250910.jsonl (chart 4)
- lines_total: 16632 | valid_json: 16632 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 12475
- missing_keys (top): {"VAH": 16632, "session": 16632, "ts": 16632, "VAL": 16632, "symbol": 16632, "POC": 16632, "vwap": 12476}

### chart_4_atr_20250911.jsonl (chart 4)
- lines_total: 91607 | valid_json: 91607 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91606
- missing_keys (top): {"VAH": 91607, "session": 91607, "ts": 91607, "VAL": 91607, "symbol": 91607, "POC": 91607, "vwap": 91607}

### chart_4_atr_20250912.jsonl (chart 4)
- lines_total: 516 | valid_json: 516 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 515
- missing_keys (top): {"VAH": 516, "session": 516, "ts": 516, "VAL": 516, "symbol": 516, "POC": 516, "vwap": 516}

### chart_4_correlation_20250911.jsonl (chart 4)
- lines_total: 62828 | valid_json: 62828 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 62827
- missing_keys (top): {"VAH": 62828, "session": 62828, "ts": 62828, "VAL": 62828, "symbol": 62828, "POC": 62828, "vwap": 62828}

### chart_4_correlation_20250912.jsonl (chart 4)
- lines_total: 531 | valid_json: 531 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 530
- missing_keys (top): {"VAH": 531, "session": 531, "ts": 531, "VAL": 531, "symbol": 531, "POC": 531, "vwap": 531}

### chart_4_cumulative_delta_20250911.jsonl (chart 4)
- lines_total: 91585 | valid_json: 91585 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91584
- missing_keys (top): {"VAH": 91585, "session": 91585, "ts": 91585, "VAL": 91585, "symbol": 91585, "POC": 91585, "vwap": 91585}

### chart_4_cumulative_delta_20250912.jsonl (chart 4)
- lines_total: 547 | valid_json: 547 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 546
- missing_keys (top): {"VAH": 547, "session": 547, "ts": 547, "VAL": 547, "symbol": 547, "POC": 547, "vwap": 547}

### chart_4_hvn_lvn_20250911.jsonl (chart 4)
- lines_total: 91606 | valid_json: 91606 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91605
- missing_keys (top): {"VAH": 91606, "session": 91606, "ts": 91606, "VAL": 91606, "symbol": 91606, "POC": 91606, "vwap": 91606}

### chart_4_nbcv_20250911.jsonl (chart 4)
- lines_total: 91602 | valid_json: 91602 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91601
- missing_keys (top): {"VAH": 91602, "session": 91602, "ts": 91602, "VAL": 91602, "symbol": 91602, "POC": 91602, "vwap": 91602}

### chart_4_nbcv_20250912.jsonl (chart 4)
- lines_total: 586 | valid_json: 586 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 585
- missing_keys (top): {"VAH": 586, "session": 586, "ts": 586, "VAL": 586, "symbol": 586, "POC": 586, "vwap": 586}

### chart_4_ohlc_20250911.jsonl (chart 4)
- lines_total: 91607 | valid_json: 91607 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91606
- missing_keys (top): {"VAH": 91607, "session": 91607, "ts": 91607, "VAL": 91607, "symbol": 91607, "POC": 91607, "vwap": 91607}

### chart_4_ohlc_20250912.jsonl (chart 4)
- lines_total: 1649 | valid_json: 1649 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 1648
- missing_keys (top): {"VAH": 1649, "session": 1649, "ts": 1649, "VAL": 1649, "symbol": 1649, "POC": 1649, "vwap": 1649}

### chart_4_previous_vp_20250912.jsonl (chart 4)
- lines_total: 607 | valid_json: 607 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 606
- missing_keys (top): {"VAH": 607, "session": 607, "ts": 607, "VAL": 607, "symbol": 607, "POC": 607, "vwap": 607}

### chart_4_previous_vwap_20250912.jsonl (chart 4)
- lines_total: 607 | valid_json: 607 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 606
- missing_keys (top): {"VAH": 607, "session": 607, "ts": 607, "VAL": 607, "symbol": 607, "POC": 607, "vwap": 607}

### chart_4_pvwap_20250911.jsonl (chart 4)
- lines_total: 91607 | valid_json: 91607 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91606
- missing_keys (top): {"VAH": 91607, "session": 91607, "ts": 91607, "VAL": 91607, "symbol": 91607, "POC": 91607, "vwap": 91607}

### chart_4_volume_profile_20250911.jsonl (chart 4)
- lines_total: 91342 | valid_json: 91342 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91341
- missing_keys (top): {"VAH": 91342, "session": 91342, "ts": 91342, "VAL": 91342, "symbol": 91342, "POC": 91342, "vwap": 91342}

### chart_4_volume_profile_20250912.jsonl (chart 4)
- lines_total: 1691 | valid_json: 1691 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 1690
- missing_keys (top): {"VAH": 1691, "session": 1691, "ts": 1691, "VAL": 1691, "symbol": 1691, "POC": 1691, "vwap": 1691}

### chart_4_vva_20250912.jsonl (chart 4)
- lines_total: 649 | valid_json: 649 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 648
- missing_keys (top): {"VAH": 649, "session": 649, "ts": 649, "VAL": 649, "symbol": 649, "POC": 649, "vwap": 649}

### chart_4_vva_previous_20250911.jsonl (chart 4)
- lines_total: 91607 | valid_json: 91607 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91606
- missing_keys (top): {"VAH": 91607, "session": 91607, "ts": 91607, "VAL": 91607, "symbol": 91607, "POC": 91607, "vwap": 91607}

### chart_4_vva_previous_20250912.jsonl (chart 4)
- lines_total: 666 | valid_json: 666 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 665
- missing_keys (top): {"VAH": 666, "session": 666, "ts": 666, "VAL": 666, "symbol": 666, "POC": 666, "vwap": 666}

### chart_4_vwap_20250911.jsonl (chart 4)
- lines_total: 91606 | valid_json: 91606 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91605
- missing_keys (top): {"VAH": 91606, "session": 91606, "ts": 91606, "VAL": 91606, "symbol": 91606, "POC": 91606}

### chart_4_vwap_20250912.jsonl (chart 4)
- lines_total: 688 | valid_json: 688 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 687
- missing_keys (top): {"VAH": 688, "session": 688, "ts": 688, "VAL": 688, "symbol": 688, "POC": 688}

### chart_8_vix_20250911.jsonl (chart 8)
- lines_total: 91754 | valid_json: 91754 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 91753
- missing_keys (top): {"ts": 91754, "vix": 91754}

### chart_8_vix_20250912.jsonl (chart 8)
- lines_total: 59 | valid_json: 59 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 58
- missing_keys (top): {"ts": 59, "vix": 59}

### chart_8_vix_close_20250911.jsonl (chart 8)
- lines_total: 87897 | valid_json: 87897 | invalid_json: 0
- with_ts: 0 | with_symbol: 0
- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): 87896
- missing_keys (top): {"ts": 87897}
