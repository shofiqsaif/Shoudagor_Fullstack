# Purchase Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [Purchase Module Entry Point](#1-purchase-module-entry-point)
3. [Purchase Order Creation Workflow](#2-purchase-order-creation-workflow)
4. [Purchase Order Listing & Search](#3-purchase-order-listing--search)
5. [Goods Receipt (GRN) Workflow](#4-goods-receipt-grn-workflow)
6. [Purchase Return Workflow](#5-purchase-return-workflow)
7. [Payment Workflow](#6-payment-workflow)
8. [Purchase Order Status Management](#7-purchase-order-status-management)
9. [Purchase Order Cancellation & Deletion](#8-purchase-order-cancellation--deletion)
10. [Supplier Management](#9-supplier-management)
11. [Data Models](#10-data-models)

---

## Overview

The Purchase Module manages all procurement operations in Shoudagor ERP. It handles the complete purchase lifecycle from order creation to goods receipt, returns, and supplier payments.

### Key Entities
- **Purchase Order (PO)**: Master order document with supplier, date, location
- **Purchase Order Detail**: Line items with product, quantity, price, discounts
- **ProductOrderDeliveryDetail**: Records of goods received (GRN entries)
- **ProductOrderPaymentDetail**: Records of payments made to suppliers
- **Supplier**: Vendor information with contact details and balance tracking

### Core Functions
- **Create PO**: Raise purchase orders to suppliers
- **Receive Goods**: Record deliveries and update inventory (GRN)
- **Process Returns**: Return damaged/excess goods to suppliers
- **Make Payments**: Pay suppliers against purchase orders
- **Track Status**: Monitor order, payment, and delivery status
- **Supplier Balance**: Track payable amounts per supplier

---

## 1. Purchase Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Purchases'<br/>in main menu| C["📋 Purchases Listing Page"]
    B -->|Click 'Suppliers'<br/>in main menu| D["🏭 Suppliers Page"]
    B -->|Click 'New Purchase'<br/>quick action| E["➕ Create Purchase Order"]
    
    %% Purchases Page Components
    C --> C1["📊 Purchase Orders Table"]
    C --> C2["🔍 Search & Filter Panel"]
    C --> C3["⚡ Quick Action Buttons"]
    
    %% Table Columns
    C1 --> C1a["Order Number<br/>PO-XXXX format"]
    C1 --> C1b["Supplier Name<br/>Who you're buying from"]
    C1 --> C1c["Order Date<br/>When PO was created"]
    C1 --> C1d["Expected Delivery<br/>When goods should arrive"]
    C1 --> C1e["Total Amount<br/>Order value"]
    C1 --> C1f["Status<br/>Open/Partial/Completed/Cancelled"]
    C1 --> C1g["Payment Status<br/>Pending/Partial/Paid"]
    C1 --> C1h["Delivery Status<br/>Pending/Partial/Received"]
    
    %% Search & Filters
    C2 --> C2a["🔎 Search by order number"]
    C2 --> C2b["🏭 Filter by Supplier"]
    C2 --> C2c["📍 Filter by Location"]
    C2 --> C2d["✓ Filter by Status"]
    C2 --> C2e["📅 Date range filter"]
    C2 --> C2f["💰 Amount range filter"]
    
    %% Action Buttons
    C3 --> C3a["➕ New Purchase"]
    C3 --> C3b["📥 Download Report"]
    
    %% Row Actions
    C --> C4["⋮ Actions Menu (per row)"]
    C4 --> C4a["💰 Make Payment"]
    C4 --> C4b["🚚 Get Delivery (GRN)"]
    C4 --> C4c["📦 Return Purchase"]
    C4 --> C4d["👁️ View Details"]
    C4 --> C4e["🗑️ Delete"]
    
    %% Suppliers Page
    D --> D1["📋 Suppliers Table"]
    D --> D2["➕ Add Supplier Button"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E userAction
    class C1,D1 page
    class C2,C3,C4,D2 component
    class C1a,C1b,C1c,C1d,C1e,C1f,C1g,C1h,C2a,C2b,C2c,C2d,C2e,C2f,C3a,C3b,C4a,C4b,C4c,C4d,C4e data
```

### How to Navigate the Purchases Page

1. **Getting There**: Click "Purchases" in the left sidebar menu after logging in
2. **What You See**: A table listing all purchase orders with filtering options above
3. **Quick Actions**: Use the "New Purchase" button to create orders, "Download Report" for PDF export
4. **Row Actions**: Click the "⋮" (three dots) on any row to access payments, delivery, returns, or delete

### UI Elements - Purchases List Page

| Component | Type | Description |
|-----------|------|-------------|
| Search Input | Text Field | Search by order number |
| Supplier Filter | Dropdown | Filter by specific supplier |
| Location Filter | Dropdown | Filter by delivery location |
| Status Filter | Dropdown | Pending/Received/Cancelled |
| Order Date Range | Date Picker | Filter by order creation date |
| Delivery Date Range | Date Picker | Filter by expected delivery date |
| Amount Range | Slider | Min/Max amount filter |
| New Purchase | Button | Navigate to creation page |
| Download Report | Button | Generate PDF report |
| Purchases Table | Data Table | Paginated list with sorting |
| Actions Menu | Dropdown | Payment, Delivery, Return, View, Delete |

---

## 2. Purchase Order Creation Workflow

### 2.1 Step-by-Step: Creating a New Purchase Order

**Overview**: This workflow guides you through creating a purchase order with all items, pricing, and supplier details.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'New Purchase' button"] --> B["📄 Purchase Order Form Opens"]
    
    %% Step 1: Header Information
    B --> C["📋 STEP 1: Order Header"]
    C --> C1["📅 Select Order Date*<br/>Defaults to today"]
    C --> C2["📅 Select Expected Delivery Date*<br/>When goods should arrive"]
    C --> C3["🏷️ Enter Order Number<br/>Auto-generated or manual"]
    C --> C4["🏭 Select Supplier*<br/>Choose from dropdown"]
    C --> C5["📍 Select Location*<br/>Where goods will be received"]
    C --> C6["💰 Enter Amount Paid<br/>If advance payment made"]
    
    %% Duplicate Check
    C3 --> D{"❓ Order number exists?"}
    D -->|Yes| D1["⚠️ Error: 'Order number already exists'<br/>Use unique number"]
    D -->|No| E["✅ Continue to items"]
    D1 --> C3
    
    %% Step 2: Add Items
    E --> F["📦 STEP 2: Add Order Items"]
    F --> F0["💡 Individual Entry or<br/>📁 Product Group Selection"]
    
    %% Add Item
    F --> F1["➕ Click 'Add Item' or<br/>📁 Select Product Group"]
    F1 --> F2["🪟 Item Selection"]
    
    %% Item Details
    F2 --> G["📋 Enter Item Details"]
    G --> G1["📦 Select Product*<br/>From product dropdown"]
    G --> G2["🎨 Select Variant*<br/>SKU/Size/Color options"]
    G --> G3["📊 Enter Quantity*<br/>How many to order"]
    G --> G4["⚖️ Select Unit of Measure*<br/>Pieces, kg, boxes..."]
    G --> G5["💵 Enter Unit Price*<br/>Price per unit"]
    G --> G6["💰 Or Enter Total Amount<br/>Auto-calculate unit price"]
    G --> G7["🎁 Free Quantity<br/>Free items from supplier"]
    
    %% Scheme Application
    G --> H["🎯 Apply Scheme (Optional)"]
    H --> H1["Select Claim Scheme<br/>Buy X Get Y, Discounts..."]
    H --> H2["Auto-calculate:<br/>- Free items<br/>- Discount amount"]
    
    %% Validation
    H --> I["🔍 Validation Checks"]
    I --> I1{"✓ Valid product/variant?"}
    I1 -->|No| I1a["❌ Error: Select valid product"]
    I --> I2{"✓ Quantity > 0?"}
    I2 -->|No| I2a["❌ Error: Enter valid quantity"]
    I --> I3{"✓ Unit price >= 0?"}
    I3 -->|No| I3a["❌ Error: Enter valid price"]
    I3 -->|Yes| J["✅ Item added to order"]
    
    %% Add More
    J --> K{"🤔 Add more items?"}
    K -->|Yes| F1
    K -->|No, I'm done| L["📊 Review Order Summary"]
    
    %% Summary
    L --> L1["📈 Total Items: X"]
    L --> L2["💰 Total Amount: XXX"]
    L --> L3["🎁 Free Items: X"]
    L --> L4["💵 Discount Applied: XXX"]
    
    %% Submit
    L --> M["💾 Click 'Create Purchase Order'"]
    
    %% Final Validation
    M --> N{"✓ At least 1 item?"}
    N -->|No| N1["❌ Error: 'Add at least one item'"]
    N -->|Yes| O["🔄 Submitting to system..."]
    
    %% Backend Process
    O --> P["🌐 API: POST /procurement/purchase-orders/"]
    P --> Q["💾 Creating PO Master Record"]
    Q --> R["💾 Creating PO Detail Records"]
    R --> S["📈 Logging Scheme Applications"]
    S --> T["💰 Updating Supplier Balance<br/>+Total Amount"]
    T --> U["📦 Creating Delivery Records<br/>If received_quantity > 0"]
    U --> V["💳 Creating Payment Record<br/>If amount_paid > 0"]
    
    %% Completion
    V --> W["✅ PO Created Successfully!"]
    W --> X["🏠 Redirect to Purchases List"]
    X --> Y["🎉 Success: 'Purchase order created'"]
    
    %% Excel Import Path
    F0 --> Z["📤 Import from Excel"]
    Z --> Z1["Select .xlsx file"]
    Z1 --> Z2["Validate columns:<br/>- VariantSKU<br/>- Quantity<br/>- UnitPrice"]
    Z2 --> Z3{"✓ All rows valid?"}
    Z3 -->|No| Z3a["❌ Show error report<br/>Fix and re-upload"]
    Z3 -->|Yes| Z4["✅ Import items to form"]
    Z4 --> L
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef import fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class A start
    class C,F,L step
    class C1,C2,C3,C4,C5,C6,G1,G2,G3,G4,G5,G6,G7,H1 input
    class D,I1,I2,I3,K,N decision
    class D1,I1a,I2a,I3a,N1,Z3a error
    class J,L1,L2,L3,L4,W,X,Y success
    class M,O,P,Q,R,S,T,U,V backend
    class Z,Z1,Z2,Z4 import
```

### 💡 Tips for Purchase Order Creation

1. **Supplier Selection**: Choose from existing suppliers (add new suppliers in Suppliers page first)
2. **Location**: Select where goods will be received (affects inventory stock location)
3. **Order Number**: Leave blank for auto-generation, or enter custom format
4. **Product Selection**: Search products by name, then select specific variant (SKU)
5. **Scheme Benefits**: Apply claim schemes for automatic discounts/free items
6. **Excel Import**: Use bulk import for large orders - download template first
7. **Advance Payment**: Enter amount paid if you're paying upfront

### 2.2 Field Requirements & Validation

| Field | Required | Validation Rules |
|-------|----------|------------------|
| Order Date | Yes | Valid date, defaults to today |
| Expected Delivery | Yes | Must be today or future date |
| Order Number | No | Unique per company if provided |
| Supplier | Yes | Must exist in system |
| Location | Yes | Must exist in system |
| Product | Yes | Must exist in system |
| Variant | Yes | Must belong to selected product |
| Quantity | Yes | Number > 0 |
| Unit of Measure | Yes | Must exist in system |
| Unit Price | Yes | Number >= 0 |

### 2.3 Excel Import Format

Your import file must have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| **VariantSKU** | Yes | SKU of the variant to order |
| **ProductCode** | Alternative | Product code + VariantAttribute |
| **Quantity** | Yes | How many to order |
| **UnitPrice** | Yes | Price per unit |
| **UnitName** | No | Unit of measure (matches variant if omitted) |
| **VariantAttribute** | No | Required if using ProductCode instead of SKU |

---

## 3. Purchase Order Listing & Search

### 3.1 How the Purchases Page Loads

**What happens when you open the Purchases page:**

```mermaid
flowchart TD
    %% Page Load
    A["🏠 User clicks 'Purchases' menu"] --> B["🔐 System identifies your company"]
    
    %% Loading Supporting Data
    B --> C["📦 Loading helper data..."]
    C --> C1["🏭 Loading suppliers list<br/>For supplier filter"]
    C --> C2["📍 Loading locations list<br/>For location filter"]
    
    %% Loading Purchases
    C --> D["🔍 Loading purchase orders..."]
    D --> D1["📡 API: GET /procurement/purchase-orders/"]
    D1 --> D2["⚙️ Applying filters"]
    D2 --> D3["📄 POs returned with pagination"]
    
    %% Data Processing
    D3 --> G["⚙️ Preparing data for display..."]
    G --> G1["🔗 Joining supplier data<br/>Names, codes"]
    G --> G2["🔗 Joining location data<br/>Warehouse names"]
    G --> G3["🧮 Calculating effective totals<br/>Minus returns/rejections"]
    G --> G4["📊 Calculating unpaid amounts<br/>Total - Amount Paid"]
    
    %% Display
    G4 --> H["🖥️ Displaying Purchase Table"]
    H --> H1["📊 Showing all columns"]
    H --> H2["⋮ Actions menu on each row"]
    H --> H3["🔍 Filter panels above table"]
    
    %% User Interactions
    H --> I["👤 Now you can interact:"]
    I --> I1["🔎 Type in search box"]
    I --> I2["📂 Apply filters<br/>Supplier, Location, Status, Dates"]
    I --> I3["📄 Change page<br/>Click pagination"]
    I --> I4["🔃 Sort columns<br/>Click headers"]
    
    %% System Response
    I1 --> J["🔄 Refreshes results"]
    I2 --> K["🔄 Table refreshes<br/>Filtered results"]
    I3 --> L["📄 New page loads"]
    I4 --> M["🔃 Re-sorts data"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A,I,I1,I2,I3,I4 userAction
    class B,C,D,G,H system
    class C1,C2,G1,G2,G3,G4,H1,H2,H3 data
    class D1,D2 api
```

### 📱 Quick Guide: Finding Purchase Orders

| What you want to do | How to do it |
|---------------------|--------------|
| **Search by PO number** | Type in search box |
| **Filter by supplier** | Use "Supplier" dropdown |
| **Filter by location** | Use "Location" dropdown |
| **Show pending orders** | Use "Status" filter → Pending |
| **Find unpaid orders** | Sort by "Amount Unpaid" column |
| **View date range** | Use Order Date or Delivery Date filters |
| **Make payment** | Click "⋮" → Make Payment |
| **Record delivery** | Click "⋮" → Get Delivery |

### 3.2 Purchase Order Status Badges

```mermaid
flowchart LR
    subgraph OrderStatus["Order Status"]
        A["⏳ Pending<br/>New order, no activity"]
        B["📦 Partial<br/>Some deliveries/payments"]
        C["✅ Completed<br/>Fully delivered & paid"]
        D["❌ Cancelled<br/>Order cancelled"]
    end
    
    subgraph PaymentStatus["Payment Status"]
        E["⏳ Pending<br/>Nothing paid"]
        F["💰 Partial<br/>Partially paid"]
        G["✅ Completed<br/>Fully paid"]
    end
    
    subgraph DeliveryStatus["Delivery Status"]
        H["⏳ Pending<br/>Nothing received"]
        I["🚚 Partial<br/>Partially received"]
        J["✅ Completed<br/>Fully received"]
    end
```

---

## 4. Goods Receipt (GRN) Workflow

### 4.1 Step-by-Step: Recording a Delivery (GRN)

**Overview**: Use this workflow when goods arrive from the supplier. This creates the Goods Received Note (GRN) and updates inventory.

```mermaid
flowchart TD
    %% Start
    A["🚚 Goods arrive from supplier"] --> B["📋 Go to Purchases page"]
    
    %% Find PO
    B --> C["🔍 Find the Purchase Order"]
    C --> D["⋮ Click Actions menu on PO row"]
    D --> E["✅ Select 'Get Delivery'"]
    
    %% Form Opens
    E --> F["🪟 Delivery Dialog Opens"]
    F --> F1["⏳ Loading PO details..."]
    F1 --> F2["📦 Display ordered items"]
    
    %% Enter Delivery Details
    F --> G["📋 Enter Delivery Information"]
    G --> G1["📅 Delivery Date*<br/>When goods arrived"]
    G --> G2["📦 For each item, enter:<br/>- Delivered Quantity<br/>- Delivered Free Quantity<br/>- Rejected Quantity<br/>- Rejected Free Quantity"]
    G --> G3["📝 Add Remarks<br/>Optional notes"]
    
    %% Validation
    G --> H["🔍 Validation Checks"]
    H --> H1{"Qty delivered > 0?"}
    H1 -->|No| H1a["⚠️ Skip this item<br/>No update"]
    H --> H2{"Delivered <= Ordered?"}
    H2 -->|No| H2a["❌ Error: Cannot exceed ordered quantity"]
    H --> H3{"Rejected <= Remaining?"}
    H3 -->|No| H3a["❌ Error: Cannot reject more than pending"]
    H2 -->|Yes| I["✅ Items validated"]
    H3 -->|Yes| I
    
    %% Process
    I --> J["💾 Click 'Submit Delivery'"]
    J --> K["🔄 Processing delivery..."]
    
    %% Backend
    K --> L["🌐 API: POST /procurement/purchase-orders/{id}/delivery"]
    L --> M["💾 Creating Delivery Detail Records"]
    M --> N["📦 Updating Inventory Stock<br/>+Delivered quantities"]
    N --> O["🏷️ Creating Batch Records<br/>If batch tracking enabled"]
    O --> P["📊 Updating PO Delivery Status"]
    P --> Q["📝 Creating Inventory Transactions<br/>For audit trail"]
    Q --> R["📈 Updating Supplier Balance<br/>If rejections affect total"]
    
    %% Completion
    R --> S["✅ Delivery Recorded!"]
    S --> T["🎉 Success: 'Delivery created successfully'"]
    T --> U["🔄 PO status updated<br/>Inventory quantities updated"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C,D,E start
    class F,G form
    class H1,H2,H3 decision
    class H2a,H3a error
    class H1a success
    class J,K,L,M,N,O,P,Q,R,S,T,U backend
```

### 💡 Tips for Recording Deliveries

1. **Delivery Date**: Use the actual date goods arrived (may differ from expected date)
2. **Partial Deliveries**: You can record partial quantities - PO stays "Partial" status
3. **Rejected Items**: Record rejections for damaged/incorrect items - affects supplier balance
4. **Free Items**: Record delivered free quantities separately from ordered quantities
5. **Batch Creation**: If batch tracking is enabled, new batches are auto-created for received items
6. **Inventory Updates**: Stock is immediately added to the selected location

### 4.2 Understanding GRN Quantities

```mermaid
flowchart TD
    A["Ordered Quantity"] --> B["Delivered Quantity<br/>✓ Accepted into stock"]
    A --> C["Rejected Quantity<br/>❌ Damaged/Wrong - goes back"]
    A --> D["Returned Quantity<br/>↩️ Later returned to supplier"]
    
    B --> E["Effective Quantity<br/>Actually kept = Delivered - Returned"]
    
    F["Free Quantity<br/>(Ordered)"] --> G["Delivered Free<br/>✓ Accepted"]
    F --> H["Rejected Free<br/>❌ Damaged"]
    
    %% Styling
    classDef ordered fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef delivered fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef rejected fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef returned fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef free fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,F ordered
    class B,G delivered
    class C,H rejected
    class D returned
    class E free
```

---

## 5. Purchase Return Workflow

### 5.1 Step-by-Step: Processing a Return to Supplier

**Overview**: Use this workflow when returning goods to the supplier (damaged, excess, wrong items).

```mermaid
flowchart TD
    %% Start
    A["📦 Need to return goods to supplier"] --> B["📋 Go to Purchases page"]
    
    %% Find PO
    B --> C["🔍 Find the Purchase Order"]
    C --> D["⋮ Click Actions menu"]
    D --> E["↩️ Select 'Return Purchase'"]
    
    %% Form Opens
    E --> F["🪟 Return Dialog Opens"]
    F --> F1["⏳ Loading delivered items..."]
    F1 --> F2["📋 Show items available for return<br/>Based on received_quantity"]
    
    %% Enter Return Details
    F --> G["📋 Enter Return Information"]
    G --> G1["📅 Return Date*<br/>When items being returned"]
    G --> G2["📦 For each item, enter:<br/>Return Quantity"]
    G --> G3["📝 Remarks<br/>Reason for return"]
    
    %% Validation
    G --> H["🔍 Validation Checks"]
    H --> H1{"Return Qty > 0?"}
    H1 -->|No| H1a["⚠️ Skip this item"]
    H --> H2{"Return Qty <= Received?"}
    H2 -->|No| H2a["❌ Error: Cannot return more than received"]
    H --> H3{"Stock available?<br/>(Batch check)"}
    H3 -->|No| H3a["❌ Error: Items already sold/used<br/>Insufficient batch quantity"]
    H2 -->|Yes| I["✅ Items validated"]
    H3 -->|Yes| I
    
    %% Submit
    I --> J{"✓ At least 1 item to return?"}
    J -->|No| J1["❌ Error: Enter quantity for at least one item"]
    J -->|Yes| K["💾 Click 'Process Return'"]
    
    %% Backend
    K --> L["🌐 API: POST /procurement/purchase-orders/{id}/return"]
    L --> M["🔍 Pre-validation:<br/>Check all items can be returned"]
    M --> N{"✓ All validations pass?"}
    N -->|No| N1["❌ Show errors<br/>Return cancelled"]
    N -->|Yes| O["🔄 Executing return..."]
    
    %% Execution
    O --> P["📦 Update PO Detail<br/>-received_quantity<br/>+returned_quantity"]
    P --> Q["📦 Update Inventory Stock<br/>-Return quantities"]
    Q --> R["🏷️ Update Batch Quantities<br/>Decrement batches (FIFO)"]
    R --> S["📝 Create Inventory Transaction<br/>Type: PURCHASE_RETURN"]
    S --> T["📊 Create Batch Movement<br/>Type: RETURN_OUT"]
    T --> U["💰 Update Supplier Balance<br/>-Value of returned items<br/>(at effective TP)"]
    V --> W["📈 Update PO Status<br/>Recalculate delivery status"]
    
    %% Completion
    W --> X["✅ Return Processed!"]
    X --> Y["🎉 Success: 'Return processed successfully'"]
    Y --> Z["🔄 Stock and balance updated"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C,D,E start
    class F,G form
    class H1,H2,H3,J,N decision
    class H2a,H3a,J1,N1 error
    class H1a success
    class K,L,M,O,P,Q,R,S,T,U,V,W,X,Y,Z backend
```

### 💡 Tips for Purchase Returns

1. **Return Eligibility**: Can only return items that have been received (based on received_quantity)
2. **Batch Tracking**: System checks batch availability - cannot return already-sold items
3. **FIFO Returns**: Batch quantities are reduced using FIFO (First In, First Out) method
4. **Supplier Balance**: Return value (at effective TP) is deducted from supplier balance
5. **Inventory Impact**: Stock is immediately reduced from the location
6. **Status Update**: PO delivery status is recalculated after return

### 5.2 Return vs Rejection

| Aspect | Rejection (During Delivery) | Return (After Acceptance) |
|--------|----------------------------|------------------------|
| **When** | At time of receiving goods | After goods accepted into stock |
| **Stock Impact** | Never added to inventory | Deducted from inventory |
| **Batch Impact** | No batch created for rejected | Batch quantity reduced |
| **Transaction** | No inventory transaction | PURCHASE_RETURN transaction |
| **Calculation** | Deducted from order total | Deducted from supplier balance |

---

## 6. Payment Workflow

### 6.1 Step-by-Step: Making a Payment to Supplier

**Overview**: Use this workflow to record payments made to suppliers against purchase orders.

```mermaid
flowchart TD
    %% Start
    A["💰 Need to pay supplier"] --> B["📋 Go to Purchases page"]
    
    %% Find PO
    B --> C["🔍 Find the Purchase Order"]
    C --> D["⋮ Click Actions menu"]
    D --> E["💵 Select 'Make Payment'"]
    
    %% Form Opens
    E --> F["🪟 Payment Dialog Opens"]
    F --> F1["📊 Display Payment Summary"]
    
    %% Summary Display
    F1 --> F2["📈 Total Amount: XXX"]
    F1 --> F3["💰 Effective Total: XXX<br/>(Minus returns/rejections)"]
    F1 --> F4["💵 Amount Paid: XXX"]
    F1 --> F5["📊 Remaining Balance: XXX<br/>Highlighted prominently"]
    
    %% Already Paid Check
    F5 --> G{"Remaining Balance > 0?"}
    G -->|No| G1["✅ Show: 'Payments completed'"]
    G -->|Yes| H["📋 Enter Payment Details"]
    
    %% Payment Form
    H --> H1["📅 Payment Date*<br/>When payment made"]
    H --> H2["💵 Amount Paid*<br/>How much being paid"]
    H --> H3["💳 Payment Method<br/>Cash, Bank, Check..."]
    H --> H4["📝 Transaction Reference<br/>Check number, transfer ID"]
    H --> H5["📝 Remarks<br/>Optional notes"]
    
    %% Quick Actions
    H --> I["⚡ Quick Action:<br/>'Full Payment' button<br/>Auto-fills remaining balance"]
    
    %% Validation
    H --> J["🔍 Validation"]
    J --> J1{"Amount > 0?"}
    J1 -->|No| J1a["❌ Error: Enter valid amount"]
    J --> J2{"Amount <= Remaining?"}
    J2 -->|No| K["⚠️ Overpayment Warning"]
    
    %% Overpayment
    K --> K1["📝 Require Remarks<br/>'Why overpaying?'"]
    K --> K2["🔔 Show confirmation dialog"]
    K2 --> K3{"User confirms?"}
    K3 -->|No| K3a["↩️ Back to form"]
    K3 -->|Yes| L["✅ Proceed with overpayment"]
    J2 -->|Yes| L
    
    %% Submit
    L --> M["💾 Click 'Submit Payment'"]
    M --> N["🌐 API: POST /procurement/purchase-orders/{id}/payment"]
    
    %% Backend
    N --> O["💾 Creating Payment Detail Record"]
    O --> P["📊 Updating PO Payment Status"]
    P --> Q{"Total paid >= Effective total?"}
    Q -->|Yes| Q1["✅ Set status: Completed"]
    Q -->|No| Q2["⏳ Set status: Partial"]
    Q1 --> R["📈 Update PO Overall Status"]
    Q2 --> R
    
    %% Overpayment Handling
    R --> S{"Overpayment?"}
    S -->|Yes| S1["💰 Add excess to supplier balance<br/>(Advance payment)"]
    S -->|No| T["✅ Payment Complete"]
    S1 --> T
    
    %% Completion
    T --> U["🎉 Success: 'Payment created successfully'"]
    U --> V["🔄 Payment reflected in supplier balance"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef summary fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C,D,E start
    class F,H form
    class F1,F2,F3,F4,F5 summary
    class G,J1,J2,K3,Q,S decision
    class J1a error
    class G1,L,Q1 success
    class M,N,O,P,Q2,R,S1,T,U,V backend
```

### 💡 Tips for Supplier Payments

1. **Full Payment Button**: Use "Full Payment" button to auto-fill the remaining balance
2. **Partial Payments**: Make multiple partial payments - system tracks cumulative amount paid
3. **Overpayments**: System allows overpayment with confirmation; excess goes to supplier balance as advance
4. **Payment Methods**: Enter method (Cash, Bank Transfer, Check) for record keeping
5. **Reference Number**: Record check numbers or transaction IDs for reconciliation
6. **Effective Total**: Payments are matched against effective total (minus returns/rejections)

---

## 7. Purchase Order Status Management

### 7.1 Status Flow Diagram

```mermaid
flowchart TD
    subgraph OrderLifecycle["Purchase Order Lifecycle"]
        A["🆕 OPEN<br/>Newly created<br/>No deliveries/payments"] 
        B["📦 PARTIAL<br/>Some items delivered<br/>or partially paid"]
        C["✅ COMPLETED<br/>Fully delivered<br/>& fully paid"]
        D["❌ CANCELLED<br/>Order cancelled<br/>No deliveries/payments"]
    end
    
    A -->|"Receive delivery<br/>or Make payment"| B
    B -->|"Full delivery<br/>& Full payment"| C
    A -->|"Cancel (no activity)"| D
    B -->|"Cancel (no further<br/>deliveries/payments)"| D
    
    %% Styling
    classDef open fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef partial fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef completed fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef cancelled fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A open
    class B partial
    class C completed
    class D cancelled
```

### 7.2 How Status Updates Work

```mermaid
flowchart TD
    A["Activity Occurs"] --> B{"What happened?"}
    
    B -->|"Delivery Recorded"| C["Update Delivery Status"]
    B -->|"Payment Made"| D["Update Payment Status"]
    B -->|"Return Processed"| E["Recalculate All Statuses"]
    
    C --> C1{"Fully delivered?"}
    C1 -->|Yes| C2["Set: Completed"]
    C1 -->|No| C3["Set: Partial"]
    
    D --> D1{"Fully paid?"}
    D1 -->|Yes| D2["Set: Completed"]
    D1 -->|No| D3["Set: Partial"]
    
    C2 --> F["Update Overall Status"]
    C3 --> F
    D2 --> F
    D3 --> F
    E --> F
    
    F --> F1{"Both Completed?"}
    F1 -->|Yes| F2["✅ Order Status: Completed"]
    F1 -->|No| F3{"Any activity?"}
    F3 -->|Yes| F4["📦 Order Status: Partial"]
    F3 -->|No| F5["⏳ Order Status: Open"]
    
    %% Styling
    classDef trigger fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B trigger
    class C,D,E,F process
    class C1,D1,F1,F3 decision
    class C2,C3,D2,D3,F2,F4,F5 success
```

---

## 8. Purchase Order Cancellation & Deletion

### 8.1 Cancellation Workflow

**Cancel**: Soft-close an order that won't be fulfilled (reverses supplier balance).

```mermaid
flowchart TD
    A["❌ Need to cancel order"] --> B["📋 Go to Purchases page"]
    B --> C["🔍 Find the PO"]
    C --> D["⚠️ Check if cancellable"]
    
    D --> D1{"✓ No deliveries?"}
    D1 -->|No| D1a["❌ Cannot cancel<br/>Deliveries recorded"]
    D --> D2{"✓ No payments?"}
    D2 -->|No| D2a["❌ Cannot cancel<br/>Payments recorded"]
    D --> D3{"✓ Not completed?"}
    D3 -->|No| D3a["❌ Cannot cancel<br/>Already completed"]
    
    D1 -->|Yes| E
    D2 -->|Yes| E
    D3 -->|Yes| E["✅ Eligible for cancellation"]
    
    E --> F["🌐 API: Cancel request"]
    F --> G["💾 Set status: Cancelled"]
    G --> H["💰 Reverse supplier balance<br/>-Total Amount"]
    H --> I["🎉 Success: Order cancelled"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef check fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef block fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C start
    class D,D1,D2,D3 check
    class D1a,D2a,D3a block
    class E success
    class F,G,H,I backend
```

### 8.2 Deletion Workflow

**Delete**: Permanently remove an order (only allowed if no deliveries/payments).

```mermaid
flowchart TD
    A["🗑️ Need to delete order"] --> B["📋 Go to Purchases page"]
    B --> C["🔍 Find the PO"]
    C --> D["⋮ Click Actions → Delete"]
    
    D --> E["⚠️ Delete Confirmation Dialog"]
    E --> E1["⚠️ Warning: This action:<br/>- Removes PO record<br/>- Reverses supplier balance<br/>- Deletes all details"]
    E --> E2["📝 Type to confirm:<br/>'Delete order #{number}'"]
    
    E --> F{"User confirms?"}
    F -->|No| F1["↩️ Cancelled"]
    F -->|Yes| G["🔍 Validation Check"]
    
    G --> G1{"✓ No deliveries?"}
    G1 -->|No| G1a["❌ Error: Cannot delete<br/>Has deliveries"]
    G --> G2{"✓ No payments?"}
    G2 -->|No| G2a["❌ Error: Cannot delete<br/>Has payments"]
    
    G1 -->|Yes| H
    G2 -->|Yes| H["✅ Eligible for deletion"]
    
    H --> I["🌐 API: DELETE request"]
    I --> J["💾 Soft-delete PO<br/>(Mark is_deleted=true)"]
    J --> K["💾 Soft-delete all details"]
    K --> L["💾 Soft-delete delivery records"]
    L --> M["💾 Soft-delete payment records"]
    M --> N["💰 Reverse supplier balance"]
    N --> O["🎉 Success: Order deleted"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef confirm fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef check fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef block fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C,D start
    class E,E1,E2,F confirm
    class G,G1,G2 check
    class G1a,G2a,F1 block
    class H success
    class I,J,K,L,M,N,O backend
```

### 💡 Cancel vs Delete

| Aspect | Cancel | Delete |
|--------|--------|--------|
| **Purpose** | Stop order, keep record | Completely remove order |
| **Record** | PO marked "Cancelled" | PO soft-deleted (hidden) |
| **History** | Visible in list with status | Removed from main list |
| **Reversible** | No (permanent status) | Admin can restore |
| **Requirements** | No deliveries, no payments | Same as cancel |
| **Supplier Balance** | Reversed | Reversed |

---

## 9. Supplier Management

### 9.1 Supplier Entry Point

```mermaid
flowchart TD
    A["👤 User logs in"] --> B["Click 'Suppliers' in menu"]
    B --> C["📋 Suppliers List Page"]
    
    C --> C1["📊 Suppliers Table"]
    C --> C2["🔍 Search & Filter"]
    C --> C3["➕ Add Supplier Button"]
    
    C1 --> D["Table Columns:"]
    D --> D1["Supplier Name"]
    D --> D2["Supplier Code"]
    D --> D3["Contact Info<br/>Phone, Email, Address"]
    D --> D4["Payment Terms"]
    D --> D5["Balance Amount<br/>Total payable"]
    D --> D6["Status<br/>Active/Inactive"]
    
    C --> E["⋮ Row Actions"]
    E --> E1["✏️ Edit Supplier"]
    E --> E2["🗑️ Delete Supplier"]
    E --> E3["📋 View Purchase Orders"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C userAction
    class C1 page
    class C2,C3 component
    class D1,D2,D3,D4,D5,D6 data
```

### 9.2 Supplier Balance Tracking

```mermaid
flowchart TD
    subgraph BalanceCalculation["Supplier Balance Calculation"]
        A["Starting Balance"] 
        B["+ Purchase Order Total<br/>When PO created"]
        C["- Returns<br/>Value at effective TP"]
        D["- Payments Made<br/>Recorded payments"]
        E["- Rejections<br/>During delivery"]
        F["= Current Balance<br/>Amount Payable"]
    end
    
    A --> B --> C --> D --> E --> F
    
    %% Styling
    classDef base fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef add fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef subtract fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef result fill:#fff8e1,stroke:#f9a825,stroke-width:3px
    
    class A base
    class B add
    class C,D,E subtract
    class F result
```

### 💡 Supplier Management Tips

1. **Balance Tracking**: Supplier balance automatically updates with every PO, return, and payment
2. **Payment Terms**: Record terms (e.g., "Net 30", "COD") for reference
3. **Contact Info**: Maintain complete address, phone, email for communication
4. **Code**: Use consistent supplier codes for easy identification
5. **Active Status**: Mark inactive suppliers to hide from PO dropdowns
6. **Purchase History**: View all POs for a supplier from the actions menu

---

## 10. Data Models

### 10.1 Purchase Order Entity Relationships

```mermaid
erDiagram
    PURCHASE_ORDER ||--o{ PURCHASE_ORDER_DETAIL : contains
    PURCHASE_ORDER ||--o{ PRODUCT_ORDER_PAYMENT_DETAIL : has
    PURCHASE_ORDER }o--|| SUPPLIER : from
    PURCHASE_ORDER }o--|| STORAGE_LOCATION : to
    PURCHASE_ORDER_DETAIL ||--o{ PRODUCT_ORDER_DELIVERY_DETAIL : receives
    PURCHASE_ORDER_DETAIL ||--o{ BATCH : creates
    PURCHASE_ORDER_DETAIL }o--|| PRODUCT : orders
    PURCHASE_ORDER_DETAIL }o--|| PRODUCT_VARIANT : specifies
    
    PURCHASE_ORDER {
        int purchase_order_id PK
        string order_number
        int supplier_id FK
        int location_id FK
        date order_date
        date expected_delivery_date
        decimal total_amount
        decimal amount_paid
        string status
        string payment_status
        string delivery_status
        int company_id
    }
    
    PURCHASE_ORDER_DETAIL {
        int purchase_order_detail_id PK
        int purchase_order_id FK
        int product_id FK
        int variant_id FK
        decimal quantity
        decimal unit_price
        decimal received_quantity
        decimal free_quantity
        decimal returned_quantity
        decimal rejected_quantity
        decimal discount_amount
        boolean is_free_item
    }
    
    PRODUCT_ORDER_DELIVERY_DETAIL {
        int delivery_detail_id PK
        int purchase_order_detail_id FK
        date delivery_date
        decimal delivered_quantity
        decimal delivered_free_quantity
        decimal rejected_quantity
        int received_by
    }
    
    PRODUCT_ORDER_PAYMENT_DETAIL {
        int payment_detail_id PK
        int purchase_order_id FK
        date payment_date
        decimal amount_paid
        string payment_method
        string transaction_reference
    }
    
    SUPPLIER {
        int supplier_id PK
        string supplier_name
        string supplier_code
        string payment_terms
        decimal balance_amount
        string phone
        string email
        string address
    }
```

### 10.2 Status Values Reference

| Entity | Status Values | Description |
|--------|--------------|-------------|
| **Purchase Order** | Open, Partial, Completed, Cancelled | Overall order status |
| **Payment Status** | Pending, Partial, Completed | Payment completion |
| **Delivery Status** | Pending, Partial, Completed | Goods receipt completion |

### 10.3 Important Calculations

```mermaid
flowchart LR
    subgraph EffectiveTotal["Effective Total Calculation"]
        A["Effective Total = Σ<BR/>(Ordered Qty - Returned Qty - Rejected Qty)<BR/>× Unit Price<BR/>- Discount"]
    end
    
    subgraph EffectiveTP["Effective TP Calculation"]
        B["Effective TP =<BR/>(Gross Price - Discount)<BR/>÷ (Ordered Qty + Free Qty)"]
    end
    
    subgraph UnpaidAmount["Unpaid Amount"]
        C["Unpaid =<BR/>Effective Total<BR/>- Amount Paid"]
    end
    
    %% Styling
    classDef calc fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    
    class A,B,C calc
```

---

## Summary

The Purchase Module provides comprehensive procurement management capabilities:

### Key Workflows:
1. **Create PO** → Add items → Submit → Update supplier balance
2. **Receive Goods** → Record delivery → Update inventory → Create batches
3. **Process Returns** → Select items → Reduce stock → Update supplier balance
4. **Make Payments** → Enter amount → Update payment status → Track balance

### Status Tracking:
- **Order Status**: Open → Partial → Completed/Cancelled
- **Payment Status**: Pending → Partial → Completed
- **Delivery Status**: Pending → Partial → Completed

### Integration Points:
- **Inventory**: Deliveries add stock, returns deduct stock
- **Batches**: Deliveries create new batches with supplier info
- **Suppliers**: Balance tracks total payable, updated by all transactions
- **Accounting**: All transactions create audit trail entries

### Security & Validation:
- Cannot delete PO with deliveries or payments
- Cannot cancel completed orders
- Cannot return more than received
- Batch availability checked before returns
- Overpayments require confirmation with remarks
