# Purchase Order Testing - Quick Reference Guide

**Document Version:** 1.0  
**Generated:** March 26, 2026  
**For:** Shoudagor ERP System

---

## Quick Test Checklist

### ✅ Pre-Testing Setup
- [ ] Test database initialized
- [ ] 5+ test suppliers created
- [ ] 20+ test products with variants
- [ ] 3+ storage locations configured
- [ ] Test schemes configured
- [ ] Test user accounts ready
- [ ] Browser cache cleared

---

## Critical Test Scenarios (Must Test)

### 1. Basic PO Creation (Test Case 1)
**Steps:** Supplier → Location → Add Product → Quantity → Price → Submit  
**Verify:** PO number generated, Status = "Open", Supplier balance increased

### 2. Full Delivery (Test Case 7)
**Steps:** Open PO → Record Delivery → Enter quantities → Submit  
**Verify:** Delivery Status = "Completed", Inventory updated, Batches created

### 3. Full Payment (Test Case 13)
**Steps:** Open PO → Record Payment → Enter amount → Submit  
**Verify:** Payment Status = "Completed", Supplier balance decreased

### 4. Complete Lifecycle (Test Case 71)
**Steps:** Create → Partial Delivery → Partial Payment → Complete Delivery → Complete Payment  
**Verify:** All statuses = "Completed", Inventory correct, Balance = 0

### 5. Scheme Application (Test Case 27)
**Steps:** Create PO → Add product with scheme → Verify free items  
**Verify:** Free quantity calculated, Effective TP correct, Separate batches

---

## Edge Cases to Test

### Must Test Edge Cases
1. **Zero/Negative Quantity** (TC 41, 42) - Should be prevented
2. **Over-delivery** (TC 51) - Should be prevented
3. **Over-payment** (TC 52) - Should be prevented
4. **Over-return** (TC 53) - Should be prevented
5. **Decimal Quantities** (TC 45) - Should work correctly
6. **Large Numbers** (TC 44) - Should handle without overflow
7. **Date Validation** (TC 47) - Delivery before order should fail
8. **Concurrent Operations** (TC 50) - No duplicate PO numbers

---

## Known Issues to Verify

### ⚠️ Critical Issues
1. **PO Cancellation** - Does NOT reverse supplier balance (TC 21)
2. **Return Calculation** - Uses unit_price instead of effective_tp (TC 17, 18)

### ⚠️ Medium Issues
3. **Delivery Status** - Includes returned quantities incorrectly (TC 17)
4. **Location Validation** - No validation for location consistency (TC 49)

---

## Quick Validation Checklist

### After PO Creation
- [ ] PO number format: PO-YYYYMMDD-XXX
- [ ] Status = "Open"
- [ ] Payment Status = "Pending"
- [ ] Delivery Status = "Pending"
- [ ] Total amount calculated correctly
- [ ] Supplier balance increased
- [ ] All line items saved

### After Delivery
- [ ] Received quantities updated
- [ ] Inventory stock increased
- [ ] Batches created (billable + free separate)
- [ ] Inventory transactions logged (PURCHASE_RECEIPT)
- [ ] Delivery status updated
- [ ] PO status updated if complete

### After Payment
- [ ] Amount paid updated
- [ ] Supplier balance decreased
- [ ] Payment status updated
- [ ] Payment record created
- [ ] PO status updated if complete

### After Return
- [ ] Returned quantities updated
- [ ] Inventory stock decreased
- [ ] Inventory transactions logged (PURCHASE_RETURN)
- [ ] Effective total adjusted
- [ ] Supplier balance adjusted
- [ ] Return record created

---

## Test Data Quick Reference

### Sample Suppliers
```
SUP-001: ABC Distributors (Net 30)
SUP-002: XYZ Wholesale (Net 15)
SUP-003: Quick Supply Co (COD)
```

### Sample Products
```
Laptop HP 15 (Electronics, ₹45,000)
Mouse Logitech (Electronics, ₹500)
Rice Basmati (Groceries, ₹50/Kg)
```

### Sample Schemes
```
Buy 10 Get 2 Free (Same Product)
10% Discount on quantity > 50
Flat ₹500 discount on order > ₹10,000
```

---

## Common Formulas

### Total Amount
```
total = SUM((quantity × unit_price × uom_factor) - discount)
```

### Effective TP
```
effective_tp = (gross_price - discount) / (quantity + free_quantity)
```

### Supplier Balance
```
balance += PO_total
balance -= payment_amount
balance -= return_amount
```

### Pending Quantity
```
pending = quantity - received - rejected - returned
```

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| PO not in list | Check filters, company, permissions |
| Can't record delivery | Check PO status, permissions, location |
| Payment validation error | Check amount ≤ pending amount |
| Scheme not applying | Check eligibility, active status |
| Inventory not updating | Check delivery success, location |
| Balance incorrect | Review all transactions, reconcile |

---

## Performance Targets

| Operation | Target Time |
|-----------|-------------|
| PO List Load | < 2 seconds |
| PO Create | < 3 seconds |
| Delivery Record | < 2 seconds |
| Payment Record | < 1 second |
| Report Generation | < 5 seconds |

---

## Test Execution Priority

### P1 - Critical (Must Pass)
- TC 1-6: PO Creation
- TC 7-12: Delivery
- TC 13-16: Payment
- TC 71: Complete Lifecycle

### P2 - High (Should Pass)
- TC 17-20: Returns
- TC 27-32: Schemes
- TC 41-60: Edge Cases
- TC 65-70: Security

### P3 - Medium (Nice to Pass)
- TC 21-23: Cancellation
- TC 33-40: Reports
- TC 61-64: Performance

### P4 - Low (Optional)
- TC 24-26: Supplier Management
- TC 72-80: Complex Scenarios

---

## Quick Status Reference

### PO Status Values
- **Open**: Initial state, no activity
- **Partial**: Some delivery or payment done
- **Completed**: Both delivery and payment complete
- **Cancelled**: PO cancelled

### Payment Status Values
- **Pending**: No payment made
- **Partial**: Some payment made
- **Completed**: Fully paid

### Delivery Status Values
- **Pending**: No delivery recorded
- **Partial**: Some items received
- **Completed**: All items received/rejected

---

## Browser Support

| Browser | Status |
|---------|--------|
| Chrome 120+ | ✅ Recommended |
| Firefox 120+ | ✅ Recommended |
| Edge 120+ | ✅ Supported |
| Safari 17+ | ⚠️ Limited |

---

## Contact for Issues

**Testing Team:** #shoudagor-testing  
**Technical Support:** support@shoudagor.com

---

**For detailed test cases, see:** `PURCHASE_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md`
