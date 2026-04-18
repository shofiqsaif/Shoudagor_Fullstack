# Claims Module - Complete Reference Documentation

**Generated:** April 16, 2026  
**Scope:** Full-stack analysis of the Claims (Claims Processing) Module  
**Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND LAYER (React + TypeScript + TailwindCSS + shadcn/ui)             │
│  ├── React Router v7 for navigation                                        │
│  ├── TanStack Query for state management                                    │
│  ├── React Hook Form + Zod for validation                                   │
│  ├── Lucide React for icons                                                 │
│  └── Sonner for toast notifications                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  BACKEND LAYER (FastAPI + SQLAlchemy + Pydantic)                           │
│  ├── FastAPI for REST API endpoints                                        │
│  ├── SQLAlchemy ORM for database operations                                  │
│  ├── Pydantic for request/response validation                              │
│  ├── Repository Pattern for data access                                    │
│  └── Service Layer for business logic                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  DATABASE LAYER (PostgreSQL)                                               │
│  ├── Schema: `inventory`                                                    │
│  ├── Tables: claim_scheme, claim_slab, claim_log                           │
│  ├── Soft delete pattern (is_deleted flag)                                  │
│  └── Audit trail (cb, mb, cd, md fields)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  EXTERNAL SERVICES                                                         │
│  ├── ReportLab for PDF export                                               │
│  ├── OpenPyXL for Excel export                                              │
│  └── pytz for timezone handling (Asia/Dhaka)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
                    ┌─────────────────────────────────────┐
                    │          AppClientCompany           │
                    │         (1 company)                 │
                    └──────────────┬──────────────────────┘
                                   │ 1:N
                                   ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    claim_scheme                              │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │ scheme_id (PK)                                          │ │
    │  │ scheme_name, scheme_type, description                  │ │
    │  │ start_date, end_date, applicable_to                     │ │
    │  │ trigger_product_id ──────┐                              │ │
    │  │ trigger_variant_id ──────┼─────┐                        │ │
    │  │ free_product_id ─────────┤     │                        │ │
    │  │ free_variant_id ─────────┤     │                        │ │
    │  │ company_id (FK)          │     │                        │ │
    │  └──────────────────────────┼─────┼────────────────────────┘ │
    │                             │     │     1:N                  │
    │                             ▼     ▼        │                │
    │  ┌──────────────┐   ┌──────────────┐       │                │
    │  │   product    │   │product_variant│       ▼                │
    │  │  (trigger)   │   │  (trigger)    │ ┌──────────────┐       │
    │  └──────────────┘   └──────────────┘ │ claim_slab   │       │
    │  ┌──────────────┐   ┌──────────────┐ │ (N slabs)    │       │
    │  │   product    │   │product_variant│ │ per scheme   │       │
    │  │   (free)     │   │   (free)      │ └──────────────┘       │
    │  └──────────────┘   └──────────────┘                        │
    └─────────────────────────────────────────────────────────────┘
                                   │ 1:N
                                   ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                     claim_log                                │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │ log_id (PK)                                             │ │
    │  │ scheme_id (FK) ────────┐                                │ │
    │  │ ref_id, ref_type       │ (purchase_order/sales_order)  │ │
    │  │ order_detail_id        │                                │ │
    │  │ product_id, variant_id │                                │ │
    │  │ applied_on_qty         │                                │ │
    │  │ given_free_qty         │                                │ │
    │  │ given_discount_amount  │                                │ │
    │  │ status ('active','reversed','adjusted')                │ │
    │  │ reversed_by_log_id ────┼────┐ (self-referential)        │ │
    │  │ reversal_reason        │    │                           │ │
    │  └────────────────────────┘    │                           │ │
    │                                ▼                           │ │
    │  ┌─────────────────────────────────────────────────────────┐ │ │
    │  │                    Self (reversal entry)                │ │ │
    │  │              (negative values to offset original)       │ │ │
    │  └─────────────────────────────────────────────────────────┘ │ │
    └─────────────────────────────────────────────────────────────────┘
```

**Cardinalities:**
- `AppClientCompany` 1:N `ClaimScheme` (one company has many schemes)
- `ClaimScheme` 1:N `ClaimSlab` (one scheme has multiple slabs/thresholds)
- `ClaimScheme` 1:N `ClaimLog` (one scheme applied to many orders)
- `Product` 1:N `ClaimScheme` (as trigger or free product)
- `ProductVariant` 1:N `ClaimScheme` (as trigger or free variant)
- `ClaimLog` self-referential 1:1 (reversal tracking)

### 1.3 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend Framework** | React 18+ | UI component library |
| **Language** | TypeScript | Type-safe development |
| **Styling** | TailwindCSS | Utility-first CSS |
| **UI Components** | shadcn/ui | Pre-built accessible components |
| **Forms** | React Hook Form | Form state management |
| **Validation** | Zod | Schema validation |
| **State Management** | TanStack Query | Server state, caching, mutations |
| **Routing** | React Router v7 | Client-side navigation |
| **Backend Framework** | FastAPI | High-performance Python API |
| **ORM** | SQLAlchemy | Database abstraction |
| **Database** | PostgreSQL | Relational data storage |
| **Schema Validation** | Pydantic | Request/response models |
| **Export** | OpenPyXL, ReportLab | Excel and PDF generation |
| **Timezone** | pytz | Bangladesh Standard Time (Asia/Dhaka) |

---

## 2. Entity Inventory

### 2.1 claim_scheme (Main Entity)

**Table:** `inventory.claim_scheme`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| scheme_id | Integer | PK, Auto-increment | Unique identifier |
| scheme_name | String(200) | NOT NULL | Human-readable name |
| description | String(500) | Nullable | Detailed description |
| scheme_type | String(50) | NOT NULL | `buy_x_get_y`, `rebate_flat`, `rebate_percentage` |
| start_date | TIMESTAMP | NOT NULL | Scheme activation date |
| end_date | TIMESTAMP | NOT NULL | Scheme expiration date |
| applicable_to | String(50) | NOT NULL, Default: `purchase` | `purchase`, `sale`, or `all` |
| trigger_product_id | Integer | FK → product.product_id, Nullable | Product that triggers scheme |
| trigger_variant_id | Integer | FK → product_variant.variant_id, Nullable | Specific variant trigger |
| free_product_id | Integer | FK → product.product_id, Nullable | Product given free |
| free_variant_id | Integer | FK → product_variant.variant_id, Nullable | Specific variant free |
| is_active | Boolean | NOT NULL, Default: TRUE | Soft activation flag |
| is_deleted | Boolean | NOT NULL, Default: FALSE | Soft delete flag |
| company_id | Integer | FK → app_client_company.id, NOT NULL | Multi-tenant isolation |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | NOT NULL, Default: NOW() | Created date |
| md | TIMESTAMP | NOT NULL, Default: NOW() | Modified date |

**Relationships:**
- Belongs to: `AppClientCompany`
- Has many: `ClaimSlab` (cascade delete)
- Has many: `ClaimLog`
- Belongs to (optional): `Product` (trigger_product, free_product)
- Belongs to (optional): `ProductVariant` (trigger_variant, free_variant)

---

### 2.2 claim_slab (Junction/Child Entity)

**Table:** `inventory.claim_slab`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| slab_id | Integer | PK, Auto-increment | Unique identifier |
| scheme_id | Integer | FK → claim_scheme.scheme_id, NOT NULL | Parent scheme |
| threshold_qty | Numeric(18,4) | NOT NULL, > 0 | Quantity to trigger slab |
| free_qty | Numeric(18,4) | NOT NULL, Default: 0 | Free quantity given |
| discount_amount | Numeric(18,2) | Nullable | Flat discount value |
| discount_percentage | Numeric(5,2) | Nullable | Percentage discount (0-100) |
| is_deleted | Boolean | NOT NULL, Default: FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by |
| mb | Integer | NOT NULL | Modified by |
| cd | TIMESTAMP | NOT NULL | Created date |
| md | TIMESTAMP | NOT NULL | Modified date |

**Relationships:**
- Belongs to: `ClaimScheme` (with cascade delete)

**Constraints:**
- Multiple slabs per scheme must have unique `threshold_qty` values

---

### 2.3 claim_log (Audit/Transaction Entity)

**Table:** `inventory.claim_log`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| log_id | Integer | PK, Auto-increment | Unique identifier |
| scheme_id | Integer | FK → claim_scheme.scheme_id, NOT NULL | Applied scheme |
| ref_id | Integer | NOT NULL | Order ID (PO or SO) |
| ref_type | String(50) | NOT NULL | `purchase_order` or `sales_order` |
| order_detail_id | Integer | Nullable | Specific order line item |
| product_id | Integer | FK → product.product_id, Nullable | Product claimed |
| variant_id | Integer | FK → product_variant.variant_id, Nullable | Variant claimed |
| applied_on_qty | Numeric(18,4) | NOT NULL | Quantity scheme applied to |
| given_free_qty | Numeric(18,4) | NOT NULL, Default: 0 | Free qty given |
| given_discount_amount | Numeric(18,2) | NOT NULL, Default: 0 | Discount given |
| free_product_id | Integer | FK → product.product_id, Nullable | Free product (if different) |
| free_variant_id | Integer | FK → product_variant.variant_id, Nullable | Free variant |
| status | String(20) | NOT NULL, Default: `active` | `active`, `reversed`, `adjusted` |
| reversed_by_log_id | Integer | FK → claim_log.log_id, Nullable | Reversal entry reference |
| reversal_reason | String(500) | Nullable | Reason for reversal/adjustment |
| is_deleted | Boolean | NOT NULL, Default: FALSE | Soft delete flag |
| company_id | Integer | FK → app_client_company.id, NOT NULL | Multi-tenant |
| cb | Integer | NOT NULL | Created by |
| mb | Integer | NOT NULL | Modified by |
| cd | TIMESTAMP | NOT NULL | Created date |
| md | TIMESTAMP | NOT NULL | Modified date |

**Table Arguments:**
```sql
-- Unique constraint for idempotency
UNIQUE (order_detail_id, scheme_id, status)

-- Indexes for performance
INDEX idx_claim_log_ref (ref_id, ref_type)
INDEX idx_claim_log_scheme (scheme_id)
```

**Relationships:**
- Belongs to: `ClaimScheme`
- Belongs to: `Product`, `ProductVariant`
- Self-referential: `reversed_by_log_id` → `log_id`

---

## 3. Backend Operations Reference

### 3.1 ClaimScheme Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| Create | POST | `/api/company/claims/schemes` | `ClaimService.create_scheme()` | Create new scheme with slabs |
| List | GET | `/api/company/claims/schemes` | `ClaimService.list_schemes()` | Paginated list with filters |
| Get Single | GET | `/api/company/claims/schemes/{id}` | `ClaimService.get_scheme()` | Get scheme with related data |
| Update | PUT | `/api/company/claims/schemes/{id}` | `ClaimService.update_scheme()` | Update scheme (replaces slabs) |
| Delete | DELETE | `/api/company/claims/schemes/{id}` | `ClaimService.delete_scheme()` | Soft delete scheme |
| Evaluate | POST | `/api/company/claims/orders/re-evaluate` | `ClaimService.re_evaluate_order_schemes()` | Re-apply schemes to order |

### 3.2 ClaimLog Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/claims/logs` | `ClaimService.list_logs()` | Query claim applications |
| Reverse | POST | `/api/company/claims/logs/reverse` | `ClaimService.reverse_claim_logs()` | Reverse all logs for order |
| Adjust | POST | `/api/company/claims/logs/adjust` | `ClaimService.adjust_claim_logs()` | Partial return adjustment |

### 3.3 Report Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| Summary | GET | `/api/company/claims/reports/summary` | `ClaimReportService.get_claim_summary()` | Aggregate metrics |
| By Scheme | GET | `/api/company/claims/reports/by-scheme` | `ClaimReportService.get_claims_by_scheme()` | Grouped by scheme |
| By Product | GET | `/api/company/claims/reports/by-product` | `ClaimReportService.get_claims_by_product()` | Grouped by product |
| Free Qty by Variant | GET | `/api/company/claims/reports/free-qty-by-variant` | `ClaimReportService.get_free_qty_by_variant()` | Variant-level free qty |
| Discount by Variant | GET | `/api/company/claims/reports/discount-by-variant` | `ClaimReportService.get_discount_by_variant()` | Variant-level discounts |
| Variants List | GET | `/api/company/claims/reports/variants-list` | `ClaimReportService.get_all_variants_for_filter()` | Filter dropdown data |
| Export Free Qty | GET | `/api/company/claims/reports/free-qty-by-variant/export` | `ClaimExportService.export_free_qty_*()` | Excel/PDF export |
| Export Discount | GET | `/api/company/claims/reports/discount-by-variant/export` | `ClaimExportService.export_discount_*()` | Excel/PDF export |

### 3.4 Dashboard Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| Dashboard Summary | GET | `/api/dashboard/claims/dashboard-summary` | `ClaimsDashboardService.get_dashboard_summary()` | Complete dashboard data |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| Scheme List | `/claims/schemes` | ✅ | List all schemes with pagination and actions |
| Scheme Form (Create) | `/claims/schemes/new` | ✅ | Create new promotional scheme |
| Scheme Form (Edit) | `/claims/schemes/:id/edit` | ✅ | Edit existing scheme |
| Scheme Logs | `/claims/logs` | ✅ | Historical claim applications with filters |
| Claim Reports | `/claims/reports` | ✅ | Variant-wise reports with export |

**Route Configuration** (from `App.tsx`):
```typescript
// Admin Routes (requires AdminRoute guard)
{
  element: <AdminRoute />,
  children: [
    { path: "/claims/schemes", element: <SchemeList /> },
    { path: "/claims/schemes/new", element: <SchemeForm /> },
    { path: "/claims/schemes/:id/edit", element: <SchemeForm /> },
    { path: "/claims/logs", element: <SchemeLogList /> },
    { path: "/claims/reports", element: <ClaimReports /> },
  ]
}
```

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| SchemeForm | `src/pages/claims/SchemeForm.tsx` | Create/edit scheme with dynamic slabs |
| SchemeDetailsDialog | `src/components/claims/SchemeDetailsDialog.tsx` | View scheme details in modal |
| ConfirmDeleteDialog | `src/components/shared/ConfirmDeleteDialog.tsx` | Delete confirmation with name validation |

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| CustomTable | `src/components/Table.tsx` | Reusable data table with pagination |
| SearchableSelect | `src/components/forms/SearchWithSelect.tsx` | Product/variant dropdowns |
| DateRangePicker | `src/components/DateRangePicker.tsx` | Date range filtering |
| ActiveInactiveStatus | `src/components/shared/ActiveInactiveStatus.tsx` | Status badge display |
| FreeQtyReportTable | `src/components/claims/FreeQtyReportTable.tsx` | Free quantity report table |
| DiscountReportTable | `src/components/claims/DiscountReportTable.tsx` | Discount report table |

### 4.4 Context Providers

| Context | File Path | Purpose |
|---------|-----------|---------|
| Claims Dashboard | Uses TanStack Query | Server state management for claims |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `src/lib/api/claimsApi.ts` | `getSchemes()`, `getScheme()`, `createScheme()`, `updateScheme()`, `deleteScheme()`, `getClaimLogs()`, `getFreeQtyByVariant()`, `getDiscountByVariant()`, `exportFreeQtyReport()`, `exportDiscountReport()`, `reevaluateOrderSchemes()`, `reverseClaimLogs()`, `adjustClaimLogs()` |
| `src/lib/api/adminClaimsDashboardApi.ts` | `getClaimsDashboardSummary()` |

### 4.6 Types & Zod Schemas

| Schema | File | Fields |
|--------|------|--------|
| `ClaimSlabSchema` | `src/lib/schema/claims.ts` | `slab_id?, scheme_id?, threshold_qty, free_qty?, discount_amount?, discount_percentage?` |
| `ClaimSchemeSchema` | `src/lib/schema/claims.ts` | `scheme_id?, scheme_name, description?, scheme_type, start_date, end_date, trigger_product_id?, trigger_variant_id, free_product_id?, free_variant_id?, applicable_to, is_active?, slabs[]` |
| `ClaimSchemeResponse` | `src/lib/schema/claims.ts` | Extends ClaimSchemeType + `trigger_product?, trigger_variant?, free_product?, free_variant?` |
| `ClaimLogResponse` | `src/lib/schema/claims.ts` | `log_id, scheme_id, ref_id, ref_type, order_detail_id?, product_id?, variant_id?, applied_on_qty, given_free_qty, given_discount_amount, company_id, cd, scheme?, product_name?, variant_name?` |
| `VariantFreeQtyReportResponse` | `src/lib/schema/claims.ts` | `date_range_start?, date_range_end?, ref_type?, total_free_qty, total_applications, items[]` |
| `VariantDiscountReportResponse` | `src/lib/schema/claims.ts` | `date_range_start?, date_range_end?, ref_type?, total_discount_amount, total_applications, items[]` |

---

## 5. Interconnected Workflows

### 5.1 Scheme Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: User navigates to Claims > Add Scheme                           │
│ → Route: `/claims/schemes/new`                                          │
│ → Component: `SchemeForm.tsx`                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: User fills Basic Information                                    │
│ → Fields: scheme_name, description, scheme_type, applicable_to          │
│ → Date pickers: start_date, end_date (react-day-picker)                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: User selects Trigger Product/Variant                              │
│ → SearchableSelect for products (fetched from `/products`)              │
│ → Dependent dropdown for variants (fetched from `/inventory/product-variant`)
│ → Watch: trigger_product_id change resets trigger_variant_id           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: For buy_x_get_y, select Free Product/Variant                     │
│ → Conditional rendering based on scheme_type                              │
│ → Same product/variant selection pattern                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Configure Slabs                                               │
│ → useFieldArray for dynamic slab management                              │
│ → Fields adapt: free_qty (buy_x_get_y), discount_amount (rebate_flat),   │
│   discount_percentage (rebate_percentage)                               │
│ → Validation: threshold_qty must be unique across slabs                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Submit to Backend                                               │
│ → API: `createScheme(data)` → POST `/api/company/claims/schemes`       │
│ → Payload: ClaimSchemeType with ISO date strings                          │
│ → Backend: `ClaimService.create_scheme()`                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 7: Backend Validation & Creation                                   │
│ → Check: end_date > start_date, end_date not in past                    │
│ → Check: overlapping schemes (find_overlapping_schemes)                 │
│ → Check: at least one trigger (product or variant)                        │
│ → Auto-link: variant selected → auto-populate product_id                  │
│ → Create: ClaimScheme + ClaimSlab records (transaction)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 8: Success Redirect                                                │
│ → Toast: "Scheme created successfully"                                  │
│ → Invalidate: `['/claims/schemes']` query cache                          │
│ → Navigate: `/claims/schemes`                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Order Processing with Scheme Application

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: User creates Purchase/Sales Order                                 │
│ → API: `evaluate_pre_claim()` called automatically                        │
│ → Target module: 'purchase' or 'sale' based on order type               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Backend evaluates active schemes                                │
│ → Query: `get_active_schemes(company_id, target_module)`                 │
│ → Filter: active, not deleted, date range valid, applicable_to matches  │
│ → Organize: schemes by variant_id and product_id for fast lookup        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Match items to schemes                                          │
│ → For each order item: check variant_schemes[variant_id]                 │
│ → Fallback: check product_schemes[product_id]                            │
│ → Specific scheme: if applied_scheme_id provided, verify it's active    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Calculate benefits                                              │
│ → Sort slabs by threshold_qty DESC (highest first)                       │
│ → Find first applicable slab: quantity >= threshold                      │
│ → Calculate multiplier: floor(quantity / threshold)                       │
│ → Apply:                                                                  │
│   - buy_x_get_y: free_qty * multiplier                                  │
│   - rebate_flat: discount_amount * multiplier                           │
│   - rebate_percentage: (multiplier * threshold) * unit_price * %        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Select best scheme (FND-014 Fix)                                │
│ → Calculate total benefit value: (free_qty * price) + discount          │
│ → If multiple schemes match, keep only the highest benefit                │
│ → Set: free_quantity, discount_amount, applied_scheme_id                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Log claim application (idempotent)                                │
│ → API: `log_claim_applications()`                                       │
│ → Check: existing logs for (order_detail_id, scheme_id, 'active')         │
│ → Skip if duplicate (prevents double-counting)                            │
│ → Create: ClaimLog record with all benefit details                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Order Cancellation / Return Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 1: Full Order Cancellation                                     │
│ → User cancels entire order (status change to Cancelled)                │
│ → Trigger: `reverse_claim_logs()`                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Reverse All Active Logs                                                  │
│ → Query: all ClaimLog where ref_id={order_id}, ref_type={type},         │
│          status='active'                                                  │
│ → For each log:                                                           │
│   - Skip if all values are zero (CLM-001 fix)                           │
│   - Create reversal entry with NEGATIVE values                          │
│   - Set original log status='reversed'                                    │
│   - Link: original.reversed_by_log_id = reversal.log_id                  │
│ → Result: Net zero impact on claim totals                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 2: Partial Return (Sales Order)                                  │
│ → User processes return for specific items                                │
│ → Trigger: `adjust_claim_logs()`                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Adjust Specific Order Detail                                             │
│ → Query: ClaimLog where order_detail_id={detail_id}, status='active'    │
│ → Calculate ratio: returned_qty / applied_on_qty                          │
│ → Create adjustment entry:                                                │
│   - applied_on_qty: -returned_qty                                         │
│   - given_free_qty: -(original_free * ratio)                              │
│   - given_discount_amount: -(original_discount * ratio)                 │
│   - reversal_reason: "Partial return adjustment: {qty} units"             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Report Generation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: User navigates to Claims > Reports                                │
│ → Component: `ClaimReports.tsx`                                           │
│ → Default: Last 30 days date range                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Apply Filters                                                     │
│ → Date range picker (react-day-picker)                                    │
│ → Reference type: All / purchase_order / sales_order                      │
│ → Variant filter: dropdown from `getVariantsForFilter()`                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Fetch Report Data                                                 │
│ → Tab: Free Qty → `getFreeQtyByVariant()`                                 │
│   - Aggregates: SUM(given_free_qty), COUNT(logs)                          │
│   - Groups by: variant_id, product_id                                      │
│   - Array aggregation: schemes_involved (distinct scheme names)           │
│ → Tab: Discount → `getDiscountByVariant()`                                │
│   - Same pattern, SUM(given_discount_amount)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Export (Optional)                                                 │
│ → Excel: `exportFreeQtyReport('excel')` / `exportDiscountReport('excel')`   │
│   - OpenPyXL generates .xlsx with styling                                 │
│ → PDF: `exportFreeQtyReport('pdf')` / `exportDiscountReport('pdf')`        │
│   - ReportLab generates landscape A4 tables                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Scheme Overlap Prevention

**Problem:** Prevent creating schemes with overlapping date ranges on the same product/variant.

**Solution:**
```python
# claim_repository.py - find_overlapping_schemes()
conditions = [
    ClaimScheme.company_id == company_id,
    ClaimScheme.is_deleted == False,
    ClaimScheme.start_date <= end_date,      # Overlap condition 1
    ClaimScheme.end_date >= start_date,        # Overlap condition 2
]

# Key fix: applicable_to allows overlap between purchase and sale schemes
if applicable_to:
    conditions.append(
        or_(
            ClaimScheme.applicable_to == applicable_to,
            ClaimScheme.applicable_to == "all",
        )
    )
```

**Business Rule:**
- Same product/variant CAN have overlapping schemes if they target different modules (purchase vs sale)
- Cannot have overlapping schemes for the same module on the same product/variant

### 6.2 Slab-Based Benefit Calculation

**Calculation Logic:**
```python
# claim_service.py - _calculate_scheme_benefits()
sorted_slabs = sorted(scheme.slabs, key=lambda s: s.threshold_qty, reverse=True)

for slab in sorted_slabs:
    if quantity >= threshold:
        multiplier = int(quantity // threshold)  # Floor division
        
        if scheme.scheme_type == "buy_x_get_y":
            benefits["free_quantity"] = multiplier * float(slab.free_qty)
            # Validation: cap at purchased quantity
            if benefits["free_quantity"] > quantity:
                benefits["free_quantity"] = quantity
                
        elif scheme.scheme_type == "rebate_flat":
            benefits["discount_amount"] = multiplier * float(slab.discount_amount)
            
        elif scheme.scheme_type == "rebate_percentage":
            # FIXED: Discount only applies to threshold multiples
            discountable_qty = multiplier * threshold
            benefits["discount_amount"] = discountable_qty * unit_price * (percentage / 100)
```

**Example:**
- Scheme: Buy 10 Get 1 Free
- Order: 25 units
- Multiplier: floor(25 / 10) = 2
- Free quantity: 2 × 1 = 2 units (not 2.5)

### 6.3 Idempotent Claim Logging

**Problem:** Prevent duplicate ClaimLog entries when order is saved multiple times.

**Solution:**
```python
# claim_service.py - log_claim_applications()
existing_logs = self.repo.get_logs_by_reference(ref_id=ref_id, ref_type=ref_type)
existing_detail_schemes = {
    (log.order_detail_id, log.scheme_id)
    for log in existing_logs
    if log.status == "active"
}

# Before creating new log
if (order_detail_id, scheme_id) in existing_detail_schemes:
    logger.debug(f"Skipping duplicate claim log for order_detail_id={order_detail_id}")
    continue
```

**Database Constraint:**
```sql
UNIQUE (order_detail_id, scheme_id, status)
```

### 6.4 Reversal and Adjustment Tracking

**Status Flow:**
```
Active Log ──► Reversed (full cancellation)
     │
     └──► Adjustment Entry (partial return)
```

**Reversal Entry Structure:**
```python
reversal = ClaimLog(
    scheme_id=original.scheme_id,
    ref_id=original.ref_id,
    ref_type=original.ref_type,
    applied_on_qty=-original.applied_on_qty,      # Negative
    given_free_qty=-original.given_free_qty,        # Negative
    given_discount_amount=-original.given_discount_amount,  # Negative
    status="active",  # New entry is active
    reversal_reason="Order cancelled",
)
original.status = "reversed"
original.reversed_by_log_id = reversal.log_id
```

### 6.5 Date Validation and Timezone Handling

**Validation Rules:**
1. `end_date` must be after `start_date`
2. `end_date` cannot be in the past
3. Warning if `start_date` is in the past (allowed but warned)

**Timezone Handling:**
```python
def _make_naive_dhaka(self, dt: datetime) -> datetime:
    """Convert to Asia/Dhaka timezone and make naive for DB storage"""
    tz = pytz.timezone("Asia/Dhaka")
    if dt.tzinfo is not None:
        return dt.astimezone(tz).replace(tzinfo=None)
    return dt  # Assume already Dhaka time if naive
```

### 6.6 Multi-Tenant Isolation

**Implementation:**
- All queries filter by `company_id` from JWT token
- `get_current_company_id` dependency injects company context
- Repository methods accept `company_id` parameter
- Cross-company data access is prevented at query level

### 6.7 Soft Delete Pattern

**Implementation:**
```python
# Repository delete method
def delete(self, db_scheme: ClaimScheme, user_id: int):
    db_scheme.is_deleted = True  # Soft delete
    db_scheme.mb = user_id
    db_scheme.md = func.now()
    # No actual DELETE SQL issued
```

**Query Pattern:**
```python
# All list queries include:
query = query.filter(ClaimScheme.is_deleted == False)
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **ClaimScheme** | ✅ GET /schemes | ✅ GET /schemes/{id} | ✅ POST /schemes | ✅ PUT /schemes/{id} | ✅ DELETE /schemes/{id} | Re-evaluate: POST /orders/re-evaluate |
| **ClaimLog** | ✅ GET /logs | - | - | - | - | Reverse: POST /logs/reverse, Adjust: POST /logs/adjust |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-------------------|------------------|
| List Schemes | `getSchemes(skip, limit, isActive?, search?)` | GET `/api/company/claims/schemes` |
| Get Scheme | `getScheme(id)` | GET `/api/company/claims/schemes/{id}` |
| Create Scheme | `createScheme(data)` | POST `/api/company/claims/schemes` |
| Update Scheme | `updateScheme(id, data)` | PUT `/api/company/claims/schemes/{id}` |
| Delete Scheme | `deleteScheme(id)` | DELETE `/api/company/claims/schemes/{id}` |
| List Logs | `getClaimLogs(skip, limit, filters)` | GET `/api/company/claims/logs` |
| Re-evaluate | `reevaluateOrderSchemes(orderId, orderType)` | POST `/api/company/claims/orders/re-evaluate` |
| Reverse Logs | `reverseClaimLogs(refId, refType, reason)` | POST `/api/company/claims/logs/reverse` |
| Adjust Logs | `adjustClaimLogs(refId, refType, factor, reason)` | POST `/api/company/claims/logs/adjust` |
| Free Qty Report | `getFreeQtyByVariant(dates, refType?, variantId?)` | GET `/api/company/claims/reports/free-qty-by-variant` |
| Discount Report | `getDiscountByVariant(dates, refType?, variantId?)` | GET `/api/company/claims/reports/discount-by-variant` |
| Export Excel | `exportFreeQtyReport(dates, format='excel')` | GET `/api/company/claims/reports/free-qty-by-variant/export` |
| Dashboard Summary | `getClaimsDashboardSummary(filters)` | GET `/api/dashboard/claims/dashboard-summary` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/claims.py` | SQLAlchemy models: ClaimScheme, ClaimSlab, ClaimLog |
| **Schemas** | `Shoudagor/app/schemas/claims.py` | Pydantic schemas for API I/O |
| **Dashboard Schemas** | `Shoudagor/app/schemas/dashboard/claims.py` | Dashboard-specific DTOs |
| **Repository** | `Shoudagor/app/repositories/claims/claim_repository.py` | Data access layer with aggregation queries |
| **Service** | `Shoudagor/app/services/claims/claim_service.py` | Core business logic, scheme evaluation |
| **Report Service** | `Shoudagor/app/services/claims/claim_report_service.py` | Report aggregation queries |
| **Export Service** | `Shoudagor/app/services/claims/claim_export_service.py` | Excel/PDF generation |
| **Dashboard Service** | `Shoudagor/app/services/dashboard/claims_dashboard_service.py` | Dashboard data aggregation |
| **API Routes** | `Shoudagor/app/api/claims.py` | FastAPI endpoints (schemes, logs, reports) |
| **Dashboard API** | `Shoudagor/app/api/dashboard/admin_claims.py` | Dashboard endpoint |
| **Alembic Migration** | `Shoudagor/alembic/versions/4a56edd10e3f_add_claims_schemes.py` | Initial schema migration |
| **Alembic Migration** | `Shoudagor/alembic/versions/9924dce24459_add_applicable_to_to_claims.py` | Add applicable_to field |
| **Alembic Migration** | `Shoudagor/alembic/versions/a1234567890ab_claim_reversal.py` | Add reversal tracking |
| **Alembic Migration** | `Shoudagor/alembic/versions/cb182489557f_add_unique_constraint_on_claim_log_.py` | Add idempotency constraint |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages** | `shoudagor_FE/src/pages/claims/SchemeList.tsx` | Scheme listing with pagination |
| **Pages** | `shoudagor_FE/src/pages/claims/SchemeForm.tsx` | Create/edit scheme form |
| **Pages** | `shoudagor_FE/src/pages/claims/SchemeLogList.tsx` | Claim application logs |
| **Pages** | `shoudagor_FE/src/pages/claims/ClaimReports.tsx` | Reports with export |
| **Components** | `shoudagor_FE/src/components/claims/SchemeDetailsDialog.tsx` | Scheme detail modal |
| **Components** | `shoudagor_FE/src/components/claims/FreeQtyReportTable.tsx` | Free quantity table |
| **Components** | `shoudagor_FE/src/components/claims/DiscountReportTable.tsx` | Discount table |
| **Dashboard** | `shoudagor_FE/src/components/dashboard/ClaimsWidget.tsx` | Dashboard KPI widget |
| **API** | `shoudagor_FE/src/lib/api/claimsApi.ts` | Main claims API client |
| **API** | `shoudagor_FE/src/lib/api/adminClaimsDashboardApi.ts` | Dashboard API client |
| **Schemas** | `shoudagor_FE/src/lib/schema/claims.ts` | Zod validation schemas |
| **Hooks** | `shoudagor_FE/src/hooks/useClaimsDashboard.ts` | TanStack Query hooks |
| **Routes** | `shoudagor_FE/src/App.tsx` (lines 237-241) | Route definitions |

---

## 9. Appendix: Operation Counts

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|------------------------|---------------------|
| **ClaimScheme** | 5 (List, Get, Create, Update, Delete) | 4 (Re-evaluate, Get Active, Find Overlapping, Validate Slabs) | 5 (getSchemes, getScheme, createScheme, updateScheme, deleteScheme) | 2 (SchemeList, SchemeForm) |
| **ClaimSlab** | 0 (Managed via Scheme) | 2 (Create with Scheme, Update with Scheme) | 0 | 0 (embedded in SchemeForm) |
| **ClaimLog** | 1 (List) | 5 (Log Applications, Reverse, Adjust, Get by Reference, Idempotency Check) | 4 (getClaimLogs, reevaluateOrderSchemes, reverseClaimLogs, adjustClaimLogs) | 1 (SchemeLogList) |
| **Reports** | 0 | 6 (Summary by Scheme, By Product, Free Qty by Variant, Discount by Variant, Variants List, Export) | 6 (getClaimSummary, getClaimsByScheme, getClaimsByProduct, getFreeQtyByVariant, getDiscountByVariant, export*) | 3 (ClaimReports, FreeQtyReportTable, DiscountReportTable) |
| **Dashboard** | 0 | 1 (get_dashboard_summary) | 1 (getClaimsDashboardSummary) | 1 (ClaimsWidget) |
| **TOTAL** | **6** | **18** | **16** | **7** |

---

## 10. Known Issues & Fixes Reference

| Issue ID | Description | Fix Location |
|----------|-------------|--------------|
| CLM-001 | Zero-value reversal entries created | `claim_service.py:678-690` - Skip logs with no values |
| CLM-002 | Re-evaluation changes not persisted | `claim_service.py:928-932` - Added explicit commit |
| CLM-003 | Invalid slab configurations allowed | `claim_service.py:86-109` - Scheme-type validation |
| FND-014 | Multiple scheme benefits summed incorrectly | `claim_service.py:494-524` - Select best scheme only |
| FND-015 | Manual overrides reset when scheme inactive | `claim_service.py:478-486` - Preserve manual values |
| ISSUE-018 | Past dates allowed, overlapping schemes | `claim_service.py:50-64`, `233-263` - Date validation |
| ISSUE-019 | No reversal tracking | Migration + `claim_service.py:641-757` - Reversal system |
| ISSUE-020 | Cannot re-evaluate schemes | `claim_service.py:826-947` - Re-evaluation endpoint |
| ISSUE-037 | Missing indexes on claim_log | Migration `cb182489557f` - Added composite indexes |
| BE-021 | Duplicate claim logs possible | Migration - Unique constraint on (detail_id, scheme_id, status) |

---

**End of Documentation**

*This reference covers the complete Claims (Claims Processing) module of the Shoudagor ERP system. For questions or updates, refer to the source files listed in the File Map sections.*
