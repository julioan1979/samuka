# CashCheck – Agent Instructions (AGENT.md)

This document describes how a coding assistant or autonomous agent should work
with the CashCheck project.

---

## Project Purpose

CashCheck is a multi-tenant cash register reconciliation and audit system for
restaurants and small retail businesses. It automates daily cash closing
verification by comparing POS-reported totals with counted totals and surfacing
discrepancies.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Airtable as database | No-code database familiar to non-technical business owners |
| Multi-tenant via separate bases | Strong data isolation per company |
| Streamlit for UI | Rapid prototyping; deployable to Streamlit Cloud without DevOps overhead |
| pytesseract + OpenCV for OCR | Portable, open-source; handles printed receipts well |
| pandas for reconciliation | Flexible aggregation and pivot reporting |

---

## Source of Truth

- `docs/ARCHITECTURE.md` – overall architecture
- `docs/DATABASE_SCHEMA.md` – Airtable table definitions
- `docs/ROADMAP.md` – planned features

---

## How to Add a New Feature

1. **Model changes** → edit `src/models/`.
2. **Airtable table changes** → update `src/airtable_client.py` and `docs/DATABASE_SCHEMA.md`.
3. **Business logic** → add/modify a service in `src/services/`.
4. **UI page** → add/modify a file in `ui/`, then register it in `src/app.py`.
5. **OCR enhancements** → edit `src/ocr/ocr_reader.py`.

---

## Conventions

- All monetary amounts are stored as **positive floats** in Airtable.
- The sign of a movement is determined by `Movement.signed_amount()`.
- All dates are ISO 8601 (`YYYY-MM-DD`).
- Environment variables follow the pattern `AIRTABLE_BASE_<TENANT_SLUG>` where
  the slug is upper-cased with spaces/dashes replaced by underscores.

---

## Running Locally

```bash
cp .env.example .env
# Fill in your Airtable API key and base IDs

pip install -r requirements.txt
streamlit run src/app.py
```

## Testing

There is no automated test suite yet. To validate changes:

1. Start the app with `streamlit run src/app.py`.
2. Exercise each page manually.
3. Verify Airtable records are created/updated correctly.

---

## Common Pitfalls

- Always call `closing.evaluate_status()` (or `reconcile()`) after changing
  `expected_total` or `settled_total`.
- Never pass a negative `amount` to `MovementService.create_movement()`.
  Use the `movement_type` to encode direction.
- The OCR module expects the system package `tesseract-ocr` to be installed.
  On Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
