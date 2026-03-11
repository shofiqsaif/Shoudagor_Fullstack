# Phase 3 Implementation Plan: Guardrails and Consistency Checks

**Document Version:** 2.0  
**Created:** 2026-03-11  
**Based on:** `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md`

---

## Executive Summary

This document outlines the implementation plan for **Phase 3: Guardrails and Consistency Checks** of the inventory batch synchronization project. After analyzing the existing codebase, most of the core infrastructure is already in place. This plan focuses on enhancements, edge case handling, and closing gaps to ensure robust invariant enforcement.

---

## Part A: Current Implementation Status (What's DONE)

Based on deep codebase analysis, the following Phase 3 components are **already implemented**:

| Component | File Location | Status |
|-----------|---------------|--------|
| Post-transaction consistency check | `app/services/inventory/inventory_sync_service.py:1251` - `PostTransactionGuard` class | ✅ Implemented |
| Company settings columns | `app/models/batch_models.py:262-270` - via migration `phase3_consistency_settings.py` | ✅ Implemented |
| Scheduled consistency job | `app/services/inventory/consistency_job.py` - `ConsistencyCheckJob` class | ✅ Implemented |
| Manual consistency endpoints | `app/api/inventory/batch.py:832` - `/consistency-check`, `/consistency/manual-check` | ✅ Implemented |
| Sync endpoints | `app/api/inventory/batch.py:897` - `/consistency-check/sync` | ✅ Implemented |
| Materialized views | `alembic/versions/phase3_materialized_views.py` | ✅ Implemented |
| Database triggers (batch) | `alembic/versions/phase3_batch_triggers.py` | ✅ Implemented |
| Exception handlers | `app/main.py:170` - `StockConsistencyError` handler | ✅ Implemented |
| Materialized view service | `app/services/inventory/materialized_view_service.py` | ✅ Implemented |
| Invariant verification | `verify_invariant()`, `verify_all_invariants()` methods | ✅ Implemented |
| Stock sync methods | `sync_stock_to_batch()`, `sync_all_stock_to_batch()` | ✅ Implemented |

---

## Part B: What's NOT Implemented (Gaps to Close)

Based on the deep dive document and codebase analysis, the following components need to be implemented:

---

### Task 1: Repair Action Suggestions Endpoint

**Priority:** HIGH  
**File:** `app/api/inventory/batch.py`

**Problem:** Currently, the system can detect discrepancies but cannot provide actionable recommendations for fixing them.

**Implementation:**

Add a new endpoint that analyzes discrepancies and suggests specific repair actions:

```python
@batch_router.get("/consistency/repair-suggestions")
async def get_repair_suggestions(
    company_id: int = Query(...),
    product_id: Optional[int] = Query(None),
    location_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_company_id: int = Depends(get_current_company_id),
):
    """
    Analyze discrepancies and provide repair action suggestions.
    
    Returns recommended actions:
    - SYNC_TO_BATCH: Sync inventory_stock to match batch totals
    - SYNC_TO_STOCK: Sync batch totals to match inventory_stock
    - CREATE_BATCH: Create missing batch records
    - INVESTIGATE: Manual investigation required
    """
    # Implementation:
    # 1. Get all discrepancies using verify_all_invariants()
    # 2. For each discrepancy, determine root cause:
    #    - batch_total = 0, stock > 0 → SYNC_TO_BATCH
    #    - stock = 0, batch > 0 → SYNC_TO_STOCK  
    #    - both exist but differ → SYNC_TO_BATCH (batch is source of truth)
    #    - both missing → INVESTIGATE
    # 3. Return list of suggested actions
```

**Edge Cases to Handle:**
- Handle NULL variant_id properly (treat as NULL not as 0)
- Consider tolerance settings when determining action
- Check for soft-deleted records before suggesting action

---

### Task 2: Enhanced Post-Transaction Guard with Proper Enforcement

**Priority:** HIGH  
**File:** `app/services/inventory/inventory_sync_service.py`

**Problem:** Currently, the post-transaction guard only logs violations but the `strict_consistency_check` setting exists but isn't enforced to actually block operations.

**Implementation:**

Enhance `PostTransactionGuard.verify_and_raise()` to actually enforce the invariant:

```python
class PostTransactionGuard:
    """
    Guard that runs after stock mutations to verify invariant.
    
    ENHANCEMENT: Add support for:
    - Automatic rollback option
    - Detailed error context
    - Custom tolerance per operation
    """
    
    def verify_and_raise(
        self,
        company_id: int,
        product_id: int,
        variant_id: Optional[int],
        location_id: int,
        force_strict: bool = False,  # Override setting
    ) -> None:
        """
        Verify invariant and raise StockConsistencyError if invalid.
        
        Args:
            company_id: Company ID
            product_id: Product ID
            variant_id: Variant ID (can be None)
            location_id: Location ID
            force_strict: Force strict mode regardless of company setting
            
        Raises:
            StockConsistencyError: If invariant is violated and strict mode is enabled
        """
        settings = self.setting_repo.get_by_company(company_id)
        
        # Check if strict mode should be enforced
        is_strict = force_strict or (
            settings and settings.strict_consistency_check
        )
        
        if not is_strict:
            return  # Skip check if not strict
        
        # Get tolerance from settings or use default
        tolerance = (
            settings.consistency_tolerance 
            if settings and settings.consistency_tolerance 
            else Decimal("0.0001")
        )
        
        is_valid, details = self.verify_after_mutation(
            company_id, product_id, variant_id, location_id, tolerance
        )
        
        if not is_valid:
            # Include suggested repair action in error
            suggested_action = self._determine_repair_action(details)
            
            raise StockConsistencyError(
                f"Post-mutation invariant violated. "
                f"Batch: {details['batch_total']}, Stock: {details['stock_quantity']}, "
                f"Difference: {details['difference']}. "
                f"Recommended action: {suggested_action}",
                details=details,
                suggested_action=suggested_action,
            )
    
    def _determine_repair_action(self, details: Dict) -> str:
        """Determine recommended repair action based on discrepancy details."""
        batch_total = details.get('batch_total', 0)
        stock_quantity = details.get('stock_quantity', 0)
        
        if batch_total == 0 and stock_quantity == 0:
            return "INVESTIGATE"
        elif batch_total == 0:
            return "CREATE_BATCH"
        elif stock_quantity == 0:
            return "SYNC_TO_BATCH"
        else:
            # Both have values but differ - batch is source of truth
            return "SYNC_TO_STOCK"
```

**Edge Cases:**
- Handle Decimal comparison properly (avoid floating-point issues)
- Log detailed context before raising exception
- Provide rollback SQL in error details for manual recovery

---

### Task 3: Enhanced Consistency Check with Better Edge Case Handling

**Priority:** HIGH  
**File:** `app/services/inventory/inventory_sync_service.py`

**Problem:** Current consistency check has gaps in handling:
- NULL variant_id
- Soft-deleted records
- UOM conversions

**Implementation:**

Enhance `verify_invariant()` method with proper edge case handling:

```python
def verify_invariant(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
    location_id: int,
    tolerance: Optional[Decimal] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify invariant: SUM(batch.qty_on_hand) == inventory_stock.quantity
    
    ENHANCEMENTS:
    - Proper NULL variant handling
    - Exclude soft-deleted batches
    - Check location company ownership
    - Consider UOM conversions
    """
    # Get settings for tolerance
    if tolerance is None:
        settings = self.setting_repo.get_by_company(company_id)
        tolerance = (
            settings.consistency_tolerance 
            if settings and settings.consistency_tolerance 
            else Decimal("0.0001")
        )
    
    # EDGE CASE 1: Handle NULL variant_id properly
    # Get batch total (only active, non-deleted)
    batch_total_query = self.db.query(
        func.coalesce(func.sum(Batch.qty_on_hand), Decimal("0"))
    ).filter(
        Batch.company_id == company_id,
        Batch.product_id == product_id,
        # CRITICAL: Handle NULL variant properly
        (
            (Batch.variant_id == variant_id) if variant_id is not None 
            else Batch.variant_id.is_(None)
        ),
        Batch.location_id == location_id,
        Batch.status == "active",
        Batch.is_deleted == False,  # EDGE CASE 2: Exclude soft-deleted
    )
    batch_total = batch_total_query.scalar() or Decimal("0")
    
    # Get inventory_stock (only non-deleted)
    stock_query = self.db.query(InventoryStock).filter(
        InventoryStock.company_id == company_id,
        InventoryStock.product_id == product_id,
        # CRITICAL: Handle NULL variant properly
        (
            (InventoryStock.variant_id == variant_id) if variant_id is not None 
            else InventoryStock.variant_id.is_(None)
        ),
        InventoryStock.location_id == location_id,
        InventoryStock.is_deleted == False,  # EDGE CASE 2: Exclude soft-deleted
    )
    
    stock = stock_query.first()
    stock_qty = stock.quantity if stock else Decimal("0")
    
    # Calculate difference using Decimal for precision
    difference = batch_total - stock_qty
    is_valid = abs(difference) <= tolerance
    
    return (is_valid, {
        "company_id": company_id,
        "product_id": product_id,
        "variant_id": variant_id,
        "location_id": location_id,
        "batch_total": float(batch_total),
        "stock_quantity": float(stock_qty),
        "difference": float(difference),
        "tolerance": float(tolerance),
        "is_valid": is_valid,
        # Additional context for debugging
        "batch_count": self._get_batch_count(company_id, product_id, variant_id, location_id),
        "has_stock_record": stock is not None,
    })

def _get_batch_count(
    self, 
    company_id: int, 
    product_id: int, 
    variant_id: Optional[int], 
    location_id: int
) -> int:
    """Get count of active batches for debugging."""
    query = self.db.query(func.count(Batch.batch_id)).filter(
        Batch.company_id == company_id,
        Batch.product_id == product_id,
        (
            (Batch.variant_id == variant_id) if variant_id is not None 
            else Batch.variant_id.is_(None)
        ),
        Batch.location_id == location_id,
        Batch.status == "active",
        Batch.is_deleted == False,
    )
    return query.scalar() or 0
```

**Edge Cases:**
- EDGE CASE 3: Handle location NULL properly (should fail with clear error)
- EDGE CASE 4: Consider multiple UOMs in same company
- EDGE CASE 5: Handle negative quantities (should not exist but might due to bugs)

---

### Task 4: Add Blocking Validation for Non-Sync Operations

**Priority:** HIGH  
**File:** `app/services/warehouse/warehouse.py`

**Problem:** As noted in the deep dive document, manual inventory_stock CRUD operations bypass batch logic entirely.

**Implementation:**

Add validation in warehouse service:

```python
def validate_batch_mode(self, company_id: int, operation: str) -> None:
    """
    Validate that mutation is allowed in current batch mode.
    
    Args:
        company_id: Company ID
        operation: Operation name (create_stock, update_stock, delete_stock)
        
    Raises:
        BatchModeViolationError: If operation not allowed in batch mode
    """
    from app.services.inventory.setting_service import CompanyInventorySettingService
    
    setting_service = CompanyInventorySettingService(self.db)
    settings = setting_service.get_by_company(company_id)
    
    if settings and settings.batch_tracking_enabled:
        if settings.strict_consistency_check:
            # In strict mode, block direct stock operations
            raise BatchModeViolationError(
                f"Cannot {operation} inventory_stock directly when batch tracking is enabled. "
                f"Use InventorySyncService to maintain invariant."
            )
        else:
            # Non-strict mode: warn but allow
            logger.warning(
                f"Direct stock {operation - may cause drift. "
                f} in batch mode"Consider using InventorySyncService."
            )

# Apply to all warehouse stock CRUD methods
def create_inventory_stock(self, ...):
    self.validate_batch_mode(company_id, "create_stock")
    # ... existing logic

def update_inventory_stock(self, ...):
    self.validate_batch_mode(company_id, "update_stock")
    # ... existing logic

def delete_inventory_stock(self, ...):
    self.validate_batch_mode(company_id, "delete_stock")
    # ... existing logic
```

**Edge Cases:**
- Allow manual operations during migration/setup phase (use migration mode flag)
- Provide bypass option for emergency repairs

---

### Task 5: Add Comprehensive Stock Mutation Audit Trail

**Priority:** MEDIUM  
**File:** New migration + new service

**Problem:** Currently, there's no comprehensive audit of which operations modified stock, making it hard to trace the source of inconsistencies.

**Implementation:**

Create new migration for audit table:

```sql
-- New table: inventory.stock_mutation_audit
CREATE TABLE inventory.stock_mutation_audit (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    location_id INT NOT NULL,
    operation VARCHAR(50) NOT NULL,  -- CREATE_BATCH, ALLOCATE, TRANSFER, etc.
    qty_delta NUMERIC(18,4) NOT NULL,
    user_id INT,
    ref_type VARCHAR(50),
    ref_id INT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_stock_mutation_audit_company 
    ON inventory.stock_mutation_audit (company_id, created_at);
CREATE INDEX ix_stock_mutation_audit_product 
    ON inventory.stock_mutation_audit (company_id, product_id, created_at);
```

Create service class:

```python
class StockMutationAuditService:
    """
    Service to audit all stock mutations for traceability.
    
    This helps identify which operations caused drift.
    """
    
    def log_mutation(
        self,
        company_id: int,
        product_id: int,
        variant_id: Optional[int],
        location_id: int,
        operation: str,
        qty_delta: Decimal,
        user_id: int,
        ref_type: str,
        ref_id: Optional[int],
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Log a stock mutation for audit purposes."""
        audit = StockMutationAudit(
            company_id=company_id,
            product_id=product_id,
            variant_id=variant_id,
            location_id=location_id,
            operation=operation,
            qty_delta=qty_delta,
            user_id=user_id,
            ref_type=ref_type,
            ref_id=ref_id,
            success=success,
            error_message=error_message,
        )
        self.db.add(audit)
        self.db.commit()
    
    def get_mutation_history(
        self,
        company_id: int,
        product_id: int,
        variant_id: Optional[int],
        location_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get mutation history for a specific stock record."""
        # Query stock_mutation_audit with filters
        pass
```

**Edge Cases:**
- Handle high-volume mutations (consider async logging)
- Ensure audit log doesn't become a performance bottleneck
- Clean up old audit logs based on retention policy

---

### Task 6: Enhanced Scheduled Job with Better Error Handling

**Priority:** MEDIUM  
**File:** `app/services/inventory/consistency_job.py`

**Problem:** Current job lacks proper error handling and notification for partial failures.

**Implementation:**

Enhance the job with:
1. Per-company error handling (don't fail all if one fails)
2. Exponential backoff for retries
3. Detailed failure reporting
4. Automatic notification on job failure

```python
class ConsistencyCheckJob:
    """Enhanced consistency check job with better error handling."""
    
    def run_consistency_check(self) -> Dict[str, Any]:
        """
        Run consistency check with enhanced error handling.
        
        IMPROVEMENTS:
        - Per-company error isolation
        - Retry logic for transient failures
        - Detailed failure reporting
        - Job health metrics
        """
        # ... existing logic ...
        
        company_failures = []
        
        for company in companies:
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    discrepancies = self._check_company(db, company)
                    # ... process results ...
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Final attempt failed
                        logger.error(
                            f"Consistency check failed for company {company.id} "
                            f"after {max_retries} attempts: {e}"
                        )
                        company_failures.append({
                            "company_id": company.id,
                            "company_name": company.company_name,
                            "error": str(e),
                            "attempts": max_retries,
                        })
                    else:
                        # Retry with exponential backoff
                        import time
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
        
        # ... existing logic ...
        
        # If any companies failed, send alert
        if company_failures:
            self._send_job_failure_notification(company_failures)
        
        return {
            "companies_checked": len(companies),
            "companies_succeeded": len(companies) - len(company_failures),
            "companies_failed": len(company_failures),
            "company_failures": company_failures,
            # ... existing fields ...
        }
```

---

### Task 7: Add Consistency Settings API

**Priority:** MEDIUM  
**File:** New file `app/api/inventory/settings.py` or extend existing

**Problem:** No API to manage consistency settings (strict mode, tolerance, etc.)

**Implementation:**

Create or extend existing endpoints for managing consistency settings:

```python
from fastapi import APIRouter, Depends
from app.schemas.inventory import CompanyInventorySettingUpdate

router = APIRouter(prefix="/inventory/settings", tags=["Inventory Settings"])

@router.get("/consistency")
async def get_consistency_settings(
    company_id: int = Depends(get_current_company_id),
    db: Session = Depends(get_db),
):
    """Get consistency settings for company."""
    setting_service = CompanyInventorySettingService(db)
    settings = setting_service.get_by_company(company_id)
    
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    return {
        "company_id": company_id,
        "batch_tracking_enabled": settings.batch_tracking_enabled,
        "valuation_mode": settings.valuation_mode,
        "strict_consistency_check": settings.strict_consistency_check,
        "auto_repair_on_violation": settings.auto_repair_on_violation,
        "consistency_tolerance": float(settings.consistency_tolerance),
        "check_interval_minutes": settings.check_interval_minutes,
    }

@router.patch("/consistency")
async def update_consistency_settings(
    settings_update: CompanyInventorySettingUpdate,
    company_id: int = Depends(get_current_company_id),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update consistency settings.
    
    Settings:
    - strict_consistency_check: Raise exception if invariant violated
    - consistency_tolerance: Allowable difference between batch and stock
    - check_interval_minutes: How often to run scheduled check
    
    Note: auto_repair_on_violation is reserved for future use.
    """
    setting_service = CompanyInventorySettingService(db)
    settings = setting_service.get_by_company(company_id)
    
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    # Update fields
    if settings_update.strict_consistency_check is not None:
        settings.strict_consistency_check = settings_update.strict_consistency_check
    
    if settings_update.consistency_tolerance is not None:
        settings.consistency_tolerance = settings_update.consistency_tolerance
    
    if settings_update.check_interval_minutes is not None:
        settings.check_interval_minutes = settings_update.check_interval_minutes
    
    # Note: auto_repair_on_violation should remain False (manual approval required)
    settings.mb = current_user.get("user_id", 1)
    
    db.commit()
    db.refresh(settings)
    
    return {"success": True, "message": "Settings updated"}
```

---

### Task 8: DSR Flow Consistency Verification

**Priority:** MEDIUM  
**File:** `app/services/inventory/inventory_sync_service.py` (new method)

**Problem:** DSR load/unload operations may cause inconsistencies as noted in deep dive.

**Implementation:**

Add DSR-specific consistency check:

```python
def verify_dsr_allocation_consistency(
    self,
    dsr_assignment_id: int,
) -> Dict[str, Any]:
    """
    Verify DSR allocations are consistent with batches.
    
    Checks:
    - No orphan allocations (batch deleted but allocation exists)
    - No over-allocations (allocation > batch.qty_on_hand)
    - Quantities match between allocation and batch
    """
    from app.models.sales import DSRBatchAllocation
    
    dsr_allocations = self.db.query(DSRBatchAllocation).filter(
        DSRBatchAllocation.assignment_id == dsr_assignment_id,
        DSRBatchAllocation.is_deleted == False,
    ).all()
    
    issues = []
    
    for alloc in dsr_allocations:
        batch = self.db.query(Batch).filter(
            Batch.batch_id == alloc.batch_id,
            Batch.is_deleted == False,
        ).first()
        
        # EDGE CASE: Orphan allocation (batch deleted)
        if not batch:
            issues.append({
                "type": "orphan_allocation",
                "allocation_id": alloc.dsr_allocation_id,
                "batch_id": alloc.batch_id,
                "message": "Batch no longer exists but allocation record remains",
            })
            continue
        
        # EDGE CASE: Over-allocation
        if alloc.qty_allocated > batch.qty_on_hand:
            issues.append({
                "type": "over_allocation",
                "allocation_id": alloc.dsr_allocation_id,
                "batch_id": alloc.batch_id,
                "allocated": float(alloc.qty_allocated),
                "available": float(batch.qty_on_hand),
                "message": "Allocated quantity exceeds available batch quantity",
            })
        
        # EDGE CASE: Quantity mismatch
        # (comparing allocated vs actual batch state)
    
    return {
        "assignment_id": dsr_assignment_id,
        "total_allocations": len(dsr_allocations),
        "issue_count": len(issues),
        "issues": issues,
        "is_consistent": len(issues) == 0,
    }
```

---

## Part C: Implementation Order

| Task | Priority | Dependencies | Estimated Effort |
|------|----------|--------------|------------------|
| Task 3: Edge Case Handling | HIGH | None | Medium |
| Task 1: Repair Suggestions | HIGH | Task 3 | Medium |
| Task 2: Enhanced Guard | HIGH | Task 1 | Medium |
| Task 4: Blocking Validation | HIGH | Task 2, Task 3 | Medium |
| Task 6: Job Enhancement | MEDIUM | Task 3 | Small |
| Task 7: Settings API | MEDIUM | None | Small |
| Task 5: Audit Trail | MEDIUM | None | Medium |
| Task 8: DSR Consistency | MEDIUM | None | Small |

---

## Part D: Testing Plan

### Unit Tests
- [ ] Test `verify_invariant` with NULL variants
- [ ] Test `verify_invariant` with soft-deleted records
- [ ] Test tolerance handling with Decimal precision
- [ ] Test repair action determination logic
- [ ] Test blocking validation in batch mode

### Integration Tests
- [ ] Test full repair workflow
- [ ] Test blocking validation in batch mode
- [ ] Test scheduled job with multiple companies
- [ ] Test edge cases from Phase 1 & 2 fixes
- [ ] Test DSR load → sale → unload consistency

### Manual Testing
- [ ] Enable strict mode and verify exceptions are raised
- [ ] Test partial failures in scheduled job
- [ ] Verify materialized views refresh correctly

---

## Part E: Rollback Strategy

If issues arise after implementation:

1. **Quick Rollback**: Disable strict mode via settings (no code change needed)
2. **Full Rollback**: 
   - Revert migrations (if new tables/columns added)
   - Set `batch_tracking_enabled = False` for affected companies

---

## Part F: Acceptance Criteria

After implementation:

1. ✅ All stock mutations go through consistency validation
2. ✅ Discrepancies provide actionable repair suggestions
3. ✅ NULL variant handling works correctly
4. ✅ Soft-deleted records excluded from checks
5. ✅ Manual stock operations blocked or warned in batch mode
6. ✅ Scheduled job handles failures gracefully
7. ✅ Settings API allows configuration management
8. ✅ DSR allocation consistency can be verified

---

## Part G: Files to Modify

| File | Changes |
|------|---------|
| `app/api/inventory/batch.py` | Add repair suggestions endpoint |
| `app/services/inventory/inventory_sync_service.py` | Enhance PostTransactionGuard, verify_invariant, add DSR check |
| `app/services/warehouse/warehouse.py` | Add batch mode validation to CRUD methods |
| `app/services/inventory/consistency_job.py` | Enhance error handling |
| `app/schemas/inventory/` | Add/update settings update schema |
| `alembic/versions/` | New migration for audit table (optional) |

---

## Part H: Open Questions for User

Before implementation, please clarify:

1. **Auto-repair**: Should the system automatically repair discrepancies when `auto_repair_on_violation=True`? Current code has the setting but doesn't use it. Recommendation: Keep it disabled (manual approval required).

2. **Blocking mode**: Should direct stock CRUD be completely blocked in strict mode, or just warn? Current plan suggests blocking, but may break existing workflows. Consider adding a "migration mode" flag.

3. **Audit volume**: The audit trail will generate significant records. Should we:
   - Keep all records indefinitely?
   - Use data expiration (e.g., 90 days)?
   - Make it optional per company?

4. **Trigger overhead**: The batch trigger is implemented. Should we add a stock trigger (Task 8 from deep dive)? This adds overhead to every stock operation.

5. **Database migrations**: The existing migrations (phase3_consistency_settings, phase3_materialized_views, phase3_batch_triggers) need to be applied. Do you want me to check if they're applied, or should we create new ones for the audit table?

---

*Document prepared based on deep analysis of INVENTORY_BATCH_SYNC_DEEP_DIVE.md and existing codebase.*
