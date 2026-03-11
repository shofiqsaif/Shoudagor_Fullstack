# Phase 4: Migration and Backfill - Gap Fix Implementation Plan

This document outlines the strategy for resolving identified bugs, integrating missing components, and implementing placeholders in the Phase 4 Migration workflow.

---

## 1. Analysis & Context

The Phase 4 implementation provides the core infrastructure for migrating companies to batch tracking. However, critical gaps in the locking mechanism, DSR integration, and pre-migration checks currently compromise the reliability and safety of the workflow.

### Identified Gaps:
1.  **Broken Migration Lock**: The filter `is_locked == True` in `_get_active_migration` prevented the system from finding a newly created migration record to lock it.
2.  **Advisory Lock Scope**: Transaction-level advisory locks were released on `commit()`, causing the lock to be lost during the multi-commit migration process.
3.  **DSR Integration**: `handle_dsr_inventory_migration` contained a `NameError` and was not invoked in the main execution flow.
4.  **Placeholder Logic**: `check_pending_stock_operations` and `_check_uom_consistency` were empty stubs.

---

## 2. Technical Strategy

The strategy focuses on making the migration "Atomic and Guarded" by fixing the locking lifecycle and ensuring all inventory storage types (including DSR) are covered.

### Key Architectural Changes:
*   **State-Aware Locking**: Transitioned from "filtering by lock" to "status-based identification" for active migrations.
*   **Session-Level Advisory Locks**: Utilized `pg_try_advisory_lock` for locks that persist across transaction boundaries.
*   **Unified Execution Flow**: Integrated DSR and UOM checks into the standard migration pipeline.

---

## 3. Implementation Details

### Step 1: Repair the Locking Mechanism
- **File**: `Shoudagor/app/services/inventory/inventory_migration_service.py`
- Removed `is_locked == True` filter from `_get_active_migration`.
- Switched to `pg_try_advisory_lock` (session-level).
- Added explicit `pg_advisory_unlock` in `release_migration_lock`.

### Step 2: Fix and Integrate DSR Migration
- Updated `handle_dsr_inventory_migration` to accept `user_id`.
- Added `_run_dsr_migration` helper to the service.
- Integrated DSR migration into `_execute_migration_steps` for `FULL_BACKFILL`.

### Step 3: Implement Pre-Migration Guard Logic
- **`check_pending_stock_operations`**: Now queries for unposted `InventoryAdjustment` and incomplete `StockTransfer`.
- **`_check_uom_consistency`**: Now verifies that all products have a `base_uom_id`.

### Step 4: Harden Rollback Procedures
- Updated `rollback_migration` to use `started_at` timestamp and `is_synthetic=True` flags to prevent accidental data loss of non-migration batches.

---

## 4. Verification Results

- [x] Locking bug fixed (Lock now persists across commits).
- [x] DSR Migration integrated (User ID error resolved).
- [x] Pre-checks functional (Pending ops detected).
- [x] Rollback safety improved.
