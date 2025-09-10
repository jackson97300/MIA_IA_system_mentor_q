#!/usr/bin/env python3
"""
Script pour générer des données MenthorQ de test dans le fichier unifié
"""

import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from features.unifier import create_unified_writer, create_unify_config
from features.sierra_stream import SierraEvent

async def generate_menthorq_test_data():
    """Génère des données MenthorQ de test"""
    print("🚀 GÉNÉRATION DE DONNÉES MENTHORQ DE TEST")
    print("=" * 50)
    
    # Configuration pour désactiver le filtrage MenthorQ
    config = create_unify_config(
        enable_filtering=False,
        filter_menthorq=False,  # Désactiver le filtrage pour écrire les données
        filter_trades=False,
        filter_quotes=False,
        filter_basedata=False
    )
    
    # Créer le writer
    writer = await create_unified_writer(config=config, date_str="20250907")
    
    try:
        # Données MenthorQ de test
        menthorq_events = [
            # Gamma Levels
            SierraEvent(
                raw_data={
                    "type": "menthorq_gamma_levels",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5300.0,
                    "level_type": "Call Resistance",
                    "strength": 0.8,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            ),
            SierraEvent(
                raw_data={
                    "type": "menthorq_gamma_levels",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5290.0,
                    "level_type": "Put Support",
                    "strength": 0.7,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            ),
            SierraEvent(
                raw_data={
                    "type": "menthorq_gamma_levels",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5295.0,
                    "level_type": "HVL",
                    "strength": 0.9,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            ),
            # Blind Spots
            SierraEvent(
                raw_data={
                    "type": "menthorq_blind_spots",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5302.0,
                    "level_type": "BL 1",
                    "strength": 0.6,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            ),
            SierraEvent(
                raw_data={
                    "type": "menthorq_blind_spots",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5298.0,
                    "level_type": "BL 2",
                    "strength": 0.5,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            ),
            # Swing Levels
            SierraEvent(
                raw_data={
                    "type": "menthorq_swing_levels",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5305.0,
                    "level_type": "1D Max",
                    "strength": 0.8,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            ),
            SierraEvent(
                raw_data={
                    "type": "menthorq_swing_levels",
                    "graph": 10,
                    "sym": "ESU25_FUT_CME",
                    "price": 5285.0,
                    "level_type": "1D Min",
                    "strength": 0.8,
                    "t": datetime.now(timezone.utc).isoformat()
                },
                graph=10,
                ingest_ts=datetime.now(timezone.utc),
                file_path=Path("test_menthorq.jsonl")
            )
        ]
        
        # Écrire les événements
        for i, event in enumerate(menthorq_events):
            success, reason = await writer.write_event(event)
            if success:
                print(f"✅ Événement {i+1} écrit: {event.event_type} @ {event.raw_data.get('price', 'N/A')}")
            else:
                print(f"❌ Événement {i+1} échoué: {reason}")
        
        print(f"\n🎉 {len(menthorq_events)} événements MenthorQ générés !")
        
    finally:
        await writer.close()

if __name__ == "__main__":
    asyncio.run(generate_menthorq_test_data())
