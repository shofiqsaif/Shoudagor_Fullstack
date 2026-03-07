# Batch Inventory Frontend Implementation Plan

## Overview

This plan outlines the implementation of Batch Inventory pages in the Shoudagor ERP frontend, including navigation, routes, and a new Reconciliation page.

---

## Current State

### Existing Routes (Already in App.tsx)
| Page | Route | Status |
|------|-------|--------|
| Batch Drilldown | `/inventory/batch-drilldown` | ✅ Route exists |
| Movement Ledger | `/inventory/movement-ledger` | ✅ Route exists |
| Stock by Batch | `/reports/inventory/stock-by-batch` | ✅ Route exists |
| Inventory Aging Batch | `/reports/inventory/inventory-aging-batch` | ✅ Route exists |
| COGS by Period | `/reports/inventory/cogs-by-period` | ✅ Route exists |
| Margin Analysis | `/reports/inventory/margin-analysis` | ✅ Route exists |
| Batch P&L | `/reports/inventory/batch-pnl` | ✅ Route exists |

### Missing Items
- ❌ No sidebar navigation entries for batch pages
- ❌ No Reconciliation page (backend API exists)
- ❌ No Backfill page (backend API exists)

---

## Implementation Plan

### Phase 1: Update Navigation (navigation.ts)

Create a new "Batch Inventory" section in the sidebar navigation.

**File:** `shoudagor_FE/src/data/navigation.ts`

```typescript
// Add new section after "Inventory" section
{
  title: "Batch Inventory",
  url: "#",
  icon: Package,  // Need to import Package from lucide-react
  items: [
    {
      title: "Batch Drilldown",
      url: "/inventory/batch-drilldown",
    },
    {
      title: "Movement Ledger",
      url: "/inventory/movement-ledger",
    },
    {
      title: "Reconciliation",
      url: "/inventory/reconciliation",
    },
    {
      title: "Backfill",
      url: "/inventory/backfill",
    },
  ],
},
```

### Phase 2: Add Routes to App.tsx

**File:** `shoudagor_FE/src/App.tsx`

Add imports and routes:

```typescript
// Add imports
import BatchReconciliation from "./pages/inventory/BatchReconciliation";
import BatchBackfill from "./pages/inventory/BatchBackfill";

// Add routes (around line 177-180)
{ path: "/inventory/batch-drilldown", element: <BatchDrillDown /> },
{ path: "/inventory/movement-ledger", element: <MovementLedger /> },
{ path: "/inventory/reconciliation", element: <BatchReconciliation /> },
{ path: "/inventory/backfill", element: <BatchBackfill /> },
```

### Phase 3: Create BatchReconciliation Page

**File:** `shoudagor_FE/src/pages/inventory/BatchReconciliation.tsx`

Features:
- Display reconciliation overview (total batches, mismatches, etc.)
- List products with batch vs stock quantity mismatches
- Filter by product, location
- "Reconcile Product" action button
- Link to run backfill if needed

**API Integration:**
- `GET /api/company/inventory/reconciliation` - Main reconciliation report
- `GET /api/company/inventory/reconciliation/product/{product_id}` - Product-specific reconciliation

### Phase 4: Create BatchBackfill Page

**File:** `shoudagor_FE/src/pages/inventory/BatchBackfill.tsx`

Features:
- DRY RUN mode (default) - Preview changes
- Execute mode - Commit changes
- Chunk size configuration
- Progress indicator for large datasets
- Results summary (batches created, errors, etc.)

**API Integration:**
- `POST /api/company/inventory/reconciliation/backfill?dry_run=true`
- `POST /api/company/inventory/reconciliation/backfill?dry_run=false`
- `POST /api/company/inventory/reconciliation/backfill-sales`

### Phase 5: Add Batch API Functions

**File:** `shoudagor_FE/src/lib/api/batchApi.ts`

Add new functions:

```typescript
// Reconciliation
export const getReconciliationReport = async (): Promise<any> => {
    return apiRequest(api, "/api/company/inventory/reconciliation");
};

export const getReconciliationByProduct = async (productId: number, variantId?: number): Promise<any> => {
    const params = variantId ? `?variant_id=${variantId}` : "";
    return apiRequest(api, `/api/company/inventory/reconciliation/product/${productId}${params}`);
};

// Backfill
export const runBackfill = async (dryRun: boolean = true, chunkSize: number = 500): Promise<any> => {
    return apiRequest(api, `/api/company/inventory/reconciliation/backfill?dry_run=${dryRun}&chunk_size=${chunkSize}`, {
        method: "POST",
    });
};

export const runSalesBackfill = async (dryRun: boolean = true, chunkSize: number = 500): Promise<any> => {
    return apiRequest(api, `/api/company/inventory/reconciliation/backfill-sales?dry_run=${dryRun}&chunk_size=${chunkSize}`, {
        method: "POST",
    });
};
```

### Phase 6: Run Typecheck

Run `npm run typecheck` to verify no TypeScript errors.

---

## Summary of Changes

### Files to Modify
1. `shoudagor_FE/src/data/navigation.ts` - Add Batch Inventory section
2. `shoudagor_FE/src/App.tsx` - Add routes for Reconciliation and Backfill
3. `shoudagor_FE/src/lib/api/batchApi.ts` - Add API functions

### Files to Create
1. `shoudagor_FE/src/pages/inventory/BatchReconciliation.tsx` - Reconciliation page
2. `shoudagor_FE/src/pages/inventory/BatchBackfill.tsx` - Backfill page

### Icons
Add `Package` icon to the lucide-react imports in navigation.ts (or use existing icon like `Box` or `Layers`)

---

## Execution Order

1. Update navigation.ts (Phase 1)
2. Add API functions to batchApi.ts (Phase 5)
3. Create BatchReconciliation.tsx (Phase 3)
4. Create BatchBackfill.tsx (Phase 4)
5. Update App.tsx with imports and routes (Phase 2)
6. Run typecheck (Phase 6)

---

## Notes

- The existing batch pages (BatchDrillDown, MovementLedger) already work - they just need to be added to navigation
- Both new pages should follow the existing UI patterns (shadcn/ui, TanStack Query)
- Consider adding loading states and error handling for API calls
- The Backfill page should clearly warn users about DRY RUN vs EXECUTE mode
