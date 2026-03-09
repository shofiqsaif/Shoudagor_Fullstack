# Frontend Plan: Stock to Batch Consolidation Feature

## Objective
Create frontend pages to run, preview, and view the stock-to-batch consolidation feature.

---

## Overview

The feature will be added as a new page under the existing `/inventory/` route group, similar to the existing `BatchBackfill` page.

**Route:** `/inventory/stock-to-batch`

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/lib/api/batchApi.ts` | Add API functions for preview and execute |
| `src/lib/schema/batch.ts` | Add TypeScript interfaces for response types |
| `src/pages/inventory/StockToBatch.tsx` | **Create** - Main page component |
| `src/App.tsx` | Add route registration |

---

## API Functions (batchApi.ts)

Add two new functions:

```typescript
// Preview endpoint (GET)
export const previewStockToBatch = async (): Promise<{
    to_create: number;
    to_update: number;
    to_skip: number;
    total_products: number;
    details: Array<{
        product_id: number;
        variant_id: number | null;
        location_id: number;
        total_qty: number;
        unit_cost: number;
        action: "create" | "update";
        existing_batch_id: number | null;
    }>;
    warnings: string[];
}> => {
    return apiRequest(api, `/inventory/reconciliation/stock-to-batch`);
};

// Execute endpoint (POST)
export const executeStockToBatch = async (userId?: number): Promise<{
    to_create: number;
    to_update: number;
    to_skip: number;
    batches_created: number;
    movements_created: number;
    errors: string[];
    warnings: string[];
}> => {
    return apiRequest(api, `/inventory/reconciliation/stock-to-batch`, {
        method: "POST",
        body: JSON.stringify({ user_id: userId }),
    });
};
```

---

## TypeScript Interfaces (batch.ts)

Add interfaces for the new response types:

```typescript
export interface StockToBatchPreviewDetail {
    product_id: number;
    variant_id: number | null;
    location_id: number;
    total_qty: number;
    unit_cost: number;
    action: "create" | "update";
    existing_batch_id: number | null;
}

export interface StockToBatchPreviewResponse {
    to_create: number;
    to_update: number;
    to_skip: number;
    total_products: number;
    details: StockToBatchPreviewDetail[];
    warnings: string[];
}

export interface StockToBatchExecuteResponse {
    to_create: number;
    to_update: number;
    to_skip: number;
    batches_created: number;
    movements_created: number;
    errors: string[];
    warnings: string[];
}
```

---

## Page Component (StockToBatch.tsx)

### Structure

The page will follow the existing `BatchBackfill.tsx` pattern with:

1. **Header Section**
   - Title: "Stock to Batch Consolidation"
   - Description: "Consolidate inventory_stock into single batches per product-variant-location"

2. **Configuration Card** (optional, since it's full backfill)
   - Show current settings/info
   - DRY RUN toggle (default: true)

3. **Preview Results Card** (when preview is run)
   - Summary stats: to_create, to_update, total_products
   - Details table showing each product-variant-location combination
   - Warnings list

4. **Execute Button**
   - Primary action to run the consolidation
   - Show confirmation dialog before executing (since it's destructive)
   - Disabled in DRY RUN mode

5. **Execution Results Card** (when executed)
   - Summary: batches_created, movements_created
   - Errors list (if any)
   - Warnings list

6. **Info Card**
   - Explanation of the feature
   - What it does: consolidates all inventory_stock to single batches
   - Price source: purchase_price from product_price table
   - Warning about destructive nature

### Key UI Components

| Component | Purpose |
|-----------|---------|
| `Card` | Main container for each section |
| `Button` | Execute/Preview actions |
| `Switch` | DRY RUN toggle |
| `Table` | Preview details display |
| `Badge` | Status indicators (create/update) |
| `AlertTriangle` | Warnings and cautions |
| `Dialog` | Confirmation before execute |

### State Management

```typescript
const [isDryRun, setIsDryRun] = useState(true);
const [showExecuteConfirm, setShowExecuteConfirm] = useState(false);

// Preview mutation
const previewMutation = useMutation({
    mutationFn: previewStockToBatch,
    onSuccess: (data) => { ... },
    onError: (error) => { ... },
});

// Execute mutation
const executeMutation = useMutation({
    mutationFn: executeStockToBatch,
    onSuccess: (data) => { ... },
    onError: (error) => { ... },
});
```

---

## Route Registration (App.tsx)

Add to the AdminRoute children section under "Batch Inventory":

```typescript
// Batch Inventory
{ path: "/inventory/batch-drilldown", element: <BatchDrillDown /> },
{ path: "/inventory/movement-ledger", element: <MovementLedger /> },
{ path: "/inventory/reconciliation", element: <BatchReconciliation /> },
{ path: "/inventory/backfill", element: <BatchBackfill /> },
{ path: "/inventory/stock-to-batch", element: <StockToBatch /> },  // NEW
{ path: "/inventory/allocations", element: <SalesOrderBatchAllocations /> },
```

---

## UI Mockup

```
┌─────────────────────────────────────────────────────────────────┐
│  Stock to Batch Consolidation                                  │
│  Consolidate inventory_stock into single batches               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ DRY RUN Mode                    [Toggle Switch]       │    │
│  │                                                         │    │
│  │  ● Preview   ○ Execute                                 │    │
│  │                                                         │    │
│  │  [Run Preview]                    [Execute Consolidation]│
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Preview Results                           (DRY RUN)     │    │
│  │                                                         │    │
│  │  Summary:                                               │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐              │    │
│  │  │ 15       │ │ 5        │ │ 20       │              │    │
│  │  │ To Create│ │ To Update│ │ Total    │              │    │
│  │  └──────────┘ └──────────┘ └──────────┘              │    │
│  │                                                         │    │
│  │  Details Table:                                         │    │
│  │  ┌───────────┬──────────┬──────────┬────────┬──────┐  │    │
│  │  │ Product   │ Variant  │ Location │ Qty    │Action│  │    │
│  │  ├───────────┼──────────┼──────────┼────────┼──────┤  │    │
│  │  │ 123      │ null     │ 5        │ 1000   │Create│  │    │
│  │  │ 124      │ 456      │ 5        │ 500    │Update│  │    │
│  │  └───────────┴──────────┴──────────┴────────┴──────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ⚠ About Stock to Batch                                 │    │
│  │ This process consolidates ALL inventory_stock records   │    │
│  │ into single synthetic batches per product-variant-      │    │
│  │ location. Uses purchase_price from product_price table.│    │
│  │ WARNING: This will replace existing batches!           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

1. **Add API functions** to `batchApi.ts`
2. **Add TypeScript types** to `batch.ts` schema
3. **Create page component** `StockToBatch.tsx`
4. **Register route** in `App.tsx`
5. **Test**: Run preview and execute to verify functionality

---

## Key Differences from Existing Backfill

| Aspect | Existing BatchBackfill | New StockToBatch |
|--------|----------------------|------------------|
| **Source Data** | Historical PO deliveries | Current inventory_stock |
| **Price Source** | PO unit_cost | product_price.purchase_price |
| **Scope** | Configurable chunk size | Full backfill (all records) |
| **Behavior** | Creates new batches | Replaces existing batches |
| **Preview** | Shows reconciliation | Shows create/update actions |
