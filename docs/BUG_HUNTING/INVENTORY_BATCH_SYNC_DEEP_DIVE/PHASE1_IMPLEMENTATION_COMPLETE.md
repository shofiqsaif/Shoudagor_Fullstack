# Phase 1 Implementation: Inventory Stock and Batch Synchronization

## Overview

Phase 1 implements a centralized **StockMutationService** within the existing `InventorySyncService` that owns all stock mutations atomically. When batch tracking is enabled, both `batch` and `inventory_stock` tables are updated in a single transaction with rollback on failure.

## Purpose

When batch tracking is enabled (`CompanyInventorySetting.batch_tracking_enabled = true`), the invariant must hold:

```
For every (company_id, product_id, variant_id, location_id):
  SUM(batch.qty_on_hand) == inventory_stock.quantity
```

## Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| StockSource enum | ✅ Complete | `app/schemas/inventory/stock_change.py` |
| StockChange schema | ✅ Complete | `app/schemas/inventory/stock_change.py` |
| StockMutationResult schema | ✅ Complete | `app/schemas/inventory/stock_change.py` |
| apply_stock_mutation() | ✅ Complete | `app/services/inventory/inventory_sync_service.py:482` |
| Nested transaction | ✅ Complete | `app/services/inventory/inventory_sync_service.py:536` |
| API endpoint | ✅ Complete | `app/api/inventory/batch.py:964` |

---

## Architecture

### Data Flow

```
Client Request
      │
      ▼
API Endpoint (POST /stock-mutation)
      │
      ▼
InventorySyncService.apply_stock_mutation()
      │
      ├──▶ is_batch_tracking_enabled?
      │
      ├──▶ YES (Batch Mode):
      │     │
      │     ▼
      │     1. Validate location_id not NULL
      │     2. Check stock availability (for outbound)
      │     3. BEGIN NESTED TRANSACTION (Savepoint)
      │     │     │
      │     │     ├── _execute_batch_operation()
      │     │     │     │
      │     │     │     └── Route to handler:
      │     │     │           • _handle_purchase_receipt
      │     │     │           • _handle_sales_delivery
      │     │     │           • _handle_sales_return
      │     │     │           • _handle_adjustment
      │     │     │           • _handle_transfer
      │     │     │           • _handle_dsr_load
      │     │     │           • _handle_dsr_unload
      │     │     │           • _handle_opening_balance
      │     │     │
      │     │     └── _sync_inventory_stock_to_batch()
      │     │
      │     ├── IF success: COMMIT
      │     └── IF error: ROLLBACK (both batch & stock)
      │
      └──▶ NO (Legacy Mode):
            │
            ▼
            _apply_stock_mutation_legacy()
                  │
                  └── Update inventory_stock only
```

---

## API Usage

### Endpoint

```
POST /api/company/inventory/batches/stock-mutation
```

### Request Schema

```json
{
  "company_id": 1,
  "product_id": 100,
  "variant_id": 50,
  "location_id": 1,
  "qty_delta": 10,
  "source": "PURCHASE_RECEIPT",
  "ref_type": "PURCHASE_DELIVERY",
  "ref_id": 123,
  "unit_cost": 15.50,
  "user_id": 1,
  "sales_order_detail_id": null,
  "dsr_assignment_id": null
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | int | Yes | Company ID |
| `product_id` | int | Yes | Product ID |
| `variant_id` | int | No | Variant ID (can be null) |
| `location_id` | int | Yes | Storage location ID |
| `qty_delta` | decimal | Yes | Positive for increase, negative for decrease |
| `source` | enum | Yes | Source type (see below) |
| `ref_type` | string | Yes | Reference type (e.g., PURCHASE_DELIVERY) |
| `ref_id` | int | No | Reference ID |
| `unit_cost` | decimal | No | Unit cost for the transaction |
| `user_id` | int | No | User ID (defaults to 1) |
| `sales_order_detail_id` | int | No | Sales order detail ID for allocation tracking |
| `dsr_assignment_id` | int | No | DSR assignment ID for DSR operations |

### StockSource Enum Values

| Value | Description |
|-------|-------------|
| `PURCHASE_RECEIPT` | Create batch for purchase delivery |
| `SALES_DELIVERY` | Allocate from batch for sales delivery |
| `SALES_RETURN` | Reverse allocation for sales return |
| `ADJUSTMENT` | Create adjustment batch (positive or negative) |
| `TRANSFER` | Transfer between locations |
| `DSR_LOAD` | Load stock to DSR storage |
| `DSR_UNLOAD` | Unload stock from DSR storage |
| `OPENING_BALANCE` | Create synthetic opening batch |

### Response Schema

```json
{
  "success": true,
  "message": "Stock mutation applied successfully",
  "data": {
    "success": true,
    "batch_ids": [1, 2],
    "movement_ids": [10, 11],
    "stock_quantity_after": 100.0,
    "inventory_stock_updated": true,
    "error": null
  }
}
```

---

## Core Methods

### InventorySyncService

#### `apply_stock_mutation(ctx: StockChangeContext) -> Dict[str, Any]`

Main entry point for stock mutations. Routes to batch mode or legacy mode based on company settings.

#### `_apply_stock_mutation_batch_mode(ctx: StockChangeContext) -> Dict[str, Any]`

Atomic batch mode handler with nested transaction (savepoint). Updates both batch and inventory_stock, rolling back on any failure.

#### `_apply_stock_mutation_legacy(ctx: StockChangeContext) -> Dict[str, Any]`

Legacy mode handler that only updates inventory_stock.

#### `_execute_batch_operation(ctx: StockChangeContext) -> BatchOperationResult`

Routes to the appropriate handler based on `StockSource`.

#### Handlers

| Method | Source | Operation |
|--------|--------|-----------|
| `_handle_purchase_receipt` | PURCHASE_RECEIPT | Creates batch + IN movement |
| `_handle_sales_delivery` | SALES_DELIVERY | Allocates from batch + OUT movement |
| `_handle_sales_return` | SALES_RETURN | Reverses allocation + RETURN_IN movement |
| `_handle_adjustment` | ADJUSTMENT | Creates adjustment batch + movement |
| `_handle_transfer` | TRANSFER | Source batch decrement + dest batch increment |
| `_handle_dsr_load` | DSR_LOAD | Allocates to DSR storage |
| `_handle_dsr_unload` | DSR_UNLOAD | Reverses DSR allocation |
| `_handle_opening_balance` | OPENING_BALANCE | Creates synthetic opening batch |

---

## Edge Cases and Error Handling

| Edge Case | Detection | Handling |
|-----------|-----------|----------|
| `location_id` is NULL | Check before batch op | Raise `BatchModeViolationError` |
| Insufficient stock | Check before outbound | Raise `InsufficientStockError` |
| Batch operation fails | Exception caught | Rollback entire transaction |
| Stock goes negative | Validate after | Raise `InsufficientStockError` |
| Concurrent modification | Use row locking | `SELECT FOR UPDATE SKIP LOCKED` |

### Exception Classes

- `InsufficientStockError`: Raised when not enough stock for outbound operation
- `BatchModeViolationError`: Raised when operation violates batch tracking rules
- `StockConsistencyError`: Raised when stock and batch totals are inconsistent

---

## Files Modified/Created

```
app/
├── schemas/
│   └── inventory/
│       └── stock_change.py           (EXISTING - Schema definitions)
│
├── services/
│   └── inventory/
│       └── inventory_sync_service.py (MODIFIED - Added mutation methods)
│
└── api/
    └── inventory/
        └── batch.py                  (MODIFIED - Added stock-mutation endpoint)
```

---

## Integration with Existing Services

The centralized `InventorySyncService.apply_stock_mutation()` is now available. Existing services that need to be refactored to use it:

### High Priority

| Service | Current Method | Should Use |
|---------|----------------|------------|
| `product_order_delivery_detail_service.py` | Creates batch + updates stock separately | `apply_stock_mutation()` with `PURCHASE_RECEIPT` |
| `sales_order_delivery_detail_service.py` | `_update_inventory_stock()` | `apply_stock_mutation()` with `SALES_DELIVERY` |
| `sales_order_service.py` | `process_return()` | `apply_stock_mutation()` with `SALES_RETURN` |
| `inventory_adjustment.py` | Direct batch + stock | `apply_stock_mutation()` with `ADJUSTMENT` |
| `stock_transfer.py` | Direct operations | `apply_stock_mutation()` with `TRANSFER` |
| `dsr_so_assignment_service.py` | DSR load/unload | `apply_stock_mutation()` with `DSR_LOAD/UNLOAD` |

---

## Testing Requirements

### Integration Tests Needed

| Test Scenario | Expected Behavior |
|---------------|-------------------|
| PO delivery with partial deliveries | Batch created for each delivery, stock updated |
| Sales delivery | Batch allocated, stock decremented |
| Sales return | Allocation reversed, stock incremented |
| Positive adjustment | Batch created, stock increased |
| Negative adjustment | Batch decremented, stock decreased |
| Stock transfer | Source batch decremented, dest batch incremented |
| DSR load | DSR batch allocated, DSR stock updated |
| DSR unload | DSR allocation reversed, DSR stock decremented |
| Batch op fails | Entire transaction rolled back |

---

## Success Criteria

1. ✅ All stock mutations go through single service
2. ✅ Batch and inventory_stock always match after any operation
3. ✅ Failures roll back completely (no partial updates)
4. ✅ All existing workflows continue to work
5. ✅ New error handling prevents data corruption
6. ⏳ Integration with existing services (Phase 2)
7. ⏳ Integration tests

---

## References

- Deep Dive Document: `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md`
- Implementation Plan: `docs/PHASE1_IMPLEMENTATION_PLAN.md`
- Batch Allocation Service: `app/services/inventory/batch_allocation_service.py`
- Batch Models: `app/models/batch_models.py`
- Inventory Stock Model: `app/models/warehouse.py`
