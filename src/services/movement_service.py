"""Movement service: business logic for cash movement records."""

import logging
from typing import List, Optional

from ..airtable_client import TenantBaseClient
from ..models.movement import Movement, MOVEMENT_TYPES, PAYMENT_METHODS

logger = logging.getLogger(__name__)


class MovementService:
    """Handles CRUD operations for CashMovement records."""

    def __init__(self, tenant_slug: str, api_key: Optional[str] = None) -> None:
        self.client = TenantBaseClient(tenant_slug, api_key)

    def list_movements_for_closing(self, closing_id: str) -> List[Movement]:
        """Return all movements linked to a specific closing record."""
        formula = f"{{ClosingId}} = '{closing_id}'"
        records = self.client.list_movements(formula)
        return [Movement.from_airtable(r) for r in records]

    def list_all_movements(self) -> List[Movement]:
        """Return all movements for the tenant."""
        records = self.client.list_movements()
        return [Movement.from_airtable(r) for r in records]

    def create_movement(
        self,
        tenant_id: str,
        movement_type: str,
        payment_method: str,
        amount: float,
        closing_id: Optional[str] = None,
        terminal: Optional[str] = None,
        description: Optional[str] = None,
        supplier: Optional[str] = None,
    ) -> Movement:
        """
        Create a new cash movement record.

        Args:
            tenant_id: Airtable record ID of the tenant.
            movement_type: One of MOVEMENT_TYPES.
            payment_method: One of PAYMENT_METHODS.
            amount: Absolute monetary amount (always positive).
            closing_id: Optional link to a closing record.
            terminal: Optional terminal identifier.
            description: Optional free-text description.
            supplier: Optional supplier name.

        Returns:
            The created Movement instance.
        """
        if movement_type not in MOVEMENT_TYPES:
            raise ValueError(f"Invalid movement_type '{movement_type}'. Choose from {MOVEMENT_TYPES}")
        if payment_method not in PAYMENT_METHODS:
            raise ValueError(f"Invalid payment_method '{payment_method}'. Choose from {PAYMENT_METHODS}")
        if amount < 0:
            raise ValueError("amount must be a non-negative value.")

        movement = Movement(
            tenant_id=tenant_id,
            closing_id=closing_id,
            movement_type=movement_type,
            payment_method=payment_method,
            terminal=terminal,
            amount=amount,
            description=description,
            supplier=supplier,
        )
        record = self.client.create_movement(movement.to_airtable())
        return Movement.from_airtable(record)

    def update_movement(self, record_id: str, fields: dict) -> Movement:
        """Update a movement record with the given fields dict."""
        record = self.client.update_movement(record_id, fields)
        return Movement.from_airtable(record)
