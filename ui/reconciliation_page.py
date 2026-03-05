"""Reconciliation page: display totals, difference, and payment breakdown."""

from typing import List, Optional

import pandas as pd
import streamlit as st

from src.airtable_client import GlobalBaseClient
from src.models.tenant import Tenant
from src.reconciliation import summary_by_payment_method
from src.services.closing_service import ClosingService
from src.services.movement_service import MovementService


def _load_tenants() -> List[Tenant]:
    try:
        client = GlobalBaseClient()
        records = client.list_tenants()
        return [
            Tenant.from_airtable(r)
            for r in records
            if r.get("fields", {}).get("Active", True)
        ]
    except Exception as exc:
        st.warning(f"Could not load tenants: {exc}")
        return []


def show_reconciliation_page() -> None:
    st.title("🔄 Reconciliation")
    st.caption("Enter a closing record ID to view its full reconciliation summary.")

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

    record_id = st.text_input("Closing Record ID (from Airtable)")

    col_run, col_reconcile = st.columns([1, 1])
    run_clicked = col_run.button("Load Summary", type="primary")
    reconcile_clicked = col_reconcile.button("Run Reconciliation")

    if not record_id:
        st.info("Enter a Closing Record ID above to load its reconciliation summary.")
        return

    if not selected_tenant:
        st.error("Please select a tenant.")
        return

    if run_clicked or reconcile_clicked:
        try:
            closing_svc = ClosingService(selected_tenant.slug)
            movement_svc = MovementService(selected_tenant.slug)

            if reconcile_clicked:
                closing = closing_svc.reconcile_closing(record_id)
                st.success("Reconciliation updated in Airtable.")
            else:
                closing = closing_svc.get_closing(record_id)

            movements = movement_svc.list_movements_for_closing(record_id)

        except Exception as exc:
            st.error(f"Failed to load reconciliation data: {exc}")
            return

        # ----------------------------------------------------------------- KPIs
        status_color = "green" if closing.status == "OK" else "red"
        status_icon = "✅" if closing.status == "OK" else "⚠️"

        st.divider()
        st.subheader(f"{status_icon} Closing Status: **:{status_color}[{closing.status}]**")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Expected Total", f"R$ {closing.expected_total:,.2f}")
        col2.metric("Settled Total", f"R$ {closing.settled_total:,.2f}")
        col3.metric(
            "Difference",
            f"R$ {closing.difference:,.2f}",
            delta=f"{closing.difference:+.2f}",
            delta_color="inverse",
        )
        col4.metric("Movements", len(movements))

        # ---------------------------------------------------------------- Details
        st.divider()
        with st.expander("Closing Details", expanded=True):
            detail_cols = st.columns(3)
            detail_cols[0].write(f"**Date:** {closing.closing_date or '—'}")
            detail_cols[0].write(f"**Operator:** {closing.operator or '—'}")
            detail_cols[1].write(f"**Shift:** {closing.shift or '—'}")
            detail_cols[1].write(f"**Terminal:** {closing.terminal or '—'}")
            detail_cols[2].write(f"**POS Total:** R$ {closing.pos_total:,.2f}")
            if closing.notes:
                st.write(f"**Notes:** {closing.notes}")

        # ------------------------------------------------------------- Breakdown
        st.subheader("Payment Method Breakdown")
        if movements:
            pivot_df = summary_by_payment_method(movements)
            if not pivot_df.empty:
                st.dataframe(pivot_df, use_container_width=True)
            else:
                st.info("No movement data to display.")

            # Movement list
            st.subheader("All Movements")
            rows = [
                {
                    "Type": m.movement_type,
                    "Method": m.payment_method,
                    "Amount (R$)": m.amount,
                    "Signed (R$)": m.signed_amount(),
                    "Terminal": m.terminal or "—",
                    "Description": m.description or "—",
                    "Supplier": m.supplier or "—",
                }
                for m in movements
            ]
            df = pd.DataFrame(rows)
            st.dataframe(
                df.style.map(
                    lambda v: "color: green" if isinstance(v, float) and v > 0
                    else ("color: red" if isinstance(v, float) and v < 0 else ""),
                    subset=["Signed (R$)"],
                ),
                use_container_width=True,
            )
        else:
            st.info("No movements found for this closing.")
