"""
Tests de validation des schémas Pydantic
========================================

Tests unitaires pour la validation des événements unifiés.
"""

import pytest
import json
from datetime import datetime, timezone
from pydantic import ValidationError

from schema.unified_event import (
    validate_unified_event,
    validate_jsonl_line,
    BaseDataEvent,
    VWAPEvent,
    VIXEvent,
    MenthorQEvent,
    UnifiedEvent,
)


class TestSchemaValidation:
    """Tests de validation des schémas"""
    
    def test_validate_basedata_event(self, sample_basedata_event):
        """Test validation événement basedata"""
        event = validate_unified_event(sample_basedata_event)
        assert isinstance(event, BaseDataEvent)
        assert event.sym == "ESU25_FUT_CME"
        assert event.chart == "3"
        assert event.type == "basedata"
        assert event.open == 5295.0
        assert event.high == 5297.0
        assert event.low == 5293.0
        assert event.close == 5295.5
        assert event.volume == 1000
    
    def test_validate_vwap_event(self, sample_vwap_event):
        """Test validation événement VWAP"""
        event = validate_unified_event(sample_vwap_event)
        assert isinstance(event, VWAPEvent)
        assert event.type == "vwap"
        assert event.vwap == 5294.5
        assert event.sd1_up == 5296.0
        assert event.sd1_dn == 5293.0
    
    def test_validate_vix_event(self, sample_vix_event):
        """Test validation événement VIX"""
        event = validate_unified_event(sample_vix_event)
        assert isinstance(event, VIXEvent)
        assert event.sym == "VIX"
        assert event.chart == "8"
        assert event.type == "vix"
        assert event.last == 15.2
        assert event.policy == "normal"
    
    def test_validate_menthorq_event(self, sample_menthorq_event):
        """Test validation événement MenthorQ"""
        event = validate_unified_event(sample_menthorq_event)
        assert isinstance(event, MenthorQEvent)
        assert event.type == "menthorq_gamma_levels"
        assert len(event.levels) == 2
        assert event.levels[0].label == "SG1"
        assert event.levels[0].price == 5300.0
        assert event.levels[0].type == "CALL"
    
    def test_validate_jsonl_line(self, sample_basedata_event):
        """Test validation ligne JSONL"""
        json_line = json.dumps(sample_basedata_event)
        event = validate_jsonl_line(json_line)
        assert isinstance(event, BaseDataEvent)
        assert event.sym == "ESU25_FUT_CME"
    
    def test_invalid_event_type(self):
        """Test événement avec type invalide"""
        invalid_event = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "ESU25_FUT_CME",
            "chart": "3",
            "type": "invalid_type",
            "data": "some_data"
        }
        
        with pytest.raises(ValueError, match="Type d'événement non reconnu"):
            validate_unified_event(invalid_event)
    
    def test_invalid_jsonl_line(self):
        """Test ligne JSONL invalide"""
        invalid_json = '{"invalid": json}'
        
        with pytest.raises(ValueError, match="Ligne JSON invalide"):
            validate_jsonl_line(invalid_json)
    
    def test_basedata_validation_errors(self):
        """Test erreurs de validation basedata"""
        # High < Low
        invalid_event = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "ESU25_FUT_CME",
            "chart": "3",
            "type": "basedata",
            "open": 5295.0,
            "high": 5290.0,  # Plus bas que low
            "low": 5293.0,
            "close": 5295.5,
            "volume": 1000
        }
        
        with pytest.raises(ValidationError):
            validate_unified_event(invalid_event)
    
    def test_vix_negative_value(self):
        """Test VIX avec valeur négative"""
        invalid_vix = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "VIX",
            "chart": "8",
            "type": "vix",
            "last": -5.0,  # Valeur négative
            "policy": "normal"
        }
        
        with pytest.raises(ValidationError):
            validate_unified_event(invalid_vix)
    
    def test_quote_ask_bid_validation(self):
        """Test validation ask > bid pour les quotes"""
        invalid_quote = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "ESU25_FUT_CME",
            "chart": "3",
            "type": "quote",
            "bid": 4500.0,
            "ask": 4495.0,  # Ask < Bid
            "bid_size": 100,
            "ask_size": 100
        }
        
        with pytest.raises(ValidationError):
            validate_unified_event(invalid_quote)
    
    def test_menthorq_levels_validation(self):
        """Test validation des niveaux MenthorQ"""
        # Niveau sans label
        invalid_menthorq = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "ESU25_FUT_CME",
            "chart": "10",
            "type": "menthorq_gamma_levels",
            "levels": [
                {
                    "price": 5300.0,
                    "type": "CALL"
                    # Manque le label
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            validate_unified_event(invalid_menthorq)
    
    def test_timestamp_parsing(self):
        """Test parsing des timestamps"""
        event_data = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "ESU25_FUT_CME",
            "chart": "3",
            "type": "basedata",
            "open": 5295.0,
            "high": 5297.0,
            "low": 5293.0,
            "close": 5295.5,
            "volume": 1000
        }
        
        event = validate_unified_event(event_data)
        assert isinstance(event.ts, datetime)
        assert event.ts.tzinfo is not None
    
    def test_enum_validation(self):
        """Test validation des énumérations"""
        # Symbole invalide
        invalid_event = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "INVALID_SYMBOL",
            "chart": "3",
            "type": "basedata",
            "open": 5295.0,
            "high": 5297.0,
            "low": 5293.0,
            "close": 5295.5,
            "volume": 1000
        }
        
        with pytest.raises(ValidationError):
            validate_unified_event(invalid_event)
    
    def test_optional_fields(self):
        """Test champs optionnels"""
        minimal_event = {
            "ts": "2025-01-07T10:30:00Z",
            "sym": "ESU25_FUT_CME",
            "chart": "3",
            "type": "basedata",
            "open": 5295.0,
            "high": 5297.0,
            "low": 5293.0,
            "close": 5295.5,
            "volume": 1000
        }
        
        event = validate_unified_event(minimal_event)
        assert event is not None
        # Les champs optionnels devraient avoir des valeurs par défaut ou None

