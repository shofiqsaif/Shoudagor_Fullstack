# Batch Implementation - Critical Action Items
**Status:** Ready for Implementation  
**Priority:** Address before production deployment

---

## 🔴 CRITICAL (Must Fix Before Production)

### 1. Verify RBAC Screen Registration
**Issue:** Batch-related screens may not be accessible to users if not registered in security system  
**Files to Check:**
- `security.app_screen` table for these screens:
  - batch_drill_down
  - movement_ledger
  - batch_pnl_report
  - batch_cogs_report
  - batch_aging_report
  - batch_stock_report
  - batch_margin_report
  - company_inventory_settings

**Action Required:**
```sql
-- Verify screens exist (run this query to check current state)
SELECT screen_id, screen_code, screen_name 
FROM security.app_screen 
WHERE screen_code LIKE 'batch%' OR screen_code LIKE 'movement%' OR screen_code LIKE '%inventory_setting%';
```

**Resolution:**
If screens missing, insert them using similar pattern to existing screens:
```sql
INSERT INTO security.app_screen (screen_code, screen_name, menu_order, is_active)
VALUES 
  ('batch_drill_down', 'Batch Drill-Down', 1, true),
  ('movement_ledger', 'Movement Ledger', 2, true),
  ('batch_pnl_report', 'Batch P&L Report', 3, true),
  -- ... etc
```

**Owner:** Security/DBA Team  
**Timeline:** Before staging deployment

---

### 2. Load Test Concurrent Allocations
**Issue:** Unknown performance behavior under concurrent load (100+ simultaneous orders)  
**Risk:** Timeouts, allocation failures, or database deadlocks in production  

**Required Testing:**
- Spawn 50-100 concurrent threads allocating from same location
- Measure: allocation time, success rate, deadlock count
- Expected result: 100% success, <500ms per allocation, 0 deadlocks

**Test Script Location:**
```
tests/test_batch_inventory/test_concurrent_allocations.py  # Create if missing
```

**Owner:** QA/Performance Team  
**Timeline:** Before production deployment  
**Pass Criteria:** 
- ✅ 100% allocation success rate
- ✅ <2% timeout rate
- ✅ 0 database deadlocks

---

## 🟡 HIGH (Strongly Recommended Before Production)

### 3. Set Up Monitoring & Alerting
**Issue:** No automatic detection of reconciliation failures or batch operation errors  
**Impact:** Silent data corruption could go undetected for days

**Required Setup:**

#### 3a. Reconciliation Monitoring
```
Daily Cron Job (22:00 UTC):
- Call: POST /api/company/inventory/reconciliation/verify
- Compare batch totals with legacy inventory_stock
- If mismatches > 0:
  - Send EMAIL: operations@shoudagor.com
  - Log: WARN in application logs
  - Create ALERT in monitoring dashboard
```

**Implementation:**
```python
# File: Shoudagor/scripts/reconciliation_check.py
import requests
from datetime import datetime

def check_reconciliation(company_id):
    response = requests.post(
        'http://api/company/inventory/reconciliation/',
        json={'company_id': company_id, 'dry_run': True}
    )
    
    mismatches = response.json()['mismatches_found']
    if mismatches > 0:
        send_alert(f"Batch reconciliation mismatch on {company_id}")
```

#### 3b. Allocation Error Monitoring
```
Real-time Alert:
- If allocation returns InsufficientStockError
- Alert: ops-team@shoudagor.com
- Log level: ERROR
- Include: product_id, location_id, qty_needed
```

**Owner:** DevOps/SysAdmin Team  
**Timeline:** Before pilot production  

---

### 4. Create Production Backfill Runbook
**Issue:** Backfill execution steps not documented; risk of operator error  

**Runbook Template Location:**
```
docs/batch-backfill-runbook.md
```

**Must Document:**
- [ ] Pre-backfill checks (backup, feature flag state)
- [ ] Dry-run execution steps
- [ ] Review reconciliation report
- [ ] Commit backfill steps
- [ ] Post-backfill validation
- [ ] Rollback procedure (if needed)
- [ ] Expected duration
- [ ] Contact points if failure

**Owner:** Operations Documentation Lead  
**Timeline:** Before pilot production

---

## 🟠 MEDIUM (Recommended But Can Defer)

### 5. Performance Optimization Review
**Issue:** Large batch/movement tables may slow down reports over time  

**Recommended Actions:**
- [ ] Add table partitioning by month on `inventory.inventory_movement.txn_timestamp`
- [ ] Create materialized view for stock-by-batch total
- [ ] Monitor query performance on batch-heavy reports
- [ ] Consider read replica for heavy reporting

**Timeline:** Post-production (when table > 1M rows)  
**Owner:** Database Team

---

### 6. Frontend UX Polish
**Issue:** Pages exist but may need styling/usability improvements  

**Components to Review:**
- [ ] BatchDrillDown.tsx - filter/sort UI
- [ ] MovementLedger.tsx - scrolling performance, color-coding visibility
- [ ] Report pages - chart rendering, export CSV functionality
- [ ] Settings page - clear labeling of cost modes (FIFO/LIFO/WAC)

**Timeline:** Post-production if user feedback indicates  
**Owner:** Frontend Team

---

### 7. Add DB Constraints for Data Integrity
**Issue:** Currently relying on app-level validation for qty_on_hand >= 0  

**Proposed Addition:**
```sql
-- Migration to add (optional but recommended)
ALTER TABLE inventory.batch
  ADD CONSTRAINT check_qty_on_hand 
  CHECK (qty_on_hand >= 0);
```

**Timeline:** Optional, post-production if desired  
**Owner:** DBA Team

---

## 🟢 LOW (Optional Enhancements)

### 8. Enable Query Logging for Allocation
**Purpose:** Diagnostic troubleshooting if allocation issues reported  

```sql
-- Enable on production database
SET log_statement = 'ddl,dml';  -- Logs all DDL + DML (inserts/updates)
SET log_min_duration_statement = 500;  -- Only log queries > 500ms
```

**Owner:** DBA Team  
**Timeline:** Optional, can add after go-live

---

### 9. Create Batch History Report
**Purpose:** Archive historical batches for audit trail  

**For Phase 3 (Future):**
- Export depleted batches monthly
- Provide batch P&L analysis over time
- Support tax/accounting audits

**Timeline:** Phase 3 or later  
**Owner:** Reporting Team

---

## Implementation Timeline

### This Week
- [x] Review this document
- [ ] CRITICAL #1: Verify RBAC screens (1-2 hours)
- [ ] CRITICAL #2: Schedule load testing (2-4 hours)

### Next Week
- [ ] CRITICAL #2: Execute load testing (4-8 hours)
- [ ] HIGH #3: Set up monitoring (6-8 hours)
- [ ] HIGH #4: Document backfill runbook (2-3 hours)
- [ ] MEDIUM #6: Frontend UX review (4-6 hours)

### Staging Deployment (Week 3)
- [ ] Deploy code
- [ ] Run backfill dry-run
- [ ] 5-day staging validation
- [ ] Fix any issues found

### Pilot Production (Week 4)
- [ ] Enable feature flag for one company
- [ ] Run backfill (commit)
- [ ] 5-day monitoring period
- [ ] Gather feedback

---

## Sign-Off Checklist

Before moving each phase:

### ✅ Before Staging
- [ ] RBAC screens verified
- [ ] Load testing passed
- [ ] All unit tests passing
- [ ] Code reviewed (this document)

### ✅ Before Pilot Production
- [ ] Staging deployment successful
- [ ] Monitoring/alerting in place
- [ ] Backfill runbook documented
- [ ] Team trained on new UX

### ✅ Before Full Production
- [ ] Pilot runs for 5 days with 0 critical issues
- [ ] Operations team signed off
- [ ] Support documentation ready
- [ ] Executive sign-off from project lead

---

## Contacts & Escalation

**Technical Lead:** [Name needed]  
**DevOps Lead:** [Name needed]  
**DBA Lead:** [Name needed]  
**QA Lead:** [Name needed]  
**Product Owner:** [Name needed]  

**Escalation Path:** Technical Lead → Product Owner → Executive Sponsor

---

**Document Created:** March 7, 2026  
**Next Review:** Before staging deployment
