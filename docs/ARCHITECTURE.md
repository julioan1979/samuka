# CashCheck – Architecture

## Overview

CashCheck is a multi-tenant cash register reconciliation and audit system designed
for restaurants and small retail businesses. It automates daily cash closing
verification by comparing expected totals from POS systems with the actual counted
totals.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend language | Python 3.11+ |
| Web UI | Streamlit |
| Database | Airtable (via pyairtable) |
| Data processing | pandas |
| OCR | pytesseract + OpenCV + Pillow |
| Configuration | python-dotenv |

---

## Project Structure

```
cashcheck/
├── src/
│   ├── app.py                  # Streamlit entry point
│   ├── airtable_client.py      # Airtable API wrappers
│   ├── reconciliation.py       # Reconciliation logic (pandas)
│   ├── ocr/
│   │   ├── __init__.py
│   │   └── ocr_reader.py       # OCR extraction (pytesseract + OpenCV)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── closing_service.py  # Business logic for closings
│   │   └── movement_service.py # Business logic for movements
│   └── models/
│       ├── __init__.py
│       ├── closing.py          # Closing dataclass
│       ├── movement.py         # Movement dataclass
│       └── tenant.py           # Tenant dataclass
│
├── ui/
│   ├── __init__.py
│   ├── dashboard.py            # Dashboard page
│   ├── closing_page.py         # New closing + review page
│   ├── movements_page.py       # Add cash movement page
│   └── evidence_page.py        # Upload evidence + OCR page
│
├── docs/
│   ├── ARCHITECTURE.md         # This file
│   ├── DATABASE_SCHEMA.md      # Airtable schema
│   ├── AGENT.md                # AI agent instructions
│   └── ROADMAP.md              # Future roadmap
│
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Data Flow

```
[Streamlit UI]
     │
     ▼
[Service Layer]          ← Business logic + validation
  closing_service.py
  movement_service.py
     │
     ▼
[Airtable Client]        ← CRUD helpers (pyairtable)
  airtable_client.py
     │
     ▼
[Airtable REST API]      ← Cloud database (multi-tenant bases)
```

### OCR Flow

```
[User uploads image]
     │
     ▼
[evidence_page.py]
     │
     ▼
[ocr_reader.py]          ← OpenCV pre-processing
     │                   ← pytesseract extraction
     │                   ← regex currency parsing
     ▼
[Structured result]      ← {raw_text, values, suggested_total}
     │
     ▼
[Airtable Evidence table]
```

---

## Multi-Tenancy

Each tenant (e.g., Casa da Pizza, Julipan) has:
- A record in the **Global Base** `Tenants` table.
- A dedicated Airtable **Operational Base** with their own Closings,
  CashMovements, Evidence, and Terminals tables.

The `TenantBaseClient` resolves the correct base ID from an environment
variable using the pattern `AIRTABLE_BASE_<TENANT_SLUG>`.

---

## Reconciliation Logic

```
settled_total  = Σ signed_amount(movement)
               = +Sales − Expenses − Sangria − Courier Payments ± Adjustments

difference     = expected_total − settled_total

status         = "OK"           if |difference| ≤ 0.01
               = "Discrepancy"  otherwise
```

---

## Deployment

### Streamlit Cloud

1. Push to GitHub.
2. Connect the repo on [share.streamlit.io](https://share.streamlit.io).
3. Set the main file to `src/app.py`.
4. Add all environment variables in the Secrets panel.

### VPS (e.g., Ubuntu + systemd)

```bash
pip install -r requirements.txt
streamlit run src/app.py --server.port 8501 --server.headless true
```

Create a systemd service to keep the process running.
