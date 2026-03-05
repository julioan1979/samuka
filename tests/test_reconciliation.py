"""Tests for reconciliation logic."""

import pytest

from src.models.closing import Closing
from src.models.movement import Movement
from src.reconciliation import (
    aggregate_movements,
    calculate_settled_total,
    reconcile,
    summary_by_payment_method,
)


def _make_movement(movement_type: str, payment_method: str, amount: float) -> Movement:
    return Movement(movement_type=movement_type, payment_method=payment_method, amount=amount)


class TestAggregateMovements:
    def test_empty_movements_returns_empty_df(self):
        df = aggregate_movements([])
        assert df.empty
        assert list(df.columns) == ["movement_type", "payment_method", "amount", "signed_amount"]

    def test_single_movement(self):
        m = _make_movement("Sale", "Cash", 100.0)
        df = aggregate_movements([m])
        assert len(df) == 1
        assert df.iloc[0]["signed_amount"] == 100.0

    def test_outflow_has_negative_signed_amount(self):
        m = _make_movement("Expense", "Pix", 50.0)
        df = aggregate_movements([m])
        assert df.iloc[0]["signed_amount"] == -50.0


class TestCalculateSettledTotal:
    def test_single_sale(self):
        movements = [_make_movement("Sale", "Cash", 500.0)]
        assert calculate_settled_total(movements) == 500.0

    def test_sale_minus_expense(self):
        movements = [
            _make_movement("Sale", "Cash", 1000.0),
            _make_movement("Expense", "Cash", 100.0),
        ]
        assert calculate_settled_total(movements) == 900.0

    def test_multiple_payment_methods(self):
        movements = [
            _make_movement("Sale", "Cash", 400.0),
            _make_movement("Sale", "Pix", 300.0),
            _make_movement("Sale", "Credit Card", 1700.0),
            _make_movement("Expense", "Cash", 50.0),
        ]
        # 400 + 300 + 1700 - 50 = 2350
        assert calculate_settled_total(movements) == 2350.0

    def test_sangria_reduces_total(self):
        movements = [
            _make_movement("Sale", "Cash", 500.0),
            _make_movement("Sangria", "Cash", 200.0),
        ]
        assert calculate_settled_total(movements) == 300.0

    def test_empty_movements_returns_zero(self):
        assert calculate_settled_total([]) == 0.0


class TestReconcile:
    def test_ok_status_when_balanced(self):
        closing = Closing(expected_total=1000.0)
        movements = [_make_movement("Sale", "Cash", 1000.0)]
        result = reconcile(closing, movements)
        assert result.status == "OK"
        assert result.settled_total == 1000.0
        assert result.difference == 0.0

    def test_discrepancy_when_unbalanced(self):
        closing = Closing(expected_total=3250.0)
        movements = [
            _make_movement("Sale", "Cash", 500.0),
            _make_movement("Sale", "Credit Card", 2500.0),
            _make_movement("Sale", "Pix", 200.0),
        ]
        result = reconcile(closing, movements)
        # Settled = 3200, Expected = 3250 → diff = 50
        assert result.status == "Discrepancy"
        assert result.difference == 50.0

    def test_pos_total_used_as_expected_when_expected_is_zero(self):
        closing = Closing(pos_total=500.0, expected_total=0.0)
        movements = [_make_movement("Sale", "Cash", 500.0)]
        result = reconcile(closing, movements)
        assert result.expected_total == 500.0
        assert result.status == "OK"

    def test_explicit_expected_total_not_overridden_by_pos(self):
        # expected_total explicitly set to non-zero should not be replaced
        closing = Closing(pos_total=1000.0, expected_total=800.0)
        movements = [_make_movement("Sale", "Cash", 800.0)]
        result = reconcile(closing, movements)
        assert result.expected_total == 800.0
        assert result.status == "OK"


class TestSummaryByPaymentMethod:
    def test_empty_movements_returns_empty_df(self):
        df = summary_by_payment_method([])
        assert df.empty

    def test_pivot_totals_by_payment_method(self):
        movements = [
            _make_movement("Sale", "Cash", 400.0),
            _make_movement("Sale", "Pix", 300.0),
            _make_movement("Expense", "Cash", 50.0),
        ]
        pivot = summary_by_payment_method(movements)
        assert not pivot.empty
        assert "Total" in pivot.columns
        # Cash row: Sale=400, Expense=-50 → Total=350
        cash_row = pivot[pivot["payment_method"] == "Cash"].iloc[0]
        assert cash_row["Total"] == 350.0
        # Pix row: Sale=300 → Total=300
        pix_row = pivot[pivot["payment_method"] == "Pix"].iloc[0]
        assert pix_row["Total"] == 300.0
