# Depleted Batch Fix Plan

## 1. Issue Description
When a Sales Order return is processed, the `BatchAllocationService` checks if the original batch used for the order is currently `active`. If the batch was fully sold (status: `depleted`), the system currently skips it and creates a new "Synthetic" batch record. This results in fragmented batch history and redundant records, as the original batch should simply be re-credited and re-activated.

---

## 2. Technical Root Cause
In `Shoudagor/app/services/inventory/batch_allocation_service.py`, the `process_return` method contains the following conditional check:
```python
if batch and batch.status == "active" and not batch.is_deleted:
    # Logic to increment existing batch
else:
    # Logic to create a NEW synthetic batch
```
Since `depleted` batches do not match `status == "active"`, they fall into the `else` block every time.

---

## 3. Implementation Steps

### 3.1 Backend Service Update
Modify the `process_return` method in `Shoudagor/app/services/inventory/batch_allocation_service.py`:
- **Change**: Update the conditional to include `depleted` status.
- **New Code**: `if batch and batch.status in ["active", "depleted"] and not batch.is_deleted:`

### 3.2 Verification of Repository Logic
Ensure `BatchRepository.increment_qty_on_hand` (in `Shoudagor/app/repositories/inventory/batch.py`) is functioning as expected:
- It must increment the `qty_on_hand`.
- It must toggle `status` from `depleted` back to `active` if the new quantity is greater than zero.
*(Analysis confirms this logic is already present in the repository, so only the service layer change is required.)*

---

## 4. Expected Outcome
- **Re-activation**: When an item is returned to a depleted batch, that batch's quantity increases and its status returns to `active`.
- **History Preservation**: The `inventory.movement` table will show a `RETURN_IN` entry linked to the original batch ID, maintaining a clean audit trail.
- **No Redundancy**: No unnecessary "Synthetic" batches will be created for items that have an existing (but depleted) original batch record.

---

## 5. Verification Plan
1.  **Setup**: Identify an SO detail fulfilled from a batch that is now `depleted` (qty = 0).
2.  **Action**: Process a return for 1 unit of that item.
3.  **Check**: 
    - Verify the original batch's `qty_on_hand` is now 1.
    - Verify the original batch's `status` is now `active`.
    - Verify **no new batch** was created in the `inventory.batch` table.
