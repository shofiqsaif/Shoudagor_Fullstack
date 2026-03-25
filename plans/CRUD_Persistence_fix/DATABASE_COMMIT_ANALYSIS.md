# Database Commit Analysis - Shoudagor ERP

> **Date:** 2026-03-24  
> **Project:** Shoudagor Fullstack  
> **Issue:** Inventory settings API returns success but data not persisted to database  

---

## Executive Summary

The investigation revealed that multiple API endpoints in the Shoudagor backend fail to persist data to the database because they call `flush()` without `commit()`. This is a critical issue affecting data integrity across the system.

**Root Cause:** Database session configured with `autocommit=False` requires explicit commits.

---

## 1. Technical Background

### 1.1 Database Configuration

**File:** `Shoudagor/app/core/database.py` (Line 21)

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

| Parameter | Value | Implication |
|-----------|-------|-------------|
| `autocommit` | `False` | Every transaction must be explicitly committed |
| `autoflush` | `False` | Session won't auto-flush before queries |

### 1.2 Flush vs Commit

| Operation | What it does | Persistence |
|-----------|--------------|-------------|
| `flush()` | Synchronizes changes to DB within transaction | Changes visible in DB but not committed |
| `commit()` | Finalizes transaction, makes changes permanent | Changes survive connection close |
| `rollback()` | Reverts all uncommitted changes | Changes lost |

**Critical Issue:** When a connection returns to the pool, uncommitted transactions are automatically rolled back.

---

## 2. Investigation Findings

### 2.1 Codebase Statistics

| Category | Count |
|----------|-------|
| Repository methods using `flush()` | 146+ |
| Service methods using `flush()` | 28 |
| API endpoints calling `db.commit()` manually | 8 |
| Service methods calling `commit()` | 197 |

### 2.2 Confirmed Broken Endpoints

| # | Endpoint | Method | File | Lines | Status |
|---|----------|--------|------|-------|--------|
| 1 | `POST /api/company/inventory/settings/` | Create/Update settings | `app/api/inventory/batch.py` | 619-659 | **FIXED** |
| 2 | `POST /api/company/inventory/batches/` | Create batch | `app/api/inventory/batch.py` | 88-177 | **BROKEN** |
| 3 | `PATCH /api/company/inventory/batches/{id}` | Update batch | `app/api/inventory/batch.py` | 525-600 | **BROKEN** |
| 4 | `POST /api/company/inventory/movements/` | Create movement | `app/api/inventory/inventory_movement.py` | 107-196 | **BROKEN** |

### 2.3 Why They Appear to Work

1. `flush()` makes changes visible within the transaction
2. API returns 201 Created with the "saved" data
3. When request ends and connection returns to pool → **automatic rollback**
4. User sees success, but data never persisted

---

## 3. Detailed Code Analysis

### 3.1 Example: Settings Endpoint (Now Fixed)

**File:** `app/api/inventory/batch.py` (Lines 619-659)

```python
@settings_router.post("/", response_model=CompanyInventorySettingResponse)
def create_company_inventory_setting(
    setting_data: CompanyInventorySettingCreate,
    db: Session = Depends(get_db),
    ...
):
    setting_repo = CompanyInventorySettingRepository(db)
    setting = setting_repo.create_or_update(...)  # Only flush, no commit
    return CompanyInventorySettingResponse(...)
```

**Repository Code:** `app/repositories/inventory/batch.py` (Lines 1044-1072)

```python
def create_or_update(self, ...):
    setting = self.get_by_company(company_id)
    if setting:
        setting.valuation_mode = valuation_mode
        setting.batch_tracking_enabled = batch_tracking_enabled
        setting.mb = user_id
        setting.md = func.now()
    else:
        setting = CompanyInventorySetting(...)
        self.db.add(setting)
    
    self.db.flush()        # ❌ Missing commit
    self.db.refresh(setting)
    return setting
```

**Fix Applied:**
```python
self.db.flush()
self.db.commit()           # ✅ Added
self.db.refresh(setting)
return setting
```

### 3.2 Example: Batch Creation Endpoint (Broken)

**File:** `app/api/inventory/batch.py` (Lines 88-177)

```python
batch_repo = BatchRepository(db)
created_batch = batch_repo.create(batch)  # flush() only

movement_repo = InventoryMovementRepository(db)
movement_repo.create_movement(...)       # flush() only

# ❌ No db.commit() - changes rolled back
```

**Repository Method:** `app/repositories/inventory/batch.py` (Lines 112-117)

```python
def create(self, batch_obj: Batch) -> Batch:
    self.db.add(batch_obj)
    self.db.flush()       # ❌ No commit
    self.db.refresh(batch_obj)
    return batch_obj
```

---

## 4. Call Flow Analysis

### 4.1 Correct Pattern (Service Layer)

```
API → Service → Repository → (flush + commit) → DB
```

Example: `app/services/claims/claim_service.py`
- Calls `self.repo.db.flush()` for intermediate writes
- Later calls `self.repo.db.commit()` to finalize

### 4.2 Broken Pattern (Direct Repository)

```
API → Repository → (flush only) → DB → ❌ Rollback
```

Example: `app/api/inventory/batch.py:create_batch()`
- Calls `batch_repo.create()` (flush only)
- Calls `movement_repo.create_movement()` (flush only)
- Returns success
- Connection returns to pool → **Rollback**

---

## 5. Recommended Solution

### 5.1 Option A: Fix at Repository Level (Recommended)

**Pros:**
- Single fix covers all API endpoints using repositories
- Consistent behavior across codebase

**Cons:**
- Could cause double-commit if service also commits

**Implementation:**
Add `self.db.commit()` after `self.db.flush()` in repository methods that are typically called from API endpoints.

### 5.2 Option B: Fix at API Level

**Pros:**
- Surgical fix per endpoint
- No risk of double-commit

**Cons:**
- Must update each endpoint individually
- Higher chance of missing some

**Implementation:**
Add `db.commit()` after repository calls in each problematic endpoint.

### 5.3 Option C: Fix at Service Layer

**Pros:**
- Proper architectural approach
- Services handle transactions

**Cons:**
- Requires significant refactoring
- Not all operations go through services

---

## 6. Implementation Plan

### Phase 1: Immediate Fixes (High Priority)

| Priority | Action | Files |
|----------|--------|-------|
| ✅ Done | Fix settings endpoint commit | `app/repositories/inventory/batch.py` |
| 🔄 Next | Add commit to batch creation | `app/api/inventory/batch.py` |
| 🔄 Next | Add commit to batch update | `app/api/inventory/batch.py` |
| 🔄 Next | Add commit to movement creation | `app/api/inventory/inventory_movement.py` |

### Phase 2: Audit Repository Methods

Review and fix repository methods that use `flush()` without clear commit ownership:

| Repository | Methods to Audit |
|------------|-----------------|
| `app/repositories/inventory/batch.py` | `create()`, `update()`, `delete()`, `create_movement()`, `decrement_qty()`, etc. |
| `app/repositories/warehouse/*` | Stock transfers, inventory stock methods |
| `app/repositories/sales/*` | Sales order, delivery, payment details |
| `app/repositories/procurement/*` | Purchase orders, delivery details |

### Phase 3: Standardization

1. **Document commit expectations** in repository method docstrings
2. **Create base repository** with consistent commit pattern
3. **Add integration tests** for critical write operations

---

## 7. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Double-commit | Data saved twice, potential locking | Low | Review each fix individually |
| Missing commits | Data loss | High | Comprehensive audit |
| Performance (extra commits) | Slight overhead | Low | Commits are necessary anyway |

---

## 8. Test Plan

### Manual Testing
1. POST to `/api/company/inventory/settings/` with new values
2. GET the same endpoint - verify values persist
3. Check database directly: `SELECT * FROM inventory.company_inventory_setting`

### Automated Testing
1. Add integration tests for each broken endpoint
2. Verify data exists in DB after API call
3. Test rollback scenarios

---

## 9. Files to Modify

### Fixed
- `Shoudagor/app/repositories/inventory/batch.py` (Line 1070-1072)

### Pending Fixes
- `Shoudagor/app/api/inventory/batch.py` (Add commit after batch operations)
- `Shoudagor/app/api/inventory/inventory_movement.py` (Add commit after movement creation)
- Other repositories as identified in audit

---

## 10. Conclusion

The issue stems from inconsistent commit patterns between API endpoints and repositories. The database session requires explicit commits, but many endpoints only flush and return success. The fix requires either:
1. Adding commits to repository methods
2. Adding commits to API endpoints after repository calls

Both approaches are valid; the choice depends on architectural preferences. The investigation identified at least 4 broken endpoints that return success but don't persist data.

---

*Document created as part of issue investigation for Shoudagor ERP system.*