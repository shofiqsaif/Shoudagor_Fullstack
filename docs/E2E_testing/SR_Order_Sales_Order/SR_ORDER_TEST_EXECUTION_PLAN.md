# SR Order to Sales Order - Test Execution Plan

## Document Purpose
This document provides a structured test execution plan for validating the complete SR Order to Sales Order lifecycle, including commission management and DSR delivery operations.

---

## Test Environment Setup

### Prerequisites
1. **Database**: Clean test database with schema applied
2. **Users**:
   - Admin user (for approvals, assignments)
   - SR user (for order creation)
   - DSR user (for delivery operations)
3. **Master Data**:
   - Products with variants
   - Units of Measure with conversions
   - Storage locations
   - Customers
   - Sales Representatives
   - Distributor Sales Representatives
4. **Configurations**:
   - SR product assignments
   - SR customer assignments
   - DSR storage setup
   - Product pricing
   - Schemes (optional)

### Test Data Setup Script
```sql
-- Create test company
INSERT INTO security.app_client_company (company_name, is_active) 
VALUES ('Test Company', true);

-- Create test users
-- Admin, SR, DSR users with appropriate roles

-- Create test products
INSERT INTO inventory.product (product_name, product_code, company_id)
VALUES 
    ('Product A', 'PROD-A', 1),
    ('Product B', 'PROD-B', 1);

-- Create test customers
INSERT INTO sales.customer (customer_name, customer_code, company_id)
VALUES 
    ('Customer 1', 'CUST-001', 1),
    ('Customer 2', 'CUST-002', 1);

-- Create test SR
INSERT INTO sales.sales_representative (sr_name, sr_code, company_id)
VALUES ('Test SR', 'SR-001', 1);

-- Create test DSR with storage
INSERT INTO sales.delivery_sales_representative (dsr_name, dsr_code, company_id)
VALUES ('Test DSR', 'DSR-001', 1);

-- Assign products to SR
-- Assign customers to SR
-- Create DSR storage
-- Add initial stock
```

---

## Test Execution Schedule

### Phase 1: Core Functionality (Day 1)
**Duration**: 4 hours  
**Focus**: Happy path scenarios

| Test Case | Duration | Priority | Tester |
|-----------|----------|----------|--------|
| SR Order Creation | 30 min | P0 | SR User |
| SR Order Approval | 15 min | P0 | Admin |
| SR Order Consolidation | 45 min | P0 | Admin |
| Sales Order Creation | 30 min | P0 | Admin |
| DSR Assignment | 20 min | P0 | Admin |
| DSR Load Operation | 30 min | P0 | DSR User |
| DSR Delivery | 30 min | P0 | DSR User |
| Payment Collection | 20 min | P0 | DSR User |
| Commission Calculation | 20 min | P0 | Admin |
| Commission Disbursement | 20 min | P0 | Admin |

### Phase 2: Edge Cases (Day 2)
**Duration**: 4 hours  
**Focus**: Error handling and boundary conditions

| Test Case | Duration | Priority | Tester |
|-----------|----------|----------|--------|
| Negative Commission | 20 min | P1 | SR User |
| Insufficient Stock | 30 min | P1 | Admin |
| Partial Delivery | 30 min | P1 | DSR User |
| Return Processing | 30 min | P1 | DSR User |
| Bulk Operations | 45 min | P1 | Admin |
| Concurrent Operations | 30 min | P1 | Multiple |
| Inactive User Scenarios | 25 min | P1 | Admin |
| UOM Conversions | 30 min | P1 | SR User |

### Phase 3: Integration & Data Integrity (Day 3)
**Duration**: 3 hours  
**Focus**: System integration and data consistency

| Test Case | Duration | Priority | Tester |
|-----------|----------|----------|--------|
| Scheme Application | 45 min | P1 | Admin |
| Batch Tracking | 30 min | P1 | DSR User |
| Commission Reconciliation | 30 min | P0 | Admin |
| DSR Payment Reconciliation | 30 min | P0 | Admin |
| Inventory Consistency | 30 min | P0 | Admin |
| Status Consistency | 15 min | P0 | Admin |

---

## Detailed Test Scenarios

### Scenario 1: Complete Order Lifecycle (Happy Path)
**Objective**: Validate end-to-end flow without errors

**Steps**:
1. **SR Creates Order** (SR User)
   - Login as SR
   - Navigate to `/sr/orders/new`
   - Select Customer: "Customer 1"
   - Add Item: Product A, Variant 1, Qty 10, Price 100
   - Verify commission displayed
   - Submit order
   - **Verify**: Order created with status "pending"

2. **Admin Approves Order** (Admin User)
   - Login as Admin
   - Navigate to `/sr/orders`
   - Find pending order
   - Click "Approve"
   - **Verify**: Status changed to "approved"

3. **Admin Consolidates Orders** (Admin User)
   - Navigate to `/sr/orders/unconsolidated`
   - Select "Customer 1"
   - Click "Validate"
   - Select approved orders
   - Select storage location
   - Click "Validate Selected Orders"
   - **Verify**: Validation passes
   - Enter shipment date
   - Click "Generate Consolidated Order"
   - **Verify**: Sales Order created, SR orders status = "consolidated"

4. **Admin Assigns to DSR** (Admin User)
   - Navigate to `/sales`
   - Find consolidated order
   - Click "Add to DSR"
   - Select DSR: "Test DSR"
   - Submit assignment
   - **Verify**: Assignment created

5. **DSR Loads Order** (DSR User)
   - Login as DSR
   - Navigate to `/dsr/my-assignments`
   - Find assigned order
   - Click "Load to Van"
   - Confirm load
   - **Verify**: Order loaded, inventory transferred

6. **DSR Delivers Items** (DSR User)
   - Click "Make Delivery"
   - Enter delivered quantities (full delivery)
   - Submit delivery
   - **Verify**: Delivery recorded, inventory updated

7. **DSR Collects Payment** (DSR User)
   - Click "Collect Payment"
   - Enter full amount
   - Select payment method
   - Submit payment
   - **Verify**: Payment recorded, SO completed

8. **Admin Disburses Commission** (Admin User)
   - Navigate to `/sr/orders/undisbursed`
   - Find Ready commission
   - Click "Disburse"
   - Enter payment details
   - Confirm disbursement
   - **Verify**: Commission disbursed, SR balance updated

**Expected Duration**: 45 minutes  
**Success Criteria**: All steps complete without errors, data consistent

---

### Scenario 2: Partial Delivery with Returns
**Objective**: Test partial operations and return handling

**Steps**:
1. Create and approve SR Order (10 items)
2. Consolidate to Sales Order
3. Assign to DSR and load
4. Deliver 6 items, reject 2 items
5. Collect partial payment (for 6 items)
6. Verify:
   - Delivery status = "Partial"
   - Payment status = "Partial"
   - SO status = "Partial"
   - Returned items back in stock
   - Commission calculated on 6 items only

**Expected Duration**: 30 minutes  
**Success Criteria**: Partial statuses correct, commission accurate

---

### Scenario 3: Bulk Commission Disbursement
**Objective**: Test bulk operations efficiency

**Steps**:
1. Create 10 SR Orders for different SRs
2. Approve all orders
3. Consolidate each to Sales Orders
4. Complete all Sales Orders (delivery + payment)
5. Verify all commissions = "Ready"
6. Navigate to `/sr/orders/undisbursed`
7. Select all Ready orders
8. Click "Disburse (10)"
9. Review summary
10. Confirm bulk disbursement
11. Verify:
    - All orders disbursed
    - SR balances updated correctly
    - Disbursement records created

**Expected Duration**: 45 minutes  
**Success Criteria**: All 10 orders processed successfully

---

### Scenario 4: Concurrent Operations Test
**Objective**: Verify system handles concurrent users

**Setup**: 2 testers, same order

**Steps**:
1. Tester A: Opens disburse dialog for Order X
2. Tester B: Disburses Order X
3. Tester A: Attempts to confirm disbursement
4. **Verify**: Tester A gets error "Already disbursed"

**Repeat for**:
- Concurrent approval
- Concurrent consolidation
- Concurrent DSR load

**Expected Duration**: 30 minutes  
**Success Criteria**: No double processing, appropriate errors

---

### Scenario 5: UOM Conversion Accuracy
**Objective**: Verify pricing and commission with UOM conversions

**Setup**: Product with Box (12 pieces) and Piece UOMs

**Steps**:
1. Create SR Order
2. Add item: 1 Box, Base price 10/piece
3. Verify displayed price = 120 (10 × 12)
4. Enter negotiated price = 150
5. Verify commission = (150 - 120) × 1 = 30
6. Change to 12 Pieces
7. Verify price = 120 (10 × 12)
8. Verify commission = (150 - 120) × 12 = 360
9. Complete order flow
10. Verify backend stored in base UOM

**Expected Duration**: 30 minutes  
**Success Criteria**: All conversions accurate

---

## Test Data Matrix

### SR Order Test Data

| Test Case | Customer | Product | Variant | Qty | UOM | Sale Price | Negotiated | Expected Commission |
|-----------|----------|---------|---------|-----|-----|------------|------------|-------------------|
| Basic | Cust-1 | Prod-A | Var-1 | 10 | Piece | 100 | 110 | +100 |
| Negative | Cust-1 | Prod-A | Var-1 | 10 | Piece | 100 | 90 | -100 |
| UOM | Cust-1 | Prod-B | Var-2 | 1 | Box | 1200 | 1500 | +300 |
| Large Qty | Cust-2 | Prod-A | Var-1 | 1000 | Piece | 100 | 105 | +5000 |
| Zero Comm | Cust-2 | Prod-B | Var-2 | 5 | Piece | 50 | 50 | 0 |

### Consolidation Test Data

| Scenario | SR Orders | Customer | Total Items | Expected SO Items | Stock Available |
|----------|-----------|----------|-------------|-------------------|-----------------|
| Single | 1 | Cust-1 | 3 | 3 | Yes |
| Multiple | 3 | Cust-1 | 9 | 9 | Yes |
| With Scheme | 2 | Cust-2 | 5 | 7 (2 free) | Yes |
| Insufficient | 2 | Cust-1 | 10 | - | No (Error) |

---

## Test Execution Tracking

### Test Run Log Template

| Test ID | Test Case | Date | Tester | Status | Duration | Issues | Notes |
|---------|-----------|------|--------|--------|----------|--------|-------|
| TC-001 | SR Order Creation | | | | | | |
| TC-002 | SR Order Approval | | | | | | |
| TC-003 | Consolidation | | | | | | |
| ... | ... | | | | | | |

**Status Values**: Pass, Fail, Blocked, Skip

---

## Defect Reporting Template

### Bug Report Format
```
Title: [Component] Brief description
Severity: Critical / High / Medium / Low
Priority: P0 / P1 / P2 / P3

Steps to Reproduce:
1. 
2. 
3. 

Expected Result:


Actual Result:


Environment:
- Browser:
- User Role:
- Test Data:

Screenshots/Logs:


Additional Notes:

```

---

## Data Integrity Verification Queries

### Run After Each Test Phase

```sql
-- 1. Commission Balance Check
SELECT 
    sr.sr_name,
    sr.commission_amount as balance,
    COUNT(CASE WHEN sro.commission_disbursed = 'Ready' THEN 1 END) as ready_count,
    SUM(CASE WHEN sro.commission_disbursed = 'Ready' THEN sro.commission_amount ELSE 0 END) as ready_total
FROM sales.sales_representative sr
LEFT JOIN sales.sr_order sro ON sr.sr_id = sro.sr_id
WHERE sr.is_deleted = false
GROUP BY sr.sr_id, sr.sr_name, sr.commission_amount;

-- 2. DSR Payment Balance Check
SELECT 
    dsr.dsr_name,
    dsr.payment_on_hand,
    COALESCE(SUM(sopd.amount_paid), 0) as collected,
    COALESCE((SELECT SUM(amount) FROM sales.dsr_payment_settlement WHERE dsr_id = dsr.dsr_id), 0) as settled
FROM sales.delivery_sales_representative dsr
LEFT JOIN sales.dsr_so_assignment dsa ON dsr.dsr_id = dsa.dsr_id
LEFT JOIN sales.sales_order_payment_detail sopd ON dsa.sales_order_id = sopd.sales_order_id
WHERE dsr.is_deleted = false
GROUP BY dsr.dsr_id, dsr.dsr_name, dsr.payment_on_hand;

-- 3. Inventory Consistency Check
SELECT 
    p.product_name,
    pv.variant_name,
    SUM(inv.quantity) as total_stock,
    SUM(dsr_inv.quantity) as dsr_stock
FROM inventory.product p
LEFT JOIN inventory.product_variant pv ON p.product_id = pv.product_id
LEFT JOIN warehouse.inventory_stock inv ON p.product_id = inv.product_id AND pv.variant_id = inv.variant_id
LEFT JOIN warehouse.dsr_inventory_stock dsr_inv ON p.product_id = dsr_inv.product_id AND pv.variant_id = dsr_inv.variant_id
WHERE p.is_deleted = false
GROUP BY p.product_id, p.product_name, pv.variant_id, pv.variant_name;

-- 4. Status Consistency Check
SELECT 
    order_number,
    status,
    payment_status,
    delivery_status,
    CASE 
        WHEN payment_status = 'Completed' AND delivery_status IN ('Completed', 'Delivered') THEN 'Completed'
        WHEN payment_status != 'Pending' OR delivery_status != 'Pending' THEN 'Partial'
        ELSE 'Open'
    END as expected_status
FROM sales.sales_order
WHERE is_deleted = false
    AND status != CASE 
        WHEN payment_status = 'Completed' AND delivery_status IN ('Completed', 'Delivered') THEN 'Completed'
        WHEN payment_status != 'Pending' OR delivery_status != 'Pending' THEN 'Partial'
        ELSE 'Open'
    END;
```

**Expected**: All queries return 0 discrepancies

---

## Test Sign-Off Criteria

### Phase 1 Sign-Off
- [ ] All P0 test cases passed
- [ ] No critical defects open
- [ ] Data integrity checks passed
- [ ] Performance acceptable (< 3s per operation)

### Phase 2 Sign-Off
- [ ] All P1 test cases passed
- [ ] Edge cases handled correctly
- [ ] Error messages clear and actionable
- [ ] No high severity defects open

### Phase 3 Sign-Off
- [ ] All integration tests passed
- [ ] Data reconciliation successful
- [ ] Audit trail complete
- [ ] Documentation updated

### Final Sign-Off
- [ ] All test phases completed
- [ ] All defects resolved or deferred
- [ ] Test summary report created
- [ ] Stakeholder approval obtained

---

## Test Summary Report Template

```
SR Order to Sales Order - Test Summary Report

Test Period: [Start Date] to [End Date]
Testers: [Names]
Environment: [Test/Staging]

Test Statistics:
- Total Test Cases: X
- Passed: X (X%)
- Failed: X (X%)
- Blocked: X (X%)
- Skipped: X (X%)

Defects Summary:
- Critical: X
- High: X
- Medium: X
- Low: X

Test Coverage:
- SR Order Management: X%
- Consolidation: X%
- DSR Operations: X%
- Commission Management: X%
- Payment Processing: X%

Key Findings:
1. 
2. 
3. 

Recommendations:
1. 
2. 
3. 

Sign-Off:
QA Lead: _________________ Date: _______
Dev Lead: _________________ Date: _______
Product Owner: ____________ Date: _______
```

---

## Appendix: Test Automation Opportunities

### High Priority for Automation
1. SR Order creation with various UOMs
2. Bulk approval operations
3. Commission calculation verification
4. Data integrity checks
5. Status transition validation

### Medium Priority
1. Consolidation validation
2. DSR load/unload operations
3. Payment collection
4. Bulk disbursement

### Low Priority (Manual Testing Preferred)
1. UI/UX validation
2. Error message clarity
3. User workflow efficiency
4. Edge case discovery

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Next Review**: After each major release
