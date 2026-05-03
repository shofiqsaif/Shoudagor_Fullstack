# Expense Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [Expense Module Entry Point](#1-expense-module-entry-point)
3. [Expense Creation Workflow](#2-expense-creation-workflow)
4. [Expense Listing & Search](#3-expense-listing--search)
5. [Expense Edit/Update Workflow](#4-expense-editupdate-workflow)
6. [Expense Deletion Workflow](#5-expense-deletion-workflow)
7. [Expense Category Management](#6-expense-category-management)
8. [Expense Reports & Analytics](#7-expense-reports--analytics)
9. [Data Models](#8-data-models)

---

## Overview

The Expense Module is a comprehensive expense tracking and management system within Shoudagor ERP. It enables businesses to record, categorize, analyze, and report on all business expenditures with multi-category support and detailed analytics.

### Key Entities
- **Expense**: Core expense record (title, amount, date, payment method, description)
- **Expense Category**: Classification system for organizing expenses (supports multi-category tagging)
- **Payment Method**: How the expense was paid (cash, card, bank)
- **Expense Statistics**: Aggregated data for dashboard insights
- **Expense Reports**: Detailed analytics including trends, patterns, and breakdowns

---

## 1. Expense Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Expenses'<br/>in main menu| C["💰 Expenses Listing Page"]
    B -->|Click 'Expense Categories'<br/>in main menu| D["📁 Expense Categories Page"]
    B -->|Click 'Reports → Expenses'<br/>in main menu| E["📊 Expense Reports Page"]
    
    %% Expenses Page Components
    C --> C1["📊 Expenses Table"]
    C --> C2["🔍 Filter Panel"]
    C --> C3["📈 Statistics Cards"]
    C --> C4["⚡ Quick Action Buttons"]
    
    %% Table Columns
    C1 --> C1a["Title<br/>Expense Description"]
    C1 --> C1b["Categories<br/>Multiple category tags"]
    C1 --> C1c["Amount<br/>Expense value in BDT"]
    C1 --> C1d["Payment Method<br/>Cash/Card/Bank"]
    C1 --> C1e["Expense Date<br/>When incurred"]
    
    %% Statistics Cards
    C3 --> C3a["Total Expenses<br/>Count of all expenses"]
    C3 --> C3b["Total Amount<br/>Sum of all expenses"]
    C3 --> C3c["Average Amount<br/>Mean expense value"]
    C3 --> C3d["Top Category<br/>Highest spend category"]
    
    %% Filters
    C2 --> C2a["📂 Categories<br/>Multi-select filter"]
    C2 --> C2b["💳 Payment Method<br/>Cash/Card/Bank"]
    C2 --> C2c["📅 Date Range<br/>From/To picker"]
    C2 --> C2d["💰 Amount Range<br/>Min/Max slider"]
    
    %% Action Buttons
    C4 --> C4a["➕ Add Expense"]
    
    %% Row Actions
    C --> C5["⋮ Actions Menu (per row)"]
    C5 --> C5a["✏️ Edit Expense"]
    C5 --> C5b["🗑️ Delete Expense"]
    
    %% Expense Categories Page
    D --> D1["📁 Categories Table"]
    D --> D2["➕ Add Category Button"]
    D --> D3["🔍 Search Categories"]
    
    %% Reports Page
    E --> E1["📊 Category Breakdown Chart"]
    E --> E2["📈 Monthly Trend Chart"]
    E --> E3["📅 Daily Pattern Chart"]
    E --> E4["📊 Weekly Trend Chart"]
    E --> E5["🏆 Top Expenses Table"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E userAction
    class C1,D1,E1 page
    class C2,C3,C4,C5,D2,D3 component
    class C1a,C1b,C1c,C1d,C1e,C2a,C2b,C2c,C2d,C3a,C3b,C3c,C3d,C4a,C5a,C5b data
```

### How to Navigate the Expenses Page

1. **Getting There**: Click "Expenses" in the left sidebar menu after logging in
2. **What You See**: A dashboard with statistics cards at the top, followed by a filter panel and expenses table
3. **Quick Actions**: Use the "Add Expense" button to create new expenses
4. **Row Actions**: Click the "⋮" (three dots) on any row to edit or delete that expense

### UI Elements - Expenses List Page

| Component | Type | Description |
|-----------|------|-------------|
| Statistics Cards | Info Cards | Total Expenses, Total Amount, Average Amount, Top Category |
| Categories Filter | Multi-Select | Select multiple expense categories to filter |
| Payment Method Filter | Dropdown | Filter by cash, card, or bank |
| Date Range | Date Picker | Select from/to dates for filtering |
| Amount Range | Slider | Min/Max amount range filter |
| Add Expense | Button | Navigate to expense creation page |
| Expenses Table | Data Table | Paginated list with sorting |
| Actions Menu | Dropdown | Edit, Delete options per expense |

---

## 2. Expense Creation Workflow

### 2.1 Step-by-Step: Creating a New Expense

**Overview**: This workflow guides you through recording a new business expense with multi-category support.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'Add Expense' button"] --> B["📄 Expense Creation Form Opens"]
    
    %% Form Sections
    B --> C["📋 Expense Information Form"]
    
    %% Required Fields
    C --> C1["📝 Enter Expense Title*<br/>Example: 'Office Supplies'"]
    C --> C2["💵 Enter Amount*<br/>Example: 5000.00 BDT"]
    C --> C3["📅 Select Expense Date*<br/>Default: Today"]
    
    %% Category Selection
    C --> D["🏷️ Select Categories*"]
    D --> D1["Open Multi-Select Dropdown"]
    D1 --> D2{"Need new category?"}
    D2 -->|Yes| D3["Click ➕ button<br/>Add Category Dialog"]
    D2 -->|No| D4["Select existing categories"]
    D3 --> D3a["Enter Category Name*"]
    D3 --> D3b["Enter Description"]
    D3 --> D3c["Click 'Create Category'"]
    D3c --> D4
    
    %% Payment Method
    C --> E["💳 Select Payment Method*"]
    E --> E1["Cash<br/>Physical money"]
    E --> E2["Card<br/>Credit/Debit card"]
    E --> E3["Bank<br/>Bank transfer/Check"]
    
    %% Optional Fields
    C --> F["📝 Optional: Description<br/>Additional details about expense"]
    
    %% Validation
    C --> G["💾 Click 'Create Expense' button"]
    G --> H{"🔍 Validation Check"}
    H -->|Invalid| H1["❌ Show field errors<br/>Red highlights on invalid fields"]
    H1 --> C
    H -->|Valid| I["✅ Ready to submit"]
    
    %% API Call
    I --> J["🌐 API Call: POST /billing/expense/"]
    J --> K["💾 Creating Expense Record"]
    K --> L["🔗 Creating Category Mappings"]
    L --> M["✅ Expense saved successfully!"]
    M --> N["🏠 Redirecting to Expenses List..."]
    N --> O["🎉 Success! 'Expense created successfully'"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class C,D,E,F step
    class C1,C2,C3,D1,D3a,D3b,E1,E2,E3,F input
    class D2,H decision
    class H1 error
    class D3c,M,N,O success
    class G,I,J,K,L backend
```

### 2.2 Field Requirements & Validation

| Field | Required | Validation Rules |
|-------|----------|------------------|
| Title | Yes | Min 1 character, max 255 |
| Amount | Yes | Number > 0, max 18 digits with 2 decimals |
| Expense Date | Yes | Valid date, not future date |
| Categories | Yes | At least one category must be selected |
| Payment Method | Yes | Must be 'cash', 'card', or 'bank' |
| Description | No | Max 500 characters |

### 2.3 Multi-Category Selection Flow

```mermaid
flowchart LR
    A[Open Category Dropdown] --> B[Check Available Categories]
    B --> C{Categories Exist?}
    C -->|Yes| D[Display Category List]
    C -->|No| E[Show 'Add Category' Prompt]
    E --> F[Open Category Form]
    F --> G[Create Category]
    G --> D
    D --> H[Select Multiple Categories]
    H --> I[Click to Toggle Selection]
    I --> J[Selected Categories Show as Tags]
    J --> K[Click X to Remove Tag]
    H --> L[Click Outside to Close]
```

### 💡 Tips for Expense Creation

1. **Be Descriptive**: Use clear titles like "Q1 Office Stationery" instead of just "Supplies"
2. **Multi-Category**: Tag expenses with multiple categories for better reporting (e.g., "Travel" + "Marketing")
3. **Payment Method**: Choose accurately for cash flow tracking
4. **Date Accuracy**: Record the actual expense date, not the entry date

---

## 3. Expense Listing & Search

### 3.1 How the Expenses Page Loads

**What happens when you open the Expenses page:**

```mermaid
flowchart TD
    %% Page Load
    A["🏠 User clicks 'Expenses' menu"] --> B["🔐 System identifies your company"]
    
    %% Loading Data
    B --> C["📦 Loading helper data..."]
    C --> C1["🏷️ Loading categories list<br/>For category filter dropdown"]
    C --> C2["💳 Loading payment methods<br/>For payment method filter"]
    
    %% Loading Expenses
    C --> D["🔍 Loading your expenses..."]
    D --> D1["📡 API: GET /billing/expense/"]
    D1 --> D2["⚙️ Applying default filters"]
    D2 --> D3["📄 Expenses returned with pagination"]
    
    %% Statistics
    D --> E["📊 Loading statistics..."]
    E --> E1["📡 API: GET /billing/expense/statistics/summary"]
    E1 --> E2["📈 Stats calculated<br/>Total count, amount, averages"]
    
    %% Display
    D3 --> F["🖥️ Displaying Expenses Table"]
    E2 --> F
    F --> F1["📊 Showing all columns<br/>Title, Categories, Amount, Payment, Date"]
    F --> F2["⋮ Actions menu on each row<br/>Edit, Delete"]
    
    %% User Interactions
    F --> G["👤 Now you can interact:"]
    G --> G1["🔎 Apply filters<br/>Category, Payment, Date, Amount"]
    G --> G2["📄 Change page<br/>Click pagination numbers"]
    G --> G3["🔃 Sort columns<br/>Click column headers"]
    
    %% System Response
    G1 --> H["🔄 Table refreshes<br/>With filtered results"]
    G2 --> I["📄 New page loads<br/>More expenses shown"]
    G3 --> J["🔃 Re-sorts data<br/>Ascending/descending toggle"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A,G,G1,G2,G3 userAction
    class B,C,D,E,F system
    class C1,C2,D3,E2,F1,F2 data
    class D1,E1 api
```

### 📱 Quick Guide: Finding Expenses

| What you want to do | How to do it |
|---------------------|--------------|
| **Filter by category** | Use the "Categories" multi-select dropdown |
| **Filter by payment method** | Use the "Payment Method" dropdown |
| **Filter by date range** | Use the date pickers to select from/to dates |
| **Filter by amount** | Use the amount range slider |
| **Sort by amount** | Click the "Amount" column header |
| **View more expenses** | Click page numbers at the bottom |
| **Edit an expense** | Click the "⋮" (three dots) on that row → Edit |
| **Delete an expense** | Click the "⋮" (three dots) on that row → Delete |

### 3.2 Filter Architecture

```mermaid
flowchart LR
    A[User Selects Filters] --> B[Build Query Params]
    B --> C[Construct API Request]
    C --> D["GET /billing/expense/"]
    D --> E[Backend Applies Filters]
    E --> E1[Category Filter]
    E --> E2[Payment Method Filter]
    E --> E3[Date Range Filter]
    E --> E4[Amount Range Filter]
    E --> F[Return Filtered Results]
    F --> G[Update UI with Results]
    G --> H[Update Statistics Cards]
```

### 3.3 Table Columns Display

```mermaid
flowchart TD
    A[Table Rendered] --> B[Title Column]
    A --> C[Categories Column]
    A --> D[Amount Column]
    A --> E[Payment Method Column]
    A --> F[Expense Date Column]
    A --> G[Actions Column]
    
    C --> C1{Multiple Categories?}
    C1 -->|Yes| C1a[Show All as Colored Badges]
    C1 -->|No| C1b[Show Single Badge]
    
    D --> D1[Format as Currency]
    D1 --> D1a["Add ৳ Symbol"]
    D1 --> D1b["Format with Commas"]
    
    E --> E1[Color-code by Method]
    E1 --> E1a["Cash = Green"]
    E1 --> E1b["Card = Blue"]
    E1 --> E1c["Bank = Purple"]
    
    G --> G1[Dropdown Menu]
    G1 --> G1a["✏️ Edit"]
    G1 --> G1b["🗑️ Delete"]
```

---

## 4. Expense Edit/Update Workflow

### 4.1 Editing an Expense

**Use this workflow to update an existing expense:**

```mermaid
flowchart TD
    %% Start
    A["👤 User wants to edit expense"] --> B["⋮ Click 'Actions' menu<br/>on the expense row"]
    
    %% Action Menu
    B --> C["📋 Select 'Edit'<br/>from dropdown menu"]
    C --> D["🪟 Edit Dialog Opens"]
    
    %% Loading Data
    D --> D0["⏳ Loading expense data..."]
    D0 --> D1["📡 API: GET /billing/expense/{id}"]
    D1 --> D2["📊 Pre-populate form with current values"]
    
    %% Form Display
    D --> E["📋 Edit Expense Form"]
    E --> E1["📝 Title field<br/>Current value shown"]
    E --> E2["💵 Amount field<br/>Current value shown"]
    E --> E3["📅 Expense Date<br/>Current date shown"]
    E --> E4["🏷️ Categories<br/>Current selections shown"]
    E --> E5["💳 Payment Method<br/>Current method shown"]
    E --> E6["📝 Description<br/>Current text shown"]
    
    %% User Input
    E --> F["✏️ User makes changes<br/>Updates one or more fields"]
    F --> G["💾 Click 'Update Expense' button"]
    
    %% Validation
    G --> H{"🔍 Validation Check"}
    H -->|Invalid| H1["❌ Show field errors<br/>Red highlights on invalid fields"]
    H1 --> F
    H -->|Valid| I["✅ Ready to save"]
    H -->|No Changes| I1["ℹ️ Button disabled<br/>'No changes detected'"]
    
    %% API Call
    I --> J["🌐 API: PATCH /billing/expense/{id}"]
    J --> K["💾 Updating Expense Record"]
    K --> L["🔄 Updating Category Mappings"]
    L --> M["✅ Expense updated successfully!"]
    M --> N["🪟 Dialog closes"]
    N --> O["🔄 Table refreshes<br/>Showing updated data"]
    O --> P["🎉 Success toast displayed"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class C,D,E,F step
    class E1,E2,E3,E4,E5,E6 input
    class H decision
    class H1 error
    class I1 info
    class M,N,O,P success
    class G,I,J,K,L backend
```

### 4.2 What Can Be Edited

| Field | Editable | Notes |
|-------|----------|-------|
| Title | Yes | Must remain unique and valid |
| Amount | Yes | Must be positive number |
| Expense Date | Yes | Can be past or present date |
| Categories | Yes | Can add/remove categories |
| Payment Method | Yes | Can switch between methods |
| Description | Yes | Optional field |
| Company | No | Fixed to user's company |
| Created Date | No | System-generated |

---

## 5. Expense Deletion Workflow

### 5.1 Deleting an Expense

```mermaid
flowchart TD
    A["👤 User wants to delete expense"] --> B["⋮ Click 'Actions' menu<br/>on the expense row"]
    B --> C["📋 Select 'Delete'<br/>from dropdown menu"]
    C --> D["🗑️ Delete Confirmation Dialog"]
    
    D --> D1["⚠️ Warning Message"]
    D1 --> D1a["'Are you sure you want to delete?'"]
    D1 --> D1b["Expense title displayed"]
    D1 --> D1c["'This action cannot be undone'"]
    
    D --> E{"🤔 User decides"}
    E -->|Cancel| E1["❌ Dialog closes<br/>No action taken"]
    E -->|Confirm| F["🌐 API: DELETE /billing/expense/{id}"]
    
    F --> G["💾 Soft Delete Executed"]
    G --> G1["is_deleted = True"]
    G --> G2["Category mappings removed"]
    
    G --> H["✅ Expense deleted successfully!"]
    H --> I["🪟 Dialog closes"]
    I --> J["🔄 Table refreshes<br/>Expense removed from list"]
    J --> K["🎉 Success toast: 'Expense deleted'"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef cancel fill:#f5f5f5,stroke:#616161,stroke-width:2px
    classDef delete fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class B,C,D step
    class E decision
    class E1 cancel
    class D1,G,F delete
    class H,I,J,K success
```

---

## 6. Expense Category Management

### 6.1 Category Management Entry Point

```mermaid
flowchart TD
    A["👤 User navigates to<br/>Expense Categories"] --> B["📁 Categories List Page"]
    
    B --> C["📊 Categories Table"]
    C --> C1["Name Column"]
    C --> C2["Description Column"]
    C --> C3["Status Column<br/>Active/Inactive"]
    C --> C4["Created Date Column"]
    C --> C5["Actions Column<br/>Edit/Delete"]
    
    B --> D["🔍 Search Input"]
    D --> D1["Search by name<br/>Instant filter"]
    
    B --> E["➕ Add Category Button"]
    E --> F["🪟 Category Form Dialog"]
    
    F --> G["📋 Category Form"]
    G --> G1["Name Input*"]
    G --> G2["Description Input"]
    G --> G3["Create/Update Button"]
    
    %% Styling
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef action fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    
    class A,B,C action
    class D,E,F,G component
    class C1,C2,C3,C4,C5,D1,G1,G2,G3 page
```

### 6.2 Creating a New Category

```mermaid
flowchart TD
    A["Click 'Add Category'"] --> B["Category Form Opens"]
    B --> C["Enter Category Name*"]
    B --> D["Enter Description"]
    C --> E{"Name exists?"}
    E -->|Yes| E1["❌ Error: 'Category already exists'"]
    E1 --> C
    E -->|No| F["Click 'Create Category'"]
    F --> G["API: POST /billing/expense-category/"]
    G --> H["✅ Category created"]
    H --> I["Dialog closes<br/>Table refreshes"]
```

### 6.3 Category Usage in Expenses

```mermaid
flowchart LR
    A[Expense] --> B{Categories}
    B --> C[Office Supplies]
    B --> D[Utilities]
    B --> E[Marketing]
    B --> F[Travel]
    B --> G[Equipment]
    B --> H[Custom Category]
    
    C --> I[Reports]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J[Category Breakdown]
    I --> K[Category Trends]
```

---

## 7. Expense Reports & Analytics

### 7.1 Reports Dashboard Overview

```mermaid
flowchart TD
    A["📊 Expense Reports Page"] --> B["📅 Date Range Selector"]
    B --> B1["Default: Last 30 Days"]
    B --> B2["Custom Range Selectable"]
    
    A --> C["📈 Summary Cards"]
    C --> C1["Total Expense<br/>Period total"]
    C --> C2["Top Category<br/>Highest spend"]
    C --> C3["Largest Transaction<br/>Single expense"]
    
    A --> D["📊 Charts Section"]
    D --> D1["Category Breakdown<br/>Pie Chart"]
    D --> D2["Monthly Trend<br/>Line Chart"]
    D --> D3["Daily Pattern<br/>Bar Chart"]
    D --> D4["Weekly Trend<br/>Line Chart"]
    D --> D5["Category Trend<br/>Area Chart"]
    
    A --> E["📋 Top Expenses Table"]
    E --> E1["Highest 10 Expenses"]
    E --> E2["Sortable Columns"]
    
    B --> F["API: GET /billing/expense/reports/overview"]
    F --> G["Data Aggregated"]
    G --> D
    G --> E
    
    %% Styling
    classDef header fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef cards fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef charts fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef table fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B header
    class C,C1,C2,C3 cards
    class D,D1,D2,D3,D4,D5 charts
    class E,E1,E2 table
    class F,G api
```

### 7.2 Report Data Flow

```mermaid
flowchart LR
    A[Select Date Range] --> B[Build Filter Params]
    B --> C["GET /billing/expense/reports/overview"]
    C --> D[Backend Aggregates Data]
    D --> D1[Category Breakdown]
    D --> D2[Monthly Aggregation]
    D --> D3[Daily Patterns]
    D --> D4[Weekly Trends]
    D --> D5[Top Expenses]
    D1 --> E[Update Pie Chart]
    D2 --> F[Update Line Chart]
    D3 --> G[Update Bar Chart]
    D4 --> H[Update Weekly Chart]
    D5 --> I[Update Top Expenses Table]
```

### 7.3 Available Reports

| Report | Type | Description |
|--------|------|-------------|
| Category Breakdown | Pie Chart | Spending distribution by category |
| Monthly Trend | Line Chart | Spending over months |
| Daily Pattern | Bar Chart | Spending by day of week |
| Weekly Trend | Line Chart | Spending by week |
| Category Trend | Area Chart | Category spending over time |
| Top Expenses | Table | Highest individual expenses |

---

## 8. Data Models

### 8.1 Expense Entity

```mermaid
erDiagram
    EXPENSE {
        int id PK
        string title
        string description
        decimal amount
        string category
        enum payment_method
        timestamp expense_date
        int company_id FK
        timestamp cd
        timestamp md
        int cb
        int mb
        boolean is_deleted
    }
    
    EXPENSE_CATEGORY {
        int id PK
        string name
        string description
        int company_id FK
        boolean is_active
        timestamp cd
        timestamp md
    }
    
    EXPENSE_CATEGORY_MAPPING {
        int id PK
        int expense_id FK
        int category_id FK
        timestamp created_at
    }
    
    EXPENSE ||--o{ EXPENSE_CATEGORY_MAPPING : "has"
    EXPENSE_CATEGORY ||--o{ EXPENSE_CATEGORY_MAPPING : "assigned to"
```

### 8.2 Expense Schema Definition

```typescript
// Expense Base Schema
interface Expense {
  id: number;
  title: string;
  description?: string;
  amount: number;
  category?: string;           // Legacy single category
  categories: ExpenseCategory[]; // Multi-category support
  category_ids: number[];
  payment_method: 'cash' | 'card' | 'bank';
  expense_date: string;        // ISO date string
  company_id: number;
  cd: string;                  // Created date
  md: string;                  // Modified date
}

// Expense Category Schema
interface ExpenseCategory {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  company_id: number;
}

// Filter Parameters
interface ExpenseFilterParams {
  categories?: string[];
  payment_method?: 'cash' | 'card' | 'bank';
  expense_date_start?: string;
  expense_date_end?: string;
  amount_min?: number;
  amount_max?: number;
}

// Statistics Response
interface ExpenseStatistics {
  total_count: number;
  total_amount: number;
  average_amount: number;
  category_breakdown: Record<string, number>;
  payment_method_breakdown: Record<string, number>;
}

// Report Response
interface ExpenseReportsResponse {
  category_breakdown: Array<{
    category: string;
    total_amount: number;
    transaction_count: number;
  }>;
  monthly_trend: Array<{
    month: string;
    total_amount: number;
  }>;
  daily_pattern: Array<{
    day_of_week: number;
    day_name: string;
    total_amount: number;
  }>;
  weekly_trend: Array<{
    week_start: string;
    total_amount: number;
  }>;
  top_expenses: Expense[];
  category_trend: Array<{
    month: string;
    category: string;
    total_amount: number;
  }>;
}
```

### 8.3 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/billing/expense/` | List expenses with filters |
| POST | `/api/company/billing/expense/` | Create new expense |
| GET | `/api/company/billing/expense/{id}` | Get single expense |
| PATCH | `/api/company/billing/expense/{id}` | Update expense |
| DELETE | `/api/company/billing/expense/{id}` | Delete expense |
| GET | `/api/company/billing/expense/statistics/summary` | Get statistics |
| GET | `/api/company/billing/expense/reports/overview` | Get reports data |
| GET | `/api/company/billing/expense-category/` | List categories |
| POST | `/api/company/billing/expense-category/` | Create category |
| GET | `/api/company/billing/expense-category/{id}` | Get single category |
| PATCH | `/api/company/billing/expense-category/{id}` | Update category |
| DELETE | `/api/company/billing/expense-category/{id}` | Delete category |

---

## Summary

The Expense Module provides a complete solution for tracking and analyzing business expenses:

1. **Easy Recording**: Quick expense entry with multi-category support
2. **Flexible Categorization**: Tag expenses with multiple categories for detailed tracking
3. **Comprehensive Filtering**: Filter by category, payment method, date, and amount
4. **Visual Analytics**: Charts and graphs for spending insights
5. **Detailed Reports**: Category breakdowns, trends, and patterns
6. **Soft Delete**: Safe deletion with recovery possibility

For support or questions, contact your system administrator.
