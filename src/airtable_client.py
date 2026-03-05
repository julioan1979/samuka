"""Airtable client helpers for CashCheck.

Provides thin wrappers around pyairtable to perform CRUD operations on the
Global Base (Tenants, Users, PaymentMethods, Suppliers) and on each
tenant's Operational Base (Closings, CashMovements, Evidence, Terminals).
"""

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Table name constants
# ---------------------------------------------------------------------------

# Global Base tables
TABLE_TENANTS = "Tenants"
TABLE_USERS = "Users"
TABLE_PAYMENT_METHODS = "PaymentMethods"
TABLE_SUPPLIERS = "Suppliers"

# Tenant Operational Base tables
TABLE_CLOSINGS = "Closings"
TABLE_CASH_MOVEMENTS = "CashMovements"
TABLE_EVIDENCE = "Evidence"
TABLE_TERMINALS = "Terminals"


class AirtableClient:
    """Generic Airtable client wrapping pyairtable.Api."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "Airtable API key not found. "
                "Set AIRTABLE_API_KEY in your .env file."
            )
        self._api = Api(self.api_key)
        logger.info("AirtableClient initialised.")

    def get_table(self, base_id: str, table_name: str):
        """Return a pyairtable Table object."""
        return self._api.table(base_id, table_name)

    # ------------------------------------------------------------------
    # Generic CRUD helpers
    # ------------------------------------------------------------------

    def list_records(
        self,
        base_id: str,
        table_name: str,
        formula: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return all records from a table, optionally filtered by formula."""
        table = self.get_table(base_id, table_name)
        kwargs: Dict[str, Any] = {}
        if formula:
            kwargs["formula"] = formula
        records = table.all(**kwargs)
        logger.debug("Fetched %d records from %s/%s", len(records), base_id, table_name)
        return records

    def get_record(self, base_id: str, table_name: str, record_id: str) -> Dict[str, Any]:
        """Fetch a single record by its Airtable record ID."""
        table = self.get_table(base_id, table_name)
        record = table.get(record_id)
        return record

    def create_record(
        self, base_id: str, table_name: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record and return the created record dict."""
        table = self.get_table(base_id, table_name)
        record = table.create(fields)
        logger.info("Created record %s in %s/%s", record.get("id"), base_id, table_name)
        return record

    def update_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing record and return the updated record dict."""
        table = self.get_table(base_id, table_name)
        record = table.update(record_id, fields)
        logger.info("Updated record %s in %s/%s", record_id, base_id, table_name)
        return record

    def delete_record(self, base_id: str, table_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record by ID."""
        table = self.get_table(base_id, table_name)
        result = table.delete(record_id)
        logger.info("Deleted record %s from %s/%s", record_id, base_id, table_name)
        return result


class GlobalBaseClient(AirtableClient):
    """Client scoped to the Global Airtable Base."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        super().__init__(api_key)
        self.base_id = os.getenv("AIRTABLE_GLOBAL_BASE_ID", "")
        if not self.base_id:
            raise ValueError(
                "Global base ID not found. "
                "Set AIRTABLE_GLOBAL_BASE_ID in your .env file."
            )

    # Tenants
    def list_tenants(self) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_TENANTS)

    def get_tenant(self, record_id: str) -> Dict[str, Any]:
        return self.get_record(self.base_id, TABLE_TENANTS, record_id)

    def create_tenant(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.create_record(self.base_id, TABLE_TENANTS, fields)

    def update_tenant(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.update_record(self.base_id, TABLE_TENANTS, record_id, fields)

    # PaymentMethods
    def list_payment_methods(self) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_PAYMENT_METHODS)

    # Suppliers
    def list_suppliers(self) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_SUPPLIERS)

    def create_supplier(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.create_record(self.base_id, TABLE_SUPPLIERS, fields)


class TenantBaseClient(AirtableClient):
    """Client scoped to a single tenant's Operational Airtable Base."""

    def __init__(self, tenant_slug: str, api_key: Optional[str] = None) -> None:
        super().__init__(api_key)
        env_var = f"AIRTABLE_BASE_{tenant_slug.upper().replace(' ', '_').replace('-', '_')}"
        self.base_id = os.getenv(env_var, "")
        if not self.base_id:
            raise ValueError(
                f"Tenant base ID not found for slug '{tenant_slug}'. "
                f"Set {env_var} in your .env file."
            )
        self.tenant_slug = tenant_slug

    # Closings
    def list_closings(self, formula: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_CLOSINGS, formula)

    def get_closing(self, record_id: str) -> Dict[str, Any]:
        return self.get_record(self.base_id, TABLE_CLOSINGS, record_id)

    def create_closing(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.create_record(self.base_id, TABLE_CLOSINGS, fields)

    def update_closing(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.update_record(self.base_id, TABLE_CLOSINGS, record_id, fields)

    # CashMovements
    def list_movements(self, formula: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_CASH_MOVEMENTS, formula)

    def create_movement(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.create_record(self.base_id, TABLE_CASH_MOVEMENTS, fields)

    def update_movement(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.update_record(self.base_id, TABLE_CASH_MOVEMENTS, record_id, fields)

    # Evidence
    def list_evidence(self, formula: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_EVIDENCE, formula)

    def create_evidence(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        return self.create_record(self.base_id, TABLE_EVIDENCE, fields)

    # Terminals
    def list_terminals(self) -> List[Dict[str, Any]]:
        return self.list_records(self.base_id, TABLE_TERMINALS)
