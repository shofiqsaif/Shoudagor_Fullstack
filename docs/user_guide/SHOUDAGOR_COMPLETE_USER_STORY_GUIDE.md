# Shoudagor ERP - Complete User Story Guide
## From Admin, SR, DSR, and Super Admin Perspectives

**Version:** 2.0  
**Date:** March 26, 2026  
**Purpose:** Comprehensive user story-style guide covering all workflows from different user perspectives

---

## 📖 Table of Contents

1. [Welcome to Shoudagor](#welcome-to-shoudagor)
2. [Understanding Your Role](#understanding-your-role)
3. [Product & Variant Management](#product--variant-management)
4. [Purchase Order Workflow](#purchase-order-workflow)
5. [Sales Order Workflow](#sales-order-workflow)
6. [Scheme and Claim Management](#scheme-and-claim-management)
7. [SR Order Flow](#sr-order-flow)
8. [DSR Flow](#dsr-flow)
9. [Expense Module](#expense-module)
10. [Supplier and Customer Management](#supplier-and-customer-management)
11. [Batch and Inventory Stock](#batch-and-inventory-stock)
12. [Reports](#reports)
13. [Stock Transfer and Adjustments](#stock-transfer-and-adjustments)
14. [Beat Management](#beat-management)
15. [Quick Reference](#quick-reference)

---

## Welcome to Shoudagor

Shoudagor is your complete business management system that helps you run your distribution business efficiently. Whether you're managing inventory, processing orders, or tracking sales representatives, Shoudagor has you covered.

### What Makes Shoudagor Special?

- **Real-time Inventory Tracking** - Know exactly what you have in stock
- **Batch Tracking with FIFO/LIFO** - Track costs accurately
- **Mobile-First Design** - SRs and DSRs work on the go
- **Automatic Scheme Application** - Promotions apply automatically
- **Commission Tracking** - Fair and transparent SR compensation
- **Multi-Location Support** - Manage multiple warehouses
- **Comprehensive Reports** - Make data-driven decisions


---

## Understanding Your Role

### 👤 Super Admin - The System Master

**Who You Are:** You have complete control over the entire system. You manage companies, configure system settings, and oversee all operations.

**What You Can Do:**
- Create and manage companies
- Create admin users for each company
- Configure system-wide settings
- Access all modules across all companies
- Monitor system health and performance
- Manage user permissions and roles

**Your Daily Tasks:**
- Review system performance
- Handle user access requests
- Configure new companies
- Monitor data integrity
- Troubleshoot system issues

---

### 👨‍💼 Admin - The Business Manager

**Who You Are:** You manage day-to-day operations for your company. You oversee inventory, orders, and team members.

**What You Can Do:**
- Manage products and inventory
- Process purchase and sales orders
- Approve SR orders and consolidate them
- Assign orders to DSRs
- Create and manage schemes
- Generate reports
- Manage suppliers and customers
- Handle payments and settlements

**Your Daily Tasks:**
- Check dashboard for alerts
- Approve pending SR orders
- Consolidate orders for delivery
- Assign orders to DSRs
- Process payments
- Review reports
- Manage stock levels

---

### 🚶 SR (Sales Representative) - The Field Warrior

**Who You Are:** You're on the ground, visiting customers, taking orders, and building relationships.

**What You Can Do:**
- Create orders for assigned customers
- View assigned products and prices
- Negotiate prices within limits
- Track your commission
- View order status
- Access customer information

**Your Daily Tasks:**
- Check your route and customers
- Visit shops and take orders
- Negotiate best prices
- Submit orders for approval
- Track commission earnings
- Follow up on pending orders

---

### 🚚 DSR (Delivery Sales Representative) - The Delivery Expert

**Who You Are:** You deliver orders to customers, collect payments, and ensure customer satisfaction.

**What You Can Do:**
- View assigned orders
- Load orders to your van
- Deliver items to customers
- Collect payments
- Handle returns
- Track your deliveries

**Your Daily Tasks:**
- Load orders in the morning
- Follow delivery route
- Deliver items and get signatures
- Collect payments
- Handle any returns
- Settle payments with admin


---

## Product & Variant Management

### Story: Admin Sets Up New Product Line

**Meet Priya - Inventory Manager**

"We just signed a deal with a new soap manufacturer. I need to add their entire product line to our system."

#### Step 1: Create Product Categories

**Priya's Actions:**
1. Logs into Shoudagor
2. Navigates to **Inventory → Categories**
3. Clicks **"+ New Category"**
4. Enters:
   - Category Name: "Personal Care"
   - Parent Category: "FMCG"
   - Description: "Soaps, shampoos, and hygiene products"
5. Clicks **"Save"**

**What Happens:**
- ✅ Category created and appears in the tree structure
- ✅ Can now be used for product classification
- ✅ Helps in organizing products and reports

---

#### Step 2: Create Base Product

**Priya's Actions:**
1. Navigates to **Inventory → Products**
2. Clicks **"+ New Product"**
3. Fills in details:
   - Product Name: "Dove Beauty Soap"
   - Product Code: "DOVE-SOAP-001"
   - Category: "Personal Care"
   - Brand: "Dove"
   - Description: "Moisturizing beauty soap"
   - Base Unit: "Piece"
   - Enable Batch Tracking: ✓ Yes
   - Track Expiry: ✓ Yes
4. Uploads product image
5. Clicks **"Create Product"**

**What Happens:**
- ✅ Product created with unique ID
- ✅ Searchable in Elasticsearch
- ✅ Ready for variant creation
- ✅ Batch tracking enabled for cost management

---

#### Step 3: Create Product Variants

**Priya's Actions:**
1. Opens the newly created product
2. Clicks **"Add Variant"** tab
3. Creates variants:
   
   **Variant 1:**
   - Variant Name: "100g"
   - SKU: "DOVE-100G"
   - Weight: 100g
   - Barcode: "8901030123456"
   
   **Variant 2:**
   - Variant Name: "75g"
   - SKU: "DOVE-75G"
   - Weight: 75g
   - Barcode: "8901030123457"
   
   **Variant 3:**
   - Variant Name: "125g"
   - SKU: "DOVE-125G"
   - Weight: 125g
   - Barcode: "8901030123458"

4. Saves all variants

**What Happens:**
- ✅ Three variants created under one product
- ✅ Each has unique SKU and barcode
- ✅ Can be priced differently
- ✅ Stock tracked separately for each

---

#### Step 4: Set Up Unit of Measures (UOM)

**Priya's Actions:**
1. Navigates to **Inventory → Units**
2. Creates UOM hierarchy:
   
   **Base Unit: Piece**
   - Conversion Factor: 1
   
   **Box**
   - Contains: 12 Pieces
   - Conversion Factor: 12
   
   **Carton**
   - Contains: 12 Boxes (144 Pieces)
   - Conversion Factor: 144

3. Saves UOM configuration

**What Happens:**
- ✅ Can buy in Cartons, sell in Pieces
- ✅ System converts automatically
- ✅ Pricing adjusts based on UOM
- ✅ Stock always tracked in base unit

---

#### Step 5: Set Product Pricing

**Priya's Actions:**
1. Opens product "Dove Beauty Soap 100g"
2. Clicks **"Pricing"** tab
3. Adds price entries:
   
   **Retail Price:**
   - UOM: Piece
   - Price: ₹45.00
   - Effective From: Today
   - Effective To: (blank - ongoing)
   
   **Wholesale Price:**
   - UOM: Box (12 pieces)
   - Price: ₹500.00 (₹41.67 per piece)
   - Effective From: Today
   
   **Bulk Price:**
   - UOM: Carton (144 pieces)
   - Price: ₹5,800.00 (₹40.28 per piece)
   - Effective From: Today

4. Saves pricing

**What Happens:**
- ✅ Multiple price points configured
- ✅ Time-based pricing supported
- ✅ UOM-specific pricing
- ✅ System picks correct price automatically

---

### Story: SR Gets Product Assignment

**Meet Rahul - Sales Representative**

"I need to know which products I can sell and at what prices."

#### Admin Assigns Products to SR

**Admin's Actions:**
1. Navigates to **Sales → Sales Representatives**
2. Selects "Rahul Kumar"
3. Clicks **"Assign Products"**
4. Searches and selects products:
   - Dove Beauty Soap 100g
   - Dove Beauty Soap 75g
   - Lux Soap 100g
5. For each product, sets:
   - Assigned Price: ₹42.00 (SR's base price)
   - Minimum Price: ₹40.00 (can't go below)
   - Maximum Price: ₹45.00 (can't go above)
6. Clicks **"Save Assignments"**

**What Happens:**
- ✅ Rahul can only see assigned products
- ✅ Knows his base selling price
- ✅ Can negotiate within min-max range
- ✅ Commission calculated on difference

**Rahul's View (Mobile App):**
```
📱 My Products (3)
┌─────────────────────────────────┐
│ Dove Beauty Soap 100g           │
│ My Price: ₹42.00                │
│ Range: ₹40.00 - ₹45.00          │
│ Stock: 500 pieces available     │
└─────────────────────────────────┘
```


---

## Purchase Order Workflow

### Story: Admin Orders Stock from Supplier

**Meet Amit - Purchase Manager**

"Our Dove soap stock is running low. I need to order 1000 units from our supplier."

#### Step 1: Create Purchase Order

**Amit's Actions:**
1. Navigates to **Purchases → New Purchase Order**
2. Fills in header:
   - Supplier: "Unilever Bangladesh"
   - Location: "Main Warehouse"
   - Order Date: Today
   - Expected Delivery: 7 days from now
   - Payment Terms: Net 30
3. Clicks **"Add Products"**

**Adding Products:**
```
Product 1: Dove Beauty Soap 100g
- Quantity: 1000
- UOM: Pieces
- Unit Price: ₹35.00
- Line Total: ₹35,000

Product 2: Dove Shampoo 200ml
- Quantity: 500
- UOM: Pieces
- Unit Price: ₹80.00
- Line Total: ₹40,000

Order Total: ₹75,000
```

4. Reviews order summary
5. Clicks **"Create Purchase Order"**

**What Happens:**
- ✅ PO created with number: PO-20260326-001
- ✅ Status: "Open"
- ✅ Payment Status: "Pending"
- ✅ Delivery Status: "Pending"
- ✅ Supplier balance increased by ₹75,000
- ✅ Email notification sent to supplier (if configured)

---

#### Step 2: Receive Delivery

**Three Days Later - Truck Arrives**

**Amit's Actions:**
1. Opens PO-20260326-001
2. Clicks **"Record Delivery"**
3. Enters delivery details:
   
   **Dove Soap:**
   - Ordered: 1000
   - Delivered: 980
   - Rejected: 20 (damaged packaging)
   - Free Qty: 100 (supplier bonus!)
   
   **Dove Shampoo:**
   - Ordered: 500
   - Delivered: 500
   - Rejected: 0
   - Free Qty: 0

4. Adds delivery note: "20 soaps damaged, supplier agreed to credit"
5. Clicks **"Save Delivery"**

**What Happens Behind the Scenes:**

**Batch Creation:**
```
Batch 1: Dove Soap (Billable)
- Quantity: 980 pieces
- Unit Cost: ₹35.00
- Total Cost: ₹34,300
- Batch Number: BATCH-20260329-001
- Expiry Date: 2 years from now
- Source: Purchase Order

Batch 2: Dove Soap (Free)
- Quantity: 100 pieces
- Unit Cost: ₹0.00 (free items)
- Total Cost: ₹0.00
- Batch Number: BATCH-20260329-002
- Expiry Date: 2 years from now
- Source: Purchase Order (Free)

Batch 3: Dove Shampoo
- Quantity: 500 pieces
- Unit Cost: ₹80.00
- Total Cost: ₹40,000
- Batch Number: BATCH-20260329-003
- Expiry Date: 3 years from now
```

**Inventory Update:**
```
Main Warehouse Stock:
- Dove Soap 100g: +1,080 pieces (980 + 100)
- Dove Shampoo 200ml: +500 pieces
```

**Financial Impact:**
```
Original Order: ₹75,000
Rejected Items: -₹700 (20 × ₹35)
Effective Total: ₹74,300
Supplier Balance: ₹74,300 (reduced from ₹75,000)
```

**Status Updates:**
- ✅ Delivery Status: "Completed"
- ✅ PO Status: "Partial" (payment pending)
- ✅ Inventory movements logged
- ✅ Batches created with FIFO queue

---

#### Step 3: Record Payment

**Two Weeks Later - Payment Time**

**Amit's Actions:**
1. Opens PO-20260326-001
2. Clicks **"Record Payment"**
3. Enters payment details:
   - Amount: ₹74,300 (full payment)
   - Payment Date: Today
   - Method: Bank Transfer
   - Reference: TXN-2026-03-15-12345
   - Bank: HDFC Bank
   - Notes: "Payment for PO-20260326-001"
4. Clicks **"Save Payment"**

**What Happens:**
- ✅ Payment recorded
- ✅ Payment Status: "Completed"
- ✹ PO Status: "Completed" (both delivery and payment done)
- ✅ Supplier balance decreased by ₹74,300 (now ₹0)
- ✅ Payment appears in supplier statement
- ✅ Cash flow report updated

---

### Story: Handling Returns to Supplier

**One Week Later - Quality Issue Discovered**

**Amit's Actions:**
1. Opens completed PO
2. Clicks **"Return Items"**
3. Selects items to return:
   
   **Dove Soap:**
   - Return Quantity: 50 pieces
   - Reason: "Quality issue - soap cracking"
   - Return Date: Today

4. Clicks **"Process Return"**

**What Happens:**
- ✅ Inventory reduced by 50 pieces
- ✅ Batch allocation reversed
- ✅ Effective total reduced: ₹74,300 - ₹1,750 = ₹72,550
- ✅ Supplier balance reduced by ₹1,750
- ✅ Return transaction logged
- ✅ Can request credit note from supplier


---

## Sales Order Workflow

### Story: Direct Sales Order Creation

**Meet Sneha - Sales Counter Staff**

"A customer just walked in wanting to buy products. Let me create a sales order."

#### Step 1: Create Sales Order

**Sneha's Actions:**
1. Navigates to **Sales → New Sales Order**
2. Fills in header:
   - Customer: "ABC Retail Store"
   - Location: "Main Warehouse"
   - Order Date: Today
   - Expected Shipment: Tomorrow
3. Adds products:
   
   **Product 1: Dove Soap 100g**
   - Quantity: 50 pieces
   - Unit Price: ₹45.00
   - Line Total: ₹2,250
   
   **Product 2: Dove Shampoo 200ml**
   - Quantity: 20 pieces
   - Unit Price: ₹95.00
   - Line Total: ₹1,900

4. Reviews order:
   - Subtotal: ₹4,150
   - Schemes Applied: (checking...)
   
**System Checks Schemes:**
```
🎁 Scheme Found!
"Buy 50 Dove Soap, Get 5 Free"

Applied to Order:
- Billable Qty: 50 pieces
- Free Qty: 5 pieces
- Total to Deliver: 55 pieces
- Customer Pays: ₹2,250 (only for 50)
```

5. Final order total: ₹4,150
6. Clicks **"Create Sales Order"**

**What Happens:**
- ✅ SO created: SO-20260326-001
- ✅ Status: "Open"
- ✅ Payment Status: "Pending"
- ✅ Delivery Status: "Pending"
- ✅ Customer balance increased by ₹4,150
- ✅ Stock NOT deducted yet (happens on delivery)
- ✅ Batch allocation prepared (FIFO)

---

#### Step 2: Deliver Order

**Next Day - Delivery Time**

**Sneha's Actions:**
1. Opens SO-20260326-001
2. Clicks **"Record Delivery"**
3. Confirms delivery quantities:
   
   **Dove Soap:**
   - Ordered: 50 + 5 free = 55 pieces
   - Delivered: 55 pieces ✓
   
   **Dove Shampoo:**
   - Ordered: 20 pieces
   - Delivered: 20 pieces ✓

4. Delivery Date: Today
5. Delivery Notes: "Delivered by company vehicle"
6. Clicks **"Process Delivery"**

**What Happens Behind the Scenes:**

**Batch Allocation (FIFO):**
```
Dove Soap - Need 55 pieces:
1. Batch-001 (oldest): Take 50 pieces @ ₹35.00 = ₹1,750
2. Batch-002 (free batch): Take 5 pieces @ ₹0.00 = ₹0
Total Cost of Goods Sold: ₹1,750

Dove Shampoo - Need 20 pieces:
1. Batch-003: Take 20 pieces @ ₹80.00 = ₹1,600
Total Cost of Goods Sold: ₹1,600

Order COGS: ₹3,350
```

**Inventory Update:**
```
Main Warehouse Stock:
- Dove Soap 100g: 1,080 → 1,025 pieces (-55)
- Dove Shampoo 200ml: 500 → 480 pieces (-20)
```

**Batch Update:**
```
Batch-001 (Dove Soap):
- qty_on_hand: 980 → 930 pieces

Batch-002 (Dove Soap Free):
- qty_on_hand: 100 → 95 pieces

Batch-003 (Dove Shampoo):
- qty_on_hand: 500 → 480 pieces
```

**Status Updates:**
- ✅ Delivery Status: "Completed"
- ✅ SO Status: "Partial" (payment pending)
- ✅ Inventory movements logged
- ✅ COGS calculated: ₹3,350

---

#### Step 3: Collect Payment

**Customer Pays**

**Sneha's Actions:**
1. Opens SO-20260326-001
2. Clicks **"Record Payment"**
3. Enters payment:
   - Amount: ₹4,150 (full payment)
   - Payment Date: Today
   - Method: Cash
   - Reference: CASH-001
4. Clicks **"Save Payment"**

**What Happens:**
- ✅ Payment recorded
- ✅ Payment Status: "Completed"
- ✅ SO Status: "Completed" (both delivery and payment done)
- ✅ Customer balance decreased by ₹4,150 (now ₹0)
- ✅ Cash added to cash register
- ✅ Receipt can be printed

**Profit Calculation:**
```
Revenue: ₹4,150
COGS: ₹3,350
Gross Profit: ₹800
Margin: 19.3%
```

---

### Story: Handling Customer Returns

**One Week Later - Customer Returns Items**

**Sneha's Actions:**
1. Opens completed SO
2. Clicks **"Process Return"**
3. Enters return details:
   
   **Dove Soap:**
   - Return Quantity: 10 pieces
   - Reason: "Customer overstocked"
   - Return Date: Today
   - Condition: Good

4. Clicks **"Process Return"**

**What Happens:**
- ✅ Inventory increased by 10 pieces
- ✅ Batch allocation reversed (FIFO)
- ✅ Effective total reduced: ₹4,150 - ₹450 = ₹3,700
- ✅ Customer balance increased by ₹450 (credit)
- ✅ Return transaction logged
- ✅ Can issue credit note

**Batch Reversal:**
```
Return 10 pieces to Batch-001:
- qty_on_hand: 930 → 940 pieces
- Returned items back in FIFO queue
```


---

## Scheme and Claim Management

### Story: Marketing Creates Promotional Scheme

**Meet Zara - Marketing Manager**

"We're launching a Ramadan promotion. Buy 10 Dove soaps, get 2 free!"

#### Step 1: Create Scheme

**Zara's Actions:**
1. Navigates to **Claims & Schemes → New Scheme**
2. Fills in scheme details:
   
   **Basic Information:**
   - Scheme Name: "Ramadan Dove Promotion"
   - Scheme Type: Buy X Get Y Free (Same Product)
   - Start Date: March 1, 2026
   - End Date: March 31, 2026
   - Status: Active
   
   **Trigger Product:**
   - Product: Dove Beauty Soap 100g
   - Applies To: Purchase Orders & Sales Orders
   
   **Scheme Slabs:**
   ```
   Slab 1: Buy 10-19 pieces → Get 2 free
   Slab 2: Buy 20-49 pieces → Get 5 free
   Slab 3: Buy 50+ pieces → Get 10 free
   ```

3. Clicks **"Create Scheme"**

**What Happens:**
- ✅ Scheme activated immediately
- ✅ Applies to all new POs and SOs
- ✅ System evaluates automatically
- ✅ Claim logs track usage

---

#### Step 2: Scheme Auto-Application

**When Sneha Creates Sales Order:**

**Customer Orders: 25 Dove Soaps**

**System Evaluation:**
```
Checking schemes for Dove Soap 100g...
✓ Found: "Ramadan Dove Promotion"
✓ Quantity: 25 pieces
✓ Matches Slab 2: 20-49 pieces
✓ Free Quantity: 5 pieces

Order Details:
- Billable: 25 pieces @ ₹45 = ₹1,125
- Free: 5 pieces @ ₹0 = ₹0
- Total to Deliver: 30 pieces
- Customer Pays: ₹1,125
```

**On Screen:**
```
┌─────────────────────────────────────┐
│ 🎁 Promotion Applied!               │
│ Ramadan Dove Promotion              │
│ Buy 25, Get 5 Free                  │
│                                     │
│ Billable Qty: 25 pieces             │
│ Free Qty: 5 pieces                  │
│ You Save: ₹225                      │
└─────────────────────────────────────┘
```

---

### Story: Different Scheme Types

#### Type 1: Buy X Get Different Product Y

**Scheme: "Buy 10 Dove Soap, Get 1 Lux Soap Free"**

**Configuration:**
- Trigger: Dove Soap 100g, Qty: 10
- Free Product: Lux Soap 100g, Qty: 1

**Result:**
```
Order Line 1: Dove Soap 100g
- Quantity: 10
- Price: ₹45.00
- Total: ₹450.00

Order Line 2: Lux Soap 100g (FREE)
- Quantity: 1
- Price: ₹0.00
- Total: ₹0.00
- Linked to Line 1
```

---

#### Type 2: Flat Discount

**Scheme: "₹100 Off on Orders Above ₹1,000"**

**Configuration:**
- Trigger: Any product
- Minimum Order Value: ₹1,000
- Discount: ₹100 flat

**Result:**
```
Order Subtotal: ₹1,250
Discount Applied: -₹100
Final Total: ₹1,150
```

---

#### Type 3: Percentage Discount

**Scheme: "10% Off on Dove Products"**

**Configuration:**
- Trigger: All Dove products
- Discount: 10%

**Result:**
```
Dove Soap: 20 × ₹45 = ₹900
Discount (10%): -₹90
Line Total: ₹810
```

---

### Story: Tracking Scheme Performance

**Zara Reviews Scheme Performance:**

**Zara's Actions:**
1. Navigates to **Claims & Schemes → Reports**
2. Selects scheme: "Ramadan Dove Promotion"
3. Date range: March 1-31, 2026
4. Clicks **"Generate Report"**

**Report Shows:**
```
┌─────────────────────────────────────────────┐
│ Ramadan Dove Promotion Performance          │
│ Period: March 1-31, 2026                    │
├─────────────────────────────────────────────┤
│                                             │
│ Total Orders with Scheme: 156               │
│ Total Billable Quantity: 4,250 pieces       │
│ Total Free Quantity: 850 pieces             │
│                                             │
│ Revenue Generated: ₹191,250                 │
│ Cost of Free Items: ₹29,750                 │
│ Net Benefit: ₹45,000 (extra sales)          │
│                                             │
│ Slab Breakdown:                             │
│ - Slab 1 (10-19): 45 orders, 170 free      │
│ - Slab 2 (20-49): 89 orders, 445 free      │
│ - Slab 3 (50+): 22 orders, 235 free        │
│                                             │
│ ROI: 151% (₹45k gain vs ₹29.75k cost)      │
└─────────────────────────────────────────────┘
```

**Zara's Decision:**
"Great ROI! Let's extend this scheme for another month."


---

## SR Order Flow

### Story: SR Takes Orders in the Field

**Meet Rahul - Sales Representative**

"I'm visiting 15 shops today. Let me take orders on my mobile app."

#### Step 1: Morning Preparation

**Rahul's Actions (Mobile App):**
1. Opens Shoudagor SR App
2. Logs in with credentials
3. Views today's route:

```
📱 Today's Route - March 26, 2026
┌─────────────────────────────────────┐
│ 🗺️ Beat: North Zone                 │
│ 📍 15 Customers to Visit             │
│                                     │
│ 1. Corner Store (2.5 km)            │
│ 2. Mini Mart (1.2 km)               │
│ 3. Big Bazaar (3.1 km)              │
│ ... 12 more                         │
│                                     │
│ 📦 My Products: 25 items            │
│ 💰 Target: ₹50,000                  │
└─────────────────────────────────────┘
```

---

#### Step 2: Visit Customer #1 - Corner Store

**At Corner Store:**

**Shop Owner:** "I need 20 Dove soaps and 10 shampoos."

**Rahul's Actions:**
1. Clicks **"Create Order"**
2. Selects Customer: "Corner Store"
3. Adds products:
   
   **Product 1: Dove Soap 100g**
   - My Base Price: ₹42.00
   - Negotiated Price: ₹41.50 (good deal!)
   - Quantity: 20 pieces
   - My Commission: (₹42 - ₹41.50) × 20 = ₹10.00 💚
   
   **Product 2: Dove Shampoo 200ml**
   - My Base Price: ₹90.00
   - Negotiated Price: ₹92.00 (premium!)
   - Quantity: 10 pieces
   - My Commission: (₹92 - ₹90) × 10 = ₹20.00 💚

4. Reviews order:
   ```
   Order Total: ₹1,750
   My Commission: ₹30.00
   ```

5. Clicks **"Submit Order"**

**What Happens:**
- ✅ SR Order created: SR-20260326-001-001
- ✅ Status: "Pending" (needs admin approval)
- ✅ Commission: ₹30.00 (pending)
- ✅ Order synced to server
- ✅ Rahul can continue to next shop

---

#### Step 3: Visit Customer #2 - Mini Mart

**At Mini Mart:**

**Shop Owner:** "Give me your best price on 50 Dove soaps."

**Rahul's Actions:**
1. Creates new order for Mini Mart
2. Adds Dove Soap:
   - My Base Price: ₹42.00
   - Negotiated Price: ₹40.50 (volume discount)
   - Quantity: 50 pieces
   - My Commission: (₹42 - ₹40.50) × 50 = ₹75.00 💚

**System Checks Scheme:**
```
🎁 Scheme Applied!
"Buy 50 Dove Soap, Get 10 Free"

Order Details:
- Billable: 50 pieces @ ₹40.50 = ₹2,025
- Free: 10 pieces @ ₹0.00 = ₹0
- Total to Deliver: 60 pieces
- Rahul's Commission: ₹75.00
```

3. Submits order

**Shop Owner:** "Great! 60 pieces for ₹2,025. Deal!"

---

#### Step 4: End of Day Summary

**Rahul's Dashboard:**
```
📱 Today's Performance
┌─────────────────────────────────────┐
│ Customers Visited: 15               │
│ Orders Created: 12                  │
│ Total Order Value: ₹48,500          │
│ Pending Commission: ₹1,250          │
│                                     │
│ Status Breakdown:                   │
│ - Pending Approval: 12 orders       │
│ - Approved: 0 orders                │
│ - Rejected: 0 orders                │
│                                     │
│ 🎯 Target Achievement: 97%          │
└─────────────────────────────────────┘
```

---

### Story: Admin Approves and Consolidates SR Orders

**Meet Priya - Admin**

"Rahul submitted 12 orders yesterday. Let me review and consolidate them."

#### Step 1: Review SR Orders

**Priya's Actions:**
1. Navigates to **SR → SR Orders**
2. Filters: Status = "Pending", SR = "Rahul Kumar"
3. Reviews each order:
   - Checks customer credit limit
   - Verifies stock availability
   - Reviews negotiated prices

**Priya's Checklist:**
```
✓ Corner Store: Credit OK, Stock OK, Price OK
✓ Mini Mart: Credit OK, Stock OK, Price OK
✓ Big Bazaar: Credit OK, Stock OK, Price OK
... (all 12 orders reviewed)
```

4. Selects all 12 orders
5. Clicks **"Bulk Approve"**

**What Happens:**
- ✅ All 12 orders status → "Approved"
- ✅ Orders now available for consolidation
- ✅ Rahul gets notification: "12 orders approved"

---

#### Step 2: Consolidate Orders

**Priya Notices:**
- Corner Store has 2 separate orders
- Mini Mart has 1 order
- Big Bazaar has 3 orders

**Priya's Actions:**
1. Navigates to **SR → Consolidate Orders**
2. Groups by customer:
   
   **Corner Store (2 orders):**
   - Order 1: 20 Dove Soap, 10 Shampoo
   - Order 2: 15 Lux Soap, 5 Toothpaste
   
3. Selects both Corner Store orders
4. Clicks **"Validate"**

**System Validation:**
```
✓ Same customer: Corner Store
✓ All orders approved
✓ Stock check:
  - Dove Soap: Need 20, Available 1,025 ✓
  - Shampoo: Need 10, Available 480 ✓
  - Lux Soap: Need 15, Available 200 ✓
  - Toothpaste: Need 5, Available 150 ✓
✓ All validations passed
```

5. Selects Location: "Main Warehouse"
6. Expected Shipment: Tomorrow
7. Clicks **"Generate Consolidated Order"**

**What Happens:**

**Sales Order Created:**
```
SO-20260326-015
Customer: Corner Store
Source: SR Consolidated
SR Orders: SR-001, SR-002

Line Items:
1. Dove Soap 100g
   - Quantity: 20
   - Negotiated Price: ₹41.50
   - Sale Price: ₹42.00
   - Price Difference: -₹0.50
   - SR: Rahul Kumar
   - Commission: ₹10.00

2. Dove Shampoo 200ml
   - Quantity: 10
   - Negotiated Price: ₹92.00
   - Sale Price: ₹90.00
   - Price Difference: +₹2.00
   - SR: Rahul Kumar
   - Commission: ₹20.00

3. Lux Soap 100g
   - Quantity: 15
   - Negotiated Price: ₹38.00
   - Sale Price: ₹40.00
   - Price Difference: -₹2.00
   - SR: Rahul Kumar
   - Commission: ₹30.00

4. Toothpaste
   - Quantity: 5
   - Negotiated Price: ₹55.00
   - Sale Price: ₹50.00
   - Price Difference: +₹5.00
   - SR: Rahul Kumar
   - Commission: ₹25.00

Total Commission: ₹85.00
```

**SR Order Updates:**
- ✅ SR-001 status → "Consolidated"
- ✅ SR-002 status → "Consolidated"
- ✅ Both linked to SO-20260326-015

---

#### Step 3: Delivery and Commission

**When SO is Delivered and Paid:**

**What Happens:**
1. SO Status → "Completed"
2. SR Order commission_disbursed → "Ready"
3. Rahul's commission_amount increased by ₹85.00

**Rahul's Commission Balance:**
```
Previous Balance: ₹500.00
New Commission: +₹85.00
Current Balance: ₹585.00
Status: Ready for Disbursement
```

---

#### Step 4: Commission Disbursement

**Priya Disburses Commission:**

**Priya's Actions:**
1. Navigates to **SR → Commission Disbursement**
2. Filters: Status = "Ready", SR = "Rahul Kumar"
3. Sees all completed orders with ready commission
4. Selects orders to disburse
5. Clicks **"Disburse Commission"**
6. Enters payment details:
   - Amount: ₹585.00
   - Method: Bank Transfer
   - Reference: TXN-2026-03-26-789
   - Bank: HDFC Bank
   - Account: Rahul's account
7. Clicks **"Process Disbursement"**

**What Happens:**
- ✅ Disbursement record created
- ✅ SR Orders commission_disbursed → "Disbursed"
- ✅ Rahul's commission_amount decreased by ₹585.00
- ✅ Payment recorded in accounts
- ✅ Rahul gets notification: "Commission ₹585 disbursed"

**Rahul's View:**
```
📱 Commission History
┌─────────────────────────────────────┐
│ March 26, 2026                      │
│ Disbursed: ₹585.00                  │
│ Method: Bank Transfer               │
│ Reference: TXN-2026-03-26-789       │
│ Status: Paid ✓                      │
│                                     │
│ Current Balance: ₹0.00              │
│ Pending: ₹1,165.00 (other orders)   │
└─────────────────────────────────────┘
```


---

## DSR Flow

### Story: DSR Delivers Orders to Customers

**Meet David - Delivery Sales Representative**

"Every morning I load orders in my van and deliver to customers throughout the day."

#### Step 1: Morning - Admin Assigns Orders

**Priya (Admin) Assigns Orders:**

**Priya's Actions:**
1. Navigates to **DSR → Assignments**
2. Clicks **"Assign Orders to DSR"**
3. Selects DSR: "David Kumar"
4. Selects orders to assign:
   ```
   ☑ SO-20260326-015 (Corner Store) - ₹2,500
   ☑ SO-20260326-018 (Mini Mart) - ₹3,200
   ☑ SO-20260326-021 (Big Bazaar) - ₹5,800
   
   Total: 3 orders, ₹11,500
   ```
5. Adds notes: "Priority: Big Bazaar (urgent)"
6. Clicks **"Assign to DSR"**

**What Happens:**
- ✅ DSR assignments created
- ✅ Status: "Assigned"
- ✅ David gets notification
- ✅ Orders appear in David's app

---

#### Step 2: David Loads Orders to Van

**David's Actions (Mobile App):**
1. Opens Shoudagor DSR App
2. Navigates to **"My Assignments"**
3. Sees 3 assigned orders
4. Clicks **"Load All to Van"**

**System Validation:**
```
Checking stock availability...

Corner Store Order:
✓ Dove Soap 100g: Need 20, Available 1,025
✓ Shampoo 200ml: Need 10, Available 480
✓ Lux Soap 100g: Need 15, Available 200
✓ Toothpaste: Need 5, Available 150

Mini Mart Order:
✓ Dove Soap 100g: Need 60, Available 1,005
✓ All items available

Big Bazaar Order:
✓ All items available

✓ All validations passed
Ready to load!
```

5. Confirms load

**What Happens Behind the Scenes:**

**Inventory Transfer:**
```
Main Warehouse → David's Van Storage

Dove Soap 100g:
- Warehouse: 1,025 → 945 pieces (-80)
- David's Van: 0 → 80 pieces (+80)

Dove Shampoo 200ml:
- Warehouse: 480 → 470 pieces (-10)
- David's Van: 0 → 10 pieces (+10)

Lux Soap 100g:
- Warehouse: 200 → 185 pieces (-15)
- David's Van: 0 → 15 pieces (+15)

... (all items transferred)
```

**Batch Allocation:**
```
For each item, batches allocated using FIFO:
- Oldest batches selected first
- Batch allocations created
- DSR batch allocations recorded
```

**Sales Order Updates:**
```
SO-20260326-015:
- is_loaded: true
- loaded_by_dsr_id: David's ID
- loaded_at: 2026-03-26 08:30:00

SO-20260326-018:
- is_loaded: true
- loaded_by_dsr_id: David's ID
- loaded_at: 2026-03-26 08:30:00

SO-20260326-021:
- is_loaded: true
- loaded_by_dsr_id: David's ID
- loaded_at: 2026-03-26 08:30:00
```

**David's Van Inventory:**
```
📱 My Van Inventory
┌─────────────────────────────────────┐
│ Loaded: March 26, 2026 08:30 AM     │
│                                     │
│ Dove Soap 100g: 80 pieces           │
│ Dove Shampoo 200ml: 10 pieces       │
│ Lux Soap 100g: 15 pieces            │
│ Toothpaste: 5 pieces                │
│ ... (more items)                    │
│                                     │
│ Total Value: ₹11,500                │
│ Orders: 3                           │
└─────────────────────────────────────┘
```

---

#### Step 3: Delivery #1 - Corner Store

**David Arrives at Corner Store:**

**David's Actions:**
1. Opens order SO-20260326-015
2. Clicks **"Make Delivery"**
3. Confirms items:
   ```
   Dove Soap 100g:
   - To Deliver: 20 pieces
   - Delivered: 20 pieces ✓
   - Rejected: 0
   
   Dove Shampoo 200ml:
   - To Deliver: 10 pieces
   - Delivered: 10 pieces ✓
   - Rejected: 0
   
   Lux Soap 100g:
   - To Deliver: 15 pieces
   - Delivered: 15 pieces ✓
   - Rejected: 0
   
   Toothpaste:
   - To Deliver: 5 pieces
   - Delivered: 5 pieces ✓
   - Rejected: 0
   ```

4. Gets customer signature on mobile
5. Takes photo of delivered items
6. Clicks **"Complete Delivery"**

**What Happens:**
- ✅ Delivery details recorded
- ✅ shipped_quantity updated for all items
- ✅ David's van inventory reduced
- ✅ Batch allocations updated
- ✅ Delivery status → "Completed"
- ✅ Photo and signature saved

**David's Van Inventory Updated:**
```
Dove Soap 100g: 80 → 60 pieces (-20)
Dove Shampoo 200ml: 10 → 0 pieces (-10)
Lux Soap 100g: 15 → 0 pieces (-15)
Toothpaste: 5 → 0 pieces (-5)
```

---

#### Step 4: Collect Payment

**Shop Owner:** "Here's the payment."

**David's Actions:**
1. Clicks **"Collect Payment"**
2. Enters payment details:
   - Amount: ₹2,500 (full payment)
   - Method: Cash
   - Reference: CASH-001
3. Clicks **"Collect"**

**What Happens:**
- ✅ Payment recorded
- ✅ SO payment status → "Completed"
- ✅ SO status → "Completed"
- ✅ Customer balance decreased by ₹2,500
- ✅ David's payment_on_hand increased by ₹2,500
- ✅ Receipt printed/emailed

**David's Cash on Hand:**
```
Previous: ₹0
Collected: +₹2,500
Current: ₹2,500
```

---

#### Step 5: Delivery #2 - Mini Mart (Partial Delivery)

**At Mini Mart - Issue Discovered:**

**Shop Owner:** "I ordered 60 Dove soaps, but I can only take 50 today. Storage issue."

**David's Actions:**
1. Opens order SO-20260326-018
2. Clicks **"Make Delivery"**
3. Adjusts quantities:
   ```
   Dove Soap 100g:
   - To Deliver: 60 pieces
   - Delivered: 50 pieces
   - Rejected: 0
   - Pending: 10 pieces
   ```
4. Adds note: "Customer storage full, will deliver remaining 10 tomorrow"
5. Gets signature for 50 pieces
6. Clicks **"Complete Delivery"**

**What Happens:**
- ✅ Partial delivery recorded
- ✅ shipped_quantity: 50 (not 60)
- ✅ Delivery status: "Partial"
- ✅ 10 pieces remain in David's van
- ✅ Can deliver remaining tomorrow

**David's Van Inventory:**
```
Dove Soap 100g: 60 → 10 pieces (10 pending for Mini Mart)
```

---

#### Step 6: Delivery #3 - Big Bazaar (With Return)

**At Big Bazaar - Quality Issue:**

**Shop Owner:** "5 Lux soaps have damaged packaging. I'll return them."

**David's Actions:**
1. Opens order SO-20260326-021
2. Clicks **"Make Delivery"**
3. Records delivery with return:
   ```
   Lux Soap 100g:
   - To Deliver: 20 pieces
   - Delivered: 15 pieces
   - Rejected: 5 pieces (damaged)
   - Reason: "Damaged packaging"
   ```
4. Takes photo of damaged items
5. Gets signature
6. Clicks **"Complete Delivery"**

**What Happens:**
- ✅ Delivery recorded: 15 pieces
- ✅ Return recorded: 5 pieces
- ✅ Rejected items back in David's van
- ✅ Effective total reduced
- ✅ Customer balance adjusted

**Financial Impact:**
```
Original Order: ₹5,800
Returned Items: -₹200 (5 × ₹40)
Effective Total: ₹5,600
```

**David's Van Inventory:**
```
Lux Soap 100g: 0 → 5 pieces (returned items)
```

---

#### Step 7: End of Day - Return to Office

**David's Summary:**
```
📱 Today's Deliveries
┌─────────────────────────────────────┐
│ Orders Delivered: 3                 │
│ - Completed: 2                      │
│ - Partial: 1                        │
│                                     │
│ Cash Collected: ₹11,100             │
│ - Corner Store: ₹2,500              │
│ - Mini Mart: ₹3,200 (partial)       │
│ - Big Bazaar: ₹5,400 (after return) │
│                                     │
│ Remaining in Van:                   │
│ - Dove Soap: 10 pieces (Mini Mart)  │
│ - Lux Soap: 5 pieces (returns)      │
└─────────────────────────────────────┘
```

---

#### Step 8: Settlement with Admin

**Back at Office:**

**Priya's Actions:**
1. Navigates to **DSR → Settlements**
2. Selects DSR: "David Kumar"
3. Sees payment_on_hand: ₹11,100
4. Clicks **"Settle Payment"**
5. Enters settlement:
   - Amount: ₹11,100 (full settlement)
   - Method: Cash Deposit
   - Reference: CASH-DEP-001
   - Notes: "End of day settlement"
6. Clicks **"Process Settlement"**

**What Happens:**
- ✅ Settlement record created
- ✅ David's payment_on_hand: ₹11,100 → ₹0
- ✅ Cash added to company accounts
- ✅ Settlement appears in history

**David's Account:**
```
📱 Settlement History
┌─────────────────────────────────────┐
│ March 26, 2026 - 06:30 PM           │
│ Settled: ₹11,100                    │
│ Method: Cash Deposit                │
│ Reference: CASH-DEP-001             │
│ Status: Settled ✓                   │
│                                     │
│ Current Balance: ₹0.00              │
└─────────────────────────────────────┘
```

---

#### Step 9: Unload Remaining Items

**David Unloads Pending Items:**

**David's Actions:**
1. Clicks **"Unload from Van"**
2. Selects items to unload:
   - Dove Soap: 10 pieces (Mini Mart pending)
   - Lux Soap: 5 pieces (returns)
3. Selects return location: "Main Warehouse"
4. Adds notes: "10 Dove for Mini Mart tomorrow, 5 Lux returns"
5. Clicks **"Unload"**

**What Happens:**

**Inventory Transfer:**
```
David's Van → Main Warehouse

Dove Soap 100g:
- David's Van: 10 → 0 pieces
- Warehouse: 945 → 955 pieces (+10)

Lux Soap 100g:
- David's Van: 5 → 0 pieces
- Warehouse: 185 → 190 pieces (+5)
```

**Mini Mart Order:**
```
SO-20260326-018:
- is_loaded: false (unloaded)
- Can be loaded again tomorrow
```

