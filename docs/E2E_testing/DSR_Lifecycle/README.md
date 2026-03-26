# DSR Complete Lifecycle - UI Testing Documentation

## Overview

This directory contains comprehensive UI testing documentation for the complete DSR (Delivery Sales Representative) lifecycle in the Shoudagor Distribution Management System.

## Document Structure

### 1. [DSR_LIFECYCLE_OVERVIEW.md](./DSR_LIFECYCLE_OVERVIEW.md) ✅ CREATED
- System architecture and data flow
- Business rules and validation logic
- Prerequisites and setup requirements
- Data models and relationships

### 2. [DSR_COMPLETE_UI_TESTING_GUIDE.md](./DSR_COMPLETE_UI_TESTING_GUIDE.md) ✅ CREATED
- **25+ Core Test Cases** covering complete DSR lifecycle
- SR Order creation and approval (3 test cases)
- SR Order consolidation to Sales Orders (1 test case)
- DSR assignment to Sales Orders (3 test cases)
- DSR Load operations (3 test cases)
- DSR Delivery and Payment collection (5 test cases)
- DSR Unload operations (2 test cases)
- DSR Payment settlement (5 test cases)
- Commission disbursement (3 test cases)
- **7+ Edge Cases** with validation scenarios
- **Complete data verification queries**

### 3. [DSR_INTEGRATION_SCENARIOS.md](./DSR_INTEGRATION_SCENARIOS.md) ✅ CREATED
- **10+ Integration test scenarios**
- End-to-end flow testing
- Multi-SR order consolidation
- Concurrent DSR operations
- Scheme application through DSR flow
- Customer balance management
- Performance testing scenarios
- Security testing scenarios
- Data consistency scenarios
- Error recovery scenarios
- Audit trail scenarios

### 4. [TESTING_SUMMARY_AND_QUICK_REFERENCE.md](./TESTING_SUMMARY_AND_QUICK_REFERENCE.md) ✅ CREATED
- Quick reference guide
- Common issues and solutions
- Key validation queries
- Test data templates
- Performance benchmarks
- Testing best practices
- Reporting template

## Complete DSR Lifecycle Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SR ORDER CREATION                             │
│  SR creates order with negotiated prices for assigned customers │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SR ORDER APPROVAL                             │
│     Admin/Manager approves SR orders (single or bulk)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              SR ORDER CONSOLIDATION TO SO                        │
│  Multiple SR orders consolidated into single Sales Order        │
│  - Stock validation                                              │
│  - Scheme application                                            │
│  - Price difference tracking                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSR ASSIGNMENT                                │
│  Sales Order assigned to DSR for delivery                       │
│  - DSR must be active                                            │
│  - DSR must have storage configured                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSR LOAD OPERATION                            │
│  Inventory transferred from warehouse to DSR van                │
│  - inventory_stock decreased at warehouse                        │
│  - dsr_inventory_stock increased at DSR storage                 │
│  - Batch allocations created                                     │
│  - SO.is_loaded = true                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSR DELIVERY                                  │
│  DSR delivers items to customer                                 │
│  - Updates shipped_quantity                                      │
│  - Deducts from DSR inventory                                    │
│  - Handles returns/rejections                                    │
│  - Updates delivery status                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSR PAYMENT COLLECTION                        │
│  DSR collects payment from customer                             │
│  - DSR.payment_on_hand increased                                 │
│  - Customer.balance_amount decreased                             │
│  - SO.amount_paid increased                                      │
│  - Payment status updated                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSR UNLOAD OPERATION                          │
│  Undelivered items returned to warehouse                        │
│  - dsr_inventory_stock decreased                                 │
│  - inventory_stock increased at warehouse                        │
│  - SO.is_loaded = false                                          │
│  - Batch allocations reversed                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DSR PAYMENT SETTLEMENT                        │
│  Admin collects payment from DSR                                │
│  - DSR.payment_on_hand decreased                                 │
│  - Settlement record created                                     │
│  - Payment method and reference tracked                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMMISSION DISBURSEMENT                       │
│  SR commission calculated and disbursed                         │
│  - Commission = (Negotiated - Sale) × Shipped Qty                │
│  - SR.commission_amount updated                                  │
│  - SR_Order.commission_disbursed = "Disbursed"                   │
└─────────────────────────────────────────────────────────────────┘
```

## Testing Coverage Summary

### ✅ Comprehensive Documentation Created

**Total Documentation**: 4 comprehensive documents covering 45+ test scenarios

**Test Case Coverage**:
- ✅ 25+ Core UI test cases with step-by-step instructions
- ✅ 10+ Integration scenarios across modules
- ✅ 7+ Edge case scenarios with error handling
- ✅ 3+ Performance testing scenarios
- ✅ 3+ Security testing scenarios
- ✅ 2+ Data consistency scenarios
- ✅ 2+ Error recovery scenarios
- ✅ 2+ Audit trail scenarios

**Verification Coverage**:
- ✅ SQL verification queries for all operations
- ✅ Balance reconciliation queries (DSR, SR, Customer)
- ✅ Inventory consistency checks
- ✅ Status consistency validation
- ✅ Audit trail completeness checks

**Documentation Features**:
- ✅ Step-by-step test procedures
- ✅ Expected results for each test
- ✅ SQL verification queries
- ✅ Common issues and solutions
- ✅ Performance benchmarks
- ✅ Test data templates
- ✅ Quick reference guide

---

## Quick Start Guide

### For First-Time Testers

1. **Read Overview** (15 minutes)
   - Start with [DSR_LIFECYCLE_OVERVIEW.md](./DSR_LIFECYCLE_OVERVIEW.md)
   - Understand system architecture and business rules

2. **Setup Environment** (30 minutes)
   - Follow prerequisites section
   - Create test users and master data
   - Configure DSR storage

3. **Run Smoke Test** (10 minutes)
   - Follow smoke test in [TESTING_SUMMARY_AND_QUICK_REFERENCE.md](./TESTING_SUMMARY_AND_QUICK_REFERENCE.md)
   - Verify basic functionality works

4. **Execute Core Tests** (2-3 hours)
   - Follow test cases in [DSR_COMPLETE_UI_TESTING_GUIDE.md](./DSR_COMPLETE_UI_TESTING_GUIDE.md)
   - Document any failures

5. **Run Integration Tests** (1-2 hours)
   - Execute scenarios from [DSR_INTEGRATION_SCENARIOS.md](./DSR_INTEGRATION_SCENARIOS.md)
   - Verify cross-module functionality

6. **Verify Data Consistency** (30 minutes)
   - Run verification queries
   - Check for any discrepancies

### For Experienced Testers

1. **Quick Reference** (5 minutes)
   - Review [TESTING_SUMMARY_AND_QUICK_REFERENCE.md](./TESTING_SUMMARY_AND_QUICK_REFERENCE.md)
   - Check for any new test cases

2. **Execute Regression** (4 hours)
   - Run all core test cases
   - Execute integration scenarios
   - Run edge case tests

3. **Performance Testing** (1 hour)
   - Execute performance scenarios
   - Compare against benchmarks

4. **Report Results**
   - Use reporting template
   - Document any issues

---

## Testing Approach

### Happy Path Testing
- Standard workflows with valid data
- Expected user journeys
- Positive test cases

### Negative Testing
- Invalid inputs
- Missing required fields
- Unauthorized access attempts

### Edge Case Testing
- Boundary conditions
- Concurrent operations
- Race conditions
- Stock depletion scenarios

### Integration Testing
- Cross-module data flow
- Inventory synchronization
- Balance calculations
- Status transitions

### Performance Testing
- Bulk operations
- Large datasets
- Concurrent users
- Response time validation

---

## Prerequisites

1. **Functional Correctness**: Verify all operations work as designed
2. **Data Integrity**: Ensure data consistency across all operations
3. **Edge Case Handling**: Test boundary conditions and unusual scenarios
4. **Error Handling**: Validate proper error messages and recovery
5. **Performance**: Verify system handles load efficiently
6. **Security**: Ensure proper authorization and access control
7. **Audit Trail**: Verify all operations are logged correctly

## Testing Approach

### Happy Path Testing
- Standard workflows with valid data
- Expected user journeys
- Positive test cases

### Negative Testing
- Invalid inputs
- Missing required fields
- Unauthorized access attempts

### Edge Case Testing
- Boundary conditions
- Concurrent operations
- Race conditions
- Stock depletion scenarios

### Integration Testing
- Cross-module data flow
- Inventory synchronization
- Balance calculations
- Status transitions

### Performance Testing
- Bulk operations
- Large datasets
- Concurrent users
- Response time validation

## Prerequisites

### Master Data Required
- Active company with configuration
- Users: Admin, SR, DSR with proper roles
- Products with stock and pricing
- Customers assigned to SRs
- DSRs with storage configured
- Active claim schemes
- Storage locations

### Environment Setup
- Backend API running (port 8000)
- Frontend application running (port 5173)
- PostgreSQL database accessible
- Test data loaded

## Testing Tools

- **Manual Testing**: Primary method for UI validation
- **Browser DevTools**: Network inspection, console logs
- **Database Client**: SQL verification queries
- **Postman/Insomnia**: API endpoint testing (optional)

## Document Maintenance

**Review Schedule**: Quarterly or after major releases  
**Update Triggers**:
- New features added
- Business logic changes
- Bug fixes affecting workflows
- Schema modifications

**Contact**: Development Team  
**Version**: 2.0 (March 26, 2026)
