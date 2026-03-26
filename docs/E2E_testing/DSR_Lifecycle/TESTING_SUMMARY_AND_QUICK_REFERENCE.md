# DSR Lifecycle Testing - Summary & Quick Reference

**Document Version:** 1.0  
**Created:** March 26, 2026  
**Purpose:** Quick reference guide for DSR lifecycle testing

---

## Quick Links

- [Complete Testing Guide](./DSR_COMPLETE_UI_TESTING_GUIDE.md)
- [System Overview](./DSR_LIFECYCLE_OVERVIEW.md)
- [Integration Scenarios](./DSR_INTEGRATION_SCENARIOS.md)
- [Sales Order Testing](../Sales_Order/SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md)
- [SR Order Testing](../SR_Order_Sales_Order/SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md)

---

## Testing Summary

### Total Test Cases: 25+ Core + 10+ Integration + 10+ Edge Cases

### Coverage Areas

| Module | Test Cases | Status |
|--------|-----------|--------|
| SR Order Creation | 3 | ✅ Documented |
| SR Order Approval | 1 | ✅ Documented |
| SR Order Consolidation | 1 | ✅ Documented |
| DSR Assignment | 3 | ✅ Documented |
| DSR Load Operations | 3 | ✅ Documented |
| DSR Delivery | 5 | ✅ Documented |
| DSR Payment Collection | 2 | ✅ Documented |
| DSR Unload Operations | 2 | ✅ Documented |
| DSR Settlement | 5 | ✅ Documented |
| Commission Disbursement | 3 | ✅ Documented |
| Edge Cases | 7 | ✅ Documented |
| Integration Scenarios | 10 | ✅ Documented |

---

## Critical Test Paths

### Path 1: Happy Path (Complete Success Flow)
```
SR Order → Approval → Consolidation → DSR Assignment → 
Load → Delivery → Payment → Unload → Settlement → Commission
```
**Time**: ~30 minutes  
**Priority**: P0 (Must test every release)

### Path 2: Partial Delivery Path
```
SR Order → Approval → Consolidation → DSR Assignment → 
Load → Partial Delivery → Partial Payment → Unload → Settlement
```
**Time**: ~25 minutes  
**Priority**: P1 (Test major releases)

### Path 3: Multi-SR Consolidation Path
```
Multiple SR Orders → Approval → Consolidation → 
DSR Assignment → Load → Delivery → Payment → Settlement → 
Multiple Commission Disbursements
```
**Time**: ~40 minutes  
**Priority**: P1 (Test major releases)

### Path 4: Error Handling Path
```
Test all validation errors and edge cases
```
**Time**: ~60 minutes  
**Priority**: P2 (Test quarterly)

---

## Quick Test Execution Guide

### Pre-Test Checklist (5 minutes)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Database accessible
- [ ] Test users created (Admin, SR, DSR)
- [ ] Master data loaded
- [ ] DSR storage configured

### Smoke Test (10 minutes)
1. Login as SR → Create order → Verify success
2. Login as Admin → Approve order → Verify success
3. Consolidate to SO → Verify success
4. Assign to DSR → Verify success
5. Login as DSR → Load order → Verify success
6. Make delivery → Verify success
7. Collect payment → Verify success
8. Login as Admin → Settle DSR → Verify success

### Full Regression Test (4 hours)
- Execute all 25+ core test cases
- Execute 10+ integration scenarios
- Execute 7+ edge cases
- Run data verification queries
- Document any failures

---

## Common Issues & Solutions

### Issue 1: DSR Cannot Load Order
**Symptoms**: Load button disabled or error  
**Possible Causes**:
- DSR is inactive
- DSR has no storage configured
- SO already loaded
- Insufficient stock at warehouse

**Solution**:
1. Check DSR is_active status
2. Verify DSR storage exists
3. Check SO.is_loaded flag
4. Verify inventory stock

**SQL Check**:
```sql
SELECT dsr_id, dsr_name, is_active, 
       (SELECT COUNT(*) FROM warehouse.dsr_storage WHERE dsr_id = dsr.dsr_id) as has_storage
FROM sales.delivery_sales_representative dsr
WHERE dsr_id = [DSR_ID];
```

---

### Issue 2: Commission Not Calculated
**Symptoms**: Commission status stuck at "pending"  
**Possible Causes**:
- SO not completed (payment or delivery incomplete)
- SR order not consolidated
- Status update failed

**Solution**:
1. Verify SO status = "Completed"
2. Verify payment_status = "Completed"
3. Verify delivery_status = "Completed"
4. Check SR order status = "consolidated"

**SQL Check**:
```sql
SELECT so.sales_order_id, so.status, so.payment_status, so.delivery_status,
       sro.sr_order_id, sro.status, sro.commission_disbursed
FROM sales.sales_order so
JOIN sales.sr_order sro ON sro.sr_order_id = ANY(
    SELECT jsonb_array_elements_text(so.consolidated_sr_orders)::int
)
WHERE so.sales_order_id = [SO_ID];
```

---

### Issue 3: Settlement Fails
**Symptoms**: Error during settlement  
**Possible Causes**:
- Settlement amount > payment_on_hand
- DSR is inactive
- Duplicate reference number
- Concurrent settlement

**Solution**:
1. Verify DSR.payment_on_hand ≥ settlement amount
2. Check DSR is_active = true
3. Verify reference number is unique
4. Retry if concurrent conflict

**SQL Check**:
```sql
SELECT dsr_id, dsr_name, payment_on_hand, is_active
FROM sales.delivery_sales_representative
WHERE dsr_id = [DSR_ID];

SELECT COUNT(*) as duplicate_ref
FROM sales.dsr_payment_settlement
WHERE reference_number = '[REF_NUMBER]' AND is_deleted = false;
```

---

### Issue 4: Inventory Mismatch After DSR Operations
**Symptoms**: DSR inventory doesn't match expected  
**Possible Causes**:
- Failed transaction rollback
- Concurrent operations
- Batch allocation errors

**Solution**:
1. Run inventory reconciliation query
2. Check inventory movement logs
3. Verify batch allocations
4. Contact development team if discrepancy persists

**SQL Check**:
```sql
-- DSR Inventory Reconciliation
SELECT 
    dis.product_id,
    dis.variant_id,
    dis.quantity as dsr_stock,
    COALESCE(SUM(dba.allocated_quantity - dba.delivered_quantity), 0) as allocated_stock,
    dis.quantity - COALESCE(SUM(dba.allocated_quantity - dba.delivered_quantity), 0) as discrepancy
FROM warehouse.dsr_inventory_stock dis
LEFT JOIN warehouse.dsr_batch_allocation dba ON 
    dis.product_id = dba.product_id AND 
    dis.variant_id = dba.variant_id AND
    dis.dsr_storage_id = dba.dsr_storage_id
WHERE dis.dsr_storage_id = [DSR_STORAGE_ID]
GROUP BY dis.product_id, dis.variant_id, dis.quantity
HAVING ABS(dis.quantity - COALESCE(SUM(dba.allocated_quantity - dba.delivered_quantity), 0)) > 0.01;
```

---

## Key Validation Queries

### Query 1: DSR Payment Balance Verification
```sql
WITH dsr_payments AS (
    SELECT 
        dsr.dsr_id,
        dsr.dsr_name,
        dsr.payment_on_hand as current_balance,
        COALESCE(SUM(sopd.amount_paid), 0) as total_collected,
        COALESCE((SELECT SUM(amount) FROM sales.dsr_payment_settlement 
                  WHERE dsr_id = dsr.dsr_id AND is_deleted = false), 0) as total_settled
    FROM sales.delivery_sales_representative dsr
    LEFT JOIN sales.dsr_so_assignment dsa ON dsr.dsr_id = dsa.dsr_id
    LEFT JOIN sales.sales_order_payment_detail sopd ON dsa.sales_order_id = sopd.sales_order_id
    WHERE dsr.is_deleted = false
    GROUP BY dsr.dsr_id, dsr.dsr_name, dsr.payment_on_hand
)
SELECT *, (total_collected - total_settled) as expected_balance,
       current_balance - (total_collected - total_settled) as discrepancy
FROM dsr_payments
WHERE ABS(current_balance - (total_collected - total_settled)) > 0.01;
```

### Query 2: SR Commission Balance Verification
```sql
WITH commission_summary AS (
    SELECT 
        sr.sr_id,
        sr.sr_name,
        sr.commission_amount as current_balance,
        COALESCE(SUM(CASE WHEN sro.commission_disbursed = 'Ready' 
                     THEN sro.commission_amount ELSE 0 END), 0) as ready_amount
    FROM sales.sales_representative sr
    LEFT JOIN sales.sr_order sro ON sr.sr_id = sro.sr_id
    WHERE sr.is_deleted = false
    GROUP BY sr.sr_id, sr.sr_name, sr.commission_amount
)
SELECT *, ready_amount as expected_balance,
       current_balance - ready_amount as discrepancy
FROM commission_summary
WHERE ABS(current_balance - ready_amount) > 0.01;
```

### Query 3: Sales Order Status Consistency
```sql
SELECT 
    sales_order_id,
    order_number,
    status,
    payment_status,
    delivery_status,
    CASE 
        WHEN payment_status = 'Completed' AND delivery_status IN ('Completed', 'Delivered') 
            THEN 'Completed'
        WHEN payment_status != 'Pending' OR delivery_status NOT IN ('Pending', NULL) 
            THEN 'Partial'
        ELSE 'Open'
    END as expected_status
FROM sales.sales_order
WHERE is_deleted = false
    AND status != CASE 
        WHEN payment_status = 'Completed' AND delivery_status IN ('Completed', 'Delivered') 
            THEN 'Completed'
        WHEN payment_status != 'Pending' OR delivery_status NOT IN ('Pending', NULL) 
            THEN 'Partial'
        ELSE 'Open'
    END
    AND status != 'Cancelled';
```

---

## Test Data Templates

### Template 1: SR Order Test Data
```json
{
  "sr_id": 1,
  "customer_id": 5,
  "order_date": "2026-03-26",
  "status": "pending",
  "details": [
    {
      "product_id": 10,
      "variant_id": 15,
      "quantity": 20,
      "unit_of_measure_id": 1,
      "negotiated_price": 120.00
    }
  ]
}
```

### Template 2: DSR Settlement Test Data
```json
{
  "dsr_id": 3,
  "amount": 5000.00,
  "payment_method": "Cash",
  "reference_number": "SETTLE-20260326-001",
  "notes": "Full settlement for March deliveries"
}
```

### Template 3: Commission Disbursement Test Data
```json
{
  "sr_id": 1,
  "sr_order_id": 25,
  "amount": 400.00,
  "payment_method": "Bank Transfer",
  "reference_number": "COMM-20260326-001",
  "notes": "Commission for SO-20260320-0015"
}
```

---

## Performance Benchmarks

### Expected Response Times

| Operation | Expected Time | Acceptable Time | Action Required |
|-----------|--------------|-----------------|-----------------|
| SR Order Creation | < 1s | < 2s | > 2s investigate |
| SR Order Approval | < 0.5s | < 1s | > 1s investigate |
| SO Consolidation | < 3s | < 5s | > 5s investigate |
| DSR Load | < 2s | < 4s | > 4s investigate |
| DSR Delivery | < 1s | < 2s | > 2s investigate |
| Payment Collection | < 1s | < 2s | > 2s investigate |
| DSR Unload | < 2s | < 4s | > 4s investigate |
| Settlement | < 1s | < 2s | > 2s investigate |
| Commission Disbursement | < 1s | < 2s | > 2s investigate |
| Bulk Approval (10 orders) | < 3s | < 5s | > 5s investigate |
| Bulk Disbursement (10 orders) | < 3s | < 5s | > 5s investigate |

---

## Testing Best Practices

### 1. Always Start Fresh
- Clear test data between test runs
- Reset sequences if needed
- Verify initial state before testing

### 2. Test in Sequence
- Follow the natural workflow order
- Don't skip steps
- Verify each step before proceeding

### 3. Verify Data Consistency
- Run verification queries after each major operation
- Check balances reconcile
- Verify audit trails

### 4. Document Failures
- Screenshot error messages
- Note exact steps to reproduce
- Include relevant data (order numbers, IDs)
- Check browser console for errors

### 5. Test Edge Cases
- Don't just test happy paths
- Try invalid inputs
- Test boundary conditions
- Test concurrent operations

---

## Reporting Template

### Test Execution Report

**Date**: [Date]  
**Tester**: [Name]  
**Environment**: [Dev/Staging/Production]  
**Build Version**: [Version]

**Test Summary**:
- Total Test Cases: [Number]
- Passed: [Number]
- Failed: [Number]
- Blocked: [Number]
- Pass Rate: [Percentage]

**Failed Test Cases**:
1. Test Case ID: [ID]
   - Description: [Brief description]
   - Steps to Reproduce: [Steps]
   - Expected Result: [Expected]
   - Actual Result: [Actual]
   - Screenshot: [Link]
   - Priority: [P0/P1/P2]

**Blocked Test Cases**:
1. Test Case ID: [ID]
   - Reason: [Why blocked]
   - Dependency: [What's needed]

**Performance Issues**:
- [List any operations exceeding acceptable time]

**Data Consistency Issues**:
- [List any balance discrepancies]
- [List any inventory mismatches]

**Recommendations**:
- [List any recommendations for fixes or improvements]

---

## Contact & Support

**Development Team**: dev@shoudagor.com  
**QA Team**: qa@shoudagor.com  
**Documentation**: docs@shoudagor.com

**Emergency Contact**: [Phone Number]

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-26 | QA Team | Initial comprehensive testing guide |

---

**END OF DOCUMENT**
