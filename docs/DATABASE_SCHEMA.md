# CashCheck – Database Schema

All data is stored in **Airtable**. There are two types of bases:

1. **Global Base** – shared across all tenants (configuration/master data).
2. **Tenant Operational Base** – one per tenant (transactional data).

---

## Global Base

### Tenants

| Field | Type | Description |
|---|---|---|
| Name | Single line text | Company display name |
| Slug | Single line text | URL-safe identifier (e.g. `casa_da_pizza`) |
| AirtableBaseId | Single line text | Base ID of this tenant's operational base |
| Active | Checkbox | Whether the tenant is active |
| ContactEmail | Email | Primary contact email |
| ContactPhone | Phone number | Primary contact phone |

### Users

| Field | Type | Description |
|---|---|---|
| Name | Single line text | Full name |
| Email | Email | Login email |
| TenantId | Link to Tenants | Associated tenant |
| Role | Single select | Admin, Cashier, Auditor |
| Active | Checkbox | Whether the user is active |

### PaymentMethods

| Field | Type | Description |
|---|---|---|
| Name | Single line text | e.g. Cash, Pix, Credit Card |
| Code | Single line text | Short code |
| Active | Checkbox | |

### Suppliers

| Field | Type | Description |
|---|---|---|
| Name | Single line text | Supplier display name |
| TenantId | Link to Tenants | |
| Category | Single line text | e.g. Food, Delivery, Utilities |
| ContactEmail | Email | |
| ContactPhone | Phone number | |

---

## Tenant Operational Base

One instance per tenant.

### Closings

| Field | Type | Description |
|---|---|---|
| ClosingDate | Date | Date of the daily closing |
| TenantId | Single line text | Tenant identifier |
| PosTotal | Currency | Total reported by POS system |
| ExpectedTotal | Currency | Total expected (usually = PosTotal) |
| SettledTotal | Currency | Total calculated from movements |
| Difference | Currency | `ExpectedTotal − SettledTotal` |
| Status | Single select | Pending, OK, Discrepancy |
| Terminal | Single line text | Terminal/register identifier |
| Notes | Long text | Free-text auditor notes |

### CashMovements

| Field | Type | Description |
|---|---|---|
| TenantId | Single line text | Tenant identifier |
| ClosingId | Single line text | Link to a closing (optional) |
| MovementType | Single select | Sale, Expense, Sangria, Courier Payment, Adjustment |
| PaymentMethod | Single select | Cash, Pix, Credit Card, Debit Card, Ticket, Check |
| Amount | Currency | Absolute value (always positive) |
| Terminal | Single line text | Terminal/register |
| Description | Long text | Optional description |
| Supplier | Single line text | Optional supplier name |
| CreatedAt | Date & time | Record creation timestamp |

### Evidence

| Field | Type | Description |
|---|---|---|
| TenantId | Single line text | Tenant identifier |
| ClosingId | Single line text | Link to a closing (optional) |
| FileName | Single line text | Original file name |
| RawText | Long text | Full OCR output (max 5,000 chars) |
| SuggestedTotal | Currency | Largest value detected by OCR |
| CreatedAt | Date & time | Record creation timestamp |

### Terminals

| Field | Type | Description |
|---|---|---|
| Name | Single line text | Terminal display name |
| Code | Single line text | Short identifier |
| Active | Checkbox | Whether the terminal is in use |

---

## Reconciliation Formula

```
settled_total  = Σ signed_amount
               = +Sales − Expenses − Sangria − Courier Payments ± Adjustments

difference     = expected_total − settled_total

status         = "OK"           if |difference| ≤ R$ 0.01
               = "Discrepancy"  otherwise
```
