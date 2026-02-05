# Kostan

Kostan is a **multi-property kost (boarding house) management system** built to replace manual bookkeeping (paper notes, Excel, WhatsApp) with a structured, auditable, and role-aware system.

The system is intentionally **boring and strict under the hood**, while the UI stays simple and familiar for non-technical users.

---

## 1. Core Goals

- Replace notebook-style kost management with structured data
- Support **multiple kosts across regions**
- Support **owner + regional admins**
- Track tenants, payments, and expenses reliably
- Generate monthly summaries without manual math

This is **not** a generic SaaS dashboard.
It is a purpose-built operational system for real kost owners.

---

## 2. Tech Stack

### Frontend

- Vue
- Firebase Hosting
- Firebase Auth

### Backend

- Python
- FastAPI (REST API)
- Firebase ID Token verification (no backend login system)

### Database

- PostgreSQL (Supabase)
- Backend-only access (no direct client DB access)

---

## 3. Authentication & Authorization

### Authentication

- Fully handled by **Firebase Auth**
- Frontend retrieves Firebase ID token
- Token sent to backend via `Authorization: Bearer <token>`

### Authorization

- Backend verifies token
- Extracts `firebase_uid`
- Maps to `user_profiles` table
- Applies **role + region-based access control**

If user has no profile → **403 Forbidden**

---

## 4. User Roles

| Role  | Description                                            |
| ----- | ------------------------------------------------------ |
| owner | Superadmin, full access to all regions, kosts, reports |
| admin | Manages exactly **one region**                         |
| it    | Technical role, no financial modification by default   |

Admins only see kosts inside their assigned region.

---

## 5. Domain Model (Final)

### Key Design Decision

A **kost is the smallest unit**.
Rooms are not modeled individually.

Reality model:

> “Papandayan – 3 kamar”
> “Kerinci – 2 kamar”

Occupancy is **count-based**, not room-based.

---

### Entity Relationships

```
regions
  └── kosts
        └── tenants
              └── transactions
```

---

### Table Responsibilities

#### regions

Logical grouping (area / admin responsibility).

#### kosts

Physical properties.

- Name, address
- `total_units` = number of rooms
- No per-room records

#### tenants

Represents **one occupied slot** in a kost.

- Time-bound record
- Never overwritten
- Closed via `end_date`

Active tenant = `end_date IS NULL`

#### transactions

Single source of financial truth.

- Income and expense events
- Linked to kost, optionally tenant
- Immutable after creation (recommended)

#### user_profiles

Authorization metadata only.

- Maps Firebase user → role + region
- No credentials stored

---

## 6. Critical Business Rules (Must Be Enforced)

These are enforced **in backend logic**, not DB triggers.

1. **Occupancy rule**

```
COUNT(active tenants for kost) <= kost.total_units
```

2. **Derived state only**

- Availability = `total_units - active tenants`
- No stored “status” for kost occupancy

3. **No hard deletes**

- Tenants and transactions must remain auditable

4. **Authorization is server-side**

- UI hiding ≠ security
- Every query filtered by role + region

---

## 7. Financial Model

All money lives in `transactions`.

### Transaction Types

- `income`
- `expense`

### Categories (flexible)

Examples:

- rent
- dp
- admin
- listrik
- pdam
- sampah
- maintenance
- renovasi

No summary tables.
Reports are computed via queries.

---

## 8. Features (Essential Only)

### Dashboard

- Monthly income
- Occupancy count
- Total kost count
- Status tracker (derived)

### Tenant Management

- Add tenant
- Close tenant (move out)
- View active / inactive tenants
- Status labels (dp / aktif / telat / pindah)

### Transactions

- Record payment (income)
- Record expense
- Optional tenant association
- Category-based filtering

### Export / Reports

- Date-range export
- Income report
- Expense report
- Tenant list

### Role-based Access

- Owner sees all
- Admin sees region-only
- IT sees limited or read-only

---

## 9. API Design Guidelines

- REST only
- Role-aware
- Region-scoped
- No business logic in frontend

Examples:

- `GET /kosts` → filtered by user role
- `POST /tenants` → checks occupancy rule
- `POST /transactions` → checks kost access
- `GET /reports/monthly` → owner/admin only

---

## 10. What This System Is NOT

- Not a spreadsheet clone
- Not Firebase-only
- Not room-level management
- Not real-time analytics

This system optimizes for:
**correctness, auditability, and survival in messy reality**

---

## 11. Non-Negotiables for Contributors

- Do not reintroduce room-level entities
- Do not bypass backend authorization
- Do not denormalize for UI convenience
- Do not add auth logic outside Firebase
- Do not mutate historical financial data

---

## 12. Design Intent (Read This First)

This system is intentionally conservative.

If something feels “too strict”, it’s probably protecting you from:

- silent money bugs
- admin data leaks
- broken monthly reports
- unfixable historical errors
