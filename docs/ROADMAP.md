# CashCheck – Roadmap

## v0.1.0 (Current) – Starter Project

- [x] Multi-tenant Airtable integration (Global Base + per-tenant Operational Bases)
- [x] Closing model with reconciliation logic
- [x] CashMovement model with signed amounts
- [x] OCR module (pytesseract + OpenCV)
- [x] Streamlit UI: Dashboard, New Closing, Cash Movements, Upload Evidence
- [x] Environment-based configuration
- [x] Basic logging

---

## v0.2.0 – Authentication & Security

- [ ] User authentication (Streamlit-Authenticator or Auth0)
- [ ] Role-based access control (Admin, Cashier, Auditor)
- [ ] Audit log table to track changes

---

## v0.3.0 – Enhanced Reporting

- [ ] Weekly and monthly reconciliation summaries
- [ ] Exportable PDF reports
- [ ] Email notifications for discrepancies
- [ ] Charts and trend analysis on the dashboard

---

## v0.4.0 – POS Integration

- [ ] Webhook endpoint to receive POS totals automatically
- [ ] Integration adapters for common POS systems (Stone, Cielo, Rede)
- [ ] Automated closing creation from POS webhooks

---

## v0.5.0 – Advanced OCR

- [ ] Support PDF extraction (pdfplumber / PyMuPDF)
- [ ] Batch image upload and processing
- [ ] Confidence score per OCR result
- [ ] Manual correction workflow for low-confidence extractions

---

## v1.0.0 – SaaS Release

- [ ] Self-service tenant onboarding
- [ ] Subscription management (Stripe)
- [ ] White-label branding per tenant
- [ ] API for third-party integrations
- [ ] Mobile-friendly responsive layout
