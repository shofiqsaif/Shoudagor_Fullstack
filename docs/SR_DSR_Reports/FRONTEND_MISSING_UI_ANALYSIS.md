# Frontend UI Missing — Backend Features Without Frontend Pages

> **Analysis Date:** 2026-04-03  
> **Scope:** All backend API endpoints cross-referenced against frontend pages, components, and API client functions  
> **Total Backend Endpoints:** ~216  
> **Total Frontend API Functions:** ~250  
> **Total Frontend Pages:** ~120

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **HIGH** | 3 | Core features fully built in backend with zero frontend UI |
| **MEDIUM** | 10 | Backend endpoints exist, API functions may exist, but UI actions/pages missing |
| **LOW** | 7 | Optimization endpoints, debug tools, or redundant alternate paths |

---

## HIGH Severity — Core Features Missing UI

### 1. Product Variant Image Management (20 endpoints, 0 frontend)

**Backend:** `app/api/inventory/product_variant_image.py`  
**What's Built:** Complete S3-backed image management system with:
- Single & batch image upload (multipart/form-data)
- Presigned URL workflow for direct S3 uploads (request → confirm → status → retry → cleanup)
- Image gallery management (list, get, update metadata, delete)
- Primary image selection
- Image reordering
- Bulk operations
- Upload statistics (per-variant and company-wide)
- Pending uploads tracking

**Missing Frontend:**
| Missing UI | What It Should Do |
|------------|-------------------|
| **Image upload component** | Upload single/multiple images for a product variant |
| **Image gallery viewer** | Display all images for a variant in a grid/carousel |
| **Primary image selector** | Click to set which image is the thumbnail/primary |
| **Image reorder UI** | Drag-and-drop to reorder images |
| **Image metadata editor** | Edit alt text, display order per image |
| **Presigned URL upload flow** | Get presigned URL → upload directly to S3 → confirm |
| **Upload progress indicator** | Show upload status for pending/failed uploads |
| **Image delete confirmation** | Delete image with dependency check |

**Impact:** Product variants have no images in the system despite the entire backend infrastructure being ready. This affects product catalog display, POS interface, and mobile SR/DSR apps.

**Files that need to be created:**
- `src/lib/api/productVariantImageApi.ts` — API client (20 functions)
- `src/components/forms/ProductImageUpload.tsx` — Upload form with drag-and-drop
- `src/components/shared/ProductImageGallery.tsx` — Gallery with reorder/primary selection
- Integration into `src/pages/products/new/AddProduct.tsx` and `src/pages/products/Products.tsx`

---

### 2. Sales Ledger (Khata) Management (5 endpoints, API exists, 0 UI)

**Backend:** `app/api/sr_reports.py` → `/sr-reports/ledger/*`  
**What's Built:** Full CRUD for manual ledger entries with:
- Create ledger entries (order amount, sales amount, payment amount)
- List with pagination and date filtering
- Get single entry
- Update entry
- Delete entry
- Reference linking to SR orders or sales orders

**Missing Frontend:**
| Missing UI | What It Should Do |
|------------|-------------------|
| **Ledger entry page** (`/reports/ledger`) | List all ledger entries with date filter, pagination |
| **Ledger entry form** | Create/edit ledger entry with: date, type (order/sales/payment/return), group, customer, amounts, reference |
| **Ledger detail view** | View single ledger entry with linked order details |
| **Delete confirmation** | Delete ledger entry with confirmation |

**Impact:** The Reconciliation Report (`/reports/reconciliation`) compares SR orders vs Khata entries, but the Khata side is always empty because there's no way to create ledger entries. The reconciliation report cannot show meaningful data.

**API functions already exist:** `createLedger`, `getLedgerList`, `getLedger`, `updateLedger`, `deleteLedger` in `srReportsApi.ts`

**Files that need to be created:**
- `src/pages/reports/LedgerManagement.tsx` — Ledger list + create/edit form
- Route addition in `App.tsx`: `<Route path="ledger" element={<LedgerManagement />} />`

---

### 3. SR Order Bulk Approve (1 endpoint, 0 frontend)

**Backend:** `app/api/sr/sr_order.py` → `POST /sales/sr-orders/bulk-approve`  
**What's Built:** Approve multiple SR orders in a single API call.

**Missing Frontend:**
| Missing UI | What It Should Do |
|------------|-------------------|
| **Bulk approve action** | Checkbox selection on SR order list → "Approve Selected" button |
| **Bulk approve confirmation** | Show count of orders to approve, confirm dialog |

**Impact:** Admins must approve SR orders one-by-one. For distributors with 50+ pending SR orders daily, this is a significant productivity bottleneck.

**Files that need to be created:**
- Add `bulkApproveSrOrders` function to `srOrderApi.ts`
- Add checkbox column + bulk action bar to `src/pages/sr-orders/UnconsolidatedSROrders.tsx`

---

## MEDIUM Severity — Partial UI or Missing Actions

### 4. Damage Record Edit (PATCH endpoint, API exists, no edit UI)

**Backend:** `PATCH /sr-reports/damage/{id}`  
**What's Built:** Update an existing damage record (quantity, reason, notes, unit cost).

**Missing:** Edit button in DamageReport table. Currently only Create and Delete are available.

**Impact:** If a damage record is entered incorrectly, users must delete and recreate instead of editing.

**API function exists:** `updateDamage` in `srReportsApi.ts` (unused)

---

### 5. Daily Cost Edit (PATCH endpoint, API exists, no edit UI)

**Backend:** `PATCH /sr-reports/daily-cost/{id}`  
**What's Built:** Update an existing daily cost expense record.

**Missing:** Edit button in CostProfitReport table. Currently only Create and Delete are available.

**Impact:** If a cost entry is wrong, users must delete and recreate.

**API function exists:** `updateDailyCost` in `srReportsApi.ts` (unused)

---

### 6. Cost & Profit Aggregated Report (1 endpoint, 0 frontend API)

**Backend:** `GET /sr-reports/cost-profit`  
**What's Built:** Server-side aggregated cost-profit report joining daily costs, damage costs, and sales revenue by group and date.

**Missing:** Frontend API function and/or usage in CostProfitReport page. Currently the page does client-side aggregation from separate `getDailyCostList` and `getDamageList` calls.

**Impact:** Works functionally but less efficient. Server-side aggregation would be faster for large date ranges.

---

### 7. Claims: Re-evaluate Order Schemes (1 endpoint, 0 frontend)

**Backend:** `POST /claims/orders/re-evaluate`  
**What's Built:** Re-evaluate claim schemes for an existing order when scheme rules change or new schemes activate.

**Missing:** "Re-evaluate Schemes" button on order detail view.

**Impact:** When a new scheme is activated, existing orders don't automatically get the new benefits. Admins have no way to trigger re-evaluation from the UI.

---

### 8. Claims: Reverse Claim Logs (1 endpoint, 0 frontend)

**Backend:** `POST /claims/logs/reverse`  
**What's Built:** Create reversal entries (negative values) for cancelled or returned orders.

**Missing:** "Reverse Claims" action on cancelled/returned orders.

**Impact:** When an order is cancelled, the claim benefits already applied are not reversed, leading to inaccurate claim reports.

---

### 9. Claims: Adjust Claim Logs (1 endpoint, 0 frontend)

**Backend:** `POST /claims/logs/adjust`  
**What's Built:** Create proportional adjustment entries for partial returns.

**Missing:** "Adjust Claims" action on partially returned orders.

**Impact:** Partial returns don't proportionally reduce claim benefits, leading to over-credited claims.

---

### 10. DSR Admin: Deliver/Payment/Load/Unload Actions (4 endpoints, API exists, no admin UI)

**Backend:** `app/api/dsr/dsr_so_assignment.py`
- `POST /{id}/deliver` — Mark assignment as delivered
- `POST /{id}/payment` — Collect payment
- `POST /{id}/load` — Load SO into DSR storage
- `POST /{id}/unload` — Unload SO from DSR storage

**What's Built:** Full delivery workflow actions for DSR SO assignments.

**Missing:** Action buttons on the admin DSR SO Assignments page (`DSRSOAssignments.tsx`). Currently the admin page only has CRUD (create, update, delete). The DSR-facing page (`DSRMyAssignments.tsx`) has load/unload but not deliver/payment.

**Impact:** Admins cannot trigger delivery workflow actions from the admin panel. They must either use the DSR mobile interface or call the API directly.

**API functions exist:** `markDSRSOAssignmentDelivered`, `collectDSRPayment`, `loadSalesOrder`, `unloadSalesOrder` in `dsrApi.ts`

---

### 11. Invoice Statistics Summary (1 endpoint, 0 frontend)

**Backend:** `GET /billing/invoice/statistics/summary`  
**What's Built:** Comprehensive invoice statistics: total count, total amount, average, status breakdown, order type breakdown, date range.

**Missing:** Statistics cards on the Invoices page.

**Impact:** The invoices page shows a plain list without summary metrics (total invoices, paid vs unpaid, average amount, etc.).

---

### 12. Invoice Detail Management (6 endpoints, 0 frontend)

**Backend:** `app/api/billing/invoice_detail.py`
- `GET /billing/invoice-detail/` — List with filtering
- `POST /billing/invoice-detail/` — Create
- `GET /billing/invoice-detail/{id}` — Get single
- `PATCH /billing/invoice-detail/{id}` — Update
- `DELETE /billing/invoice-detail/{id}` — Delete
- `GET /billing/invoice-detail/statistics/summary` — Statistics

**What's Built:** Full CRUD for invoice line items.

**Missing:** No dedicated invoice detail page. Invoice details are shown inline within the invoice view but cannot be managed independently.

**Impact:** Invoice line items cannot be edited, deleted, or filtered independently. Any correction requires modifying the parent invoice.

---

### 13. Expense Statistics Summary (1 endpoint, 0 frontend)

**Backend:** `GET /billing/expense/statistics/summary`  
**What's Built:** Expense statistics: total count, total amount, average, category breakdown, payment method breakdown, date range.

**Missing:** Statistics cards on the Expenses page.

**Impact:** The expenses page shows a plain list without summary metrics.

---

## LOW Severity — Optimization/Debug Endpoints

### 14. SR Price Validation (1 endpoint, API exists, unused)

**Backend:** `GET /sr/product-assignments/{id}/validate-price`  
**What's Built:** Validates if a proposed price override is within allowed min/max bounds.

**Missing:** The price management pages (`AdminSRPriceManagement.tsx`, `SRPriceManagement.tsx`) don't call this validation before saving.

**Impact:** Users can set prices outside allowed bounds without warning.

**API function exists:** `validatePriceOverride` in `srProductAssignmentPriceApi.ts` (unused)

---

### 15. SR Order Bulk Details (1 endpoint, 0 frontend)

**Backend:** `POST /sales/sr-orders/bulk-details`  
**What's Built:** Get full details for multiple SR orders by IDs in one request.

**Missing:** No frontend usage. Individual order detail fetch works fine.

**Impact:** Performance optimization only. No functional gap.

---

### 16. Single Damage Record View (1 endpoint, API exists, unused)

**Backend:** `GET /sr-reports/damage/{id}`  
**What's Built:** Fetch a single damage record by ID.

**Missing:** No detail view for individual damage records.

**Impact:** Low — the list view shows all needed information.

**API function exists:** `getDamage` in `srReportsApi.ts` (unused)

---

### 17. Single Daily Cost View (1 endpoint, API exists, unused)

**Backend:** `GET /sr-reports/daily-cost/{id}`  
**What's Built:** Fetch a single daily cost record by ID.

**Missing:** No detail view for individual cost records.

**Impact:** Low — the list view shows all needed information.

**API function exists:** `getDailyCost` in `srReportsApi.ts` (unused)

---

### 18. Elasticsearch Health Check (1 endpoint, 0 frontend)

**Backend:** `GET /api/admin/elasticsearch/health`  
**What's Built:** ES cluster status, node count, shard info, per-index document counts and sizes.

**Missing:** No dedicated health check page. The `ElasticsearchSyncStatus.tsx` page shows sync status but not cluster health.

**Impact:** Low — sync-status page provides related operational info.

---

### 19. Undelivery Report (orphaned endpoint, alternate exists)

**Backend:** `GET /sr-reports/undelivery`  
**What's Built:** Date-wise undelivery breakdown by product group.

**Status:** Functionality exists via alternate endpoint `/reports/sr-program/undelivery` used by `SRProgramWorkflow.tsx`. This `/sr-reports/undelivery` endpoint is orphaned.

**Impact:** None — feature works via alternate path.

---

### 20. DO Cash Report (orphaned endpoint, alternate exists)

**Backend:** `GET /sr-reports/do-cash`  
**What's Built:** Date-wise DO cash breakdown by product group.

**Status:** Functionality exists via alternate endpoint `/reports/sr-program/do-cash` used by `SRProgramWorkflow.tsx`. This `/sr-reports/do-cash` endpoint is orphaned.

**Impact:** None — feature works via alternate path.

---

## Complete Gap Summary Table

| # | Feature | Backend Endpoints | Frontend API? | Frontend UI? | Severity | Effort Estimate |
|---|---------|-------------------|---------------|--------------|----------|-----------------|
| 1 | **Product Image Management** | 20 | ❌ No | ❌ No | **HIGH** | 3-4 days |
| 2 | **Sales Ledger (Khata) CRUD** | 5 | ✅ Yes | ❌ No | **HIGH** | 1-2 days |
| 3 | **SR Order Bulk Approve** | 1 | ❌ No | ❌ No | **HIGH** | 0.5 day |
| 4 | **Damage Record Edit** | 1 | ✅ Yes | ❌ No | MEDIUM | 0.5 day |
| 5 | **Daily Cost Edit** | 1 | ✅ Yes | ❌ No | MEDIUM | 0.5 day |
| 6 | **Cost & Profit Aggregated Report** | 1 | ❌ No | ⚠️ Partial | MEDIUM | 0.5 day |
| 7 | **Claims: Re-evaluate Order** | 1 | ❌ No | ❌ No | MEDIUM | 0.5 day |
| 8 | **Claims: Reverse Logs** | 1 | ❌ No | ❌ No | MEDIUM | 0.5 day |
| 9 | **Claims: Adjust Logs** | 1 | ❌ No | ❌ No | MEDIUM | 0.5 day |
| 10 | **DSR Admin: Deliver/Pay/Load/Unload** | 4 | ✅ Yes | ⚠️ Partial | MEDIUM | 1 day |
| 11 | **Invoice Statistics** | 1 | ❌ No | ❌ No | MEDIUM | 0.5 day |
| 12 | **Invoice Detail Management** | 6 | ❌ No | ❌ No | MEDIUM | 1-2 days |
| 13 | **Expense Statistics** | 1 | ❌ No | ❌ No | MEDIUM | 0.5 day |
| 14 | **SR Price Validation** | 1 | ✅ Yes | ❌ Unused | LOW | 0.5 day |
| 15 | **SR Order Bulk Details** | 1 | ❌ No | ❌ No | LOW | 0.5 day |
| 16 | **Single Damage View** | 1 | ✅ Yes | ❌ Unused | LOW | 0.25 day |
| 17 | **Single Daily Cost View** | 1 | ✅ Yes | ❌ Unused | LOW | 0.25 day |
| 18 | **ES Health Check** | 1 | ❌ No | ❌ No | LOW | 0.5 day |
| 19 | **Undelivery (orphaned)** | 1 | ❌ No | ✅ Alt exists | LOW | 0 |
| 20 | **DO Cash (orphaned)** | 1 | ❌ No | ✅ Alt exists | LOW | 0 |

---

## Orphaned Frontend API Functions (exist but unused)

These API functions are defined in frontend code but not called by any page or component:

| Function | File | Backend Endpoint | Intended Use |
|----------|------|-------------------|--------------|
| `updateDamage` | `srReportsApi.ts` | `PATCH /sr-reports/damage/{id}` | Edit damage record |
| `getDamage` | `srReportsApi.ts` | `GET /sr-reports/damage/{id}` | View single damage |
| `updateDailyCost` | `srReportsApi.ts` | `PATCH /sr-reports/daily-cost/{id}` | Edit daily cost |
| `getDailyCost` | `srReportsApi.ts` | `GET /sr-reports/daily-cost/{id}` | View single cost |
| `createLedger` | `srReportsApi.ts` | `POST /sr-reports/ledger` | Create ledger entry |
| `getLedgerList` | `srReportsApi.ts` | `GET /sr-reports/ledger` | List ledger entries |
| `getLedger` | `srReportsApi.ts` | `GET /sr-reports/ledger/{id}` | View single ledger |
| `updateLedger` | `srReportsApi.ts` | `PATCH /sr-reports/ledger/{id}` | Edit ledger entry |
| `deleteLedger` | `srReportsApi.ts` | `DELETE /sr-reports/ledger/{id}` | Delete ledger entry |
| `validatePriceOverride` | `srProductAssignmentPriceApi.ts` | `GET /sr/product-assignments/{id}/validate-price` | Validate price bounds |

---

## Recommended Priority Order for Implementation

### Phase 1: Critical Gaps (HIGH — 4-6 days)

1. **Product Image Management** — Largest gap, affects product catalog UX
2. **Sales Ledger (Khata) CRUD** — Enables Reconciliation Report to work properly
3. **SR Order Bulk Approve** — High productivity impact for daily operations

### Phase 2: Important Gaps (MEDIUM — 5-6 days)

4. **DSR Admin: Deliver/Pay/Load/Unload** — Complete admin workflow
5. **Damage Record Edit** — Data correction capability
6. **Daily Cost Edit** — Data correction capability
7. **Claims: Re-evaluate/Reverse/Adjust** — Claim accounting accuracy
8. **Invoice Statistics** — Dashboard enhancement
9. **Invoice Detail Management** — Line item management
10. **Expense Statistics** — Dashboard enhancement
11. **Cost & Profit Aggregated Report** — Performance optimization

### Phase 3: Nice-to-Have (LOW — 2-3 days)

12. **SR Price Validation** — Data integrity
13. **ES Health Check** — Operational visibility
14. **Single record views** — Detail drill-down

---

*Analysis completed: 2026-04-03*  
*Total missing UI features: 20 (3 HIGH, 10 MEDIUM, 7 LOW)*  
*Estimated total effort: ~12-15 days for complete coverage*
