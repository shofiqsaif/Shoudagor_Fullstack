Phase 4: Migration and Backfill - Gap Fix Implementation Plan

  This document outlines the strategy for resolving identified bugs, integrating missing components, and implementing
  placeholders in the Phase 4 Migration workflow.

---

1. Analysis & Context

  The Phase 4 implementation provides the core infrastructure for migrating companies to batch tracking. However,
  critical gaps in the locking mechanism, DSR integration, and pre-migration checks currently compromise the reliability
  and safety of the workflow.

  Identified Gaps:

1. Broken Migration Lock: The filter is_locked == True in _get_active_migration prevents the system from finding a
   newly created migration record to lock it. This renders the "Migration Lock" ineffective, allowing concurrent
   stock operations during migration.
2. Advisory Lock Scope: Transaction-level advisory locks are released on commit(). Since start_migration performs
   multiple commits, the physical DB lock is lost before the migration truly begins.
3. DSR Integration: handle_dsr_inventory_migration contains a NameError (undefined user_id) and is not invoked in the
   main _execute_migration_steps flow.
4. Placeholder Logic: check_pending_stock_operations and _check_uom_consistency are currently empty stubs, failing to
   detect potential data conflicts.

---

2. Technical Strategy

  The strategy focuses on making the migration "Atomic and Guarded" by fixing the locking lifecycle and ensuring all
  inventory storage types (including DSR) are covered.

  Key Architectural Changes:

* State-Aware Locking: Transition from "filtering by lock" to "status-based identification" for active migrations.
* Session-Level Advisory Locks: Utilize pg_try_advisory_lock for locks that persist across transaction boundaries
  within the same session.
* Unified Execution Flow: Integrate DSR and UOM checks into the standard migration pipeline.

---

3. Step-by-Step Implementation Plan

  Step 1: Repair the Locking Mechanism
  File: Shoudagor/app/services/inventory/inventory_migration_service.py

1. Modify _get_active_migration:
   * Change the filter to look for any migration with status PENDING, IN_PROGRESS, or VERIFYING.
   * Remove InventoryMigration.is_locked == True from the initial query filter.
2. Modify acquire_migration_lock:
   * Change pg_try_advisory_xact_lock to pg_try_advisory_lock.
   * Update the logic to set is_locked = True on the migration record once the advisory lock is acquired.

  Step 2: Fix and Integrate DSR Migration
  File: Shoudagor/app/services/inventory/inventory_migration_service.py

1. Update handle_dsr_inventory_migration:
   * Change signature to handle_dsr_inventory_migration(self, company_id: int, user_id: int).
   * Pass user_id to the Batch creation logic.
2. Update _execute_migration_steps:
   * Add a new step: self._run_dsr_migration(migration, dry_run).
   * This step will call handle_dsr_inventory_migration and wrap it in a MigrationStepResult.

  Step 3: Implement Pre-Migration Guard Logic
  File: Shoudagor/app/services/inventory/inventory_migration_service.py

1. Implement check_pending_stock_operations:
   * Query inventory.inventory_adjustment for status NOT IN ('posted', 'cancelled').
   * Query transaction.stock_transfer for status NOT IN ('completed', 'cancelled').
   * Return a list of PendingOperation objects to warn the user.
2. Implement _check_uom_consistency:
   * Verify all inventory_stock records for the company have a valid uom_id that matches the product's base_uom_id.

  Step 4: Harden Rollback Procedures
  File: Shoudagor/app/services/inventory/inventory_migration_service.py

1. Update rollback_migration:
   * Add a timestamp filter: Batch.cd >= migration.started_at.
   * Add a verification check to ensure only is_synthetic=True batches are targeted.

---

4. Anticipated Risks

* Session Stickiness: Session-level advisory locks require the same database connection. In a pooled environment
  (like FastAPI with SQLAlchemy), we must ensure the lock is explicitly released or the session is handled carefully
  to avoid "leaked" locks.
* DSR Data Drift: Migrating DSR stock as "Synthetic Batches" assumes the DSR storage total is correct. If DSR stock
  was already out of sync with physical reality, the migration will carry that error forward.
* Alembic Conflicts: If other developers modify the inventory_migration table schema, migrations must be re-synced.

---

5. Next Steps
6. User Approval: Confirm that this gap-fix plan aligns with the architectural requirements.
7. Surgical Fixes: Apply the code changes to inventory_migration_service.py.
8. Verification: Run a "Dry Run" migration via the /api/inventory/batch/migration/pre-check and start-migration
   endpoints.
9. Unit Tests: Add test cases specifically for the locking bug and the DSR user_id fix.
