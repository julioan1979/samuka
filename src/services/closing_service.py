"""Closing service: business logic for creating and managing cash closings."""

import logging
from datetime import date
from typing import List, Optional

from ..airtable_client import TenantBaseClient
from ..models.closing import Closing
from ..reconciliation import reconcile
from .movement_service import MovementService

logger = logging.getLogger(__name__)


class ClosingService:
    """Handles CRUD and reconciliation operations for Closing records."""

    def __init__(self, tenant_slug: str, api_key: Optional[str] = None) -> None:
        self.client = TenantBaseClient(tenant_slug, api_key)
        self.movement_service = MovementService(tenant_slug, api_key)

    def list_closings(self, closing_date: Optional[date] = None) -> List[Closing]:
        """
        Return all closings, optionally filtered by date.

        Args:
            closing_date: If provided, only return closings for that date.
        """
        formula: Optional[str] = None
        if closing_date:
            formula = f"IS_SAME({{ClosingDate}}, '{closing_date.isoformat()}', 'day')"
        records = self.client.list_closings(formula)
        return [Closing.from_airtable(r) for r in records]

    def get_closing(self, record_id: str) -> Closing:
        """Fetch a single closing by Airtable record ID."""
        record = self.client.get_closing(record_id)
        return Closing.from_airtable(record)

    def create_closing(
        self,
        tenant_id: str,
        closing_date: date,
        pos_total: float,
        terminal: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Closing:
        """
        Create a new closing record in Airtable.

        Args:
            tenant_id: Airtable record ID of the tenant.
            closing_date: The date of the closing.
            pos_total: The POS-reported total for the day.
            terminal: Optional terminal name/identifier.
            notes: Optional free-text notes.

        Returns:
            The newly created Closing instance.
        """
        closing = Closing(
            tenant_id=tenant_id,
            closing_date=closing_date,
            pos_total=pos_total,
            expected_total=pos_total,
            terminal=terminal,
            notes=notes,
        )
        record = self.client.create_closing(closing.to_airtable())
        return Closing.from_airtable(record)

    def reconcile_closing(self, record_id: str) -> Closing:
        """
        Fetch a closing and all its movements, perform reconciliation,
        then persist the updated totals and status back to Airtable.

        Returns:
            The reconciled Closing instance.
        """
        closing = self.get_closing(record_id)
        movements = self.movement_service.list_movements_for_closing(record_id)
        reconcile(closing, movements)

        updated_record = self.client.update_closing(
            record_id,
            {
                "SettledTotal": closing.settled_total,
                "ExpectedTotal": closing.expected_total,
                "Difference": closing.difference,
                "Status": closing.status,
            },
        )
        logger.info(
            "Reconciliation complete for closing %s: status=%s diff=%.2f",
            record_id,
            closing.status,
            closing.difference,
        )
        return Closing.from_airtable(updated_record)

    def update_closing_notes(self, record_id: str, notes: str) -> Closing:
        """Update the notes field of a closing."""
        record = self.client.update_closing(record_id, {"Notes": notes})
        return Closing.from_airtable(record)
