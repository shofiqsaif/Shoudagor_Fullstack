# Phase 2 Implementation Plan: Fix Each Workflow

## Overview

Phase 1 established the centralized `InventorySyncService` (`app/services/inventory/inventory_sync_service.py`) that owns all stock mutations atomically. Phase 2 focuses on **refactoring existing workflow services** to use this centralized service, eliminating inconsistencies and ensuring batch/inventory_stock synchronization.

**Key Principle**: When batch tracking is enabled, ALL stock mutations must go through `InventorySyncService.apply_stock_mutation()`. Any deviation creates the split-authority problem documented in the deep dive.

---

## Summary of Issues to Fix

| # | Workflow | Current Issue | Phase 2 Action |
|---|----------|---------------|----------------|
| 1 | Purchase Receipts | Partial deliveries block batch creation after first receipt | Allow multiple batches per PO detail |
| 2 | Sales Deliveries | Fallback to legacy stock on batch failure | Fail completely if batch tracking enabled |
| 3 | Sales Returns | DSR/non-DSR inconsistent allocation handling | Use centralized return method |
| 4 | Inventory Adjustments | Uses `sales_order_detail_id=0`, incorrect rollback | Dedicated adjustment path with proper rollback |
| 5 | Stock Transfers | Double-decrement, `sales_order_detail_id=0` | Proper transfer method without double-decrement |
| 6 | DSR Load/Unload | Rewrites SALES_DELIVERY movements | True transfer movements |
| 7 | DSR Stock Transfers | No batch updates | Add batch sync for general DSR transfers |
| 8 | Manual Stock CRUD | Bypasses batch logic | Block or route through adjustment |
| 9 | Variant Nested Updates | Deletes/recreates without batch sync | Delta-based sync |
| 10 | Reporting | Double-counts when batch enabled | Use batch as single source |

---

## Detailed Implementation Plan

### 1. Purchase Receipts (Partial Deliveries)

**Current Issues:**
- `create_batch_for_purchase_receipt` blocks duplicate `purchase_order_detail_id`
- If partial deliveries exist, batch creation fails after first receipt
- Stock increases without batch update on failure

**Implementation Steps:**

1.1 Modify `BatchAllocationService.create_batch_for_purchase_receipt` to allow multiple batches per PO detail:
- Change uniqueness constraint from `purchase_order_detail_id` alone to `(purchase_order_detail_id, delivery_detail_id)` or use `delivery_detail_id` as primary key
- If same unit cost exists, append quantity to existing batch

1.2 Update `ProductOrderDeliveryDetailService.create_delivery_detail` to use `InventorySyncService.apply_stock_mutation()`:
- Pass `ref_id` as delivery detail ID (not PO detail ID)
- Remove direct batch creation code

**Edge Cases:**
1. **Partial delivery with same unit cost**: Append to existing batch if unit_cost matches
2. **Partial delivery with different unit cost**: Create new batch
3. **Free quantity handling**: Include free qty in batch creation
4. **Zero-cost receipts**: Allow zero unit_cost with proper tracking

**Error Handling:**
- If batch creation fails: Do NOT update inventory_stock
- Raise exception with clear message
- Log failure for audit trail

---

### 2. Sales Deliveries

**Current Issues:**
- Falls back to legacy stock update if batch allocation fails
- Swallows errors and continues

**Implementation Steps:**

2.1 Modify `SalesOrderDeliveryDetailService._update_inventory_stock`:
- Check `is_batch_tracking_enabled()` first
- If enabled: Use `InventorySyncService.apply_stock_mutation()` with `StockSource.SALES_DELIVERY`
- If batch operation fails: Raise HTTPException (NO FALLBACK)
- If disabled: Use legacy stock update

2.2 Key code changes in `sales_order_delivery_detail_service.py`:
- Import `InventorySyncService`, `StockChangeContext`, `StockSource`
- Replace direct stock update with sync service call
- Remove fallback logic

**Edge Cases:**
1. **Zero quantity delivery**: Skip batch allocation
2. **Negative stock after delivery**: Should never happen if allocation succeeds
3. **Concurrent deliveries**: Use row-level locking in batch allocation
4. **Partial allocation**: Should fail if full quantity cannot be allocated

**Error Handling:**
- If batch allocation fails: Raise HTTPException (no fallback)
- Log detailed error with sales_order_detail_id
- Include available stock information in error message

---

### 3. Sales Returns

**Current Issues:**
- DSR and non-DSR returns handle allocations differently
- `SalesOrderBatchAllocation` may be stale in DSR workflows

**Implementation Steps:**

3.1 Enhance `_handle_sales_return` in `InventorySyncService`:
- Add parameter to detect DSR return path
- Use separate handler for DSR returns
- Ensure both paths update inventory_stock

3.2 Add `_handle_dsr_return` method:
- Query `DSRBatchAllocation` by assignment_id
- Reverse allocations and create RETURN_IN movements
- Mark allocations as deleted

3.3 Update `SalesOrderService.process_return` to use sync service:
- Pass `dsr_assignment_id` when processing DSR returns

**Edge Cases:**
1. **Return quantity > delivery quantity**: Validate against shipped_quantity
2. **Return to different location**: Support return to warehouse vs DSR storage
3. **Partial return**: Handle partial allocation reversal
4. **Expired batches**: Handle return to expired batches gracefully

**Error Handling:**
- If no allocation found: Raise error with clear message
- Log return details for audit

---

### 4. Inventory Adjustments

**Current Issues:**
- Uses `sales_order_detail_id=0` for negative adjustments
- Creates `SalesOrderBatchAllocation` for non-sales operations
- Adjustment update/delete only rolls back stock, not batch
- Wrong movement `ref_type` (SALES_DELIVERY)

**Implementation Steps:**

4.1 Create dedicated adjustment handler in `InventorySyncService`:
- Add `StockSource.ADJUSTMENT` handler that does NOT use `allocate()` method
- Create movements with `ref_type = ADJUSTMENT`
- Do NOT create `SalesOrderBatchAllocation` records

4.2 Modify `InventoryAdjustmentService`:
- Use `InventorySyncService.apply_stock_mutation()` instead of direct batch operations
- For positive adjustments: Create adjustment batch
- For negative adjustments: Consume from batches using FIFO but without allocation linkage

4.3 Fix rollback logic:
- Store movement IDs in adjustment detail
- On update/delete: Reverse movements by creating counter-movements
- Update batch qty_on_hand accordingly

**Edge Cases:**
1. **Adjustment to zero**: Allow reducing to zero but not below
2. **Negative adjustment on zero stock**: Should fail with insufficient stock error
3. **Concurrent adjustments**: Use row locking
4. **Multiple adjustments**: Each adjustment creates separate movement

**Error Handling:**
- If batch decrement fails: Rollback entire adjustment
- Log adjustment ID and details

---

### 5. Stock Transfers (Warehouse)

**Current Issues:**
- Double-decrement of batch qty: calls `allocate()` AND `create_transfer_movements()`
- Uses `sales_order_detail_id=0` placeholder
- Falls back to legacy stock on batch failure

**Implementation Steps:**

5.1 Fix `_handle_transfer` in `InventorySyncService`:
- Remove double-decrement: allocate() already decrements, remove separate transfer movement creation
- OR: Create proper transfer without calling allocate()

5.2 Recommended approach - proper two-step transfer:
- Step 1: Allocate from source batches (creates OUT movements)
- Step 2: Create new batch at destination (NOT using purchase receipt logic)
- Do NOT call both allocate() AND create_transfer_movements()

5.3 Update `StockTransferService.create_stock_transfer`:
- Use `InventorySyncService.apply_stock_mutation()` with `StockSource.TRANSFER`
- Remove direct batch operations
- Remove fallback to legacy mode

**Edge Cases:**
1. **Transfer to same location**: Reject with error
2. **Insufficient source stock**: Fail before any changes
3. **Partial transfer**: Handle partial allocation
4. **Transfer with different unit costs**: Track average cost

**Error Handling:**
- If source allocation fails: Rollback entire transfer
- If destination creation fails: Reverse source allocation

---

### 6. DSR Load/Unload

**Current Issues:**
- DSR load rewrites existing SALES_DELIVERY movements to DSR_TRANSFER
- Pollutes `SalesOrderBatchAllocation` semantics
- DSR allocations may include already-shipped quantities

**Implementation Steps:**

6.1 Refactor DSR load to be a true transfer:
- Do NOT modify existing sales delivery movements
- Create NEW DSR-specific transfer movements
- Use `DSRBatchAllocation` for tracking (already exists)

6.2 Fix `_handle_dsr_load` in `InventorySyncService`:
- Keep existing allocation for source batches (creates OUT movements)
- Add DSRBatchAllocation records
- Create DSR transfer movements (not rewriting sales movements)

6.3 Fix `_handle_dsr_unload`:
- Reverse DSR transfer movements (RETURN_IN)
- Reverse DSRBatchAllocation
- Do NOT modify SalesOrderBatchAllocation

6.4 Update `DSRSOAssignmentService`:
- Remove code that rewrites InventoryMovement ref_type
- Use sync service for load/unload operations

**Edge Cases:**
1. **Load after partial delivery**: Only allocate unshipped quantity
2. **Unload without prior load**: Reject with error
3. **Partial unload**: Handle partial quantity reversal
4. **DSR inventory vs warehouse**: Track separately

**Error Handling:**
- If allocation fails: Fail the load operation
- If unload finds no allocations: Raise error

---

### 7. DSR Stock Transfers (General)

**Current Issues:**
- Updates `inventory_stock` / `dsr_inventory_stock` only
- No batch movement or batch qty updates

**Implementation Steps:**

7.1 Update `DSRStockTransferService`:
- Use `InventorySyncService.apply_stock_mutation()` for batch-enabled companies
- DSR to warehouse: Use `DSR_UNLOAD` source
- Warehouse to DSR: Use `DSR_LOAD` source
- General DSR to DSR: Use `TRANSFER` with both locations

7.2 Add batch tracking support:
- Decrement warehouse batch qty on load to DSR
- Increment warehouse batch qty on unload from DSR
- Update `DSRBatchAllocation` appropriately

**Edge Cases:**
1. **DSR to DSR transfer**: Proper bidirectional handling
2. **Insufficient DSR stock**: Validate before transfer
3. **Concurrent transfers**: Use row locking

---

### 8. Manual Inventory Stock CRUD

**Current Issues:**
- `warehouse.py` CRUD operations bypass batch logic entirely
- Creates immediate invariant violation when batch tracking enabled

**Implementation Steps:**

8.1 Add guards in `InventoryStockRepository`:
- Check `is_batch_tracking_enabled()` before any CRUD
- If enabled: Block direct operations with `BatchModeViolationError`

8.2 Alternative: Route through sync service:
- If user tries to create/update stock directly:
  - In batch mode: Suggest using adjustment form instead
  - Or: Auto-convert to synthetic adjustment

8.3 Update API layer:
- Add validation in `warehouse.py` service methods
- Return clear error message explaining why operation is blocked

**Edge Cases:**
1. **Initial setup**: Allow stock creation before batch migration
2. **Emergency stock correction**: Provide adjustment workflow
3. **Bulk imports**: Route through import with batch creation

**Error Handling:**
- Return 403 Forbidden with clear message
- Include suggestion to use adjustment workflow

---

### 9. Variant Nested Stock Updates

**Current Issues:**
- Deletes existing `inventory_stock` and recreates new entries
- No batch synchronization
- Guaranteed mismatch when batch tracking enabled

**Implementation Steps:**

9.1 Modify `ProductVariantService`:
- Calculate delta between old and new stock values
- If batch tracking enabled:
  - Use `InventorySyncService.apply_stock_mutation()` with `StockSource.ADJUSTMENT`
  - Create synthetic adjustments for the delta
- If batch tracking disabled: Keep existing behavior

9.2 Handle different update scenarios:
- **Stock increase**: Create positive adjustment batch
- **Stock decrease**: Create negative adjustment (consume from batches)
- **Stock delete**: Reduce to zero via adjustment

**Edge Cases:**
1. **Multiple location updates**: Handle each location separately
2. **Variant without existing batch**: Create synthetic batch
3. **Concurrent updates**: Use optimistic locking

---

### 10. Reporting Logic

**Current Issues:**
- Reports compute stock as `inventory_stock + batch_qty` when batch enabled
- This doubles the stock value

**Implementation Steps:**

10.1 Update `ProductVariantRepository`:
- When batch tracking enabled: Use batch totals ONLY
- Remove the addition of inventory_stock and batch_qty
- Keep side-by-side display option for debugging

10.2 Create helper method:
```python
def get_effective_stock(company_id, product_id, variant_id, location_id):
    sync_service = InventorySyncService(db)
    if sync_service.is_batch_tracking_enabled(company_id):
        return sync_service.get_batch_total_qty(...)
    else:
        return sync_service.get_inventory_stock_qty(...)
```

10.3 Update all report queries:
- Replace direct inventory_stock queries with helper method
- Ensure consistent stock calculation across all reports

**Edge Cases:**
1. **No batches but inventory_stock exists**: Show warning, use inventory_stock
2. **Mismatched totals**: Flag in reconciliation report
3. **Historical reports**: Use batch totals at point in time

---

## Implementation Priority

| Priority | Workflow | Complexity | Risk |
|----------|----------|------------|------|
| 1 | Sales Deliveries | Medium | High (affects core sales) |
| 2 | Purchase Receipts | Medium | High (affects core procurement) |
| 3 | Stock Transfers | Medium | Medium |
| 4 | Inventory Adjustments | Medium | Medium |
| 5 | DSR Load/Unload | High | High (complex DSR flow) |
| 6 | Sales Returns | Medium | Medium |
| 7 | DSR Stock Transfers | Medium | Low |
| 8 | Manual Stock CRUD | Low | Low |
| 9 | Variant Nested Updates | Low | Medium |
| 10 | Reporting | Low | Low |

---

## Testing Plan

### Integration Tests Required

| Test | Workflow | Expected Behavior |
|------|----------|-------------------|
| test_po_partial_delivery | Purchase Receipt | Multiple batches per PO detail |
| test_po_delivery_batch_failure | Purchase Receipt | Stock NOT updated if batch fails |
| test_sales_delivery_batch_enabled | Sales Delivery | Batch allocated, stock decremented |
| test_sales_delivery_no_fallback | Sales Delivery | Fails completely if batch fails |
| test_sales_return_dsr | Sales Returns | DSR allocation reversed correctly |
| test_positive_adjustment | Adjustment | Batch created, stock increased |
| test_negative_adjustment | Adjustment | Batch decremented, stock decreased |
| test_adjustment_rollback | Adjustment | Update/delete reverses batch |
| test_stock_transfer_no_double | Stock Transfer | Source batch decremented once |
| test_dsr_load_no_rewrite | DSR Load | Sales movements not modified |
| test_dsr_unload_reversal | DSR Unload | DSR allocation reversed |
| test_manual_stock_blocked | Manual CRUD | Blocked in batch mode |
| test_variant_update_sync | Variant Update | Batch and stock synced |
| test_report_no_double_count | Reporting | Single source used |

---

## Error Handling Summary

| Scenario | Current Behavior | Phase 2 Behavior |
|----------|------------------|------------------|
| Batch allocation fails | Fallback to legacy stock | Raise error, rollback |
| Transfer double-decrement | Leaves stock/batch wrong | Single decrement |
| Partial PO delivery | Blocks batch creation | Allow multiple batches |
| DSR load rewrite | Modifies sales movements | Keep separate movements |
| Manual stock CRUD | Allows bypass | Block or route to adjustment |
| Report calculation | Double counts | Single source |

---

## Files to Modify

```
app/
├── services/
│   ├── inventory/
│   │   └── inventory_sync_service.py     # ADD: handlers, fix existing
│   ├── procurement/
│   │   └── product_order_delivery_detail_service.py  # USE sync service
│   ├── sales/
│   │   ├── sales_order_delivery_detail_service.py    # USE sync service
│   │   └── sales_order_service.py        # USE sync service for returns
│   ├── transaction/
│   │   └── inventory_adjustment.py      # USE sync service, fix rollback
│   ├── warehouse/
│   │   ├── stock_transfer.py             # USE sync service, fix double-decrement
│   │   ├── warehouse.py                  # ADD guards for batch mode
│   │   └── dsr_stock_transfer.py         # ADD batch sync
│   ├── dsr/
│   │   └── dsr_so_assignment_service.py  # USE sync service, fix rewrite
│   └── inventory/
│       └── product_variant_service.py     # USE sync service for deltas
│
├── repositories/
│   ├── inventory/
│   │   └── product_variant.py            # FIX report calculation
│   └── warehouse/
│       └── inventory_stock.py             # ADD batch mode guards
│
└── api/
    └── inventory/
        └── batch.py                       # ADD additional endpoints if needed
```

---

## Rollback Strategy

Each workflow change should be implemented with:
1. **Feature flag**: Allow toggling between old and new behavior
2. **Shadow mode**: Log new behavior without executing
3. **Gradual rollout**: Deploy to one company, verify, then expand
4. **Quick rollback**: Ability to revert to old code path

Example feature flag structure:
```python
USE_INVENTORY_SYNC_SERVICE = os.getenv("USE_INVENTORY_SYNC_SERVICE", "false").lower() == "true"
```

---

## Success Criteria

1. All 10 workflows use `InventorySyncService` when batch tracking enabled
2. No fallback to legacy stock updates in batch mode
3. Batch and inventory_stock remain consistent after any operation
4. All integration tests pass
5. No double-counting in reports
6. Proper error messages guide users to correct workflow
7. DSR load/unload does not modify sales delivery movements
8. Stock transfers use single-decrement logic
