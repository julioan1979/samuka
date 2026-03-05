"""Tenant model representing a company (multi-tenant support)."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Tenant:
    """Represents a business tenant (e.g., Casa da Pizza, Julipan)."""

    id: Optional[str] = None
    name: str = ""
    slug: str = ""
    airtable_base_id: str = ""
    active: bool = True
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    @classmethod
    def from_airtable(cls, record: dict) -> "Tenant":
        """Create a Tenant instance from an Airtable record."""
        fields = record.get("fields", {})
        return cls(
            id=record.get("id"),
            name=fields.get("Name", ""),
            slug=fields.get("Slug", ""),
            airtable_base_id=fields.get("AirtableBaseId", ""),
            active=fields.get("Active", True),
            contact_email=fields.get("ContactEmail"),
            contact_phone=fields.get("ContactPhone"),
        )

    def to_airtable(self) -> dict:
        """Serialize to Airtable fields dict."""
        data: dict = {
            "Name": self.name,
            "Slug": self.slug,
            "AirtableBaseId": self.airtable_base_id,
            "Active": self.active,
        }
        if self.contact_email:
            data["ContactEmail"] = self.contact_email
        if self.contact_phone:
            data["ContactPhone"] = self.contact_phone
        return data
