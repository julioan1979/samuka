"""New Closing page: select tenant, enter date and POS total."""

from datetime import date
from typing import List, Optional

import streamlit as st

from src.airtable_client import GlobalBaseClient
from src.models.tenant import Tenant
from src.services.closing_service import ClosingService


def _load_tenants() -> List[Tenant]:
    try:
        client = GlobalBaseClient()
        records = client.list_tenants()
        return [Tenant.from_airtable(r) for r in records if r.get("fields", {}).get("Active", True)]
    except Exception as exc:
        st.warning(f"Could not load tenants: {exc}")
        return []


def show_closing_page() -> None:
    st.title("📋 New Closing")

    tenants = _load_tenants()

    if not tenants:
        st.warning(
            "No tenants available. Please configure your Airtable credentials "
            "and create at least one active Tenant record."
        )
        return

    tenant_names = [t.name for t in tenants]
    selected_name = st.selectbox("Select Tenant", tenant_names)
    selected_tenant: Optional[Tenant] = next(
        (t for t in tenants if t.name == selected_name), None
    )

    closing_date = st.date_input("Closing Date", value=date.today())
    pos_total = st.number_input("POS Total (R$)", min_value=0.0, step=0.01, format="%.2f")
    terminal = st.text_input("Terminal (optional)")
    notes = st.text_area("Notes (optional)")

    if st.button("Create Closing", type="primary"):
        if selected_tenant is None:
            st.error("Please select a tenant.")
            return
        if pos_total <= 0:
            st.error("POS Total must be greater than zero.")
            return

        try:
            svc = ClosingService(selected_tenant.slug)
            closing = svc.create_closing(
                tenant_id=selected_tenant.id or "",
                closing_date=closing_date,
                pos_total=pos_total,
                terminal=terminal or None,
                notes=notes or None,
            )
            st.success(
                f"✅ Closing created for **{selected_tenant.name}** on "
                f"{closing_date.strftime('%d/%m/%Y')} "
                f"(POS Total: R$ {pos_total:,.2f})."
            )
            st.json(closing.to_airtable())
        except Exception as exc:
            st.error(f"Failed to create closing: {exc}")

    # ----------------------------------------------------------------- Review
    st.divider()
    st.subheader("🔍 Review & Reconcile Existing Closing")

    record_id = st.text_input("Closing Record ID (from Airtable)")

    if st.button("Reconcile") and record_id and selected_tenant:
        try:
            svc = ClosingService(selected_tenant.slug)
            closing = svc.reconcile_closing(record_id)
            status_icon = "✅" if closing.status == "OK" else "⚠️"
            st.info(
                f"{status_icon} Status: **{closing.status}** | "
                f"Expected: R$ {closing.expected_total:,.2f} | "
                f"Settled: R$ {closing.settled_total:,.2f} | "
                f"Difference: R$ {closing.difference:,.2f}"
            )
        except Exception as exc:
            st.error(f"Reconciliation failed: {exc}")
