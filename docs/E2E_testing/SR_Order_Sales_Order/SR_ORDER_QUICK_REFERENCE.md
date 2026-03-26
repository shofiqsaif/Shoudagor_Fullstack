# SR Order to Sales Order - Quick Reference Guide

## Quick Navigation
- [SR Order Flow](#sr-order-flow)
- [Commission States](#commission-states)
- [DSR Operations](#dsr-operations)
- [Key Formulas](#key-formulas)
- [Common Queries](#common-queries)

---

## SR Order Flow

### Complete Lifecycle (Happy Path)
```
1. SR creates order → Status: pending, Commission: pending
2. Admin approves → Status: approved, Commission: pending
3. Admin consolidates → SR Status: consolidated, SO created
4. Admin assigns to DSR → DSR Assignment created
5. DSR loads to van → is_loaded: true, inventory transferred
6. DSR delivers items → shipped_quantity updated
7. DSR collects payment → amount_paid updated
8. SO completes → Status: Completed, Commission: Ready
9. Admin disburses → Commission: Disbursed, SR paid
```

### Key Status Fields

**SR Order Status**:
- `pending` - Awaiting approval
- `approved` - Ready for consolidation
- `consolidated` - Merged into Sales Order
- `Completed` - Sales Order completed

**Commission Status**:
- `pending` - Not ready for payment
- `Ready` - Available for disbursement
- `Disbursed` - Paid to SR

**Sales Order Status**:
- `Open` - No payment or delivery
- `Partial` - Some payment or delivery
- `Completed` - Fully paid and delivered
- `Cancelled` - Order cancelled

---

## Commission States

### Transition Rules
```
pending → Ready: When SO status = Completed
Ready → Disbursed: When admin disburses commission
```

### Commission Calculation
```javascript
// For each SR Order Detail
commission = (negotiated_price - sale_price) × shipped_quantity

// Total SR Order Commission
total_commission = SUM(all detail commissions)
```

### SR Balance Updates
```
When Ready: SR.commission_amount += order.commission_amount
When Disbursed: SR.commission_amount -= order.commission_amount
```

---

## DSR Operations

### Load Operation
**What happens**:
1. Validates SO not already loaded
2. Validates DSR has storage
3. Validates sufficient stock at SO location
4. Transfers inventory:
   - `inventory_stock` (SO location) ↓
   - `dsr_inventory_stock` (DSR storage) ↑
5. Creates batch allocations (if enabled)
6. Sets `is_loaded = true`

### Delivery Operation
**What happens**:
1. Creates delivery detail records
2. Updates `shipped_quantity` on SO detail
3. Decreases DSR inventory
4. Updates batch allocations
5. Updates delivery status

### Unload Operation
**What happens**:
1. Calculates remaining undelivered items
2. Transfers back to warehouse:
   - `dsr_inventory_stock` ↓
   - `inventory_stock` (target location) ↑
3. Reverses batch allocations
4. Sets `is_loaded = false`

---

## Key Formulas

### Effective Total Amount
```sql
effective_total = SUM((quantity - returned_quantity) × unit_price - discount_amount)
-- Excludes free items (is_free_item = true)
```

### Commission Calculation
```sql
commission = SUM((negotiated_price - sale_price) × shipped_quantity)
WHERE is_deleted = false
```

### DSR Payment Balance
```sql
payment_on_hand = total_collected - total_settled
```

### Stock Required for Load
```sql
required_stock = (quantity - shipped_quantity - returned_quantity) 
               + (free_quantity - shipped_free_quantity - returned_free_quantity)
-- Converted to base UOM
```

---

## Common Queries

### Find Unconsolidated SR Orders
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    ARRAY_AGG(sro.sr_order_id) as sr_order_ids,
    COUNT(*) as order_count
FROM sales.sr_order sro
JOIN sales.customer c ON sro.customer_id = c.customer_id
WHERE sro.status = 'approved'
    AND sro.is_deleted = false
    AND sro.company_id = [COMPANY_ID]
GROUP BY c.customer_id, c.customer_name;
```

### Find Ready Commissions
```sql
SELECT 
    sro.sr_order_id,
    sro.order_number,
    sr.sr_name,
    sro.commission_amount,
    sro.order_date
FROM sales.sr_order sro
JOIN sales.sales_representative sr ON sro.sr_id = sr.sr_id
WHERE sro.commission_disbursed = 'Ready'
    AND sro.is_deleted = false
    AND sro.company_id = [COMPANY_ID]
ORDER BY sro.order_date;
```

### Find DSR Loaded Orders
```sql
SELECT 
    so.sales_order_id,
    so.order_number,
    dsr.dsr_name,
    so.loaded_at,
    so.is_loaded
FROM sales.sales_order so
JOIN sales.delivery_sales_representative dsr ON so.loaded_by_dsr_id = dsr.dsr_id
WHERE so.is_loaded = true
    AND so.is_deleted = false
    AND so.company_id = [COMPANY_ID];
```

### Check SR Commission Balance
```sql
SELECT 
    sr.sr_id,
    sr.sr_name,
    sr.commission_amount as current_balance,
    COUNT(CASE WHEN sro.commission_disbursed = 'Ready' THEN 1 END) as ready_orders,
    SUM(CASE WHEN sro.commission_disbursed = 'Ready' THEN sro.commission_amount ELSE 0 END) as ready_amount
FROM sales.sales_representative sr
LEFT JOIN sales.sr_order sro ON sr.sr_id = sro.sr_id AND sro.is_deleted = false
WHERE sr.is_deleted = false
    AND sr.company_id = [COMPANY_ID]
GROUP BY sr.sr_id, sr.sr_name, sr.commission_amount;
```

### Find DSR Payment to Settle
```sql
SELECT 
    dsr.dsr_id,
    dsr.dsr_name,
    dsr.payment_on_hand,
    COUNT(dsa.assignment_id) as active_assignments
FROM sales.delivery_sales_representative dsr
LEFT JOIN sales.dsr_so_assignment dsa ON dsr.dsr_id = dsa.dsr_id 
    AND dsa.status != 'completed'
    AND dsa.is_deleted = false
WHERE dsr.payment_on_hand > 0
    AND dsr.is_deleted = false
    AND dsr.company_id = [COMPANY_ID]
GROUP BY dsr.dsr_id, dsr.dsr_name, dsr.payment_on_hand;
```

---

## UI Navigation Map

### SR User Flows
- Create Order: `/sr/orders/new`
- View Orders: `/sr/orders`
- Order Details: Click order number

### Admin Flows
- Approve Orders: `/sr/orders` → Approve button
- Consolidate: `/sr/orders/unconsolidated`
- View Sales Orders: `/sales`
- Assign to DSR: Sales Order → "Add to DSR"
- Disburse Commission: `/sr/orders/undisbursed`
- View Disbursements: `/sr/orders/disbursement-history`

### DSR User Flows
- My Assignments: `/dsr/my-assignments`
- My Inventory: `/dsr/inventory-stock`
- Settlement History: `/dsr/settlement-history`

### Admin DSR Management
- DSR List: `/dsr`
- DSR Assignments: `/dsr/so-assignments`
- Settle Payment: DSR List → "Settle Payment"
- Settlement History: `/dsr/settlement-history`

---

## Validation Rules

### SR Order Creation
- ✅ SR must have product assignment
- ✅ SR must have customer assignment
- ✅ Negotiated price can be any value (including negative commission)
- ✅ Quantity must be > 0
- ✅ Stock check is informational only

### SR Order Approval
- ✅ Only pending/draft orders can be approved
- ✅ Cannot delete approved orders
- ✅ Cannot edit approved orders

### Consolidation
- ✅ All orders must be approved
- ✅ All orders must belong to same customer
- ✅ Sufficient stock required at selected location
- ✅ Stock includes free quantities from schemes

### DSR Assignment
- ✅ DSR must be active
- ✅ DSR must have storage configured
- ✅ SO cannot be already loaded
- ✅ Sufficient stock at SO location

### DSR Load
- ✅ SO must be assigned to DSR
- ✅ SO not already loaded
- ✅ Sufficient stock for all items (billable + free)
- ✅ Stock converted to base UOM

### Commission Disbursement
- ✅ Commission status must be "Ready"
- ✅ Cannot disburse twice
- ✅ SR must exist

---

## Error Messages Reference

### Common Errors

**"Sales Representative does not have assignment for product"**
- Cause: SR trying to order unassigned product
- Fix: Admin must assign product to SR

**"Sales Representative does not have assignment for customer"**
- Cause: SR trying to order for unassigned customer
- Fix: Admin must assign customer to SR

**"Insufficient stock for assignment"**
- Cause: Not enough stock at SO location for DSR assignment
- Fix: Transfer stock or reduce order quantity

**"DSR does not have a storage location configured"**
- Cause: DSR storage not created
- Fix: Admin creates DSR storage

**"Cannot assign to inactive DSR"**
- Cause: DSR is deactivated
- Fix: Activate DSR or choose different DSR

**"Sales Order is already loaded"**
- Cause: Attempting to load already loaded SO
- Fix: Unload first or check loaded status

**"Commission is not ready for disbursement"**
- Cause: SO not completed or commission already disbursed
- Fix: Complete SO or check commission status

---

## Performance Tips

### For Large Datasets
1. Use filters before bulk operations
2. Limit date ranges in queries
3. Use pagination for large lists
4. Index on frequently queried fields

### Recommended Indexes
```sql
-- Already implemented in schema
CREATE INDEX idx_sr_order_status ON sales.sr_order(status);
CREATE INDEX idx_sr_order_commission ON sales.sr_order(commission_disbursed);
CREATE INDEX idx_so_consolidated ON sales.sales_order(is_consolidated);
CREATE INDEX idx_so_loaded ON sales.sales_order(is_loaded);
```

---

## Troubleshooting Guide

### Issue: Commission Not Updating to Ready
**Check**:
1. SO status = "Completed"?
2. Payment status = "Completed"?
3. Delivery status = "Completed" or "Delivered"?

**Fix**: Complete missing payment or delivery

### Issue: Cannot Load SO to DSR
**Check**:
1. DSR has storage? `SELECT * FROM warehouse.dsr_storage WHERE dsr_id = X`
2. DSR is active? `SELECT is_active FROM sales.delivery_sales_representative WHERE dsr_id = X`
3. SO already loaded? `SELECT is_loaded FROM sales.sales_order WHERE sales_order_id = X`
4. Sufficient stock? Run stock validation query

### Issue: Inventory Mismatch
**Check**:
1. Run inventory reconciliation queries
2. Check for failed transactions in logs
3. Verify batch allocations match inventory

**Fix**: Contact admin for manual reconciliation

---

## Testing Quick Checklist

### Smoke Test (15 minutes)
- [ ] Create SR Order
- [ ] Approve SR Order
- [ ] Consolidate to SO
- [ ] Assign to DSR
- [ ] Load to DSR
- [ ] Deliver items
- [ ] Collect payment
- [ ] Verify commission Ready
- [ ] Disburse commission

### Regression Test (1 hour)
- [ ] All smoke test steps
- [ ] Bulk approval
- [ ] Bulk disbursement
- [ ] Partial delivery
- [ ] Return processing
- [ ] Unload operation
- [ ] DSR settlement
- [ ] Data integrity checks

---

**Last Updated**: 2025  
**Version**: 1.0
