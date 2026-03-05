"""Tests for the Closing model."""

import pytest
from datetime import date

from src.models.closing import Closing, SHIFTS


class TestClosingDefaults:
    def test_default_status_is_pending(self):
        c = Closing()
        assert c.status == "Pending"

    def test_default_totals_are_zero(self):
        c = Closing()
        assert c.pos_total == 0.0
        assert c.expected_total == 0.0
        assert c.settled_total == 0.0
        assert c.difference == 0.0

    def test_default_operator_and_shift_are_none(self):
        c = Closing()
        assert c.operator is None
        assert c.shift is None


class TestClosingCalculateDifference:
    def test_positive_difference(self):
        c = Closing(expected_total=1000.0, settled_total=950.0)
        diff = c.calculate_difference()
        assert diff == 50.0
        assert c.difference == 50.0

    def test_negative_difference(self):
        c = Closing(expected_total=900.0, settled_total=950.0)
        diff = c.calculate_difference()
        assert diff == -50.0

    def test_zero_difference(self):
        c = Closing(expected_total=500.0, settled_total=500.0)
        assert c.calculate_difference() == 0.0


class TestClosingEvaluateStatus:
    def test_ok_when_within_tolerance(self):
        c = Closing(expected_total=100.0, settled_total=100.0)
        assert c.evaluate_status() == "OK"

    def test_ok_when_difference_exactly_tolerance(self):
        c = Closing(expected_total=100.0, settled_total=99.99)
        assert c.evaluate_status() == "OK"

    def test_discrepancy_when_outside_tolerance(self):
        c = Closing(expected_total=100.0, settled_total=50.0)
        assert c.evaluate_status() == "Discrepancy"

    def test_custom_tolerance(self):
        c = Closing(expected_total=100.0, settled_total=95.0)
        assert c.evaluate_status(tolerance=10.0) == "OK"


class TestClosingFromAirtable:
    def test_basic_fields(self):
        record = {
            "id": "rec123",
            "fields": {
                "TenantId": "tenant_abc",
                "ClosingDate": "2024-01-15",
                "PosTotal": 2500.0,
                "ExpectedTotal": 2500.0,
                "SettledTotal": 2450.0,
                "Difference": 50.0,
                "Status": "Discrepancy",
                "Notes": "Missing cash",
                "Terminal": "POS1",
                "Operator": "João",
                "Shift": "Morning",
            },
        }
        c = Closing.from_airtable(record)
        assert c.id == "rec123"
        assert c.tenant_id == "tenant_abc"
        assert c.closing_date == date(2024, 1, 15)
        assert c.pos_total == 2500.0
        assert c.settled_total == 2450.0
        assert c.difference == 50.0
        assert c.status == "Discrepancy"
        assert c.notes == "Missing cash"
        assert c.terminal == "POS1"
        assert c.operator == "João"
        assert c.shift == "Morning"

    def test_missing_optional_fields_default_to_none(self):
        record = {"id": "rec456", "fields": {}}
        c = Closing.from_airtable(record)
        assert c.closing_date is None
        assert c.notes is None
        assert c.terminal is None
        assert c.operator is None
        assert c.shift is None


class TestClosingToAirtable:
    def test_serializes_operator_and_shift(self):
        c = Closing(
            tenant_id="t1",
            closing_date=date(2024, 6, 1),
            pos_total=1000.0,
            expected_total=1000.0,
            settled_total=980.0,
            difference=20.0,
            status="Discrepancy",
            operator="Maria",
            shift="Afternoon",
        )
        data = c.to_airtable()
        assert data["Operator"] == "Maria"
        assert data["Shift"] == "Afternoon"
        assert data["ClosingDate"] == "2024-06-01"

    def test_omits_none_optional_fields(self):
        c = Closing(tenant_id="t1", pos_total=500.0, expected_total=500.0)
        data = c.to_airtable()
        assert "Operator" not in data
        assert "Shift" not in data
        assert "Terminal" not in data
        assert "Notes" not in data
        assert "ClosingDate" not in data


class TestShiftsConstant:
    def test_shifts_not_empty(self):
        assert len(SHIFTS) > 0

    def test_shifts_are_strings(self):
        assert all(isinstance(s, str) for s in SHIFTS)
