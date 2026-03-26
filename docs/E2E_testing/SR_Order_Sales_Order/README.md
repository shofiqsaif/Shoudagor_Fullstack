# SR Order to Sales Order Lifecycle - Testing Documentation Index

## Overview
This directory contains comprehensive UI testing documentation for the complete SR (Sales Representative) Order to Sales Order lifecycle, including commission management, DSR (Distributor Sales Representative) delivery operations, and payment processing.

---

## Document Structure

### 📘 Main Documentation

#### 1. [Comprehensive UI Testing Guide](./SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md)
**Purpose**: Complete detailed testing guide with step-by-step scenarios  
**Use When**: 
- Planning comprehensive test coverage
- Training new QA team members
- Investigating specific edge cases
- Documenting test procedures

**Contents**:
- System architecture overview
- Detailed test cases with verification steps
- Edge case scenarios
- Data integrity verification queries
- SQL verification scripts
- Common issues and resolutions

**Estimated Reading Time**: 45 minutes

---

#### 2. [Quick Reference Guide](./SR_ORDER_QUICK_REFERENCE.md)
**Purpose**: Fast lookup for common operations and queries  
**Use When**:
- Need quick formula reference
- Looking up status transitions
- Finding common SQL queries
- Troubleshooting issues
- During active testing sessions

**Contents**:
- Complete lifecycle flow diagram
- Commission state transitions
- DSR operation details
- Key formulas and calculations
- Common SQL queries
- UI navigation map
- Validation rules
- Error messages reference
- Troubleshooting guide

**Estimated Reading Time**: 15 minutes

---

#### 3. [Test Execution Plan](./SR_ORDER_TEST_EXECUTION_PLAN.md)
**Purpose**: Structured plan for executing tests  
**Use When**:
- Planning test cycles
- Organizing test team activities
- Tracking test progress
- Reporting test results

**Contents**:
- Test environment setup
- Test execution schedule
- Detailed test scenarios
- Test data matrix
- Test execution tracking templates
- Defect reporting format
- Data integrity verification queries
- Sign-off criteria
- Test summary report template

**Estimated Reading Time**: 30 minutes

---

## Quick Start Guide

### For QA Engineers (First Time)
1. Read [Quick Reference Guide](./SR_ORDER_QUICK_REFERENCE.md) (15 min)
2. Review [Test Execution Plan](./SR_ORDER_TEST_EXECUTION_PLAN.md) - Setup section (10 min)
3. Execute Scenario 1 from Execution Plan (45 min)
4. Refer to [Comprehensive Guide](./SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md) for detailed steps

### For Developers
1. Review [Quick Reference Guide](./SR_ORDER_QUICK_REFERENCE.md) - Formulas and Queries section
2. Check [Comprehensive Guide](./SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md) - Edge Cases section
3. Use Data Integrity Verification queries for debugging

### For Product Owners
1. Read [Quick Reference Guide](./SR_ORDER_QUICK_REFERENCE.md) - Complete Lifecycle section
2. Review [Test Execution Plan](./SR_ORDER_TEST_EXECUTION_PLAN.md) - Test Scenarios
3. Check Test Summary Report format for status updates

---

## Testing Workflow

### Phase 1: Preparation
```
1. Review Quick Reference Guide
2. Set up test environment (Test Execution Plan)
3. Prepare test data (Test Execution Plan - Test Data Matrix)
4. Assign test cases to team members
```

### Phase 2: Execution
```
1. Follow Test Execution Plan schedule
2. Use Comprehensive Guide for detailed steps
3. Refer to Quick Reference for formulas/queries
4. Log results in Test Run Log
5. Report defects using template
```

### Phase 3: Verification
```
1. Run Data Integrity Verification queries
2. Check all status transitions
3. Verify commission calculations
4. Validate inventory consistency
5. Review audit trails
```

### Phase 4: Sign-Off
```
1. Complete all test phases
2. Resolve or defer defects
3. Generate Test Summary Report
4. Obtain stakeholder approvals
```

---

## Key Concepts

### SR Order Lifecycle
```
Create → Approve → Consolidate → Complete → Disburse
```

### Commission States
```
pending → Ready → Disbursed
```

### Sales Order Status
```
Open → Partial → Completed
```

### DSR Operations
```
Assign → Load → Deliver → Collect Payment → Unload (if needed)
```

---

## Critical Test Areas

### 🔴 High Priority (Must Test Every Release)
1. SR Order creation and approval
2. SR Order consolidation to Sales Order
3. Commission calculation accuracy
4. Commission disbursement
5. DSR load/unload operations
6. Payment collection and settlement
7. Data integrity (balances, inventory)

### 🟡 Medium Priority (Test Major Releases)
1. Bulk operations (approval, disbursement)
2. Partial delivery scenarios
3. Return processing
4. UOM conversions
5. Scheme application
6. Concurrent operations

### 🟢 Low Priority (Periodic Testing)
1. UI/UX validation
2. Error message clarity
3. Performance testing
4. Edge case discovery
5. Negative testing

---

## Common Testing Scenarios

### Scenario 1: Happy Path (30 min)
Complete order lifecycle without errors
- **Guide**: Test Execution Plan - Scenario 1
- **Verification**: Comprehensive Guide - Test Case 1.1 to 4.2

### Scenario 2: Partial Operations (30 min)
Partial delivery and payment handling
- **Guide**: Test Execution Plan - Scenario 2
- **Verification**: Comprehensive Guide - Edge Case 7.3

### Scenario 3: Bulk Processing (45 min)
Bulk approval and disbursement
- **Guide**: Test Execution Plan - Scenario 3
- **Verification**: Comprehensive Guide - Test Case 1.4, 4.3

### Scenario 4: Error Handling (30 min)
Insufficient stock, inactive users, concurrent operations
- **Guide**: Comprehensive Guide - Edge Cases section
- **Verification**: Quick Reference - Error Messages

---

## Data Verification Checklist

After each test cycle, run these verifications:

### ✅ Commission Balance Reconciliation
```sql
-- From Quick Reference Guide - Common Queries section
-- Verify SR commission balances match expected
```

### ✅ DSR Payment Balance Reconciliation
```sql
-- From Quick Reference Guide - Common Queries section
-- Verify DSR payment_on_hand is accurate
```

### ✅ Inventory Consistency
```sql
-- From Comprehensive Guide - Verification 8.3
-- Verify inventory matches after DSR operations
```

### ✅ Status Consistency
```sql
-- From Comprehensive Guide - Verification 8.4
-- Verify SO status matches payment/delivery status
```

---

## Troubleshooting Quick Links

### Issue: Commission Not Calculated
→ [Quick Reference - Troubleshooting Guide](./SR_ORDER_QUICK_REFERENCE.md#troubleshooting-guide)

### Issue: Cannot Load SO to DSR
→ [Quick Reference - Troubleshooting Guide](./SR_ORDER_QUICK_REFERENCE.md#troubleshooting-guide)

### Issue: Disbursement Fails
→ [Quick Reference - Troubleshooting Guide](./SR_ORDER_QUICK_REFERENCE.md#troubleshooting-guide)

### Issue: Inventory Mismatch
→ [Comprehensive Guide - Verification 8.3](./SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md#verification-83-inventory-consistency-after-dsr-operations)

---

## SQL Query Library

### Quick Access to Common Queries

**Find Unconsolidated SR Orders**
→ [Quick Reference - Common Queries](./SR_ORDER_QUICK_REFERENCE.md#common-queries)

**Find Ready Commissions**
→ [Quick Reference - Common Queries](./SR_ORDER_QUICK_REFERENCE.md#common-queries)

**Check SR Commission Balance**
→ [Quick Reference - Common Queries](./SR_ORDER_QUICK_REFERENCE.md#common-queries)

**Find DSR Loaded Orders**
→ [Quick Reference - Common Queries](./SR_ORDER_QUICK_REFERENCE.md#common-queries)

**Data Integrity Checks**
→ [Comprehensive Guide - Data Integrity Verification](./SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md#data-integrity-verification)

---

## Test Data Templates

### SR Order Test Data
→ [Test Execution Plan - Test Data Matrix](./SR_ORDER_TEST_EXECUTION_PLAN.md#test-data-matrix)

### Consolidation Test Data
→ [Test Execution Plan - Test Data Matrix](./SR_ORDER_TEST_EXECUTION_PLAN.md#test-data-matrix)

### Test Environment Setup
→ [Test Execution Plan - Test Environment Setup](./SR_ORDER_TEST_EXECUTION_PLAN.md#test-environment-setup)

---

## Reporting Templates

### Test Run Log
→ [Test Execution Plan - Test Execution Tracking](./SR_ORDER_TEST_EXECUTION_PLAN.md#test-execution-tracking)

### Bug Report Format
→ [Test Execution Plan - Defect Reporting Template](./SR_ORDER_TEST_EXECUTION_PLAN.md#defect-reporting-template)

### Test Summary Report
→ [Test Execution Plan - Test Summary Report Template](./SR_ORDER_TEST_EXECUTION_PLAN.md#test-summary-report-template)

---

## Related Documentation

### Backend Documentation
- API Endpoints: `Shoudagor/app/api/sr/`, `Shoudagor/app/api/sales/`, `Shoudagor/app/api/dsr/`
- Services: `Shoudagor/app/services/sr/`, `Shoudagor/app/services/sales/`, `Shoudagor/app/services/dsr/`
- Models: `Shoudagor/app/models/sales.py`

### Frontend Documentation
- SR Components: `shoudagor_FE/src/pages/sr-orders/`
- Sales Components: `shoudagor_FE/src/pages/sales/`
- DSR Components: `shoudagor_FE/src/pages/dsr/`

### Other Testing Guides
- [Sales Order Testing Guide](../Sales_Order/)
- [Purchase Order Testing Guide](../Purchase_Order/)
- [General UI Testing Guide](../General/)

---

## Document Maintenance

### Update Triggers
- New features added to SR/DSR workflow
- Schema changes affecting SR Order or Sales Order
- Business logic updates
- Bug fixes affecting tested scenarios
- Performance optimizations

### Review Schedule
- **Quarterly**: Review all documents for accuracy
- **After Major Release**: Update test scenarios and data
- **After Bug Fixes**: Add new edge cases if applicable

### Version History
- **v1.0 (2025)**: Initial comprehensive documentation
  - Complete UI testing guide
  - Quick reference guide
  - Test execution plan

---

## Contact & Support

### For Questions About
- **Test Procedures**: QA Lead
- **Test Data Setup**: DevOps Team
- **Bug Reports**: Development Team
- **Documentation Updates**: Technical Writer

### Feedback
Please provide feedback on these documents to help improve testing efficiency and coverage.

---

## Appendix: Testing Tools

### Recommended Tools
1. **Database Client**: DBeaver, pgAdmin (for SQL verification)
2. **API Testing**: Postman (for backend verification)
3. **Browser DevTools**: For network inspection
4. **Screen Recording**: For bug reproduction
5. **Test Management**: Jira, TestRail (for tracking)

### Browser Compatibility
- Chrome (latest)
- Firefox (latest)
- Edge (latest)
- Safari (latest)

---

## Quick Command Reference

### Start Test Environment
```bash
# Backend
cd Shoudagor
python -m uvicorn app.main:app --reload

# Frontend
cd shoudagor_FE
npm run dev
```

### Run Data Verification
```bash
# Connect to database
psql -U [username] -d [database]

# Run verification queries from documentation
\i verification_queries.sql
```

---

**Last Updated**: 2025  
**Documentation Version**: 1.0  
**Maintained By**: QA Team

---

## Document Navigation

| Document | Purpose | Time | Priority |
|----------|---------|------|----------|
| [Comprehensive Guide](./SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md) | Detailed testing procedures | 45 min | High |
| [Quick Reference](./SR_ORDER_QUICK_REFERENCE.md) | Fast lookup and troubleshooting | 15 min | High |
| [Test Execution Plan](./SR_ORDER_TEST_EXECUTION_PLAN.md) | Structured test execution | 30 min | High |

**Total Documentation**: ~90 minutes reading time  
**Recommended First Read**: Quick Reference Guide (15 min)

---

**END OF INDEX**
