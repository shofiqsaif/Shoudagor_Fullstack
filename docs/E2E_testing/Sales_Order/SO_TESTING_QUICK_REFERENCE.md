# Sales Order Testing - Quick Reference Guide

**Quick access to common testing scenarios and validation queries**

---

## 🚀 Quick Test Scenarios

### 1. Basic SO Creation (2 minutes)
```
1. Navigate to Sales → Sales Orders → New
2. Select Customer: "ABC Store"
3. Select Location: "Main Warehouse"
4. Add Product: "Widget A", Qty: 10, Price: 100
5. Click "Create Sales Order"
6. Verify: Order created, status "Open"
```

### 2. Full Payment (1 minute)
```
1. Open SO details
2. Click "Record Payment"
3. Amount: [Full SO total]
4. Method: "Cash"
5. Click "Record Payment"
6. Verify: payment_status = "Completed"
```

### 3. Full Delivery (1 minute)
```
1. Open SO details
2. Click "Record Delivery"
3. Delivered Qty: [Full ordered qty]
4. Click "Record Delivery"
5. Verify: delivery_status = "Completed"
```

### 4. Full Return (1 minute)
```
1. Open SO details
2. Click "Process Return"
3. Return Qty: [Full delivered qty]
4. Remarks: "Customer return"
5. Click "Process Return"
6. Verify: effective_total_amount reduced
```

### 5. SO with Scheme (2 minutes)
```
1. Create SO with scheme-eligible product
2. Qty: [Meets threshold]
3. Verify: free_quantity auto-populated
4. Submit SO
5. Verify: Claim log created
```

---

## 🔍 Quick Verification Queries

### Check Customer Balance
```sql
SELECT customer_name, balance_amount, store_credit
FROM sales.customer
WHERE customer_id = <customer_id>;
```

### Check SO Status
```sql
SELECT order_number, status, payment_status, delivery_status,
       total_amount, amount_paid, effective_total_amount
FROM sales.sales_order
WHERE sales_order_id = <so_id>;
```

### Check SO Details
```sql
SELECT product_id, variant_id, quantity, free_quantity,
       shipped_quantity, returned_quantity,
       unit_price, discount_amount, applied_scheme_id
FROM sales.sales_order_detail
WHERE sales_order_id = <so_id>;
```

### Check Payments
```sql
SELECT payment_date, amount_paid, payment_method, 
       transaction_reference, remarks
FROM sales.sales_order_payment_detail
WHERE sales_order_id = <so_id>
ORDER BY payment_date;
```

### Check Deliveries
```sql
SELECT delivery_date, product_id, delivered_quantity,
       delivered_free_quantity, remarks
FROM sales.sales_order_delivery_detail
WHERE sales_order_id = <so_id>
ORDER BY delivery_date;
```

### Check Stock
```sql
SELECT location_id, product_id, variant_id, quantity
FROM warehouse.inventory_stock
WHERE product_id = <product_id> AND variant_id = <variant_id>;
```

### Check Batch Allocations
```sql
SELECT ba.batch_id, ba.allocated_quantity, ba.consumed_quantity,
       b.batch_number, b.expiry_date
FROM warehouse.batch_allocation ba
JOIN warehouse.batch b ON ba.batch_id = b.batch_id
WHERE ba.sales_order_detail_id = <detail_id>;
```

### Check Claim Logs
```sql
SELECT scheme_id, product_id, variant_id,
       quantity_claimed, free_quantity, discount_amount,
       claim_date
FROM inventory.claim_log
WHERE sales_order_id = <so_id>;
```

---

## ⚠️ Common Error Scenarios

### Insufficient Stock
**Error:** "Insufficient stock for Widget A"  
**Cause:** Ordered quantity exceeds available stock  
**Fix:** Reduce quantity or add stock

### Credit Limit Exceeded
**Error:** "Customer credit limit exceeded"  
**Cause:** SO total + existing balance > credit limit  
**Fix:** Reduce SO amount or increase credit limit

### Over-Delivery
**Error:** "Delivered quantity cannot exceed ordered quantity"  
**Cause:** Attempting to deliver more than ordered  
**Fix:** Correct delivered quantity

### Over-Return
**Error:** "Return quantity cannot exceed shipped quantity"  
**Cause:** Attempting to return more than delivered  
**Fix:** Correct return quantity

### Deleted Product
**Error:** "Product has been deleted"  
**Cause:** Product soft-deleted after SO creation  
**Fix:** Restore product or cancel SO

### UOM Conversion Missing
**Error:** "UOM conversion not defined"  
**Cause:** No conversion between selected UOM and base UOM  
**Fix:** Configure UOM conversion

---

## 📊 Quick Status Reference

### SO Status Values
- **Open:** Created, no payment or delivery
- **Partial:** Some payment or delivery completed
- **Completed:** Both payment and delivery completed
- **Cancelled:** SO cancelled

### Payment Status Values
- **Pending:** No payment received
- **Partial:** Some payment received (amount_paid < effective_total)
- **Completed:** Full payment received (amount_paid >= effective_total)

### Delivery Status Values
- **Pending:** No items delivered
- **Partial:** Some items delivered
- **Completed:** All items delivered

### Commission Status Values
- **pending:** SO not yet completed
- **Ready:** SO completed, ready for commission calculation
- **disbursed:** Commission paid to SR/DSR

---

## 🎯 Critical Validations

### Before SO Creation
- [ ] Customer exists and is active
- [ ] Products exist and are active
- [ ] Sufficient stock available (billable + free)
- [ ] UOM conversions defined
- [ ] Location is active

### After SO Creation
- [ ] Order number generated
- [ ] Customer balance increased
- [ ] Batch allocations created
- [ ] Scheme applied correctly (if eligible)
- [ ] Claim log created (if scheme applied)

### After Payment
- [ ] Payment record created
- [ ] amount_paid updated
- [ ] payment_status updated
- [ ] Customer balance unchanged (payment offsets order)
- [ ] Commission status updated (if completed)

### After Delivery
- [ ] Delivery record created
- [ ] shipped_quantity updated
- [ ] delivery_status updated
- [ ] Stock deducted from correct source
- [ ] Batch allocations consumed
- [ ] Inventory transaction created

### After Return
- [ ] Return quantities updated
- [ ] effective_total_amount recalculated
- [ ] Stock restored
- [ ] Batch allocations reversed
- [ ] Customer balance adjusted
- [ ] payment_status updated

---

## 🔧 Quick Fixes

### Reset Test Data
```sql
-- Delete test SOs
DELETE FROM sales.sales_order WHERE order_number LIKE 'TEST-%';

-- Reset customer balance
UPDATE sales.customer SET balance_amount = 0 WHERE customer_code = 'TEST-CUST';

-- Reset stock
UPDATE warehouse.inventory_stock SET quantity = 1000 WHERE product_id = <test_product_id>;
```

### Clear Batch Allocations
```sql
DELETE FROM warehouse.batch_allocation 
WHERE sales_order_detail_id IN (
    SELECT sales_order_detail_id FROM sales.sales_order_detail 
    WHERE sales_order_id = <test_so_id>
);
```

### Clear Claim Logs
```sql
DELETE FROM inventory.claim_log WHERE sales_order_id = <test_so_id>;
```

---

## 📱 Mobile Testing Quick Checks

### SR Mobile App
- [ ] Can create SR orders
- [ ] Can view assigned customers
- [ ] Can apply schemes
- [ ] Can view order history
- [ ] Can track commission

### DSR Mobile App
- [ ] Can view assigned SOs
- [ ] Can record deliveries
- [ ] Can record payments
- [ ] Can view DSR storage stock
- [ ] Can process returns

---

## 🎨 UI Element Quick Reference

### SO List Page
- **Filters:** Location, Status, Date Range, Amount Range, Customer
- **Sort:** Order Date, Shipment Date, Amount, Customer Name
- **Actions:** View, Edit, Delete, Print, Export

### SO Details Page
- **Tabs:** Details, Payments, Deliveries, Returns
- **Actions:** Record Payment, Record Delivery, Process Return, Assign to DSR, Cancel

### SO Creation Form
- **Required:** Customer, Location, Order Date, At least 1 line item
- **Optional:** Expected Shipment Date, Remarks
- **Line Item:** Product, Variant, Quantity, UOM, Unit Price

---

## 🚨 Critical Bugs to Watch For

1. **Negative Stock:** Stock goes below zero
2. **Balance Mismatch:** Customer balance doesn't match SOs
3. **Status Inconsistency:** Status doesn't reflect actual state
4. **Batch Over-Allocation:** More allocated than available
5. **Scheme Stacking:** Multiple schemes applied instead of best
6. **Cross-Company Access:** User can see other company's data
7. **Lost Updates:** Concurrent edits cause data loss
8. **Payment Double-Count:** Payment counted twice
9. **Return Over-Limit:** Can return more than delivered
10. **Free Stock Not Validated:** Free items not checked against stock

---

## 📞 Quick Contacts

**For Bugs:** Create ticket in JIRA with prefix "BUG-SO-"  
**For Questions:** Slack channel #qa-testing  
**For Urgent Issues:** Call QA Lead

---

**Last Updated:** March 26, 2026  
**Version:** 1.0
