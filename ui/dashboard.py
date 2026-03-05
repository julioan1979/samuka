"""Dashboard page: today's closings, discrepancies, and total cash movements."""

import os
from datetime import date
from typing import List

import pandas as pd
import streamlit as st

from src.airtable_client import GlobalBaseClient, TenantBaseClient
from src.models.closing import Closing
from src.models.tenant import Tenant


def _load_tenants() -> List[Tenant]:
    try:
        client = GlobalBaseClient()
        records = client.list_tenants()
        return [Tenant.from_airtable(r) for r in records if r.get("fields", {}).get("Active", True)]
    except Exception as exc:
        st.warning(f"Could not load tenants: {exc}")
        return []


def _load_todays_closings(tenants: List[Tenant]) -> List[dict]:
    today = date.today()
    rows = []
    for tenant in tenants:
        try:
            tc = TenantBaseClient(tenant.slug)
            closings = tc.list_closings(
                formula=f"IS_SAME({{ClosingDate}}, '{today.isoformat()}', 'day')"
            )
            for r in closings:
                c = Closing.from_airtable(r)
                rows.append(
                    {
                        "Tenant": tenant.name,
                        "Date": c.closing_date,
                        "POS Total": c.pos_total,
                        "Expected": c.expected_total,
                        "Settled": c.settled_total,
                        "Difference": c.difference,
                        "Status": c.status,
                    }
                )
        except Exception as exc:
            st.warning(f"Could not load closings for {tenant.name}: {exc}")
    return rows


def show_dashboard() -> None:
    st.title("📊 Dashboard")
    st.caption(f"Today: {date.today().strftime('%d/%m/%Y')}")

    tenants = _load_tenants()

    if not tenants:
        st.info(
            "No tenants found. Configure your Airtable credentials in the `.env` file "
            "and make sure the Tenants table has at least one active record."
        )
        _show_demo_metrics()
        return

    rows = _load_todays_closings(tenants)

    # ------------------------------------------------------------------ KPIs
    total_cash = sum(r["Settled"] for r in rows)
    discrepancies = [r for r in rows if r["Status"] == "Discrepancy"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Closings Today", len(rows))
    col2.metric("Total Cash Movements", f"R$ {total_cash:,.2f}")
    col3.metric("Discrepancies", len(discrepancies), delta_color="inverse")

    st.divider()

    # -------------------------------------------------------------- All closings
    st.subheader("Today's Closings")
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(
            df.style.map(
                lambda v: "background-color: #ffcccc" if v == "Discrepancy" else "",
                subset=["Status"],
            ),
            use_container_width=True,
        )
    else:
        st.info("No closings registered for today yet.")

    # --------------------------------------------------------- Discrepancy list
    if discrepancies:
        st.subheader("⚠️ Discrepancies")
        st.dataframe(pd.DataFrame(discrepancies), use_container_width=True)


def _show_demo_metrics() -> None:
    """Show placeholder metrics when no live data is available."""
    st.subheader("Demo Preview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Closings Today", "—")
    col2.metric("Total Cash Movements", "R$ —")
    col3.metric("Discrepancies", "—")
