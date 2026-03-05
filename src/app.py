"""CashCheck – Cash Register Reconciliation & Audit System.

Entry point for the Streamlit application.
Run with:
    streamlit run src/app.py
"""

import logging
import os
import sys

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on sys.path when running from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=os.getenv("APP_TITLE", "CashCheck"),
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
PAGES = {
    "📊 Dashboard": "dashboard",
    "📋 New Closing": "closing",
    "💵 Cash Movements": "movements",
    "📎 Upload Evidence": "evidence",
    "🔄 Reconciliation": "reconciliation",
}

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/cash-register.png",
        width=72,
    )
    st.title("CashCheck")
    st.caption("Cash reconciliation & audit")
    st.divider()
    selected_page = st.radio("Navigation", list(PAGES.keys()))
    st.divider()
    st.caption("v0.1.0 · julioan1979/samuka")

# ---------------------------------------------------------------------------
# Render the selected page
# ---------------------------------------------------------------------------
page_key = PAGES[selected_page]

if page_key == "dashboard":
    from ui.dashboard import show_dashboard
    show_dashboard()

elif page_key == "closing":
    from ui.closing_page import show_closing_page
    show_closing_page()

elif page_key == "movements":
    from ui.movements_page import show_movements_page
    show_movements_page()

elif page_key == "evidence":
    from ui.evidence_page import show_evidence_page
    show_evidence_page()

elif page_key == "reconciliation":
    from ui.reconciliation_page import show_reconciliation_page
    show_reconciliation_page()
