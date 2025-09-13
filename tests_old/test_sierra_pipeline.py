#!/usr/bin/env python3
"""
🧪 TESTS SIERRA PIPELINE - MIA_IA_SYSTEM
=========================================

Tests pour la pipeline Sierra-only : SierraTail + UnifiedWriter + MenthorQ
"""

import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

import pytest

from features.sierra_stream import SierraTail
from features.unifier import UnifiedWriter
from features.menthorq_processor import MenthorQProcessor
from config.sierra_paths import get_current_date_str

class TestSierraPipeline:
    """Tests pour la pipeline Sierra complète"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.date_str = get_current_date_str()
        
        # Créer des fichiers JSONL de test
        self.create_test_chart_files()
        
        # Initialiser les composants
        self.sierra_tail = SierraTail(
            charts=[3, 4, 8, 10],
            base_dir=self.temp_dir
        )
        self.unified_writer = UnifiedWriter(
            output_dir=self.temp_dir
        )
        self.menthorq_processor = MenthorQProcessor()
    
    def create_test_chart_files(self):
        """Crée des fichiers JSONL de test"""
        test_data = {
            3: [
                {"ts": "2025-01-07T10:30:00Z", "sym": "ESU25_FUT_CME", "chart": 3, "type": "basedata", "open": 5295.0, "high": 5297.0, "low": 5293.0, "close": 5295.5, "volume": 1000},
                {"ts": "2025-01-07T10:31:00Z", "sym": "ESU25_FUT_CME", "chart": 3, "type": "vwap", "value": 5295.2}
            ],
            4: [
                {"ts": "2025-01-07T10:30:00Z", "sym": "ESU25_FUT_CME", "chart": 4, "type": "basedata", "open": 5295.0, "high": 5297.0, "low": 5293.0, "close": 5295.5, "volume": 5000}
            ],
            8: [
                {"ts": "2025-01-07T10:30:00Z", "sym": "VIX", "chart": 8, "type": "vix", "last": 15.2, "policy": "normal"}
            ],
            10: [
                {"ts": "2025-01-07T10:30:00Z", "sym": "ESU25_FUT_CME", "chart": 10, "type": "menthorq_gamma_levels", "label": "Call Resistance", "price": 5300.0},
                {"ts": "2025-01-07T10:30:00Z", "sym": "ESU25_FUT_CME", "chart": 10, "type": "menthorq_blind_spots", "label": "BL 1", "price": 5295.0}
            ]
        }
        
        for chart_num, data in test_data.items():
            filename = f"chart_{chart_num}_{self.date_str}.jsonl"
            filepath = self.temp_dir / filename
            
            with open(filepath, 'w') as f:
                for line in data:
                    f.write(json.dumps(line) + '\n')
    
    def teardown_method(self):
        """Cleanup après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_sierra_tail_reading(self):
        """Test de lecture des fichiers Sierra"""
        events = []
        
        async for event in self.sierra_tail.events():
            events.append(event)
            if len(events) >= 5:  # Limiter pour le test
                break
        
        assert len(events) >= 5
        assert all('ts' in event for event in events)
        assert all('chart' in event for event in events)
    
    @pytest.mark.asyncio
    async def test_unified_writer(self):
        """Test du UnifiedWriter"""
        # Simuler des événements
        test_events = [
            {"ts": "2025-01-07T10:30:00Z", "chart": 3, "type": "basedata", "sym": "ESU25_FUT_CME"},
            {"ts": "2025-01-07T10:30:00Z", "chart": 8, "type": "vix", "sym": "VIX"},
            {"ts": "2025-01-07T10:30:00Z", "chart": 10, "type": "menthorq_gamma_levels", "sym": "ESU25_FUT_CME"}
        ]
        
        # Router les événements
        for event in test_events:
            self.unified_writer.route(event)
        
        # Vérifier le fichier unifié
        unified_file = self.temp_dir / f"mia_unified_{self.date_str}.jsonl"
        assert unified_file.exists()
        
        # Lire et vérifier le contenu
        with open(unified_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        for line in lines:
            event = json.loads(line.strip())
            assert 'ts' in event
            assert 'chart' in event
    
    @pytest.mark.asyncio
    async def test_menthorq_processor_integration(self):
        """Test de l'intégration MenthorQ"""
        # Simuler des données MenthorQ
        menthorq_events = [
            {"ts": "2025-01-07T10:30:00Z", "sym": "ESU25_FUT_CME", "chart": 10, "type": "menthorq_gamma_levels", "label": "Call Resistance", "price": 5300.0},
            {"ts": "2025-01-07T10:30:00Z", "sym": "ESU25_FUT_CME", "chart": 10, "type": "menthorq_blind_spots", "label": "BL 1", "price": 5295.0}
        ]
        
        # Traiter les événements
        for event in menthorq_events:
            self.menthorq_processor.process_menthorq_line(json.dumps(event))
        
        # Vérifier les niveaux
        levels = self.menthorq_processor.get_levels("ESU25_FUT_CME")
        
        assert "gamma" in levels
        assert "blind_spots" in levels
        assert "swing" in levels
        assert levels["last_update"] is not None
    
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self):
        """Test de la pipeline complète"""
        events_processed = 0
        vix_events = 0
        menthorq_events = 0
        
        async for event in self.sierra_tail.events():
            # Router vers UnifiedWriter
            self.unified_writer.route(event)
            
            # Traiter MenthorQ si applicable
            if event.get('chart') == 10 and event.get('type', '').startswith('menthorq_'):
                self.menthorq_processor.process_menthorq_line(json.dumps(event))
                menthorq_events += 1
            
            # Compter les événements VIX
            if event.get('chart') == 8 and event.get('type') == 'vix':
                vix_events += 1
            
            events_processed += 1
            if events_processed >= 10:  # Limiter pour le test
                break
        
        # Vérifications
        assert events_processed > 0
        assert vix_events > 0
        assert menthorq_events > 0
        
        # Vérifier le fichier unifié
        unified_file = self.temp_dir / f"mia_unified_{self.date_str}.jsonl"
        assert unified_file.exists()
        
        # Vérifier MenthorQ
        levels = self.menthorq_processor.get_levels("ESU25_FUT_CME")
        assert not levels.get("stale", True)

def test_sierra_paths():
    """Test des chemins Sierra"""
    from config.sierra_paths import (
        per_chart_daily_path,
        unified_daily_path,
        get_current_date_str
    )
    
    date_str = get_current_date_str()
    
    # Test chemins par chart
    chart3_path = per_chart_daily_path(3, date_str)
    assert chart3_path.name == f"chart_3_{date_str}.jsonl"
    
    # Test chemin unifié
    unified_path = unified_daily_path(date_str)
    assert unified_path.name == f"mia_unified_{date_str}.jsonl"

def test_menthorq_runtime_config():
    """Test de la configuration MenthorQ runtime"""
    from config.menthorq_runtime import get_menthorq_config, MenthorQRuntimeConfig
    
    # Test configuration normale
    config = get_menthorq_config(test_mode=False)
    assert isinstance(config, MenthorQRuntimeConfig)
    assert config.vix_normal_threshold == 20.0
    
    # Test configuration test
    test_config = get_menthorq_config(test_mode=True)
    assert test_config.graph10_update_interval_normal == 5
    
    # Test méthodes
    assert config.get_vix_policy(15.0) == "normal"
    assert config.get_vix_policy(25.0) == "elevated"
    assert config.get_vix_policy(35.0) == "extreme"
    
    # Test sizing factor
    sizing = config.get_sizing_factor(15.0, 0.3)
    assert 0.1 <= sizing <= 2.0

if __name__ == "__main__":
    # Tests manuels
    import asyncio
    
    async def run_manual_tests():
        test = TestSierraPipeline()
        test.setup_method()
        
        try:
            await test.test_sierra_tail_reading()
            print("✅ SierraTail reading test passed")
            
            await test.test_unified_writer()
            print("✅ UnifiedWriter test passed")
            
            await test.test_menthorq_processor_integration()
            print("✅ MenthorQ processor test passed")
            
            await test.test_full_pipeline_integration()
            print("✅ Full pipeline test passed")
            
        finally:
            test.teardown_method()
    
    # Tests synchrones
    test_sierra_paths()
    print("✅ Sierra paths test passed")
    
    test_menthorq_runtime_config()
    print("✅ MenthorQ runtime config test passed")
    
    # Tests asynchrones
    asyncio.run(run_manual_tests())
    
    print("\n🎉 Tous les tests Sierra pipeline sont passés !")
