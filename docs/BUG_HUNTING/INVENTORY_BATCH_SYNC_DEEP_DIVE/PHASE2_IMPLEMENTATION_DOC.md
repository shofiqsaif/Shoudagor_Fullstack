# Phase 2 Implementation Documentation

## Overview

Phase 2 builds upon the centralized `InventorySyncService` established in Phase 1 to refactor all existing workflow services, eliminating inconsistencies and ensuring batch/inventory_stock synchronization. When batch tracking is enabled, ALL stock mutations must go through `InventorySyncService.apply_stock_mutation()`.

---

## Central Service: InventorySyncService

**Location:** `app/services/inventory/inventory_sync_service.py`

### StockSource Enumeration

```python
class StockSource(str, Enum):
    PURCHASE_RECEIPT = "PURCHASE_RECEIPT"
    SALES_DELIVERY = "SALES_DELIVERY"
    SALES_RETURN = "SALES_RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"
    DSR_LOAD = "DSR_LOAD"
    DSR_UNLOAD = "DSR_UNLOAD"
    OPENING_BALANCE = "OPENING_BALANCE"
```

### StockChangeContext

```python
@dataclass
class StockChangeContext:
    company_id: int
    product_id: int
    variant_id: Optional[int]
    location_id: int
    qty_delta: Decimal
    source: StockSource
    ref_type: str
    ref_id: Optional[int] = None
    unit_cost: Optional[Decimal] = None
    user_id: int = 1
    sales_order_detail_id: Optional[int] = None
    dsr_assignment_id: Optional[int] = None
    to_location_id: Optional[int] = None  # For transfers
    delivery_detail_id: Optional[int] = None  # For partial PO deliveries
```

### Implemented Handlers

| Handler Method | Source | Purpose |
|----------------|--------|---------|
| `_handle_purchase_receipt` | `StockSource.PURCHASE_RECEIPT` | Handle PO delivery batch creation |
| `_handle_sales_delivery` | `StockSource.SALES_DELIVERY` | Allocate from batches for sales |
| `_handle_sales_return` | `StockSource.SALES_RETURN` | Reverse allocations on return |
| `_handle_adjustment` | `StockSource.ADJUSTMENT` | Handle inventory adjustments |
| `_handle_transfer` | `StockSource.TRANSFER` | Handle warehouse transfers |
| `_handle_dsr_load` | `StockSource.DSR_LOAD` | Load stock to DSR storage |
| `_handle_dsr_unload` | `StockSource.DSR_UNLOAD` | Unload stock from DSR storage |
| `_handle_opening_balance` | `StockSource.OPENING_BALANCE` | Initial stock setup |

---

## Workflow Implementations

### 1. Purchase Receipts (Partial Deliveries)

**File:** `app/services/procurement/product_order_delivery_detail_service.py`

**Implementation:**
- Uses `InventorySyncService.apply_stock_mutation()` with `StockSource.PURCHASE_RECEIPT`
- Tracks `delivery_detail_id` to allow multiple batches per PO detail
- Creates batch records with unit cost from PO
- **NO FALLBACK**: If batch operation fails, entire operation fails

**Key Code:**
```python
if batch_tracking_enabled and base_quantity_change > 0 and location_id:
    ctx = StockChangeContext(
        company_id=company_id,
        product_id=purchase_order_detail.product_id,
        variant_id=purchase_order_detail.variant_id,
        location_id=location_id,
        qty_delta=Decimal(str(base_quantity_change)),
        source=StockSource.PURCHASE_RECEIPT,
        ref_type="PURCHASE_RECEIPT",
        ref_id=purchase_order_detail.purchase_order_detail_id,
        unit_cost=unit_cost,
        user_id=user_id,
        delivery_detail_id=delivery_detail_id,
    )
    result = sync_service.apply_stock_mutation(ctx)
    
    if not result.get("success", False):
        raise ValueError(f"Batch creation failed: {error_msg}...")
```

---

### 2. Sales Deliveries

**File:** `app/services/sales/sales_order_delivery_detail_service.py`

**Implementation:**
- Uses `InventorySyncService.apply_stock_mutation()` with `StockSource.SALES_DELIVERY`
- Allocates from batches using FIFO/LIFO/Weighted Average based on company settings
- Links to `SalesOrderBatchAllocation` for traceability
- **NO FALLBACK**: If batch allocation fails, raises HTTPException

**Key Code:**
```python
if batch_tracking_enabled:
    ctx = StockChangeContext(
        company_id=company_id,
        product_id=sales_order_detail.product_id,
        variant_id=sales_order_detail.variant_id,
        location_id=location_id,
        qty_delta=Decimal(str(base_quantity_change)),  # Negative for outbound
        source=StockSource.SALES_DELIVERY,
        ref_type="SALES_DELIVERY",
        ref_id=sales_order_detail.sales_order_detail_id,
        user_id=user_id,
        sales_order_detail_id=sales_order_detail.sales_order_detail_id,
    )
    
    result = sync_service.apply_stock_mutation(ctx)
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=f"Batch allocation failed...")
```

---

### 3. Sales Returns

**File:** `app/services/sales/sales_order_delivery_detail_service.py`

**Implementation:**
- Uses `BatchAllocationService.process_return()` 
- Reverses original batch allocation
- Creates RETURN_IN movement
- Validates return quantity <= shipped quantity

**Key Code:**
```python
if quantity_diff < 0 and sales_order and not (sales_order.is_loaded and sales_order.loaded_by_dsr_id):
    if self.batch_service.is_batch_tracking_enabled(company_id):
        abs_qty = abs(Decimal(str(quantity_diff)))
        self.batch_service.process_return(
            company_id=company_id,
            sales_order_detail_id=sales_order_detail.sales_order_detail_id,
            qty_returned=Decimal(str(base_qty)),
            user_id=user_id,
        )
```

---

### 4. Inventory Adjustments

**File:** `app/services/transaction/inventory_adjustment.py`

**Implementation:**
- Uses `InventorySyncService.apply_stock_mutation()` with `StockSource.ADJUSTMENT`
- Positive adjustments: Creates synthetic batch with movement
- Negative adjustments: Allocates from existing batches using FIFO
- Validates available stock before negative adjustment
- **NO FALLBACK**: If adjustment fails, raises HTTPException

**Key Code:**
```python
if batch_tracking_enabled:
    ctx = StockChangeContext(
        company_id=company_id,
        product_id=detail.product_id,
        variant_id=detail.variant_id,
        location_id=adjustment.location_id,
        qty_delta=quantity_change,
        source=StockSource.ADJUSTMENT,
        ref_type="ADJUSTMENT",
        ref_id=adjustment.adjustment_id,
        unit_cost=unit_cost,
        user_id=user_id,
    )
    
    result = sync_service.apply_stock_mutation(ctx)
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=f"Adjustment failed: {error_msg}")
```

---

### 5. Stock Transfers

**File:** `app/services/warehouse/stock_transfer.py`

**Implementation:**
- Uses `InventorySyncService.apply_stock_mutation()` with `StockSource.TRANSFER`
- Handles source decrement AND destination increment atomically
- **FIXED**: No more double-decrement (was calling allocate() AND create_transfer_movements())
- Single operation handles both source and destination

**Key Code:**
```python
# PHASE 2 FIX: Use centralized sync service
sync_service = InventorySyncService(self.repository.db)

if batch_tracking_enabled:
    ctx = StockChangeContext(
        company_id=company_id,
        product_id=detail.product_id,
        variant_id=detail.variant_id,
        location_id=transfer.source_location_id,
        qty_delta=-base_quantity_decimal,
        source=StockSource.TRANSFER,
        ref_type="STOCK_TRANSFER",
        ref_id=db_transfer.transfer_id,
        user_id=user_id,
        to_location_id=detail.target_location_id,
    )
    
    result = sync_service.apply_stock_mutation(ctx)
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=f"Stock transfer failed...")
```

---

### 6. DSR Load/Unload

**File:** `app/services/dsr/dsr_so_assignment_service.py`

**Implementation:**

**Load (load_so):**
- Creates `DSRBatchAllocation` records to track what's loaded to DSR
- Uses existing sales delivery allocations as source
- Does NOT rewrite existing SALES_DELIVERY movements

**Unload (unload_so):**
- Reverses exactly what was loaded via `DSRBatchAllocation`
- Increments batch qty_on_hand
- Creates DSR_TRANSFER movements (not rewriting sales movements)

**Key Code (Load):**
```python
if is_batch_enabled:
    for alloc in allocations:
        dsr_alloc = DSRBatchAllocation(
            assignment_id=assignment_id,
            batch_id=alloc.batch_id,
            qty_allocated=alloc.qty_allocated,
            unit_cost_at_transfer=alloc.unit_cost_at_allocation,
            movement_id=alloc.movement_id,
            cb=user_id,
            mb=user_id,
        )
        self.db.add(dsr_alloc)
```

**Key Code (Unload):**
```python
if is_batch_enabled:
    for alloc in dsr_allocations:
        # 1. Increment Batch Qty
        batch_repo.increment_qty_on_hand(alloc.batch_id, amount, user_id)
        
        # 2. Create Movement (Ref: DSR_TRANSFER)
        movement_repo.create_movement(..., movement_type="TRANSFER_IN", ...)
```

---

### 7. DSR Stock Transfers

**File:** `app/services/warehouse/dsr_stock_transfer.py`

**Implementation:**
- Uses `InventorySyncService.apply_stock_mutation()`
- Warehouse to DSR: Uses `StockSource.DSR_LOAD`
- DSR to Warehouse: Uses `StockSource.DSR_UNLOAD`
- Creates proper audit trail via InventoryTransaction

**Key Code:**
```python
if batch_tracking_enabled:
    if source_location and target_dsr_storage:
        # Warehouse to DSR: Use DSR_LOAD
        ctx = StockChangeContext(
            company_id=company_id,
            product_id=detail.product_id,
            variant_id=detail.variant_id,
            location_id=source_loc_id,
            qty_delta=-base_quantity,
            source=StockSource.DSR_LOAD,
            ref_type="DSR_STOCK_TRANSFER",
            ref_id=db_transfer.transfer_id,
            user_id=user_id,
        )
        result = sync_service.apply_stock_mutation(ctx)
    elif source_dsr_storage and target_location:
        # DSR to Warehouse: Use DSR_UNLOAD
        ctx.source = StockSource.DSR_UNLOAD
        result = sync_service.apply_stock_mutation(ctx)
```

---

### 8. Manual Inventory Stock CRUD

**File:** `app/services/inventory/batch_guard.py`

**Implementation:**
- Guards block direct stock mutations when batch tracking is enabled
- Raises `BatchModeViolationError` when attempting direct mutations
- Applied in `product_variant_service.py` for nested variant operations

**Guard Function:**
```python
def block_stock_mutation_in_batch_mode(
    db: Session, company_id: int, operation: str = "mutate inventory stock"
) -> None:
    sync_service = InventorySyncService(db)
    sync_service.validate_mutation_allowed(company_id, operation)
```

**Applied in:**
- `create_variant_nested()`: Blocks direct stock creation in batch mode
- `update_variant_nested()`: Blocks direct stock updates in batch mode

---

### 9. Variant Nested Updates

**File:** `app/services/inventory/product_variant_service.py`

**Implementation:**
- Uses blocking guards via `block_stock_mutation_in_batch_mode()`
- When batch tracking is enabled:
  - Prevents direct stock updates
  - Suggests using adjustment workflow instead
- Delta-based approach: deletes old, creates new

**Key Code:**
```python
if variant_update.inventory_stocks is not None:
    # BLOCK: Prevent direct stock updates when batch tracking is enabled
    block_stock_mutation_in_batch_mode(
        self.repo.db, product.company_id, "update_inventory_stock"
    )
    
    # Delete existing stocks
    existing_stocks = (...)
    for stock in existing_stocks:
        stock.is_deleted = True
        stock.md = datetime.now()
    
    # Create new stocks from provided list
    for stock_data in variant_update.inventory_stocks:
        # ... create new stock ...
```

---

### 10. Reporting

**File:** `app/repositories/inventory/product_variant.py`

**Implementation:**
- When batch tracking enabled: Uses batch totals ONLY
- When batch tracking disabled: Uses inventory_stock only
- Includes batch_stocks in API response for transparency

**Key Code:**
```python
if batch_repo.is_batch_tracking_enabled(company_id):
    variant_ids = [v.variant_id for v in variants]
    batch_stocks_summary = batch_repo.get_stock_summary_by_variant_and_location(
        company_id=company_id,
        variant_ids=variant_ids if variant_ids else None,
        location_ids=location_ids_list,
    )

if batch_tracking_enabled:
    # Use ONLY batch stock when batch tracking is enabled
    if batch_stocks_summary and variant.variant_id in batch_stocks_summary:
        for location_id, batch_qty in batch_locations.items():
            total_stock += batch_qty
else:
    # Legacy mode: Use inventory_stock only
    for stock in variant.inventory_stocks:
        total_stock += float(stock.quantity)
```

---

## Error Handling Summary

| Scenario | Behavior |
|----------|----------|
| Batch allocation fails | Raise HTTPException, rollback |
| Transfer double-decrement | Fixed - single decrement |
| Partial PO delivery | Allows multiple batches per PO detail |
| DSR load rewrite | Keeps separate movements |
| Manual stock CRUD | Blocked in batch mode |
| Report calculation | Single source (batch or inventory_stock) |

---

## Files Modified

```
app/
├── services/
│   ├── inventory/
│   │   ├── inventory_sync_service.py     # Central orchestrator
│   │   └── batch_guard.py                # Batch mode guards
│   ├── procurement/
│   │   └── product_order_delivery_detail_service.py  # Uses sync service
│   ├── sales/
│   │   ├── sales_order_delivery_detail_service.py    # Uses sync service
│   │   └── sales_order_service.py        # Uses sync service for returns
│   ├── transaction/
│   │   └── inventory_adjustment.py        # Uses sync service
│   ├── warehouse/
│   │   ├── stock_transfer.py              # Uses sync service, fixed double-decrement
│   │   └── dsr_stock_transfer.py         # Uses sync service
│   ├── dsr/
│   │   └── dsr_so_assignment_service.py  # Uses DSRBatchAllocation
│   └── inventory/
│       └── product_variant_service.py     # Uses blocking guards
│
└── repositories/
    └── inventory/
        └── product_variant.py             # Fixed report calculation
```

---

## Testing

### Unit Tests (Passing)
- `test_dsr_batch_tracking_load_so` - DSR Batch Tracking
- `test_record_locking_po_delivery` - PO Delivery locking
- `test_sales_return_deallocation` - Return deallocation
- `test_transaction_safety_batch_allocation` - Transaction safety

### Integration Tests
- Require PostgreSQL database with proper schema setup
- Require running API server
- Use endpoints at `http://localhost:8000`

---

## Success Criteria

1. All 10 workflows use `InventorySyncService` when batch tracking enabled
2. No fallback to legacy stock updates in batch mode
3. Batch and inventory_stock remain consistent after any operation
4. Proper error messages guide users to correct workflow
5. DSR load/unload does not modify sales delivery movements
6. Stock transfers use single-decrement logic

---

## Rollback Strategy

Each workflow change can be rolled back by:
1. Setting environment variable `USE_INVENTORY_SYNC_SERVICE=false`
2. Reverting to previous service implementation
3. Using database rollback for failed transactions

