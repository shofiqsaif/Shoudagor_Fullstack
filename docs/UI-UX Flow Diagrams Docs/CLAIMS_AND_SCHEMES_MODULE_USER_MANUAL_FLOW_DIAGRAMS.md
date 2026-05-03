# Claims and Schemes Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [Claims Module Entry Point](#1-claims-module-entry-point)
3. [Scheme Creation Workflow](#2-scheme-creation-workflow)
4. [Scheme Management Workflow](#3-scheme-management-workflow)
5. [Claim Application on Orders](#4-claim-application-on-orders)
6. [Claim Log Management](#5-claim-log-management)
7. [Re-evaluation and Reversal Workflow](#6-re-evaluation-and-reversal-workflow)
8. [Reports and Analytics](#7-reports-and-analytics)
9. [Data Models](#8-data-models)

---

## Overview

The Claims and Schemes Module manages promotional offers, discounts, and free quantity benefits in the Shoudagor ERP system. It enables businesses to create flexible incentive programs that automatically apply to Purchase Orders and Sales Orders.

### Key Entities
- **ClaimScheme**: Master promotion configuration (name, type, duration, trigger products)
- **ClaimSlab**: Tiered benefit thresholds within a scheme (Buy X Get Y, discount slabs)
- **ClaimLog**: Audit trail of scheme applications on orders

### Scheme Types
| Type | Description | Use Case |
|------|-------------|----------|
| **Buy X Get Y** | Free quantity based on purchase quantity | "Buy 10 Get 1 Free" |
| **Rebate Flat** | Fixed discount amount per threshold met | "Get $50 off per 100 units" |
| **Rebate Percentage** | Percentage discount on qualifying quantity | "Get 10% off per 50 units" |
| **Tiered Pricing** | Unit price reduction based on order value | "Spend $1000, pay $9/unit" |

### Applicability
- **Purchase Orders**: Schemes apply when buying from suppliers
- **Sales Orders**: Schemes apply when selling to customers

---

## 1. Claims Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Claims & Schemes'<br/>in main menu| C["🏷️ Claims Dashboard"]
    
    %% Dashboard Components
    C --> C1["📊 Dashboard Overview Cards"]
    C --> C2["📈 Scheme Summary Section"]
    C --> C3["💰 Claim Summary Section"]
    C --> C4["🏆 Top Performing Schemes"]
    C --> C5["📦 Top Claimed Products"]
    C --> C6["🕐 Recent Claim Logs"]
    C --> C7["📉 Monthly Trend Chart"]
    
    %% Scheme Summary Cards
    C2 --> C2a["Active Schemes<br/>Currently running"]
    C2 --> C2b["Expired Schemes<br/>Past end date"]
    C2 --> C2c["Expiring Soon<br/>Within 30 days"]
    C2 --> C2d["By Type<br/>Buy X Get Y / Rebate / Tiered"]
    C2 --> C2e["By Module<br/>Purchase vs Sale"]
    
    %% Claim Summary Cards
    C3 --> C3a["Total Claims Applied<br/>Count of applications"]
    C3 --> C3b["Total Free Quantity<br/>Units given free"]
    C3 --> C3c["Total Discount Amount<br/>Money saved"]
    C3 --> C3d["By Order Type<br/>PO vs SO claims"]
    C3 --> C3e["By Status<br/>Active / Reversed / Adjusted"]
    
    %% Quick Action Buttons
    C --> C8["⚡ Quick Action Buttons"]
    C8 --> C8a["➕ Create New Scheme"]
    C8 --> C8b["📋 View All Schemes"]
    C8 --> C8c["📜 View Claim Logs"]
    
    %% Navigation Sub-menu
    B -->|Click 'All Schemes'| D["📋 Schemes Listing Page"]
    B -->|Click 'Claim Logs'| E["📜 Claim Logs Page"]
    
    %% Schemes List Components
    D --> D1["🔍 Search & Filter Panel"]
    D --> D2["📊 Schemes Table"]
    D --> D3["➕ Add Scheme Button"]
    
    %% Search & Filters
    D1 --> D1a["🔎 Search by name"]
    D1 --> D1b["📂 Filter by Type"]
    D1 --> D1c["✓ Filter by Status"]
    D1 --> D1d["📅 Date Range Filter"]
    D1 --> D1e["📦 Filter by Product"]
    
    %% Table Columns
    D2 --> D2a["Scheme Name"]
    D2 --> D2b["Type<br/>Buy X Get Y / Rebate"]
    D2 --> D2c["Applicable To<br/>Purchase / Sale"]
    D2 --> D2d["Trigger Product<br/>What activates it"]
    D2 --> D2e["Date Range<br/>Start - End"]
    D2 --> D2f["Status<br/>Active/Inactive/Expired"]
    D2 --> D2g["Slabs Count<br/>Number of tiers"]
    
    %% Row Actions
    D --> D4["⋮ Actions Menu (per row)"]
    D4 --> D4a["✏️ Edit Scheme"]
    D4 --> D4b["🗑️ Delete Scheme"]
    D4 --> D4c["📊 View Details"]
    D4 --> D4d["📜 View Claim Logs"]
    
    %% Claim Logs Components
    E --> E1["🔍 Filter Panel"]
    E --> E2["📜 Claim Logs Table"]
    
    %% Log Filters
    E1 --> E1a["📅 Date Range"]
    E1 --> E1b["📦 Filter by Product"]
    E1 --> E1c["🏷️ Filter by Scheme"]
    E1 --> E1d["📋 Filter by Order Type<br/>PO / SO"]
    E1 --> E1e["🔢 Filter by Order ID"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef metric fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,B,C,D,E userAction
    class C1,D2,E2 page
    class C2,C3,C4,C5,C6,C7,D1,D3,D4,E1 component
    class C2a,C2b,C2c,C2d,C2e,C3a,C3b,C3c,C3d,C3e,D2a,D2b,D2c,D2d,D2e,D2f,D2g data
    class C8,C8a,C8b,C8c metric
```

### How to Navigate the Claims Module

1. **Getting There**: Click "Claims & Schemes" in the left sidebar menu after logging in
2. **Dashboard View**: See summary cards showing scheme and claim statistics at a glance
3. **Quick Actions**: Use buttons to create new schemes or view detailed lists
4. **Scheme Management**: Click "All Schemes" to manage existing schemes
5. **Audit Trail**: Click "Claim Logs" to review all scheme applications

### Dashboard Metrics Explained

| Metric | What It Shows | Why It Matters |
|--------|---------------|----------------|
| **Active Schemes** | Currently running promotions | See what's currently available |
| **Expired Schemes** | Past promotions | Review historical offers |
| **Expiring Soon** | Schemes ending within 30 days | Plan renewals or replacements |
| **Total Claims** | Number of times schemes applied | Usage frequency indicator |
| **Free Quantity** | Total free units given | Inventory impact |
| **Discount Amount** | Total money saved/given | Financial impact |
| **Top Schemes** | Best performing promotions | ROI analysis |
| **Top Products** | Most claimed items | Popular products |

---

## 2. Scheme Creation Workflow

### 2.1 Step-by-Step: Creating a New Scheme

**Overview**: This workflow guides you through creating a promotional scheme with tiered benefits that automatically apply to qualifying orders.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'Create New Scheme' button"] --> B["📄 Scheme Creation Form Opens"]
    
    %% Step 1: Basic Information
    B --> C["📋 STEP 1: Basic Information"]
    C --> C1["📝 Enter Scheme Name*<br/>Example: 'Summer Sale - Buy 10 Get 1'"]
    C --> C2["💡 Enter Description<br/>Optional details about the scheme"]
    
    %% Step 2: Scheme Configuration
    C --> D["⚙️ STEP 2: Scheme Configuration"]
    D --> D1["🏷️ Select Scheme Type*<br/>Dropdown with 4 options:"]
    
    %% Scheme Types
    D1 --> D1a["buy_x_get_y<br/>Free quantity"]
    D1 --> D1b["rebate_flat<br/>Fixed discount"]
    D1 --> D1c["rebate_percentage<br/>Percentage discount"]
    D1 --> D1d["tiered_pricing<br/>Volume-based pricing"]
    
    D --> D2["📅 Set Date Range*<br/>Start Date & End Date"]
    D --> D3{"🔍 Date Validation"}
    D3 -->|Invalid| D3a["❌ Error: End date must be after start date"]
    D3 -->|Invalid| D3b["❌ Error: End date cannot be in the past"]
    D3 -->|Valid| D4["✅ Dates accepted"]
    
    D --> D5["🎯 Select Applicable To*<br/>purchase or sale"]
    
    %% Step 3: Trigger Product
    D4 --> E["📦 STEP 3: Trigger Product Setup"]
    E --> E1["🔍 Search and Select Trigger Product*<br/>What customer must buy"]
    E --> E2["🎨 Select Trigger Variant<br/>Optional: Specific SKU"]
    E --> E3{"❓ Product Selected?"}
    E3 -->|No| E3a["❌ Error: Trigger product or variant is required"]
    E3 -->|Yes| F["✅ Trigger set"]
    
    %% Step 4: Free Product (for Buy X Get Y)
    F --> G{"🤔 Is this Buy X Get Y?"}
    G -->|Yes| G1["🎁 STEP 4: Free Product Setup"]
    G -->|No| H["⏭️ Skip to Step 5"]
    
    G1 --> G2["🔍 Select Free Product<br/>What customer gets free"]
    G1 --> G3["🎨 Select Free Variant<br/>Optional: Specific SKU"]
    G1 --> G4["💡 Note: Can be same or different from trigger"]
    
    %% Step 5: Slabs Configuration
    G --> H["📊 STEP 5: Configure Slabs (Tiers)"]
    H --> H0["💡 What are slabs?<br/>Different benefit levels based on quantity/amount"]
    
    H --> H1["➕ Click 'Add Slab' button"]
    H1 --> H2["🪟 Slab Configuration Modal Opens"]
    
    %% Slab Fields by Type
    H2 --> I{"📋 Configure Based on Scheme Type"}
    
    %% Buy X Get Y Slab
    I -->|buy_x_get_y| I1["Buy X Get Y Slab"]
    I1 --> I1a["📊 Threshold Qty*<br/>Minimum quantity to buy (X)"]
    I1 --> I1b["🎁 Free Qty*<br/>Quantity given free (Y)"]
    I1 --> I1c["Example: Buy 10 Get 1<br/>threshold=10, free=1"]
    
    %% Rebate Flat Slab
    I -->|rebate_flat| I2["Flat Rebate Slab"]
    I2 --> I2a["📊 Threshold Qty*<br/>Quantity to trigger rebate"]
    I2 --> I2b["💰 Discount Amount*<br/>Fixed amount off<br/>Example: $50"]
    I2 --> I2c["Example: Buy 100 Get $50 off<br/>threshold=100, discount=50"]
    
    %% Rebate Percentage Slab
    I -->|rebate_percentage| I3["Percentage Rebate Slab"]
    I3 --> I3a["📊 Threshold Qty*<br/>Quantity to trigger rebate"]
    I3 --> I3b["📈 Discount %*<br/>Percentage off<br/>Example: 10%"]
    I3 --> I3c["Example: Buy 50 Get 10% off<br/>threshold=50, percent=10"]
    
    %% Tiered Pricing Slab
    I -->|tiered_pricing| I4["Tiered Pricing Slab"]
    I4 --> I4a["💵 Threshold Amount*<br/>Min order value<br/>Example: $1000"]
    I4 --> I4b["💰 Tier Unit Price*<br/>Special price at this tier<br/>Example: $9.00"]
    I4 --> I4c["💡 Price must decrease<br/>at higher tiers"]
    I4 --> I4d["Example: Spend $1000,<br/>pay $9/unit instead of $10"]
    
    %% Save Slab
    I1 --> J["💾 Click 'Save Slab'"]
    I2 --> J
    I3 --> J
    I4 --> J
    
    J --> K["✅ Slab added to list<br/>Shown in slabs table"]
    
    %% Multiple Slabs
    K --> L{"🤔 Add more slabs?"}
    L -->|Yes, add tier| H1
    L -->|No, I'm done| M["➡️ Click 'Create Scheme' button"]
    
    %% Validation
    M --> N{"✓ Validation Checks"}
    N -->|No slabs| N1["❌ Error: At least one slab required"]
    N -->|Duplicate thresholds| N2["❌ Error: Threshold values must be unique"]
    N -->|Tiered pricing order wrong| N3["❌ Error: Tier prices must decrease at higher thresholds"]
    N -->|Overlapping scheme| N4["❌ Error: Overlapping scheme exists on same product"]
    N -->|All valid| O["✅ Ready to save"]
    
    %% Backend Process
    O --> P["🔄 Submitting to system..."]
    P --> P1["🌐 API Call: POST /claims/schemes"]
    P1 --> P2["💾 Creating Scheme Record"]
    P2 --> P3["💾 Creating Slab Records"]
    P3 --> P4["🔍 Checking for overlaps"]
    P4 --> Q["✅ All data saved successfully!"]
    Q --> R["🏠 Redirecting to Schemes List..."]
    R --> S["🎉 Success! 'Scheme created successfully'"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class C,D,E,G1,H step
    class C1,C2,D1a,D1b,D1c,D1d,D2,D5,E1,E2,G2,G3,H0,I1a,I1b,I1c,I2a,I2b,I2c,I3a,I3b,I3c,I4a,I4b,I4c,I4d input
    class D3,E3,G,L,N decision
    class D3a,D3b,E3a,N1,N2,N3,N4 error
    class D4,F,K,O,Q,R,S success
    class P,P1,P2,P3,P4 backend
```

### 💡 Tips for Scheme Creation

1. **Scheme Name**: Use descriptive names that indicate the benefit (e.g., "Q1 Promo - Buy 10 Get 1 Free")
2. **Date Planning**: Set start date in the future to prepare upcoming promotions
3. **Trigger Product**: Can be at product level (all variants) or specific variant
4. **Slab Design**: Create progressive tiers for better incentives (e.g., Buy 10 get 1, Buy 20 get 3)
5. **Overlap Check**: System prevents overlapping schemes on same product during same period

### 2.2 Scheme Type Selection Guide

```mermaid
flowchart TD
    A["🤔 What do you want to achieve?"] --> B{"Choose Scheme Type"}
    
    B -->|Give free items| C["buy_x_get_y<br/>Buy X Get Y Free"]
    B -->|Give fixed discount| D["rebate_flat<br/>Fixed Amount Off"]
    B -->|Give percentage discount| E["rebate_percentage<br/>Percentage Off"]
    B -->|Volume-based pricing| F["tiered_pricing<br/>Better Unit Price"]
    
    C --> C1["Example Scenarios:"]
    C1 --> C1a["Buy 10 Get 1 Free"]
    C1 --> C1b["Buy 50 Get 5 Free"]
    C1 --> C1c["✓ Good for: Inventory clearance,<br/>bulk purchase incentives"]
    
    D --> D1["Example Scenarios:"]
    D1 --> D1a["Buy 100 Get $50 off"]
    D1 --> D1b["Buy 500 Get $200 off"]
    D1 --> D1c["✓ Good for: B2B discounts,<br/>loyalty rewards"]
    
    E --> E1["Example Scenarios:"]
    E1 --> E1a["Buy 50 Get 10% off"]
    E1 --> E1b["Buy 200 Get 15% off"]
    E1 --> E1c["✓ Good for: Sales promotions,<br/>seasonal discounts"]
    
    F --> F1["Example Scenarios:"]
    F1 --> F1a["Spend $1000, pay $9/unit"]
    F1 --> F1b["Spend $5000, pay $8/unit"]
    F1 --> F1c["✓ Good for: Wholesale pricing,<br/>volume contracts"]
    
    %% Styling
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef typeBox fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef example fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,B decision
    class C,D,E,F typeBox
    class C1,D1,E1,F1,C1a,C1b,C1c,D1a,D1b,D1c,E1a,E1b,E1c,F1a,F1b,F1c example
```

### 2.3 Field Requirements & Validation

| Field | Required | Validation Rules | Scheme Types |
|-------|----------|------------------|--------------|
| Scheme Name | Yes | Min 1 char | All |
| Scheme Type | Yes | Must select one of 4 types | All |
| Start Date | Yes | Must be valid date | All |
| End Date | Yes | Must be after start date | All |
| Applicable To | Yes | "purchase" or "sale" | All |
| Trigger Product | Yes | Must exist in system | All |
| Trigger Variant | No | If set, must belong to trigger product | All |
| Free Product | No | Required for buy_x_get_y | buy_x_get_y |
| Free Variant | No | Optional even for buy_x_get_y | buy_x_get_y |
| Threshold Qty | Conditional | Required for non-tiered types | buy_x_get_y, rebate_* |
| Threshold Amount | Conditional | Required for tiered_pricing | tiered_pricing |
| Free Qty | Conditional | Required for buy_x_get_y | buy_x_get_y |
| Discount Amount | Conditional | Required for rebate_flat | rebate_flat |
| Discount % | Conditional | Required for rebate_percentage | rebate_percentage |
| Tier Unit Price | Conditional | Required for tiered_pricing | tiered_pricing |

---

## 3. Scheme Management Workflow

### 3.1 Editing a Scheme

```mermaid
flowchart TD
    %% Start
    A["👤 User wants to edit a scheme"] --> B["📋 Navigate to Schemes List"]
    
    %% Find Scheme
    B --> C["🔍 Locate the scheme to edit"]
    C --> C1["Use search box"]
    C --> C2["Use filters"]
    C --> C3["Browse the list"]
    
    %% Open Edit
    C --> D["⋮ Click 'Actions' menu on scheme row"]
    D --> E["✏️ Select 'Edit Scheme'"]
    
    %% Edit Form
    E --> F["🪟 Scheme Edit Form Opens"]
    F --> F1["⏳ Loading current data..."]
    F1 --> F2["📊 Fetching scheme details"]
    F2 --> F3["📊 Fetching slabs"]
    
    %% Editable Fields
    F --> G["📋 Editable Fields"]
    G --> G1["📝 Scheme Name<br/>Can change"]
    G --> G2["💡 Description<br/>Can change"]
    G --> G3["📅 Date Range<br/>Can extend/modify"]
    G --> G4["✓ Active Status<br/>Can toggle"]
    G --> G5["🎯 Applicable To<br/>Can change"]
    
    %% Non-Editable Fields
    G --> H["🔒 Locked Fields"]
    H --> H1["🏷️ Scheme Type<br/>Cannot change<br/>(data integrity)"]
    H --> H2["📦 Trigger Product<br/>Cannot change<br/>(use new scheme)"]
    
    %% Slab Management
    G --> I["📊 Slab Management"]
    I --> I1["➕ Add new slab"]
    I --> I2["✏️ Edit existing slab"]
    I --> I3["🗑️ Delete slab"]
    I --> I4["🔄 Replace all slabs"]
    
    %% Validation on Save
    I --> J["💾 Click 'Save Changes'"]
    J --> K{"🔍 Validation Check"}
    
    K -->|Invalid dates| K1["❌ Error: End date must be after start"]
    K -->|Past end date| K2["❌ Error: End date cannot be in past"]
    K -->|Overlap detected| K3["❌ Error: Overlapping scheme exists"]
    K -->|Invalid slabs| K4["❌ Error: Slab validation failed"]
    K -->|All valid| L["✅ Ready to update"]
    
    %% Update Process
    L --> M["🔄 Updating..."]
    M --> M1["🌐 API: PUT /claims/schemes/{id}"]
    M1 --> M2["💾 Updating scheme record"]
    M2 --> M3["💾 Updating/deleting slabs"]
    M3 --> M4["🔍 Re-checking overlaps"]
    M4 --> N["✅ Update successful!"]
    N --> O["🎉 Success message shown"]
    
    %% Error Recovery
    K1 --> P["✏️ Return to form<br/>Fix the error"]
    K2 --> P
    K3 --> P
    K4 --> P
    P --> J
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef locked fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C,D,E,J userAction
    class F,G,I,P form
    class H,H1,H2 locked
    class K decision
    class K1,K2,K3,K4 error
    class L,N,O success
    class M,M1,M2,M3,M4 backend
```

### 3.2 Deleting a Scheme

```mermaid
flowchart TD
    A["👤 User wants to delete a scheme"] --> B["📋 Navigate to Schemes List"]
    B --> C["🔍 Locate the scheme"]
    C --> D["⋮ Click 'Actions' menu"]
    D --> E["🗑️ Select 'Delete Scheme'"]
    
    E --> F["⚠️ Confirm Delete Dialog"]
    F --> F1["❓ System checks for claim logs"]
    
    F1 --> G{"📊 Has this scheme been used?"}
    G -->|Yes - Has logs| G1["⚠️ Warning shown:<br/>'This scheme has been applied to orders'"]
    G1 --> G2["📜 Shows: Number of applications"]
    G -->|No - No logs| G3["ℹ️ Info: 'No applications yet'"]
    
    G2 --> H["⌨️ Type scheme name to confirm"]
    G3 --> H
    H --> I["✅ Click 'Confirm Delete'"]
    
    I --> J["🔄 Processing deletion..."]
    J --> J1["🌐 API: DELETE /claims/schemes/{id}"]
    J1 --> J2["💾 Soft delete scheme<br/>(sets is_deleted=true)"]
    J2 --> J3["💾 Soft delete slabs<br/>(cascade)"]
    J3 --> K["✅ Deletion successful!"]
    K --> L["🎉 'Scheme deleted successfully'"]
    
    %% Note
    L --> M["📝 Note: Soft delete preserves<br/>historical claim logs"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef warning fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef note fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,B,C,D,E,H,I userAction
    class F,F1,G1,G2,G3 warning
    class G decision
    class J,J1,J2,J3 backend
    class K,L success
    class M note
```

### 3.3 Viewing Scheme Details

```mermaid
flowchart TD
    A["📋 Schemes List Page"] --> B["⋮ Click 'Actions' menu"]
    B --> C["📊 Select 'View Details'"]
    
    C --> D["🪟 Scheme Details Modal Opens"]
    D --> D1["📋 Basic Information Section"]
    D --> D2["📦 Product Information Section"]
    D --> D3["📊 Slabs Configuration Section"]
    D --> D4["📜 Recent Claim Logs Section"]
    
    D1 --> D1a["Scheme Name"]
    D1 --> D1b["Scheme Type<br/>With icon/color code"]
    D1 --> D1c["Description"]
    D1 --> D1d["Date Range<br/>With status indicator"]
    D1 --> D1e["Applicable To<br/>Purchase/Sale badge"]
    D1 --> D1f["Active Status"]
    
    D2 --> D2a["Trigger Product<br/>Name + Code"]
    D2 --> D2b["Trigger Variant<br/>SKU if specified"]
    D2 --> D2c["Free Product<br/>For Buy X Get Y"]
    D2 --> D2d["Free Variant<br/>If specified"]
    
    D3 --> D3a["Slabs Table"]
    D3a --> D3a1["Threshold Column"]
    D3a --> D3a2["Benefit Column<br/>(varies by type)"]
    
    D4 --> D4a["Last 5 claim applications"]
    D4 --> D4b["Link to full logs"]
    
    %% Styling
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef modal fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef section fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,B,C action
    class D modal
    class D1,D2,D3,D4,D1a,D1b,D1c,D1d,D1e,D1f,D2a,D2b,D2c,D2d,D3a,D3a1,D3a2,D4a,D4b section
```

---

## 4. Claim Application on Orders

### 4.1 How Claims Auto-Apply to Orders

**Overview**: When creating or editing Purchase Orders or Sales Orders, the system automatically evaluates and applies eligible schemes.

```mermaid
flowchart TD
    %% Order Creation Flow
    A["📝 User creates/edits an order"] --> B["📦 Adds order line items"]
    
    B --> C["➕ Add Item: Select product"]
    C --> C1["🔍 Search product catalog"]
    C1 --> C2["🎨 Select variant (if applicable)"]
    C2 --> C3["📊 Enter quantity"]
    C3 --> C4["💰 Enter unit price"]
    
    %% System Evaluation
    C4 --> D["🔄 System auto-evaluates schemes"]
    D --> D1["🌐 API Call:<br/>POST /claims/evaluate-pre-claim"]
    D1 --> D2["⚙️ Backend Processing"]
    
    %% Evaluation Steps
    D2 --> E["🔍 Step 1: Find Active Schemes"]
    E --> E1["Filter by company"]
    E --> E2["Filter by applicable_to<br/>(purchase vs sale)"]
    E --> E3["Filter by current date<br/>(within date range)"]
    E --> E4["Filter by is_active=true"]
    
    D2 --> F["🔗 Step 2: Match Products to Schemes"]
    F --> F1["Check variant-level triggers"]
    F --> F2["Check product-level triggers"]
    F --> F3["Build lookup maps for fast matching"]
    
    D2 --> G["🧮 Step 3: Calculate Benefits"]
    G --> G1["For each line item:"]
    G1 --> G2["Check quantity against thresholds"]
    G2 --> G3["Calculate multiplier<br/>(floor division)"]
    G3 --> G4{"📋 Scheme Type?"}
    
    %% Benefit Calculation by Type
    G4 -->|buy_x_get_y| H1["Calculate free quantity<br/>multiplier × free_qty"]
    G4 -->|rebate_flat| H2["Calculate discount<br/>multiplier × discount_amount"]
    G4 -->|rebate_percentage| H3["Calculate discount<br/>multiplier × threshold × price × %"]
    G4 -->|tiered_pricing| H4["Calculate discount<br/>(price - tier_price) × quantity"]
    
    %% Best Scheme Selection
    H1 --> I["🏆 Step 4: Select Best Scheme"]
    H2 --> I
    H3 --> I
    H4 --> I
    
    I --> I1["Compare total benefit value<br/>(free_qty × price + discount)"]
    I1 --> I2["Keep only the best scheme<br/>if multiple match"]
    I2 --> I3["Store applied_scheme_id"]
    
    %% Apply to UI
    I --> J["📱 Step 5: Update Order Form"]
    J --> J1["Populate free_quantity field"]
    J --> J2["Populate discount_amount field"]
    J --> J3["Show applied scheme name<br/>in tooltip"]
    J --> J4["Enable manual override<br/>if needed"]
    
    %% User Actions
    J --> K["👤 User can:"]
    K --> K1["✏️ Edit free quantity<br/>(manual override)"]
    K --> K2["✏️ Edit discount amount<br/>(manual override)"]
    K --> K3["🚫 Set applied_scheme_id=-1<br/>(skip schemes)"]
    K --> K4["✅ Accept auto-calculated values"]
    
    %% Save Order
    K --> L["💾 Save Order"]
    L --> L1["🌐 API: POST /purchase-orders or /sales-orders"]
    L1 --> L2["💾 Save order header"]
    L2 --> L3["💾 Save order details<br/>with scheme info"]
    L3 --> L4["📝 Log claim applications<br/>Create ClaimLog records"]
    L4 --> M["✅ Order saved with claims applied!"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef calculation fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    
    class A,B,C,C1,C2,C3,C4,K,K1,K2,K3,K4 userAction
    class D,D2,E,F,G,I,J,L2,L3,L4 system
    class D1,L,L1 api
    class E1,E2,E3,E4,F1,F2,F3,G1,G2,G3 process
    class G4,H1,H2,H3,H4,I1,I2,I3 calculation
    class M success
```

### 4.2 Claim Application Example: Buy X Get Y

```mermaid
flowchart TD
    A["Example: Buy 10 Get 1 Free Scheme"] --> B["Order Line Item"]
    
    B --> B1["Product: Widget-A"]
    B --> B2["Quantity: 25 units"]
    B --> B3["Unit Price: $10.00"]
    
    B --> C["🧮 Calculation"]
    C --> C1["Scheme: Buy 10 Get 1 Free"]
    C1 --> C2["Threshold: 10"]
    C2 --> C3["Free Qty: 1"]
    
    C --> D["Multiplier = floor(25 / 10) = 2"]
    D --> E["Free Quantity = 2 × 1 = 2"]
    E --> F["✅ Customer gets 2 units FREE"]
    
    %% Visual breakdown
    F --> G["📦 Total items: 25 purchased + 2 free = 27"]
    F --> H["💰 Customer pays for: 25 × $10 = $250"]
    F --> I["🎁 Free items value: 2 × $10 = $20"]
    
    %% Styling
    classDef example fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef calc fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef result fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,B1,B2,B3 example
    class C,C1,C2,C3,D,E calc
    class F,G,H,I result
```

### 4.3 Claim Application Example: Tiered Pricing

```mermaid
flowchart TD
    A["Example: Volume Discount Scheme"] --> B["Order Line Item"]
    
    B --> B1["Product: Widget-A"]
    B --> B2["Quantity: 150 units"]
    B --> B3["Standard Price: $10.00/unit"]
    
    B --> C["📊 Scheme: Tiered Pricing"]
    C --> C1["Tier 1: Spend $500 → Pay $9.50/unit"]
    C --> C2["Tier 2: Spend $1000 → Pay $9.00/unit"]
    C --> C3["Tier 3: Spend $2000 → Pay $8.50/unit"]
    
    C --> D["🧮 Evaluation"]
    D --> D1["Order Value = 150 × $10 = $1500"]
    D1 --> D2["Check tiers (highest first):"]
    D2 --> D3["Tier 3: $1500 < $2000? ❌ No"]
    D3 --> D4["Tier 2: $1500 >= $1000? ✅ Yes"]
    
    D4 --> E["✅ Tier 2 applies!"]
    E --> E1["New unit price: $9.00"]
    E1 --> E2["Discount per unit: $10 - $9 = $1"]
    E2 --> E3["Total discount: 150 × $1 = $150"]
    
    F["📦 Summary"]
    E3 --> F
    F --> F1["Quantity: 150 units"]
    F --> F2["Applied price: $9.00/unit"]
    F --> F3["Total after discount: 150 × $9 = $1350"]
    F --> F4["Savings: $150"]
    
    %% Styling
    classDef example fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef tiers fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef calc fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef result fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,B1,B2,B3 example
    class C,C1,C2,C3 tiers
    class D,D1,D2,D3,D4,E,E1,E2,E3 calc
    class F,F1,F2,F3,F4 result
```

---

## 5. Claim Log Management

### 5.1 Viewing Claim Logs

```mermaid
flowchart TD
    A["📜 Navigate to Claim Logs Page"] --> B["📊 Claim Logs Table Loads"]
    
    B --> C["🔍 Filter Panel"]
    C --> C1["📅 Date Range Filter"]
    C --> C2["🏷️ Scheme Filter<br/>Dropdown of all schemes"]
    C --> C3["📦 Product Filter<br/>Search by product name"]
    C --> C4["📋 Order Type Filter<br/>Purchase / Sale"]
    C --> C5["🔢 Order ID Filter<br/>Specific PO/SO number"]
    
    B --> D["📜 Claim Logs Table"]
    D --> D1["Table Columns:"]
    D1 --> D2["Log ID"]
    D1 --> D3["Scheme Name<br/>With type badge"]
    D1 --> D4["Product<br/>Name + Variant"]
    D1 --> D5["Order Reference<br/>PO-1234 or SO-5678"]
    D1 --> D6["Applied Qty"]
    D1 --> D7["Free Qty Given"]
    D1 --> D8["Discount Amount<br/>Money value"]
    D1 --> D9["Status<br/>Active/Reversed/Adjusted"]
    D1 --> D10["Date Applied"]
    
    D --> E["⋮ Row Actions"]
    E --> E1["👁️ View Details"]
    
    %% Pagination
    B --> F["📄 Pagination Controls"]
    F --> F1["Show 10/25/50/100 per page"]
    F --> F2["Previous/Next buttons"]
    F --> F3["Page number selector"]
    
    %% Styling
    classDef page fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef filter fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef table fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,D,F page
    class C,C1,C2,C3,C4,C5,E,E1 filter
    class D1,D2,D3,D4,D5,D6,D7,D8,D9,D10,F1,F2,F3 table
```

### 5.2 Understanding Claim Log Status

```mermaid
flowchart TD
    A["📜 Claim Log Status Values"] --> B{"What does each status mean?"}
    
    B -->|active| C["🟢 ACTIVE"]
    B -->|reversed| D["🔴 REVERSED"]
    B -->|adjusted| E["🟡 ADJUSTED"]
    
    C --> C1["Normal applied claim<br/>Scheme benefits given"]
    C --> C2["Appears in:<br/>Reports, totals, analytics"]
    C --> C3["Can be reversed<br/>if order cancelled"]
    
    D --> D1["Original claim was reversed<br/>Order was cancelled"]
    D --> D2["Negative entry created<br/>to offset original"]
    D --> D3["Not counted in:<br/>Report totals"]
    D --> D4["Shows reversal reason<br/>and linked to original log"]
    
    E --> E1["Claim was partially adjusted<br/>Items were returned"]
    E --> E2["Adjustment entry created<br/>Reduces original benefit"]
    E --> E3["Proportional reduction<br/>Based on returned qty"]
    E --> E4["Original + Adjustment =<br/>Net benefit amount"]
    
    %% Styling
    classDef statusActive fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef statusReversed fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef statusAdjusted fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    
    class C,C1,C2,C3 statusActive
    class D,D1,D2,D3,D4 statusReversed
    class E,E1,E2,E3,E4 statusAdjusted
```

---

## 6. Re-evaluation and Reversal Workflow

### 6.1 When to Re-evaluate Schemes

```mermaid
flowchart TD
    A["🔄 Re-evaluation Scenarios"] --> B{"When should you re-evaluate?"}
    
    B -->|Order Modified| C["✏️ Order Quantity Changed"]
    B -->|Scheme Changed| D["🏷️ Scheme Updated/Created"]
    B -->|Error Found| E["🐛 Wrong Scheme Applied"]
    
    C --> C1["User increased/decreased<br/>line item quantity"]
    C1 --> C2["May qualify for:<br/>Different tier"]
    C2 --> C3["May lose or gain:<br/>Free items or discounts"]
    
    D --> D1["New scheme activated<br/>that matches order"]
    D1 --> D2["Existing scheme dates<br/>or thresholds changed"]
    D2 --> D3["Better benefits may<br/>now be available"]
    
    E --> E1["Wrong scheme was<br/>auto-selected"]
    E1 --> E2["User wants to apply<br/>different scheme"]
    E2 --> E3["Manual correction<br/>needed"]
    
    %% Process
    C3 --> F["🔄 Re-evaluation Process"]
    D3 --> F
    E3 --> F
    
    F --> F1["🌐 API: POST /claims/orders/re-evaluate"]
    F1 --> F2{"✓ Order status valid?<br/>Pending/Approved/Draft only"}
    F2 -->|Invalid| F2a["❌ Error: Cannot re-evaluate<br/>processed orders"]
    F2 -->|Valid| F3["✅ Proceed with re-evaluation"]
    
    F3 --> G["⚙️ Processing Steps"]
    G --> G1["1. Reverse existing claim logs<br/>(mark as reversed)"]
    G --> G2["2. Re-evaluate all line items<br/>with current active schemes"]
    G --> G3["3. Apply new best schemes<br/>to each line item"]
    G --> G4["4. Create new claim logs<br/>for new applications"]
    G --> H["✅ Re-evaluation complete!"]
    
    %% Styling
    classDef scenario fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class C,D,E,C1,C2,C3,D1,D2,D3,E1,E2,E3 scenario
    class F,F1,F3,G,G1,G2,G3,G4 process
    class F2 decision
    class F2a error
    class F3,H success
```

### 6.2 Reversing Claims for Cancelled Orders

```mermaid
flowchart TD
    A["🗑️ Order Cancellation Trigger"] --> B["Order status changed to<br/>CANCELLED"]
    
    B --> C["🔄 Automatic Claim Reversal"]
    C --> C1["System detects cancellation"]
    C1 --> C2["Finds all claim logs<br/>for this order"]
    C2 --> C3["Marks original logs as<br/>'reversed'"]
    
    C --> D["📝 Creates Reversal Entries"]
    D --> D1["For each active claim log:"]
    D1 --> D2["Create reversal log with<br/>negative values"]
    D2 --> D3["given_free_qty = -original"]
    D3 --> D4["given_discount = -original"]
    D4 --> D5["status = 'active'<br/>(reversal is the new record)"]
    
    D --> E["🔗 Links Reversal to Original"]
    E --> E1["reversed_by_log_id set<br/>to reversal log"]
    E --> E2["Preserves audit trail<br/>of what happened"]
    
    %% Example
    F["📊 Example: Reversal Calculation"]
    E2 --> F
    F --> F1["Original Claim:"]
    F1 --> F2["Free Qty: 5 units"]
    F1 --> F3["Discount: $50.00"]
    
    F --> F4["Reversal Entry:"]
    F4 --> F5["Free Qty: -5 units"]
    F4 --> F6["Discount: -$50.00"]
    F4 --> F7["Reason: 'Order cancelled'"]
    
    F --> G["✅ Net Effect: Zero<br/>As if claim never happened"]
    
    %% Styling
    classDef trigger fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef link fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef example fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef result fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B trigger
    class C,C1,C2,C3,D,D1,D2,D3,D4,D5 process
    class E,E1,E2 link
    class F,F1,F2,F3,F4,F5,F6,F7 example
    class G result
```

### 6.3 Adjusting Claims for Partial Returns

```mermaid
flowchart TD
    A["📦 Partial Return Scenario"] --> B["Customer returns some items"]
    
    B --> C["Example Situation:"]
    C --> C1["Original Order:<br/>100 units of Widget-A"]
    C1 --> C2["Original Claim:<br/>Buy 10 Get 1 → 10 free units"]
    C2 --> C3["Customer Returns:<br/>30 units"]
    
    C3 --> D["🧮 Adjustment Calculation"]
    D --> D1["Return Ratio = 30/100 = 30%"]
    D1 --> D2["Adjust Free Qty = 10 × 30% = 3 units"]
    D2 --> D3["Adjustment Entry:<br/>Free Qty = -3"]
    
    D --> E["📝 Adjustment Process"]
    E --> E1["🌐 API: POST /claims/logs/adjust"]
    E1 --> E2["Create adjustment log<br/>with reduced quantities"]
    E2 --> E3["Link to original<br/>claim log"]
    E3 --> E4["Preserves original +<br/>shows adjustment"]
    
    %% Result
    E4 --> F["📊 Final State"]
    F --> F1["Original: 10 free units"]
    F --> F2["Adjustment: -3 free units"]
    F --> F3["Net Free: 7 units<br/>(for remaining 70 units kept)"]
    
    %% Styling
    classDef scenario fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef calc fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef result fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,C1,C2,C3 scenario
    class D,D1,D2,D3 calc
    class E,E1,E2,E3,E4 process
    class F,F1,F2,F3 result
```

---

## 7. Reports and Analytics

### 7.1 Available Reports

```mermaid
flowchart TD
    A["📊 Claims & Schemes Reports"] --> B{"What reports are available?"}
    
    B -->|Summary Report| C["📈 Claim Summary Report"]
    B -->|Scheme Report| D["🏷️ Claims by Scheme"]
    B -->|Product Report| E["📦 Claims by Product"]
    B -->|Variant Report| F["🎨 Variant-Level Reports"]
    
    C --> C1["Shows overall metrics:"]
    C1 --> C2["Total claims applied"]
    C1 --> C3["Total free quantity given"]
    C1 --> C4["Total discount amount"]
    C1 --> C5["Breakdown by order type<br/>(PO vs SO)"]
    C1 --> C6["Breakdown by status<br/>(Active/Reversed/Adjusted)"]
    
    D --> D1["Groups claims by scheme:"]
    D1 --> D2["Scheme name and type"]
    D1 --> D3["Number of times applied"]
    D1 --> D4["Total benefits given"]
    D1 --> D5["Helps identify:<br/>Best performing schemes"]
    
    E --> E1["Groups claims by product:"]
    E1 --> E2["Product name and code"]
    E1 --> E3["Total claims count"]
    E1 --> E4["Total free quantity"]
    E1 --> E5["Total discount amount"]
    E1 --> E6["Helps identify:<br/>Most popular products"]
    
    F --> F1["Detailed variant reports:"]
    F1 --> F2["📋 Free Qty by Variant"]
    F1 --> F3["💰 Discount by Variant"]
    
    F2 --> F2a["Per variant breakdown:"]
    F2a --> F2b["SKU"]
    F2b --> F2c["Total free qty received"]
    F2c --> F2d["Number of applications"]
    F2d --> F2e["Schemes involved"]
    
    F3 --> F3a["Per variant breakdown:"]
    F3a --> F3b["SKU"]
    F3b --> F3c["Total discount received"]
    F3c --> F3d["Number of applications"]
    F3d --> F3e["Schemes involved"]
    
    %% Export options
    C --> G["📤 Export Options"]
    D --> G
    E --> G
    F --> G
    G --> G1["Export as Excel<br/>For analysis"]
    G --> G2["Export as PDF<br/>For sharing"]
    
    %% Styling
    classDef report fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef metrics fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef variant fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef export fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class C,D,E,F report
    class C1,C2,C3,C4,C5,C6,D1,D2,D3,D4,D5,E1,E2,E3,E4,E5,E6 metrics
    class F1,F2,F3,F2a,F2b,F2c,F2d,F2e,F3a,F3b,F3c,F3d,F3e variant
    class G,G1,G2 export
```

### 7.2 Generating a Report

```mermaid
flowchart TD
    A["👤 User wants a report"] --> B["📊 Navigate to Reports Section"]
    
    B --> C["🎯 Select Report Type"]
    C --> C1["Claim Summary"]
    C --> C2["Claims by Scheme"]
    C --> C3["Claims by Product"]
    C --> C4["Free Qty by Variant"]
    C --> C5["Discount by Variant"]
    
    %% Filter Configuration
    C --> D["⚙️ Configure Filters"]
    D --> D1["📅 Date Range<br/>Start and end date"]
    D --> D2["📋 Order Type<br/>Purchase / Sale / Both"]
    D --> D3["🏷️ Scheme Filter<br/>Specific scheme or all"]
    D --> D4["📦 Product Filter<br/>Specific product or all"]
    D --> D5["🎨 Variant Filter<br/>Specific variant or all"]
    
    %% Generate
    D --> E["🚀 Click 'Generate Report'"]
    E --> F["⏳ Loading..."]
    F --> G["📊 Report Generated"]
    
    %% Display
    G --> H["📈 Report Display"]
    H --> H1["Summary cards at top"]
    H --> H2["Data table below"]
    H --> H3["Charts (if applicable)"]
    
    %% Actions
    G --> I["📤 Export Actions"]
    I --> I1["📥 Download Excel"]
    I --> I2["📄 Download PDF"]
    I --> I3["🖨️ Print Report"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef config fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef loading fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef result fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,C1,C2,C3,C4,C5 userAction
    class D,D1,D2,D3,D4,D5,E config
    class F loading
    class G,H,H1,H2,H3,I,I1,I2,I3 result
```

---

## 8. Data Models

### 8.1 Entity Relationship Diagram

```mermaid
erDiagram
    CLAIM_SCHEME ||--o{ CLAIM_SLAB : contains
    CLAIM_SCHEME ||--o{ CLAIM_LOG : generates
    CLAIM_SCHEME ||--o{ PRODUCT : triggers
    CLAIM_SCHEME ||--o{ PRODUCT_VARIANT : triggers
    CLAIM_SCHEME ||--o{ PRODUCT : gives_free
    CLAIM_SCHEME ||--o{ PRODUCT_VARIANT : gives_free
    CLAIM_LOG ||--o{ PRODUCT : applies_to
    CLAIM_LOG ||--o{ PRODUCT_VARIANT : applies_to
    
    CLAIM_SCHEME {
        int scheme_id PK
        string scheme_name
        string description
        string scheme_type "buy_x_get_y|rebate_flat|rebate_percentage|tiered_pricing"
        timestamp start_date
        timestamp end_date
        string applicable_to "purchase|sale"
        int trigger_product_id FK
        int trigger_variant_id FK
        int free_product_id FK
        int free_variant_id FK
        boolean is_active
        int company_id FK
    }
    
    CLAIM_SLAB {
        int slab_id PK
        int scheme_id FK
        decimal threshold_qty
        decimal threshold_amount
        decimal free_qty
        decimal discount_amount
        decimal discount_percentage
        decimal tier_unit_price
    }
    
    CLAIM_LOG {
        int log_id PK
        int scheme_id FK
        int ref_id "Order ID"
        string ref_type "purchase_order|sales_order"
        int order_detail_id
        int product_id FK
        int variant_id FK
        decimal applied_on_qty
        decimal given_free_qty
        decimal given_discount_amount
        int free_product_id FK
        int free_variant_id FK
        string status "active|reversed|adjusted"
        int reversed_by_log_id FK
        string reversal_reason
        int company_id FK
    }
    
    PRODUCT {
        int product_id PK
        string product_name
        string product_code
    }
    
    PRODUCT_VARIANT {
        int variant_id PK
        int product_id FK
        string sku
        string attribute_value
    }
```

### 8.2 Model Field Descriptions

#### ClaimScheme
| Field | Type | Description |
|-------|------|-------------|
| scheme_id | Integer | Primary key, auto-generated |
| scheme_name | String(200) | Human-readable name for the promotion |
| description | String(500) | Optional detailed description |
| scheme_type | String(50) | Type: buy_x_get_y, rebate_flat, rebate_percentage, tiered_pricing |
| start_date | Timestamp | When the scheme becomes active |
| end_date | Timestamp | When the scheme expires |
| applicable_to | String(50) | Applies to: purchase (PO) or sale (SO) |
| trigger_product_id | Integer | FK to Product - what triggers the scheme |
| trigger_variant_id | Integer | FK to Variant - specific SKU trigger (optional) |
| free_product_id | Integer | FK to Product - what to give free (Buy X Get Y only) |
| free_variant_id | Integer | FK to Variant - specific free SKU (optional) |
| is_active | Boolean | Whether scheme is currently active |
| company_id | Integer | FK to company (multi-tenant) |

#### ClaimSlab
| Field | Type | Description |
|-------|------|-------------|
| slab_id | Integer | Primary key, auto-generated |
| scheme_id | Integer | FK to parent ClaimScheme |
| threshold_qty | Decimal | Quantity to trigger this slab (non-tiered) |
| threshold_amount | Decimal | Order value to trigger (tiered_pricing only) |
| free_qty | Decimal | Free quantity to give (Buy X Get Y) |
| discount_amount | Decimal | Fixed discount amount (rebate_flat) |
| discount_percentage | Decimal | Discount percentage (rebate_percentage) |
| tier_unit_price | Decimal | Special unit price (tiered_pricing) |

#### ClaimLog
| Field | Type | Description |
|-------|------|-------------|
| log_id | Integer | Primary key, auto-generated |
| scheme_id | Integer | FK to applied ClaimScheme |
| ref_id | Integer | Order ID (PO or SO) |
| ref_type | String(50) | 'purchase_order' or 'sales_order' |
| order_detail_id | Integer | Specific line item ID |
| product_id | Integer | FK to Product that was ordered |
| variant_id | Integer | FK to Variant that was ordered |
| applied_on_qty | Decimal | Quantity the scheme applied to |
| given_free_qty | Decimal | Free quantity given (can be negative for reversals) |
| given_discount_amount | Decimal | Discount amount (can be negative for reversals) |
| free_product_id | Integer | FK to free product (Buy X Get Y) |
| free_variant_id | Integer | FK to free variant (Buy X Get Y) |
| status | String(20) | 'active', 'reversed', or 'adjusted' |
| reversed_by_log_id | Integer | Self-referential FK for reversals |
| reversal_reason | String(500) | Why claim was reversed/adjusted |
| company_id | Integer | FK to company (multi-tenant) |

---

## Appendix: Common Scenarios

### Scenario 1: Creating a Simple Buy 10 Get 1 Free

```mermaid
flowchart LR
    A["Create Scheme"] --> B["Name: 'Summer Promo'"]
    B --> C["Type: buy_x_get_y"]
    C --> D["Applicable: sale"]
    D --> E["Trigger: Product-X"]
    E --> F["Free: Same Product-X"]
    F --> G["Add Slab:"]
    G --> H["Threshold: 10"]
    H --> I["Free: 1"]
    I --> J["Save Scheme"]
```

### Scenario 2: Creating Tiered Volume Discounts

```mermaid
flowchart LR
    A["Create Scheme"] --> B["Name: 'Volume Discount'"]
    B --> C["Type: tiered_pricing"]
    C --> D["Applicable: purchase"]
    D --> E["Trigger: Product-Y"]
    E --> F["Slab 1: $500 → $9.50"]
    F --> G["Slab 2: $1000 → $9.00"]
    G --> H["Slab 3: $2000 → $8.50"]
    H --> I["Save Scheme"]
```

### Scenario 3: Finding Claim Impact on Sales

```mermaid
flowchart LR
    A["Go to Reports"] --> B["Select 'Claim Summary'"]
    B --> C["Set Date Range"]
    C --> D["Filter: Sales Orders"]
    D --> E["Generate Report"]
    E --> F["View Total Discounts"]
    F --> G["View Free Qty Given"]
```

---

**Document Version**: 1.0  
**Module**: Claims and Schemes  
**Last Updated**: May 2026  
**Compatible with**: Shoudagor ERP v2.0+
