"""Evidence upload page: upload images/PDFs, run OCR, store results."""

import os
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st

from src.airtable_client import GlobalBaseClient, TenantBaseClient
from src.models.tenant import Tenant
from src.ocr.ocr_reader import extract_total_from_image


def _load_tenants():
    try:
        client = GlobalBaseClient()
        records = client.list_tenants()
        return [Tenant.from_airtable(r) for r in records if r.get("fields", {}).get("Active", True)]
    except Exception as exc:
        st.warning(f"Could not load tenants: {exc}")
        return []


def show_evidence_page() -> None:
    st.title("📎 Upload Evidence")

    tenants = _load_tenants()
    tenant_names = [t.name for t in tenants] if tenants else ["(Demo Mode)"]
    selected_name = st.selectbox("Select Tenant", tenant_names)
    selected_tenant: Optional[Tenant] = next(
        (t for t in tenants if t.name == selected_name), None
    )

    closing_id = st.text_input("Closing Record ID (optional)")

    uploaded_file = st.file_uploader(
        "Upload receipt image or PDF",
        type=["png", "jpg", "jpeg", "tiff", "bmp", "webp"],
        help="Upload an image of a card machine report or POS receipt to extract totals automatically.",
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded file", use_container_width=True)

        if st.button("Run OCR", type="primary"):
            with st.spinner("Running OCR…"):
                # Write to a temp file so pytesseract can read it
                suffix = Path(uploaded_file.name).suffix
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                try:
                    result = extract_total_from_image(tmp_path)
                    st.success("OCR completed.")

                    st.subheader("Extracted Values")
                    if result["values"]:
                        st.write(f"All numeric values found: {result['values']}")
                        st.metric(
                            "Suggested Total",
                            f"R$ {result['suggested_total']:,.2f}" if result["suggested_total"] else "—",
                        )
                    else:
                        st.warning("No numeric values detected.")

                    with st.expander("Raw OCR Text"):
                        st.text(result["raw_text"])

                    # Optionally store in Airtable
                    if selected_tenant and st.button("Store OCR Result in Airtable"):
                        try:
                            tc = TenantBaseClient(selected_tenant.slug)
                            fields: dict = {
                                "TenantId": selected_tenant.id or "",
                                "FileName": uploaded_file.name,
                                "RawText": result["raw_text"][:5000],
                                "SuggestedTotal": result["suggested_total"] or 0.0,
                            }
                            if closing_id:
                                fields["ClosingId"] = closing_id
                            tc.create_evidence(fields)
                            st.success("Evidence stored in Airtable.")
                        except Exception as exc:
                            st.error(f"Could not store evidence: {exc}")

                except Exception as exc:
                    st.error(f"OCR failed: {exc}")
                finally:
                    os.unlink(tmp_path)
