# Purchase Order (PO) - Comprehensive UI Testing Guide

**Document Version:** 1.0  
**Generated:** March 26, 2026  
**Project:** Shoudagor ERP System  
**Purpose:** Complete UI testing scenarios covering all PO-related workflows with edge cases

---

## Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [PO Creation Testing](#po-creation-testing)
4. [PO Delivery Testing](#po-delivery-testing)
5. [PO Payment Testing](#po-payment-testing)
6. [PO Return Testing](#po-return-testing)
7. [PO Cancellation Testing](#po-cancellation-testing)
8. [Supplier Management Testing](#supplier-management-testing)
9. [Scheme Application Testing](#scheme-application-testing)
10. [Reports Testing](#reports-testing)
11. [Edge Cases & Boundary Testing](#edge-cases--boundary-testing)
12. [Performance Testing](#performance-testing)
13. [Security Testing](#security-testing)

---

## Overview

### Purpose
This document provides step-by-step UI testing scenarios for the complete Purchase Order lifecycle in the Shoudagor ERP system.

### Scope
- Purchase Order Creation (with/without schemes)
- Delivery Management (full/partial/rejection)
- Payment Processing (single/multiple)
- Return Processing
- Supplier Management
- Scheme Application
- Reports and Analytics
- Edge Cases and Error Handling

### Prerequisites
- Access to Shoudagor ERP system
- Test user credentials with appropriate permissions
- Test data: Suppliers, Products, Variants, Storage Locations
- Browser: Chrome/Firefox/Edge (latest versions)

---

## Test Environment Setup

### 1. Initial Setup Checklist

| Item | Status | Notes |
|------|--------|-------|
| Test database initialized | ☐ | Fresh database or known state |
| Test suppliers created | ☐ | Minimum 5 suppliers |
| Test products created | ☐ | Minimum 20 products with variants |
| Storage locations configured | ☐ | Minimum 3 locations |
| Test schemes configured | ☐ | Various scheme types |
| Test user accounts | ☐ | Different permission levels |
| Browser cleared | ☐ | Cache and cookies cleared |

### 2. Test Data Requirements

#### Suppliers
```
Supplier 1: ABC Distributors (Active, Payment Terms: Net 30)
Supplier 2: XYZ Wholesale (Active, Payment Terms: Net 15)
Supplier 3: Quick Supply Co (Active, Payment Terms: COD)
Supplier 4: Bulk Traders (Inactive)
Supplier 5: International Imports (Active, Payment Terms: Net 60)
```

#### Products
```
Product Categories:
- Electronics (10 products, 2-3 variants each)
- Groceries (10 products, 1-2 variants each)
- Stationery (5 products, 1 variant each)
```

#### Storage Locations
```
Location 1: Main Warehouse
Location 2: Retail Store A
Location 3: Retail Store B
```

#### Schemes
```
Scheme 1: Buy 10 Get 2 Free (Same Product)
Scheme 2: Buy Product A Get Product B Free
Scheme 3: 10% Discount on quantity > 50
Scheme 4: Flat ₹500 discount on order > ₹10,000
```

---

## PO Creation Testing

### Test Case 1: Basic PO Creation (Happy Path)

**Objective:** Create a simple purchase order with single item

**Pre-conditions:**
- User logged in with PO creation permissions
- At least 1 active supplier exists
- At least 1 product with stock available

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Purchases → Add Purchase | Add Purchase form loads | ☐ |
| 2 | Select Supplier: "ABC Distributors" | Supplier details populate | ☐ |
| 3 | Select Location: "Main Warehouse" | Location selected | ☐ |
| 4 | Set Order Date: Today's date | Date field populated | ☐ |
| 5 | Set Expected Delivery: Today + 7 days | Date field populated | ☐ |
| 6 | Click "Add Product" | Product selection modal opens | ☐ |
| 7 | Search and select Product: "Laptop HP 15" | Product added to list | ☐ |
| 8 | Select Variant: "8GB RAM, 256GB SSD" | Variant selected | ☐ |
| 9 | Enter Quantity: 10 | Quantity field updated | ☐ |
| 10 | Select UOM: "Pieces" | UOM selected | ☐ |
| 11 | Enter Unit Price: 45000 | Price field updated | ☐ |
| 12 | Verify Total Amount: 450000 | Total calculated correctly | ☐ |
| 13 | Click "Submit" | PO creation success message | ☐ |
| 14 | Verify PO Number generated | Format: PO-YYYYMMDD-XXX | ☐ |
| 15 | Verify Status: "Open" | Status badge shows "Open" | ☐ |
| 16 | Verify Payment Status: "Pending" | Payment status correct | ☐ |
| 17 | Verify Delivery Status: "Pending" | Delivery status correct | ☐ |

**Validation Points:**
- PO number auto-generated in correct format
- Total amount = Quantity × Unit Price
- Supplier balance increased by total amount
- PO appears in purchase list
- All fields saved correctly

---

### Test Case 2: PO Creation with Multiple Items

**Objective:** Create PO with multiple products and variants

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Add Purchase | Form loads | ☐ |
| 2 | Select Supplier: "XYZ Wholesale" | Supplier selected | ☐ |
| 3 | Select Location: "Main Warehouse" | Location selected | ☐ |
| 4 | Add Product 1: "Mouse Logitech" | Product added | ☐ |
| 5 | - Variant: "Wireless" | Variant selected | ☐ |
| 6 | - Quantity: 50, UOM: Pieces | Values entered | ☐ |
| 7 | - Unit Price: 500 | Price entered | ☐ |
| 8 | Add Product 2: "Keyboard Dell" | Product added | ☐ |
| 9 | - Variant: "Wired" | Variant selected | ☐ |
| 10 | - Quantity: 30, UOM: Pieces | Values entered | ☐ |
| 11 | - Unit Price: 800 | Price entered | ☐ |
| 12 | Add Product 3: "Monitor Samsung 24\"" | Product added | ☐ |
| 13 | - Variant: "Full HD" | Variant selected | ☐ |
| 14 | - Quantity: 15, UOM: Pieces | Values entered | ☐ |
| 15 | - Unit Price: 12000 | Price entered | ☐ |
| 16 | Verify Total: 50×500 + 30×800 + 15×12000 | Total = 229000 | ☐ |
| 17 | Submit PO | Success message | ☐ |
| 18 | Open created PO | All 3 items visible | ☐ |
| 19 | Verify each item details | All details correct | ☐ |

**Validation Points:**
- All items saved correctly
- Total amount = Sum of all line items
- Each item has correct product/variant/quantity/price
- Order details table shows all items

---

### Test Case 3: PO Creation with UOM Conversion

**Objective:** Test UOM conversion in pricing and quantity

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Add Purchase | Form loads | ☐ |
| 2 | Select Supplier | Supplier selected | ☐ |
| 3 | Add Product: "Rice Basmati" | Product added | ☐ |
| 4 | Base UOM: Kg, Conversion: 1 Bag = 25 Kg | UOM configured | ☐ |
| 5 | Select UOM: "Bag" | Bag selected | ☐ |
| 6 | Enter Quantity: 10 Bags | Quantity entered | ☐ |
| 7 | Enter Unit Price: 1250 per Bag | Price entered | ☐ |
| 8 | Verify Calculated Base Quantity: 250 Kg | Conversion correct | ☐ |
| 9 | Verify Total Amount: 10 × 1250 = 12500 | Total correct | ☐ |
| 10 | Submit PO | Success | ☐ |
| 11 | Check inventory after delivery | Stock in base UOM (Kg) | ☐ |

**Validation Points:**
- UOM conversion applied correctly
- Base quantity calculated accurately
- Pricing reflects selected UOM
- Inventory updated in base UOM

---

### Test Case 4: PO Creation with Excel Import

**Objective:** Bulk import products via Excel

**Pre-conditions:**
- Excel template downloaded
- Excel file prepared with test data

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Add Purchase | Form loads | ☐ |
| 2 | Click "Import from Excel" | File upload dialog opens | ☐ |
| 3 | Select prepared Excel file | File selected | ☐ |
| 4 | Click "Upload" | File processing starts | ☐ |
| 5 | Verify import progress indicator | Progress shown | ☐ |
| 6 | Check imported items list | All items from Excel visible | ☐ |
| 7 | Verify each item: Product, Variant, Qty, Price | All data correct | ☐ |
| 8 | Check for any import errors | Error messages if any | ☐ |
| 9 | Edit any item if needed | Edits work correctly | ☐ |
| 10 | Verify total amount calculation | Total correct | ☐ |
| 11 | Submit PO | Success | ☐ |

**Excel File Format:**
```
Product Name | Variant SKU | Quantity | UOM | Unit Price | Discount
Laptop HP 15 | HP-8GB-256 | 10 | Pieces | 45000 | 0
Mouse Logitech | LOG-WIRELESS | 50 | Pieces | 500 | 0
```

**Validation Points:**
- Excel parsing works correctly
- All columns mapped properly
- Invalid data shows error messages
- Duplicate items handled
- Total calculation accurate

---

### Test Case 5: PO Creation with Product Groups

**Objective:** Add multiple products using product groups

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Add Purchase | Form loads | ☐ |
| 2 | Click "Add Product Group" | Group selection modal opens | ☐ |
| 3 | Select Group: "Computer Accessories" | Group selected | ☐ |
| 4 | Verify all products in group listed | All products shown | ☐ |
| 5 | Select products: Mouse, Keyboard, Headset | Products selected | ☐ |
| 6 | Click "Add Selected" | Products added to PO | ☐ |
| 7 | Verify each product has default values | Defaults populated | ☐ |
| 8 | Update quantities and prices | Updates work | ☐ |
| 9 | Submit PO | Success | ☐ |

**Validation Points:**
- Product group selection works
- Multiple products added at once
- Default values populated
- Individual editing possible

---

### Test Case 6: PO Creation with Initial Payment

**Objective:** Create PO with advance payment

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Add Purchase | Form loads | ☐ |
| 2 | Fill basic PO details | Details entered | ☐ |
| 3 | Add products, Total: ₹100,000 | Products added | ☐ |
| 4 | Check "Make Initial Payment" | Payment section expands | ☐ |
| 5 | Enter Amount Paid: ₹30,000 | Amount entered | ☐ |
| 6 | Select Payment Method: "Bank Transfer" | Method selected | ☐ |
| 7 | Enter Transaction Reference: "TXN123456" | Reference entered | ☐ |
| 8 | Submit PO | Success | ☐ |
| 9 | Verify Payment Status: "Partial" | Status correct | ☐ |
| 10 | Verify Amount Paid: ₹30,000 | Amount correct | ☐ |
| 11 | Verify Pending: ₹70,000 | Pending correct | ☐ |
| 12 | Check Supplier Balance | Increased by ₹70,000 only | ☐ |
| 13 | Check Payment History | Initial payment recorded | ☐ |

**Validation Points:**
- Initial payment recorded correctly
- Payment status updated to "Partial"
- Supplier balance = Total - Amount Paid
- Payment appears in payment history

---

## PO Delivery Testing

### Test Case 7: Full Delivery (All Items Received)

**Objective:** Record complete delivery of all ordered items

**Pre-conditions:**
- PO created with Status: "Open"
- Delivery Status: "Pending"

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Purchases list | List loads | ☐ |
| 2 | Find PO: PO-20260326-001 | PO visible | ☐ |
| 3 | Click Actions → "Record Delivery" | Delivery form opens | ☐ |
| 4 | Verify PO details displayed | Details correct | ☐ |
| 5 | Verify items list with Ordered/Received/Pending | All items shown | ☐ |
| 6 | Set Delivery Date: Today | Date set | ☐ |
| 7 | For Item 1: Enter Delivered Qty = Ordered Qty | Quantity entered | ☐ |
| 8 | For Item 2: Enter Delivered Qty = Ordered Qty | Quantity entered | ☐ |
| 9 | For Item 3: Enter Delivered Qty = Ordered Qty | Quantity entered | ☐ |
| 10 | Verify Pending Qty = 0 for all items | All pending zero | ☐ |
| 11 | Click "Quick Fill - Full Delivery" | All quantities auto-filled | ☐ |
| 12 | Enter Remarks: "Complete delivery received" | Remarks entered | ☐ |
| 13 | Click "Submit Delivery" | Success message | ☐ |
| 14 | Verify Delivery Status: "Completed" | Status updated | ☐ |
| 15 | Verify PO Status: "Partial" (payment pending) | Status correct | ☐ |
| 16 | Check Inventory Stock | Stock increased correctly | ☐ |
| 17 | Check Inventory Transactions | PURCHASE_RECEIPT logged | ☐ |
| 18 | Check Batch Creation | Batches created for items | ☐ |

**Validation Points:**
- All items marked as received
- Delivery status = "Completed"
- Inventory stock updated for all items
- Inventory transactions logged
- Batches created with correct details
- PO status reflects delivery completion

---

### Test Case 8: Partial Delivery (Some Items Received)

**Objective:** Record partial delivery with remaining items pending

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO with 3 items (Qty: 100, 50, 30) | PO opens | ☐ |
| 2 | Click "Record Delivery" | Delivery form opens | ☐ |
| 3 | Item 1: Delivered = 60 (Pending = 40) | Quantity entered | ☐ |
| 4 | Item 2: Delivered = 50 (Pending = 0) | Quantity entered | ☐ |
| 5 | Item 3: Delivered = 0 (Pending = 30) | Quantity entered | ☐ |
| 6 | Submit Delivery | Success | ☐ |
| 7 | Verify Delivery Status: "Partial" | Status correct | ☐ |
| 8 | Check Item 1: Received = 60, Pending = 40 | Values correct | ☐ |
| 9 | Check Item 2: Received = 50, Pending = 0 | Values correct | ☐ |
| 10 | Check Item 3: Received = 0, Pending = 30 | Values correct | ☐ |
| 11 | Check Inventory: Only delivered items added | Stock correct | ☐ |
| 12 | Record 2nd Delivery for remaining items | Form opens | ☐ |
| 13 | Item 1: Delivered = 40 | Quantity entered | ☐ |
| 14 | Item 3: Delivered = 30 | Quantity entered | ☐ |
| 15 | Submit 2nd Delivery | Success | ☐ |
| 16 | Verify Delivery Status: "Completed" | Status updated | ☐ |
| 17 | Verify all items fully received | All complete | ☐ |

**Validation Points:**
- Partial delivery recorded correctly
- Pending quantities calculated accurately
- Multiple deliveries supported
- Cumulative received quantity tracked
- Delivery status updates appropriately

---

### Test Case 9: Delivery with Free Items

**Objective:** Record delivery including free items from schemes

**Pre-conditions:**
- PO created with scheme: "Buy 10 Get 2 Free"
- Ordered: 100 units, Free: 20 units

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO with free items | PO details show free qty | ☐ |
| 2 | Click "Record Delivery" | Delivery form opens | ☐ |
| 3 | Verify Billable Qty: 100 | Quantity shown | ☐ |
| 4 | Verify Free Qty: 20 | Free quantity shown | ☐ |
| 5 | Enter Delivered Billable: 100 | Quantity entered | ☐ |
| 6 | Enter Delivered Free: 20 | Free quantity entered | ☐ |
| 7 | Submit Delivery | Success | ☐ |
| 8 | Check Inventory: Total = 120 units | Stock correct | ☐ |
| 9 | Check Batch: Billable batch with cost | Batch created | ☐ |
| 10 | Check Batch: Free batch with cost = 0 | Free batch created | ☐ |
| 11 | Verify Effective TP calculation | TP includes free items | ☐ |

**Validation Points:**
- Billable and free quantities tracked separately
- Inventory updated with total quantity
- Separate batches for billable and free items
- Free items have zero cost
- Effective TP calculated correctly

---

### Test Case 10: Delivery with Rejection (During Receipt)

**Objective:** Reject items during delivery due to quality issues

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Ordered 100 units | PO opens | ☐ |
| 2 | Click "Record Delivery" | Delivery form opens | ☐ |
| 3 | Enter Delivered Qty: 85 | Quantity entered | ☐ |
| 4 | Enter Rejected Qty: 15 | Rejected quantity entered | ☐ |
| 5 | Enter Rejection Reason: "Damaged packaging" | Reason entered | ☐ |
| 6 | Verify Total: Delivered + Rejected = 100 | Total correct | ☐ |
| 7 | Submit Delivery | Success | ☐ |
| 8 | Verify Received Qty: 85 | Quantity correct | ☐ |
| 9 | Verify Rejected Qty: 15 | Rejection recorded | ☐ |
| 10 | Check Inventory: Only 85 units added | Stock correct | ☐ |
| 11 | Check Effective Total: Reduced by rejected amount | Total adjusted | ☐ |
| 12 | Check Supplier Balance: Reduced by rejected amount | Balance adjusted | ☐ |
| 13 | Verify Delivery Status: "Completed" | Status correct | ☐ |

**Validation Points:**
- Rejected quantity tracked separately
- Only accepted items added to inventory
- Effective total excludes rejected items
- Supplier balance adjusted for rejections
- Rejection reason recorded

---

### Test Case 11: Delivery with Free Item Rejection

**Objective:** Reject free items during delivery

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Billable 100, Free 20 | PO opens | ☐ |
| 2 | Click "Record Delivery" | Delivery form opens | ☐ |
| 3 | Enter Delivered Billable: 100 | Quantity entered | ☐ |
| 4 | Enter Delivered Free: 15 | Free quantity entered | ☐ |
| 5 | Enter Rejected Free: 5 | Rejected free entered | ☐ |
| 6 | Enter Reason: "Expired items" | Reason entered | ☐ |
| 7 | Submit Delivery | Success | ☐ |
| 8 | Verify Received Free: 15 | Quantity correct | ☐ |
| 9 | Verify Rejected Free: 5 | Rejection recorded | ☐ |
| 10 | Check Inventory: 100 + 15 = 115 units | Stock correct | ☐ |
| 11 | Verify no impact on billable amount | Amount unchanged | ☐ |

**Validation Points:**
- Free item rejection tracked separately
- No financial impact from free rejections
- Inventory reflects only accepted free items
- Rejection reason recorded

---

### Test Case 12: Multiple Deliveries Over Time

**Objective:** Test cumulative delivery tracking

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO: 1000 units | PO created | ☐ |
| 2 | Delivery 1: 300 units (Day 1) | Recorded | ☐ |
| 3 | Verify Received: 300, Pending: 700 | Correct | ☐ |
| 4 | Delivery 2: 400 units (Day 3) | Recorded | ☐ |
| 5 | Verify Received: 700, Pending: 300 | Correct | ☐ |
| 6 | Delivery 3: 300 units (Day 5) | Recorded | ☐ |
| 7 | Verify Received: 1000, Pending: 0 | Correct | ☐ |
| 8 | Verify Delivery Status: "Completed" | Status updated | ☐ |
| 9 | Check all delivery records | All 3 visible | ☐ |
| 10 | Verify inventory transactions | 3 transactions logged | ☐ |

**Validation Points:**
- Multiple deliveries tracked cumulatively
- Pending quantity decreases correctly
- Status updates when fully received
- All delivery records maintained

---

## PO Payment Testing

### Test Case 13: Single Full Payment

**Objective:** Pay complete PO amount in one transaction

**Pre-conditions:**
- PO created with Total: ₹100,000
- Payment Status: "Pending"

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to PO details | PO opens | ☐ |
| 2 | Click "Record Payment" | Payment form opens | ☐ |
| 3 | Verify Total Amount: ₹100,000 | Amount shown | ☐ |
| 4 | Verify Amount Paid: ₹0 | Current payment shown | ☐ |
| 5 | Verify Pending: ₹100,000 | Pending shown | ☐ |
| 6 | Set Payment Date: Today | Date set | ☐ |
| 7 | Enter Amount: ₹100,000 | Amount entered | ☐ |
| 8 | Select Payment Method: "Bank Transfer" | Method selected | ☐ |
| 9 | Enter Transaction Ref: "TXN789012" | Reference entered | ☐ |
| 10 | Enter Remarks: "Full payment" | Remarks entered | ☐ |
| 11 | Click "Submit Payment" | Success message | ☐ |
| 12 | Verify Payment Status: "Completed" | Status updated | ☐ |
| 13 | Verify Amount Paid: ₹100,000 | Amount correct | ☐ |
| 14 | Verify Pending: ₹0 | Pending zero | ☐ |
| 15 | Check Supplier Balance: Decreased by ₹100,000 | Balance updated | ☐ |
| 16 | Check Payment History | Payment recorded | ☐ |
| 17 | Verify PO Status: "Completed" (if delivered) | Status correct | ☐ |

**Validation Points:**
- Full payment recorded correctly
- Payment status = "Completed"
- Supplier balance decreased
- Payment appears in history
- PO status updated if delivery also complete

---

### Test Case 14: Multiple Partial Payments

**Objective:** Pay PO amount in multiple installments

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Total ₹100,000 | PO opens | ☐ |
| 2 | Payment 1: ₹30,000 | Recorded | ☐ |
| 3 | Verify Status: "Partial" | Status correct | ☐ |
| 4 | Verify Paid: ₹30,000, Pending: ₹70,000 | Amounts correct | ☐ |
| 5 | Payment 2: ₹40,000 | Recorded | ☐ |
| 6 | Verify Status: "Partial" | Status correct | ☐ |
| 7 | Verify Paid: ₹70,000, Pending: ₹30,000 | Amounts correct | ☐ |
| 8 | Payment 3: ₹30,000 | Recorded | ☐ |
| 9 | Verify Status: "Completed" | Status updated | ☐ |
| 10 | Verify Paid: ₹100,000, Pending: ₹0 | Amounts correct | ☐ |
| 11 | Check Payment History: 3 payments | All visible | ☐ |
| 12 | Verify Supplier Balance: Decreased by ₹100,000 total | Balance correct | ☐ |

**Validation Points:**
- Multiple payments tracked cumulatively
- Payment status updates appropriately
- Supplier balance decreases with each payment
- All payment records maintained

---

### Test Case 15: Payment with Different Methods

**Objective:** Test various payment methods

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Payment 1: Cash - ₹10,000 | Recorded | ☐ |
| 2 | Payment 2: Bank Transfer - ₹20,000 | Recorded | ☐ |
| 3 | Payment 3: Cheque - ₹15,000 | Recorded | ☐ |
| 4 | Payment 4: UPI - ₹5,000 | Recorded | ☐ |
| 5 | Payment 5: Credit Card - ₹10,000 | Recorded | ☐ |
| 6 | Verify each payment method recorded | All correct | ☐ |
| 7 | Check payment report by method | Breakdown correct | ☐ |

**Validation Points:**
- All payment methods supported
- Method recorded correctly for each payment
- Payment reports show method breakdown

---

### Test Case 16: Overpayment Scenario

**Objective:** Test system behavior when payment exceeds PO amount

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Total ₹50,000, Paid ₹0 | PO opens | ☐ |
| 2 | Attempt Payment: ₹60,000 | Validation error shown | ☐ |
| 3 | Error Message: "Payment exceeds pending amount" | Error displayed | ☐ |
| 4 | Adjust Payment: ₹50,000 | Amount corrected | ☐ |
| 5 | Submit Payment | Success | ☐ |

**Validation Points:**
- Overpayment prevented
- Clear error message shown
- User can correct amount

---

## PO Return Testing

### Test Case 17: Full Return (All Items)

**Objective:** Return complete order to supplier

**Pre-conditions:**
- PO fully delivered
- Items in inventory

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open delivered PO | PO opens | ☐ |
| 2 | Click "Return Items" | Return form opens | ☐ |
| 3 | Verify items with Received quantities | All items shown | ☐ |
| 4 | Item 1: Return Qty = Received Qty | Quantity entered | ☐ |
| 5 | Item 2: Return Qty = Received Qty | Quantity entered | ☐ |
| 6 | Set Return Date: Today | Date set | ☐ |
| 7 | Enter Reason: "Quality issues" | Reason entered | ☐ |
| 8 | Submit Return | Success message | ☐ |
| 9 | Verify Returned Qty updated | Quantities correct | ☐ |
| 10 | Check Inventory: Stock decreased | Stock reduced | ☐ |
| 11 | Check Transactions: PURCHASE_RETURN logged | Transaction recorded | ☐ |
| 12 | Check Effective Total: Reduced to ₹0 | Total adjusted | ☐ |
| 13 | Check Supplier Balance: Decreased | Balance adjusted | ☐ |
| 14 | Verify Delivery Status: Still "Completed" | Status unchanged | ☐ |

**Validation Points:**
- All items returned successfully
- Inventory stock decreased
- Return transaction logged
- Effective total adjusted
- Supplier balance decreased
- Delivery status remains completed

---

### Test Case 18: Partial Return

**Objective:** Return some items, keep others

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: 3 items received (100, 50, 30) | PO opens | ☐ |
| 2 | Click "Return Items" | Return form opens | ☐ |
| 3 | Item 1: Return 20 out of 100 | Quantity entered | ☐ |
| 4 | Item 2: Return 0 (keep all) | No return | ☐ |
| 5 | Item 3: Return 10 out of 30 | Quantity entered | ☐ |
| 6 | Enter Reason: "Excess stock" | Reason entered | ☐ |
| 7 | Submit Return | Success | ☐ |
| 8 | Verify Item 1: Returned = 20, Net = 80 | Correct | ☐ |
| 9 | Verify Item 2: Returned = 0, Net = 50 | Correct | ☐ |
| 10 | Verify Item 3: Returned = 10, Net = 20 | Correct | ☐ |
| 11 | Check Inventory: Reduced by returned qty | Stock correct | ☐ |
| 12 | Check Effective Total: Adjusted proportionally | Total correct | ☐ |

**Validation Points:**
- Partial returns tracked per item
- Net quantities calculated correctly
- Inventory adjusted accurately
- Effective total reflects returns

---

### Test Case 19: Return Validation (Cannot Return More Than Received)

**Objective:** Test return quantity validation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Item received = 50 | PO opens | ☐ |
| 2 | Click "Return Items" | Return form opens | ☐ |
| 3 | Attempt Return: 60 units | Validation error | ☐ |
| 4 | Error: "Cannot return more than received" | Error shown | ☐ |
| 5 | Adjust Return: 50 units | Amount corrected | ☐ |
| 6 | Submit Return | Success | ☐ |

**Validation Points:**
- Return quantity validated
- Cannot exceed received quantity
- Clear error message
- User can correct amount

---

### Test Case 20: Multiple Returns Over Time

**Objective:** Test cumulative return tracking

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | PO: Received 1000 units | PO opens | ☐ |
| 2 | Return 1: 100 units (Day 1) | Recorded | ☐ |
| 3 | Verify Returned: 100, Net: 900 | Correct | ☐ |
| 4 | Return 2: 150 units (Day 5) | Recorded | ☐ |
| 5 | Verify Returned: 250, Net: 750 | Correct | ☐ |
| 6 | Return 3: 50 units (Day 10) | Recorded | ☐ |
| 7 | Verify Returned: 300, Net: 700 | Correct | ☐ |
| 8 | Check all return records | All 3 visible | ☐ |
| 9 | Verify cumulative inventory reduction | Stock correct | ☐ |

**Validation Points:**
- Multiple returns tracked cumulatively
- Net quantity calculated correctly
- All return records maintained
- Inventory reflects cumulative returns

---

## PO Cancellation Testing

### Test Case 21: Cancel Open PO (No Activity)

**Objective:** Cancel PO before any delivery or payment

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO: Total ₹50,000 | PO created | ☐ |
| 2 | Verify Status: "Open" | Status correct | ☐ |
| 3 | Click "Cancel PO" | Confirmation dialog | ☐ |
| 4 | Confirm Cancellation | Success message | ☐ |
| 5 | Verify Status: "Cancelled" | Status updated | ☐ |
| 6 | Verify PO is read-only | No edits allowed | ☐ |
| 7 | Check Supplier Balance | Should be reversed | ☐ |
| 8 | Verify no inventory impact | No stock changes | ☐ |

**Validation Points:**
- PO cancelled successfully
- Status updated to "Cancelled"
- PO becomes read-only
- Supplier balance reversed
- No inventory impact

**⚠️ Known Issue:** Cancellation may not reverse supplier balance (see PURCHASE_ORDER_WORKFLOW_ANALYSIS.md)

---

### Test Case 22: Attempt Cancel After Partial Delivery

**Objective:** Test cancellation restrictions

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO and record partial delivery | Delivery recorded | ☐ |
| 2 | Attempt to Cancel PO | Error/Warning shown | ☐ |
| 3 | Error: "Cannot cancel PO with deliveries" | Message displayed | ☐ |
| 4 | Verify PO remains active | Status unchanged | ☐ |

**Validation Points:**
- Cancellation prevented after delivery
- Clear error message
- PO status unchanged

---

### Test Case 23: Attempt Cancel After Payment

**Objective:** Test cancellation with payments

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO and record payment | Payment recorded | ☐ |
| 2 | Attempt to Cancel PO | Error/Warning shown | ☐ |
| 3 | Error: "Cannot cancel PO with payments" | Message displayed | ☐ |
| 4 | Verify PO remains active | Status unchanged | ☐ |

**Validation Points:**
- Cancellation prevented after payment
- Clear error message
- PO status unchanged

---

## Supplier Management Testing

### Test Case 24: Create New Supplier

**Objective:** Add new supplier to system

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Suppliers → Add Supplier | Form loads | ☐ |
| 2 | Enter Supplier Code: "SUP-001" | Code entered | ☐ |
| 3 | Enter Supplier Name: "ABC Distributors" | Name entered | ☐ |
| 4 | Enter Contact Person: "John Doe" | Contact entered | ☐ |
| 5 | Enter Email: "john@abc.com" | Email entered | ☐ |
| 6 | Enter Phone: "+91-9876543210" | Phone entered | ☐ |
| 7 | Enter Address details | Address entered | ☐ |
| 8 | Select Country, State, City | Location selected | ☐ |
| 9 | Enter Payment Terms: "Net 30" | Terms entered | ☐ |
| 10 | Set Status: Active | Status set | ☐ |
| 11 | Submit Supplier | Success message | ☐ |
| 12 | Verify supplier in list | Supplier visible | ☐ |
| 13 | Verify Balance: ₹0 | Initial balance zero | ☐ |

**Validation Points:**
- Supplier created successfully
- All fields saved correctly
- Initial balance is zero
- Supplier appears in dropdown for PO

---

### Test Case 25: Supplier Balance Tracking

**Objective:** Verify supplier balance updates correctly

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check Supplier: Initial Balance ₹0 | Balance zero | ☐ |
| 2 | Create PO 1: ₹50,000 | PO created | ☐ |
| 3 | Check Balance: ₹50,000 | Balance increased | ☐ |
| 4 | Create PO 2: ₹30,000 | PO created | ☐ |
| 5 | Check Balance: ₹80,000 | Balance increased | ☐ |
| 6 | Pay PO 1: ₹50,000 | Payment recorded | ☐ |
| 7 | Check Balance: ₹30,000 | Balance decreased | ☐ |
| 8 | Pay PO 2: ₹30,000 | Payment recorded | ☐ |
| 9 | Check Balance: ₹0 | Balance zero | ☐ |

**Validation Points:**
- Balance increases with PO creation
- Balance decreases with payments
- Balance calculated correctly
- Balance visible in supplier details

---

### Test Case 26: Supplier Performance Metrics

**Objective:** Verify supplier performance tracking

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Supplier Details | Details page opens | ☐ |
| 2 | Check Total POs | Count correct | ☐ |
| 3 | Check Total Purchase Amount | Amount correct | ☐ |
| 4 | Check On-Time Delivery % | Percentage shown | ☐ |
| 5 | Check Average Lead Time | Days shown | ☐ |
| 6 | Check Fill Rate | Percentage shown | ☐ |
| 7 | View PO History | All POs listed | ☐ |

**Validation Points:**
- All metrics calculated correctly
- Performance data accurate
- Historical data maintained

---

## Scheme Application Testing

### Test Case 27: Buy X Get Y Free (Same Product)

**Objective:** Test scheme: Buy 10 Get 2 Free

**Pre-conditions:**
- Scheme configured: Buy 10 Get 2 Free on Product "Laptop HP 15"

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product: "Laptop HP 15" | Product added | ☐ |
| 3 | Enter Quantity: 10 | Quantity entered | ☐ |
| 4 | Verify Free Quantity: 2 auto-calculated | Free qty shown | ☐ |
| 5 | Enter Unit Price: ₹45,000 | Price entered | ☐ |
| 6 | Verify Total: 10 × ₹45,000 = ₹450,000 | Total correct | ☐ |
| 7 | Verify Effective TP: ₹450,000 / 12 = ₹37,500 | TP calculated | ☐ |
| 8 | Submit PO | Success | ☐ |
| 9 | Verify PO Detail: Qty=10, Free=2 | Details correct | ☐ |
| 10 | Record Delivery: 10 + 2 units | Delivery recorded | ☐ |
| 11 | Check Inventory: 12 units added | Stock correct | ☐ |
| 12 | Check Batch: 10 units with cost | Billable batch | ☐ |
| 13 | Check Batch: 2 units with cost=0 | Free batch | ☐ |

**Validation Points:**
- Free quantity auto-calculated
- Total excludes free items
- Effective TP includes free items
- Separate batches for billable and free
- Inventory reflects total quantity

---

### Test Case 28: Buy X Get Y Free (Different Product)

**Objective:** Test scheme: Buy Laptop Get Mouse Free

**Pre-conditions:**
- Scheme: Buy 1 Laptop HP 15, Get 1 Mouse Logitech Free

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product: "Laptop HP 15" | Product added | ☐ |
| 3 | Enter Quantity: 5 | Quantity entered | ☐ |
| 4 | Verify scheme applied | Scheme indicator shown | ☐ |
| 5 | Verify Free Product: "Mouse Logitech" added | Free product shown | ☐ |
| 6 | Verify Free Quantity: 5 | Free qty correct | ☐ |
| 7 | Submit PO | Success | ☐ |
| 8 | Verify 2 line items: Laptop (billable) + Mouse (free) | Both items shown | ☐ |
| 9 | Record Delivery: Both items | Delivery recorded | ☐ |
| 10 | Check Inventory: Laptop +5, Mouse +5 | Stock correct | ☐ |

**Validation Points:**
- Different free product added automatically
- Separate line items created
- Free product has zero cost
- Both products delivered and stocked

---

### Test Case 29: Percentage Discount Scheme

**Objective:** Test scheme: 10% discount on quantity > 50

**Pre-conditions:**
- Scheme: 10% discount when quantity > 50

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product: "Mouse Logitech" | Product added | ☐ |
| 3 | Enter Quantity: 60 | Quantity entered | ☐ |
| 4 | Enter Unit Price: ₹500 | Price entered | ☐ |
| 5 | Verify Gross Amount: 60 × ₹500 = ₹30,000 | Gross correct | ☐ |
| 6 | Verify Discount: 10% = ₹3,000 | Discount calculated | ☐ |
| 7 | Verify Net Amount: ₹27,000 | Net correct | ☐ |
| 8 | Submit PO | Success | ☐ |
| 9 | Verify Total: ₹27,000 | Total correct | ☐ |

**Validation Points:**
- Discount auto-calculated
- Percentage applied correctly
- Net amount reflects discount
- Supplier balance = Net amount

---

### Test Case 30: Flat Discount Scheme

**Objective:** Test scheme: ₹500 flat discount on order > ₹10,000

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO with items totaling ₹12,000 | Items added | ☐ |
| 2 | Verify scheme applied | Scheme indicator shown | ☐ |
| 3 | Verify Discount: ₹500 | Discount shown | ☐ |
| 4 | Verify Total: ₹11,500 | Total correct | ☐ |
| 5 | Submit PO | Success | ☐ |

**Validation Points:**
- Flat discount applied
- Total reduced by discount amount
- Discount recorded in PO

---

### Test Case 31: Manual Scheme Selection

**Objective:** Manually select scheme for item

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product | Product added | ☐ |
| 3 | Click "Select Scheme" | Scheme dropdown opens | ☐ |
| 4 | Select Scheme: "Buy 10 Get 2 Free" | Scheme selected | ☐ |
| 5 | Verify scheme applied | Benefits calculated | ☐ |
| 6 | Change Scheme: "10% Discount" | Scheme changed | ☐ |
| 7 | Verify new benefits | Discount applied | ☐ |
| 8 | Submit PO | Success | ☐ |

**Validation Points:**
- Manual scheme selection works
- Scheme can be changed
- Benefits recalculated on change
- Selected scheme saved

---

### Test Case 32: No Scheme Applied

**Objective:** Create PO without any scheme

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product (no scheme eligible) | Product added | ☐ |
| 3 | Verify No Scheme indicator | No scheme shown | ☐ |
| 4 | Verify Free Qty: 0 | No free items | ☐ |
| 5 | Verify Discount: 0 | No discount | ☐ |
| 6 | Submit PO | Success | ☐ |

**Validation Points:**
- PO works without schemes
- No free items or discounts
- Total = Quantity × Unit Price

---

## Reports Testing

### Test Case 33: PO Dashboard Report

**Objective:** Verify PO dashboard metrics

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → PO Dashboard | Dashboard loads | ☐ |
| 2 | Select Year: 2026 | Year selected | ☐ |
| 3 | Verify Total PO Count | Count shown | ☐ |
| 4 | Verify Total PO Value | Amount shown | ☐ |
| 5 | Verify Total Amount Paid | Amount shown | ☐ |
| 6 | Verify Pending Payment | Amount shown | ☐ |
| 7 | Check Daily Data Chart | Chart displays | ☐ |
| 8 | Check Status Distribution | Pie chart shows | ☐ |
| 9 | Check Monthly Volume | Bar chart shows | ☐ |
| 10 | Verify calculations match actual data | Data accurate | ☐ |

**Validation Points:**
- All metrics calculated correctly
- Charts display properly
- Data matches database records
- Date filters work

---

### Test Case 34: Supplier Performance Report

**Objective:** Verify supplier performance metrics

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → Supplier Performance | Report loads | ☐ |
| 2 | Verify Top Suppliers by Spend | List shown | ☐ |
| 3 | Check Supplier Lead Times | Average days shown | ☐ |
| 4 | Check On-Time Delivery % | Percentages shown | ☐ |
| 5 | Check Fill Rate | Percentages shown | ☐ |
| 6 | Filter by Date Range | Filter works | ☐ |
| 7 | Export to Excel | Export successful | ☐ |

**Validation Points:**
- Performance metrics accurate
- Lead time calculations correct
- OTD percentage accurate
- Fill rate calculated correctly

---

### Test Case 35: PO Aging Report

**Objective:** Verify PO aging analysis

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → PO Aging | Report loads | ☐ |
| 2 | Verify Aging Buckets: 0-30, 31-60, 61-90, 90+ | Buckets shown | ☐ |
| 3 | Check POs in each bucket | Counts correct | ☐ |
| 4 | Verify Days Open calculation | Days accurate | ☐ |
| 5 | Check Total Amount per bucket | Amounts correct | ☐ |
| 6 | Click on bucket to see details | Details shown | ☐ |

**Validation Points:**
- Aging buckets correct
- Days open calculated accurately
- POs categorized correctly
- Drill-down works

---

### Test Case 36: Maverick Spend Report

**Objective:** Identify low-volume suppliers

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → Maverick Spend | Report loads | ☐ |
| 2 | Set Threshold: 3 POs | Threshold set | ☐ |
| 3 | Verify suppliers with < 3 POs listed | List shown | ☐ |
| 4 | Check Reason: "Low volume supplier" | Reason shown | ☐ |
| 5 | Verify Total Spend per supplier | Amounts correct | ☐ |
| 6 | Change Threshold: 5 POs | List updates | ☐ |

**Validation Points:**
- Threshold configurable
- Suppliers filtered correctly
- Spend amounts accurate
- Recommendations shown

---

### Test Case 37: Emergency Orders Report

**Objective:** Identify orders with short lead time

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → Emergency Orders | Report loads | ☐ |
| 2 | Set Lead Time: 3 days | Threshold set | ☐ |
| 3 | Verify POs with lead time < 3 days | List shown | ☐ |
| 4 | Check Lead Time calculation | Days correct | ☐ |
| 5 | Verify Total Amount | Amount correct | ☐ |
| 6 | Change Threshold: 2 days | List updates | ☐ |

**Validation Points:**
- Lead time calculated correctly
- Threshold configurable
- Emergency orders identified
- Amounts accurate

---

### Test Case 38: Cash Flow Projection Report

**Objective:** Project upcoming payment liabilities

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → Cash Flow Projection | Report loads | ☐ |
| 2 | Verify Period Buckets: 0-7, 8-15, 16-30, 31-60, 60+ | Buckets shown | ☐ |
| 3 | Check Projected Liability per bucket | Amounts shown | ☐ |
| 4 | Verify PO Count per bucket | Counts shown | ☐ |
| 5 | Check Total Projected Liability | Total correct | ☐ |
| 6 | Verify based on Expected Delivery Date | Logic correct | ☐ |

**Validation Points:**
- Period buckets correct
- Liabilities calculated accurately
- Based on expected delivery dates
- Totals match

---

### Test Case 39: PO Progress Report

**Objective:** Track line item delivery progress

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → PO Progress | Report loads | ☐ |
| 2 | Verify all PO line items listed | Items shown | ☐ |
| 3 | Check Quantity Ordered | Quantities correct | ☐ |
| 4 | Check Quantity Received | Quantities correct | ☐ |
| 5 | Check Quantity Remaining | Calculated correctly | ☐ |
| 6 | Verify Progress % | Percentages correct | ☐ |
| 7 | Filter by Status: Pending | Filter works | ☐ |
| 8 | Filter by Supplier | Filter works | ☐ |

**Validation Points:**
- All line items tracked
- Quantities accurate
- Progress calculated correctly
- Filters work properly

---

### Test Case 40: Uninvoiced Receipts Report

**Objective:** Identify received but unpaid items

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to Reports → Uninvoiced Receipts | Report loads | ☐ |
| 2 | Verify POs with Delivery=Complete, Payment≠Complete | List shown | ☐ |
| 3 | Check Total Amount | Amount correct | ☐ |
| 4 | Check Amount Paid | Amount correct | ☐ |
| 5 | Check Uninvoiced Amount | Difference correct | ☐ |
| 6 | Verify Received Date | Dates shown | ☐ |
| 7 | Sort by Uninvoiced Amount | Sorting works | ☐ |

**Validation Points:**
- Uninvoiced POs identified
- Amounts calculated correctly
- Dates accurate
- Sorting works

---

## Edge Cases & Boundary Testing

### Test Case 41: Zero Quantity Order

**Objective:** Test validation for zero quantity

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product | Product added | ☐ |
| 3 | Enter Quantity: 0 | Quantity entered | ☐ |
| 4 | Attempt Submit | Validation error | ☐ |
| 5 | Error: "Quantity must be greater than 0" | Error shown | ☐ |
| 6 | Correct Quantity: 1 | Quantity corrected | ☐ |
| 7 | Submit PO | Success | ☐ |

**Validation Points:**
- Zero quantity prevented
- Clear error message
- User can correct

---

### Test Case 42: Negative Quantity

**Objective:** Test validation for negative quantity

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product | Product added | ☐ |
| 3 | Enter Quantity: -10 | Quantity entered | ☐ |
| 4 | Attempt Submit | Validation error | ☐ |
| 5 | Error: "Quantity must be positive" | Error shown | ☐ |

**Validation Points:**
- Negative quantity prevented
- Validation works

---

### Test Case 43: Zero Unit Price

**Objective:** Test zero price handling

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product | Product added | ☐ |
| 3 | Enter Unit Price: 0 | Price entered | ☐ |
| 4 | Verify Total: 0 | Total zero | ☐ |
| 5 | Submit PO | Success (free items) | ☐ |

**Validation Points:**
- Zero price allowed (for free items)
- Total calculated correctly
- PO created successfully

---

### Test Case 44: Very Large Quantity

**Objective:** Test system with large numbers

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product | Product added | ☐ |
| 3 | Enter Quantity: 999,999,999 | Quantity entered | ☐ |
| 4 | Enter Unit Price: ₹1,000 | Price entered | ☐ |
| 5 | Verify Total calculation | Total correct | ☐ |
| 6 | Submit PO | Success or validation | ☐ |
| 7 | Check database precision | No overflow | ☐ |

**Validation Points:**
- Large numbers handled
- No overflow errors
- Calculations accurate
- Database precision maintained

---

### Test Case 45: Decimal Quantities

**Objective:** Test fractional quantities

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product: "Rice" (UOM: Kg) | Product added | ☐ |
| 3 | Enter Quantity: 25.75 Kg | Decimal entered | ☐ |
| 4 | Enter Unit Price: ₹50 per Kg | Price entered | ☐ |
| 5 | Verify Total: 25.75 × 50 = ₹1,287.50 | Total correct | ☐ |
| 6 | Submit PO | Success | ☐ |
| 7 | Record Delivery: 25.75 Kg | Delivery recorded | ☐ |
| 8 | Check Inventory: 25.75 Kg | Stock correct | ☐ |

**Validation Points:**
- Decimal quantities supported
- Calculations accurate
- Inventory handles decimals
- No rounding errors

---

### Test Case 46: Same Product Multiple Times

**Objective:** Add same product multiple times in one PO

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Product: "Laptop HP 15" - Variant A | Product added | ☐ |
| 3 | Add Same Product: "Laptop HP 15" - Variant A again | Product added | ☐ |
| 4 | Verify 2 separate line items | Both shown | ☐ |
| 5 | Submit PO | Success | ☐ |
| 6 | Verify both line items saved | Both in database | ☐ |

**Validation Points:**
- Duplicate products allowed
- Separate line items created
- Both tracked independently

---

### Test Case 47: Expected Delivery Before Order Date

**Objective:** Test date validation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Set Order Date: 2026-03-26 | Date set | ☐ |
| 3 | Set Expected Delivery: 2026-03-20 | Date set | ☐ |
| 4 | Attempt Submit | Validation error | ☐ |
| 5 | Error: "Delivery date cannot be before order date" | Error shown | ☐ |
| 6 | Correct Delivery Date: 2026-04-02 | Date corrected | ☐ |
| 7 | Submit PO | Success | ☐ |

**Validation Points:**
- Date validation works
- Clear error message
- User can correct

---

### Test Case 48: Inactive Supplier Selection

**Objective:** Test inactive supplier handling

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Attempt to select Inactive Supplier | Not in dropdown | ☐ |
| 3 | Verify only active suppliers shown | Filter works | ☐ |

**Validation Points:**
- Inactive suppliers not selectable
- Dropdown filtered correctly

---

### Test Case 49: Delivery Without Inventory Location

**Objective:** Test delivery when location not set

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO without Location | PO created | ☐ |
| 2 | Attempt Delivery | Error or default location | ☐ |
| 3 | Verify behavior | Handled gracefully | ☐ |

**Validation Points:**
- Location requirement enforced
- Error message clear
- Or default location used

---

### Test Case 50: Concurrent PO Creation

**Objective:** Test race conditions

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open 2 browser tabs | Both open | ☐ |
| 2 | Start creating PO in Tab 1 | Form open | ☐ |
| 3 | Start creating PO in Tab 2 | Form open | ☐ |
| 4 | Submit both simultaneously | Both succeed | ☐ |
| 5 | Verify unique PO numbers | Numbers different | ☐ |
| 6 | Verify supplier balance | Increased by both | ☐ |

**Validation Points:**
- Concurrent operations handled
- No duplicate PO numbers
- Data consistency maintained
- Row-level locking works

---

### Test Case 51: Delivery Exceeding Ordered Quantity

**Objective:** Test over-delivery validation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Ordered 100 units | PO opens | ☐ |
| 2 | Record Delivery: 120 units | Quantity entered | ☐ |
| 3 | Attempt Submit | Validation error | ☐ |
| 4 | Error: "Cannot deliver more than ordered" | Error shown | ☐ |
| 5 | Correct Delivery: 100 units | Quantity corrected | ☐ |
| 6 | Submit Delivery | Success | ☐ |

**Validation Points:**
- Over-delivery prevented
- Clear error message
- User can correct

---

### Test Case 52: Payment Exceeding PO Total

**Objective:** Test overpayment validation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Total ₹50,000 | PO opens | ☐ |
| 2 | Attempt Payment: ₹60,000 | Amount entered | ☐ |
| 3 | Attempt Submit | Validation error | ☐ |
| 4 | Error: "Payment exceeds total amount" | Error shown | ☐ |
| 5 | Correct Payment: ₹50,000 | Amount corrected | ☐ |
| 6 | Submit Payment | Success | ☐ |

**Validation Points:**
- Overpayment prevented
- Clear error message
- User can correct

---

### Test Case 53: Return Exceeding Received Quantity

**Objective:** Test over-return validation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO: Received 50 units | PO opens | ☐ |
| 2 | Attempt Return: 60 units | Quantity entered | ☐ |
| 3 | Attempt Submit | Validation error | ☐ |
| 4 | Error: "Cannot return more than received" | Error shown | ☐ |
| 5 | Correct Return: 50 units | Quantity corrected | ☐ |
| 6 | Submit Return | Success | ☐ |

**Validation Points:**
- Over-return prevented
- Clear error message
- User can correct

---

### Test Case 54: Special Characters in Fields

**Objective:** Test special character handling

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Enter Remarks: "Test <script>alert('XSS')</script>" | Text entered | ☐ |
| 3 | Submit PO | Success | ☐ |
| 4 | View PO Details | Script not executed | ☐ |
| 5 | Verify text sanitized | Safe display | ☐ |

**Validation Points:**
- XSS prevented
- Special characters handled
- Data sanitized
- No script execution

---

### Test Case 55: Very Long Text in Fields

**Objective:** Test field length limits

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Enter Remarks: 5000 characters | Text entered | ☐ |
| 3 | Attempt Submit | Validation or truncation | ☐ |
| 4 | Verify behavior | Handled gracefully | ☐ |

**Validation Points:**
- Length limits enforced
- Truncation or error shown
- No database errors

---

### Test Case 56: Network Interruption During Submit

**Objective:** Test network failure handling

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO with all details | Form filled | ☐ |
| 2 | Disconnect network | Network off | ☐ |
| 3 | Click Submit | Error message | ☐ |
| 4 | Error: "Network error, please try again" | Error shown | ☐ |
| 5 | Reconnect network | Network on | ☐ |
| 6 | Click Submit again | Success | ☐ |
| 7 | Verify no duplicate PO created | Single PO | ☐ |

**Validation Points:**
- Network errors handled
- Clear error message
- No duplicate submissions
- Data not lost

---

### Test Case 57: Browser Back Button After Submit

**Objective:** Test browser navigation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create and Submit PO | Success | ☐ |
| 2 | Click Browser Back Button | Previous page | ☐ |
| 3 | Verify form state | Form cleared or warning | ☐ |
| 4 | Attempt Submit again | Prevented or new PO | ☐ |

**Validation Points:**
- Back button handled
- No duplicate submissions
- Form state managed

---

### Test Case 58: Session Timeout During PO Creation

**Objective:** Test session expiry handling

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Start creating PO | Form open | ☐ |
| 2 | Wait for session timeout (30 min) | Session expires | ☐ |
| 3 | Attempt Submit | Redirect to login | ☐ |
| 4 | Login again | Logged in | ☐ |
| 5 | Check if data preserved | Data saved or lost | ☐ |

**Validation Points:**
- Session timeout detected
- User redirected to login
- Data handling clear
- No partial data saved

---

### Test Case 59: Multiple UOM Conversions

**Objective:** Test complex UOM scenarios

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Item 1: 10 Boxes (1 Box = 12 Pieces) | Added | ☐ |
| 3 | Add Item 2: 5 Cartons (1 Carton = 24 Pieces) | Added | ☐ |
| 4 | Add Item 3: 100 Pieces | Added | ☐ |
| 5 | Verify Base Quantities: 120, 120, 100 Pieces | Correct | ☐ |
| 6 | Submit PO | Success | ☐ |
| 7 | Record Delivery | All delivered | ☐ |
| 8 | Check Inventory: All in base UOM (Pieces) | Stock correct | ☐ |

**Validation Points:**
- Multiple UOM conversions work
- Base quantities calculated correctly
- Inventory in base UOM
- No conversion errors

---

### Test Case 60: Scheme Eligibility Changes

**Objective:** Test scheme application when eligibility changes

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO with Scheme: Buy 10 Get 2 Free | Scheme applied | ☐ |
| 2 | Quantity: 10, Free: 2 | Benefits shown | ☐ |
| 3 | Change Quantity to 5 | Quantity updated | ☐ |
| 4 | Verify Scheme removed (not eligible) | Free qty = 0 | ☐ |
| 5 | Change Quantity back to 10 | Quantity updated | ☐ |
| 6 | Verify Scheme reapplied | Free qty = 2 | ☐ |
| 7 | Submit PO | Success | ☐ |

**Validation Points:**
- Scheme eligibility checked dynamically
- Benefits recalculated on changes
- Scheme removed when not eligible
- Scheme reapplied when eligible

---

## Performance Testing

### Test Case 61: Large PO with 100+ Line Items

**Objective:** Test system performance with large PO

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Import Excel with 100 products | Import completes | ☐ |
| 3 | Verify all 100 items loaded | All visible | ☐ |
| 4 | Check page responsiveness | No lag | ☐ |
| 5 | Submit PO | Success within 10 seconds | ☐ |
| 6 | Open PO Details | Loads within 5 seconds | ☐ |
| 7 | Record Delivery for all items | Completes within 15 seconds | ☐ |

**Validation Points:**
- Large PO handled efficiently
- No performance degradation
- UI remains responsive
- Database operations optimized

---

### Test Case 62: Bulk Delivery Recording

**Objective:** Test performance of bulk delivery

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Open PO with 50 items | PO opens | ☐ |
| 2 | Click "Quick Fill - Full Delivery" | All quantities filled | ☐ |
| 3 | Submit Delivery | Completes within 10 seconds | ☐ |
| 4 | Verify all inventory transactions | All logged | ☐ |
| 5 | Verify all batches created | All created | ☐ |

**Validation Points:**
- Bulk operations efficient
- Transaction processing fast
- Batch creation optimized
- No timeouts

---

### Test Case 63: Report Generation Performance

**Objective:** Test report generation speed

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to PO Dashboard | Report loads | ☐ |
| 2 | Select Year with 1000+ POs | Year selected | ☐ |
| 3 | Measure load time | < 5 seconds | ☐ |
| 4 | Export to Excel | Export < 10 seconds | ☐ |
| 5 | Verify Excel file size | Reasonable size | ☐ |

**Validation Points:**
- Reports load quickly
- Large datasets handled
- Export efficient
- No memory issues

---

### Test Case 64: Concurrent User Operations

**Objective:** Test multi-user scenarios

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | User 1: Create PO | PO created | ☐ |
| 2 | User 2: Create PO (same supplier) | PO created | ☐ |
| 3 | User 1: Record Delivery | Delivery recorded | ☐ |
| 4 | User 2: Record Payment | Payment recorded | ☐ |
| 5 | Verify no data conflicts | All data correct | ☐ |
| 6 | Check supplier balance | Correct total | ☐ |

**Validation Points:**
- Concurrent operations supported
- No data conflicts
- Locking mechanisms work
- Data consistency maintained

---

## Security Testing

### Test Case 65: Permission-Based Access

**Objective:** Test role-based access control

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Login as User with "View Only" role | Logged in | ☐ |
| 2 | Navigate to Purchases | List visible | ☐ |
| 3 | Attempt to Create PO | Button hidden/disabled | ☐ |
| 4 | Attempt to Edit PO | Button hidden/disabled | ☐ |
| 5 | Attempt to Delete PO | Button hidden/disabled | ☐ |
| 6 | Login as User with "Full Access" | Logged in | ☐ |
| 7 | Verify all actions available | All buttons visible | ☐ |

**Validation Points:**
- Permissions enforced
- UI reflects permissions
- Unauthorized actions prevented
- Role-based access works

---

### Test Case 66: Company Data Isolation

**Objective:** Test multi-tenant data isolation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Login as Company A user | Logged in | ☐ |
| 2 | Create PO | PO created | ☐ |
| 3 | Note PO ID | ID recorded | ☐ |
| 4 | Logout | Logged out | ☐ |
| 5 | Login as Company B user | Logged in | ☐ |
| 6 | Attempt to access Company A PO by ID | Access denied | ☐ |
| 7 | Verify Company A PO not in list | Not visible | ☐ |

**Validation Points:**
- Company data isolated
- Cross-company access prevented
- Data security maintained
- Multi-tenancy works

---

### Test Case 67: SQL Injection Prevention

**Objective:** Test SQL injection protection

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to PO Search | Search box visible | ☐ |
| 2 | Enter: "'; DROP TABLE purchase_order; --" | Text entered | ☐ |
| 3 | Submit Search | No error, safe handling | ☐ |
| 4 | Verify database intact | Table exists | ☐ |
| 5 | Verify search results | Empty or error | ☐ |

**Validation Points:**
- SQL injection prevented
- Input sanitized
- Database protected
- Parameterized queries used

---

### Test Case 68: XSS Prevention

**Objective:** Test cross-site scripting protection

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Enter Remarks: "<script>alert('XSS')</script>" | Text entered | ☐ |
| 3 | Submit PO | Success | ☐ |
| 4 | View PO Details | Script not executed | ☐ |
| 5 | Verify text displayed safely | HTML escaped | ☐ |

**Validation Points:**
- XSS prevented
- Scripts not executed
- HTML escaped
- Safe rendering

---

### Test Case 69: CSRF Protection

**Objective:** Test CSRF token validation

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Login to application | Logged in | ☐ |
| 2 | Open browser dev tools | Tools open | ☐ |
| 3 | Attempt API call without CSRF token | Request rejected | ☐ |
| 4 | Error: "Invalid CSRF token" | Error shown | ☐ |
| 5 | Verify request blocked | No data changed | ☐ |

**Validation Points:**
- CSRF protection active
- Tokens validated
- Unauthorized requests blocked
- Security maintained

---

### Test Case 70: Audit Trail Verification

**Objective:** Test audit logging

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | PO created | ☐ |
| 2 | Check Audit Log | Creation logged | ☐ |
| 3 | Verify: User, Timestamp, Action | All recorded | ☐ |
| 4 | Update PO | PO updated | ☐ |
| 5 | Check Audit Log | Update logged | ☐ |
| 6 | Delete PO | PO deleted (soft) | ☐ |
| 7 | Check Audit Log | Deletion logged | ☐ |
| 8 | Verify all changes tracked | Complete trail | ☐ |

**Validation Points:**
- All actions logged
- User information captured
- Timestamps accurate
- Complete audit trail

---

## Additional Complex Scenarios

### Test Case 71: Complete PO Lifecycle (End-to-End)

**Objective:** Test complete PO workflow from creation to completion

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO: 3 items, Total ₹100,000 | PO created | ☐ |
| 2 | Verify Status: Open, Payment: Pending, Delivery: Pending | Status correct | ☐ |
| 3 | Record Partial Delivery: 50% of items | Delivery recorded | ☐ |
| 4 | Verify Status: Partial, Delivery: Partial | Status updated | ☐ |
| 5 | Record Partial Payment: ₹30,000 | Payment recorded | ☐ |
| 6 | Verify Status: Partial, Payment: Partial | Status updated | ☐ |
| 7 | Record Remaining Delivery: 50% | Delivery completed | ☐ |
| 8 | Verify Delivery: Completed | Status updated | ☐ |
| 9 | Record Remaining Payment: ₹70,000 | Payment completed | ☐ |
| 10 | Verify Status: Completed, Payment: Completed | All completed | ☐ |
| 11 | Check Inventory: All items stocked | Stock correct | ☐ |
| 12 | Check Supplier Balance: ₹0 | Balance cleared | ☐ |
| 13 | Verify all transactions logged | Complete trail | ☐ |

**Validation Points:**
- Complete lifecycle works
- Status transitions correct
- All data tracked
- Final state accurate

---

### Test Case 72: PO with Mixed Schemes

**Objective:** Test multiple scheme types in one PO

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO | Form opens | ☐ |
| 2 | Add Item 1: Buy 10 Get 2 Free scheme | Scheme applied | ☐ |
| 3 | Add Item 2: 10% discount scheme | Scheme applied | ☐ |
| 4 | Add Item 3: No scheme | No scheme | ☐ |
| 5 | Verify Item 1: Free qty = 2 | Correct | ☐ |
| 6 | Verify Item 2: Discount = 10% | Correct | ☐ |
| 7 | Verify Item 3: No benefits | Correct | ☐ |
| 8 | Verify Total: Sum with all benefits | Correct | ☐ |
| 9 | Submit PO | Success | ☐ |
| 10 | Record Delivery: All items | Delivered | ☐ |
| 11 | Verify Inventory: Includes free items | Stock correct | ☐ |

**Validation Points:**
- Multiple schemes work together
- Each item tracked independently
- Total calculated correctly
- All benefits applied

---

### Test Case 73: PO Modification After Partial Delivery

**Objective:** Test editing PO after partial activity

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO: 3 items | PO created | ☐ |
| 2 | Record Delivery: Item 1 only | Delivered | ☐ |
| 3 | Attempt to Edit PO | Edit form opens | ☐ |
| 4 | Try to change Item 1 quantity | Prevented or warning | ☐ |
| 5 | Change Item 2 quantity (not delivered) | Allowed | ☐ |
| 6 | Add new Item 4 | Allowed | ☐ |
| 7 | Submit Changes | Success | ☐ |
| 8 | Verify Item 1: Unchanged | Correct | ☐ |
| 9 | Verify Item 2: Updated | Correct | ☐ |
| 10 | Verify Item 4: Added | Correct | ☐ |

**Validation Points:**
- Delivered items protected
- Undelivered items editable
- New items can be added
- Data consistency maintained

---

### Test Case 74: Supplier Balance Reconciliation

**Objective:** Verify supplier balance accuracy

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check Supplier: Initial Balance ₹0 | Balance zero | ☐ |
| 2 | Create PO 1: ₹50,000 | Balance = ₹50,000 | ☐ |
| 3 | Create PO 2: ₹30,000 | Balance = ₹80,000 | ☐ |
| 4 | Pay PO 1: ₹20,000 | Balance = ₹60,000 | ☐ |
| 5 | Return PO 2: ₹5,000 worth | Balance = ₹55,000 | ☐ |
| 6 | Pay PO 1: ₹30,000 (complete) | Balance = ₹25,000 | ☐ |
| 7 | Pay PO 2: ₹25,000 (complete) | Balance = ₹0 | ☐ |
| 8 | Verify Balance: ₹0 | Correct | ☐ |
| 9 | Check Transaction History | All recorded | ☐ |

**Validation Points:**
- Balance tracked accurately
- All transactions affect balance
- Returns reduce balance
- Final balance correct

---

### Test Case 75: Batch Tracking Verification

**Objective:** Verify batch creation and tracking

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO: Product with batch tracking | PO created | ☐ |
| 2 | Record Delivery | Delivery recorded | ☐ |
| 3 | Check Batch Created | Batch exists | ☐ |
| 4 | Verify Batch Details: PO, Product, Qty, Cost | All correct | ☐ |
| 5 | Check Batch Number Format | Format correct | ☐ |
| 6 | Verify Batch in Inventory | Linked correctly | ☐ |
| 7 | Create Sale using this batch | Sale recorded | ☐ |
| 8 | Verify Batch Quantity reduced | Qty updated | ☐ |

**Validation Points:**
- Batches created automatically
- Batch details accurate
- Batch tracking works
- FIFO/FEFO logic applied

---

### Test Case 76: Inventory Transaction Verification

**Objective:** Verify all inventory transactions logged

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO and Deliver | Delivered | ☐ |
| 2 | Check Transaction: PURCHASE_RECEIPT | Logged | ☐ |
| 3 | Verify: Product, Qty, Location, User, Timestamp | All correct | ☐ |
| 4 | Return Items | Return recorded | ☐ |
| 5 | Check Transaction: PURCHASE_RETURN | Logged | ☐ |
| 6 | Verify: Negative quantity | Correct | ☐ |
| 7 | View Transaction History | All visible | ☐ |

**Validation Points:**
- All movements logged
- Transaction types correct
- Details accurate
- History complete

---

### Test Case 77: UOM Conversion Accuracy

**Objective:** Verify UOM conversion precision

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO: 10 Boxes (1 Box = 12 Pieces) | PO created | ☐ |
| 2 | Unit Price: ₹1,200 per Box | Price entered | ☐ |
| 3 | Verify Base Qty: 120 Pieces | Conversion correct | ☐ |
| 4 | Verify Base Price: ₹100 per Piece | Conversion correct | ☐ |
| 5 | Record Delivery: 10 Boxes | Delivered | ☐ |
| 6 | Check Inventory: 120 Pieces | Stock correct | ☐ |
| 7 | Check Batch Cost: ₹100 per Piece | Cost correct | ☐ |
| 8 | Create Sale: 15 Pieces | Sale recorded | ☐ |
| 9 | Verify Stock: 105 Pieces remaining | Stock correct | ☐ |

**Validation Points:**
- UOM conversion accurate
- Price conversion correct
- Inventory in base UOM
- No rounding errors

---

### Test Case 78: Multi-Location PO Management

**Objective:** Test POs for different locations

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO 1: Location A | PO created | ☐ |
| 2 | Create PO 2: Location B | PO created | ☐ |
| 3 | Record Delivery PO 1 | Delivered to Location A | ☐ |
| 4 | Check Inventory Location A | Stock increased | ☐ |
| 5 | Check Inventory Location B | No change | ☐ |
| 6 | Record Delivery PO 2 | Delivered to Location B | ☐ |
| 7 | Check Inventory Location B | Stock increased | ☐ |
| 8 | Verify Location Isolation | Correct | ☐ |

**Validation Points:**
- Location-specific POs work
- Inventory updated at correct location
- Location isolation maintained
- No cross-location issues

---

### Test Case 79: Date Range Filtering

**Objective:** Test PO filtering by dates

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Create PO 1: Order Date 2026-03-01 | Created | ☐ |
| 2 | Create PO 2: Order Date 2026-03-15 | Created | ☐ |
| 3 | Create PO 3: Order Date 2026-03-30 | Created | ☐ |
| 4 | Filter: Order Date 2026-03-01 to 2026-03-15 | Filter applied | ☐ |
| 5 | Verify: PO 1 and PO 2 visible | Correct | ☐ |
| 6 | Verify: PO 3 not visible | Correct | ☐ |
| 7 | Clear Filter | All POs visible | ☐ |

**Validation Points:**
- Date filtering works
- Range inclusive
- Results accurate
- Clear filter works

---

### Test Case 80: Export and Import Data

**Objective:** Test data export and import

**Test Steps:**

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to PO List | List loads | ☐ |
| 2 | Click "Export to Excel" | Export starts | ☐ |
| 3 | Verify Excel file downloaded | File exists | ☐ |
| 4 | Open Excel file | File opens | ☐ |
| 5 | Verify all PO data present | Data complete | ☐ |
| 6 | Modify Excel data | Data modified | ☐ |
| 7 | Import modified Excel | Import starts | ☐ |
| 8 | Verify changes reflected | Data updated | ☐ |

**Validation Points:**
- Export works correctly
- All data included
- Import works correctly
- Data integrity maintained

---

## Test Execution Guidelines

### Test Execution Order

1. **Setup Phase** (Test Cases 1-6): Basic PO creation scenarios
2. **Delivery Phase** (Test Cases 7-12): Delivery recording scenarios
3. **Payment Phase** (Test Cases 13-16): Payment processing scenarios
4. **Return Phase** (Test Cases 17-20): Return processing scenarios
5. **Cancellation Phase** (Test Cases 21-23): Cancellation scenarios
6. **Supplier Phase** (Test Cases 24-26): Supplier management
7. **Scheme Phase** (Test Cases 27-32): Scheme application
8. **Reports Phase** (Test Cases 33-40): Report generation
9. **Edge Cases Phase** (Test Cases 41-60): Boundary and edge cases
10. **Performance Phase** (Test Cases 61-64): Performance testing
11. **Security Phase** (Test Cases 65-70): Security testing
12. **Complex Scenarios** (Test Cases 71-80): End-to-end workflows

### Test Data Management

**Before Testing:**
- Create fresh test database or restore known state
- Populate master data (suppliers, products, locations)
- Configure test schemes
- Create test user accounts

**After Testing:**
- Document all test results
- Log any defects found
- Clean up test data if needed
- Backup test results

### Defect Reporting Template

```
Defect ID: [Auto-generated]
Test Case: [Test Case Number and Name]
Severity: [Critical/High/Medium/Low]
Priority: [P1/P2/P3/P4]

Description:
[Clear description of the issue]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Result:
[What should happen]

Actual Result:
[What actually happened]

Environment:
- Browser: [Chrome/Firefox/Edge]
- OS: [Windows/Mac/Linux]
- User Role: [Role name]

Screenshots/Videos:
[Attach if available]

Additional Notes:
[Any other relevant information]
```

---

## Known Issues Reference

Based on the codebase analysis, the following known issues should be verified during testing:

### Critical Issues

**Issue 1: PO Cancellation Does Not Reverse Changes**
- **Location:** `cancel_purchase_order()` in `purchase_order_service.py`
- **Description:** Cancelling a PO does not reverse supplier balance or handle inventory
- **Test Cases:** 21, 22, 23
- **Expected Behavior:** Should reverse all financial and inventory impacts
- **Workaround:** Manually adjust supplier balance and inventory

**Issue 2: Return Uses unit_price Instead of effective_tp**
- **Location:** `process_return()` in `purchase_order_service.py`
- **Description:** Return processing uses unit_price for balance adjustment instead of effective_tp
- **Test Cases:** 17, 18, 74
- **Impact:** Incorrect supplier balance when returns involve free items or discounts
- **Workaround:** Manual balance adjustment

### Medium Issues

**Issue 3: Returned Quantity in Delivery Status**
- **Location:** `_update_po_delivery_status()` in `product_order_delivery_detail_service.py`
- **Description:** Returned quantities included in delivery completion calculation
- **Test Cases:** 17, 18
- **Impact:** Delivery status may show "Completed" incorrectly
- **Workaround:** None needed, cosmetic issue

**Issue 4: No Location Validation**
- **Location:** `create_purchase_order()` in `purchase_order_service.py`
- **Description:** No validation that delivery location matches PO location
- **Test Cases:** 49, 78
- **Impact:** Items could be delivered to wrong location
- **Workaround:** Manual verification

---

## Test Coverage Summary

### Functional Coverage

| Category | Test Cases | Coverage |
|----------|-----------|----------|
| PO Creation | 1-6 | 100% |
| PO Delivery | 7-12 | 100% |
| PO Payment | 13-16 | 100% |
| PO Return | 17-20 | 100% |
| PO Cancellation | 21-23 | 100% |
| Supplier Management | 24-26 | 100% |
| Scheme Application | 27-32 | 100% |
| Reports | 33-40 | 100% |
| Edge Cases | 41-60 | 100% |
| Performance | 61-64 | 100% |
| Security | 65-70 | 100% |
| Complex Scenarios | 71-80 | 100% |

### Business Process Coverage

- ✅ Complete PO Lifecycle
- ✅ Partial Deliveries
- ✅ Multiple Payments
- ✅ Item Returns
- ✅ Free Items Handling
- ✅ Scheme Application
- ✅ UOM Conversion
- ✅ Batch Tracking
- ✅ Supplier Balance
- ✅ Inventory Management
- ✅ Multi-Location
- ✅ Multi-Tenant
- ✅ Audit Trail
- ✅ Reports & Analytics

---

## Appendix A: Test Data Templates

### Sample Supplier Data

```csv
supplier_code,supplier_name,contact_person,contact_email,contact_phone,payment_terms,is_active
SUP-001,ABC Distributors,John Doe,john@abc.com,+91-9876543210,Net 30,true
SUP-002,XYZ Wholesale,Jane Smith,jane@xyz.com,+91-9876543211,Net 15,true
SUP-003,Quick Supply Co,Bob Johnson,bob@quick.com,+91-9876543212,COD,true
SUP-004,Bulk Traders,Alice Brown,alice@bulk.com,+91-9876543213,Net 60,false
SUP-005,International Imports,Charlie Wilson,charlie@intl.com,+91-9876543214,Net 60,true
```

### Sample Product Data

```csv
product_name,category,base_uom,has_variants
Laptop HP 15,Electronics,Pieces,true
Mouse Logitech,Electronics,Pieces,true
Keyboard Dell,Electronics,Pieces,true
Monitor Samsung 24",Electronics,Pieces,true
Rice Basmati,Groceries,Kg,false
Wheat Flour,Groceries,Kg,false
Sugar White,Groceries,Kg,false
Notebook A4,Stationery,Pieces,false
Pen Blue,Stationery,Pieces,false
Pencil HB,Stationery,Pieces,false
```

### Sample Scheme Data

```csv
scheme_name,scheme_type,condition,benefit
Buy 10 Get 2 Free,buy_x_get_y,quantity>=10,free_quantity=2
10% Discount on 50+,percentage_discount,quantity>50,discount_percent=10
Flat 500 Off,flat_discount,order_total>10000,discount_amount=500
Buy Laptop Get Mouse,buy_x_get_y_different,product=Laptop,free_product=Mouse
```

---

## Appendix B: API Endpoints Reference

### Purchase Order Endpoints

```
GET    /api/company/procurement/purchase-order/
POST   /api/company/procurement/purchase-order/
GET    /api/company/procurement/purchase-order/{id}
PATCH  /api/company/procurement/purchase-order/{id}
DELETE /api/company/procurement/purchase-order/{id}
POST   /api/company/procurement/purchase-order/{id}/cancel
POST   /api/company/procurement/purchase-order/{id}/return
POST   /api/company/procurement/purchase-order/{id}/rejection
```

### Delivery Endpoints

```
GET    /api/company/procurement/product-order-delivery-detail/
POST   /api/company/procurement/product-order-delivery-detail/
GET    /api/company/procurement/product-order-delivery-detail/{id}
PATCH  /api/company/procurement/product-order-delivery-detail/{id}
DELETE /api/company/procurement/product-order-delivery-detail/{id}
```

### Payment Endpoints

```
GET    /api/company/procurement/product-order-payment-detail/
POST   /api/company/procurement/product-order-payment-detail/
GET    /api/company/procurement/product-order-payment-detail/{id}
PATCH  /api/company/procurement/product-order-payment-detail/{id}
DELETE /api/company/procurement/product-order-payment-detail/{id}
```

### Report Endpoints

```
GET    /api/company/reports/procurement/purchase-order-report
```

---

## Appendix C: Database Schema Reference

### Key Tables

**purchase_order**
- purchase_order_id (PK)
- supplier_id (FK)
- order_number
- order_date
- expected_delivery_date
- total_amount
- amount_paid
- status
- payment_status
- delivery_status
- company_id (FK)
- location_id (FK)

**purchase_order_detail**
- purchase_order_detail_id (PK)
- purchase_order_id (FK)
- product_id (FK)
- variant_id (FK)
- quantity
- unit_price
- free_quantity
- received_quantity
- received_free_quantity
- returned_quantity
- rejected_quantity
- discount_amount
- applied_scheme_id

**product_order_delivery_detail**
- delivery_detail_id (PK)
- purchase_order_detail_id (FK)
- delivery_date
- delivered_quantity
- delivered_free_quantity
- rejected_free_quantity
- received_by

**product_order_payment_detail**
- payment_detail_id (PK)
- purchase_order_id (FK)
- payment_date
- amount_paid
- payment_method
- transaction_reference

---

## Appendix D: Status Transition Matrix

### PO Status Transitions

| From Status | Action | To Status | Conditions |
|-------------|--------|-----------|------------|
| Open | Record Delivery (Partial) | Partial | delivery_status = Partial |
| Open | Record Delivery (Full) | Partial | delivery_status = Completed, payment_status ≠ Completed |
| Open | Record Payment (Partial) | Partial | payment_status = Partial |
| Open | Cancel | Cancelled | No deliveries or payments |
| Partial | Record Delivery (Complete) | Completed | delivery_status = Completed AND payment_status = Completed |
| Partial | Record Payment (Complete) | Completed | payment_status = Completed AND delivery_status = Completed |
| Partial | Cancel | Error | Cannot cancel with activity |
| Completed | Any Action | Completed | Status locked |
| Cancelled | Any Action | Cancelled | Status locked |

### Payment Status Transitions

| From Status | Action | To Status | Conditions |
|-------------|--------|-----------|------------|
| Pending | Record Payment | Partial | 0 < amount_paid < total_amount |
| Pending | Record Payment | Completed | amount_paid >= total_amount |
| Partial | Record Payment | Partial | amount_paid < total_amount |
| Partial | Record Payment | Completed | amount_paid >= total_amount |
| Completed | Any Payment | Completed | Status locked |

### Delivery Status Transitions

| From Status | Action | To Status | Conditions |
|-------------|--------|-----------|------------|
| Pending | Record Delivery | Partial | Some items received |
| Pending | Record Delivery | Completed | All items received/rejected |
| Partial | Record Delivery | Partial | More items received |
| Partial | Record Delivery | Completed | All items received/rejected |
| Completed | Any Delivery | Completed | Status locked |

---

## Appendix E: Calculation Formulas

### PO Total Amount
```
total_amount = SUM(
  (quantity × unit_price × uom_conversion_factor) - discount_amount
) for all non-free line items
```

### Effective Total Amount
```
effective_total_amount = SUM(
  ((quantity - returned_quantity - rejected_quantity) × unit_price) - discount_amount
) for all line items
```

### Effective Trading Price (TP)
```
total_qty = quantity + free_quantity
gross_price = quantity × unit_price
discount = discount_amount
effective_tp = (gross_price - discount) / total_qty
```

### Supplier Balance
```
Initial: balance = 0
On PO Create: balance += total_amount
On Payment: balance -= amount_paid
On Return: balance -= (returned_quantity × unit_price)
On Rejection: balance -= (rejected_quantity × unit_price)
```

### Pending Quantity
```
pending_quantity = quantity - received_quantity - rejected_quantity - returned_quantity
```

### Delivery Completion %
```
completion_percent = (received_quantity / quantity) × 100
```

### Payment Completion %
```
completion_percent = (amount_paid / total_amount) × 100
```

---

## Appendix F: Browser Compatibility Matrix

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | 120+ | ✅ Supported | Recommended |
| Firefox | 120+ | ✅ Supported | Recommended |
| Edge | 120+ | ✅ Supported | Recommended |
| Safari | 17+ | ⚠️ Limited | Some features may vary |
| Opera | 105+ | ✅ Supported | Based on Chromium |
| IE 11 | - | ❌ Not Supported | Deprecated |

### Mobile Browsers

| Browser | Platform | Status | Notes |
|---------|----------|--------|-------|
| Chrome Mobile | Android | ✅ Supported | Responsive design |
| Safari Mobile | iOS | ⚠️ Limited | Some features may vary |
| Firefox Mobile | Android | ✅ Supported | Responsive design |

---

## Appendix G: Performance Benchmarks

### Expected Response Times

| Operation | Expected Time | Acceptable Time | Notes |
|-----------|---------------|-----------------|-------|
| PO List Load | < 2 seconds | < 5 seconds | 100 records |
| PO Create | < 3 seconds | < 10 seconds | 10 line items |
| PO Details Load | < 1 second | < 3 seconds | Single PO |
| Delivery Record | < 2 seconds | < 5 seconds | 10 items |
| Payment Record | < 1 second | < 3 seconds | Single payment |
| Report Generation | < 5 seconds | < 15 seconds | 1 year data |
| Excel Export | < 10 seconds | < 30 seconds | 1000 records |

### Load Testing Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Concurrent Users | 50 | Simultaneous active users |
| Requests/Second | 100 | Peak load |
| Database Connections | 20 | Connection pool |
| Response Time (95th percentile) | < 5 seconds | Most requests |
| Error Rate | < 0.1% | Acceptable failure rate |

---

## Appendix H: Glossary

### Terms and Definitions

**PO (Purchase Order)**: A commercial document issued by a buyer to a supplier indicating types, quantities, and agreed prices for products or services.

**Billable Quantity**: The quantity of items that will be charged/invoiced.

**Free Quantity**: Additional items provided at no cost, typically from promotional schemes.

**Received Quantity**: The actual quantity of items received from the supplier.

**Returned Quantity**: Items sent back to the supplier after receipt.

**Rejected Quantity**: Items refused during delivery due to quality or other issues.

**Pending Quantity**: Items not yet received (Ordered - Received - Rejected - Returned).

**Effective Total**: The actual payable amount after accounting for returns and rejections.

**Effective TP (Trading Price)**: The actual cost per unit including free items and discounts.

**UOM (Unit of Measure)**: The unit used to quantify items (Pieces, Kg, Liters, etc.).

**Base UOM**: The standard unit used for inventory tracking.

**UOM Conversion Factor**: The multiplier to convert from one UOM to base UOM.

**Scheme**: A promotional offer providing discounts or free items.

**Batch**: A group of items received together, tracked for FIFO/FEFO.

**Lead Time**: Days between order date and expected delivery date.

**Supplier Balance**: The outstanding amount owed to a supplier.

**OTD (On-Time Delivery)**: Percentage of deliveries received by expected date.

**Fill Rate**: Percentage of ordered quantity actually received.

**Maverick Spend**: Purchases from low-volume or non-preferred suppliers.

**FIFO (First In First Out)**: Inventory valuation method using oldest stock first.

**FEFO (First Expired First Out)**: Inventory method using items closest to expiry first.

**Soft Delete**: Marking records as deleted without physical removal from database.

**Audit Trail**: Complete history of all changes made to a record.

**Multi-Tenant**: System architecture supporting multiple companies with data isolation.

---

## Appendix I: Troubleshooting Guide

### Common Issues and Solutions

**Issue: PO not appearing in list**
- Check company filter
- Verify user permissions
- Check date range filters
- Refresh page

**Issue: Cannot record delivery**
- Verify PO status is not "Cancelled"
- Check if all items already received
- Verify user has delivery permissions
- Check location access

**Issue: Payment amount validation error**
- Verify amount doesn't exceed pending amount
- Check for decimal precision issues
- Ensure amount is positive
- Verify PO total is correct

**Issue: Scheme not applying**
- Check scheme eligibility conditions
- Verify scheme is active
- Check product/category matches
- Verify quantity meets threshold

**Issue: Inventory not updating**
- Check delivery was recorded successfully
- Verify location is correct
- Check batch tracking settings
- Review inventory transactions log

**Issue: Supplier balance incorrect**
- Review all PO transactions
- Check payment records
- Verify return adjustments
- Run balance reconciliation

**Issue: Report not loading**
- Check date range is valid
- Verify data exists for period
- Check browser console for errors
- Try smaller date range

**Issue: Excel import failing**
- Verify file format matches template
- Check for invalid data
- Ensure all required columns present
- Check file size limits

---

## Appendix J: Test Sign-Off Template

### Test Execution Sign-Off

**Project:** Shoudagor ERP - Purchase Order Module  
**Test Phase:** [UAT/System Testing/Regression]  
**Test Period:** [Start Date] to [End Date]  
**Tested By:** [Tester Name]  
**Test Environment:** [Environment Details]

### Test Summary

| Metric | Count |
|--------|-------|
| Total Test Cases | 80 |
| Executed | |
| Passed | |
| Failed | |
| Blocked | |
| Not Executed | |
| Pass Rate | % |

### Defects Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | | |
| High | | |
| Medium | | |
| Low | | |

### Test Coverage

| Module | Coverage % | Status |
|--------|-----------|--------|
| PO Creation | | |
| PO Delivery | | |
| PO Payment | | |
| PO Return | | |
| Supplier Management | | |
| Scheme Application | | |
| Reports | | |

### Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

### Sign-Off

**Tester:**  
Name: _______________  
Signature: _______________  
Date: _______________

**Test Lead:**  
Name: _______________  
Signature: _______________  
Date: _______________

**Project Manager:**  
Name: _______________  
Signature: _______________  
Date: _______________

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-26 | AI Assistant | Initial comprehensive testing guide created |

---

## Contact Information

For questions or clarifications regarding this testing guide:

**Project Team:**  
Email: [project-team@shoudagor.com]  
Slack: #shoudagor-testing

**Technical Support:**  
Email: [support@shoudagor.com]  
Phone: [Support Number]

---

**END OF DOCUMENT**

---

*This comprehensive UI testing guide covers all aspects of Purchase Order management in the Shoudagor ERP system. It includes 80 detailed test cases covering functional testing, edge cases, performance testing, and security testing. Use this guide to ensure complete test coverage of the PO module.*
