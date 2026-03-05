"""Add Cash Movements page."""

from typing import List, Optional

import streamlit as st

from src.airtable_client import GlobalBaseClient
from src.models.movement import MOVEMENT_TYPES, PAYMENT_METHODS
from src.models.tenant import Tenant
from src.services.movement_service import MovementService


def _load_tenants() -> List[Tenant]:
    try:
        client = GlobalBaseClient()
        records = client.list_tenants()
        return [Tenant.from_airtable(r) for r in records if r.get("fields", {}).get("Active", True)]
    except Exception as exc:
        st.warning(f"Could not load tenants: {exc}")
        return []


def show_movements_page() -> None:
    st.title("💵 Add Cash Movement")

    tenants = _load_tenants()

    if not tenants:
        st.warning("No tenants available. Check your Airtable configuration.")
        return

    tenant_names = [t.name for t in tenants]
    selected_name = st.selectbox("Select Tenant", tenant_names)
    selected_tenant: Optional[Tenant] = next(
        (t for t in tenants if t.name == selected_name), None
    )

    with st.form("movement_form"):
        col1, col2 = st.columns(2)
        with col1:
            movement_type = st.selectbox("Movement Type", MOVEMENT_TYPES)
            payment_method = st.selectbox("Payment Method", PAYMENT_METHODS)
        with col2:
            amount = st.number_input("Amount (R$)", min_value=0.01, step=0.01, format="%.2f")
            terminal = st.text_input("Terminal (optional)")

        closing_id = st.text_input("Closing Record ID (optional — link to a closing)")
        description = st.text_area("Description (optional)")
        supplier = st.text_input("Supplier (optional)")

        submitted = st.form_submit_button("Add Movement", type="primary")

    if submitted:
        if selected_tenant is None:
            st.error("Please select a tenant.")
            return
        try:
            svc = MovementService(selected_tenant.slug)
            movement = svc.create_movement(
                tenant_id=selected_tenant.id or "",
                movement_type=movement_type,
                payment_method=payment_method,
                amount=amount,
                closing_id=closing_id or None,
                terminal=terminal or None,
                description=description or None,
                supplier=supplier or None,
            )
            st.success(
                f"✅ Movement added: {movement_type} · {payment_method} · "
                f"R$ {amount:,.2f}"
            )
            st.json(movement.to_airtable())
        except Exception as exc:
            st.error(f"Failed to add movement: {exc}")

    # ------------------------------------------------------------------ List
    st.divider()
    st.subheader("Recent Movements")
    if selected_tenant and st.button("Load Movements"):
        try:
            svc = MovementService(selected_tenant.slug)
            movements = svc.list_all_movements()
            if movements:
                import pandas as pd

                rows = [
                    {
                        "ID": m.id,
                        "Type": m.movement_type,
                        "Method": m.payment_method,
                        "Amount (R$)": m.amount,
                        "Signed": m.signed_amount(),
                        "Terminal": m.terminal,
                        "Description": m.description,
                    }
                    for m in movements
                ]
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.info("No movements found.")
        except Exception as exc:
            st.error(f"Could not load movements: {exc}")
