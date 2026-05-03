# Inventory Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [Inventory Module Entry Point](#1-inventory-module-entry-point)
3. [Inventory Stock View & Search](#2-inventory-stock-view--search)
4. [Stock Transfer Workflow](#3-stock-transfer-workflow)
5. [Inventory Adjustment Workflow](#4-inventory-adjustment-workflow)
6. [Single Item Stock Transfer](#5-single-item-stock-transfer)
7. [Bulk Stock Transfer](#6-bulk-stock-transfer)
8. [Inventory Reports & Analytics](#7-inventory-reports--analytics)
9. [Data Models](#8-data-models)

---

## Overview

The Inventory Module manages all stock-related operations in Shoudagor ERP. It tracks inventory across multiple warehouse locations, enables stock transfers between locations, handles inventory adjustments, and provides comprehensive stock visibility and reporting.

### Key Entities
- **Inventory Stock**: Current stock quantities at specific locations
- **Stock Transfer**: Movement of stock between warehouse locations
- **Inventory Adjustment**: Manual corrections to stock quantities
- **Storage Location**: Physical places where inventory is stored (warehouses, shelves, bins)
- **Inventory Transaction**: Record of all stock movements (in, out, transfers, adjustments)

### Core Functions
- **View Inventory**: See stock levels across all locations
- **Stock Transfer**: Move inventory between locations
- **Adjust Stock**: Correct inventory quantities manually
- **Track History**: View all inventory transactions
- **Monitor Levels**: Check reorder points and safety stock

---

## 1. Inventory Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Inventory'<br/>in main menu| C["📦 Inventory Stock Page"]
    B -->|Click 'Stock Transfer'<br/>in main menu| D["🚚 Stock Transfer Page"]
    B -->|Click 'Adjustments'<br/>in main menu| E["⚖️ Inventory Adjustments Page"]
    B -->|Click 'Warehouses'<br/>in main menu| F["🏭 Warehouse Management"]
    
    %% Inventory Stock Page Components
    C --> C1["📊 Inventory Stock Table"]
    C --> C2["🔍 Search & Filter Panel"]
    C --> C3["⚡ Quick Action Buttons"]
    
    %% Table Columns
    C1 --> C1a["Product Name<br/>What item is this"]
    C1 --> C1b["SKU<br/>Stock Keeping Unit"]
    C1 --> C1c["Variant<br/>Size, Color, Type"]
    C1 --> C1d["Location<br/>Where it's stored"]
    C1 --> C1e["Quantity<br/>Current stock count"]
    C1 --> C1f["Unit<br/>Pieces, kg, liters..."]
    C1 --> C1g["Last Stock Take<br/>When counted"]
    
    %% Search & Filters
    C2 --> C2a["🔎 Search by product name<br/>(instant search)"]
    C2 --> C2b["📂 Filter by Location"]
    C2 --> C2c["📦 Filter by Product"]
    C2 --> C2d["🎨 Filter by Variant"]
    
    %% Action Buttons
    C3 --> C3a["🚚 Transfer Stock"]
    C3 --> C3b["⚖️ Adjust Stock"]
    C3 --> C3c["📥 Export Stock Report"]
    
    %% Row Actions
    C --> C4["⋮ Actions Menu (per row)"]
    C4 --> C4a["🚚 Transfer This Stock"]
    C4 --> C4b["⚖️ Adjust Quantity"]
    C4 --> C4c["📋 View Transaction History"]
    
    %% Stock Transfer Page
    D --> D1["📋 Transfer List Table"]
    D --> D2["➕ Create Transfer Button"]
    D --> D3["🔍 Filter Transfers"]
    
    %% Adjustment Page
    E --> E1["📋 Adjustments List"]
    E --> E2["➕ Create Adjustment"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E,F userAction
    class C1,D1,E1 page
    class C2,C3,C4,D2,D3,E2 component
    class C1a,C1b,C1c,C1d,C1e,C1f,C1g,C2a,C2b,C2c,C2d,C3a,C3b,C3c,C4a,C4b,C4c data
```

### How to Navigate the Inventory Page

1. **Getting There**: Click "Inventory" in the left sidebar menu after logging in
2. **What You See**: A table showing all inventory items across all locations
3. **Quick Actions**: Use buttons at the top for transfers, adjustments, and exports
4. **Row Actions**: Click the "⋮" (three dots) on any row to perform actions on that specific stock item

### UI Elements - Inventory Stock Page

| Component | Type | Description |
|-----------|------|-------------|
| Search Input | Text Field | Debounced search (500ms) by product name |
| Location Filter | Dropdown | Filter by warehouse location |
| Product Filter | Dropdown | Filter by specific product |
| Variant Filter | Dropdown | Filter by product variant |
| Transfer Stock | Button | Navigate to stock transfer page |
| Adjust Stock | Button | Open adjustment dialog |
| Export | Button | Download inventory report as Excel |
| Inventory Table | Data Table | Paginated list with sorting |
| Actions Menu | Dropdown | Transfer, Adjust, View History |

---

## 2. Inventory Stock View & Search

### 2.1 How the Inventory Page Loads

**What happens when you open the Inventory page:**

```mermaid
flowchart TD
    %% Page Load
    A["🏠 User clicks 'Inventory' menu"] --> B["🔐 System identifies your company"]
    
    %% Loading Supporting Data
    B --> C["📦 Loading helper data..."]
    C --> C1["🏭 Loading locations list<br/>For location filter dropdown"]
    C --> C2["📦 Loading products list<br/>For product filter"]
    C --> C3["🎨 Loading variants list<br/>For variant filter"]
    
    %% Loading Inventory
    C --> D["🔍 Loading inventory data..."]
    D --> D1["📡 API: GET /warehouse/inventory-stock/"]
    D1 --> D2["⚙️ Applying filters"]
    D2 --> D3["📄 Inventory returned in pages"]
    
    %% Data Processing
    D3 --> G["⚙️ Preparing data for display..."]
    G --> G1["🔗 Joining product data<br/>Names, SKUs"]
    G --> G2["🔗 Joining location data<br/>Warehouse names"]
    G --> G3["🔗 Joining unit data<br/>UOM names"]
    G --> G4["📊 Formatting table data<br/>Quantities, dates"]
    
    %% Display
    G4 --> H["🖥️ Displaying Inventory Table"]
    H --> H1["📊 Showing all columns<br/>Product, SKU, Location, Qty"]
    H --> H2["⋮ Actions menu on each row<br/>Transfer, Adjust, History"]
    H --> H3["☑️ Checkboxes for batch select<br/>Transfer multiple at once"]
    
    %% User Interactions
    H --> I["👤 Now you can interact:"]
    I --> I1["🔎 Type in search box<br/>Instant search"]
    I --> I2["📂 Apply filters<br/>Location, Product, Variant"]
    I --> I3["📄 Change page<br/>Click pagination numbers"]
    I --> I4["🔃 Sort columns<br/>Click column headers"]
    
    %% System Response
    I1 --> J["⏱️ Waits 500ms after typing<br/>Then searches automatically"]
    I2 --> K["🔄 Table refreshes<br/>With filtered results"]
    I3 --> L["📄 New page loads<br/>More items shown"]
    I4 --> M["🔃 Re-sorts data<br/>Ascending/descending toggle"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A,I,I1,I2,I3,I4 userAction
    class B,C,D,G,H system
    class C1,C2,C3,G1,G2,G3,G4,H1,H2,H3 data
    class D1 api
```

### 📱 Quick Guide: Finding Inventory

| What you want to do | How to do it |
|---------------------|--------------|
| **Search by product** | Type in the search box - results appear instantly |
| **Filter by location** | Click the "Location" dropdown and select warehouse |
| **Find low stock** | Sort by "Quantity" column (ascending) |
| **View by product** | Use the "Product" filter dropdown |
| **Transfer stock** | Click "⋮" on row → Transfer This Stock |
| **Adjust quantity** | Click "⋮" on row → Adjust Quantity |

### 2.2 Inventory Stock Table Columns

```mermaid
flowchart TD
    A[Table Rendered] --> B[Selection Column]
    A --> C[Product Name Column]
    A --> D[SKU Column]
    A --> E[Variant Column]
    A --> F[Location Column]
    A --> G[Quantity Column]
    A --> H[Unit Column]
    A --> I[Last Stock Take Column]
    A --> J[Actions Column]
    
    C --> C1[Click to sort<br/>A-Z / Z-A]
    D --> D1[Click to sort<br/>By SKU]
    G --> G1[Click to sort<br/>Low to High / High to Low]
    
    J --> J1[Dropdown Menu]
    J1 --> J1a["🚚 Transfer Stock"]
    J1 --> J1b["⚖️ Adjust Quantity"]
    J1 --> J1c["📋 View History"]
```

---

## 3. Stock Transfer Workflow

### 3.1 Step-by-Step: Creating a Stock Transfer

**Overview**: This workflow guides you through transferring inventory from one location to another.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'Stock Transfer' menu<br/>or 'Transfer Stock' button"] --> B["📄 Stock Transfer Page Opens"]
    
    %% Step 1: Create New Transfer
    B --> C["➕ Click 'Create Transfer' Button"]
    C --> D["🪟 Transfer Creation Form Opens"]
    
    %% Transfer Header
    D --> E["📋 STEP 1: Transfer Details"]
    E --> E1["📅 Transfer Date<br/>Defaults to today"]
    E --> E2["🏭 Select Source Location*<br/>Where stock is coming FROM"]
    E --> E3["📝 Optional: Add Notes<br/>Reason for transfer"]
    
    %% Step 2: Add Items
    E --> F["📦 STEP 2: Add Items to Transfer"]
    F --> F1["➕ Click 'Add Item' Button"]
    F1 --> F2["🪟 Item Selection Modal Opens"]
    
    %% Item Selection
    F2 --> G["🔍 Select Products to Transfer"]
    G --> G1["📦 Select Product*<br/>From dropdown"]
    G --> G2["🎨 Select Variant<br/>If product has variants"]
    G --> G3["📊 Enter Quantity*<br/>How much to transfer"]
    G --> G4["⚖️ Select Unit of Measure<br/>Auto-filled from variant"]
    G --> G5["🏭 Select Target Location*<br/>Where stock is going TO"]
    G --> G6["📝 Add Item Notes<br/>Optional details"]
    
    %% Validation
    G --> H["🔍 Validation Checks"]
    H --> H1{"✓ Stock available?"}
    H1 -->|No| H1a["❌ Error: 'Insufficient stock'<br/>Show available quantity"]
    H1 -->|Yes| H2{"✓ Valid quantity?"}
    H2 -->|No| H2a["❌ Error: 'Invalid quantity'"]
    H2 -->|Yes| I["✅ Item added to transfer list"]
    
    %% Add More
    I --> J{"🤔 Add more items?"}
    J -->|Yes| F1
    J -->|No| K["➡️ Click 'Submit Transfer'"]
    
    %% Final Validation
    K --> L{"✓ At least 1 item?"}
    L -->|No| L1["❌ Error: 'Add at least one item'"]
    L1 --> F
    L -->|Yes| M["🔄 Processing Transfer..."]
    
    %% Backend Process
    M --> N["🌐 API: POST /warehouse/stock-transfer/"]
    N --> O["💾 Creating Transfer Record"]
    O --> P["📦 Deducting from Source Location"]
    P --> Q["📦 Adding to Target Location"]
    Q --> R["📝 Creating Inventory Transactions<br/>For audit trail"]
    
    %% Completion
    R --> S["✅ Transfer Complete!"]
    S --> T["📧 Success Message:<br/>'Stock transfer completed'"]
    T --> U["🔄 Refresh Inventory Table<br/>Updated quantities shown"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class C,D,E,F step
    class E1,E2,E3,G1,G2,G3,G4,G5,G6 input
    class H1,H2,J,L decision
    class H1a,H2a,L1 error
    class I,S,T,U success
    class M,N,O,P,Q,R backend
```

### 💡 Tips for Stock Transfers

1. **Check Stock First**: Verify available quantity in source location before transferring
2. **Same Company**: Source and target locations must belong to your company
3. **Batch Tracking**: If batch tracking is enabled, batches are automatically transferred
4. **UOM Conversion**: Quantities are automatically converted to base UOM
5. **Audit Trail**: Every transfer creates transaction records for tracking

### 3.2 Stock Transfer Status Flow

```mermaid
flowchart LR
    A["🆕 PENDING<br/>Transfer created"] --> B["⏳ IN_PROGRESS<br/>Being processed"]
    B --> C["✅ COMPLETED<br/>Stock moved successfully"]
    
    B --> D["❌ FAILED<br/>Error occurred"]
    D --> E["🔄 Can retry<br/>Or cancel"]
```

---

## 4. Inventory Adjustment Workflow

### 4.1 Step-by-Step: Creating an Inventory Adjustment

**Overview**: Use this workflow to manually adjust stock quantities (for damaged goods, stock takes, corrections).

```mermaid
flowchart TD
    %% Start
    A["👤 User needs to adjust stock"] --> B["⚖️ Click 'Adjust Stock' button"]
    
    %% Form Opens
    B --> C["🪟 Adjustment Dialog Opens"]
    C --> C1["⏳ Loading current stock info..."]
    
    %% Adjustment Header
    C --> D["📋 STEP 1: Adjustment Details"]
    D --> D1["📅 Adjustment Date<br/>Defaults to today"]
    D --> D2["🏭 Select Location*<br/>Which location to adjust"]
    D --> D3["📝 Reason for Adjustment*<br/>Damaged, Stock Take, Correction, etc."]
    
    %% Add Items
    D --> E["📦 STEP 2: Add Items to Adjust"]
    E --> E1["➕ Click 'Add Item'"]
    E1 --> E2["🪟 Item Selection Opens"]
    
    E2 --> F["🔍 Select Product"]
    F --> F1["📦 Select Product*<br/>From dropdown"]
    F --> F2["🎨 Select Variant<br/>If applicable"]
    F --> F3["📊 Current Quantity<br/>Auto-displayed"]
    
    F --> G["⚖️ Set Adjustment Type"]
    G --> G1["➕ Positive Adjustment<br/>Adding stock"]
    G --> G2["➖ Negative Adjustment<br/>Removing stock"]
    
    G --> H["📊 Enter Adjustment Quantity*"]
    H --> H1["💡 For positive:<br/>Enter amount to ADD"]
    H --> H2["💡 For negative:<br/>Enter amount to REMOVE"]
    
    H --> I["🎯 New Quantity Calculated<br/>Shows result preview"]
    
    %% Validation
    I --> J["🔍 Validation"]
    J --> J1{"Negative adjustment?"}
    J1 -->|Yes| J2{"Stock exists?"}
    J2 -->|No| J2a["❌ Error: 'No stock to deduct from'"]
    J2 -->|Yes| J3{"Sufficient stock?"}
    J3 -->|No| J3a["❌ Error: 'Insufficient stock'"]
    J3 -->|Yes| K["✅ Item valid"]
    J1 -->|No| K
    
    K --> L{"Add more items?"}
    L -->|Yes| E1
    L -->|No| M["💾 Click 'Submit Adjustment'"]
    
    %% Backend
    M --> N["🌐 API: POST /transaction/inventory-adjustment/"]
    N --> O["💾 Creating Adjustment Record"]
    O --> P["📦 Updating Stock Quantity"]
    P --> Q["📝 Creating Inventory Transaction<br/>For audit trail"]
    
    %% Result
    Q --> R["✅ Adjustment Complete!"]
    R --> S["📧 Success Message"]
    S --> T["🔄 Updated stock displayed"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B start
    class C,D,E step
    class D1,D2,D3,F1,F2,F3,H,H1,H2 input
    class J1,J2,J3,L decision
    class J2a,J3a error
    class K,R,S,T success
    class M,N,O,P,Q backend
```

### 💡 When to Use Adjustments

| Scenario | Adjustment Type | Example |
|----------|----------------|---------|
| **Damaged goods** | Negative | 10 items broken, reduce by 10 |
| **Stock take surplus** | Positive | Found 5 extra items, add 5 |
| **Stock take shortage** | Negative | Missing 3 items, reduce by 3 |
| **Initial stock setup** | Positive | Adding opening balance |
| **Data correction** | Positive/Negative | Fix wrongly entered quantity |

### ⚠️ Important Notes

- **Negative Adjustments**: Require existing stock - cannot deduct from zero
- **Batch Tracking**: If enabled, batch quantities are also adjusted
- **Audit Trail**: All adjustments create transaction records with reasons
- **Permissions**: Some users may need approval for large adjustments

---

## 5. Single Item Stock Transfer

### 5.1 Quick Transfer from Inventory Row

```mermaid
flowchart TD
    A["📦 On Inventory Stock Page"] --> B["⋮ Click Actions on row"]
    B --> C["🚚 Select 'Transfer This Stock'"]
    
    C --> D["🪟 Quick Transfer Dialog Opens"]
    D --> D1["📊 Pre-filled Data:<br/>- Product<br/>- Variant<br/>- Source Location<br/>- Available Qty"]
    
    D --> E["📋 Enter Transfer Details"]
    E --> E1["📅 Transfer Date<br/>Default: Today"]
    E --> E2["🏭 Target Location*<br/>Where to send"]
    E --> E3["📊 Quantity*<br/>How much to transfer"]
    E --> E4["⚖️ Unit of Measure<br/>Auto-filled"]
    E --> E5["📝 Notes<br/>Optional"]
    
    E --> F["🔍 Validation"]
    F --> F1{"Qty <= Available?"}
    F1 -->|No| F1a["❌ Error: Insufficient stock"]
    F1 -->|Yes| G["💾 Click 'Transfer'"]
    
    G --> H["🌐 API: POST /warehouse/inventory-stock/transfer"]
    H --> I["✅ Single Transfer Complete"]
    I --> J["🔄 Page refreshes<br/>Stock updated"]
    
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C action
    class D,E form
    class F1a error
    class G,I,J success
    class H backend
```

---

## 6. Bulk Stock Transfer

### 6.1 Transferring Multiple Items at Once

```mermaid
flowchart TD
    A["📦 On Inventory Stock Page"] --> B["☑️ Select Multiple Rows<br/>Checkboxes on left"]
    
    B --> C["🚚 Click 'Transfer Selected' Button<br/>Appears when items selected"]
    C --> D["🪟 Bulk Transfer Dialog Opens"]
    
    D --> E["📋 Selected Items Displayed<br/>Summary of items to transfer"]
    
    E --> F["📅 Transfer Date<br/>Default: Today"]
    F --> G["🏭 Source Locations<br/>Shown per item"]
    G --> H["🎯 Target Location*<br/>Select ONE location for all"]
    
    H --> I["📊 Enter Quantities"]
    I --> I1["Qty for Item 1*"]
    I --> I2["Qty for Item 2*"]
    I --> I3["... etc"]
    
    I --> J["🔍 Validation Per Item"]
    J --> J1{"All quantities valid?"}
    J1 -->|No| J1a["❌ Show errors per item"]
    J1 -->|Yes| K["💾 Click 'Transfer All'"]
    
    K --> L["🌐 API: POST /warehouse/stock-transfer/"]
    L --> M["💾 Processing bulk transfer"]
    M --> N["✅ All items transferred"]
    N --> O["📊 Results shown<br/>Success/failure per item"]
    
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef selection fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C action
    class B selection
    class D,E,F,G,H,I form
    class J1a error
    class K,L,M,N,O success
```

---

## 7. Inventory Reports & Analytics

### 7.1 Available Reports

```mermaid
flowchart TD
    A["📊 Inventory Reports Menu"] --> B["📦 Stock Summary Report"]
    A --> C["🚚 Stock Transfer Report"]
    A --> D["⚖️ Adjustment Report"]
    A --> E["📈 Transaction History"]
    A --> F["🔔 Low Stock Alert"]
    
    B --> B1["Current stock by location"]
    B --> B2["Stock value calculation"]
    B --> B3["Export to Excel"]
    
    C --> C1["All transfers with dates"]
    C --> C2["Source → Target summary"]
    C --> C3["Filter by date range"]
    
    D --> D1["All adjustments with reasons"]
    D --> D2["Positive vs Negative"]
    D --> D3["Filter by adjustment type"]
    
    E --> E1["Every stock movement"]
    E --> E2["Transaction type filter<br/>IN, OUT, TRANSFER, ADJUST"]
    E --> E3["Audit trail for compliance"]
    
    F --> F1["Items below reorder level"]
    F --> F2["Items at safety stock"]
    F --> F3["Export alert list"]
```

### 7.2 Exporting Inventory Data

```mermaid
flowchart TD
    A["📦 On Inventory Page"] --> B["📥 Click 'Export' Button"]
    
    B --> C{"Select Export Format"}
    C -->|Excel| D["📊 .xlsx file"]
    C -->|CSV| E["📄 .csv file"]
    
    D --> F["⚙️ Generating Export"]
    E --> F
    
    F --> F1["📦 Current inventory data"]
    F --> F2["🔍 Respects active filters"]
    F --> F3["📊 All visible columns"]
    
    F --> G["⬇️ Download starts automatically"]
    G --> H["✅ File saved to downloads"]
    
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef format fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef process fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B start
    class C,D,E format
    class F,F1,F2,F3,G,H process
```

---

## 8. Data Models

### 8.1 Inventory Entity Relationships

```mermaid
flowchart TD
    subgraph "Product Domain"
    P["📦 Product"]
    PV["🎨 Product Variant"]
    end
    
    subgraph "Inventory Domain"
    IS["📦 Inventory Stock"]
    ST["🚚 Stock Transfer"]
    STD["📋 Stock Transfer Details"]
    IA["⚖️ Inventory Adjustment"]
    IAD["📋 Adjustment Details"]
    IT["📝 Inventory Transaction"]
    end
    
    subgraph "Location Domain"
    SL["🏭 Storage Location"]
    W["🏢 Warehouse"]
    end
    
    P -->|has| PV
    PV -->|stocked at| IS
    SL -->|contains| IS
    W -->|has| SL
    
    SL -->|source| ST
    ST -->|has| STD
    STD -->|transfers| IS
    
    SL -->|adjusted at| IA
    IA -->|has| IAD
    IAD -->|adjusts| IS
    
    IS -->|generates| IT
    ST -->|generates| IT
    IA -->|generates| IT
    
    classDef product fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef inventory fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef location fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class P,PV product
    class IS,ST,STD,IA,IAD,IT inventory
    class SL,W location
```

### 8.2 Key Fields Reference

#### Inventory Stock
| Field | Type | Description |
|-------|------|-------------|
| stock_id | Integer | Unique identifier |
| product_id | Integer | Reference to Product |
| variant_id | Integer | Reference to ProductVariant (optional) |
| location_id | Integer | Reference to StorageLocation |
| quantity | Decimal | Current stock quantity |
| uom_id | Integer | Unit of Measure |
| last_stock_take_date | DateTime | Last physical count |

#### Stock Transfer
| Field | Type | Description |
|-------|------|-------------|
| transfer_id | Integer | Unique identifier |
| transfer_code | String | Human-readable code |
| transfer_date | DateTime | When transfer occurred |
| source_location_id | Integer | Origin location |
| status | String | PENDING, COMPLETED, FAILED |
| notes | Text | Additional information |

#### Inventory Adjustment
| Field | Type | Description |
|-------|------|-------------|
| adjustment_id | Integer | Unique identifier |
| adjustment_code | String | Human-readable code |
| adjustment_date | DateTime | When adjustment made |
| location_id | Integer | Where adjustment applied |
| reason | String | Why adjustment was made |

### 8.3 Inventory Transaction Types

| Transaction Type | Description | When Created |
|------------------|-------------|------------|
| **STOCK_IN** | Stock received | Purchase receipts, production |
| **STOCK_OUT** | Stock shipped | Sales, consumption |
| **STOCK_TRANSFER_OUT** | Left source location | Stock transfers |
| **STOCK_TRANSFER_IN** | Arrived at destination | Stock transfers |
| **ADJUSTMENT** | Manual correction | Inventory adjustments |

---

## Common Questions

### Q: Can I transfer stock between different companies?
**A**: No, stock transfers are only allowed between locations within the same company.

### Q: What happens if I try to transfer more than available?
**A**: The system will show an error: "Insufficient stock" and display the available quantity.

### Q: Can I undo a stock transfer?
**A**: No, but you can create a reverse transfer going the opposite direction.

### Q: Why can't I adjust stock to negative?
**A**: The system prevents negative inventory. You can only deduct existing stock.

### Q: What's the difference between Transfer and Adjustment?
**A**: Transfer moves stock between locations (quantity stays same). Adjustment changes quantity at a location.

---

## API Endpoints Reference

### Inventory Stock
- `GET /warehouse/inventory-stock/` - List inventory stock
- `POST /warehouse/inventory-stock/` - Create stock record
- `PATCH /warehouse/inventory-stock/{id}` - Update stock
- `DELETE /warehouse/inventory-stock/{id}` - Delete stock

### Stock Transfer
- `GET /warehouse/stock-transfer/` - List transfers
- `POST /warehouse/stock-transfer/` - Create transfer
- `GET /warehouse/stock-transfer/{id}` - Get transfer details
- `POST /warehouse/inventory-stock/transfer` - Single item transfer

### Inventory Adjustment
- `GET /transaction/inventory-adjustment/` - List adjustments
- `POST /transaction/inventory-adjustment/` - Create adjustment
- `GET /transaction/inventory-adjustment/{id}` - Get adjustment details

---

*Document Version: 1.0 | Shoudagor ERP Inventory Module*
