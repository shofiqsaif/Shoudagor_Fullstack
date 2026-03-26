# Sales Order System - Comprehensive UI Testing Guide
## Complete Testing Strategy for All SO-Related Operations, Edge Cases & Data Integrity

**Document Version:** 1.0  
**Created:** March 26, 2026  
**System:** Shoudagor Distribution Management System  
**Module:** Sales Order (SO) System  
**Purpose:** End-to-end UI testing guide covering all SO workflows, edge cases, validation scenarios, and data consistency verification

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Testing Prerequisites](#2-testing-prerequisites)
3. [Sales Order Creation Testing](#3-sales-order-creation-testing)
4. [SO Payment Processing Testing](#4-so-payment-processing-testing)
5. [SO Delivery/Dispatch Testing](#5-so-deliverydispatch-testing)
6. [SO Return & Refund Testing](#6-so-return--refund-testing)
7. [Customer Management in SO Context](#7-customer-management-in-so-context)
8. [Scheme Application in SO Testing](#8-scheme-application-in-so-testing)
9. [DSR Assignment & Loading Testing](#9-dsr-assignment--loading-testing)
10. [SR Order Consolidation Testing](#10-sr-order-consolidation-testing)
11. [SO Status Management Testing](#11-so-status-management-testing)
12. [Invoice Generation Testing](#12-invoice-generation-testing)
13. [Edge Cases & Error Scenarios](#13-edge-cases--error-scenarios)
14. [Data Consistency Verification](#14-data-consistency-verification)
15. [Performance & Load Testing](#15-performance--load-testing)
16. [Complete Testing Checklist](#16-complete-testing-checklist)

---

## 1. Executive Summary

### 1.1 Document Purpose

This comprehensive guide provides complete UI testing procedures for the Sales Order system in Shoudagor ERP, covering:
- All SO-related workflows from creation to completion
- Payment processing and tracking
- Delivery/dispatch operations (warehouse and DSR)
- Return and refund processing
- Customer balance management
- Scheme/discount application
- DSR loading and assignment
- SR order consolidation
- Data consistency across interconnected modules
- Critical edge cases and error handling

### 1.2 Sales Order System Overview

The Sales Order system is the core revenue-generating module that:
- Creates sales orders with automatic scheme evaluation
- Tracks payment status (Pending → Partial → Completed)
- Manages delivery status (Pending → Partial → Completed)
- Handles batch allocation and inventory deduction
- Supports DSR-based delivery model
- Consolidates SR orders into unified SOs
- Generates invoices and tracks commissions
- Maintains customer balance and credit limits

### 1.3 Critical Business Rules

**Stock Management:**
- Validates billable + free quantities combined
- Supports UOM conversion to base units
- Prevents negative inventory
- Allocates batches using FIFO/LIFO/WAC
- Handles both warehouse and DSR storage

**Payment Processing:**
- Updates customer balance on payment
- Calculates payment status based on effective total
- Allows overpayment with remarks
- Tracks payment methods and references
- Updates commission status on completion

**Delivery Operations:**
- Validates product availability before dispatch
- Deducts from appropriate stock source (warehouse/DSR)
- Updates batch allocations
- Tracks shipped vs delivered quantities
- Handles partial deliveries

**Return Processing:**
- Reverses batch allocations
- Restores inventory stock
- Recalculates effective total
- Adjusts customer balance
- Updates payment and delivery status

### 1.4 Testing Approach

This guide follows a **comprehensive testing strategy**:

1. **Happy Path Testing** - Standard workflows with valid data
2. **Edge Case Testing** - Boundary conditions and unusual scenarios
3. **Error Handling Testing** - Invalid inputs and system errors
4. **Integration Testing** - Cross-module data flow
5. **Consistency Verification** - Data integrity across operations
6. **Performance Testing** - Load and stress scenarios
7. **Regression Testing** - Verify fixes don't break existing functionality

---

## 2. Testing Prerequisites

### 2.1 Environment Setup

**Required Components:**
- Backend API running (FastAPI on port 8000)
- Frontend application running (React on port 5173)
- PostgreSQL database accessible
- Elasticsearch cluster running (port 9200)
- Test company created with admin user

**Environment Variables:**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/shoudagor
ELASTICSEARCH_URL=http://localhost:9200
JWT_SECRET_KEY=your-secret-key
TIMEZONE=Asia/Dhaka
BATCH_ALLOCATION_MODE=FIFO  # or LIFO, WAC

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
```

### 2.2 Master Data Requirements

**Essential Master Data:**

| Entity | Minimum Required | Purpose |
|--------|------------------|---------|
| Company | 1 | Company context for all operations |
| Users | 3 (Admin, SR, DSR) | Different role testing |
| Products | 10+ with variants | Order line items |
| Product Categories | 3+ | Product organization |
| Unit of Measures | 3+ (Piece, Box, Carton) | UOM conversion testing |
| Storage Locations | 3+ | Multi-location testing |
| Customers | 10+ | Different customer scenarios |
| Suppliers | 3+ | For purchase orders |
| Sales Representatives | 3+ | SR order consolidation |
| DSRs | 3+ | DSR loading and delivery |
| Claim Schemes | 5+ | Scheme application testing |
| Beats | 3+ | Territory management |

**Product Setup Requirements:**
- Products with multiple variants (size, color, etc.)
- Products with different UOMs (Piece, Box, Carton)
- Products with batch tracking enabled
- Products with scheme eligibility
- Products with different price points

**Customer Setup Requirements:**
- Customers with credit limits
- Customers with existing balances
- Customers with zero balance
- Customers with negative balance (overpayment)
- Customers assigned to different beats
- Customers assigned to different SRs

**Scheme Setup Requirements:**
- Buy X Get Y schemes (same product)
- Buy X Get Y schemes (different product)
- Flat discount schemes
- Percentage discount schemes
- Schemes with multiple slabs
- Active and expired schemes

### 2.3 Initial Inventory Setup

**Stock Requirements:**
```sql
-- Ensure sufficient stock for testing
-- Product 1: 1000 units in Location 1
-- Product 2: 500 units in Location 2
-- Product 3: 200 units in Location 1
-- Product 4: 100 units in Location 3
-- Product 5: 50 units in Location 1 (for low stock testing)
```

**Batch Setup:**
- Multiple batches per product with different expiry dates
- Batches with sufficient quantity for allocation
- Batches with low quantity for partial allocation testing
- Expired batches for validation testing

### 2.4 User Roles for Testing

| Role | Username | Access Level | Testing Purpose |
|------|----------|--------------|-----------------|
| Super Admin | superadmin@test.com | Full system access | System-wide operations |
| Admin | admin@test.com | Company-level access | Standard SO operations |
| Sales Manager | sales@test.com | Sales module access | SO creation and management |
| SR User | sr@test.com | SR mobile interface | SR order creation |
| DSR User | dsr@test.com | DSR mobile interface | Delivery operations |
| Limited User | user@test.com | Read-only access | Permission testing |

### 2.5 Browser & Device Testing Matrix

**Desktop Browsers:**
- Chrome (latest) - Primary testing browser
- Firefox (latest) - Secondary testing
- Safari (latest) - Mac users
- Edge (latest) - Windows users

**Mobile Devices:**
- iOS Safari (iPhone 12+)
- Android Chrome (Samsung, Pixel)
- Tablet (iPad, Android tablet)

**Screen Resolutions:**
- Desktop: 1920x1080, 1366x768
- Tablet: 768x1024
- Mobile: 375x667, 414x896

---

## 3. Sales Order Creation Testing

### 3.1 Standard SO Creation Flow

**Test Case: TC-SO-001 - Create Basic Sales Order**

**Objective:** Verify standard SO creation with single product

**Prerequisites:**
- Logged in as Admin user
- Customer "ABC Store" exists
- Product "Widget A" has 100 units in stock
- Location "Main Warehouse" is active

**Test Steps:**

1. **Navigate to Sales Order Page**
   - Click "Sales" in main navigation
   - Click "Sales Orders" submenu
   - Verify page loads with SO list
   - Click "+ New Sales Order" button

2. **Fill Basic Information**
   - Select Customer: "ABC Store"
   - Select Location: "Main Warehouse"
   - Set Order Date: Today's date
   - Set Expected Shipment Date: Tomorrow
   - Verify customer details populate (code, phone, address)

3. **Add Order Line Item**
   - Click "+ Add Item" button
   - Select Product: "Widget A"
   - Select Variant: "Standard"
   - Enter Quantity: 10
   - Select UOM: "Piece"
   - Enter Unit Price: 100.00
   - Verify Line Total: 1000.00

4. **Review Order Summary**
   - Verify Total Amount: 1000.00
   - Verify Effective Total: 1000.00
   - Verify Status: "Open"
   - Verify Payment Status: "Pending"
   - Verify Delivery Status: "Pending"

5. **Submit Order**
   - Click "Create Sales Order" button
   - Verify success message appears
   - Verify order number generated (format: SO-YYYYMMDD-XXXX)
   - Verify redirect to SO list page

**Expected Results:**
- ✅ SO created successfully with status "Open"
- ✅ Order number generated in correct format
- ✅ Customer balance increased by 1000.00
- ✅ Inventory stock NOT deducted (deduction happens on delivery)
- ✅ Batch allocation created but not consumed
- ✅ SO appears in list with correct details

**Data Verification:**
```sql
-- Verify SO created
SELECT * FROM sales.sales_order WHERE order_number = 'SO-20260326-0001';

-- Verify SO detail created
SELECT * FROM sales.sales_order_detail WHERE sales_order_id = <so_id>;

-- Verify customer balance updated
SELECT customer_name, balance_amount FROM sales.customer WHERE customer_id = <customer_id>;

-- Verify batch allocation created
SELECT * FROM warehouse.batch_allocation WHERE sales_order_detail_id = <detail_id>;

-- Verify inventory stock unchanged
SELECT * FROM warehouse.inventory_stock WHERE product_id = <product_id> AND variant_id = <variant_id>;
```

---

### 3.2 SO Creation with Multiple Line Items

**Test Case: TC-SO-002 - Create SO with Multiple Products**

**Objective:** Verify SO creation with multiple line items and different UOMs

**Test Steps:**

1. **Create SO with 3 Products**
   - Product 1: Widget A, Qty: 10, UOM: Piece, Price: 100.00
   - Product 2: Widget B, Qty: 5, UOM: Box, Price: 500.00
   - Product 3: Widget C, Qty: 2, UOM: Carton, Price: 1000.00

2. **Verify Calculations**
   - Line 1 Total: 1000.00
   - Line 2 Total: 2500.00
   - Line 3 Total: 2000.00
   - Order Total: 5500.00

3. **Submit and Verify**
   - SO created with 3 detail records
   - Each detail has correct product, quantity, UOM, price
   - Total amount matches sum of line totals

**Expected Results:**
- ✅ All 3 line items created correctly
- ✅ UOM conversions applied correctly
- ✅ Total amount calculated accurately
- ✅ Batch allocations created for all items

---

### 3.3 SO Creation with Scheme Application

**Test Case: TC-SO-003 - Create SO with Buy X Get Y Scheme**

**Objective:** Verify automatic scheme evaluation and free item addition

**Prerequisites:**
- Scheme "Buy 10 Get 2 Free" exists for Widget A
- Scheme is active (start date < today < end date)
- Scheme type: buy_x_get_y
- Trigger: Widget A, Threshold: 10, Free Qty: 2

**Test Steps:**

1. **Create SO with Scheme-Eligible Product**
   - Select Customer: "ABC Store"
   - Add Product: Widget A
   - Enter Quantity: 10 (meets threshold)
   - Enter Unit Price: 100.00

2. **Verify Scheme Auto-Application**
   - Verify free quantity field shows: 2
   - Verify line total remains: 1000.00 (10 × 100)
   - Verify scheme badge/indicator appears
   - Verify scheme name displayed

3. **Submit and Verify**
   - SO created with scheme applied
   - Detail record shows: quantity=10, free_quantity=2
   - applied_scheme_id populated
   - Claim log created

**Expected Results:**
- ✅ Scheme automatically evaluated on product selection
- ✅ Free quantity calculated correctly (2 units)
- ✅ Free quantity displayed in UI
- ✅ Line total excludes free items (only billable amount)
- ✅ Claim log entry created
- ✅ Stock validation includes billable + free (12 units total)

**Data Verification:**
```sql
-- Verify scheme applied
SELECT quantity, free_quantity, applied_scheme_id 
FROM sales.sales_order_detail 
WHERE sales_order_id = <so_id>;

-- Verify claim log
SELECT * FROM inventory.claim_log 
WHERE sales_order_id = <so_id>;

-- Verify stock validation included free quantity
-- Check batch allocation for 12 units total
SELECT SUM(allocated_quantity) 
FROM warehouse.batch_allocation 
WHERE sales_order_detail_id = <detail_id>;
```

---

### 3.4 SO Creation with Different Free Product Scheme

**Test Case: TC-SO-004 - Create SO with Buy X Get Different Product Y**

**Objective:** Verify scheme that gives different product as free item

**Prerequisites:**
- Scheme "Buy 10 Widget A Get 1 Widget B Free" exists
- Scheme type: buy_x_get_y
- Trigger: Widget A, Threshold: 10
- Free Product: Widget B, Free Qty: 1

**Test Steps:**

1. **Create SO with Trigger Product**
   - Add Product: Widget A, Qty: 10, Price: 100.00
   - Verify scheme evaluation

2. **Verify Separate Free Line Created**
   - Verify 2 detail lines created:
     - Line 1: Widget A, Qty: 10, Free Qty: 0, Price: 100.00
     - Line 2: Widget B, Qty: 1, Free Qty: 0, Price: 0.00, is_free_item: true
   - Verify Line 2 marked as free item
   - Verify Line 2 has parent_detail_id pointing to Line 1

3. **Submit and Verify**
   - SO created with 2 detail records
   - Free line has zero price
   - Free line linked to parent line
   - Stock validation checks both products

**Expected Results:**
- ✅ Separate detail line created for free product
- ✅ Free line has is_free_item=true flag
- ✅ Free line has parent_detail_id reference
- ✅ Free line has zero unit price
- ✅ Stock validated for both Widget A and Widget B
- ✅ Batch allocations created for both products

---

### 3.5 SO Creation with Discount Scheme

**Test Case: TC-SO-005 - Create SO with Flat Discount Scheme**

**Objective:** Verify flat discount scheme application

**Prerequisites:**
- Scheme "Buy 10 Get 50 Off" exists
- Scheme type: rebate_flat
- Trigger: Widget A, Threshold: 10, Discount: 50.00

**Test Steps:**

1. **Create SO with Discount-Eligible Product**
   - Add Product: Widget A, Qty: 10, Price: 100.00
   - Verify scheme evaluation

2. **Verify Discount Application**
   - Verify discount_amount field shows: 50.00
   - Verify line total: 950.00 (10 × 100 - 50)
   - Verify scheme indicator displayed

3. **Submit and Verify**
   - SO created with discount applied
   - Detail shows discount_amount=50.00
   - Total amount reflects discount

**Expected Results:**
- ✅ Discount calculated correctly
- ✅ Line total reduced by discount amount
- ✅ Order total reflects discount
- ✅ Claim log created with discount details

---

### 3.6 SO Creation with Percentage Discount Scheme

**Test Case: TC-SO-006 - Create SO with Percentage Discount Scheme**

**Objective:** Verify percentage discount scheme application

**Prerequisites:**
- Scheme "Buy 10 Get 10% Off" exists
- Scheme type: rebate_percentage
- Trigger: Widget A, Threshold: 10, Discount: 10%

**Test Steps:**

1. **Create SO with Discount-Eligible Product**
   - Add Product: Widget A, Qty: 10, Price: 100.00
   - Verify scheme evaluation

2. **Verify Percentage Discount**
   - Verify discount_amount: 100.00 (10% of 1000)
   - Verify line total: 900.00
   - Verify percentage displayed in UI

3. **Submit and Verify**
   - Discount calculated as percentage of line total
   - Correct discount amount applied

**Expected Results:**
- ✅ Percentage discount calculated correctly
- ✅ Discount amount = (quantity × price) × (percentage / 100)
- ✅ Line total reduced appropriately

---

### 3.7 SO Creation with Multiple Scheme Slabs

**Test Case: TC-SO-007 - Create SO with Tiered Scheme**

**Objective:** Verify correct slab selection in multi-tier scheme

**Prerequisites:**
- Scheme "Volume Discount" with slabs:
  - Slab 1: Qty 10-19, Get 1 Free
  - Slab 2: Qty 20-49, Get 3 Free
  - Slab 3: Qty 50+, Get 10 Free

**Test Steps:**

1. **Test Slab 1 (Qty: 15)**
   - Add Product: Widget A, Qty: 15
   - Verify free_quantity: 1
   - Verify correct slab applied

2. **Test Slab 2 (Qty: 25)**
   - Update Quantity: 25
   - Verify free_quantity: 3
   - Verify slab upgrade

3. **Test Slab 3 (Qty: 60)**
   - Update Quantity: 60
   - Verify free_quantity: 10
   - Verify highest slab applied

**Expected Results:**
- ✅ Correct slab selected based on quantity
- ✅ Free quantity matches slab definition
- ✅ Slab upgrades when quantity increases
- ✅ Best slab always selected (not stacked)

---

### 3.8 SO Creation with UOM Conversion

**Test Case: TC-SO-008 - Create SO with Different UOMs**

**Objective:** Verify UOM conversion in pricing and stock validation

**Prerequisites:**
- Product "Widget A" has UOMs:
  - Piece (base): 1 unit
  - Box: 12 pieces
  - Carton: 144 pieces (12 boxes)
- Base price: 10.00 per piece

**Test Steps:**

1. **Create SO with Box UOM**
   - Add Product: Widget A
   - Select UOM: Box
   - Enter Quantity: 5 boxes
   - Enter Unit Price: 120.00 (12 × 10)
   - Verify line total: 600.00

2. **Verify Stock Validation**
   - System should validate: 5 boxes = 60 pieces
   - Stock check against base UOM (pieces)

3. **Create SO with Carton UOM**
   - Add Product: Widget A
   - Select UOM: Carton
   - Enter Quantity: 2 cartons
   - Enter Unit Price: 1440.00 (144 × 10)
   - Verify line total: 2880.00

4. **Verify Conversion**
   - System validates: 2 cartons = 288 pieces
   - Batch allocation in base UOM

**Expected Results:**
- ✅ UOM conversion applied correctly
- ✅ Stock validated in base UOM
- ✅ Pricing calculated with UOM factor
- ✅ Batch allocation in base UOM
- ✅ Display shows selected UOM

---

### 3.9 SO Creation with Insufficient Stock

**Test Case: TC-SO-009 - Create SO with Insufficient Stock (Error Case)**

**Objective:** Verify stock validation prevents order creation

**Prerequisites:**
- Product "Widget A" has only 50 units in stock
- No other locations have stock

**Test Steps:**

1. **Attempt to Create SO Exceeding Stock**
   - Add Product: Widget A
   - Enter Quantity: 100 (exceeds available 50)
   - Click "Create Sales Order"

2. **Verify Error Handling**
   - Error message displayed
   - Message shows: "Insufficient stock for Widget A"
   - Message shows: "Requested: 100, Available: 50"
   - SO not created
   - User remains on form

3. **Correct and Retry**
   - Update Quantity: 50
   - Click "Create Sales Order"
   - SO created successfully

**Expected Results:**
- ✅ Stock validation prevents order creation
- ✅ Clear error message with details
- ✅ Form data preserved (not cleared)
- ✅ User can correct and resubmit
- ✅ No partial data saved

---

### 3.10 SO Creation with Free Items Exceeding Stock

**Test Case: TC-SO-010 - Create SO with Scheme Free Items Exceeding Stock**

**Objective:** Verify stock validation includes free quantities

**Prerequisites:**
- Product "Widget A" has 100 units in stock
- Scheme "Buy 10 Get 5 Free" active

**Test Steps:**

1. **Attempt to Create SO with Scheme**
   - Add Product: Widget A
   - Enter Quantity: 98 (billable)
   - Scheme gives: 49 free (98/10 × 5)
   - Total required: 147 units
   - Available: 100 units

2. **Verify Stock Validation**
   - Error message: "Insufficient stock"
   - Message shows: "Requested: 147 (Billable: 98, Free: 49), Available: 100"
   - SO not created

3. **Adjust to Valid Quantity**
   - Update Quantity: 10
   - Free quantity: 5
   - Total required: 15
   - SO created successfully

**Expected Results:**
- ✅ Stock validation includes billable + free quantities
- ✅ Error message breaks down billable vs free
- ✅ User understands why validation failed
- ✅ Scheme-aware stock checking

---

