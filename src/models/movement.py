"""Movement model representing a single cash movement entry."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


MOVEMENT_TYPES = ["Sale", "Expense", "Sangria", "Courier Payment", "Adjustment"]

PAYMENT_METHODS = ["Cash", "Pix", "Credit Card", "Debit Card", "Ticket", "Check"]


@dataclass
class Movement:
    """Represents a single cash movement (sale, expense, sangria, etc.)."""

    id: Optional[str] = None
    closing_id: Optional[str] = None
    tenant_id: str = ""
    movement_type: str = "Sale"
    payment_method: str = "Cash"
    terminal: Optional[str] = None
    amount: float = 0.0
    description: Optional[str] = None
    supplier: Optional[str] = None
    created_at: Optional[datetime] = None

    def is_inflow(self) -> bool:
        """Return True if this movement adds to the total (Sale)."""
        return self.movement_type == "Sale"

    def is_outflow(self) -> bool:
        """Return True if this movement reduces the total (Expense, Sangria, Courier Payment)."""
        return self.movement_type in ("Expense", "Sangria", "Courier Payment")

    def signed_amount(self) -> float:
        """Return the amount with sign: positive for inflows, negative for outflows."""
        if self.is_outflow():
            return -abs(self.amount)
        return abs(self.amount)

    @classmethod
    def from_airtable(cls, record: dict) -> "Movement":
        """Create a Movement instance from an Airtable record."""
        fields = record.get("fields", {})
        raw_ts = fields.get("CreatedAt")
        created_at = datetime.fromisoformat(raw_ts) if raw_ts else None
        return cls(
            id=record.get("id"),
            closing_id=fields.get("ClosingId"),
            tenant_id=fields.get("TenantId", ""),
            movement_type=fields.get("MovementType", "Sale"),
            payment_method=fields.get("PaymentMethod", "Cash"),
            terminal=fields.get("Terminal"),
            amount=float(fields.get("Amount", 0.0)),
            description=fields.get("Description"),
            supplier=fields.get("Supplier"),
            created_at=created_at,
        )

    def to_airtable(self) -> dict:
        """Serialize to Airtable fields dict."""
        data: dict = {
            "TenantId": self.tenant_id,
            "MovementType": self.movement_type,
            "PaymentMethod": self.payment_method,
            "Amount": self.amount,
        }
        if self.closing_id:
            data["ClosingId"] = self.closing_id
        if self.terminal:
            data["Terminal"] = self.terminal
        if self.description:
            data["Description"] = self.description
        if self.supplier:
            data["Supplier"] = self.supplier
        return data
