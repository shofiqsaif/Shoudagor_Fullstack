# Implementation Plan: Inventory Batch Sync Edge Cases and Error Handling

## Overview

This document outlines the implementation plan for improving edge cases and error handling in the inventory batch sync system based on the analysis in `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md`.

---

## Current State Analysis

### Already Implemented ✅

| Edge Case | Status | Key Files |
|-----------|--------|-----------|
| UOM Conversion | **GOOD** - Exists with good coverage | `uom_utils.py`, delivery services |
| Partial Deliveries + Free | **GOOD** - Good coverage | `batch_allocation_service.py`, delivery services |
| Location NULL Handling | **GOOD** - Error handling exists | `batch_allocation_service.py:344-348`, `inventory_sync_service.py:612-615` |
| Concurrency | **GOOD** - Row-level locks | `batch.py:272-350`, `batch_allocation_service.py` |
| Failure Paths/Rollback | **GOOD** - Nested transactions | All services with `savepoint.rollback()` |
| Stock Transfer Fix | **GOOD** - Uses InventorySyncService | `stock_transfer.py:197-240` |

### Gaps Identified ⚠️

| Edge Case | Priority | Current Issue |
|-----------|----------|---------------|
| Soft Deletes | **HIGH** | No batch quantity adjustment when inventory_stock is deleted |
| Inventory Adjustment | **HIGH** | Still uses `sales_order_detail_id=0` and has fallback behavior |
| Silent UOM Fallback | **MEDIUM** | Silently uses original quantity if conversion fails |
| Free Quantity Cost | **MEDIUM** | Free items use same unit_cost as billable |
| DSR Unload Validation | **MEDIUM** | No explicit validation that DSR has sufficient stock |
| Adjustment Rollback | **MEDIUM** | Update/delete doesn't reverse batch movements |

---

## Implementation Plan

### 1. Soft Deletes - Batch Quantity Adjustment (HIGH PRIORITY)

**Issue:** When `inventory_stock` is deleted in batch tracking mode, batch quantities are NOT adjusted, causing inconsistency.

**Files to Modify:**
- `app/services/warehouse/warehouse.py` - `delete_inventory_stock()` method

**Implementation:**

```python
# In delete_inventory_stock() method, add batch adjustment before soft delete:

def delete_inventory_stock(self, stock_id: int, user_id: int = 1):
    db_stock = self.inventory_stock_repo._get_orm(stock_id)
    if not db_stock:
        return None

    # BLOCK: Prevent manual stock deletion when batch tracking is enabled
    block_stock_mutation_in_batch_mode(
        self.repo.db, db_stock.company_id, "delete_inventory_stock"
    )

    # NEW: If batch tracking enabled, validate batches before delete
    sync_service = InventorySyncService(self.inventory_stock_repo.db)
    if sync_service.is_batch_tracking_enabled(db_stock.company_id):
        # Get batch total for this stock
        batch_total = sync_service.get_batch_total_qty(
            company_id=db_stock.company_id,
            product_id=db_stock.product_id,
            variant_id=db_stock.variant_id,
            location_id=db_stock.location_id,
        )

        if batch_total > 0:
            # Block deletion if batches exist - direct users to use batch operations
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete inventory_stock: {batch_total} units exist in batches. "
                       f"Delete or transfer batch quantities first."
            )

    self.inventory_stock_repo.delete(db_stock)
    return True
```

---

### 2. Inventory Adjustment Fix (HIGH PRIORITY)

**Issue:** 
- Still uses `sales_order_detail_id=0` for negative adjustments
- Fallback behavior continues with legacy stock update even if batch fails

**Files to Modify:**
- `app/services/transaction/inventory_adjustment.py`
- `app/services/inventory/inventory_sync_service.py` - `_handle_adjustment()` method

**Implementation:**

#### 2a. Remove `sales_order_detail_id=0` - Use proper ref_type

In `inventory_adjustment.py` (lines 387-395), change to use proper adjustment handling:

```python
# OLD CODE:
allocations = self.batch_service.allocate(
    company_id=company_id,
    product_id=detail.product_id,
    variant_id=detail.variant_id,
    location_id=adjustment.location_id,
    qty_needed=qty_needed,
    sales_order_detail_id=0,  # Not applicable for adjustments  <-- PROBLEM
    user_id=user_id,
)

# NEW CODE:
# Route through InventorySyncService which handles adjustments properly
sync_service = InventorySyncService(self.repository.db)
ctx = StockChangeContext(
    company_id=company_id,
    product_id=detail.product_id,
    variant_id=detail.variant_id,
    location_id=adjustment.location_id,
    qty_delta=-qty_needed,  # Negative for deduction
    source=StockSource.ADJUSTMENT,
    ref_type="ADJUSTMENT",
    ref_id=adjustment.adjustment_id,
    user_id=user_id,
)
result = sync_service.apply_stock_mutation(ctx)
if not result.get("success"):
    raise HTTPException(
        status_code=400,
        detail=f"Batch adjustment failed: {result.get('error')}"
    )
```

#### 2b. Update _handle_adjustment in inventory_sync_service.py

```python
def _handle_adjustment(
    self,
    ctx: StockChangeContext,
) -> BatchOperationResult:
    """Handle inventory adjustment - create adjustment batch + movement"""

    from app.services.inventory.batch_allocation_service import (
        BatchAllocationService,
    )

    batch_service = BatchAllocationService(self.db)

    try:
        if ctx.qty_delta > 0:
            # Positive adjustment - create synthetic batch
            movement_id = batch_service.create_adjustment_movement(
                company_id=ctx.company_id,
                product_id=ctx.product_id,
                variant_id=ctx.variant_id,
                location_id=ctx.location_id,
                qty=ctx.qty_delta,
                unit_cost=ctx.unit_cost or Decimal("0"),
                adjustment_id=ctx.ref_id or 0,
                user_id=ctx.user_id,
                is_increase=True,
            )

            return BatchOperationResult(
                success=True,
                movement_ids=[movement_id] if movement_id else [],
            )
        else:
            # Negative adjustment - allocate from batches WITHOUT creating SalesOrderBatchAllocation
            abs_qty = abs(ctx.qty_delta)

            # Get batches and allocate (without SalesOrderBatchAllocation)
            batches = self.batch_repo.get_batches_for_allocation(
                company_id=ctx.company_id,
                product_id=ctx.product_id,
                variant_id=ctx.variant_id,
                location_id=ctx.location_id,
                qty_needed=abs_qty,
            )

            if not batches or sum(b.qty_on_hand for b in batches) < abs_qty:
                return BatchOperationResult(
                    success=False,
                    error=f"Insufficient stock for negative adjustment. Available: {sum(b.qty_on_hand for b in batches) if batches else 0}, Requested: {abs_qty}"
                )

            # Create OUT movements with ref_type='ADJUSTMENT' (NOT SALES_DELIVERY)
            movement_ids = []
            qty_remaining = abs_qty

            for batch in batches:
                qty_from_batch = min(batch.qty_on_hand, qty_remaining)
                batch.qty_on_hand -= qty_from_batch

                movement = InventoryMovement(
                    company_id=ctx.company_id,
                    batch_id=batch.batch_id,
                    product_id=ctx.product_id,
                    variant_id=ctx.variant_id,
                    qty=-qty_from_batch,  # Negative for OUT
                    movement_type="OUT",
                    ref_type="ADJUSTMENT",  # Use ADJUSTMENT not SALES_DELIVERY
                    ref_id=ctx.ref_id or 0,
                    unit_cost_at_txn=batch.unit_cost,
                    actor=ctx.user_id,
                    txn_timestamp=func.now(),
                    location_id=ctx.location_id,
                    cb=ctx.user_id,
                    mb=ctx.user_id,
                )
                self.db.add(movement)
                self.db.flush()
                movement_ids.append(movement.movement_id)

                qty_remaining -= qty_from_batch
                if qty_remaining <= 0:
                    break

            # Do NOT create SalesOrderBatchAllocation for adjustments
            return BatchOperationResult(
                success=True,
                batch_ids=[b.batch_id for b in batches],
                movement_ids=movement_ids,
                allocation_ids=[],  # EMPTY - no sales allocation
            )

    except Exception as e:
        return BatchOperationResult(
            success=False, error=f"Adjustment batch operation failed: {str(e)}"
        )
```

#### 2c. Remove Fallback Behavior in inventory_adjustment.py

In `inventory_adjustment.py` (lines 408-411 and 433-436):

```python
# OLD CODE (lines 408-411):
except Exception as e:
    logger.error(f"Error in batch allocation for adjustment: {e}")
    # Continue with legacy stock update if batch allocation fails  <-- REMOVE

# NEW CODE:
except Exception as e:
    logger.error(f"Error in batch allocation for adjustment: {e}")
    # Do NOT continue - raise error instead
    raise HTTPException(
        status_code=500,
        detail=f"Batch allocation failed for adjustment: {str(e)}. Operation rolled back.",
    )
```

---

### 3. UOM Conversion Validation (MEDIUM PRIORITY)

**Issue:** Silent fallback uses original quantity if conversion fails, could lead to incorrect stock.

**Files to Modify:**
- `app/services/uom_utils.py`

**Implementation:**

```python
# Add validation in convert_to_base function:

def convert_to_base(db: Session, quantity: Decimal, uom_id: int) -> Decimal:
    """
    Convert quantity from given UOM to base UOM.

    Args:
        db: Database session
        quantity: Quantity to convert
        uom_id: Source unit of measure ID

    Returns:
        Quantity in base UOM

    Raises:
        ValueError: If conversion fails or UOM not found
    """
    if uom_id is None:
        # NEW: Raise error instead of silent fallback
        raise ValueError("Cannot convert quantity: uom_id is None")

    # Get the UOM record
    uom = db.query(UnitOfMeasure).filter(
        UnitOfMeasure.unit_id == uom_id
    ).first()

    if not uom:
        # NEW: Raise error instead of silent fallback
        raise ValueError(f"Cannot convert quantity: UOM with id {uom_id} not found")

    # NEW: Validate conversion_factor is positive
    if not uom.conversion_factor or uom.conversion_factor <= 0:
        raise ValueError(
            f"Cannot convert quantity: UOM '{uom.unit_name}' has invalid "
            f"conversion_factor: {uom.conversion_factor}"
        )

    # Existing logic
    return quantity * uom.conversion_factor
```

---

### 4. Free Quantity Cost Tracking (MEDIUM PRIORITY)

**Issue:** Free items use same unit_cost as billable - may not reflect actual cost.

**Files to Modify:**
- `app/services/procurement/product_order_delivery_detail_service.py`
- `app/services/inventory/batch_allocation_service.py`

**Implementation:**

Add ability to specify separate cost for free quantities in batch creation:

```python
# In create_batch_for_purchase_receipt() method, add parameter:

def create_batch_for_purchase_receipt(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
    location_id: int,
    qty_received: Decimal,
    unit_cost: Decimal,
    supplier_id: Optional[int] = None,
    lot_number: Optional[str] = None,
    purchase_order_detail_id: Optional[int] = None,
    received_date: datetime = None,
    user_id: int = 1,
    delivery_detail_id: Optional[int] = None,
    free_qty: Decimal = Decimal("0"),  # NEW: Separate free quantity
    free_unit_cost: Optional[Decimal] = None,  # NEW: Separate cost for free
):
    """
    Create a new batch for purchase receipt.

    If free_qty > 0, creates separate batch or splits cost allocation.
    """

    # For billable quantity
    billable_qty = qty_received - free_qty

    # If free_unit_cost not provided, use main unit_cost
    effective_free_cost = free_unit_cost if free_unit_cost is not None else unit_cost

    # Option 1: Create single batch with weighted average cost
    total_qty = billable_qty + free_qty
    if total_qty > 0:
        weighted_avg_cost = (
            (billable_qty * unit_cost) + (free_qty * effective_free_cost)
        ) / total_qty
        # Create single batch with weighted cost

    # Option 2: Create separate batches for billable and free
    # (Recommended for accurate cost tracking)
    if billable_qty > 0:
        # Create billable batch
        ...
    if free_qty > 0:
        # Create free batch with separate cost
        ...
```

---

### 5. DSR Unload Validation (MEDIUM PRIORITY)

**Issue:** No explicit validation that DSR has sufficient stock before unload.

**Files to Modify:**
- `app/services/inventory/inventory_sync_service.py` - `_handle_dsr_unload()` method

**Implementation:**

```python
# In _handle_dsr_unload() method, add validation:

def _handle_dsr_unload(
    self,
    ctx: StockChangeContext,
) -> BatchOperationResult:
    """Handle DSR unload - reverse DSR allocation"""

    from app.models.batch_models import DSRBatchAllocation

    if not ctx.dsr_assignment_id:
        return BatchOperationResult(
            success=False, error="dsr_assignment_id required for DSR unload"
        )

    try:
        dsr_allocations = (
            self.db.query(DSRBatchAllocation)
            .filter(
                DSRBatchAllocation.assignment_id == ctx.dsr_assignment_id,
                DSRBatchAllocation.is_deleted == False,
            )
            .all()
        )

        # NEW: Validate DSR has sufficient allocated quantity
        total_allocated = sum(
            alloc.qty_allocated for alloc in dsr_allocations
        )
        unload_qty = abs(ctx.qty_delta)

        if total_allocated < unload_qty:
            return BatchOperationResult(
                success=False,
                error=f"Cannot unload {unload_qty} units: DSR only has {total_allocated} units allocated. "
                      f"Verify DSR inventory and delivery records."
            )

        # Proceed with unload...
```

---

### 6. Inventory Adjustment Rollback (MEDIUM PRIORITY)

**Issue:** Update/delete of adjustment doesn't reverse batch movements.

**Files to Modify:**
- `app/services/transaction/inventory_adjustment.py` - Update and Delete methods

**Implementation:**

```python
# In update_inventory_adjustment() method:

def update_inventory_adjustment(
    self,
    adjustment_id: int,
    adjustment_update: InventoryAdjustmentUpdate,
    company_id: int,
    user_id: int,
):
    # Get existing adjustment
    existing = self.repository.get(adjustment_id, company_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Adjustment not found")

    # NEW: If batch tracking enabled, reverse old batch movements first
    sync_service = InventorySyncService(self.db)
    if sync_service.is_batch_tracking_enabled(company_id):
        for detail in existing.details:
            if detail.quantity_change < 0:
                # Reverse the negative adjustment (return stock)
                ctx = StockChangeContext(
                    company_id=company_id,
                    product_id=detail.product_id,
                    variant_id=detail.variant_id,
                    location_id=existing.location_id,
                    qty_delta=abs(detail.quantity_change),  # Reverse sign
                    source=StockSource.ADJUSTMENT,
                    ref_type="ADJUSTMENT_REVERSAL",
                    ref_id=adjustment_id,
                    user_id=user_id,
                )
                result = sync_service.apply_stock_mutation(ctx)
                if not result.get("success"):
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to reverse batch movements: {result.get('error')}"
                    )

    # Then apply new adjustment (existing logic)
    ...

# Similarly for delete_inventory_adjustment()
```

---

## Summary of Code Changes

| File | Change Type | Lines | Description |
|------|-------------|-------|-------------|
| `app/services/warehouse/warehouse.py` | MODIFY | 194-205 | Add batch validation before delete |
| `app/services/transaction/inventory_adjustment.py` | MODIFY | 373-436 | Remove fallback, fix adjustment handling |
| `app/services/inventory/inventory_sync_service.py` | MODIFY | 932-989 | Fix _handle_adjustment to not use sales_order_detail_id |
| `app/services/uom_utils.py` | MODIFY | ~1-50 | Add validation for conversion |
| `app/services/procurement/...` | MODIFY | ~140-152 | Support free qty cost tracking |
| `app/services/inventory/inventory_sync_service.py` | MODIFY | 1140-1205 | Add DSR unload validation |

---

## Testing Plan

After implementation, the following test cases should pass:

1. **Soft Delete Test**
   - Create inventory with batch tracking enabled
   - Attempt to delete inventory_stock → Should be blocked with clear error message

2. **Adjustment Test**
   - Create negative adjustment → Should NOT create SalesOrderBatchAllocation
   - InventoryMovement ref_type should be "ADJUSTMENT" not "SALES_DELIVERY"
   - Adjustment update/delete should reverse batch movements

3. **UOM Validation Test**
   - Attempt conversion with None UOM → Should raise ValueError
   - Attempt conversion with invalid factor → Should raise ValueError

4. **DSR Unload Test**
   - Attempt to unload more than allocated → Should raise error with clear message

---

## Rollback Strategy

All changes should be made incrementally with the ability to rollback:

1. Implement changes behind feature flags where possible
2. Add comprehensive logging before/after batch operations
3. Use database transactions with proper savepoints
4. Document all database schema changes (if any)

---

## Timeline Recommendation

| Phase | Priority | Estimated Effort |
|-------|----------|------------------|
| Phase 1 | HIGH - Soft Deletes & Adjustment Fix | 2-3 days |
| Phase 2 | MEDIUM - UOM Validation & DSR Validation | 1-2 days |
| Phase 3 | MEDIUM - Free Qty Cost & Rollback | 2-3 days |
| Phase 4 | Testing & Documentation | 1-2 days |

**Total Estimated: 6-10 days**

---

*Document created based on analysis of `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md`*
