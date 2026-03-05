# CashCheck 💰

**Cash register reconciliation and audit system for restaurants and small retail businesses.**

CashCheck automates daily cash closing verification by comparing expected totals from POS systems with the actual counted totals. It supports multiple companies (multi-tenant) and uses Airtable as its backend database.

---

## Features

- 📊 **Dashboard** – today's closings, discrepancies, and total cash movements
- 📋 **New Closing** – create a closing record, enter POS total, reconcile
- 💵 **Cash Movements** – log sales, expenses, sangrias, courier payments, and adjustments
- 📎 **Upload Evidence** – upload receipt images, run OCR to extract totals automatically
- 🏢 **Multi-tenant** – each business has its own isolated Airtable base

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/julioan1979/samuka.git
cd samuka

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Airtable API key and base IDs

# 4. Run the app
streamlit run src/app.py
```

> **Note:** OCR requires the system package `tesseract-ocr`.
> On Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-por`

---

## Project Structure

```
src/
    app.py               # Streamlit entry point
    airtable_client.py   # Airtable API wrappers
    reconciliation.py    # Reconciliation calculations (pandas)
    ocr/
        ocr_reader.py    # OCR extraction (pytesseract + OpenCV)
    services/
        closing_service.py
        movement_service.py
    models/
        closing.py
        movement.py
        tenant.py

ui/
    dashboard.py
    closing_page.py
    movements_page.py
    evidence_page.py

docs/
    ARCHITECTURE.md
    DATABASE_SCHEMA.md
    AGENT.md
    ROADMAP.md
```

---

## Tenants Supported

- 🍕 Casa da Pizza
- 🥐 Julipan

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python 3.11+ |
| UI | Streamlit |
| Database | Airtable |
| Data | pandas |
| OCR | pytesseract + OpenCV + Pillow |

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Agent Instructions](docs/AGENT.md)
- [Roadmap](docs/ROADMAP.md)

---

## License

MIT
