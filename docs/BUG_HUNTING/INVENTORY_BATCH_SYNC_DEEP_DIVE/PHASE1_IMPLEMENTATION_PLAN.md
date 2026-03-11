# Phase 1 Implementation Plan: Inventory Stock and Batch Synchronization

## Purpose

When batch tracking is enabled (`CompanyInventorySetting.batch_tracking_enabled = true`), the invariant must hold:

```
For every (company_id, product_id, variant_id, location_id):
  SUM(batch.qty_on_hand) == inventory_stock.quantity
```

Phase 1 creates a centralized **StockMutationService** (extending existing `InventorySyncService`) that owns all stock mutations atomically. This eliminates the current split-authority problem where batch and inventory_stock can drift apart.

---

## Current State Analysis

### What Already Exists

| Component | Status | Purpose |
|-----------|--------|---------|
| `InventorySyncService` | ✅ Exists | Verification, reconciliation, policy enforcement |
| `InventoryStockMutationGuard` | ✅ Exists | Blocks direct stock mutations in batch mode |
| `BatchAllocationService` | ✅ Exists | Core batch allocation logic |
| `batch_guard.py` | ✅ Exists | Helper decorators and context managers |
| `CompanyInventorySetting` | ✅ Exists | `batch_tracking_enabled` flag |

### Current Problems (from Deep Dive Document)

1. **Split Authority**: Both inventory_stock and batch are updated independently
2. **Fallback on Error**: Many services continue updating inventory_stock even if batch operations fail
3. **Incorrect Allocation Usage**: Stock transfers use `sales_order_detail_id=0`
4. **Movement Semantics Corruption**: ref_type reused incorrectly for non-sales flows
5. **Partial Delivery Handling**: PO deliveries break after first receipt
6. **DSR Flow Inconsistencies**: Load/unload paths mutate unrelated movements
7. **Manual Stock Operations**: inventory_stock CRUD bypasses batch logic

---

## Implementation Plan

### 1. Create StockChange Schema

**File**: `app/schemas/inventory/stock_change.py` (NEW)

```python
from enum import Enum
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class StockSource(str, Enum):
    PURCHASE_RECEIPT = "PURCHASE_RECEIPT"
    SALES_DELIVERY = "SALES_DELIVERY"
    SALES_RETURN = "SALES_RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"
    DSR_LOAD = "DSR_LOAD"
    DSR_UNLOAD = "DSR_UNLOAD"
    OPENING_BALANCE = "OPENING_BALANCE"

class StockChange(BaseModel):
    company_id: int
    product_id: int
    variant_id: Optional[int] = None
    location_id: int
    qty_delta: Decimal = Field(description="Positive for increase, negative for decrease")
    source: StockSource
    ref_type: str
    ref_id: Optional[int] = None
    unit_cost: Optional[Decimal] = None
    user_id: int = 1
    sales_order_detail_id: Optional[int] = None
    dsr_assignment_id: Optional[int] = None
    
    @field_validator('location_id')
    @classmethod
    def validate_location(cls, v):
        if v is None:
            raise ValueError("location_id is required for batch operations")
        return v
```

### 2. Extend InventorySyncService

**File**: `app/services/inventory/inventory_sync_service.py` (EXTEND)

Add new imports and data classes:

```python
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

# Add these classes (or import from schema if preferred)

class StockSource(str, Enum):
    PURCHASE_RECEIPT = "PURCHASE_RECEIPT"
    SALES_DELIVERY = "SALES_DELIVERY"
    SALES_RETURN = "SALES_RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"
    DSR_LOAD = "DSR_LOAD"
    DSR_UNLOAD = "DSR_UNLOAD"
    OPENING_BALANCE = "OPENING_BALANCE"

@dataclass
class StockChangeContext:
    """Context object for stock mutations"""
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

@dataclass
class StockMutationResult:
    """Result of a stock mutation operation"""
    success: bool
    batch_ids: List[int] = field(default_factory=list)
    movement_ids: List[int] = field(default_factory=list)
    stock_quantity_after: Decimal = Decimal("0")
    inventory_stock_updated: bool = False
    error: Optional[str] = None
```

### 3. Add Core Mutation Methods to InventorySyncService

Add these methods to the `InventorySyncService` class:

#### 3.1 Main Entry Point

```python
def apply_stock_mutation(
    self,
    ctx: StockChangeContext,
) -> StockMutationResult:
    """
    Apply a stock mutation atomically.
    
    When batch tracking is enabled:
    - Batch and inventory_stock are updated in single transaction
    - Failure in either rolls back the entire operation
    
    When batch tracking is disabled:
    - Only updates inventory_stock (legacy behavior)
    
    Args:
        ctx: StockChangeContext with mutation details
        
    Returns:
        StockMutationResult with operation details
        
    Raises:
        BatchModeViolationError: If operation violates batch mode rules
        InsufficientStockError: If not enough stock for outbound
    """
    # Step 1: Validate batch mode requirements
    is_batch_mode = self.is_batch_tracking_enabled(ctx.company_id)
    
    if is_batch_mode:
        return self._apply_stock_mutation_batch_mode(ctx)
    else:
        return self._apply_stock_mutation_legacy(ctx)
```

#### 3.2 Batch Mode Handler

```python
def _apply_stock_mutation_batch_mode(
    self,
    ctx: StockChangeContext,
) -> StockMutationResult:
    """Apply stock mutation in batch tracking mode - atomic update"""
    
    # Validation
    if ctx.location_id is None:
        raise BatchModeViolationError(
            f"Cannot perform batch operation without location_id"
        )
    
    # For outbound operations, check stock availability
    if ctx.qty_delta < 0:
        available = self.get_batch_total_qty(
            ctx.company_id,
            ctx.product_id,
            ctx.variant_id,
            ctx.location_id,
        )
        if available + ctx.qty_delta < 0:
            raise InsufficientStockError(
                f"Insufficient stock. Available: {available}, Requested: {abs(ctx.qty_delta)}"
            )
    
    try:
        # Begin transaction
        with self.db.begin_nested():
            # Step 1: Execute batch operation based on source
            batch_result = self._execute_batch_operation(ctx)
            
            # Step 2: Update inventory_stock to match batch
            stock_result = self._sync_inventory_stock_to_batch(ctx)
            
            # Verify both succeeded
            if not batch_result.success:
                raise Exception(batch_result.error or "Batch operation failed")
        
        # Commit on success
        self.db.commit()
        
        # Return final quantity from batch
        final_qty = self.get_batch_total_qty(
            ctx.company_id,
            ctx.product_id,
            ctx.variant_id,
            ctx.location_id,
        )
        
        return StockMutationResult(
            success=True,
            batch_ids=batch_result.batch_ids,
            movement_ids=batch_result.movement_ids,
            stock_quantity_after=final_qty,
            inventory_stock_updated=True,
        )
        
    except Exception as e:
        self.db.rollback()
        # CRITICAL: Never leave inventory_stock updated when batch fails
        return StockMutationResult(
            success=False,
            error=str(e),
        )
```

#### 3.3 Legacy Mode Handler

```python
def _apply_stock_mutation_legacy(
    self,
    ctx: StockChangeContext,
) -> StockMutationResult:
    """Apply stock mutation in legacy mode - inventory_stock only"""
    
    try:
        stock = self._get_or_create_inventory_stock(
            ctx.company_id,
            ctx.product_id,
            ctx.variant_id,
            ctx.location_id,
        )
        
        old_qty = stock.quantity
        stock.quantity = old_qty + ctx.qty_delta
        stock.mb = ctx.user_id
        
        self.db.commit()
        
        return StockMutationResult(
            success=True,
            stock_quantity_after=stock.quantity,
            inventory_stock_updated=True,
        )
        
    except Exception as e:
        self.db.rollback()
        return StockMutationResult(
            success=False,
            error=str(e),
        )
```

#### 3.4 Batch Operation Router

```python
def _execute_batch_operation(
    self,
    ctx: StockChangeContext,
) -> StockMutationResult:
    """Route to appropriate batch operation based on source"""
    
    # Import here to avoid circular imports
    from app.services.inventory.batch_allocation_service import BatchAllocationService
    
    batch_service = BatchAllocationService(self.db)
    
    if ctx.source == StockSource.PURCHASE_RECEIPT:
        return self._handle_purchase_receipt(ctx, batch_service)
    elif ctx.source == StockSource.SALES_DELIVERY:
        return self._handle_sales_delivery(ctx, batch_service)
    elif ctx.source == StockSource.SALES_RETURN:
        return self._handle_sales_return(ctx, batch_service)
    elif ctx.source == StockSource.ADJUSTMENT:
        return self._handle_adjustment(ctx, batch_service)
    elif ctx.source == StockSource.TRANSFER:
        return self._handle_transfer(ctx, batch_service)
    elif ctx.source == StockSource.DSR_LOAD:
        return self._handle_dsr_load(ctx, batch_service)
    elif ctx.source == StockSource.DSR_UNLOAD:
        return self._handle_dsr_unload(ctx, batch_service)
    elif ctx.source == StockSource.OPENING_BALANCE:
        return self._handle_opening_balance(ctx, batch_service)
    else:
        raise ValueError(f"Unknown stock source: {ctx.source}")
```

#### 3.5 Individual Batch Handlers

Each handler calls the appropriate BatchAllocationService method:

- `_handle_purchase_receipt`: Create batch + IN movement
- `_handle_sales_delivery`: Allocate from batch + OUT movement
- `_handle_sales_return`: Reverse allocation + RETURN_IN movement
- `_handle_adjustment`: Create adjustment batch + ADJUSTMENT movement
- `_handle_transfer`: Transfer between batches
- `_handle_dsr_load`: DSR batch allocation + DSR stock update
- `_handle_dsr_unload`: Reverse DSR allocation + DSR stock update
- `_handle_opening_balance`: Create synthetic opening batch

#### 3.6 Inventory Stock Sync

```python
def _sync_inventory_stock_to_batch(
    self,
    ctx: StockChangeContext,
) -> StockMutationResult:
    """Sync inventory_stock to match batch totals after mutation"""
    
    batch_total = self.get_batch_total_qty(
        ctx.company_id,
        ctx.product_id,
        ctx.variant_id,
        ctx.location_id,
    )
    
    stock = self._get_or_create_inventory_stock(
        ctx.company_id,
        ctx.product_id,
        ctx.variant_id,
        ctx.location_id,
    )
    
    stock.quantity = batch_total
    stock.mb = ctx.user_id
    
    return StockMutationResult(
        success=True,
        inventory_stock_updated=True,
    )

def _get_or_create_inventory_stock(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
    location_id: int,
) -> InventoryStock:
    """Get or create inventory_stock record"""
    
    stock = self.db.query(InventoryStock).filter(
        InventoryStock.company_id == company_id,
        InventoryStock.product_id == product_id,
        InventoryStock.location_id == location_id,
        InventoryStock.is_deleted == False,
    )
_id is not None:
        stock = stock.filter(InventoryStock.variant_id == variant_id)
    
    if variant    else:
        stock = stock.filter(InventoryStock.variant_id.is_(None))
    
    stock = stock.first()
    
    if not stock:
        stock = InventoryStock(
            company_id=company_id,
            product_id=product_id,
            variant_id=variant_id,
            location_id=location_id,
            quantity=Decimal("0"),
            is_deleted=False,
            cb=1,
            mb=1,
        )
        self.db.add(stock)
        self.db.flush()
    
    return stock
```

---

## Edge Cases and Error Handling

### Edge Case Handling Matrix

| Edge Case | Detection | Handling |
|-----------|-----------|----------|
| **location_id is NULL** | Check before batch op | Raise `BatchModeViolationError` |
| **Insufficient stock** | Check before outbound | Raise `InsufficientStockError` |
| **UOM conversion needed** | Check UOM on entry | Convert to base UOM before mutation |
| **Batch operation fails** | Exception caught | Rollback entire transaction |
| **No batch for outbound** | Check batch existence | Raise error in batch mode |
| **Concurrent modification** | Use row locking | `SELECT FOR UPDATE SKIP LOCKED` |
| **Zero qty_delta** | Check at entry | Return success, no-op |
| **Negative stock after update** | Validate after | Raise `StockConsistencyError` |
| **DSR stock not found** | Check DSR inventory | Create DSRInventoryStock if needed |
| **Partial delivery** | Track delivery IDs | Allow multiple batches per PO detail |

### Error Handling Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    apply_stock_mutation()                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  is_batch_tracking_enabled?                                    │
│  ├─ NO (Legacy Mode):                                         │
│  │   └─ _apply_stock_mutation_legacy()                        │
│  │       └─ Update inventory_stock only                       │
│  │       └─ Return result                                      │
│  │                                                            │
│  └─ YES (Batch Mode):                                          │
│      ├─ Validate location_id not None                         │
│      ├─ Check stock availability (for outbound)               │
│      ├─ BEGIN TRANSACTION                                      │
│      │   ├─ _execute_batch_operation()                        │
│      │   │   └─ Route to specific handler                      │
│      │   └─ _sync_inventory_stock_to_batch()                  │
│      │                                                            │
│      ├─ IF success:                                             │
│      │   └─ COMMIT                                             │
│      │                                                            │
│      └─ IF error:                                               │
│          ├─ ROLLBACK                                            │
│          └─ Return error result                                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Services to Refactor

After implementing the centralized service, refactor these existing services to use it:

### High Priority

| Service File | Current Method | New Method |
|--------------|----------------|------------|
| `product_order_delivery_detail_service.py` | Creates batch + updates stock separately | Use `apply_stock_mutation()` with `PURCHASE_RECEIPT` |
| `sales_order_delivery_detail_service.py` | `_update_inventory_stock()` | Use `apply_stock_mutation()` with `SALES_DELIVERY` |
| `sales_order_service.py` | `process_return()` | Use `apply_stock_mutation()` with `SALES_RETURN` |
| `inventory_adjustment.py` | Direct batch + stock | Use `apply_stock_mutation()` with `ADJUSTMENT` |
| `stock_transfer.py` | Direct operations | Use `apply_stock_mutation()` with `TRANSFER` |
| `dsr_so_assignment_service.py` | DSR load/unload | Use `apply_stock_mutation()` with `DSR_LOAD/UNLOAD` |

### Medium Priority

| Service File | Issue | Fix |
|--------------|-------|-----|
| `warehouse.py` | CRUD on inventory_stock | Block or route through service |
| `product_variant_service.py` | Creates stock directly | Route through service |
| `product_import_nested_service.py` | Creates stock directly | Route through service |

---

## File Structure Changes

```
app/
├── schemas/
│   └── inventory/
│       └── stock_change.py           (NEW - StockChange schema)
│
├── services/
│   └── inventory/
│       ├── inventory_sync_service.py (MODIFY - add mutation methods)
│       ├── batch_guard.py            (existing - no change)
│       ├── batch_allocation_service.py (existing - no change)
│       └── stock_mutation_service.py (DELETE if merged into sync_service)
```

---

## Implementation Order

1. **Create schema** (`app/schemas/inventory/stock_change.py`)
   - Define `StockSource` enum
   - Define `StockChange` Pydantic model
   - Define `StockMutationResult` model

2. **Add data classes** to `inventory_sync_service.py`
   - Import new types
   - Add `StockChangeContext` dataclass
   - Add `StockMutationResult` dataclass

3. **Implement core mutation methods**
   - `apply_stock_mutation()`
   - `_apply_stock_mutation_batch_mode()`
   - `_apply_stock_mutation_legacy()`
   - `_execute_batch_operation()`
   - Individual handlers for each source type
   - `_sync_inventory_stock_to_batch()`

4. **Add validation helpers**
   - `validate_location_required()`
   - validate stock availability

5. **Refactor services** (one by one, testing after each)
   - Product order delivery detail service
   - Sales order delivery detail service
   - Sales order service (returns)
   - Inventory adjustment
   - Stock transfer
   - DSR assignment service

6. **Add integration tests**
   - PO delivery with partial deliveries
   - Sales delivery + return
   - Inventory adjustment (positive and negative)
   - Stock transfer between locations
   - DSR load -> sale -> unload
   - Manual stock update blocked/synced

---

## Testing Requirements

### Unit Tests

- Test each mutation method in isolation
- Test edge cases (NULL location, insufficient stock, etc.)
- Test legacy vs batch mode routing

### Integration Tests

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
| Manual stock update in batch mode | Blocked with error message |

### Error Handling Tests

| Error Scenario | Expected Behavior |
|----------------|-------------------|
| Batch op fails | Entire transaction rolled back |
| Stock goes negative | Error raised before commit |
| Location is NULL | Error raised with clear message |
| Concurrent modification | Proper locking, no race conditions |

---

## Success Criteria

1. ✅ All stock mutations go through single service
2. ✅ Batch and inventory_stock always match after any operation
3. ✅ Failures roll back completely (no partial updates)
4. ✅ All existing workflows continue to work
5. ✅ New error handling prevents data corruption
6. ✅ Tests pass for all scenarios

---

## References

- Deep Dive Document: `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md`
- Existing Services:
  - `app/services/inventory/batch_allocation_service.py`
  - `app/services/inventory/inventory_sync_service.py`
  - `app/services/inventory/batch_guard.py`
- Models:
  - `app/models/warehouse.py` (InventoryStock)
  - `app/models/batch_models.py` (Batch, InventoryMovement)
