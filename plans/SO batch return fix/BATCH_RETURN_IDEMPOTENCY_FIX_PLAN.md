# Batch Return Idempotency & Over-crediting Fix Plan

## 1. Issue Description
When multiple partial returns are processed for the same Sales Order (SO) detail, the system does not track how much of a specific batch allocation has already been returned. 

**Example Scenario:**
*   **Batch A**: 12 units allocated (and depleted).
*   **Batch B**: 3 units allocated.
*   **Total**: 15 units.
*   **Attempt 1**: Return 3 units. The system correctly identifies the most recent allocation (Batch B) and returns 3 units to it.
*   **Attempt 2**: Return 12 units. The system currently iterates through allocations in reverse order. It sees Batch B has 3 units allocated, and (erroneously) returns 3 more units to it because it doesn't know Batch B was already "filled back" in Attempt 1. It then returns the remaining 9 to Batch A.
*   **Final (Incorrect) State**: Batch B gets 6 units back (3 more than taken). Batch A gets 9 units back (3 fewer than taken).

## 2. Technical Root Cause
In `BatchAllocationService.process_return`, the logic for calculating `return_qty` is:
```python
return_qty = min(remaining, allocation.qty_allocated)
```
This fails to account for previously returned quantities. Additionally, `RETURN_IN` movements created during the return process are not currently linked to the original `OUT` movements via `related_movement_id`.

## 3. Implementation Plan

### 3.1 Repository Enhancement
Add a helper method to `InventoryMovementRepository` in `Shoudagor/app/repositories/inventory/batch.py` to calculate the already returned quantity for a specific movement.

```python
def get_returned_qty_for_movement(self, movement_id: int) -> Decimal:
    """Calculate total returned quantity for a specific OUT movement"""
    result = self.db.query(func.sum(InventoryMovement.qty)).filter(
        InventoryMovement.related_movement_id == movement_id,
        InventoryMovement.movement_type == "RETURN_IN",
        InventoryMovement.is_deleted == False
    ).scalar()
    return Decimal(str(result or 0))
```

### 3.2 Service Layer Refactor
Modify `process_return` in `Shoudagor/app/services/inventory/batch_allocation_service.py`:

1.  **Calculate Return Capacity**: For each allocation, subtract already returned quantities from the original allocation amount.
2.  **Link Movements**: Pass the original `allocation.movement_id` as the `related_movement_id` when creating the new `RETURN_IN` movement.

**Proposed Logic Change:**
```python
for allocation in original_allocations:
    if remaining <= 0:
        break
    
    # NEW: Calculate how much has already been returned to this specific allocation
    already_returned = self.movement_repo.get_returned_qty_for_movement(allocation.movement_id)
    return_capacity = allocation.qty_allocated - already_returned
    
    if return_capacity <= 0:
        continue
        
    return_qty = min(remaining, return_capacity)
    
    # ... logic to update batch ...

    # Create RETURN_IN movement LINKED to the original OUT movement
    movement = self.movement_repo.create_movement(
        ...
        related_movement_id=allocation.movement_id, # LINK ESTABLISHED
        ...
    )
```

## 4. Verification Plan

### 4.1 Automated Test Case
Create a new test in `Shoudagor/tests/test_batch_inventory/test_return_idempotency.py`:
1.  Setup a Sales Order with two batches (12 from Batch A, 3 from Batch B).
2.  Process Return 1: 3 units.
    *   Verify Batch B `qty_on_hand` increases by 3.
    *   Verify Batch A `qty_on_hand` remains unchanged.
3.  Process Return 2: 12 units.
    *   Verify Batch B `qty_on_hand` **does not change** (it's already at capacity).
    *   Verify Batch A `qty_on_hand` increases by 12.
4.  Verify no "Synthetic" batches were created unnecessarily.

## 5. Anticipated Risks
*   **Performance**: One additional query per allocation in the return loop. If an SO detail has many small allocations, this could be slow. *Mitigation*: We could fetch all return movements for the SO detail once and aggregate them in memory if performance becomes an issue.
*   **Data Migration**: Existing returns that were processed before this fix will not have `related_movement_id` set, so they won't be accounted for in future partial returns.

## 6. Next Steps
- [ ] Approve the implementation plan.
- [ ] Apply Repository changes.
- [ ] Apply Service Layer changes.
- [ ] Run verification tests.
