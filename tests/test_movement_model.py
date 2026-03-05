"""Tests for the Movement model."""

import pytest

from src.models.movement import Movement, MOVEMENT_TYPES, PAYMENT_METHODS


class TestMovementDefaults:
    def test_default_type_is_sale(self):
        m = Movement()
        assert m.movement_type == "Sale"

    def test_default_payment_method_is_cash(self):
        m = Movement()
        assert m.payment_method == "Cash"

    def test_default_amount_is_zero(self):
        m = Movement()
        assert m.amount == 0.0


class TestMovementInflowOutflow:
    def test_sale_is_inflow(self):
        m = Movement(movement_type="Sale")
        assert m.is_inflow() is True
        assert m.is_outflow() is False

    def test_expense_is_outflow(self):
        m = Movement(movement_type="Expense")
        assert m.is_outflow() is True
        assert m.is_inflow() is False

    def test_sangria_is_outflow(self):
        m = Movement(movement_type="Sangria")
        assert m.is_outflow() is True

    def test_courier_payment_is_outflow(self):
        m = Movement(movement_type="Courier Payment")
        assert m.is_outflow() is True

    def test_adjustment_is_neither(self):
        m = Movement(movement_type="Adjustment")
        assert m.is_inflow() is False
        assert m.is_outflow() is False


class TestMovementSignedAmount:
    def test_sale_signed_amount_positive(self):
        m = Movement(movement_type="Sale", amount=500.0)
        assert m.signed_amount() == 500.0

    def test_expense_signed_amount_negative(self):
        m = Movement(movement_type="Expense", amount=100.0)
        assert m.signed_amount() == -100.0

    def test_sangria_signed_amount_negative(self):
        m = Movement(movement_type="Sangria", amount=200.0)
        assert m.signed_amount() == -200.0

    def test_adjustment_signed_amount_positive(self):
        m = Movement(movement_type="Adjustment", amount=50.0)
        assert m.signed_amount() == 50.0


class TestMovementFromAirtable:
    def test_basic_fields(self):
        record = {
            "id": "recABC",
            "fields": {
                "TenantId": "t1",
                "ClosingId": "recCLOSING",
                "MovementType": "Expense",
                "PaymentMethod": "Pix",
                "Amount": 75.50,
                "Terminal": "T2",
                "Description": "Water supply",
                "Supplier": "AguaLimpa",
            },
        }
        m = Movement.from_airtable(record)
        assert m.id == "recABC"
        assert m.tenant_id == "t1"
        assert m.closing_id == "recCLOSING"
        assert m.movement_type == "Expense"
        assert m.payment_method == "Pix"
        assert m.amount == 75.50
        assert m.terminal == "T2"
        assert m.description == "Water supply"
        assert m.supplier == "AguaLimpa"


class TestMovementToAirtable:
    def test_basic_serialization(self):
        m = Movement(
            tenant_id="t1",
            movement_type="Sale",
            payment_method="Credit Card",
            amount=300.0,
            closing_id="rec999",
            terminal="POS1",
            description="Lunch",
        )
        data = m.to_airtable()
        assert data["TenantId"] == "t1"
        assert data["MovementType"] == "Sale"
        assert data["PaymentMethod"] == "Credit Card"
        assert data["Amount"] == 300.0
        assert data["ClosingId"] == "rec999"
        assert data["Terminal"] == "POS1"
        assert data["Description"] == "Lunch"

    def test_omits_none_optional_fields(self):
        m = Movement(tenant_id="t1", movement_type="Sale", payment_method="Cash", amount=10.0)
        data = m.to_airtable()
        assert "ClosingId" not in data
        assert "Terminal" not in data
        assert "Description" not in data
        assert "Supplier" not in data


class TestMovementTypesAndMethods:
    def test_movement_types_contains_required(self):
        required = {"Sale", "Expense", "Sangria", "Courier Payment", "Adjustment"}
        assert required.issubset(set(MOVEMENT_TYPES))

    def test_payment_methods_contains_required(self):
        required = {"Cash", "Pix", "Credit Card", "Debit Card"}
        assert required.issubset(set(PAYMENT_METHODS))
