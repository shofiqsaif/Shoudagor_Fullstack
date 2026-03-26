# Shoudagor ERP System - Comprehensive UI Test Flow Guide
## Complete Testing Strategy for All Modules and Data Consistency Verification

**Document Version:** 1.0  
**Created:** March 25, 2026  
**System:** Shoudagor Distribution Management System  
**Purpose:** End-to-end UI testing guide covering all workflows, data consistency checks, and verification procedures

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Testing Prerequisites](#2-testing-prerequisites)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Core Module Testing Workflows](#4-core-module-testing-workflows)
5. [Interconnected Module Testing](#5-interconnected-module-testing)
6. [Data Consistency Verification](#6-data-consistency-verification)
7. [Batch Inventory System Testing](#7-batch-inventory-system-testing)
8. [Claims & Schemes Testing](#8-claims--schemes-testing)
9. [SR/DSR System Testing](#9-srdsr-system-testing)
10. [Financial & Reporting Testing](#10-financial--reporting-testing)
11. [Critical Data Integrity Checks](#11-critical-data-integrity-checks)
12. [Performance & Load Testing](#12-performance--load-testing)
13. [Security & Permission Testing](#13-security--permission-testing)
14. [Troubleshooting & Common Issues](#14-troubleshooting--common-issues)
15. [Complete Testing Checklist](#15-complete-testing-checklist)

---

## 1. Executive Summary

### 1.1 Document Purpose

This comprehensive guide provides complete UI testing procedures for the Shoudagor ERP system, covering:
- All user-facing workflows from UI perspective
- Data consistency verification across interconnected modules
- Critical business logic validation
- Multi-module integration testing
- System health verification procedures

### 1.2 What Defines System Health

A healthy Shoudagor system must satisfy ALL of the following:


**✅ Data Consistency Criteria:**
- Batch quantities match inventory stock (when batch tracking enabled)
- Customer/supplier balances match order totals minus payments
- Inventory movements ledger is immutable and complete
- Order statuses reflect actual delivery and payment states
- Commission calculations match sales order completion
- DSR storage stock matches main warehouse transfers
- Claim logs match scheme applications in orders
- Report totals match underlying transaction data

**✅ Business Logic Integrity:**
- No negative inventory quantities
- No over-allocation of batches
- FIFO/LIFO/WAC allocation follows configured mode
- Scheme thresholds applied correctly
- UOM conversions accurate
- Price calculations include all discounts and schemes
- Return transactions properly reverse original operations

**✅ System Performance:**
- Pages load within 3 seconds
- API responses under 1 second for standard queries
- No memory leaks or connection pool exhaustion
- Elasticsearch sync status healthy
- Background jobs running successfully

### 1.3 Testing Approach

This guide follows a **layered testing strategy**:

1. **Module-Level Testing** - Test each module independently
2. **Integration Testing** - Test data flow between modules
3. **End-to-End Testing** - Complete business workflows
4. **Consistency Verification** - Cross-module data validation
5. **Regression Testing** - Verify fixes don't break existing functionality

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

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000
```

### 2.2 Test Data Requirements

**Master Data (Minimum):**
- 1 Company with settings configured
- 3+ Users (Admin, SR, DSR roles)
- 5+ Products with variants
- 3+ Product Categories
- 2+ Unit of Measures
- 3+ Storage Locations
- 5+ Customers (different beats)
- 3+ Suppliers
- 2+ Sales Representatives
- 2+ Delivery Sales Representatives
- 3+ Claim Schemes (different types)

**Transaction Data (For Testing):**
- 10+ Purchase Orders (various statuses)
- 10+ Sales Orders (various statuses)
- 5+ SR Orders
- 3+ Stock Transfers
- 5+ Inventory Adjustments
- 3+ Returns (both purchase and sales)

### 2.3 User Roles for Testing

| Role | Username | Purpose |
|------|----------|---------|
| Super Admin | superadmin@test.com | Multi-company management, system admin |
| Admin | admin@test.com | Full company access, all modules |
| SR User | sr@test.com | Sales representative mobile interface |
| DSR User | dsr@test.com | Delivery representative mobile interface |
| Limited User | user@test.com | Restricted access for permission testing |

### 2.4 Browser & Device Testing

**Browsers:**
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Devices:**
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

---

## 3. System Architecture Overview

### 3.1 Module Interconnections

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SHOUDAGOR SYSTEM ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │   PROCUREMENT    │
                        │  (Purchase Orders)│
                        └────────┬─────────┘
                                 │
                                 │ Creates Batches
                                 │ Updates Stock
                                 ▼
                        ┌──────────────────┐
                        │ BATCH INVENTORY  │◀────────────┐
                        │  - Batches       │             │
                        │  - Movements     │             │
                        │  - Allocations   │             │
                        └────────┬─────────┘             │
                                 │                       │
                                 │ Allocates Batches     │
                                 │ Reduces Stock         │
                                 ▼                       │
                        ┌──────────────────┐             │
                        │      SALES       │             │
                        │  (Sales Orders)  │             │
                        └────────┬─────────┘             │
                                 │                       │
                                 ├───────────────────────┘
                                 │ Updates Stock
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  SR SYSTEM   │ │  DSR SYSTEM  │ │   CLAIMS     │
        │  - SR Orders │ │  - Loading   │ │  - Schemes   │
        │  - Consolidate│ │  - Delivery  │ │  - Logs      │
        └──────────────┘ └──────────────┘ └──────────────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  WAREHOUSE       │
                        │  - Stock         │
                        │  - Transfers     │
                        │  - Adjustments   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    BILLING       │
                        │  - Invoices      │
                        │  - Expenses      │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │    REPORTS       │
                        │  - Inventory     │
                        │  - Sales         │
                        │  - Financial     │
                        └──────────────────┘
```

### 3.2 Data Flow Patterns

**Purchase Order Flow:**
```
PO Creation → Scheme Application → Delivery → Batch Creation → 
Stock Update → Movement Logging → Payment → Supplier Balance Update
```

**Sales Order Flow:**
```
SO Creation → Stock Validation → Scheme Application → Delivery → 
Batch Allocation → Stock Reduction → Movement Logging → Payment → 
Customer Balance Update → Commission Calculation
```

**Return Flow:**
```
Return Creation → Batch Restoration → Stock Update → 
Movement Logging → Balance Adjustment → Commission Reversal
```

---

## 4. Core Module Testing Workflows

### 4.1 Inventory Management Module

#### 4.1.1 Product Management Testing

**Test Flow: Create Product**

1. Navigate to **Inventory → Products**
2. Click **Add Product** button
3. Fill in required fields:
   - Product Name: "Test Product A"
   - SKU: "TEST-001"
   - Category: Select from dropdown
   - Unit of Measure: Select base unit
   - Description: "Test product description"
4. Click **Save**

**Verification Steps:**
- ✅ Product appears in product list
- ✅ Product ID generated automatically
- ✅ Created timestamp shows current time
- ✅ Product searchable in Elasticsearch
- ✅ Product appears in dropdown selectors

**Test Flow: Create Product Variant**

1. Open product detail page
2. Navigate to **Variants** tab
3. Click **Add Variant**
4. Fill in variant details:
   - Variant Name: "Size L"
   - SKU: "TEST-001-L"
   - Barcode: "1234567890123"
5. Set pricing:
   - Purchase Price: 100.00
   - Selling Price: 150.00
   - Retail Price: 180.00
6. Click **Save**

**Verification Steps:**
- ✅ Variant appears in variant list
- ✅ Variant linked to parent product
- ✅ Pricing saved correctly
- ✅ Variant searchable by SKU/barcode
- ✅ Variant available in order creation

**Test Flow: Product Category Management**

1. Navigate to **Inventory → Categories**
2. Click **Add Category**
3. Create parent category: "Electronics"
4. Create child category: "Mobile Phones" (parent: Electronics)
5. Assign products to categories

**Verification Steps:**
- ✅ Category hierarchy displays correctly
- ✅ Products filter by category
- ✅ Reports group by category correctly

#### 4.1.2 Unit of Measure (UOM) Testing

**Test Flow: UOM Conversion**

1. Navigate to **Inventory → Units**
2. Create base unit: "Piece" (conversion_factor: 1)
3. Create derived unit: "Box" (conversion_factor: 12, base_unit: Piece)
4. Create derived unit: "Carton" (conversion_factor: 144, base_unit: Piece)

**Verification Steps:**
- ✅ Conversions calculate correctly (1 Carton = 12 Boxes = 144 Pieces)
- ✅ Orders accept any UOM
- ✅ Stock calculations use base units
- ✅ Reports show correct quantities

**Test Scenario: Order with Different UOM**

1. Create PO with 5 Cartons (should equal 720 pieces)
2. Receive delivery
3. Check inventory stock: should show 720 pieces
4. Create SO with 10 Boxes (should equal 120 pieces)
5. Check inventory stock: should show 600 pieces remaining

#### 4.1.3 Pricing Management Testing

**Test Flow: Product Pricing**

1. Navigate to product variant
2. Set pricing:
   - Purchase Price: 100.00
   - Selling Price: 150.00 (50% markup)
   - Retail Price: 180.00 (80% markup)
3. Save pricing

**Verification Steps:**
- ✅ Prices saved correctly
- ✅ PO uses purchase price by default
- ✅ SO uses selling price by default
- ✅ Margin calculations correct in reports

---


### 4.2 Purchase Order Module Testing

#### 4.2.1 Purchase Order Creation

**Test Flow: Complete PO Workflow**

1. Navigate to **Procurement → Purchase Orders**
2. Click **Create Purchase Order**
3. Fill header information:
   - Supplier: Select supplier
   - Location: Select warehouse
   - Order Date: Today's date
   - Expected Delivery: 7 days from now
   - Reference Number: "PO-TEST-001"
4. Add line items:
   - Product: Select product
   - Variant: Select variant
   - Quantity: 100
   - Unit Price: 50.00
   - UOM: Piece
5. Review totals:
   - Subtotal: 5,000.00
   - Tax (if applicable)
   - Total: 5,000.00
6. Click **Save**

**Verification Steps:**
- ✅ PO created with status "Open"
- ✅ PO number auto-generated
- ✅ Delivery status: "Pending"
- ✅ Payment status: "Pending"
- ✅ Supplier balance NOT updated yet (no delivery)
- ✅ Inventory stock NOT updated yet (no delivery)
- ✅ PO appears in PO list
- ✅ PO searchable by PO number, supplier

#### 4.2.2 Purchase Order Delivery

**Test Flow: Receive PO Delivery**

1. Open PO detail page
2. Navigate to **Deliveries** tab
3. Click **Add Delivery**
4. Fill delivery details:
   - Delivery Date: Today
   - Reference: "DEL-001"
5. For each line item:
   - Delivered Quantity: 100 (full delivery)
   - Confirm unit price: 50.00
6. Click **Save Delivery**

**Verification Steps:**
- ✅ PO delivery status changes to "Completed"
- ✅ PO overall status changes to "Partial" (payment pending)
- ✅ PO detail received_quantity updated to 100
- ✅ **Batch created** (if batch tracking enabled):
   - Batch qty_received: 100
   - Batch qty_on_hand: 100
   - Batch unit_cost: 50.00
   - Batch status: "active"
   - Batch source_type: "purchase"
- ✅ **Inventory stock updated**:
   - Stock quantity increased by 100
- ✅ **Inventory movement created**:
   - Movement type: "IN"
   - Reference type: "PURCHASE_DELIVERY"
   - Quantity: 100
   - Unit cost: 50.00
- ✅ **Supplier balance updated**:
   - Balance increased by 5,000.00
- ✅ Delivery appears in delivery list

**Critical Data Consistency Check:**
```sql
-- Verify batch total matches stock
SELECT 
    p.name,
    pv.name as variant,
    SUM(b.qty_on_hand) as batch_total,
    s.quantity as stock_quantity,
    SUM(b.qty_on_hand) - s.quantity as difference
FROM inventory.batch b
JOIN inventory.product_variant pv ON b.variant_id = pv.id
JOIN inventory.product p ON pv.product_id = p.id
JOIN warehouse.inventory_stock s ON s.variant_id = pv.id AND s.location_id = b.location_id
WHERE b.is_deleted = false
GROUP BY p.name, pv.name, s.quantity
HAVING SUM(b.qty_on_hand) != s.quantity;
```
Expected: No rows (perfect consistency)

#### 4.2.3 Purchase Order Payment

**Test Flow: Record PO Payment**

1. Open PO detail page
2. Navigate to **Payments** tab
3. Click **Add Payment**
4. Fill payment details:
   - Payment Date: Today
   - Amount: 5,000.00 (full payment)
   - Payment Method: "Bank Transfer"
   - Reference: "PAY-001"
5. Click **Save Payment**

**Verification Steps:**
- ✅ PO payment status changes to "Completed"
- ✅ PO overall status changes to "Completed"
- ✅ PO amount_paid updated to 5,000.00
- ✅ Supplier balance reduced by 5,000.00
- ✅ Payment appears in payment list

#### 4.2.4 Purchase Return Testing

**Test Flow: Return Purchased Items**

1. Open completed PO
2. Navigate to **Returns** tab
3. Click **Add Return**
4. Select line items to return:
   - Product/Variant: Select
   - Return Quantity: 10
   - Reason: "Damaged"
5. Click **Save Return**

**Verification Steps:**
- ✅ PO detail returned_quantity updated to 10
- ✅ **Batch updated**:
   - Original batch qty_on_hand reduced by 10
   - OR new batch created with negative quantity (depends on implementation)
- ✅ **Inventory stock reduced** by 10
- ✅ **Inventory movement created**:
   - Movement type: "RETURN_OUT"
   - Reference type: "PURCHASE_RETURN"
   - Quantity: -10
- ✅ **Supplier balance adjusted**:
   - Balance reduced by (10 × 50.00 = 500.00)
- ✅ Return appears in return list

---

### 4.3 Sales Order Module Testing

#### 4.3.1 Sales Order Creation

**Test Flow: Complete SO Workflow**

1. Navigate to **Sales → Sales Orders**
2. Click **Create Sales Order**
3. Fill header information:
   - Customer: Select customer
   - Location: Select warehouse
   - Order Date: Today
   - Expected Delivery: 3 days from now
   - Reference: "SO-TEST-001"
4. Add line items:
   - Product: Select product
   - Variant: Select variant (must have stock)
   - Quantity: 20
   - Unit Price: 150.00 (selling price)
   - UOM: Piece
5. Review totals:
   - Subtotal: 3,000.00
   - Discount: 0.00
   - Tax: 0.00
   - Total: 3,000.00
6. Click **Save**

**Verification Steps:**
- ✅ **Stock validation passed**:
   - Available stock (100 - 10 return = 90) >= requested (20)
- ✅ SO created with status "Open"
- ✅ SO number auto-generated
- ✅ Delivery status: "Pending"
- ✅ Payment status: "Pending"
- ✅ Customer balance NOT updated yet (no delivery)
- ✅ Inventory stock NOT reduced yet (no delivery)
- ✅ SO appears in SO list

**Test Scenario: Insufficient Stock**

1. Try to create SO with quantity 100 (more than available 90)
2. Expected: Error message "Insufficient stock"
3. SO should NOT be created

#### 4.3.2 Sales Order Delivery

**Test Flow: Ship SO Delivery**

1. Open SO detail page
2. Navigate to **Deliveries** tab
3. Click **Add Delivery**
4. Fill delivery details:
   - Delivery Date: Today
   - Reference: "SHIP-001"
5. For each line item:
   - Shipped Quantity: 20 (full delivery)
   - Confirm unit price: 150.00
6. Click **Save Delivery**

**Verification Steps:**
- ✅ SO delivery status changes to "Completed"
- ✅ SO overall status changes to "Partial" (payment pending)
- ✅ SO detail shipped_quantity updated to 20
- ✅ **Batch allocation created**:
   - Batch allocated based on valuation mode (FIFO/LIFO/WAC)
   - SalesOrderBatchAllocation record created
   - Batch qty_on_hand reduced by 20
   - Batch status may change to "depleted" if qty_on_hand = 0
- ✅ **Inventory stock reduced** by 20
- ✅ **Inventory movement created**:
   - Movement type: "OUT"
   - Reference type: "SALES_DELIVERY"
   - Quantity: -20
   - Unit cost: (from allocated batch)
- ✅ **Customer balance updated**:
   - Balance increased by 3,000.00
- ✅ **Commission calculated** (if SR assigned):
   - Commission amount calculated
   - Commission status: "pending"
- ✅ Delivery appears in delivery list

**Critical Batch Allocation Check:**

Navigate to **Batch Inventory → Batch Drilldown**:
- Find the allocated batch
- Verify qty_on_hand reduced correctly
- Check for "cost lock" indicator (batch cannot be edited after OUT movement)

Navigate to **Batch Inventory → Movement Ledger**:
- Find the OUT movement
- Verify movement links to sales delivery
- Verify unit cost recorded at time of transaction

#### 4.3.3 Sales Order Payment

**Test Flow: Record SO Payment**

1. Open SO detail page
2. Navigate to **Payments** tab
3. Click **Add Payment**
4. Fill payment details:
   - Payment Date: Today
   - Amount: 3,000.00 (full payment)
   - Payment Method: "Cash"
   - Reference: "RCV-001"
5. Click **Save Payment**

**Verification Steps:**
- ✅ SO payment status changes to "Completed"
- ✅ SO overall status changes to "Completed"
- ✅ SO amount_paid updated to 3,000.00
- ✅ Customer balance reduced by 3,000.00
- ✅ **Commission status updated** to "approved" (if applicable)
- ✅ Payment appears in payment list

#### 4.3.4 Sales Return Testing

**Test Flow: Return Sold Items**

1. Open completed SO
2. Navigate to **Returns** tab
3. Click **Add Return**
4. Select line items to return:
   - Product/Variant: Select
   - Return Quantity: 5
   - Reason: "Customer dissatisfaction"
5. Click **Save Return**

**Verification Steps:**
- ✅ SO detail returned_quantity updated to 5
- ✅ **Batch restored**:
   - Original allocated batch qty_on_hand increased by 5
   - OR synthetic batch created (depends on implementation)
- ✅ **Inventory stock increased** by 5
- ✅ **Inventory movement created**:
   - Movement type: "RETURN_IN"
   - Reference type: "SALES_RETURN"
   - Quantity: 5
   - Links to original OUT movement
- ✅ **Customer balance adjusted**:
   - Balance reduced by (5 × 150.00 = 750.00)
- ✅ **Commission adjusted**:
   - Commission amount reduced
   - Commission status may change to "pending_adjustment"
- ✅ Return appears in return list

---

### 4.4 Warehouse Management Testing

#### 4.4.1 Storage Location Management

**Test Flow: Create Storage Location**

1. Navigate to **Warehouse → Storage Locations**
2. Click **Add Location**
3. Fill details:
   - Location Name: "Main Warehouse"
   - Location Code: "WH-001"
   - Address: "123 Main St"
   - Is Active: Yes
4. Click **Save**

**Verification Steps:**
- ✅ Location appears in location list
- ✅ Location available in order creation dropdowns
- ✅ Location can be assigned to inventory stock

#### 4.4.2 Stock Transfer Testing

**Test Flow: Transfer Stock Between Locations**

1. Navigate to **Warehouse → Stock Transfers**
2. Click **Create Transfer**
3. Fill transfer details:
   - From Location: "Main Warehouse"
   - To Location: "Branch Warehouse"
   - Transfer Date: Today
4. Add items:
   - Product/Variant: Select
   - Quantity: 10
5. Click **Save Transfer**

**Verification Steps:**
- ✅ Transfer created with status "Pending"
- ✅ **Source location stock NOT reduced yet** (pending confirmation)

**Test Flow: Confirm Transfer**

1. Open transfer detail
2. Click **Confirm Transfer**

**Verification Steps:**
- ✅ Transfer status changes to "Completed"
- ✅ **Source location stock reduced** by 10
- ✅ **Destination location stock increased** by 10
- ✅ **Batch transferred** (if batch tracking):
   - Source batch qty_on_hand reduced
   - New batch created at destination OR existing batch updated
- ✅ **Inventory movements created**:
   - TRANSFER_OUT movement at source
   - TRANSFER_IN movement at destination
- ✅ Total company stock unchanged (just moved between locations)

#### 4.4.3 Inventory Adjustment Testing

**Test Flow: Adjust Inventory**

1. Navigate to **Warehouse → Inventory Adjustments**
2. Click **Create Adjustment**
3. Fill adjustment details:
   - Location: Select location
   - Adjustment Date: Today
   - Reason: "Physical count correction"
4. Add items:
   - Product/Variant: Select
   - Current Quantity: 70 (system shows)
   - Adjusted Quantity: 75 (physical count)
   - Difference: +5
5. Click **Save Adjustment**

**Verification Steps:**
- ✅ Adjustment created
- ✅ **Inventory stock updated** to 75
- ✅ **Batch adjusted** (if batch tracking):
   - Synthetic batch created with +5 quantity
   - OR existing batch adjusted
- ✅ **Inventory movement created**:
   - Movement type: "ADJUSTMENT"
   - Reference type: "ADJUSTMENT"
   - Quantity: +5
- ✅ Adjustment appears in adjustment list

---


## 5. Interconnected Module Testing

### 5.1 Purchase-to-Sale Complete Workflow

**End-to-End Test Scenario:**

**Step 1: Purchase Inventory**
1. Create PO for 100 units @ $50/unit
2. Receive full delivery
3. Verify batch created: 100 units @ $50
4. Verify stock: 100 units
5. Record payment

**Step 2: Sell Inventory**
1. Create SO for 30 units @ $150/unit
2. Ship full delivery
3. Verify batch allocation: 30 units from original batch
4. Verify stock: 70 units remaining
5. Record payment

**Step 3: Verify Data Consistency**

Navigate to **Batch Inventory → Batch Drilldown**:
- Original batch qty_on_hand: 70 units
- Batch status: "active"

Navigate to **Batch Inventory → Movement Ledger**:
- IN movement: +100 units (purchase)
- OUT movement: -30 units (sale)
- Net: 70 units

Navigate to **Warehouse → Inventory Stock**:
- Stock quantity: 70 units
- Matches batch total ✅

Navigate to **Reports → Inventory → Stock by Batch**:
- Total stock value: 70 × $50 = $3,500
- Matches calculation ✅

**Step 4: Process Return**
1. Create sales return for 5 units
2. Verify batch restored: 75 units
3. Verify stock: 75 units
4. Verify movement ledger: RETURN_IN +5 units

**Step 5: Final Consistency Check**
- Batch total: 75 units
- Stock quantity: 75 units
- Movement ledger net: +100 -30 +5 = 75 units
- All match ✅

### 5.2 Multi-Location Workflow Testing

**Test Scenario: Purchase → Transfer → Sale**

**Step 1: Purchase at Main Warehouse**
1. Create PO for Location A: 100 units
2. Receive delivery
3. Verify stock at Location A: 100 units

**Step 2: Transfer to Branch**
1. Create stock transfer: Location A → Location B, 40 units
2. Confirm transfer
3. Verify stock at Location A: 60 units
4. Verify stock at Location B: 40 units
5. Verify batch at Location B created

**Step 3: Sell from Both Locations**
1. Create SO from Location A: 20 units
2. Create SO from Location B: 15 units
3. Ship both deliveries
4. Verify stock at Location A: 40 units
5. Verify stock at Location B: 25 units

**Step 4: Verify Total Company Stock**
- Location A: 40 units
- Location B: 25 units
- Total: 65 units
- Should match sum of all batches ✅

### 5.3 Scheme Application Workflow

**Test Scenario: Buy X Get Y Scheme**

**Step 1: Create Scheme**
1. Navigate to **Claims → Schemes**
2. Click **Create Scheme**
3. Fill scheme details:
   - Scheme Name: "Buy 10 Get 2 Free"
   - Scheme Type: "buy_x_get_y"
   - Start Date: Today
   - End Date: 30 days from now
   - Applicable To: "Purchase Orders"
4. Add slab:
   - Threshold Quantity: 10
   - Free Quantity: 2
   - Free Product: Same product
5. Click **Save**

**Step 2: Create PO with Scheme**
1. Create PO with 20 units of scheme product
2. Verify scheme applied:
   - Regular line: 20 units @ $50 = $1,000
   - Free line: 4 units @ $0 = $0 (2 free per 10 purchased)
   - Total: $1,000 (only pay for 20)
3. Save PO

**Step 3: Receive Delivery**
1. Receive delivery for all items (20 + 4 = 24 units)
2. Verify batches created:
   - Batch 1: 20 units @ $50 (paid items)
   - Batch 2: 4 units @ $0 (free items)
3. Verify stock: 24 units total

**Step 4: Verify Claim Log**
1. Navigate to **Claims → Claim Logs**
2. Find log for this PO
3. Verify:
   - Scheme applied: "Buy 10 Get 2 Free"
   - Quantity purchased: 20
   - Free quantity: 4
   - Discount value: $200 (4 × $50)

**Step 5: Sell Mixed Inventory**
1. Create SO for 15 units
2. Ship delivery
3. Verify batch allocation (FIFO mode):
   - First allocate from free batch: 4 units @ $0
   - Then allocate from paid batch: 11 units @ $50
4. Verify COGS: (4 × $0) + (11 × $50) = $550
5. Verify margin: Revenue $2,250 - COGS $550 = $1,700 margin

---

## 6. Data Consistency Verification

### 6.1 Batch-Stock Reconciliation

**Manual Verification Steps:**

1. Navigate to **Batch Inventory → Reconciliation**
2. Review reconciliation summary:
   - Total Batches: Count of all batches
   - Mismatches Found: Products where batch ≠ stock
   - Products Checked: Total products analyzed
   - Match Rate: Should be 100%

**If Mismatches Found:**

1. Click on mismatched product
2. Review details:
   - Batch Total: Sum of all batch qty_on_hand
   - Stock Quantity: inventory_stock.quantity
   - Difference: Batch Total - Stock Quantity
3. Investigate cause:
   - Missing batch creation?
   - Stock updated without batch?
   - Concurrent transaction issue?

**Resolution:**

1. Navigate to **Batch Inventory → Backfill**
2. Set Dry Run: ON
3. Click **Run Backfill**
4. Review planned changes
5. Set Dry Run: OFF
6. Click **Run Backfill** to fix
7. Verify reconciliation shows 0 mismatches

### 6.2 Movement Ledger Verification

**Test: Movement Ledger Completeness**

1. Navigate to **Batch Inventory → Movement Ledger**
2. Filter by specific product/variant
3. Export movements to CSV
4. Calculate net quantity:
   ```
   Net = SUM(IN movements) - SUM(OUT movements) + SUM(RETURN_IN) - SUM(RETURN_OUT) + SUM(ADJUSTMENTS)
   ```
5. Compare to current stock quantity
6. Should match exactly ✅

**Test: Movement Immutability**

1. Find any movement in ledger
2. Try to edit movement (should not be possible)
3. Try to delete movement (should not be possible)
4. Verify: Movements are append-only ✅

### 6.3 Customer/Supplier Balance Verification

**Test: Customer Balance Accuracy**

1. Navigate to **Sales → Customers**
2. Select a customer
3. Note balance_amount displayed
4. Navigate to customer detail
5. Review all sales orders:
   ```
   Expected Balance = SUM(delivered_amount) - SUM(paid_amount) - SUM(return_amount)
   ```
6. Compare to displayed balance
7. Should match exactly ✅

**Test: Supplier Balance Accuracy**

1. Navigate to **Procurement → Suppliers**
2. Select a supplier
3. Note balance_amount displayed
4. Navigate to supplier detail
5. Review all purchase orders:
   ```
   Expected Balance = SUM(received_amount) - SUM(paid_amount) - SUM(return_amount)
   ```
6. Compare to displayed balance
7. Should match exactly ✅

### 6.4 Order Status Consistency

**Test: Order Status Logic**

For each order (PO or SO):

1. Check delivery_status:
   - "Pending": received/shipped_quantity = 0
   - "Partial": 0 < received/shipped_quantity < quantity
   - "Completed": received/shipped_quantity >= quantity

2. Check payment_status:
   - "Pending": amount_paid = 0
   - "Partial": 0 < amount_paid < total_amount
   - "Completed": amount_paid >= total_amount

3. Check overall status:
   - "Open": delivery_status = Pending AND payment_status = Pending
   - "Partial": delivery_status = Partial OR payment_status = Partial
   - "Completed": delivery_status = Completed AND payment_status = Completed

**Automated Check Query:**
```sql
-- Find orders with inconsistent status
SELECT 
    po.id,
    po.order_number,
    po.status,
    po.delivery_status,
    po.payment_status,
    SUM(pod.quantity) as total_qty,
    SUM(pod.received_quantity) as received_qty,
    po.total_amount,
    po.amount_paid
FROM procurement.purchase_order po
JOIN procurement.purchase_order_detail pod ON po.id = pod.purchase_order_id
WHERE po.is_deleted = false
GROUP BY po.id
HAVING 
    (po.delivery_status = 'Completed' AND SUM(pod.received_quantity) < SUM(pod.quantity))
    OR (po.delivery_status = 'Pending' AND SUM(pod.received_quantity) > 0)
    OR (po.payment_status = 'Completed' AND po.amount_paid < po.total_amount)
    OR (po.payment_status = 'Pending' AND po.amount_paid > 0);
```
Expected: No rows (all statuses consistent)

### 6.5 Commission Calculation Verification

**Test: SR Commission Accuracy**

1. Navigate to **SR → Sales Representatives**
2. Select an SR
3. Review assigned sales orders
4. For each completed order:
   ```
   Expected Commission = (order_total - returns) × commission_rate
   ```
5. Navigate to **SR → Commissions**
6. Verify commission amounts match calculations
7. Verify commission status:
   - "pending": Order completed but not paid
   - "approved": Order fully paid
   - "disbursed": Commission paid to SR

---

## 7. Batch Inventory System Testing

### 7.1 Batch Tracking Enable/Disable

**Test: Enable Batch Tracking**

1. Navigate to **Settings → Invoice** tab
2. Find **Batch Inventory** section
3. Enable **Batch Tracking** toggle
4. Select **Valuation Mode**: FIFO
5. Click **Save**

**Verification:**
- ✅ Setting saved successfully
- ✅ Future PO deliveries create batches
- ✅ Future SO deliveries allocate from batches
- ✅ Batch pages become accessible

**Test: Disable Batch Tracking**

1. Disable **Batch Tracking** toggle
2. Click **Save**

**Verification:**
- ✅ Future PO deliveries do NOT create batches
- ✅ Future SO deliveries use legacy stock system
- ✅ Existing batches remain in database (not deleted)
- ✅ Batch pages show warning message

### 7.2 Valuation Mode Testing

#### 7.2.1 FIFO (First-In-First-Out) Testing

**Test Scenario:**

1. Set valuation mode to FIFO
2. Create batches:
   - Batch A: 50 units @ $40 (received 2026-03-01)
   - Batch B: 50 units @ $50 (received 2026-03-15)
   - Batch C: 50 units @ $60 (received 2026-03-25)
3. Create SO for 80 units
4. Ship delivery

**Expected Allocation:**
- Allocate from Batch A first (oldest): 50 units @ $40
- Allocate from Batch B next: 30 units @ $50
- Batch C untouched: 50 units @ $60

**Verification:**
1. Navigate to **Batch Inventory → Batch Drilldown**
2. Check batch quantities:
   - Batch A: 0 units (depleted)
   - Batch B: 20 units remaining
   - Batch C: 50 units (untouched)
3. Navigate to SO detail → Batch Allocations tab
4. Verify allocation records:
   - Allocation 1: Batch A, 50 units, $40/unit
   - Allocation 2: Batch B, 30 units, $50/unit
5. Calculate COGS: (50 × $40) + (30 × $50) = $3,500 ✅

#### 7.2.2 LIFO (Last-In-First-Out) Testing

**Test Scenario:**

1. Set valuation mode to LIFO
2. Use same batches as FIFO test
3. Create SO for 80 units
4. Ship delivery

**Expected Allocation:**
- Allocate from Batch C first (newest): 50 units @ $60
- Allocate from Batch B next: 30 units @ $50
- Batch A untouched: 50 units @ $40

**Verification:**
1. Check batch quantities:
   - Batch A: 50 units (untouched)
   - Batch B: 20 units remaining
   - Batch C: 0 units (depleted)
2. Verify allocation records:
   - Allocation 1: Batch C, 50 units, $60/unit
   - Allocation 2: Batch B, 30 units, $50/unit
3. Calculate COGS: (50 × $60) + (30 × $50) = $4,500 ✅

#### 7.2.3 Weighted Average Cost Testing

**Test Scenario:**

1. Set valuation mode to WEIGHTED_AVG
2. Use same batches as previous tests
3. Calculate weighted average:
   ```
   Total Quantity = 50 + 50 + 50 = 150 units
   Total Cost = (50 × $40) + (50 × $50) + (50 × $60) = $7,500
   Weighted Avg = $7,500 / 150 = $50/unit
   ```
4. Create SO for 80 units
5. Ship delivery

**Expected Allocation:**
- All 80 units allocated at weighted average cost: $50/unit
- Batches reduced proportionally or from oldest (implementation dependent)

**Verification:**
1. Verify allocation uses $50/unit cost
2. Calculate COGS: 80 × $50 = $4,000 ✅

### 7.3 Batch Expiry Testing

**Test Scenario: Expired Batch Handling**

1. Create batch with expiry date in past
2. Try to allocate from this batch in SO
3. Expected: System should skip expired batch and allocate from next available

**Verification:**
1. Navigate to **Batch Inventory → Batch Drilldown**
2. Filter by status: "expired"
3. Verify expired batches not allocated
4. Verify warning shown if trying to sell expired inventory

### 7.4 Batch Cost Lock Testing

**Test: Cost Lock After Allocation**

1. Create batch: 100 units @ $50
2. Create SO and allocate 30 units from this batch
3. Try to edit batch unit_cost
4. Expected: Error message "Cannot edit cost - batch has OUT movements"

**Verification:**
1. Navigate to batch detail
2. Check for "cost lock" indicator (lock icon)
3. Verify unit_cost field is read-only
4. Verify qty_received is read-only

---


## 8. Claims & Schemes Testing

### 8.1 Scheme Types Testing

#### 8.1.1 Buy X Get Y Scheme

**Test Scenario:**

1. Navigate to **Claims → Schemes**
2. Create scheme:
   - Name: "Buy 10 Get 2 Free"
   - Type: "buy_x_get_y"
   - Applicable To: "Purchase Orders"
   - Start Date: Today
   - End Date: 30 days from now
3. Add slab:
   - Threshold: 10 units
   - Free Quantity: 2 units
   - Free Product: Same product
4. Save scheme

**Test Application:**

1. Create PO with 25 units
2. Expected scheme application:
   - 25 units purchased
   - 4 free units (2 for first 10, 2 for second 10)
   - Remaining 5 units don't trigger scheme
3. Verify PO details:
   - Line 1: 25 units @ $50 = $1,250
   - Line 2: 4 units @ $0 = $0 (free)
   - Total: $1,250

**Verification:**
- ✅ Scheme applied correctly
- ✅ Free items added as separate line
- ✅ Claim log created
- ✅ Both paid and free items received in delivery
- ✅ Separate batches created for paid vs free items

#### 8.1.2 Percentage Discount Scheme

**Test Scenario:**

1. Create scheme:
   - Name: "10% Volume Discount"
   - Type: "percentage_discount"
   - Applicable To: "Sales Orders"
2. Add slab:
   - Threshold: 50 units
   - Discount Percentage: 10%
3. Save scheme

**Test Application:**

1. Create SO with 60 units @ $150/unit
2. Expected:
   - Subtotal: 60 × $150 = $9,000
   - Discount: 10% = $900
   - Total: $8,100
3. Verify SO shows discount applied

**Verification:**
- ✅ Discount calculated correctly
- ✅ Claim log shows discount amount
- ✅ Customer charged discounted amount

#### 8.1.3 Tiered Rebate Scheme

**Test Scenario:**

1. Create scheme with multiple slabs:
   - Slab 1: 10-49 units → 5% rebate
   - Slab 2: 50-99 units → 10% rebate
   - Slab 3: 100+ units → 15% rebate
2. Save scheme

**Test Application:**

1. Create PO with 75 units
2. Expected: 10% rebate applied (falls in Slab 2)
3. Verify correct slab selected

**Verification:**
- ✅ Correct slab applied based on quantity
- ✅ Rebate calculated correctly
- ✅ Claim log shows slab details

### 8.2 Scheme Date Range Testing

**Test: Expired Scheme**

1. Create scheme with end date in past
2. Try to create order with scheme product
3. Expected: Scheme NOT applied (expired)

**Test: Future Scheme**

1. Create scheme with start date in future
2. Try to create order with scheme product
3. Expected: Scheme NOT applied (not yet active)

**Test: Active Scheme**

1. Create scheme with current date in range
2. Create order with scheme product
3. Expected: Scheme applied successfully

### 8.3 Claim Log Verification

**Test: Claim Log Completeness**

1. Navigate to **Claims → Claim Logs**
2. For each order with scheme applied:
   - Verify claim log exists
   - Verify scheme details recorded
   - Verify quantities correct
   - Verify discount/free item amounts correct
3. Export claim logs
4. Verify totals match order discounts

---

## 9. SR/DSR System Testing

### 9.1 Sales Representative (SR) Testing

#### 9.1.1 SR Order Creation

**Test Flow:**

1. Login as SR user
2. Navigate to **SR → My Orders**
3. Click **Create Order**
4. Fill order details:
   - Customer: Select from assigned customers
   - Products: Select from assigned products
   - Quantities: Enter quantities
5. Save order

**Verification:**
- ✅ SR order created with status "pending"
- ✅ Order appears in SR's order list
- ✅ Order visible to admin for consolidation
- ✅ Stock NOT reduced yet (pending consolidation)

#### 9.1.2 SR Order Consolidation

**Test Flow:**

1. Login as admin
2. Navigate to **SR → Consolidation**
3. Select multiple SR orders for same customer
4. Click **Consolidate**
5. Review consolidated order:
   - All SR order items combined
   - Quantities summed
   - Prices from SR assignments
6. Click **Create Sales Order**

**Verification:**
- ✅ Sales order created from SR orders
- ✅ SR orders marked as "consolidated"
- ✅ Sales order links to SR orders
- ✅ Stock validation performed
- ✅ Commission tracking enabled

#### 9.1.3 SR Commission Calculation

**Test Flow:**

1. Complete sales order created from SR order
2. Navigate to **SR → Commissions**
3. Find commission record for this order

**Verification:**
- ✅ Commission calculated: order_total × commission_rate
- ✅ Commission status: "pending" (order completed, not paid)
4. Record payment on sales order
5. Check commission status
**Verification:**
- ✅ Commission status: "approved" (order paid)
6. Disburse commission to SR
7. Check commission status
**Verification:**
- ✅ Commission status: "disbursed"

#### 9.1.4 SR Product Assignment

**Test: Product Visibility**

1. Navigate to **SR → Product Assignments**
2. Assign specific products to SR with custom prices
3. Login as SR
4. Try to create order
5. Verify: Only assigned products visible
6. Verify: Prices match assigned prices (not default)

### 9.2 Delivery Sales Representative (DSR) Testing

#### 9.2.1 DSR Stock Loading

**Test Flow:**

1. Navigate to **DSR → Stock Loading**
2. Select DSR
3. Select sales orders to load
4. Specify quantities to load
5. Click **Load Stock**

**Verification:**
- ✅ Stock transferred from main warehouse to DSR storage
- ✅ Main warehouse stock reduced
- ✅ DSR storage stock increased
- ✅ Stock transfer record created
- ✅ Inventory movements created (TRANSFER_OUT, DSR_TRANSFER)

#### 9.2.2 DSR Delivery

**Test Flow:**

1. Login as DSR
2. Navigate to **My Deliveries**
3. Select loaded sales order
4. Click **Deliver**
5. Confirm delivery quantities
6. Save delivery

**Verification:**
- ✅ Sales order delivery created
- ✅ DSR storage stock reduced
- ✅ Batch allocated from DSR storage
- ✅ Customer balance updated
- ✅ Delivery appears in SO detail

#### 9.2.3 DSR Payment Settlement

**Test Flow:**

1. DSR collects payment from customer
2. Navigate to **DSR → Payment Settlements**
3. Click **Record Settlement**
4. Fill settlement details:
   - Amount collected
   - Payment method
   - Reference
5. Save settlement

**Verification:**
- ✅ Settlement record created
- ✅ DSR balance updated
- ✅ Customer payment recorded
- ✅ Sales order payment status updated

#### 9.2.4 DSR Stock Return

**Test Flow:**

1. DSR has unsold stock
2. Navigate to **DSR → Stock Return**
3. Select items to return
4. Specify quantities
5. Click **Return Stock**

**Verification:**
- ✅ DSR storage stock reduced
- ✅ Main warehouse stock increased
- ✅ Stock transfer record created
- ✅ Inventory movements created

---

## 10. Financial & Reporting Testing

### 10.1 Inventory Reports

#### 10.1.1 Inventory KPI Report

**Test Flow:**

1. Navigate to **Reports → Inventory → KPI**
2. Review KPI cards:
   - Total Inventory Value
   - Potential Revenue
   - Inventory Turnover
   - Days Sales of Inventory (DSI)
   - Gross Margin Return on Investment (GMROI)

**Verification:**
- ✅ Total Inventory Value = SUM(batch.qty_on_hand × batch.unit_cost)
- ✅ Potential Revenue = SUM(batch.qty_on_hand × product.selling_price)
- ✅ Inventory Turnover = COGS / Average Inventory
- ✅ DSI = 365 / Inventory Turnover
- ✅ GMROI = Gross Margin / Average Inventory

#### 10.1.2 Stock by Batch Report

**Test Flow:**

1. Navigate to **Reports → Inventory → Stock by Batch**
2. Apply filters:
   - Product: Select product
   - Location: Select location
   - Status: Active
3. Review report table

**Verification:**
- ✅ Shows all batches matching filters
- ✅ Displays: Batch ID, Product, SKU, Qty, Cost, Value
- ✅ Total Value = SUM(qty_on_hand × unit_cost)
- ✅ Export to CSV works

#### 10.1.3 Inventory Aging Report

**Test Flow:**

1. Navigate to **Reports → Inventory → Aging**
2. Review aging buckets:
   - 0-30 days
   - 31-60 days
   - 61-90 days
   - 91-180 days
   - 180+ days

**Verification:**
- ✅ Batches grouped by age correctly
- ✅ Age calculated from batch received_date
- ✅ Quantities summed per bucket
- ✅ Values calculated correctly
- ✅ Color coding indicates aging severity

#### 10.1.4 COGS by Period Report

**Test Flow:**

1. Navigate to **Reports → Inventory → COGS by Period**
2. Set date range: Last 30 days
3. Review report

**Verification:**
- ✅ COGS = SUM(OUT movement qty × unit_cost_at_txn)
- ✅ Grouped by period (daily/weekly/monthly)
- ✅ Excludes returns (or shows separately)
- ✅ Matches sales order COGS

#### 10.1.5 Margin Analysis Report

**Test Flow:**

1. Navigate to **Reports → Inventory → Margin Analysis**
2. Set filters:
   - Product: Select product
   - Date range: Last 30 days
3. Review report

**Verification:**
- ✅ Revenue = SUM(sales_order_detail.shipped_quantity × unit_price)
- ✅ COGS = SUM(allocated_batch.quantity × unit_cost)
- ✅ Margin = Revenue - COGS
- ✅ Margin % = (Margin / Revenue) × 100
- ✅ Grouped by product/category

#### 10.1.6 Batch P&L Report

**Test Flow:**

1. Navigate to **Reports → Inventory → Batch P&L**
2. Review report showing profit/loss per batch

**Verification:**
- ✅ Shows batches with OUT movements
- ✅ Cost = batch.unit_cost × qty_sold
- ✅ Revenue = selling_price × qty_sold
- ✅ Profit = Revenue - Cost
- ✅ Margin % calculated correctly

### 10.2 Sales Reports

#### 10.2.1 Sales Performance Report

**Test Flow:**

1. Navigate to **Reports → Sales → Performance**
2. Set date range
3. Review metrics:
   - Total Sales
   - Total Orders
   - Average Order Value
   - Top Products
   - Top Customers

**Verification:**
- ✅ Total Sales = SUM(sales_order.total_amount) for completed orders
- ✅ Total Orders = COUNT(sales_order)
- ✅ Average Order Value = Total Sales / Total Orders
- ✅ Top Products ranked by revenue
- ✅ Top Customers ranked by total purchases

#### 10.2.2 Customer Activity Report

**Test Flow:**

1. Navigate to **Reports → Sales → Customer Activity**
2. Select customer
3. Review activity:
   - Order history
   - Payment history
   - Outstanding balance
   - Purchase trends

**Verification:**
- ✅ All orders listed chronologically
- ✅ Balance matches customer.balance_amount
- ✅ Trends calculated correctly

### 10.3 Purchase Order Reports

#### 10.3.1 PO Progress Report

**Test Flow:**

1. Navigate to **Reports → Procurement → PO Progress**
2. Review open POs:
   - Pending deliveries
   - Partial deliveries
   - Overdue deliveries

**Verification:**
- ✅ Shows POs with delivery_status != "Completed"
- ✅ Overdue = expected_delivery_date < today
- ✅ Progress % = received_quantity / quantity × 100

#### 10.3.2 Supplier Performance Report

**Test Flow:**

1. Navigate to **Reports → Procurement → Supplier Performance**
2. Review metrics:
   - On-time delivery rate
   - Average delivery time
   - Quality issues
   - Total purchases

**Verification:**
- ✅ On-time rate = (on_time_deliveries / total_deliveries) × 100
- ✅ Average delivery time calculated correctly
- ✅ Total purchases = SUM(purchase_order.total_amount)

---

## 11. Critical Data Integrity Checks

### 11.1 Database-Level Checks

**Check 1: Batch-Stock Consistency**

```sql
-- Find products where batch total != stock quantity
SELECT 
    p.name as product,
    pv.name as variant,
    sl.name as location,
    COALESCE(SUM(b.qty_on_hand), 0) as batch_total,
    COALESCE(s.quantity, 0) as stock_quantity,
    COALESCE(SUM(b.qty_on_hand), 0) - COALESCE(s.quantity, 0) as difference
FROM inventory.product p
JOIN inventory.product_variant pv ON pv.product_id = p.id
LEFT JOIN inventory.batch b ON b.variant_id = pv.id AND b.is_deleted = false
LEFT JOIN warehouse.inventory_stock s ON s.variant_id = pv.id AND s.location_id = b.location_id
LEFT JOIN warehouse.storage_location sl ON sl.id = s.location_id
WHERE p.is_deleted = false
GROUP BY p.name, pv.name, sl.name, s.quantity
HAVING COALESCE(SUM(b.qty_on_hand), 0) != COALESCE(s.quantity, 0);
```

**Expected Result:** No rows (perfect consistency)

**Check 2: Movement Ledger Completeness**

```sql
-- Verify movement ledger matches current stock
SELECT 
    pv.id as variant_id,
    p.name as product,
    pv.name as variant,
    SUM(CASE WHEN im.movement_type = 'IN' THEN im.quantity ELSE 0 END) as total_in,
    SUM(CASE WHEN im.movement_type = 'OUT' THEN ABS(im.quantity) ELSE 0 END) as total_out,
    SUM(CASE WHEN im.movement_type = 'RETURN_IN' THEN im.quantity ELSE 0 END) as total_return_in,
    SUM(CASE WHEN im.movement_type = 'RETURN_OUT' THEN ABS(im.quantity) ELSE 0 END) as total_return_out,
    SUM(CASE WHEN im.movement_type = 'ADJUSTMENT' THEN im.quantity ELSE 0 END) as total_adjustment,
    (SUM(CASE WHEN im.movement_type = 'IN' THEN im.quantity ELSE 0 END) -
     SUM(CASE WHEN im.movement_type = 'OUT' THEN ABS(im.quantity) ELSE 0 END) +
     SUM(CASE WHEN im.movement_type = 'RETURN_IN' THEN im.quantity ELSE 0 END) -
     SUM(CASE WHEN im.movement_type = 'RETURN_OUT' THEN ABS(im.quantity) ELSE 0 END) +
     SUM(CASE WHEN im.movement_type = 'ADJUSTMENT' THEN im.quantity ELSE 0 END)) as calculated_stock,
    s.quantity as actual_stock,
    (SUM(CASE WHEN im.movement_type = 'IN' THEN im.quantity ELSE 0 END) -
     SUM(CASE WHEN im.movement_type = 'OUT' THEN ABS(im.quantity) ELSE 0 END) +
     SUM(CASE WHEN im.movement_type = 'RETURN_IN' THEN im.quantity ELSE 0 END) -
     SUM(CASE WHEN im.movement_type = 'RETURN_OUT' THEN ABS(im.quantity) ELSE 0 END) +
     SUM(CASE WHEN im.movement_type = 'ADJUSTMENT' THEN im.quantity ELSE 0 END)) - s.quantity as difference
FROM inventory.product_variant pv
JOIN inventory.product p ON p.id = pv.product_id
LEFT JOIN inventory.inventory_movement im ON im.variant_id = pv.id
LEFT JOIN warehouse.inventory_stock s ON s.variant_id = pv.id
WHERE pv.is_deleted = false
GROUP BY pv.id, p.name, pv.name, s.quantity
HAVING (SUM(CASE WHEN im.movement_type = 'IN' THEN im.quantity ELSE 0 END) -
        SUM(CASE WHEN im.movement_type = 'OUT' THEN ABS(im.quantity) ELSE 0 END) +
        SUM(CASE WHEN im.movement_type = 'RETURN_IN' THEN im.quantity ELSE 0 END) -
        SUM(CASE WHEN im.movement_type = 'RETURN_OUT' THEN ABS(im.quantity) ELSE 0 END) +
        SUM(CASE WHEN im.movement_type = 'ADJUSTMENT' THEN im.quantity ELSE 0 END)) != s.quantity;
```

**Expected Result:** No rows (movement ledger matches stock)

**Check 3: Customer Balance Accuracy**

```sql
-- Verify customer balances
SELECT 
    c.id,
    c.name,
    c.balance_amount as recorded_balance,
    COALESCE(SUM(so.total_amount), 0) - COALESCE(SUM(so.amount_paid), 0) as calculated_balance,
    c.balance_amount - (COALESCE(SUM(so.total_amount), 0) - COALESCE(SUM(so.amount_paid), 0)) as difference
FROM sales.customer c
LEFT JOIN sales.sales_order so ON so.customer_id = c.id AND so.is_deleted = false
WHERE c.is_deleted = false
GROUP BY c.id, c.name, c.balance_amount
HAVING c.balance_amount != (COALESCE(SUM(so.total_amount), 0) - COALESCE(SUM(so.amount_paid), 0));
```

**Expected Result:** No rows (balances accurate)

**Check 4: Supplier Balance Accuracy**

```sql
-- Verify supplier balances
SELECT 
    s.id,
    s.name,
    s.balance_amount as recorded_balance,
    COALESCE(SUM(po.total_amount), 0) - COALESCE(SUM(po.amount_paid), 0) as calculated_balance,
    s.balance_amount - (COALESCE(SUM(po.total_amount), 0) - COALESCE(SUM(po.amount_paid), 0)) as difference
FROM procurement.supplier s
LEFT JOIN procurement.purchase_order po ON po.supplier_id = s.id AND po.is_deleted = false
WHERE s.is_deleted = false
GROUP BY s.id, s.name, s.balance_amount
HAVING s.balance_amount != (COALESCE(SUM(po.total_amount), 0) - COALESCE(SUM(po.amount_paid), 0));
```

**Expected Result:** No rows (balances accurate)

**Check 5: Negative Inventory**

```sql
-- Find negative inventory quantities
SELECT 
    p.name as product,
    pv.name as variant,
    sl.name as location,
    s.quantity
FROM warehouse.inventory_stock s
JOIN inventory.product_variant pv ON pv.id = s.variant_id
JOIN inventory.product p ON p.id = pv.product_id
JOIN warehouse.storage_location sl ON sl.id = s.location_id
WHERE s.quantity < 0;
```

**Expected Result:** No rows (no negative inventory)

**Check 6: Negative Batch Quantities**

```sql
-- Find negative batch quantities
SELECT 
    b.id as batch_id,
    p.name as product,
    pv.name as variant,
    b.qty_on_hand,
    b.status
FROM inventory.batch b
JOIN inventory.product_variant pv ON pv.id = b.variant_id
JOIN inventory.product p ON p.id = pv.product_id
WHERE b.qty_on_hand < 0 AND b.is_deleted = false;
```

**Expected Result:** No rows (no negative batches)

### 11.2 UI-Based Verification

**Daily Health Check Routine:**

1. **Check Reconciliation**
   - Navigate to **Batch Inventory → Reconciliation**
   - Verify: 0 mismatches
   - If mismatches found: Run backfill

2. **Check Elasticsearch Sync**
   - Navigate to **Admin → Elasticsearch Sync Status**
   - Verify: All entities synced
   - If out of sync: Trigger reindex

3. **Check Background Jobs**
   - Navigate to **Admin → Background Jobs**
   - Verify: All jobs running successfully
   - If failures: Review logs and retry

4. **Check Recent Activities**
   - Navigate to **Dashboard → Recent Activities**
   - Review recent transactions
   - Look for anomalies or errors

5. **Check Order Statuses**
   - Navigate to **Sales → Orders**
   - Filter by status inconsistencies
   - Verify: No stuck orders

6. **Check Balances**
   - Review customer balances
   - Review supplier balances
   - Verify: No unexpected large balances

---


## 12. Performance & Load Testing

### 12.1 Page Load Performance

**Test: Measure Page Load Times**

For each major page, measure load time:

| Page | Target Load Time | Test Method |
|------|------------------|-------------|
| Dashboard | < 2 seconds | Open page, measure time to interactive |
| Product List | < 3 seconds | With 100+ products |
| Order List | < 3 seconds | With 100+ orders |
| Batch Drilldown | < 3 seconds | With 1000+ batches |
| Movement Ledger | < 3 seconds | With 10000+ movements |
| Reports | < 5 seconds | Complex calculations |

**How to Test:**

1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to page
4. Check "Load" time in Network tab
5. Verify: Load time within target

**If Slow:**
- Check API response times
- Check database query performance
- Check Elasticsearch response times
- Review browser console for errors

### 12.2 API Response Time Testing

**Test: Measure API Response Times**

| Endpoint | Target Response Time | Test Method |
|----------|---------------------|-------------|
| GET /products | < 500ms | List 100 products |
| GET /orders | < 500ms | List 100 orders |
| POST /orders | < 1000ms | Create order |
| GET /batches | < 500ms | List 1000 batches |
| GET /movements | < 1000ms | List 10000 movements |
| GET /reports/* | < 3000ms | Complex reports |

**How to Test:**

1. Open browser DevTools → Network tab
2. Trigger API call
3. Check response time in Network tab
4. Verify: Response time within target

**Using curl:**
```bash
# Test API response time
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/company/inventory/products"

# curl-format.txt content:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
----------\n
time_total:  %{time_total}\n
```

### 12.3 Concurrent User Testing

**Test: Multiple Users Simultaneously**

**Scenario 1: Concurrent Order Creation**

1. Have 5 users create orders simultaneously
2. All orders for same product
3. Verify:
   - All orders created successfully
   - Stock reduced correctly (no race condition)
   - No duplicate order numbers
   - No negative inventory

**Scenario 2: Concurrent Batch Allocation**

1. Have 3 users create sales orders simultaneously
2. All orders allocate from same batch
3. Verify:
   - Batch allocated correctly (no over-allocation)
   - Each order gets correct allocation
   - Batch qty_on_hand accurate
   - No deadlocks or timeouts

**Scenario 3: Concurrent Stock Adjustments**

1. Have 2 users adjust same product stock simultaneously
2. Verify:
   - Both adjustments recorded
   - Final stock = initial + adjustment1 + adjustment2
   - No lost updates

### 12.4 Large Dataset Testing

**Test: System with Large Data Volumes**

**Scenario: 10,000+ Products**

1. Import 10,000 products
2. Test:
   - Product list pagination
   - Product search performance
   - Order creation product selector
   - Report generation
3. Verify: All operations complete within acceptable time

**Scenario: 100,000+ Batches**

1. Create 100,000 batches (via script)
2. Test:
   - Batch drilldown pagination
   - Batch filtering
   - Reconciliation report
   - Stock by batch report
3. Verify: All operations complete within acceptable time

**Scenario: 1,000,000+ Movements**

1. Generate 1,000,000 movements (via script)
2. Test:
   - Movement ledger pagination
   - Movement filtering
   - COGS by period report
   - Movement export
3. Verify: All operations complete within acceptable time

### 12.5 Memory Leak Testing

**Test: Long-Running Session**

1. Login to application
2. Perform various operations for 2 hours:
   - Navigate between pages
   - Create/edit/delete records
   - Run reports
   - Export data
3. Monitor browser memory usage (DevTools → Memory)
4. Verify: Memory usage stable (no continuous growth)

**Test: Repeated Operations**

1. Create a script to repeat same operation 1000 times
2. Example: Create and delete order 1000 times
3. Monitor memory usage
4. Verify: Memory returns to baseline after operations

---

## 13. Security & Permission Testing

### 13.1 Authentication Testing

**Test: Login Flow**

1. Navigate to login page
2. Enter valid credentials
3. Click Login
4. Verify:
   - JWT token received
   - Token stored in localStorage/cookie
   - Redirected to dashboard
   - User info displayed

**Test: Invalid Credentials**

1. Enter invalid username/password
2. Click Login
3. Verify:
   - Error message displayed
   - No token issued
   - Remain on login page

**Test: Token Expiration**

1. Login successfully
2. Wait for token to expire (or manually expire)
3. Try to access protected page
4. Verify:
   - Redirected to login page
   - Error message: "Session expired"

**Test: Logout**

1. Login successfully
2. Click Logout
3. Verify:
   - Token removed from storage
   - Redirected to login page
   - Cannot access protected pages

### 13.2 Authorization Testing

**Test: Role-Based Access**

**Admin Role:**
1. Login as admin
2. Verify access to:
   - All inventory pages ✅
   - All sales pages ✅
   - All procurement pages ✅
   - All warehouse pages ✅
   - All reports ✅
   - Admin pages ✅
   - User management ✅

**SR Role:**
1. Login as SR
2. Verify access to:
   - SR order creation ✅
   - Assigned customers only ✅
   - Assigned products only ✅
   - SR commission view ✅
3. Verify NO access to:
   - Admin pages ❌
   - User management ❌
   - Full inventory management ❌
   - Supplier management ❌

**DSR Role:**
1. Login as DSR
2. Verify access to:
   - Assigned deliveries ✅
   - DSR storage view ✅
   - Payment settlement ✅
3. Verify NO access to:
   - Admin pages ❌
   - Full order management ❌
   - Inventory management ❌

**Limited User:**
1. Login as limited user
2. Verify access based on assigned permissions
3. Verify restricted pages show "Access Denied"

### 13.3 Data Isolation Testing

**Test: Multi-Tenancy**

1. Create 2 companies: Company A, Company B
2. Create user for Company A
3. Create user for Company B
4. Login as Company A user
5. Verify:
   - See only Company A data
   - Cannot access Company B data
   - API calls filtered by company_id
6. Login as Company B user
7. Verify:
   - See only Company B data
   - Cannot access Company A data

**Test: Company ID Validation**

1. Login as Company A user
2. Try to access Company B resource via API:
   ```bash
   curl -H "Authorization: Bearer <company_a_token>" \
        "http://localhost:8000/api/company/products/<company_b_product_id>"
   ```
3. Verify:
   - 404 Not Found (resource not visible)
   - OR 403 Forbidden (access denied)

### 13.4 Input Validation Testing

**Test: SQL Injection Prevention**

1. Try to inject SQL in search fields:
   - Product search: `'; DROP TABLE products; --`
   - Order search: `1' OR '1'='1`
2. Verify:
   - No SQL executed
   - Input sanitized
   - No error messages revealing DB structure

**Test: XSS Prevention**

1. Try to inject JavaScript in text fields:
   - Product name: `<script>alert('XSS')</script>`
   - Customer name: `<img src=x onerror=alert('XSS')>`
2. Verify:
   - Script not executed
   - HTML escaped in display
   - No alert shown

**Test: CSRF Protection**

1. Try to submit form from external site
2. Verify:
   - Request rejected
   - CSRF token required
   - Error message shown

### 13.5 API Security Testing

**Test: Unauthorized Access**

1. Try to access API without token:
   ```bash
   curl "http://localhost:8000/api/company/products"
   ```
2. Verify:
   - 401 Unauthorized response
   - Error message: "Authentication required"

**Test: Token Tampering**

1. Get valid token
2. Modify token payload
3. Try to access API with modified token
4. Verify:
   - 401 Unauthorized response
   - Error message: "Invalid token"

**Test: Rate Limiting**

1. Send 1000 requests in 1 second
2. Verify:
   - Rate limit triggered
   - 429 Too Many Requests response
   - Retry-After header present

---

## 14. Troubleshooting & Common Issues

### 14.1 Batch-Stock Mismatch

**Symptom:**
- Reconciliation report shows mismatches
- Batch total ≠ inventory stock quantity

**Possible Causes:**
1. Batch tracking enabled mid-operation
2. Manual stock adjustment without batch update
3. Concurrent transaction race condition
4. Failed transaction rollback

**Resolution:**
1. Navigate to **Batch Inventory → Reconciliation**
2. Review mismatch details
3. Navigate to **Batch Inventory → Backfill**
4. Run backfill in dry-run mode first
5. Review planned changes
6. Run backfill in execute mode
7. Verify reconciliation shows 0 mismatches

### 14.2 Order Status Stuck

**Symptom:**
- Order shows "Partial" but all items delivered/paid
- Order shows "Open" but has deliveries

**Possible Causes:**
1. Status update logic not triggered
2. Rounding errors in quantity/amount
3. Soft-deleted records not excluded

**Resolution:**
1. Open order detail
2. Check delivery status:
   - Sum received/shipped quantities
   - Compare to order quantities
3. Check payment status:
   - Sum payment amounts
   - Compare to order total
4. If quantities/amounts match, manually update status
5. Or run status recalculation script

### 14.3 Negative Inventory

**Symptom:**
- Inventory stock shows negative quantity
- Batch shows negative qty_on_hand

**Possible Causes:**
1. Concurrent sales without stock validation
2. Return processed incorrectly
3. Stock adjustment error
4. Race condition in allocation

**Resolution:**
1. Identify affected product/variant
2. Review movement ledger:
   - Check all IN/OUT movements
   - Calculate expected quantity
3. Review recent transactions:
   - Find transaction causing negative
   - Check if validation bypassed
4. Create inventory adjustment to correct
5. Investigate root cause to prevent recurrence

### 14.4 Elasticsearch Out of Sync

**Symptom:**
- Search results missing recent records
- Search results show deleted records
- Search results outdated

**Possible Causes:**
1. Elasticsearch sync failed
2. Background job not running
3. Elasticsearch cluster down
4. Index mapping outdated

**Resolution:**
1. Navigate to **Admin → Elasticsearch Sync Status**
2. Check sync status for each entity
3. If out of sync:
   - Click **Trigger Reindex** for affected entity
   - Wait for reindex to complete
   - Verify sync status updated
4. If reindex fails:
   - Check Elasticsearch cluster health
   - Check backend logs for errors
   - Restart Elasticsearch if needed

### 14.5 Commission Not Calculated

**Symptom:**
- Sales order completed but no commission record
- Commission amount incorrect

**Possible Causes:**
1. SR not assigned to order
2. Commission rate not set
3. Order not from SR consolidation
4. Commission calculation logic error

**Resolution:**
1. Open sales order detail
2. Check if SR assigned
3. Check SR commission rate
4. Navigate to **SR → Commissions**
5. If missing, manually create commission record
6. If incorrect, recalculate:
   - Commission = (order_total - returns) × commission_rate

### 14.6 DSR Stock Not Loading

**Symptom:**
- DSR stock loading fails
- Main warehouse stock not reduced
- DSR storage stock not increased

**Possible Causes:**
1. Insufficient stock in main warehouse
2. Stock transfer validation failed
3. DSR storage location not configured
4. Transaction rollback

**Resolution:**
1. Check main warehouse stock availability
2. Check DSR storage location exists
3. Review error logs
4. Retry stock loading
5. If persistent, check database constraints

### 14.7 Report Shows Incorrect Data

**Symptom:**
- Report totals don't match expected
- Report missing recent transactions
- Report shows deleted records

**Possible Causes:**
1. Report query includes soft-deleted records
2. Report date range incorrect
3. Report filters not applied correctly
4. Cached data outdated

**Resolution:**
1. Verify report filters:
   - Date range
   - Location
   - Product
   - Status
2. Clear browser cache
3. Refresh report
4. Export data and verify manually
5. If still incorrect, check report query logic

---

## 15. Complete Testing Checklist

### 15.1 Pre-Deployment Checklist

**Environment Setup:**
- [ ] Backend API running and accessible
- [ ] Frontend application running
- [ ] PostgreSQL database accessible
- [ ] Elasticsearch cluster running
- [ ] All migrations applied
- [ ] Test data loaded

**Configuration:**
- [ ] Environment variables set correctly
- [ ] Database connection working
- [ ] Elasticsearch connection working
- [ ] JWT secret configured
- [ ] Timezone set to Asia/Dhaka

**Master Data:**
- [ ] Test company created
- [ ] Users created (all roles)
- [ ] Products created
- [ ] Categories created
- [ ] Units of measure created
- [ ] Storage locations created
- [ ] Customers created
- [ ] Suppliers created
- [ ] SRs created
- [ ] DSRs created
- [ ] Schemes created

### 15.2 Module Testing Checklist

**Inventory Module:**
- [ ] Product CRUD operations
- [ ] Product variant management
- [ ] Category management
- [ ] UOM management
- [ ] Pricing management
- [ ] Product search (Elasticsearch)
- [ ] Product image upload

**Purchase Order Module:**
- [ ] PO creation
- [ ] PO with schemes
- [ ] PO delivery
- [ ] Batch creation on delivery
- [ ] Stock update on delivery
- [ ] Movement logging
- [ ] PO payment
- [ ] Supplier balance update
- [ ] PO return
- [ ] Batch restoration on return

**Sales Order Module:**
- [ ] SO creation
- [ ] Stock validation
- [ ] SO with schemes
- [ ] SO delivery
- [ ] Batch allocation (FIFO/LIFO/WAC)
- [ ] Stock reduction on delivery
- [ ] Movement logging
- [ ] SO payment
- [ ] Customer balance update
- [ ] Commission calculation
- [ ] SO return
- [ ] Batch restoration on return
- [ ] Commission adjustment

**Warehouse Module:**
- [ ] Storage location management
- [ ] Stock transfer between locations
- [ ] Inventory adjustment
- [ ] Stock reconciliation

**Batch Inventory Module:**
- [ ] Batch tracking enable/disable
- [ ] Valuation mode selection
- [ ] Batch drilldown
- [ ] Movement ledger
- [ ] Reconciliation report
- [ ] Backfill operation
- [ ] Batch cost lock
- [ ] Batch expiry handling

**Claims & Schemes Module:**
- [ ] Scheme creation (all types)
- [ ] Scheme application on PO
- [ ] Scheme application on SO
- [ ] Claim log creation
- [ ] Scheme date range validation
- [ ] Tiered slab selection

**SR Module:**
- [ ] SR order creation
- [ ] SR order consolidation
- [ ] Sales order creation from SR orders
- [ ] Commission calculation
- [ ] Commission approval
- [ ] Commission disbursement
- [ ] SR product assignment
- [ ] SR customer assignment

**DSR Module:**
- [ ] DSR stock loading
- [ ] DSR delivery
- [ ] DSR payment settlement
- [ ] DSR stock return
- [ ] DSR storage management

**Reports Module:**
- [ ] Inventory KPI report
- [ ] Stock by batch report
- [ ] Inventory aging report
- [ ] COGS by period report
- [ ] Margin analysis report
- [ ] Batch P&L report
- [ ] Sales performance report
- [ ] Customer activity report
- [ ] PO progress report
- [ ] Supplier performance report

### 15.3 Integration Testing Checklist

**End-to-End Workflows:**
- [ ] Purchase → Stock → Sale → Return
- [ ] Purchase → Transfer → Sale
- [ ] SR Order → Consolidation → Sale
- [ ] DSR Loading → Delivery → Settlement
- [ ] Scheme Application → Order → Claim Log
- [ ] Multi-location workflow

**Data Consistency:**
- [ ] Batch-stock reconciliation (0 mismatches)
- [ ] Movement ledger completeness
- [ ] Customer balance accuracy
- [ ] Supplier balance accuracy
- [ ] Order status consistency
- [ ] Commission calculation accuracy
- [ ] No negative inventory
- [ ] No negative batches

**Cross-Module:**
- [ ] Inventory affects sales
- [ ] Sales affects inventory
- [ ] Purchase affects inventory
- [ ] Returns affect inventory
- [ ] Transfers affect inventory
- [ ] Adjustments affect inventory
- [ ] Schemes affect orders
- [ ] Orders affect balances
- [ ] Payments affect balances

### 15.4 Performance Testing Checklist

**Page Load:**
- [ ] Dashboard < 2s
- [ ] Product list < 3s
- [ ] Order list < 3s
- [ ] Batch drilldown < 3s
- [ ] Movement ledger < 3s
- [ ] Reports < 5s

**API Response:**
- [ ] GET /products < 500ms
- [ ] GET /orders < 500ms
- [ ] POST /orders < 1000ms
- [ ] GET /batches < 500ms
- [ ] GET /movements < 1000ms
- [ ] GET /reports/* < 3000ms

**Concurrent Users:**
- [ ] 5 users creating orders simultaneously
- [ ] 3 users allocating from same batch
- [ ] 2 users adjusting same stock
- [ ] No race conditions
- [ ] No deadlocks
- [ ] No data corruption

**Large Datasets:**
- [ ] 10,000+ products
- [ ] 100,000+ batches
- [ ] 1,000,000+ movements
- [ ] All operations within acceptable time

### 15.5 Security Testing Checklist

**Authentication:**
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Token expiration handling
- [ ] Logout functionality
- [ ] Password reset (if implemented)

**Authorization:**
- [ ] Admin role access
- [ ] SR role access
- [ ] DSR role access
- [ ] Limited user access
- [ ] Role-based page restrictions
- [ ] Role-based API restrictions

**Data Isolation:**
- [ ] Multi-tenancy working
- [ ] Company A cannot access Company B data
- [ ] Company ID validation on API calls

**Input Validation:**
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Input sanitization

**API Security:**
- [ ] Unauthorized access blocked
- [ ] Token tampering detected
- [ ] Rate limiting working

### 15.6 Post-Deployment Checklist

**Smoke Tests:**
- [ ] Application accessible
- [ ] Login working
- [ ] Dashboard loading
- [ ] Create test order
- [ ] View test report
- [ ] No console errors

**Data Verification:**
- [ ] Production data migrated correctly
- [ ] Batch-stock reconciliation clean
- [ ] Customer balances accurate
- [ ] Supplier balances accurate
- [ ] No negative inventory

**Monitoring:**
- [ ] Application logs clean
- [ ] Database performance acceptable
- [ ] Elasticsearch sync healthy
- [ ] Background jobs running
- [ ] No memory leaks

**User Acceptance:**
- [ ] Admin user tested
- [ ] SR user tested
- [ ] DSR user tested
- [ ] Feedback collected
- [ ] Issues documented

---

## 16. Appendix

### 16.1 Test Data Generation Scripts

**Generate Test Products:**
```python
# Script to generate test products
import requests

API_BASE = "http://localhost:8000/api/company"
TOKEN = "your-jwt-token"

headers = {"Authorization": f"Bearer {TOKEN}"}

for i in range(1, 101):
    product = {
        "name": f"Test Product {i}",
        "sku": f"TEST-{i:04d}",
        "category_id": 1,
        "unit_of_measure_id": 1,
        "description": f"Test product {i} description"
    }
    response = requests.post(f"{API_BASE}/inventory/products", json=product, headers=headers)
    print(f"Created product {i}: {response.status_code}")
```

**Generate Test Batches:**
```python
# Script to generate test batches via PO deliveries
import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/company"
TOKEN = "your-jwt-token"

headers = {"Authorization": f"Bearer {TOKEN}"}

for i in range(1, 101):
    # Create PO
    po = {
        "supplier_id": 1,
        "location_id": 1,
        "order_date": datetime.now().isoformat(),
        "expected_delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "details": [
            {
                "product_id": i,
                "variant_id": i,
                "quantity": 100,
                "unit_price": 50.00,
                "unit_of_measure_id": 1
            }
        ]
    }
    po_response = requests.post(f"{API_BASE}/procurement/purchase-order", json=po, headers=headers)
    po_id = po_response.json()["id"]
    
    # Create delivery
    delivery = {
        "delivery_date": datetime.now().isoformat(),
        "reference": f"DEL-{i:04d}",
        "details": [
            {
                "purchase_order_detail_id": po_response.json()["details"][0]["id"],
                "delivered_quantity": 100
            }
        ]
    }
    delivery_response = requests.post(
        f"{API_BASE}/procurement/purchase-order/{po_id}/delivery",
        json=delivery,
        headers=headers
    )
    print(f"Created batch {i}: {delivery_response.status_code}")
```

### 16.2 Useful SQL Queries

**Find All Mismatches:**
```sql
-- Comprehensive mismatch report
SELECT 
    p.name as product,
    pv.name as variant,
    sl.name as location,
    COALESCE(SUM(b.qty_on_hand), 0) as batch_total,
    COALESCE(s.quantity, 0) as stock_quantity,
    COALESCE(SUM(b.qty_on_hand), 0) - COALESCE(s.quantity, 0) as difference,
    COUNT(b.id) as batch_count
FROM inventory.product p
JOIN inventory.product_variant pv ON pv.product_id = p.id
LEFT JOIN inventory.batch b ON b.variant_id = pv.id AND b.is_deleted = false
LEFT JOIN warehouse.inventory_stock s ON s.variant_id = pv.id AND s.location_id = b.location_id
LEFT JOIN warehouse.storage_location sl ON sl.id = s.location_id
WHERE p.is_deleted = false
GROUP BY p.name, pv.name, sl.name, s.quantity
HAVING COALESCE(SUM(b.qty_on_hand), 0) != COALESCE(s.quantity, 0)
ORDER BY ABS(COALESCE(SUM(b.qty_on_hand), 0) - COALESCE(s.quantity, 0)) DESC;
```

**Find Stuck Orders:**
```sql
-- Orders with inconsistent status
SELECT 
    'Purchase Order' as order_type,
    po.id,
    po.order_number,
    po.status,
    po.delivery_status,
    po.payment_status,
    SUM(pod.quantity) as total_qty,
    SUM(pod.received_quantity) as received_qty,
    po.total_amount,
    po.amount_paid
FROM procurement.purchase_order po
JOIN procurement.purchase_order_detail pod ON po.id = pod.purchase_order_id
WHERE po.is_deleted = false
GROUP BY po.id
HAVING 
    (po.delivery_status = 'Completed' AND SUM(pod.received_quantity) < SUM(pod.quantity))
    OR (po.delivery_status = 'Pending' AND SUM(pod.received_quantity) > 0)
    OR (po.payment_status = 'Completed' AND po.amount_paid < po.total_amount)
    OR (po.payment_status = 'Pending' AND po.amount_paid > 0)

UNION ALL

SELECT 
    'Sales Order' as order_type,
    so.id,
    so.order_number,
    so.status,
    so.delivery_status,
    so.payment_status,
    SUM(sod.quantity) as total_qty,
    SUM(sod.shipped_quantity) as shipped_qty,
    so.total_amount,
    so.amount_paid
FROM sales.sales_order so
JOIN sales.sales_order_detail sod ON so.id = sod.sales_order_id
WHERE so.is_deleted = false
GROUP BY so.id
HAVING 
    (so.delivery_status = 'Completed' AND SUM(sod.shipped_quantity) < SUM(sod.quantity))
    OR (so.delivery_status = 'Pending' AND SUM(sod.shipped_quantity) > 0)
    OR (so.payment_status = 'Completed' AND so.amount_paid < so.total_amount)
    OR (so.payment_status = 'Pending' AND so.amount_paid > 0);
```

**Audit Recent Transactions:**
```sql
-- Recent high-value transactions
SELECT 
    'Purchase Order' as type,
    po.order_number as reference,
    s.name as party,
    po.total_amount,
    po.status,
    po.cd as created_date
FROM procurement.purchase_order po
JOIN procurement.supplier s ON s.id = po.supplier_id
WHERE po.cd >= NOW() - INTERVAL '7 days'
    AND po.is_deleted = false
    AND po.total_amount > 10000

UNION ALL

SELECT 
    'Sales Order' as type,
    so.order_number as reference,
    c.name as party,
    so.total_amount,
    so.status,
    so.cd as created_date
FROM sales.sales_order so
JOIN sales.customer c ON c.id = so.customer_id
WHERE so.cd >= NOW() - INTERVAL '7 days'
    AND so.is_deleted = false
    AND so.total_amount > 10000

ORDER BY created_date DESC;
```

### 16.3 Browser Console Commands

**Check Token:**
```javascript
// View stored JWT token
console.log(localStorage.getItem('token'));

// Decode JWT token (without verification)
function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

console.log(parseJwt(localStorage.getItem('token')));
```

**Monitor API Calls:**
```javascript
// Log all fetch requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
    console.log('Fetch:', args[0]);
    return originalFetch.apply(this, args).then(response => {
        console.log('Response:', response.status, args[0]);
        return response;
    });
};
```

**Check Memory Usage:**
```javascript
// Monitor memory usage
setInterval(() => {
    if (performance.memory) {
        console.log('Memory:', {
            used: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
            total: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
            limit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
        });
    }
}, 5000);
```

---

## Conclusion

This comprehensive testing guide covers all aspects of the Shoudagor ERP system from a UI testing perspective. By following these workflows and verification procedures, you can ensure:

1. **Data Consistency** - All interconnected modules maintain accurate data
2. **Business Logic Integrity** - All workflows execute correctly
3. **System Performance** - Application performs within acceptable limits
4. **Security** - Access control and data isolation working properly
5. **User Experience** - All features accessible and functional

**Key Takeaways:**

- Test each module independently first
- Then test integration between modules
- Always verify data consistency after operations
- Use both UI and database-level checks
- Monitor performance continuously
- Test with realistic data volumes
- Verify security and permissions thoroughly

**Regular Maintenance:**

- Run daily health checks
- Monitor reconciliation reports
- Review error logs
- Check Elasticsearch sync status
- Verify background jobs
- Audit high-value transactions
- Review user feedback

By following this guide systematically, you can confidently verify that the Shoudagor system is running properly and all data remains consistent across all modules.

---

**Document Version:** 1.0  
**Last Updated:** March 25, 2026  
**Maintained By:** Shoudagor Development Team

