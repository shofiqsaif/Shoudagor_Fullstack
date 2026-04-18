# Billing Module (Expenses & Invoices) - Complete Reference

---

**Generated:** April 17, 2026  
**Scope:** Full-stack analysis of the Billing Module  
**Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

---

## Table of Contents

1. [Module Architecture Overview](#1-module-architecture-overview)
2. [Entity Inventory](#2-entity-inventory)
3. [Backend Operations Reference](#3-backend-operations-reference)
4. [Frontend UI Walkthrough](#4-frontend-ui-walkthrough)
5. [Interconnected Workflows](#5-interconnected-workflows)
6. [Special Features Deep-Dive](#6-special-features-deep-dive)
7. [API Quick Reference](#7-api-quick-reference)
8. [File Map](#8-file-map)
9. [Appendix: Operation Counts](#9-appendix-operation-counts)

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAYER STRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐                                                      │
│  │   PRESENTATION      │  React + TypeScript + Tailwind CSS                 │
│  │   LAYER             │  Shadcn/UI Components                               │
│  │                     │  React Query (TanStack Query)                       │
│  └─────────────────────┘                                                      │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────┐                                                      │
│  │   API LAYER         │  RESTful API Client (axios wrapper)               │
│  │                     │  Zod Schema Validation                              │
│  │                     │  React Hook Form                                    │
│  └─────────────────────┘                                                      │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────┐                                                      │
│  │   BACKEND           │  FastAPI (Python)                                   │
│  │   LAYER             │  SQLAlchemy ORM                                     │
│  │                     │  Pydantic Schemas                                   │
│  └─────────────────────┘                                                      │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────┐                                                      │
│  │   DATA LAYER        │  PostgreSQL (billing schema)                       │
│  │                     │  Database Indexes                                   │
│  └─────────────────────┘                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENTITY RELATIONSHIPS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────────┐         ┌──────────────────────┐                  │
│   │  AppClientCompany    │         │   expense_category   │                  │
│   │       (1)            │         │         (1)          │                  │
│   └──────────┬───────────┘         └──────────┬───────────┘                  │
│              │ 1:N                              │ 1:N                          │
│              ▼                                  ▼                              │
│   ┌──────────────────────┐         ┌──────────────────────┐                  │
│   │      expenses        │◄───────►│expense_category_mapping│                │
│   │       (N)            │   N:M   │         (N)          │                  │
│   └──────────┬───────────┘         └──────────────────────┘                  │
│              │                                                                │
│              │ N:1                                                            │
│              ▼                                                                │
│   ┌──────────────────────┐                                                    │
│   │    variant_group     │                                                    │
│   │       (1)            │                                                    │
│   └──────────────────────┘                                                    │
│                                                                              │
│   ┌──────────────────────┐         ┌──────────────────────┐                  │
│   │   sales_order        │◄───────►│      invoice         │                  │
│   │       (1)            │   1:N   │         (1)          │                  │
│   └──────────────────────┘         └──────────┬───────────┘                  │
│                                              │ 1:N                          │
│                                              ▼                              │
│                                   ┌──────────────────────┐                    │
│                                   │   invoice_detail     │                    │
│                                   │         (N)          │                    │
│                                   └──────────┬───────────┘                    │
│                                              │                              │
│           ┌──────────────────────────────────┼──────────────────┐           │
│           │                                  │                  │           │
│           ▼ N:1                              ▼ N:1               ▼ N:1       │
│   ┌───────────────┐               ┌──────────────────┐  ┌──────────────┐     │
│   │    product    │               │  product_variant   │  │unit_of_measure│    │
│   │      (1)      │               │       (1)          │  │     (1)      │     │
│   └───────────────┘               └──────────────────┘  └──────────────┘     │
│                                                                              │
│   Additional Invoice Relationships:                                          │
│   - customer (N:1) - sales.customer                                          │
│   - location (N:1) - warehouse.storage_location                              │
│   - company (N:1) - security.app_client_company                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18+ | UI Framework |
| **Frontend** | TypeScript 5+ | Type Safety |
| **Frontend** | Tailwind CSS | Styling |
| **Frontend** | shadcn/ui | UI Components |
| **Frontend** | TanStack Query | Data Fetching |
| **Frontend** | React Hook Form | Form Management |
| **Frontend** | Zod | Schema Validation |
| **Frontend** | Recharts | Data Visualization |
| **Frontend** | jsPDF | PDF Generation |
| **Backend** | FastAPI | API Framework |
| **Backend** | SQLAlchemy 2+ | ORM |
| **Backend** | Pydantic | Schema Validation |
| **Backend** | PostgreSQL | Database |
| **Backend** | Alembic | Migrations |

---

## 2. Entity Inventory

### 2.1 Database Schema: `billing.expense_category`

**Table:** `billing.expense_category` - Stores expense category definitions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY, INDEX` | Auto-increment primary key |
| `name` | `VARCHAR(100)` | `NOT NULL` | Category name (unique per company) |
| `description` | `VARCHAR(500)` | `NULLABLE` | Category description |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE` | Soft activation flag |
| `company_id` | `INTEGER` | `FK → security.app_client_company` | Multi-tenant company reference |
| `cb` | `INTEGER` | `NOT NULL` | Created by user ID |
| `cd` | `TIMESTAMP` | `DEFAULT NOW()` | Creation date |
| `mb` | `INTEGER` | `NULLABLE` | Modified by user ID |
| `md` | `TIMESTAMP` | `NULLABLE` | Modification date |
| `is_deleted` | `BOOLEAN` | `DEFAULT FALSE` | Soft delete flag |

**Indexes:**
- `idx_expense_category_name` on `name`

**Relationships:**
- `N:M` with `expenses` via `expense_category_mapping`
- `N:1` with `security.app_client_company`

---

### 2.2 Database Schema: `billing.expense_category_mapping`

**Table:** `billing.expense_category_mapping` - Junction table for expense-category many-to-many relationship

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY, INDEX` | Auto-increment primary key |
| `expense_id` | `INTEGER` | `NOT NULL, FK → billing.expenses` | Reference to expense |
| `category_id` | `INTEGER` | `NOT NULL, FK → billing.expense_category` | Reference to category |
| `created_at` | `TIMESTAMP` | `DEFAULT NOW()` | Mapping creation date |

**Indexes:**
- `idx_expense_category_mapping_expense` on `expense_id`
- `idx_expense_category_mapping_category` on `category_id`

**Relationships:**
- `N:1` with `billing.expenses`
- `N:1` with `billing.expense_category`

---

### 2.3 Database Schema: `billing.expenses`

**Table:** `billing.expenses` - Stores expense records

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `INTEGER` | `PRIMARY KEY, INDEX` | Auto-increment primary key |
| `title` | `VARCHAR(255)` | `NOT NULL` | Expense title/description |
| `description` | `VARCHAR(500)` | `NULLABLE` | Detailed description |
| `amount` | `NUMERIC(18,2)` | `NOT NULL` | Expense amount |
| `category` | `VARCHAR(100)` | `NULLABLE` | Legacy category (backward compatibility) |
| `payment_method` | `ENUM` | `NOT NULL` | `cash`, `card`, `bank` |
| `expense_date` | `TIMESTAMP` | `NOT NULL` | Date when expense occurred |
| `variant_group_id` | `INTEGER` | `NULLABLE, FK → inventory.variant_group` | Optional variant group reference |
| `company_id` | `INTEGER` | `FK → security.app_client_company` | Multi-tenant company reference |
| `cb` | `INTEGER` | `NOT NULL` | Created by user ID |
| `cd` | `TIMESTAMP` | `DEFAULT NOW()` | Creation date |
| `mb` | `INTEGER` | `NULLABLE` | Modified by user ID |
| `md` | `TIMESTAMP` | `NULLABLE` | Modification date |
| `is_deleted` | `BOOLEAN` | `DEFAULT FALSE` | Soft delete flag |

**Indexes:**
- `idx_expense_category` on `category`
- `idx_expense_date` on `expense_date`

**Relationships:**
- `N:M` with `expense_category` via `expense_category_mapping`
- `N:1` with `security.app_client_company`
- `N:1` with `inventory.variant_group` (optional)

**Enum Definition:**
```python
class PaymentMethod(PyEnum):
    cash = "cash"
    card = "card"
    bank = "bank"
```

---

### 2.4 Database Schema: `billing.invoice`

**Table:** `billing.invoice` - Stores invoice records linked to sales orders

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `invoice_id` | `INTEGER` | `PRIMARY KEY, INDEX` | Auto-increment primary key |
| `invoice_number` | `VARCHAR(50)` | `NOT NULL` | Unique invoice number (INV-YYYYMMDD-XXXX) |
| `order_id` | `INTEGER` | `NOT NULL, FK → sales.sales_order` | Linked sales order |
| `order_type` | `VARCHAR(10)` | `NOT NULL` | Order type (e.g., "sales") |
| `customer_id` | `INTEGER` | `NULLABLE, FK → sales.customer` | Customer reference |
| `invoice_date` | `TIMESTAMP` | `NOT NULL` | Invoice creation date |
| `due_date` | `TIMESTAMP` | `NULLABLE` | Payment due date |
| `subtotal` | `NUMERIC(18,2)` | `NOT NULL, DEFAULT 0` | Sum before discounts |
| `discount_amount` | `NUMERIC(18,2)` | `NOT NULL, DEFAULT 0` | Total discount amount |
| `discount_type` | `VARCHAR(20)` | `NULLABLE` | `percentage` or `fixed` |
| `total_amount` | `NUMERIC(18,2)` | `NOT NULL` | Final amount after discounts/tax |
| `tax_amount` | `NUMERIC(18,2)` | `NULLABLE` | Tax amount |
| `status` | `VARCHAR(20)` | `NOT NULL` | `Draft`, `Issued`, `Paid`, `Cancelled` |
| `payment_status` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'Unpaid'` | `Unpaid`, `Partial`, `Paid` |
| `location_id` | `INTEGER` | `NULLABLE, FK → warehouse.storage_location` | Storage location |
| `shipping_address` | `VARCHAR(500)` | `NULLABLE` | Shipping address |
| `remarks` | `VARCHAR(500)` | `NULLABLE` | Additional notes |
| `company_id` | `INTEGER` | `FK → security.app_client_company` | Multi-tenant reference |
| `cb` | `INTEGER` | `NOT NULL` | Created by user ID |
| `cd` | `TIMESTAMP` | `DEFAULT NOW()` | Creation date |
| `mb` | `INTEGER` | `NULLABLE` | Modified by user ID |
| `md` | `TIMESTAMP` | `NULLABLE` | Modification date |
| `is_deleted` | `BOOLEAN` | `DEFAULT FALSE` | Soft delete flag |

**Indexes:**
- `idx_invoice_number` on `invoice_number`
- `idx_invoice_order_id` on `order_id`
- `idx_invoice_customer_id` on `customer_id`
- `idx_invoice_status` on `status`
- `idx_invoice_payment_status` on `payment_status`
- `idx_invoice_date` on `invoice_date`

**Relationships:**
- `1:N` with `billing.invoice_detail` (cascade delete)
- `N:1` with `sales.sales_order`
- `N:1` with `sales.customer`
- `N:1` with `warehouse.storage_location`
- `N:1` with `security.app_client_company`

---

### 2.5 Database Schema: `billing.invoice_detail`

**Table:** `billing.invoice_detail` - Line items for invoices

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `invoice_detail_id` | `INTEGER` | `PRIMARY KEY, INDEX` | Auto-increment primary key |
| `invoice_id` | `INTEGER` | `NOT NULL, FK → billing.invoice` | Parent invoice reference |
| `product_id` | `INTEGER` | `NOT NULL, FK → inventory.product` | Product reference |
| `variant_id` | `INTEGER` | `NULLABLE, FK → inventory.product_variant` | Variant reference |
| `unit_of_measure_id` | `INTEGER` | `NULLABLE, FK → inventory.unit_of_measure` | UOM reference |
| `quantity` | `NUMERIC(18,4)` | `NOT NULL` | Item quantity |
| `original_unit_price` | `NUMERIC(18,4)` | `NULLABLE` | Price before discount |
| `unit_price` | `NUMERIC(18,4)` | `NOT NULL` | Final unit price |
| `discount_amount` | `NUMERIC(18,2)` | `NOT NULL, DEFAULT 0` | Line discount amount |
| `discount_type` | `VARCHAR(20)` | `NULLABLE` | `percentage` or `fixed` |
| `tax_rate` | `NUMERIC(5,2)` | `NOT NULL` | Tax percentage |
| `line_total` | `NUMERIC(18,2)` | `NOT NULL` | Calculated line total |
| `cb` | `INTEGER` | `NOT NULL` | Created by user ID |
| `cd` | `TIMESTAMP` | `DEFAULT NOW()` | Creation date |
| `mb` | `INTEGER` | `NULLABLE` | Modified by user ID |
| `md` | `TIMESTAMP` | `NULLABLE` | Modification date |
| `is_deleted` | `BOOLEAN` | `DEFAULT FALSE` | Soft delete flag |

**Indexes:**
- `idx_invoice_detail_invoice_id` on `invoice_id`
- `idx_invoice_detail_product_variant` on `(product_id, variant_id)`

**Relationships:**
- `N:1` with `billing.invoice`
- `N:1` with `inventory.product`
- `N:1` with `inventory.product_variant` (optional)
- `N:1` with `inventory.unit_of_measure` (optional)

---

## 3. Backend Operations Reference

### 3.1 Expense Entity Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List** | `GET` | `/api/company/billing/expense/` | `ExpenseService.list_expenses_with_filter()` | Enhanced listing with filters |
| **Get Single** | `GET` | `/api/company/billing/expense/{id}` | `ExpenseService.get_expense()` | Get expense by ID |
| **Create** | `POST` | `/api/company/billing/expense/` | `ExpenseService.create_expense()` | Create with category mappings |
| **Update** | `PATCH` | `/api/company/billing/expense/{id}` | `ExpenseService.update_expense()` | Update with category sync |
| **Delete** | `DELETE` | `/api/company/billing/expense/{id}` | `ExpenseService.delete_expense()` | Soft delete + cascade category mappings |
| **Statistics** | `GET` | `/api/company/billing/expense/statistics/summary` | `ExpenseService.get_expense_statistics()` | Get statistics with breakdowns |
| **Reports** | `GET` | `/api/company/billing/expense/reports/overview` | `ExpenseService.get_expense_report_data()` | Dashboard report data |

**Filter Parameters (List):**
- `category` - Single category partial match (backward compatible)
- `categories` - Multiple categories exact match (array)
- `payment_method` - Filter by payment method
- `expense_date_start/end` - Date range filter
- `amount_min/max` - Amount range filter
- `title` - Title partial match
- `created_date_start/end` - Creation date range
- `modified_date_start/end` - Modification date range
- `sort_by` - Sort options (12 variations)
- `start`, `limit` - Pagination

---

### 3.2 Expense Category Entity Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List** | `GET` | `/api/company/billing/expense-category/` | `ExpenseCategoryService.get_expense_categories()` | List with search/filter |
| **Get Single** | `GET` | `/api/company/billing/expense-category/{id}` | `ExpenseCategoryService.get_expense_category()` | Get category by ID |
| **Create** | `POST` | `/api/company/billing/expense-category/` | `ExpenseCategoryService.create_expense_category()` | Create with name uniqueness check |
| **Update** | `PATCH` | `/api/company/billing/expense-category/{id}` | `ExpenseCategoryService.update_expense_category()` | Update with validation |
| **Delete** | `DELETE` | `/api/company/billing/expense-category/{id}` | `ExpenseCategoryService.delete_expense_category()` | Soft delete with usage check |

**Filter Parameters (List):**
- `search` - Name partial match
- `is_active` - Filter by active status
- `start`, `limit` - Pagination

---

### 3.3 Invoice Entity Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List** | `GET` | `/api/company/billing/invoice/` | `InvoiceService.list_invoices_with_filter()` | Enhanced listing with metadata |
| **Get Single** | `GET` | `/api/company/billing/invoice/{id}` | `InvoiceService.get_invoice()` | Get invoice with details |
| **Create** | `POST` | `/api/company/billing/invoice/` | `InvoiceService.create_invoice()` | Create with auto-calculated totals |
| **Update** | `PATCH` | `/api/company/billing/invoice/{id}` | `InvoiceService.update_invoice()` | Update with recalculation |
| **Delete** | `DELETE` | `/api/company/billing/invoice/{id}` | `InvoiceService.delete_invoice()` | Soft delete + cascade details |
| **Generate from SO** | `POST` | `/api/company/billing/invoice/from-sales-order/{id}` | `InvoiceService.generate_invoice_from_sales_order()` | Auto-generate from sales order |
| **Statistics** | `GET` | `/api/company/billing/invoice/statistics/summary` | `InvoiceService.get_invoice_statistics()` | Dashboard statistics |
| **Generate Number** | *Internal* | N/A | `InvoiceService.generate_next_invoice_number()` | Auto-generate INV-YYYYMMDD-XXXX |

**Filter Parameters (List):**
- `order_id`, `order_type` - Filter by order
- `status`, `payment_status` - Status filters
- `customer_id`, `location_id` - Reference filters
- `invoice_date_start/end` - Invoice date range
- `due_date_start/end` - Due date range
- `total_amount_min/max` - Amount range
- `tax_amount_min/max` - Tax range
- `sort_by` - Sort options (12 variations)

---

### 3.4 Invoice Detail Entity Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List** | `GET` | `/api/company/billing/invoice-detail/` | `InvoiceDetailService.list_invoice_details_with_filter()` | Enhanced listing |
| **Get Single** | `GET` | `/api/company/billing/invoice-detail/{id}` | `InvoiceDetailService.get_invoice_detail()` | Get detail by ID |
| **Create** | `POST` | `/api/company/billing/invoice-detail/` | `InvoiceDetailService.create_invoice_detail()` | Create with auto line_total calc |
| **Update** | `PATCH` | `/api/company/billing/invoice-detail/{id}` | `InvoiceDetailService.update_invoice_detail()` | Update with recalculation |
| **Delete** | `DELETE` | `/api/company/billing/invoice-detail/{id}` | `InvoiceDetailService.delete_invoice_detail()` | Soft delete |
| **Statistics** | `GET` | `/api/company/billing/invoice-detail/statistics/summary` | `InvoiceDetailService.get_invoice_detail_statistics()` | Detailed statistics |

---

### 3.5 Dashboard Operations (Admin Expense)

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **Dashboard Summary** | `GET` | `/api/company/dashboard/expense/dashboard-summary` | `ExpenseDashboardService.get_dashboard_summary()` | Comprehensive dashboard data |

**Dashboard Response Includes:**
- Total count and amount
- Daily average
- Category breakdown with percentages
- Payment method breakdown with percentages
- Monthly trends
- Top 5 expenses by amount
- 10 most recent expenses

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| **Expenses List** | `/expenses` | ✅ | Main expenses listing with filters, stats cards, table |
| **Add Expense** | `/expenses/new` | ✅ | Create new expense form |
| **Expense Categories** | `/expense-categories` | ✅ | Category management CRUD |
| **Add Expense Category** | `/expense-categories/new` | ✅ | Create new category form |
| **Invoices List** | `/invoices` | ✅ | Invoice listing with print/PDF support |
| **Expense Reports** | `/reports/expenses` | ✅ | Analytics dashboard with charts |
| **Invoice Settings** | `/settings/invoice` | ✅ | Invoice width, language settings |

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **ExpenseForm** | `src/components/forms/ExpenseForm.tsx` | Create/edit expense with multi-category support |
| **ExpenseCategoryForm** | `src/components/forms/ExpenseCategoryForm.tsx` | Create/edit expense category |

**ExpenseForm Features:**
- Zod schema validation
- Multi-select category picker with inline category creation
- Number input with currency formatting
- Date picker for expense date
- Payment method searchable select
- Form dirty checking
- Loading overlay with freeze refresh

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **ExpenseFilter** | `src/components/ExpenseFilter.tsx` | Advanced filter bar with multi-category, payment method, date range, amount range |
| **Invoice** | `src/components/Invoice.tsx` | Invoice display component with A4 and thermal print layouts |
| **ExpenseWidget** | `src/components/dashboard/ExpenseWidget.tsx` | Dashboard widget showing expense KPIs |

**Invoice Component Features:**
- Dual layout modes: A4 professional and thermal POS (58mm/80mm)
- Print and PDF download functionality
- Bengali/English translation support
- jsPDF integration for PDF generation
- Company logo support
- Item variant display
- Discount and tax line items

### 4.4 Context Providers

| Context | File Path | Purpose |
|---------|-----------|---------|
| **SettingsContext** | `src/contexts/SettingsContext.tsx` | Invoice width (A4/58mm/80mm), invoice language (en/bn) |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `src/lib/api/expenseApi.ts` | `getExpenses()`, `createExpense()`, `updateExpense()`, `deleteExpense()`, `getExpenseReports()`, `getExpenseStatistics()` |
| `src/lib/api/expenseCategoryApi.ts` | `getExpenseCategories()`, `getExpenseCategory()`, `createExpenseCategory()`, `updateExpenseCategory()`, `deleteExpenseCategory()` |
| `src/lib/api/invoiceApi.ts` | `getInvoices()`, `getInvoice()`, `createInvoice()`, `updateInvoice()`, `deleteInvoice()`, `generateInvoiceFromSalesOrder()`, `getInvoiceStatistics()` |
| `src/lib/api/adminExpenseDashboardApi.ts` | `getExpenseDashboardSummary()` |

### 4.6 Types & Zod Schemas

| Schema | File | Fields |
|--------|------|--------|
| `insertExpenseSchema` | `src/lib/schema/index.ts` | `title`, `description`, `amount`, `category_ids`, `category`, `payment_method`, `expense_date`, `company_id` |
| `insertExpenseCategorySchema` | `src/lib/schema/index.ts` | `name`, `description` |
| `Expense` | `src/lib/schema/index.ts` | All insert fields + `id`, `category_ids`, `categories[]` |
| `ExpenseCategory` | `src/lib/schema/index.ts` | `id`, `name`, `description`, `is_active`, `company_id`, `cb`, `cd`, `mb`, `md` |
| `Invoice` | `src/lib/api/invoiceApi.ts` | `invoice_id`, `invoice_number`, `order_id`, `customer_id`, `invoice_date`, `due_date`, `subtotal`, `discount_amount`, `total_amount`, `tax_amount`, `status`, `payment_status`, `details[]` |
| `InvoiceDetail` | `src/lib/api/invoiceApi.ts` | `invoice_detail_id`, `product_id`, `variant_id`, `quantity`, `unit_price`, `discount_amount`, `tax_rate`, `line_total` |

---

## 5. Interconnected Workflows

### 5.1 Expense Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXPENSE CREATION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 1: User navigates to /expenses/new                                │ │
│  │ → AddExpense.tsx renders                                               │ │
│  │ → Mounts ExpenseForm component                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 2: ExpenseForm initializes                                        │ │
│  │ → useQuery fetches expense categories                                  │ │
│  │ → useForm initializes with zodResolver(expenseFormSchema)            │ │
│  │ → Category options prepared for MultiSelect                            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 3: User fills form                                                │ │
│  │ → Title, description entered                                         │ │
│  │ → Amount entered via NumberInput                                       │ │
│  │ → Categories selected via MultiSelect                                  │ │
│  │ → Payment method selected via SearchableSelect                       │ │
│  │ → Expense date selected via DatePicker                                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 4: User submits form                                              │ │
│  │ → form.handleSubmit(onSubmit) called                                 │ │
│  │ → Zod validation runs                                                  │ │
│  │ → createMutation.mutate(data) called                                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 5: API call to backend                                            │ │
│  │ → POST /api/company/billing/expense/                                   │ │
│  │ → createExpense(data) API function                                     │ │
│  │ → Request body includes category_ids array                             │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 6: Backend processing                                             │ │
│  │ → ExpenseService.create_expense()                                      │ │
│  │ → Extract category_ids from request                                    │ │
│  │ → Create Expense ORM object                                            │ │
│  │ → Save to database                                                     │ │
│  │ → Create ExpenseCategoryMapping records                                │ │
│  │ → Commit transaction                                                   │ │
│  │ → Return ExpenseRead with categories populated                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 7: Frontend success handling                                      │ │
│  │ → onSuccess: executeFreezeRefresh()                                    │ │
│  │ → Invalidates /expenses query cache                                    │ │
│  │ → Shows success toast                                                  │ │
│  │ → Navigates to /expenses                                               │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Invoice Generation from Sales Order Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INVOICE GENERATION FROM SALES ORDER                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 1: Trigger from Sales Order                                       │ │
│  │ → User clicks "Generate Invoice" in Sales Order view                   │ │
│  │ → generateInvoiceFromSalesOrder(salesOrderId) called                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 2: API call to backend                                            │ │
│  │ → POST /api/company/billing/invoice/from-sales-order/{id}              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 3: Backend processing                                             │ │
│  │ → InvoiceService.generate_invoice_from_sales_order()                   │ │
│  │ → Fetch SalesOrder by ID                                               │ │
│  │ → Check for existing invoice (prevent duplicates)                        │ │
│  │ → Generate invoice number: INV-YYYYMMDD-XXXX                           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 4: Invoice data mapping                                             │ │
│  │ → Map SO fields: customer_id, location_id                              │ │
│  │ → Calculate subtotal from SO effective_total_amount                    │ │
│  │ → Set invoice_date = NOW(), due_date = expected_shipment_date          │ │
│  │ → status = "Issued", payment_status based on SO payment_status         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 5: Create invoice details                                         │ │
│  │ → Iterate through SO details                                           │ │
│  │ → Calculate effective_qty = qty - returned_qty                         │ │
│  │ → Skip if effective_qty <= 0                                           │ │
│  │ → Create InvoiceDetail for each line                                   │ │
│  │ → unit_price from SO detail, line_total = qty * price                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 6: Link invoice to sales order                                    │ │
│  │ → Update SalesOrder.invoice_id with generated invoice_id               │ │
│  │ → Commit transaction                                                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 7: Return invoice data                                            │ │
│  │ → Return InvoiceRead with populated details                            │ │
│  │ → Frontend redirects to /invoices                                      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Invoice Print/PDF Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INVOICE PRINT/PDF WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 1: User selects invoice and clicks "Print"                         │ │
│  │ → Invoices.tsx handlePrintInvoice() called                             │ │
│  │ → Fetches full invoice with details if needed                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 2: Prepare invoice data                                             │ │
│  │ → Map Invoice + InvoiceDetail to InvoiceData interface                   │ │
│  │ → Calculate totals, format items                                       │ │
│  │ → Apply translations if Bengali mode                                   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 3: Render invoice component                                         │ │
│  │ → Invoice.tsx receives InvoiceData                                       │ │
│  │ → Determines layout: A4 or Thermal (58mm/80mm)                         │ │
│  │ → Applies settings from SettingsContext                                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 4: Print flow                                                       │ │
│  │ → User clicks "Print" button                                           │ │
│  │ → handlePrint() opens print window                                     │ │
│  │ → Injects CSS styles for selected format                               │ │
│  │ → Calls window.print()                                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│                                    ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ STEP 5: PDF flow                                                       │ │
│  │ → User clicks "PDF" button                                             │ │
│  │ → handleDownloadPDF() creates jsPDF instance                             │ │
│  │ → Always uses A4 format for PDF                                        │ │
│  │ → Adds logo, business info, customer info                              │ │
│  │ → Renders table with items                                             │ │
│  │ → Adds totals section                                                  │ │
│  │ → pdf.save(`invoice-{number}.pdf`)                                     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Multi-Category Support for Expenses

The expense module supports assigning multiple categories to a single expense through a many-to-many relationship.

**Database Implementation:**
```sql
-- Junction table
CREATE TABLE billing.expense_category_mapping (
    id SERIAL PRIMARY KEY,
    expense_id INTEGER NOT NULL REFERENCES billing.expenses(id),
    category_id INTEGER NOT NULL REFERENCES billing.expense_category(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Behavior:**
- Create: Accepts `category_ids` array, creates mapping records
- Update: Replaces all mappings with new `category_ids`
- Delete: Cascades delete all mappings
- List: Returns populated `categories` array in response

**Filter Logic:**
```python
# Supports both single category (backward compatible) and multi-category
if categories:  # Multi-category exact match
    query = query.filter(Expense.category.in_(cleaned_categories))
elif category:  # Single category partial match
    query = query.filter(Expense.category.ilike(f"%{category}%"))
```

### 6.2 Invoice Auto-Number Generation

**Algorithm:**
```python
def generate_next_invoice_number(company_id: int) -> str:
    today = datetime.now().strftime('%Y%m%d')
    prefix = f"INV-{today}"
    
    # Count existing invoices for today
    count = db.query(func.count(Invoice.invoice_id)).filter(
        Invoice.company_id == company_id,
        Invoice.invoice_number.like(f"{prefix}-%"),
        Invoice.is_deleted == False
    ).scalar() or 0
    
    # Generate with collision handling
    sequence = count + 1
    invoice_number = f"{prefix}-{sequence:04d}"
    
    # Verify uniqueness (loop until unique)
    while existing:
        sequence += 1
        invoice_number = f"{prefix}-{sequence:04d}"
    
    return invoice_number
```

**Example Output:** `INV-20260417-0001`

### 6.3 Invoice Line Total Calculation

**Formula:**
```python
# Line calculations
line_quantity = Decimal(str(detail.quantity))
orig_unit_price = Decimal(str(detail.original_unit_price or detail.unit_price))

# Discount calculation
if detail.discount_type == 'percentage':
    line_discount = (orig_unit_price * line_quantity) * (Decimal(str(detail.discount_amount)) / Decimal('100'))
else:
    line_discount = Decimal(str(detail.discount_amount)) * line_quantity

# Tax and total
line_subtotal = (orig_unit_price * line_quantity) - line_discount
tax_per_line = line_subtotal * (Decimal(str(detail.tax_rate)) / Decimal('100'))
line_total = line_subtotal + tax_per_line

# Invoice totals
subtotal = sum(orig_unit_price * qty for all lines)
discount_total = sum(line_discount for all lines)
tax_total = sum(tax_per_line for all lines)
total_amount = subtotal - discount_total + tax_total
```

### 6.4 Soft Delete Pattern

All billing entities implement soft delete via `is_deleted` flag:

```python
# Repository delete method
def delete(self, entity_obj):
    if entity_obj.is_deleted:
        return False
    entity_obj.is_deleted = True
    entity_obj.md = func.now()  # Update modification date
    return entity_obj

# Query filtering (applied automatically)
query = query.filter(Entity.is_deleted == False)
```

**Cascade Behavior:**
- Invoice delete → Cascade soft delete all invoice_details
- Expense delete → Cascade delete category_mappings (hard delete junction records)
- Category delete → Blocked if used by expenses (usage check)

### 6.5 Multi-Tenant Implementation

All billing queries are scoped by `company_id`:

```python
# Automatic filtering
if company_id is not None:
    query = query.filter(Entity.company_id == company_id)

# From JWT token via dependency
company_id: int = Depends(get_current_company_id)
```

### 6.6 Expense Reports & Analytics

**Report Endpoints:**
- `GET /api/company/billing/expense/reports/overview` - Comprehensive reports
- `GET /api/company/dashboard/expense/dashboard-summary` - Dashboard KPIs

**Analytics Included:**
- Category breakdown with totals and counts
- Monthly trend aggregation
- Daily pattern (day of week analysis)
- Weekly trend
- Top 10 expenses by amount
- Category trend over time

**Date Handling:**
```python
# Monthly aggregation
month_label = func.date_trunc("month", Expense.expense_date)

# Day of week analysis
day_label = func.extract("dow", Expense.expense_date)

# Weekly aggregation
week_label = func.date_trunc("week", Expense.expense_date)
```

### 6.7 Invoice Translation System

**Supported Languages:**
- English (`en`)
- Bengali/Bangla (`bn`)

**Translation Dictionary:**
```typescript
const invoiceTranslations = {
  en: { invoice: "Invoice", qty: "Qty", total: "Total", ... },
  bn: { invoice: "চালান", qty: "পরিমাণ", total: "মোট", ... }
};
```

**Bengali Numerals:**
```typescript
const toBengaliDigits = (num: string): string => {
  const bnDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
  return num.split('').map(char => 
    /\d/.test(char) ? bnDigits[parseInt(char, 10)] : char
  ).join('');
};
```

### 6.8 Enhanced Filter Response Pattern

All list endpoints return metadata for filter UI:

```python
# Standard filter response structure
{
    "total_count": 100,
    "filtered_count": 25,
    "categories": ["Travel", "Food", "Office"],  # Unique values
    "payment_methods": ["cash", "card"],
    "start_expense_date": "2024-01-01",
    "latest_expense_date": "2024-12-31",
    "start_amount": 10.00,
    "max_amount": 5000.00,
    "data": [...]
}
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **Expense** | `GET /billing/expense/` | `GET /billing/expense/{id}` | `POST /billing/expense/` | `PATCH /billing/expense/{id}` | `DELETE /billing/expense/{id}` | Statistics, Reports |
| **ExpenseCategory** | `GET /billing/expense-category/` | `GET /billing/expense-category/{id}` | `POST /billing/expense-category/` | `PATCH /billing/expense-category/{id}` | `DELETE /billing/expense-category/{id}` | - |
| **Invoice** | `GET /billing/invoice/` | `GET /billing/invoice/{id}` | `POST /billing/invoice/` | `PATCH /billing/invoice/{id}` | `DELETE /billing/invoice/{id}` | Generate from SO |
| **InvoiceDetail** | `GET /billing/invoice-detail/` | `GET /billing/invoice-detail/{id}` | `POST /billing/invoice-detail/` | `PATCH /billing/invoice-detail/{id}` | `DELETE /billing/invoice-detail/{id}` | Statistics |
| **Dashboard** | - | - | - | - | - | `GET /dashboard/expense/dashboard-summary` |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-------------------|------------------|
| List Expenses | `getExpenses()` | `GET /billing/expense/` |
| Create Expense | `createExpense(data)` | `POST /billing/expense/` |
| Update Expense | `updateExpense(id, data)` | `PATCH /billing/expense/{id}` |
| Delete Expense | `deleteExpense(id)` | `DELETE /billing/expense/{id}` |
| Get Expense Reports | `getExpenseReports(params)` | `GET /billing/expense/reports/overview` |
| Get Expense Statistics | `getExpenseStatistics(params)` | `GET /billing/expense/statistics/summary` |
| List Categories | `getExpenseCategories()` | `GET /billing/expense-category/` |
| Create Category | `createExpenseCategory(data)` | `POST /billing/expense-category/` |
| List Invoices | `getInvoices()` | `GET /billing/invoice/` |
| Generate from SO | `generateInvoiceFromSalesOrder(id)` | `POST /billing/invoice/from-sales-order/{id}` |
| Get Invoice Stats | `getInvoiceStatistics()` | `GET /billing/invoice/statistics/summary` |
| Get Dashboard | `getExpenseDashboardSummary()` | `GET /dashboard/expense/dashboard-summary` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/billing.py` | Expense, ExpenseCategory, ExpenseCategoryMapping, Invoice, InvoiceDetail ORM models |
| **Schemas** | `Shoudagor/app/schemas/billing/expense.py` | Expense Pydantic schemas |
| **Schemas** | `Shoudagor/app/schemas/billing/expense_category.py` | ExpenseCategory Pydantic schemas |
| **Schemas** | `Shoudagor/app/schemas/billing/invoice.py` | Invoice and InvoiceDetail Pydantic schemas |
| **Schemas** | `Shoudagor/app/schemas/dashboard/expense.py` | Dashboard expense schemas |
| **Repositories** | `Shoudagor/app/repositories/billing/expense.py` | Expense repository with filtering |
| **Repositories** | `Shoudagor/app/repositories/billing/expense_category.py` | ExpenseCategory repository |
| **Repositories** | `Shoudagor/app/repositories/billing/invoice.py` | Invoice repository |
| **Repositories** | `Shoudagor/app/repositories/billing/invoice_detail.py` | InvoiceDetail repository |
| **Services** | `Shoudagor/app/services/billing/expense_service.py` | Expense business logic |
| **Services** | `Shoudagor/app/services/billing/expense_category_service.py` | ExpenseCategory business logic |
| **Services** | `Shoudagor/app/services/billing/invoice_service.py` | Invoice business logic |
| **Services** | `Shoudagor/app/services/billing/invoice_detail_service.py` | InvoiceDetail business logic |
| **Services** | `Shoudagor/app/services/dashboard/expense_dashboard_service.py` | Dashboard aggregation |
| **API** | `Shoudagor/app/api/billing/expense.py` | Expense endpoints |
| **API** | `Shoudagor/app/api/billing/expense_category.py` | ExpenseCategory endpoints |
| **API** | `Shoudagor/app/api/billing/invoice.py` | Invoice endpoints |
| **API** | `Shoudagor/app/api/billing/invoice_detail.py` | InvoiceDetail endpoints |
| **API** | `Shoudagor/app/api/dashboard/admin_expense.py` | Dashboard endpoints |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages** | `shoudagor_FE/src/pages/expenses/Expenses.tsx` | Expenses listing page |
| **Pages** | `shoudagor_FE/src/pages/expenses/new/AddExpense.tsx` | Add expense page |
| **Pages** | `shoudagor_FE/src/pages/expense-categories/ExpenseCategories.tsx` | Categories management |
| **Pages** | `shoudagor_FE/src/pages/expense-categories/new/AddExpenseCategory.tsx` | Add category page |
| **Pages** | `shoudagor_FE/src/pages/invoices/Invoices.tsx` | Invoices listing page |
| **Pages** | `shoudagor_FE/src/pages/reports/expenses/ExpenseReports.tsx` | Expense analytics |
| **Components** | `shoudagor_FE/src/components/forms/ExpenseForm.tsx` | Expense create/edit form |
| **Components** | `shoudagor_FE/src/components/forms/ExpenseCategoryForm.tsx` | Category form |
| **Components** | `shoudagor_FE/src/components/ExpenseFilter.tsx` | Expense filter bar |
| **Components** | `shoudagor_FE/src/components/Invoice.tsx` | Invoice display/print |
| **Components** | `shoudagor_FE/src/components/dashboard/ExpenseWidget.tsx` | Dashboard widget |
| **API** | `shoudagor_FE/src/lib/api/expenseApi.ts` | Expense API client |
| **API** | `shoudagor_FE/src/lib/api/expenseCategoryApi.ts` | Category API client |
| **API** | `shoudagor_FE/src/lib/api/invoiceApi.ts` | Invoice API client |
| **API** | `shoudagor_FE/src/lib/api/adminExpenseDashboardApi.ts` | Dashboard API client |
| **Schemas** | `shoudagor_FE/src/lib/schema/index.ts` | Zod schemas (Expense, ExpenseCategory) |
| **Translations** | `shoudagor_FE/src/lib/invoiceTranslations.ts` | Invoice translations |
| **Hooks** | `shoudagor_FE/src/hooks/useExpenseDashboard.ts` | Dashboard data hook |
| **Hooks** | `shoudagor_FE/src/hooks/useInvoiceTranslations.ts` | Translation hook |
| **Context** | `shoudagor_FE/src/contexts/SettingsContext.tsx` | Invoice settings context |

---

## 9. Appendix: Operation Counts

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|----------------------|---------------------|
| **Expense** | 5 (List, Get, Create, Update, Delete) | 2 (Statistics, Reports) | 6 (getExpenses, createExpense, updateExpense, deleteExpense, getExpenseReports, getExpenseStatistics) | 3 (Expenses, AddExpense, ExpenseForm) |
| **ExpenseCategory** | 5 (List, Get, Create, Update, Delete) | 0 | 5 (getExpenseCategories, getExpenseCategory, createExpenseCategory, updateExpenseCategory, deleteExpenseCategory) | 2 (ExpenseCategories, ExpenseCategoryForm) |
| **Invoice** | 5 (List, Get, Create, Update, Delete) | 2 (Generate from SO, Statistics) | 7 (getInvoices, getInvoice, createInvoice, updateInvoice, deleteInvoice, generateInvoiceFromSalesOrder, getInvoiceStatistics) | 1 (Invoices) |
| **InvoiceDetail** | 5 (List, Get, Create, Update, Delete) | 1 (Statistics) | 0 (internal use) | 0 (internal use) |
| **Dashboard** | 0 | 1 (Dashboard Summary) | 1 (getExpenseDashboardSummary) | 1 (ExpenseWidget) |
| **TOTAL** | **20** | **6** | **19** | **7** |

---

## Summary

The Billing module in Shoudagor ERP is a comprehensive system for managing:

1. **Expenses** - Multi-category expense tracking with advanced filtering, statistics, and reporting
2. **Expense Categories** - Hierarchical category management with usage validation
3. **Invoices** - Full invoice lifecycle linked to sales orders with print/PDF generation
4. **Invoice Details** - Line-item management with automatic calculations

**Key Features:**
- Multi-tenant architecture with company isolation
- Soft delete pattern with cascade handling
- Enhanced filter responses with metadata for UI
- Multi-category support for expenses
- Auto-generated invoice numbers
- Invoice generation from sales orders
- Print and PDF export with multiple layouts (A4, 58mm, 80mm)
- Bengali/English translation support
- Comprehensive dashboard analytics
- Real-time statistics and trend analysis

**Total Operations:** 20 CRUD + 6 Special Operations across 4 main entities
