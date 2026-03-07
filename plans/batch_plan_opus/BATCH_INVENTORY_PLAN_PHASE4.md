# Batch-Based Inventory Implementation Plan — Phase 4: Risks, Sprint Estimates, Operations & References

## 15. Risk Analysis & Mitigation

| # | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| 1 | **Concurrency → double allocation** | CRITICAL | Medium | `SELECT ... FOR UPDATE SKIP LOCKED`; short transactions; retry logic with max 3 retries; integration test proving no double allocation |
| 2 | **Long-running backfill blocks production** | HIGH | High | Run in chunks of 500; off-peak hours; use read replica for data gathering; dry-run mode first; feature flag to disable if issues |
| 3 | **Reports break (assumed product-level cost)** | HIGH | High | Existing reports (`reports.py`) derive cost from PO data. Add compatibility layer: if batch_tracking enabled → use movement ledger; else → use legacy PO cost. Both live in parallel during transition |
| 4 | **Incorrect historical costs after backfill** | MEDIUM | Medium | Mark synthetic batches with `is_synthetic=TRUE`; flag reports based on synthetic data; provide reconciliation CSV for manual review of estimated costs |
| 5 | **Negative qty_on_hand** | HIGH | Low | DB CHECK constraint (`qty_on_hand >= 0`); service-layer validation; reconciliation alerts; if triggered → freeze allocations and investigate |
| 6 | **Feature flag inconsistency** | LOW | Low | `company_inventory_setting` cached at request scope; settings change requires page refresh; no mid-request flag changes |
| 7 | **Large movement table slows reports** | MEDIUM | Medium (long-term) | Partition by `txn_timestamp` (monthly); materialized views for aggregate reports; run heavy reports off read replica |
| 8 | **Existing tests fail after service modifications** | MEDIUM | Medium | Run full test suite after each service modification; add feature-flag bypass in existing tests to preserve legacy behavior |
| 9 | **DSR stock not integrated with batches** | LOW | N/A | Phase 3 scope — documented as future work; DSR operations continue in legacy mode until batch integration |

---

## 16. Sprint / Task Breakdown

### Sprint 1 — Foundation (2 weeks, ~40 story points)

| Ticket | Title | Description | Acceptance Criteria | Estimate |
|---|---|---|---|---|
| S1-01 | Create DB migration for batch tables | Alembic migration: `inventory.batch`, `inventory.inventory_movement`, `settings.company_inventory_setting`, `sales.sales_order_batch_allocation`. Add `cogs_amount` to `billing.invoice_detail`. | Tables created; migration up/down works; indexes verified | 5 SP |
| S1-02 | Create Batch model + repository | SQLAlchemy model `Batch` in `app/models/inventory.py`; `BatchRepository` in `app/repositories/inventory/batch_repository.py`; CRUD operations | Unit tests pass for CRUD | 5 SP |
| S1-03 | Create InventoryMovement model + repository | SQLAlchemy model `InventoryMovement`; `InventoryMovementRepository`; list/create/query operations | Unit tests pass | 5 SP |
| S1-04 | Create CompanyInventorySetting model + service | Model, repository, service for company-level valuation mode and feature flag | Setting CRUD works; default FIFO, batch_tracking=FALSE | 3 SP |
| S1-05 | Create Batch schemas (Pydantic) | Create, Update, Response schemas for Batch, Movement, Allocation | Validates correctly; serialization works | 3 SP |
| S1-06 | Create BatchService | Service with CRUD, cost immutability enforcement, status management | Cost edit blocked when OUT movements exist; returns 409 | 5 SP |
| S1-07 | Create InventoryMovementService | Service to create movements, immutability enforcement, ledger queries | Movements created correctly; no update/delete allowed | 5 SP |
| S1-08 | Create Batch allocation service (FIFO) | `BatchAllocationService.allocate()` with FIFO, row-level locks, retry logic | FIFO allocation correct; concurrent test passes | 8 SP |
| S1-09 | Unit tests for Sprint 1 | Test allocation (FIFO single/multi batch, insufficient stock, concurrent), cost immutability, movement creation | All tests pass; coverage > 80% for new code | 5 SP |

### Sprint 2 — Integration (2 weeks, ~35 story points)

| Ticket | Title | Description | Acceptance Criteria | Estimate |
|---|---|---|---|---|
| S2-01 | Integrate batch creation in PO delivery | Modify `ProductOrderDeliveryDetailService.create_delivery_detail()` to create batch + IN movement when `batch_tracking_enabled` | PO delivery creates batch; movement recorded; legacy mode unaffected | 8 SP |
| S2-02 | Integrate batch allocation in SO delivery | Modify `SalesOrderDeliveryDetailService.create_delivery_detail()` to call allocation service when `batch_tracking_enabled` | SO delivery allocates from batches; COGS recorded; legacy mode unaffected | 8 SP |
| S2-03 | Implement sales return with batch traceability | Return logic: restore to original batch or create synthetic; RETURN_IN movement with `related_movement_id` | Return restores batch qty; audit chain preserved | 5 SP |
| S2-04 | Integrate adjustments with movements | Modify `InventoryAdjustmentService` to create movements with cost on adjustments | Adjustment creates movement; cost recorded from `AdjustmentDetail.unit_cost` | 5 SP |
| S2-05 | Integrate stock transfers with movements | Modify `StockTransfer` service to create paired TRANSFER_OUT/TRANSFER_IN movements | Transfer creates 2 movements; batch identity preserved | 5 SP |
| S2-06 | Batch API endpoints | Create `batch_router`, `movement_router`, `allocation_router` with all endpoints from spec | All endpoints return correct data; RBAC enforced | 5 SP |
| S2-07 | Integration tests for Sprint 2 | Full cycle: PO → batch → SO → allocation → return → verify ledger | All integration tests pass | 5 SP |

### Sprint 3 — LIFO/WAC & Backfill (2 weeks, ~30 story points)

| Ticket | Title | Description | Acceptance Criteria | Estimate |
|---|---|---|---|---|
| S3-01 | Add LIFO allocation mode | Implement LIFO ordering in allocation service | LIFO allocates newest batches first; tests pass | 3 SP |
| S3-02 | Add Weighted Average allocation mode | Implement WAC with averaged cost; SERIALIZABLE isolation | WAC computes correct avg cost; concurrent test passes | 5 SP |
| S3-03 | Build backfill script | Script to create synthetic batches from PO history; idempotent; dry-run mode; reconciliation CSV output | Dry-run shows zero mismatches for test data; production run is idempotent | 8 SP |
| S3-04 | Reconciliation tooling | Query to compare batch totals vs inventory_stock; export CSV; alert on mismatches | Reconciliation report exports correctly; mismatches flagged | 3 SP |
| S3-05 | Update existing reports | Modify `ReportsService` methods to use movement ledger when batch_tracking enabled; compatibility layer for legacy mode | Reports show correct data in both modes; no regression | 5 SP |
| S3-06 | New batch-based report endpoints | Stock-by-batch, COGS by period, margin analysis, batch P&L, inventory aging from batches | All report endpoints return correct data | 5 SP |
| S3-07 | Migration + backfill tests | Test backfill dry-run, idempotency, reconciliation accuracy | All tests pass; zero reconciliation mismatches | 3 SP |

### Sprint 4 — Frontend (2 weeks, ~30 story points)

| Ticket | Title | Description | Acceptance Criteria | Estimate |
|---|---|---|---|---|
| S4-01 | Batch Drill-Down page | New page with batch table, filters, pagination, export CSV, cost lock indicator | Page renders correctly; filters work; RBAC enforced |  8 SP |
| S4-02 | Movement Ledger page | New page with movement table, filters, color-coded badges, linked references | Page renders correctly; ref links navigate to source |  5 SP |
| S4-03 | SO batch allocations view | Add read-only allocation table + COGS line to SO detail page | Allocations display correctly after delivery |  3 SP |
| S4-04 | PO batch creation indicator | Add batch created badge to PO delivery detail | Badge shows with link to batch drill-down |  2 SP |
| S4-05 | Company settings — valuation mode | Add valuation mode dropdown + batch tracking toggle to settings | Settings save and load correctly; warning on change |  3 SP |
| S4-06 | Batch report pages (5 reports) | Stock-by-batch, inventory aging, COGS by period, margin analysis, batch P&L | All reports render correctly with data | 8 SP |
| S4-07 | Update product stock view | Show avg cost, total stock from batches; "View Batches" button | Totals match; drill-down navigates correctly | 3 SP |

### Sprint 5 — Rollout & Hardening (1 week, ~15 story points)

| Ticket | Title | Description | Acceptance Criteria | Estimate |
|---|---|---|---|---|
| S5-01 | Register new screens in security system | Insert screen records for all new pages; configure default permissions | Screens accessible per RBAC; menu items visible |  3 SP |
| S5-02 | Staging deployment & validation | Deploy to staging; run backfill dry-run; full validation checklist | All checklist items pass |  5 SP |
| S5-03 | Production backfill for pilot company | Run backfill; verify reconciliation; enable batch_tracking | Zero mismatches; feature works end-to-end |  3 SP |
| S5-04 | Monitoring & alerting setup | Configure metrics, alerts, reconciliation cron job | Alerts fire correctly on test triggers |  3 SP |
| S5-05 | Documentation & runbooks | Update architecture docs; create reconciliation runbook; update user manual | Docs reviewed and approved |  2 SP |

### Summary

| Sprint | Duration | Story Points | Theme |
|---|---|---|---|
| Sprint 1 | 2 weeks | ~40 SP | Foundation: models, repos, services, allocation |
| Sprint 2 | 2 weeks | ~35 SP | Integration: PO/SO/return/adjustment/transfer |
| Sprint 3 | 2 weeks | ~30 SP | LIFO/WAC, backfill, reports |
| Sprint 4 | 2 weeks | ~30 SP | Frontend: pages, reports, settings |
| Sprint 5 | 1 week | ~15 SP | Rollout, monitoring, docs |
| **Total** | **~9 weeks** | **~150 SP** | |

### MVP vs Optional

| Feature | Priority | Sprint |
|---|---|---|
| Batch model + FIFO allocation | **MVP** | S1 |
| Movement ledger | **MVP** | S1 |
| PO/SO integration | **MVP** | S2 |
| Returns with traceability | **MVP** | S2 |
| LIFO allocation | **Optional** | S3 |
| Weighted Average allocation | **Optional** | S3 |
| Backfill script | **MVP** | S3 |
| Batch drill-down UI | **MVP** | S4 |
| Movement ledger UI | **MVP** | S4 |
| COGS/Margin reports | **MVP** | S4 |
| Batch P&L report | **Optional** | S4 |
| Multicurrency exchange rate table | **Deferred** | Future |
| DSR batch integration | **Optional** | Phase 3 |
| Table partitioning | **Optional** | As needed |

---

## 17. Missing Information / Credentials Needed

| Item | Status | Impact |
|---|---|---|
| Database access for dry-run testing | ❌ Not available | Cannot validate backfill script against real data |
| Staging environment credentials | ❌ Not available | Cannot perform staging deployment |
| Accounting export format | ❓ Unknown | Need to confirm COGS field mapping for any accounting software integration |

---

## 18. References

### PostgreSQL
- [Row-level locking & FOR UPDATE SKIP LOCKED](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

### Accounting Concepts
- **FIFO (First-In, First-Out)**: Oldest inventory sold first; COGS reflects earliest purchase costs
- **LIFO (Last-In, First-Out)**: Newest inventory sold first; COGS reflects most recent purchase costs
- **Weighted Average**: COGS = average cost across all available units

### Architecture Patterns
- **Journal-style ledger**: Append-only, immutable records. Corrections via offsetting entries.
- **Materialized views**: Pre-computed aggregates for reporting performance.
- **Feature flags**: Per-tenant configuration enabling gradual rollout.
- **CQRS**: Separate write (movement ledger) and read (aggregated views) paths for performance.

### Existing Shoudagor Documentation
- [app_architecture_documentation.md](file:///c:/Users/Shofiq/Documents/0%20work/Shoudagor_Fullstack/Shoudagor/app_architecture_documentation.md) — Architecture layers
- [inventory_stock_management_study.md](file:///c:/Users/Shofiq/Documents/0%20work/Shoudagor_Fullstack/Shoudagor/inventory_stock_management_study.md) — Current stock management flows
- [SALES_ORDER_WORKFLOW_ANALYSIS.md](file:///c:/Users/Shofiq/Documents/0%20work/Shoudagor_Fullstack/SALES_ORDER_WORKFLOW_ANALYSIS.md) — Current SO workflow
- [PURCHASE_ORDER_WORKFLOW_ANALYSIS.md](file:///c:/Users/Shofiq/Documents/0%20work/Shoudagor_Fullstack/PURCHASE_ORDER_WORKFLOW_ANALYSIS.md) — Current PO workflow

---

## Document Index

| Phase | File | Contents |
|---|---|---|
| Phase 1 | `BATCH_INVENTORY_PLAN_PHASE1.md` | Executive summary, ERD, SQL migrations, sequence diagrams, allocation algorithms |
| Phase 2 | `BATCH_INVENTORY_PLAN_PHASE2.md` | API spec, backend services, backfill strategy, test plan, acceptance scenarios |
| Phase 3 | `BATCH_INVENTORY_PLAN_PHASE3.md` | UI/UX components, system safeguards, rollout plan, operations, performance |
| Phase 4 | `BATCH_INVENTORY_PLAN_PHASE4.md` | Risk analysis, sprint estimates, missing info, references |
