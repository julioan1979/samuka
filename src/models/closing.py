"""Closing model representing a daily cash closing record."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Closing:
    """Represents a daily cash closing/reconciliation record."""

    id: Optional[str] = None
    tenant_id: str = ""
    closing_date: Optional[date] = None
    pos_total: float = 0.0
    expected_total: float = 0.0
    settled_total: float = 0.0
    difference: float = 0.0
    status: str = "Pending"  # Pending | OK | Discrepancy
    notes: Optional[str] = None
    terminal: Optional[str] = None

    def calculate_difference(self) -> float:
        """Calculate and store the difference between expected and settled totals."""
        self.difference = round(self.expected_total - self.settled_total, 2)
        return self.difference

    def evaluate_status(self, tolerance: float = 0.01) -> str:
        """
        Determine closing status based on the difference.

        Args:
            tolerance: Acceptable rounding difference (default 1 cent).

        Returns:
            'OK' if within tolerance, otherwise 'Discrepancy'.
        """
        self.calculate_difference()
        if abs(self.difference) <= tolerance:
            self.status = "OK"
        else:
            self.status = "Discrepancy"
        return self.status

    @classmethod
    def from_airtable(cls, record: dict) -> "Closing":
        """Create a Closing instance from an Airtable record."""
        fields = record.get("fields", {})
        raw_date = fields.get("ClosingDate")
        closing_date = date.fromisoformat(raw_date) if raw_date else None
        return cls(
            id=record.get("id"),
            tenant_id=fields.get("TenantId", ""),
            closing_date=closing_date,
            pos_total=float(fields.get("PosTotal", 0.0)),
            expected_total=float(fields.get("ExpectedTotal", 0.0)),
            settled_total=float(fields.get("SettledTotal", 0.0)),
            difference=float(fields.get("Difference", 0.0)),
            status=fields.get("Status", "Pending"),
            notes=fields.get("Notes"),
            terminal=fields.get("Terminal"),
        )

    def to_airtable(self) -> dict:
        """Serialize to Airtable fields dict."""
        data: dict = {
            "TenantId": self.tenant_id,
            "PosTotal": self.pos_total,
            "ExpectedTotal": self.expected_total,
            "SettledTotal": self.settled_total,
            "Difference": self.difference,
            "Status": self.status,
        }
        if self.closing_date:
            data["ClosingDate"] = self.closing_date.isoformat()
        if self.notes:
            data["Notes"] = self.notes
        if self.terminal:
            data["Terminal"] = self.terminal
        return data
