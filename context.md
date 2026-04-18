# Shoudagor Fullstack Project Context

> **Last Updated:** 2026-04-15  
> **Purpose:** Comprehensive documentation for LLMs and developers to understand the Shoudagor ERP system architecture, codebase structure, and key implementation details.
> **Note:** Updated with Admin Dashboard KPIs (SR/DSR), Pending Customer Workflow, SR Program Reports API, DSR Reports, and Dashboard enhancements (April 7-15, 2026). Previous updates include SR Reports System, SR Program Workflow, Inventory Reports (10 types), Product Image Gallery (April 1-7, 2026).

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Database Design](#database-design)
6. [API Structure](#api-structure)
7. [Key Business Domains](#key-business-domains)
   - [7.1 Batch-Based Inventory](#71-batch-based-inventory)
   - [7.2 Claims \& Schemes](#72-claims--schemes)
   - [7.3 SR Price Management](#73-sr-price-management)
   - [7.4 Notification System](#74-notification-system)
   - [7.5 Dashboard \& Activity Feed](#75-dashboard--activity-feed)
   - [7.6 Phone Suggestions](#76-phone-suggestions)
   - [7.7 Product Image Management](#77-product-image-management)
   - [7.8 Advanced Reporting System](#78-advanced-reporting-system)
   - [7.9 Super Admin Features](#79-super-admin-features)
   - [7.10 Inventory Drift \& Sync](#710-inventory-drift--sync)
   - [7.11 Elasticsearch Sync Status](#711-elasticsearch-sync-status)
   - [7.12 SR Reports System](#712-sr-reports-system-new)
   - [7.13 SR Program Workflow](#713-sr-program-workflow-new)
   - [7.14 Inventory Reports (10 Types)](#714-inventory-reports-10-types-new)
   - [7.15 Background Jobs](#715-background-jobs)
   - [7.16 Employee Management](#716-employee-management)
   - [7.17 Incomplete Features](#717-incomplete-features-planned)
   - [7.18 Pending Customer Workflow](#718-pending-customer-workflow-new)
8. [Elasticsearch Integration](#elasticsearch-integration)
9. [Frontend Hooks](#frontend-hooks)
10. [Common Patterns](#common-patterns)
11. [Quick Reference - Where to Find What](#quick-reference---where-to-find-what)
12. [Recent Implementations Summary](#recent-implementations-summary)

---

## 🎯 Project Overview

**Shoudagor** is a comprehensive, multi-tenant business management system (ERP) built specifically for the **Bangladeshi market**. It manages core business operations including:

- **Inventory Management** - Products, variants, categories, product groups
- **Sales** - Orders, customers, beats, invoices, payments, deliveries, returns
- **Procurement** - Purchase orders, suppliers, deliveries, payments, returns, rejections
- **Warehouse Management** - Storage locations, stock tracking, transfers, adjustments
- **Billing** - Invoices, invoice details, expenses
- **Sales Representatives (SR)** - Mobile workforce management, SR orders, consolidation, commissions, disbursements
- **Delivery Sales Representatives (DSR)** - Delivery workforce management, SO assignments, stock transfers, payment settlements
- **Financial Reporting** - Inventory KPIs, FIFO aging, purchase order reports, business analytics

### Project Structure
```
Shoudagor_Fullstack/
├── Shoudagor/           # Backend (FastAPI + Python)
│   ├── app/             # Main application code
│   ├── alembic/         # Database migrations
│   └── tests/           # Test suite
│
└── shoudagor_FE/        # Frontend (React + TypeScript)
    └── src/             # Source code
```

---

## 🛠️ Technology Stack

### Backend (Shoudagor/app/)
| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| **Language** | Python | 3.x |
| **Web Framework** | FastAPI | Async-ready |
| **Database** | PostgreSQL | Multi-schema architecture |
| **ORM** | SQLAlchemy | 2.0+ |
| **Migrations** | Alembic | Version-controlled schema changes |
| **Search Engine** | Elasticsearch | 8.x for product/customer/supplier search |
| **Validation** | Pydantic | Request/Response schemas |
| **Containerization** | Docker & Docker Compose | Production deployment |

### Frontend (shoudagor_FE/src/)
| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| **Framework** | React | 19.1.0 with TypeScript 5.8.3 |
| **Build Tool** | Vite | 7.0.3 with SWC for fast refresh |
| **Routing** | React Router | v7 |
| **State Management** | TanStack Query | v5 for server state |
| **UI Components** | shadcn/ui | Radix-based components |
| **Styling** | Tailwind CSS | 4.1.11 |
| **Forms** | React Hook Form + Zod | v7 + v4 validation |
| **Notifications** | Sonner + React Hot Toast | Toast notifications |
| **Charts** | Recharts | v2.15.4 for data visualization |
| **File Handling** | xlsx, exceljs, jspdf | For exports |

---

## 🏗️ Backend Architecture

### 5-Layer Clean Architecture

The backend strictly follows a **5-Layer Clean Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (app/api/)                   │
│   FastAPI endpoints - Request/Response handling & routing   │
├─────────────────────────────────────────────────────────────┤
│                  Service Layer (app/services/)              │
│        Business logic, orchestration, complex rules         │
├─────────────────────────────────────────────────────────────┤
│               Repository Layer (app/repositories/)          │
│          Data access abstractions & query building          │
├─────────────────────────────────────────────────────────────┤
│                   Models Layer (app/models/)                │
│           SQLAlchemy ORM models - DB structure              │
├─────────────────────────────────────────────────────────────┤
│                  Schemas Layer (app/schemas/)               │
│      Pydantic models - Validation & serialization           │
└─────────────────────────────────────────────────────────────┘
```

### Directory Details

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `app/api/` | Route handlers organized by domain | `security.py`, `admin.py`, `consolidation.py`, `claims.py`, subdirs for each domain |
| `app/api/dsr/` | DSR-specific routes | `delivery_sales_representative.py`, `dsr_payment_settlement.py`, `dsr_so_assignment.py` |
| `app/api/sr/` | SR-specific routes | SR management, SR orders, assignments, `sr_product_assignment_price.py` |
| `app/api/inventory/` | Inventory routes including batch | `batch.py`, `inventory_movement.py` |
| `app/services/` | Business logic services | Domain-specific service files |
| `app/services/inventory/` | Inventory services including batch | `batch_allocation_service.py`, `backfill_service.py`, `stock_consistency_service.py`, `stock_to_batch_service.py` |
| `app/services/dsr/` | DSR business logic | `delivery_sales_representative_service.py`, `dsr_payment_settlement_service.py`, `dsr_so_assignment_service.py` |
| `app/services/claims/` | Claims business logic | `claim_service.py`, `claim_report_service.py`, `claim_export_service.py` |
| `app/services/notification/` | Notification services | `notification_service.py`, `notification_generator.py`, `notification_scheduler.py` |
| `app/services/admin/` | Admin services | `onboarding_service.py`, `reindex_service.py` |
| `app/repositories/` | Database query abstractions | Mirror service structure |
| `app/models/` | SQLAlchemy models (DB tables) | `inventory.py`, `sales.py`, `procurement.py`, `warehouse.py`, `billing.py`, `batch_models.py`, `claims.py`, `notification.py`, `admin.py` |
| `app/schemas/` | Pydantic validation schemas | Create/Update/Read schemas per entity |
| `app/schemas/dsr/` | DSR-specific schemas | `delivery_sales_representative.py`, `dsr_payment_settlement.py`, `dsr_so_assignment.py` |
| `app/core/` | Core config, DB connection, security | `config.py`, `database.py`, `security.py` |
| `app/subscribers/` | Event listeners (SQLAlchemy events) | `inventory_subscriber.py`, `product_subscriber.py` |

### Entry Point
- **Main Application:** `app/main.py`
  - Configures FastAPI app
  - Sets up CORS (allows `app.bitoroni.xyz`, `localhost:5173`, `localhost:3000`)
  - Registers all routers
  - Global exception handlers for validation, integrity, and SQLAlchemy errors

---

## 🎨 Frontend Architecture

### Directory Structure

```
shoudagor_FE/src/
├── App.tsx              # Main app entry with routing
├── main.tsx             # Vite entry point
├── index.css            # Global styles
├── components/          # Reusable UI components
│   ├── ui/              # Base UI components (shadcn/ui)
│   ├── forms/           # Form components (57 files)
│   │   ├── DSRAssignmentForm.tsx
│   │   ├── DSRDeliveryForm.tsx
│   │   ├── DSRForm.tsx
│   │   ├── DSRPaymentForm.tsx
│   │   ├── DSRSettlementForm.tsx
│   │   ├── DSRStorageForm.tsx
│   │   ├── PurchaseDeliveryForm.tsx
│   │   ├── PurchaseForm.tsx
│   │   ├── PurchaseReturnForm.tsx
│   │   ├── SaleForm.tsx
│   │   ├── SalesDeliveryForm.tsx
│   │   ├── SalesReturnForm.tsx
│   │   ├── UnifiedDeliveryForm.tsx
│   │   ├── StockAdjustmentForm.tsx
│   │   ├── SalesOrderStatusForm.tsx
│   │   ├── PurchaseOrderStatusForm.tsx
│   │   └── ... (45+ more forms)
│   ├── charts/          # Chart components
│   ├── shared/          # Shared components
│   ├── modals/          # Modal dialogs
│   ├── PrivateRoute.tsx # Auth-required routes
│   ├── AdminRoute.tsx   # Admin role guard
│   ├── SuperAdminRoute.tsx # Super admin role guard
│   ├── SRRoute.tsx      # SR role guard
│   └── DSRRoute.tsx     # DSR role guard
├── pages/               # Page components
│   ├── inventory/       # Inventory management pages
│   │   ├── BatchDrillDown.tsx
│   │   ├── MovementLedger.tsx
│   │   ├── BatchReconciliation.tsx
│   │   ├── BatchBackfill.tsx
│   │   ├── SalesOrderBatchAllocations.tsx
│   │   ├── StockToBatch.tsx
│   │   └── DriftApprovals.tsx
│   ├── claims/         # Claims & Schemes pages
│   │   ├── SchemeList.tsx
│   │   ├── SchemeForm.tsx
│   │   ├── SchemeLogList.tsx
│   │   └── ClaimReports.tsx
│   ├── dsr/            # DSR management pages
│   │   ├── DeliverySalesRepresentatives.tsx
│   │   ├── DSRMyAssignments.tsx
│   │   ├── DSRSOAssignments.tsx
│   │   ├── DSRStorages.tsx
│   │   ├── DSRInventoryStock.tsx
│   │   ├── DSRSettlementHistory.tsx
│   │   └── new/AddDSR.tsx
│   ├── sr-orders/       # SR Order management pages
│   ├── reports/         # Report pages
│   │   ├── Reports.tsx
│   │   ├── Inventory.tsx
│   │   ├── PurchaseOrder.tsx
│   │   ├── sales/       # Sales reports
│   │   │   ├── FulfillmentReport.tsx
│   │   │   ├── FinancialReport.tsx
│   │   │   ├── InventoryPerformance.tsx
│   │   │   ├── SalesTeamAnalytics.tsx
│   │   │   ├── AdvancedInsights.tsx
│   │   │   ├── ProductSalesAnalysis.tsx
│   │   │   ├── TerritoryPerformance.tsx
│   │   │   ├── CustomerActivity.tsx
│   │   │   ├── PipelineAnalysis.tsx
│   │   │   └── DemandForecast.tsx
│   │   ├── purchaseorder/  # Purchase order reports
│   │   │   ├── MaverickSpend.tsx
│   │   │   ├── VarianceReport.tsx
│   │   │   ├── EmergencyOrders.tsx
│   │   │   ├── CashFlowProjection.tsx
│   │   │   ├── ABCXYZClassification.tsx
│   │   │   ├── SupplierConsolidation.tsx
│   │   │   ├── POProgress.tsx
│   │   │   └── UninvoicedReceipts.tsx
│   │   └── inventory/   # Inventory reports
│   │       ├── WarehouseSummary.tsx
│   │       ├── InventoryValuation.tsx
│   │       ├── DSIGmroi.tsx
│   │       ├── DeadStock.tsx
│   │       ├── SafetyStock.tsx
│   │       ├── StockByBatch.tsx
│   │       ├── InventoryAgingBatch.tsx
│   │       ├── COGSByPeriod.tsx
│   │       ├── MarginAnalysis.tsx
│   │       └── BatchPnL.tsx
│   ├── super-admin/      # Super admin pages
│   │   ├── users/
│   │   ├── user-categories/
│   │   ├── dsr-storage/
│   │   ├── recent-activities/
│   │   ├── ElasticsearchReindex.tsx
│   │   ├── ElasticsearchSyncStatus.tsx
│   │   └── MiscellaneousOperations.tsx
│   ├── employees/       # Employee management (routes commented)
│   │   ├── Users.tsx
│   │   ├── roles/Roles.tsx
│   │   └── new/AddEmployee.tsx
│   ├── dashboard/       # Dashboard pages
│   ├── sales/           # Sales pages
│   │   ├── Drafts.tsx       # (INCOMPLETE - placeholder only)
│   │   ├── Quotations.tsx   # (INCOMPLETE - placeholder only)
│   │   ├── SalesReturns.tsx # (INCOMPLETE - placeholder only)
│   │   └── PhoneNumberSuggestions.tsx
│   ├── purchases/       # Purchase pages
│   ├── customers/       # Customer pages
│   ├── suppliers/       # Supplier pages
│   ├── products/        # Product pages
│   ├── categories/      # Category pages
│   ├── units/           # Unit pages
│   ├── expenses/        # Expense pages
│   ├── warehouse/       # Warehouse pages
│   └── beats/           # Beat pages
├── lib/                 # Utilities and API layer
│   ├── api/             # API client functions (40 files)
│   │   ├── dsrApi.ts
│   │   ├── dsrInventoryStockApi.ts
│   │   ├── dsrSettlementApi.ts
│   │   ├── dsrStorageApi.ts
│   │   ├── batchApi.ts
│   │   ├── claimsApi.ts
│   │   ├── reindexApi.ts
│   │   ├── dashboardApi.ts
│   │   ├── reportsApi.ts
│   │   ├── srProductAssignmentPriceApi.ts
│   │   ├── notificationApi.ts
│   │   ├── phoneSuggestionApi.ts
│   │   ├── miscAdminApi.ts
│   │   ├── adjustmentApi.ts
│   │   ├── appClientsApi.ts
│   │   ├── authApi.ts
│   │   ├── beatApi.ts
│   │   ├── categoryApi.ts
│   │   ├── customerApi.ts
│   │   ├── expenseApi.ts
│   │   ├── expenseCategoryApi.ts
│   │   ├── inventoryApi.ts
│   │   ├── invoiceApi.ts
│   │   ├── onboardingApi.ts
│   │   ├── productGroupApi.ts
│   │   ├── productPricesApi.ts
│   │   ├── productsApi.ts
│   │   ├── productVariantApi.ts
│   │   ├── purchaseApi.ts
│   │   ├── salesApi.ts
│   │   ├── salesRepresentativeApi.ts
│   │   ├── srOrderApi.ts
│   │   ├── storageLocationsApi.ts
│   │   ├── supplierApi.ts
│   │   ├── testUserBasicInfoApi.ts
│   │   ├── unitOfMeasure.ts
│   │   ├── userApi.ts
│   │   ├── userCategoryApi.ts
│   │   ├── utils.ts
│   │   ├── warehousesApi.ts
│   │   └── ... (additional specialized API files)
│   ├── schema/          # Zod validation schemas
│   └── utils.ts         # Utility functions
├── contexts/            # React Context providers
├── hooks/               # Custom React hooks
└── types/               # TypeScript type definitions
```

### Routing Structure (App.tsx)

The app uses nested routing with role-based access:

```
/login                    → Public
/                        → Dashboard (Admin)
├── PrivateRoute (protected)
│   ├── /sales/pos       → POS (standalone)
│   ├── AdminRoute
│   │   ├── /dashboard
│   │   ├── /dashboard/recent-activities
│   │   ├── /notifications
│   │   ├── /products, /products/new
│   │   ├── /categories, /categories/new
│   │   ├── /units, /units/new
│   │   ├── /product-groups, /product-groups/new
│   │   ├── /customers, /customers/new, /customers/dues
│   │   ├── /customers/beats, /customers/beats/new
│   │   ├── /suppliers, /suppliers/new
│   │   ├── /purchases, /purchases/new
│   │   ├── /sales, /sales/new
│   │   ├── /invoices
│   │   ├── /claims/schemes, /claims/schemes/new, /claims/schemes/:id/edit
│   │   ├── /claims/logs
│   │   ├── /claims/reports
│   │   ├── /sales-representatives/*
│   │   │   ├── /sales-representatives
│   │   │   ├── /sales-representatives/new
│   │   │   ├── /sales-representatives/:id
│   │   │   ├── /sales-representatives/all-orders
│   │   │   ├── /sales-representatives/consolidated
│   │   │   ├── /sales-representatives/unconsolidated
│   │   │   ├── /sales-representatives/commissions
│   │   │   ├── /sales-representatives/disbursement-history
│   │   │   ├── /sales-representatives/price-management
│   │   │   └── /sales-representatives/assigned-products
│   │   ├── /dsr/*  (DSR Admin Management)
│   │   │   ├── /dsr
│   │   │   ├── /dsr/new
│   │   │   ├── /dsr/so-assignments
│   │   │   ├── /dsr/storage
│   │   │   └── /dsr/settlements
│   │   ├── /warehouse/*
│   │   │   ├── /warehouses/storage-locations
│   │   │   ├── /warehouses/storage-locations/new
│   │   │   ├── /warehouse/inventory-stock/transfer
│   │   │   ├── /warehouse/inventory-stock/adjustment
│   │   │   └── /warehouse/inventory
│   │   ├── /inventory/* (Batch Management)
│   │   │   ├── /inventory/batch-drilldown
│   │   │   ├── /inventory/movement-ledger
│   │   │   ├── /inventory/reconciliation
│   │   │   ├── /inventory/backfill
│   │   │   ├── /inventory/allocations
│   │   │   └── /inventory/stock-to-batch
│   │   ├── /expenses, /expenses/new
│   │   ├── /reports
│   │   │   ├── /reports/inventory
│   │   │   │   ├── /reports/inventory/warehouse-summary
│   │   │   │   ├── /reports/inventory/valuation
│   │   │   │   ├── /reports/inventory/dsi-gmroi
│   │   │   │   ├── /reports/inventory/dead-stock
│   │   │   │   └── /reports/inventory/safety-stock
│   │   │   │   ├── /reports/inventory/stock-by-batch
│   │   │   │   ├── /reports/inventory/inventory-aging-batch
│   │   │   │   ├── /reports/inventory/cogs-by-period
│   │   │   │   ├── /reports/inventory/margin-analysis
│   │   │   │   └── /reports/inventory/batch-pnl
│   │   │   ├── /reports/purchaseorder
│   │   │   │   ├── /reports/purchaseorder/maverick-spend
│   │   │   │   ├── /reports/purchaseorder/variance
│   │   │   │   ├── /reports/purchaseorder/emergency-orders
│   │   │   │   ├── /reports/purchaseorder/cash-flow
│   │   │   │   ├── /reports/purchaseorder/classification
│   │   │   │   ├── /reports/purchaseorder/consolidation
│   │   │   │   ├── /reports/purchaseorder/progress
│   │   │   │   └── /reports/purchaseorder/uninvoiced
│   │   │   └── /reports/sales/*
│   │   │       ├── /reports/sales/fulfillment
│   │   │       ├── /reports/sales/profitability
│   │   │       ├── /reports/sales/inventory-performance
│   │   │       ├── /reports/sales/team-performance
│   │   │       ├── /reports/sales/advanced
│   │   │       ├── /reports/sales/product-analysis
│   │   │       ├── /reports/sales/territory-performance
│   │   │       ├── /reports/sales/customer-activity
│   │   │       ├── /reports/sales/pipeline-analysis
│   │   │       └── /reports/sales/demand-forecast
│   │   └── /settings/invoice
│   ├── SuperAdminRoute
│   │   ├── /super-admin/user-categories, /super-admin/user-categories/new
│   │   ├── /super-admin/users, /super-admin/users/new
│   │   ├── /super-admin/dsr-storage, /super-admin/dsr-storage/new
│   │   ├── /super-admin/elasticsearch-reindex
│   │   └── /super-admin/recent-activities
│   ├── SRRoute (Sales Rep mobile)
│   │   ├── /sr/orders, /sr/orders/new
│   │   ├── /sr/products
│   │   ├── /sr/customers
│   │   ├── /sr/phone-suggestions
│   │   └── /sr/price-management
│   └── DSRRoute (Delivery Rep mobile)
│       ├── /dsr/my-assignments
│       └── /dsr/my-inventory
```

### Context Providers

| Context | Purpose | File |
|---------|---------|------|
| `ThemeProvider` | Light/Dark mode | `components/ThemeProvider.tsx` |
| `QueryClientProvider` | TanStack Query | Configured in `App.tsx` |
| `UserProvider` | User authentication state | `contexts/UserContext.tsx` |
| `SettingsProvider` | Application settings | `contexts/SettingsContext.tsx` |
| `BookmarksProvider` | User bookmarks | `contexts/BookmarksContext.tsx` |
| `ProductSelectionProvider` | Product selection state | `contexts/ProductSelectionContext.tsx` |

---

## 🗄️ Database Design

### Multi-Schema Architecture

The database uses **PostgreSQL multi-schema architecture** to logically separate different domains:

| Schema | Purpose | Key Tables |
|--------|---------|------------|
| `security` | User auth, permissions, multi-tenancy | `app_client`, `app_client_company`, `app_user`, `user_category`, `screen`, `module`, `system_operation` |
| `inventory` | Products, variants, batches, movements | `product`, `product_variant`, `product_category`, `unit_of_measure`, `product_price`, `product_group`, `batch`, `inventory_movement`, `claim_scheme`, `claim_slab`, `claim_log`, `company_inventory_setting` |
| `sales` | Sales orders, customers, SR, DSR | `customer`, `sales_order`, `sales_order_detail`, `sales_representative`, `sr_order`, `sr_order_detail`, `sr_product_assignment`, `sr_product_assignment_price_history`, `beat`, `delivery_sales_representative`, `dsr_so_assignment`, `dsr_payment_settlement`, `sr_disbursement`, `sales_order_batch_allocation` |
| `procurement` | Purchase orders and suppliers | `supplier`, `purchase_order`, `purchase_order_detail`, `product_order_delivery_detail`, `product_order_payment_detail` |
| `warehouse` | Storage and stock tracking | `warehouse`, `storage_location`, `inventory_stock`, `stock_transfer`, `stock_transfer_details`, `dsr_storage`, `dsr_inventory_stock`, `dsr_stock_transfer`, `dsr_stock_transfer_detail` |
| `billing` | Invoices and expenses | `invoice`, `invoice_detail`, `expenses` |
| `transaction` | Inventory movements | `inventory_transaction`, `inventory_adjustment`, `adjustment_detail`, `stock_log`, `stock_log_batch` |
| `settings` | System configuration | `country`, `state`, `city`, `currency`, `app_language`, `time_zone` |
| `notification` | System notifications | `notification`, `notification_type` |

### Common Mixins (app/models/mixins.py)

All models use standardized mixins for consistency:

| Mixin | Fields | Purpose |
|-------|--------|---------|
| `TimestampMixin` | `cb`, `cd`, `mb`, `md` | Created by/date, Modified by/date (audit trail) |
| `IsDeletedMixin` | `is_deleted` | Soft delete support |
| `CompanyMixin` | `company_id` | Multi-tenancy (FK to `app_client_company`) |
| `IsActiveMixin` | `is_active` | Active/inactive status |
| `AddressMixin` | `address`, `country_id`, `state_id`, `city_id`, `zip_code` | Location data |
| `ContactAddressMixin` | Extends `AddressMixin` + `contact_person`, `contact_email`, `contact_phone`, `balance_amount` | Contacts |
| `OrderBase` | Common order fields | Abstract base for PurchaseOrder, SalesOrder, SR_Order |
| `OrderDetailBase` | Common line item fields | Abstract base for order details |
| `PaymentDetailBase` | Payment tracking fields | Abstract base for payments |
| `DeliveryDetailBase` | Delivery tracking fields | Abstract base for deliveries |

### Key Relationships

```
AppClientCompany (Multi-tenant root)
├── Users
├── Products → Variants → Prices
│             └── ProductGroups
├── Customers → Beats
│            └── SR Assignments
├── SalesRepresentatives → SR_Orders → SR_Order_Details
│                       └── Product Assignments
│                       └── Customer Assignments
│                       └── SRDisbursements
├── DeliverySalesRepresentatives → DSR_SO_Assignments
│                               └── DSR_Storage → DSR_Inventory_Stock
│                               └── DSR_Payment_Settlements
├── SalesOrders → SalesOrderDetails
│              └── SalesOrderPaymentDetails
│              └── SalesOrderDeliveryDetails
│              └── DSR_Assignment (loaded_by_dsr)
│              └── Invoices
├── PurchaseOrders → PurchaseOrderDetails (with returned_quantity, rejected_quantity)
│                 └── Delivery/Payment Details
├── Suppliers
├── Warehouses → StorageLocations → InventoryStock
│             └── DSRStorage → DSRInventoryStock
└── Invoices → InvoiceDetails
```

### Sales Order Fields

Key fields on `SalesOrder`:
- `order_source` - 'direct' or 'sr' (consolidated from SR orders)
- `is_consolidated` - Boolean indicating if consolidated from SR orders
- `consolidated_sr_orders` - JSON array of consolidated SR order IDs
- `total_price_adjustment` - Price adjustment during consolidation
- `consolidation_date` - When SR orders were consolidated
- `consolidated_by` - User who performed consolidation
- `is_loaded` - Whether loaded into DSR storage
- `loaded_by_dsr_id` - FK to DSR who loaded the order
- `loaded_at` - Timestamp when loaded
- `commission_disbursed` - Status: 'pending', 'ready', 'disbursed'

### Sales Order Detail Fields

Key fields on `SalesOrderDetail`:
- `shipped_quantity` - Quantity shipped/delivered
- `returned_quantity` - Quantity returned by customer
- `sr_order_detail_id` - Link to original SR order detail (primary/first SR)
- `sr_order_detail_ids` - JSONB array of all SR order detail IDs (for multi-SR consolidation)
- `sr_details` - JSONB array containing detailed SR information per line item:
  - `sr_order_detail_id` - Individual SR order detail ID
  - `sr_id` - SR identifier
  - `sr_name` - SR name
  - `sr_order_id` - SR order ID
  - `sr_order_number` - SR order number
  - `quantity` - Quantity from this SR
  - `negotiated_price` - Price negotiated by this SR
  - `sale_price` - Sale price provided to this SR
  - `price_adjustment` - Price difference for this SR's portion
- `negotiated_price` - Price negotiated by SR
- `price_difference` - Difference from standard price
- `sr_id` - FK to SR who created original order
- `provided_sale_price_to_sr` - Sale price given to SR

### SalesOrderBatchAllocation Fields

Key fields on `SalesOrderBatchAllocation`:
- `sales_order_id` - Link to sales order
- `sales_order_detail_id` - Link to sales order detail
- `batch_id` - Allocated batch
- `allocated_quantity` - Quantity allocated from this batch
- `unit_cost` - Cost per unit at time of allocation
- `allocated_at` - Timestamp of allocation

### Purchase Order Detail Fields

Key fields on `PurchaseOrderDetail`:
- `received_quantity` - Quantity actually received
- `returned_quantity` - Quantity returned to supplier
- `rejected_quantity` - Quantity rejected on receipt

### Invoice Fields

Key fields on `Invoice`:
- `subtotal` - Sum before discounts
- `discount_amount` - Discount applied
- `discount_type` - 'percentage' or 'fixed'
- `total_amount` - Final amount
- `tax_amount` - Tax applied
- `status` - 'Draft', 'Issued', 'Paid', 'Cancelled'
- `payment_status` - 'Unpaid', 'Partial', 'Paid'

---

## 🔌 API Structure

### Backend API Organization

**Base Path:** `/api/company/` (company-scoped routes)

| Domain | Route Prefix | Key Endpoints |
|--------|--------------|---------------|
| **Authentication** | `/authentication/` | `POST /login`, `POST /refresh-token` |
| **Users** | `/users/` | CRUD operations |
| **Security** | `/security/` | Roles, permissions, screens |
| **Inventory** | `/inventory/` | Products, variants, categories, units, prices, batches, movements |
| **Sales** | `/sales/` | Orders, customers, beats, batch allocation |
| **SR (Sales Rep)** | `/sr/` | SR management, SR orders, assignments, price management |
| **DSR (Delivery Rep)** | `/dsr/` | DSR management, SO assignments, settlements |
| **Procurement** | `/procurement/` | Suppliers, purchase orders, deliveries, payments |
| **Warehouse** | `/warehouse/` | Storage locations, inventory stock, DSR storage |
| **Billing** | `/billing/` | Invoices, expenses |
| **Claims** | `/claims/` | Schemes, slabs, claim logs |
| **Reports** | `/reports/` | Inventory KPIs, FIFO aging, purchase order reports |
| **Consolidation** | `/sales/consolidation/` | SR order consolidation |
| **Settings** | `/settings/` | Currency, locations |
| **Notifications** | `/notifications/` | Notification management |
| **Dashboard** | `/dashboard/` | Recent activities |
| **Admin** | `/admin/` | Super-admin features, reindexing, onboarding |

### API Endpoint Patterns

1. **List with Pagination:** `GET /{resource}/?start=0&limit=20&search=...`
2. **Get Single:** `GET /{resource}/{id}`
3. **Create:** `POST /{resource}/`
4. **Update:** `PATCH /{resource}/{id}`
5. **Delete:** `DELETE /{resource}/{id}` (soft delete)

### Frontend API Layer (lib/api/)

| File | Backend Domain | Key Functions |
|------|----------------|---------------|
| `authApi.ts` | Authentication | `login()`, `refreshToken()` |
| `productsApi.ts` | Inventory | `getProducts()`, `createProduct()`, `searchProducts()` |
| `productVariantApi.ts` | Inventory | `getVariants()`, `createVariant()` |
| `salesApi.ts` | Sales | `getSales()`, `createSale()`, `getConsolidatedSROrders()`, `getConsolidatedSROrderById()` |
| `customerApi.ts` | Sales | `getCustomers()`, `createCustomer()` |
| `purchaseApi.ts` | Procurement | `getPurchases()`, `createPurchase()`, `recordDelivery()`, `processReturn()` |
| `salesRepresentativeApi.ts` | SR | `getSRs()`, `getSROrders()` |
| `srOrderApi.ts` | SR | `createSROrder()`, `getSROrders()` |
| `srProductAssignmentPriceApi.ts` | SR | SR price management |
| `dsrApi.ts` | DSR | `getDSRs()`, `createDSR()`, `getDSRAssignments()` |
| `dsrInventoryStockApi.ts` | DSR | `getDSRInventoryStock()` |
| `dsrSettlementApi.ts` | DSR | `getSettlements()`, `createSettlement()` |
| `dsrStorageApi.ts` | DSR | `getDSRStorages()`, `transferStock()` |
| `inventoryApi.ts` | Warehouse | `getInventoryStock()`, `transferStock()` |
| `storageLocationsApi.ts` | Warehouse | `getStorageLocations()` |
| `batchApi.ts` | Batch Inventory | Batch CRUD, settings, movements, reports, reconciliation |
| `claimsApi.ts` | Claims | `getSchemes()`, `createScheme()`, `getClaimLogs()` |
| `reportsApi.ts` | Reports | Multiple report endpoints |
| `invoiceApi.ts` | Billing | `getInvoices()`, `createInvoice()` |
| `notificationApi.ts` | Notifications | `getNotifications()`, `markAsRead()` |
| `dashboardApi.ts` | Dashboard | `getRecentActivities()` |
| `reindexApi.ts` | Admin | `reindexProducts()`, `reindexCustomers()` |
| `testUserBasicInfoApi.ts` | Test Accounts | `getOnboardingStatus()`, `submitOnboardingInfo()` |
| `adminSRDashboardApi.ts` | Dashboard | `getAdminSRDashboardSummary()` - SR KPIs with top performers |
| `adminDSRDashboardApi.ts` | Dashboard | `getAdminDSRDashboardSummary()` - DSR KPIs with top performers |
| `dsrReportsApi.ts` | DSR Reports | `getDSRSummaryReport()`, `getDSRLoadingReport()`, `getDSRSOBreakdown()` |
| `srProgramReportsApi.ts` | SR Program | `getSRProgramWorkflow()`, channel/mapping CRUD |
| `pendingCustomerApi.ts` | SR Workflow | `getMyPendingCustomers()`, `approvePendingCustomer()` - Customer approval workflow |

---

## 📦 Key Business Domains

### 1. Inventory Management

**Location:** `app/models/inventory.py`, `app/api/inventory/`, `app/services/inventory/`

| Entity | Description |
|--------|-------------|
| **Product** | Base product with name, category, description |
| **ProductVariant** | SKU variations (size, color) with barcode, unit |
| **ProductCategory** | Hierarchical categories (parent-child) |
| **UnitOfMeasure** | Units with conversions (base_unit_id, conversion_factor) |
| **ProductPrice** | Time-effective pricing per variant |
| **ProductGroup** | Bundled products for bulk operations |
| **VariantGroup** | Grouped variants for rapid selection |
| **ProductVariantImage** | S3-hosted product images |

**Key Fields:**
- `reorder_level` - Minimum stock level before reordering
- `safety_stock` - Buffer stock to prevent stockouts

**Storage Service:**
- **S3Service** (`app/services/storage/s3_service.py`): S3 integration for product variant image storage with presigned URL generation

**Frontend Pages:**
- `/products` - Product list with search (Elasticsearch)
- `/products/new` - Add product with variants
- `/categories`, `/units`, `/product-groups`
- `/schemes` - Manage purchase and sales schemes

### 1.1 Claims & Schemes
**Location:** `app/models/claims.py`, `app/schemas/claims.py`, `app/services/claims/`, `app/api/claims.py`

This is a **newly implemented module** for managing promotional schemes and claims:

| Entity | Description |
|--------|-------------|
| **ClaimScheme** | Defines promotional rules: `buy_x_get_y`, `rebate_flat`, or `rebate_percentage` |
| **ClaimSlab** | Tiers for schemes (e.g., Buy 5 Get 1, Buy 10 Get 3) |
| **ClaimLog** | Audit trail of scheme applications linked to specific orders |

**ClaimScheme Fields:**
- `scheme_name`, `description`, `scheme_type`
- `start_date`, `end_date`, `is_active`
- `trigger_product_id`, `trigger_variant_id` - The product that triggers the scheme
- `free_product_id`, `free_variant_id` - The free product given (for buy_x_get_y)
- `applicable_to` - 'purchase' or 'sale'
- `slabs` - One-to-many relationship with ClaimSlab

**ClaimSlab Fields:**
- `threshold_qty` - Quantity to buy to trigger this slab
- `free_qty` - Quantity given for free (for buy_x_get_y)
- `discount_amount` - Flat discount (for rebate_flat)
- `discount_percentage` - Percentage discount (for rebate_percentage)

**ClaimLog Fields:**
- `ref_id`, `ref_type` - Reference to PO or SO
- `order_detail_id` - Link to specific order detail
- `applied_on_qty` - Quantity the scheme applied to
- `given_free_qty`, `given_discount_amount` - Benefits provided

**Workflow:** `ClaimService.evaluate_pre_claim` calculates benefits during order entry, which are then persisted as `ClaimLog` entries upon order finalization.

**Key Services:**
- `ClaimService` (`app/services/claims/claim_service.py`): Core claim evaluation logic
- `ClaimReportService` (`app/services/claims/claim_report_service.py`): Report generation for claims
- `ClaimExportService` (`app/services/claims/claim_export_service.py`): Export functionality for claim data

**Frontend Pages:**
- `/claims/schemes` - List all schemes
- `/claims/schemes/new` - Create new scheme
- `/claims/schemes/:id/edit` - Edit existing scheme
- `/claims/logs` - View claim application history
- `/claims/reports` - Free quantity and discount reports

**Frontend Forms:**
- `SchemeForm.tsx` - Create/edit schemes with slabs
- `SchemeList.tsx`, `SchemeLogList.tsx`, `ClaimReports.tsx` - List and report views

### 1.2 Batch-Based Inventory

**Location:** `app/models/batch_models.py`, `app/api/inventory/batch.py`, `app/services/inventory/`

This is a **major new feature** implementing batch-level inventory tracking with full cost traceability:

| Entity | Description |
|--------|-------------|
| **Batch** | Represents a group of inventory units received together with common cost. Tracks product, variant, quantity received vs on hand, unit cost, supplier, lot number, status (active/depleted/expired/returned/quarantined), location, source type |
| **InventoryMovement** | Immutable ledger recording every stock change with quantity (positive=inbound, negative=outbound), unit cost locked at transaction time, reference to source document |
| **CompanyInventorySetting** | Company-level inventory configuration controlling valuation mode (FIFO, LIFO, WEIGHTED_AVG) and batch tracking enabled flag |
| **SalesOrderBatchAllocation** | Links sales order details to allocated batches, enabling return processing and cost traceability |

**Batch Fields:**
- `batch_id` - Unique identifier
- `product_id`, `variant_id` - Product linkage
- `qty_received` - Original quantity received
- `qty_on_hand` - Current quantity available
- `unit_cost` - Cost per unit at receipt time
- `received_date` - Date of receipt
- `supplier_id` - Source supplier (for purchases)
- `lot_number` - Optional lot/serial number
- `status` - active, depleted, expired, returned, quarantined
- `location_id` - Storage location
- `purchase_order_detail_id` - Link to PO detail
- `source_type` - purchase, return, adjustment, transfer, synthetic
- `is_synthetic` - Indicates backfilled batches

**Movement Types:**
- `IN` - Inbound (purchases, returns, transfers in)
- `OUT` - Outbound (sales, transfers out)
- `RETURN_IN` - Returned to inventory
- `RETURN_OUT` - Returned out (to supplier)
- `ADJUSTMENT` - Stock correction
- `TRANSFER_IN`, `TRANSFER_OUT` - Location transfers
- `OPENING_BALANCE`, `BACKFILL` - Initial/migration movements

**Valuation Modes:**
- **FIFO** (First In, First Out) - Default
- **LIFO** (Last In, First Out)
- **WEIGHTED_AVG** (Weighted Average Cost)

**Key Services:**
- `BatchAllocationService` (`app/services/inventory/batch_allocation_service.py`):
  - Handles batch allocation for sales orders using configured valuation mode
  - Processes sales returns with batch traceability
  - Supports partial allocations and split shipments
   
- `BackfillService` (`app/services/inventory/backfill_service.py`):
  - Creates synthetic batches from historical PO deliveries
  - Reconciles batch totals with legacy inventory_stock table
  - Backfills sales allocations for historical sales
  - Supports DRY RUN mode for safe migration

- `StockToBatchService` (`app/services/inventory/stock_to_batch_service.py`):
  - Converts existing inventory stock to batch records
  - Supports single product/variant conversion
  - Bulk conversion with unit cost specification

- `StockConsistencyService` (`app/services/inventory/stock_consistency_service.py`):
  - Verifies batch data matches inventory stock records
  - Provides reconciliation reports
  - Identifies discrepancies in stock levels

- `CompanyInventorySettingService` (`app/services/settings/company_inventory_setting_service.py`):
  - Manages company inventory settings
  - Controls valuation mode and batch tracking

**Frontend Pages:**
- `/inventory/batch-drilldown` - View and manage batches with filters, pagination, batch detail modal
- `/inventory/movement-ledger` - Complete inventory movement history with filtering and source document links
- `/inventory/reconciliation` - Verify batch data matches inventory stock records
- `/inventory/backfill` - Migrate historical data (supports DRY RUN mode)
- `/inventory/allocations` - Sales order batch allocations view with batch details per order
- `/inventory/stock-to-batch` - Convert existing inventory stock to batch records

**Batch Reports:**
- `/reports/inventory/stock-by-batch` - Inventory stock grouped by batches with quantity, cost, age, location
- `/reports/inventory/inventory-aging-batch` - Aging based on batch received dates (0-30, 31-60, 61-90, 91-180, 180+ days)
- `/reports/inventory/cogs-by-period` - Cost of Goods Sold grouped by month and product
- `/reports/inventory/margin-analysis` - Selling price vs batch cost analysis
- `/reports/inventory/batch-pnl` - Per-batch profit and loss analysis

**API Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/inventory/batches` | GET, POST | List/create batches |
| `/inventory/batches/{id}` | GET, PATCH | Get/update batch |
| `/inventory/settings` | GET, POST | Company inventory settings |
| `/inventory/movements` | GET, POST | Movement ledger query/create |
| `/inventory/reconciliation` | GET | Batch vs stock reconciliation |
| `/inventory/reconciliation/backfill` | POST | Historical data backfill |
| `/inventory/stock-to-batch` | POST | Convert inventory stock to batch |
| `/inventory/allocations` | GET | Sales order batch allocations |
| `/sales/{id}/allocate` | POST | Server-side batch allocation |
| `/sales/{id}/returns` | POST | Process sales return |
| `/reports/stock-by-batch` | GET | Stock by batch report |
| `/reports/inventory-aging` | GET | Batch-based aging report |
| `/reports/cogs-by-period` | GET | COGS by period report |
| `/reports/margin-analysis` | GET | Margin analysis report |
| `/reports/batch-pnl` | GET | Batch P&L report |
| `/products/{id}/batches` | GET | Product batch drill-down |

**Frontend API:**
- `batchApi.ts` - All batch-related API functions (18+ functions)
  - Batch CRUD: `getBatches()`, `getBatch()`, `createBatch()`, `updateBatch()`
  - Settings: `getCompanyInventorySettings()`, `updateCompanyInventorySettings()`
  - Movements: `getMovementLedger()`
  - Reports: `getStockByBatchReport()`, `getInventoryAgingReport()`, `getCOGSByPeriodReport()`, `getBatchPNLReport()`, `getMarginAnalysisReport()`
  - Reconciliation: `getReconciliationReport()`, `getReconciliationByProduct()`, `runBackfill()`, `runSalesBackfill()`

### 1.3 SR Price Management

**Location:** `app/api/sr/sr_product_assignment_price.py`, `app/services/sr/`, `app/models/sales.py`

This feature allows administrators to assign custom prices to products for individual Sales Representatives:

| Entity | Description |
|--------|-------------|
| **SR_Product_Assignment** | Links products to SRs with custom pricing |
| **SR_Product_Assignment_Price_History** | Tracks price changes over time |

**Key Features:**
- Assign specific products to SRs with custom sale prices
- Track price history for audit and transparency
- Support for both individual product assignments and bulk assignments

**API Endpoints:**
- `GET /sr/price-management/` - List all SR price assignments
- `POST /sr/price-management/` - Create new price assignment
- `PATCH /sr/price-management/{id}` - Update price assignment
- `GET /sr/price-management/history/` - Get price change history

**Frontend Pages:**
- `/sales-representatives/price-management` - Admin view for managing SR prices
- `/sr/price-management` - SR view for viewing their assigned prices
- `/sales-representatives/assigned-products` - View products assigned to SRs

**Frontend Components:**
- `SRPriceHistory.tsx` - View price change history
- `AssignProductWithPriceModal.tsx` - Modal for assigning products with prices
- `SRPriceAssignmentForm.tsx` - Form for assigning prices

### 1.4 Notification System

**Location:** `app/models/notification.py`, `app/api/notification.py`, `app/services/notification/`

A comprehensive notification system to alert users about critical events:

| Entity | Description |
|--------|-------------|
| **NotificationType** | Defines templates and categories for notifications |
| **Notification** | Stores notification data, status (read/unread), priority |

**Notification Types:**
- Low stock alerts
- Payment reminders
- Sales order status changes
- Customer due reminders
- Expense alerts

**API Endpoints:**
- `GET /notifications/` - List notifications with filters
- `GET /notifications/summary` - Get unread count and summary
- `PATCH /notifications/{id}/read` - Mark as read
- `PATCH /notifications/read-all` - Mark all as read
- `DELETE /notifications/{id}` - Delete notification

**Key Services:**
- `NotificationService` (`app/services/notification/notification_service.py`): CRUD operations
- `NotificationGenerator` (`app/services/notification/notification_generator.py`): Create notifications
- `NotificationScheduler` (`app/services/notification/notification_scheduler.py`): Scheduled processing

**Frontend:**
- `/notifications` - Notification page
- `NotificationDropdown` - UI component for viewing notifications
- `useNotifications` hook for state management
- `notificationApi.ts` - API client

### 1.5 Dashboard & Activity Feed

**Location:** `app/services/dashboard_service.py`, `app/api/dashboard.py`

Recent activity tracking provides visibility into user operations:

**Captured Activities:**
- Sales Orders (Created, Payment, Delivery)
- Purchase Orders (Created, Payment, Receipt)
- SR Disbursements & DSR Settlements
- Stock Movements (Transfers, Adjustments, DSR Load/Unload)
- Master Data Changes (Product, Customer, Supplier, etc.)

**Features:**
- **Performed By:** Tracks the specific user who performed the action
- **Pagination:** Supports infinite scroll/pagination
- **Filtering:** Aggregated view of all major system events

**API Endpoints:**
- `GET /dashboard/activities/` - Get recent activities with pagination

**Frontend Pages:**
- `/dashboard/recent-activities` - Activity feed page
- `/` (Admin Dashboard) - Main dashboard with KPIs and draggable widgets

### Admin Dashboard KPIs (NEW - April 2026)

The Admin Dashboard has been enhanced with **KPI visualizations** and **draggable widgets**:

**Dashboard Intelligence Zones:**
| Zone | Metrics Displayed |
|------|-------------------|
| **Financial Pulse** | Revenue, GP%, Collections, Expenses |
| **Sales Engine** | Orders, Fulfillment Rate, Pipeline |
| **Inventory Health** | Dead Stock, Safety Stock, Turnover |
| **Procurement Watch** | PO Status, Supplier Reliability |
| **Workforce Intelligence** | SR/DSR Performance, Commission |
| **Customer Intelligence** | Receivables Aging, Churn Risk |
| **Operational Alerts** | Pending Actions, Low Stock |

**SR Dashboard Summary API:**
- `GET /sales/sr/admin/dashboard-summary` - Aggregated SR KPIs
  - SR counts (total, active, inactive)
  - Order metrics (pending, approved, delivered, cancelled)
  - Financial data (total revenue, commission earned/paid/pending)
  - Monthly activity (orders/revenue this month)
  - Top performing SRs leaderboard

**DSR Dashboard Summary API:**
- `GET /sales/dsr/dashboard-summary` - Aggregated DSR KPIs
  - DSR counts (total, active, inactive)
  - Assignment stats (assigned, in_progress, completed)
  - Financial totals (payment_on_hand, commission, collections)
  - Activity monitoring (active 7d/30d)
  - Top performers by deliveries and collection

**Dashboard Features:**
- **DraggableDashboard Component:** Users can rearrange widgets, layout persists
- **Date Range Filtering:** Global date filter affects all KPI widgets
- **Real-time Updates:** Activity feed shows live operations
- **Top Performers Leaderboards:** SR and DSR rankings

### 1.6 Phone Suggestions

**Location:** `app/models/sales.py` (CustomerPhoneSuggestion), `app/api/sr/customer_phone_suggestion.py`, `app/services/sr/customer_phone_suggestion_service.py`

This feature allows **Sales Representatives** to suggest phone number updates for customers, which are then reviewed and approved by administrators:

| Entity | Description |
|--------|-------------|
| **CustomerPhoneSuggestion** | SR-submitted phone number suggestions with approval workflow |

**CustomerPhoneSuggestion Fields:**
- `customer_id` - Link to customer
- `suggested_phone` - Phone number suggested by SR
- `suggested_by` - FK to SR or user who submitted
- `status` - 'pending', 'approved', 'rejected'
- `reviewed_by` - Admin who approved/rejected
- `reviewed_at` - Timestamp of review
- `reason` - Rejection reason (if rejected)
- `submitted_at` - Submission timestamp

**Workflow:**
1. SR submits phone suggestion via mobile app
2. Admin reviews pending suggestions
3. Admin approves (updates customer phone) or rejects

**API Endpoints:**
- `GET /sr/phone-suggestions/` - List all pending suggestions (admin)
- `GET /sr/my-phone-suggestions/` - SR's own submissions
- `POST /sr/phone-suggestions/` - Submit new suggestion
- `GET /sr/phone-suggestions/{id}` - Get specific suggestion
- `PATCH /sr/phone-suggestions/{id}/approve` - Admin approval
- `PATCH /sr/phone-suggestions/{id}/reject` - Admin rejection

**Frontend Pages:**
- `/sales/phone-number-suggestions` - Admin approval interface
- `/sr/phone-suggestions` - SR submission page (within SR module)

**Frontend Components:**
- `PhoneSuggestionForm.tsx` - Submit phone suggestion form
- `UpdatePhoneNumberForm.tsx` - Direct phone number update
- `PhoneNumberSuggestions.tsx` - Admin approval list

### 1.7 Product Image Management

**Location:** `app/models/inventory.py` (ProductVariantImage), `app/api/inventory/product_variant_image.py`, `app/services/inventory/product_variant_image_service.py`

This feature manages **product variant images** with S3 storage and presigned URL generation:

| Entity | Description |
|--------|-------------|
| **ProductVariantImage** | Stores image metadata with S3 URL and display order |

**ProductVariantImage Fields:**
- `variant_id` - FK to product variant
- `image_url` - S3 hosted image URL
- `image_key` - S3 object key for management
- `display_order` - Ordering for gallery display
- `is_primary` - Primary image flag for thumbnail
- `alt_text` - Accessibility text
- `uploaded_at` - Upload timestamp
- `file_size` - Image file size
- `mime_type` - Image MIME type

**Key Features:**
- Single and batch image uploads
- Presigned URL generation for direct S3 uploads
- Image reordering and primary image selection
- Bulk image operations
- S3 integration with security

**API Endpoints:**
- `POST /inventory/product-variant-images/upload` - Single image upload
- `POST /inventory/product-variant-images/batch-upload` - Batch image upload
- `GET /inventory/product-variant-images/:variantId` - Get variant images
- `POST /inventory/product-variant-images/presigned-url` - Get S3 presigned URL
- `PATCH /inventory/product-variant-images/:id/reorder` - Reorder images
- `PATCH /inventory/product-variant-images/:id/set-primary` - Set primary image
- `DELETE /inventory/product-variant-images/:id` - Delete image

**Frontend Components:**
- Image upload components with preview
- Image gallery with reordering
- Presigned URL handling for direct S3 uploads
- Batch image operations UI

### 1.8 Advanced Reporting System

**Location:** `app/services/reports.py`, `app/api/reports.py`, `app/repositories/reports/`

This is a **comprehensive business intelligence system** with 28 report types across three major categories:

#### Sales Reports (10 Report Types)
| Report | Purpose | Frontend Page | Key Metrics |
|--------|---------|---------------|----|
| **Fulfillment Report** | Order fulfillment and delivery performance | `/reports/sales/fulfillment` | On-time delivery %, order fulfillment rate |
| **Financial Report** | Revenue, costs, and profitability | `/reports/sales/profitability` | Revenue, COGS, GP %, net profit |
| **Inventory Performance** | Turnover and inventory metrics | `/reports/sales/inventory-performance` | Turnover ratio, DSI, stock velocity |
| **Sales Team Analytics** | SR/DSR performance and KPIs | `/reports/sales/team-performance` | Sales per person, conversion rate, targets |
| **Advanced Insights** | Deep analytics and predictive indicators | `/reports/sales/advanced` | Trend analysis, anomalies, forecasts |
| **Product Sales Analysis** | Product-level sales metrics | `/reports/sales/product-analysis` | Top products, volume, trends per product |
| **Territory Performance** | Geographic/beat-wise analysis | `/reports/sales/territory-performance` | Sales by territory, growth rate |
| **Customer Activity** | Customer engagement metrics | `/reports/sales/customer-activity` | Purchase frequency, RFM analysis |
| **Pipeline Analysis** | Sales pipeline visibility | `/reports/sales/pipeline-analysis` | Pipeline stages, conversion rates |
| **Demand Forecast** | AI-powered sales forecasting | `/reports/sales/demand-forecast` | Projected demand, trend predictions |

#### Purchase Order Reports (8 Report Types)
| Report | Purpose | Frontend Page | Key Metrics |
|--------|---------|---------------|----|
| **Maverick Spend** | Off-contract purchasing | `/reports/purchaseorder/maverick-spend` | Non-contract spend %, exceptions |
| **Invoice Variance** | PO vs Invoice price differences | `/reports/purchaseorder/variance` | Price variance %, discrepancies |
| **Emergency Orders** | Expedited/rush procurement | `/reports/purchaseorder/emergency-orders` | Emergency order count, cost impact |
| **Cash Flow Projection** | PO payment timeline forecasting | `/reports/purchaseorder/cash-flow` | Payment schedule, cash requirements |
| **ABC/XYZ Classification** | Supplier categorization | `/reports/purchaseorder/classification` | Spend by category (ABC), volume (XYZ) |
| **Supplier Consolidation** | Supplier concentration analysis | `/reports/purchaseorder/consolidation` | Supplier count, concentration ratio |
| **PO Progress** | Purchase order status tracking | `/reports/purchaseorder/progress` | Open/closed POs, fulfillment %, aging |
| **Uninvoiced Receipts** | Goods received but not invoiced | `/reports/purchaseorder/uninvoiced` | PO receipt count, value pending invoice |

#### Inventory Reports (10 Report Types)
| Report | Purpose | Frontend Page | Key Metrics |
|--------|---------|---------------|----|
| **Warehouse Summary** | Warehouse overview and metrics | `/reports/inventory/warehouse-summary` | Total stock value, occupancy, turnover |
| **Inventory Valuation** | Stock valuation using FIFO/LIFO/WAC | `/reports/inventory/valuation` | Total value, method comparison |
| **DSI/GMROI** | Inventory efficiency metrics | `/reports/inventory/dsi-gmroi` | Days sales of inventory, GMROI |
| **Dead Stock** | Slow-moving inventory identification | `/reports/inventory/dead-stock` | Zero-movement items, age analysis |
| **Safety Stock** | Safety stock recommendations | `/reports/inventory/safety-stock` | Safety stock levels, reorder points |
| **Stock by Batch** | Batch-level inventory breakdown | `/reports/inventory/stock-by-batch` | Qty per batch, unit cost, age, location |
| **Inventory Aging (Batch)** | Batch-based aging analysis | `/reports/inventory/inventory-aging-batch` | Aging buckets (0-30, 31-60, etc.) |
| **COGS by Period** | Period-based cost of goods sold | `/reports/inventory/cogs-by-period` | COGS by month/quarter with trends |
| **Margin Analysis** | Selling price vs batch cost | `/reports/inventory/margin-analysis` | Margin per batch, margin % analysis |
| **Batch P&L** | Per-batch profit and loss | `/reports/inventory/batch-pnl` | Revenue, COGS, profit per batch |

**Frontend Pages (28 Total):**
- 10 inventory report pages in `/reports/inventory/`
- 10 sales report pages in `/reports/sales/`
- 8 purchase order report pages in `/reports/purchaseorder/`

**API Endpoints:**
```
GET /api/company/reports/inventory-kpi-ribbon/
GET /api/company/reports/current-stock/
GET /api/company/reports/purchase-orders/
GET /api/company/reports/sales-financial/
GET /api/company/reports/inventory-performance/
GET /api/company/reports/sales-team-performance/
GET /api/company/reports/sales-advanced-analytics/
GET /api/company/reports/product-sales-analysis/
GET /api/company/reports/territory-sales/
GET /api/company/reports/customer-activity/
GET /api/company/reports/pipeline-analysis/
GET /api/company/reports/demand-forecast/
GET /api/company/reports/warehouse-summary/
GET /api/company/reports/inventory-valuation/
GET /api/company/reports/dsi-gmroi/
GET /api/company/reports/dead-stock/
GET /api/company/reports/safety-stock/
GET /api/company/reports/stock-by-batch/
GET /api/company/reports/cogs-by-period/
GET /api/company/reports/margin-analysis/
GET /api/company/reports/batch-pnl/
```

**Report Components & Charts:**
- `CustomerSalesTrendChart.tsx` - Line chart for customer sales over time
- `InventoryTimelineChart.tsx` - Historical inventory trending
- `TopCustomersChart.tsx` - Bar chart of top customers
- `TopSuppliersChart.tsx` - Top suppliers by spend
- `UnitPriceSuppliers.tsx` - Unit price comparisons
- `VariantSalesChart.tsx` - Product variant sales distribution
- `VariantStocksChart.tsx` - Variant stock levels
- Plus 10+ PO report components for Maverick spend, lead times, supplier performance

### 1.9 Super Admin Features

**Location:** `app/api/admin.py`, `app/api/admin_miscellaneous.py`, `app/services/admin/`

Enhanced administrative capabilities for system-wide management:

| Feature | Description |
|---------|-------------|
| **SR Management** | List SRs across all companies |
| **DSR Management** | List DSRs across all companies |
| **User Management** | User management across companies |
| **DSR Storage** | Create DSR storage for any company |
| **Elasticsearch Reindex** | Reindex products, customers, suppliers |
| **Elasticsearch Health** | Check ES cluster health status, index stats |
| **Elasticsearch Sync Status** | Monitor ES indexing status, failed queue, retry operations |
| **Client Onboarding** | Bulk client onboarding from CSV/Excel |
| **Recent Activities** | View system-wide activities |
| **Miscellaneous Operations** | Demo data population, system-level operations |

**API Endpoints:**
- `GET /admin/sr/` - List all SRs (super admin)
- `GET /admin/dsr/` - List all DSRs (super admin)
- `GET /admin/users/` - User management
- `POST /admin/dsr-storage/` - Create DSR storage
- `POST /admin/reindex/products` - Reindex products
- `POST /admin/reindex/customers` - Reindex customers
- `POST /admin/reindex/suppliers` - Reindex suppliers
- `GET /admin/elasticsearch/health` - Check ES cluster health
- `GET /admin/elasticsearch/sync-status` - Get ES sync status
- `POST /admin/elasticsearch/retry-failed` - Retry failed indexing
- `GET /admin/elasticsearch/failed-queue` - View failed queue
- `POST /admin/onboarding/` - Bulk client onboarding
- `GET /admin/miscellaneous/populate-complex-demo` - Populate demo data

**Key Services:**
- `OnboardingService` (`app/services/admin/onboarding_service.py`): Process CSV/Excel files
- `ReindexService` (`app/services/admin/reindex_service.py`): Reindex operations with audit logging
- `MiscellaneousAdminService`: Demo data population and system operations

**Frontend Pages:**
- `/super-admin/users` - User management
- `/super-admin/user-categories` - Role management
- `/super-admin/dsr-storage` - DSR storage management
- `/super-admin/elasticsearch-reindex` - Reindex functionality
- `/super-admin/elasticsearch-sync-status` - ES sync monitoring and failed queue management
- `/super-admin/miscellaneous` - Demo data population
- `/super-admin/recent-activities` - System activity feed

### 1.10 Inventory Drift & Sync

**Location:** `app/services/inventory/inventory_sync_service.py`, `app/services/inventory/stock_consistency_service.py`

The **Inventory Drift & Sync System** ensures consistency between batch records and the legacy `inventory_stock` table:

| Entity | Description |
|--------|-------------|
| **InventoryDrift** | Tracks discrepancies between batch qty_on_hand and inventory_stock quantity |
| **InventoryMigration** | Tracks migration status for batch data |
| **StockSource** | Enum tracking the source of truth: 'batch' or 'legacy' |

**Key Features:**
- **Drift Detection**: Automatically detects when batch and inventory_stock quantities don't match
- **Drift Approval Workflow**: Admin can review and approve drift corrections
- **Consistency Enforcement**: Prevents operations that would cause inconsistency in batch mode
- **Stock Source Tracking**: Determines which system (batch or legacy) is authoritative

**Key Services:**
- `InventorySyncService` (`app/services/inventory/inventory_sync_service.py`):
  - Centralized sync service for batch inventory operations
  - `StockSource` enum: `BATCH` or `LEGACY`
  - `StockChangeContext`: Tracks the context of stock changes
  - `BatchModeViolationError`: Raised when batch mode rules are violated
  - `StockConsistencyError`: Raised when consistency check fails
  - Decorators: `@enforce_batch_mode` for batch-only operations

- `StockConsistencyService` (`app/services/inventory/stock_consistency_service.py`):
  - Verifies batch data matches inventory_stock records
  - Provides reconciliation reports
  - Identifies discrepancies in stock levels

- `InventoryMigrationService` (`app/services/inventory/inventory_migration_service.py`):
  - Tracks migration status with `MigrationLockError` handling
  - Manages migration state transitions

**Frontend Pages:**
- `/inventory/drift-approvals` - Review and approve inventory drift corrections
- `/inventory/reconciliation` - Batch vs stock reconciliation report

**Frontend Components:**
- `DriftApprovals.tsx` - Drift approval interface with repair options
- `BatchReconciliation.tsx` - Reconciliation report with bulk repair

### 1.11 Elasticsearch Sync Status

**Location:** `app/api/admin_miscellaneous.py`, `app/models/admin.py`

The **Elasticsearch Sync Status** system monitors real-time indexing operations:

| Entity | Description |
|--------|-------------|
| **FailedIndexQueue** | Tracks failed ES indexing operations for retry |
| **SyncStatus** | Real-time indexing status dashboard |

**Key Features:**
- **Real-time Monitoring**: See current ES indexing status
- **Failed Queue Management**: View and retry failed indexing operations
- **Audit Logging**: All reindex operations are logged

**Key Services:**
- `ProductElasticsearchService`: Product indexing with error handling
- `CustomerElasticsearchService`: Customer indexing
- `SupplierElasticsearchService`: Supplier indexing
- `FailedIndexQueue` model tracks: `entity_type`, `entity_id`, `error_message`, `retry_count`, `status`

**API Endpoints:**
- `GET /admin/miscellaneous/elasticsearch-status` - Get ES sync status
- `GET /admin/miscellaneous/failed-index-queue` - Get failed queue
- `POST /admin/miscellaneous/retry-failed-index` - Retry failed indexing

**Frontend Pages:**
- `/super-admin/elasticsearch-sync-status` - ES sync dashboard with failed queue

**Frontend Components:**
- `ElasticsearchSyncStatus.tsx` - Sync status dashboard with retry operations

### 1.12 SR Reports System

**Location:** `app/models/sr_reports.py`, `app/api/sr_reports.py`, `app/services/sr/sr_reports_service.py`

This is a **comprehensive SR financial and operational reporting system** (Implemented April 1-3, 2026):

| Entity | Description |
|--------|-------------|
| **ProductDamage** | Damage incidents per product with date, quantity, reason, and damage cost tracking |
| **DailyCostExpense** | Daily operational expenses (van/fuel, oil changes, labour, office costs, miscellaneous) |
| **SalesLedger** | Manual Khata-style ledger entries for SR reconciliation and adjustments |
| **SalesBudget** | Sales targets and budget tracking per product group/category |

**ProductDamage Fields:**
- `sr_id`, `product_id`, `variant_id` - Links to SR and product
- `quantity_damaged` - Number of units damaged
- `damage_date` - Date of incident
- `reason` - Damage reason (transport, handling, defect, etc.)
- `damage_cost` - Financial impact of damage
- `description` - Additional details

**DailyCostExpense Fields:**
- `sr_id`, `cost_date` - SR and date
- `van_cost` - Van/vehicle rental or fuel
- `oil_cost` - Oil/maintenance costs
- `labour_cost` - Labour charges
- `office_cost` - Office/administrative costs
- `other_cost` - Miscellaneous costs
- `total_cost` - Sum of all costs
- `notes` - Remarks

**SalesLedger Fields:**
- `sr_id`, `ledger_date` - SR and date
- `description` - Transaction description
- `debit_amount`, `credit_amount` - Ledger amounts
- `ledger_type` - sales, return, adjustment, expense, commission, etc.
- `reference_id` - Link to source document
- `running_balance` - Balance after transaction

**SalesBudget Fields:**
- `sr_id`, `product_group_id` - SR and product group
- `budget_qty` - Target quantity
- `budget_amount` - Target amount in currency
- `period` - Month or period
- `year` - Budget year
- `achieved_qty`, `achieved_amount` - Actual achievement

**API Endpoints (35+ endpoints):**
```
POST/GET /sr-reports/damage              - Damage CRUD
GET /sr-reports/damage/report             - Filtered damage report
GET /sr-reports/damage/{id}               - Get single damage record
PATCH /sr-reports/damage/{id}             - Update damage
DELETE /sr-reports/damage/{id}            - Delete damage

POST/GET /sr-reports/daily-cost           - Daily cost CRUD
GET /sr-reports/cost-profit               - Aggregated cost/profit report
GET /sr-reports/cost-profit/{sr_id}       - SR-specific cost/profit

POST/GET /sr-reports/ledger               - Ledger (Khata) CRUD
GET /sr-reports/ledger/{ledger_id}        - Get single ledger entry
GET /sr-reports/reconciliation            - SR orders vs Khata reconciliation
GET /sr-reports/undelivery                - Undelivery analytics
GET /sr-reports/do-cash                   - DO cash tracking

POST/GET /sr-reports/budget               - Budget CRUD
GET /sr-reports/group-report              - Group-wise analytics
GET /sr-reports/do-tracking               - Delivery order tracking
GET /sr-reports/slow-moving               - Slow-moving inventory analysis
GET /sr-reports/daily-report              - Consolidated daily report
```

**Key Services:**
- `SRReportsService` - Damage, cost, ledger, budget CRUD and report generation
- Methods include: `record_damage()`, `calculate_daily_cost()`, `reconcile_ledger()`, `get_slow_moving_items()`, `calculate_group_performance()`

**Frontend Pages:**
- `/reports/damage` - Record and manage product damage with edit/delete capability
- `/reports/cost-profit` - Daily operational costs with cost tracking and editing
- `/reports/daily` - Consolidated daily sales report
- `/reports/budget` - Sales budget setup and tracking
- `/reports/reconciliation` - SR orders vs Khata (manual ledger) reconciliation
- `/reports/do-tracking` - Delivery order tracking and status
- `/reports/ledger` - Ledger (Khata) CRUD with date/type filtering
- `/reports/slow-moving` - Slow-moving inventory analysis
- `/reports/group` - Group-wise sales analytics and performance

**Frontend Components:**
- `DamageReport.tsx` - Damage recording and management
- `CostProfitReport.tsx` - Cost tracking and profit analysis
- `DailyReport.tsx` - Comprehensive daily consolidated view
- `BudgetManagement.tsx` - Budget creation and tracking
- `ReconciliationReport.tsx` - SR vs Khata reconciliation interface
- `DOTrackingReport.tsx` - Delivery order status tracking
- `LedgerManagement.tsx` - Manual ledger entry and management
- `SlowMovingReport.tsx` - Slow-moving product analysis
- `GroupReport.tsx` - Group-wise performance metrics

### 1.13 SR Program Workflow

**Location:** `app/models/sr_program.py`, `app/api/sr_program_admin.py`, `app/services/sr/sr_program_service.py`

This is a **channel-based SR program management system** (Implemented April 1-3, 2026):

| Entity | Description |
|--------|-------------|
| **SRProgramChannel** | Channel master defining sales channels (Muslim Bakary, Traders, Auto, etc.) |
| **SRProgramCustomerChannel** | Mapping of customers to specific sales channels |

**SRProgramChannel Fields:**
- `channel_name` - Channel identifier (Muslim Bakary, Traders, Auto, etc.)
- `description` - Channel description
- `is_active` - Active/inactive status
- `created_at`, `updated_at` - Timestamps

**SRProgramCustomerChannel Fields:**
- `customer_id` - Customer in the channel
- `channel_id` - Assigned channel
- `assigned_date` - When customer was assigned
- `is_active` - Active assignment

**API Endpoints:**
```
GET /sr-program/channels                         - List all channels
POST /sr-program/channels                        - Create channel
GET /sr-program/channels/{channel_id}            - Get channel details
PATCH /sr-program/channels/{channel_id}          - Update channel
DELETE /sr-program/channels/{channel_id}         - Delete channel

GET /sr-program/channels/mappings                - List all customer-channel mappings
POST /sr-program/channels/mappings               - Create mapping
POST /sr-program/channels/mappings/bulk          - Bulk assign channels

GET /sr-program/channels/unmapped-customers      - Find customers without channel assignment
```

**SR Program Workflow Dashboard:**
A 7-block workflow visualization showing:
1. **Pending Orders** - SR orders awaiting consolidation
2. **Channel Performance** - By-channel sales metrics
3. **Customer Assignment** - Channel allocation status
4. **Budget Tracking** - Budget vs actual by channel
5. **Damage Summary** - Product damage incidents
6. **Cost Analysis** - Daily operational costs
7. **Slow Movers** - Slow-moving items by channel

**Frontend Pages:**
- `/reports/sr-program` - SR Program Workflow dashboard with 7-block visualization
- `/reports/sr-program/admin` - Channel management and customer-channel mapping interface

**Frontend Components:**
- `SRProgramWorkflow.tsx` - Dashboard showing 7-block workflow with metrics
- `SRProgramChannelAdmin.tsx` - Channel CRUD and customer mapping UI

### 1.14 Inventory Reports (10 Types)

**Location:** `app/api/reports.py`, `app/services/reports_inventory.py`, `shoudagor_FE/src/pages/reports/inventory/`

This is a **comprehensive inventory analytics system** extending the existing 28 reports with 10 specialized inventory-focused reports (Implemented April 1-3, 2026):

#### Inventory Report Types

| Report | Purpose | Key Metrics |
|--------|---------|-------------|
| **Warehouse Summary** | Stock position per warehouse/location | Total qty, value, occupancy %, turnover |
| **Inventory Valuation** | Financial inventory valuations (FIFO/LIFO/WAC) | Total value, method comparison |
| **DSI/GMROI** | Days Sales of Inventory & Gross Margin ROI | DSI days, GMROI %, efficiency metrics |
| **Dead Stock** | Zero-movement inventory identification | Zero-qty items, age analysis, value |
| **Safety Stock** | Reorder points and safety stock levels | Safety qty, reorder points, min stock |
| **Stock by Batch** | Inventory stock grouped by batches | Qty per batch, unit cost, age, location |
| **Inventory Aging (Batch)** | Batch-based aging in buckets | 0-30, 31-60, 61-90, 91-180, 180+ days |
| **COGS by Period** | Cost of Goods Sold analysis | COGS by month/quarter, trends |
| **Margin Analysis** | Selling price vs batch cost | Margin per batch, margin % by product |
| **Batch P&L** | Per-batch profit and loss | Revenue, COGS, profit per batch |

**API Endpoints:**
```
GET /reports/inventory/warehouse-summary    - Warehouse/location stock position
GET /reports/inventory/valuation            - Inventory financial valuation
GET /reports/inventory/dsi-gmroi            - DSI & GMROI metrics
GET /reports/inventory/dead-stock           - Zero-movement items
GET /reports/inventory/safety-stock         - Reorder & safety stock
GET /reports/inventory/stock-by-batch       - Stock drill-down by batch
GET /reports/inventory/inventory-aging-batch - Batch aging buckets
GET /reports/inventory/cogs-by-period       - COGS analysis by period
GET /reports/inventory/margin-analysis      - Margin analytics
GET /reports/inventory/batch-pnl            - Per-batch P&L
```

**Frontend Pages:**
- `/reports/inventory/warehouse-summary` - Warehouse stock position visualization
- `/reports/inventory/valuation` - Inventory valuation with method selection
- `/reports/inventory/dsi-gmroi` - Days Sales of Inventory & GMROI metrics
- `/reports/inventory/dead-stock` - Dead stock identification
- `/reports/inventory/safety-stock` - Safety stock analysis
- `/reports/inventory/stock-by-batch` - Batch-level stock drill-down
- `/reports/inventory/inventory-aging-batch` - Batch aging report with aging buckets
- `/reports/inventory/cogs-by-period` - COGS by period visualization
- `/reports/inventory/margin-analysis` - Margin analysis dashboard
- `/reports/inventory/batch-pnl` - Batch profit and loss analysis

**Frontend Components:**
- `WarehouseSummary.tsx` - Warehouse stock position
- `InventoryValuation.tsx` - Valuation report with calculations
- `DSIGmroi.tsx` - DSI and GMROI metrics
- `DeadStock.tsx` - Dead stock analysis
- `SafetyStock.tsx` - Safety stock levels
- `StockByBatch.tsx` - Batch-level stock detail
- `InventoryAgingBatch.tsx` - Batch aging analysis
- `COGSByPeriod.tsx` - COGS by period breakdown
- `MarginAnalysis.tsx` - Margin analysis
- `BatchPnL.tsx` - Batch P&L analysis

### 1.15 Background Jobs

**Location:** `app/services/inventory/consistency_job.py`, `app/services/notification/notification_scheduler.py`

The system includes **background jobs** for automated operations:

**Consistency Job:**
- `initialize_consistency_job`: Sets up hourly consistency checks
- `get_consistency_job`: Retrieves job status
- Runs hourly to verify batch vs inventory_stock consistency

**Notification Scheduler:**
- `NotificationScheduler`: Background processing for notifications
- Scheduled notification delivery and cleanup

**Materialized View Service:**
- `MaterializedViewRefreshService`: Manages materialized view refresh for optimized queries

### 1.16 Employee Management

**Location:** `app/models/security.py`, `app/api/security.py` (referenced in frontend)

The **Employee Management** system provides comprehensive user/employee handling:

| Entity | Description |
|--------|-------------|
| **Employee** | Employee records linked to users |
| **EmployeeRole** | Role assignments for employees |
| **EmployeeAttendance** | Attendance tracking |

**Features (Frontend Implementation):**
- User management with employee profile
- Role-based access control
- Employee CRUD operations

**Frontend Pages (Implemented, routes currently commented):**
- `/users` - User/Employee list
- `/users/new` - Add new employee
- `/users/roles` - Role management

**Frontend Components:**
- `Users.tsx` - Employee list with management
- `Roles.tsx` - Role management interface
- `AddEmployee.tsx` - Add employee form

### 1.17 Incomplete Features (Planned)

**Location:** `src/pages/drafts/`, `src/pages/Quotations.tsx`, `src/pages/SalesReturns.tsx`

The following features have placeholder implementations and are marked as incomplete:

| Feature | Status | Description |
|---------|--------|-------------|
| **Sales Drafts** | INCOMPLETE | Draft sales orders that can be converted to completed sales |
| **Quotations** | INCOMPLETE | Price quotations for customers with validity periods |
| **Sales Returns** | INCOMPLETE | Customer returns and refunds management |

**Implementation Notes:**
- Routes are currently commented out in `App.tsx`
- Frontend components exist as placeholders with full implementation scaffolding
- Backend support exists via SalesOrder with `type` field ('draft', 'quotation', 'sale')
- Full implementation would require backend API endpoints and form components

### 1.18 Pending Customer Workflow (NEW)

**Location:** `app/models/sales.py` (PendingCustomer), `app/api/sr/pending_customer.py`, `app/services/sr/pending_customer_service.py`, `shoudagor_FE/src/lib/api/pendingCustomerApi.ts`

This feature allows **Sales Representatives** to submit new customer requests that require **admin approval** before being added to the system:

| Entity | Description |
|--------|-------------|
| **PendingCustomer** | SR-submitted customer data with approval workflow |

**PendingCustomer Fields:**
- `customer_name`, `customer_code` - Customer identification
- `contact_person`, `phone`, `email` - Contact information
- `address`, `country_id`, `state_id`, `city_id` - Address details
- `beat_id` - Assigned beat/territory
- `sr_id` - SR who submitted the request
- `status` - 'pending', 'approved', 'rejected'
- `reviewed_by` - Admin who processed the request
- `reviewed_at` - Timestamp of approval/rejection
- `rejection_reason` - Reason if rejected

**Workflow:**
1. SR submits new customer via mobile app (`POST /sales/sales-representative/pending-customers/`)
2. Admin views all pending customers (`GET /sales/sales-representative/admin/pending-customers/`)
3. Admin approves (creates actual Customer record) or rejects with reason
4. SR sees status update on their submitted customers

**API Endpoints:**
```
# SR Operations
GET  /sales/sales-representative/pending-customers/     - List my pending customers
POST /sales/sales-representative/pending-customers/     - Submit new customer
GET  /sales/sales-representative/pending-customers/{id} - Get specific submission
PATCH /sales/sales-representative/pending-customers/{id} - Update my submission
DELETE /sales/sales-representative/pending-customers/{id} - Cancel my submission

# Admin Operations
GET  /sales/sales-representative/admin/pending-customers/     - List all pending (admin)
GET  /sales/sales-representative/admin/pending-customers/{id}   - Get specific (admin)
POST /sales/sales-representative/admin/pending-customers/{id}/approve - Approve customer
POST /sales/sales-representative/admin/pending-customers/{id}/reject  - Reject customer
```

**Frontend Pages:**
- `/sr/pending-customers` - SR view for submitting/managing pending customers
- Admin approval interface in SR management section

**Frontend API:**
- `pendingCustomerApi.ts` - Full CRUD for SR operations, approval/rejection for admin

### 2. Sales Management

**Location:** `app/models/sales.py`, `app/api/sales/`, `app/services/sales/`

| Entity | Description |
|--------|-------------|
| **Customer** | Customer with balance tracking, beat assignment, credit limit, store credit |
| **Beat** | Geographic/route grouping for customers |
| **SalesOrder** | Sales transaction with status tracking, consolidation support, DSR loading |
| **SalesOrderDetail** | Line items with shipped_quantity, returned_quantity, SR pricing |
| **SalesOrderDeliveryDetail** | Delivery tracking |
| **SalesOrderPaymentDetail** | Payment tracking |
| **ClaimLog** | Promotional benefits applied to sales (captured in SalesOrderDetail) |

**Frontend Pages:**
- `/sales` - Sales orders list with DSR info, consolidation status
- `/sales/new` - Create sales order with automated scheme evaluation
- `/sales/pos` - Point of Sale interface
- `/customers`, `/customers/beats`, `/customers/dues`
- `/sales/deliveries` - Process deliveries via `UnifiedDeliveryForm`

### 3. Sales Representative (SR) Module

**Location:** `app/models/sales.py` (SR_Order, SR_Order_Detail), `app/api/sr/`, `app/services/sr/`

This is a **key differentiator** - manages mobile sales force:

| Entity | Description |
|--------|-------------|
| **SalesRepresentative** | Field sales person with user link, commission tracking |
| **SR_Order** | Order placed by SR (not yet converted to sales) |
| **SR_Order_Detail** | Line items with negotiated_price, sale_price, shipped/returned quantities |
| **SR_Product_Assignment** | Products an SR can sell |
| **Customer_SR_Assignment** | Customers assigned to SRs |
| **CustomerPhoneSuggestion** | SR-submitted customer phone updates (pending/approved/rejected) |
| **SRDisbursement** | Commission payment records |

**SR Order Flow:**
```
SR_Order (Draft) → Validation → Consolidation → SalesOrder (Finalized)
                                    ↓
                              Stock Deduction
                                    ↓
                              Invoice Generation
```

**Key Service:** `ConsolidationService` (`app/services/consolidation_service.py`)
- Validates SR orders for consolidation
- Checks stock availability at selected location
- Creates consolidated sales order WITHOUT aggregating same product variants from different SRs
- Each SR order detail becomes a separate line item in the consolidated sales order
- Preserves individual SR details in JSONB columns (`sr_order_detail_ids`, `sr_details`)
- Links SR order details to sales order details
- Handles transaction rollback on errors
- Supports final price adjustments during consolidation

**Frontend Pages (SR Role):**
- `/sr/orders` - SR's orders
- `/sr/orders/new` - Create SR order
- `/sr/products` - Assigned products
- `/sr/customers` - Assigned customers
- `/sr/phone-suggestions` - Submit phone number corrections

**Frontend Pages (Admin):**
- `/sales-representatives` - Manage SRs
- `/sales-representatives/all-orders` - View all SR orders
- `/sales-representatives/consolidated` - Consolidated orders with detailed SR breakdown
- `/sales-representatives/unconsolidated` - Pending consolidation
- `/sales-representatives/commissions` - Undisbursed commissions
- `/sales-representatives/disbursement-history` - Disbursement records

**Consolidated SR Order Details View:**
- `ViewConsolidatedSROrderDetails.tsx` - Modal component showing:
  - Grouped product/variant display with expandable SR details
  - Individual SR contributions per line item
  - Price adjustments per SR
  - Total price adjustment calculation
  - List of all consolidated SR orders

### 4. Delivery Sales Representative (DSR) Module

**Location:** `app/models/sales.py`, `app/models/warehouse.py`, `app/api/dsr/`, `app/services/dsr/`

This module manages the **delivery workforce** who physically deliver goods:

| Entity | Description |
|--------|-------------|
| **DeliverySalesRepresentative** | Delivery person with user link, payment_on_hand, commission |
| **DSRSOAssignment** | Links Sales Orders to DSRs for delivery (assigned/in_progress/completed) |
| **DSRPaymentSettlement** | Records when admin collects payments from DSR |
| **DSRStorage** | Virtual storage location for DSR (one-to-one with DSR) |
| **DSRInventoryStock** | Stock held in DSR's storage/van |
| **DSRStockTransfer** | Transfers between warehouse and DSR storage |
| **DSRStockTransferDetail** | Line items in DSR stock transfers |

**DSR Workflow:**
```
SalesOrder (Created) → DSR Assignment → Load Stock (DSRStorage)
                            ↓
                    DSR Delivers to Customer
                            ↓
                    Collect Payment (payment_on_hand increases)
                            ↓
                    Admin Settlement (payment_on_hand decreases)
```

**Frontend Pages (Admin):**
- `/dsr` - Manage DSRs
- `/dsr/new` - Add new DSR
- `/dsr/so-assignments` - Assign SOs to DSRs
- `/dsr/storage` - View DSR storages
- `/dsr/settlements` - Payment settlement history

**Super Admin Pages:**
- `/super-admin/dsr-storage` - Manage all DSR storages
- `/super-admin/dsr-storage/new` - Create DSR storage

**Frontend Pages (DSR Role):**
- `/dsr/my-assignments` - DSR's assigned orders
- `/dsr/my-inventory` - DSR's current inventory stock

### 5. Procurement Management

**Location:** `app/models/procurement.py`, `app/api/procurement/`, `app/services/procurement/`

| Entity | Description |
|--------|-------------|
| **Supplier** | Vendor with contact, payment terms |
| **PurchaseOrder** | Procurement transaction with delivery/payment status |
| **PurchaseOrderDetail** | Line items with quantity, received_quantity, returned_quantity, rejected_quantity |
| **ProductOrderDeliveryDetail** | Receiving tracking |
| **ProductOrderPaymentDetail** | Vendor payment tracking |

**Procurement Workflow:**
```
PurchaseOrder (Created) → Partial/Full Delivery → Payment
           ↓                      ↓
      Rejection            Stock Addition
           ↓
       Return
```

**Key computed property:** `effective_total_amount` calculates:
```python
effective_qty = quantity - returned_quantity - rejected_quantity
total = sum(effective_qty * unit_price for each detail)
```

**Frontend Pages:**
- `/purchases`, `/purchases/new` - Includes automated scheme evaluation for purchases
- `/suppliers`, `/suppliers/new`

**Frontend Forms:**
- `PurchaseForm.tsx` - Create/edit purchase orders
- `UnifiedDeliveryForm.tsx` - Handles both Billable and Free quantities for deliveries and rejections
- `PurchaseReturnForm.tsx` - Process returns including free quantity reconciliation
- `PurchasePaymentForm.tsx` - Record payments

### 6. Warehouse & Inventory Stock

**Location:** `app/models/warehouse.py`, `app/api/warehouse/`, `app/services/warehouse/`

| Entity | Description |
|--------|-------------|
| **Warehouse** | Physical warehouse location |
| **StorageLocation** | Specific storage area within warehouse |
| **InventoryStock** | Current stock level per product/variant/location |
| **StockTransfer** | Movement between storage locations |
| **StockTransferDetails** | Transfer line items |
| **DSRStorage** | Virtual storage for DSR (linked one-to-one) |
| **DSRInventoryStock** | Stock in DSR storage |
| **DSRStockTransfer** | Transfers to/from DSR storage |
| **DSRStockTransferDetail** | DSR transfer line items |
| **StockLog** | Comprehensive movement log with EPP and running balance |
| **StockLogBatch** | FIFO-based cost batches for inventory valuation |

**Inventory Stock Log & EPP Tracking:**
**Location:** `app/services/transaction/stock_log_service.py`
- **StockLog**: Captures every movement (IN/OUT) with a mandatory `unit_cost` (EPP).
- **Effective Purchase Price (EPP)**: The net cost basis for an item, factoring in discounts and free quantities.
- **FIFO Logic**: `StockLogBatch` ensures that stock is consumed in the order it was received for accurate COGS (Cost of Goods Sold) calculation.

**Inventory Transactions** (`app/models/transaction.py`):
- `InventoryTransaction` - All stock movements logged
- `InventoryAdjustment` - Stock corrections with approval

**Frontend Pages:**
- `/warehouse/inventory` - Stock levels
- `/warehouse/inventory-stock/transfer` - Transfer stock
- `/warehouse/inventory-stock/adjustment` - Adjust stock
- `/warehouses/storage-locations`

### 7. Billing & Invoices

**Location:** `app/models/billing.py`, `app/api/billing/`, `app/services/billing/`

| Entity | Description |
|--------|-------------|
| **Invoice** | Generated from sales order with subtotal, discounts, taxes, payment status |
| **InvoiceDetail** | Invoice line items with original_unit_price, unit_price, discount, tax |
| **Expense** | Business expense tracking with category, payment method |

**Invoice Fields:**
- `subtotal` - Sum before discounts
- `discount_amount`, `discount_type` - Discount tracking
- `total_amount` - Final amount
- `tax_amount` - Tax applied
- `status` - Draft/Issued/Paid/Cancelled
- `payment_status` - Unpaid/Partial/Paid

**Frontend Pages:**
- `/invoices` - Invoice list
- `/expenses`, `/expenses/new`

### 8. Reports Module

**Location:** `app/services/reports.py`, `app/api/reports.py`, `app/schemas/reports.py`, `app/repositories/reports/`

| Report | Description |
|--------|-------------|
| **Inventory KPI Ribbon** | Aggregated inventory metrics using LIFO costing |
| **FIFO Aging** | Inventory aging buckets (0-30, 31-60, 61-90, 90+ days) with COGS data |
| **Current Stock** | Stock with timeline, financial metrics per product/variant |
| **Purchase Order Report** | Comprehensive PO analytics by year or date range |

#### Sales Reports (New)
| Report | Description |
|--------|-------------|
| **Fulfillment Report** | Order fulfillment metrics and delivery performance |
| **Financial Report** | Profitability and financial analysis |
| **Inventory Performance** | Inventory turnover and performance metrics |
| **Sales Team Analytics** | SR/DSR performance and productivity |
| **Advanced Insights** | Deep analytics and business insights |
| **Product Sales Analysis** | Product-wise sales breakdown |
| **Territory Performance** | Geographic/beat-wise performance |
| **Customer Activity** | Customer engagement and activity |
| **Pipeline Analysis** | Sales pipeline visibility |
| **Demand Forecast** | AI-powered demand predictions |

#### Purchase Order Reports (New)
| Report | Description |
|--------|-------------|
| **Maverick Spend** | Off-contract purchasing analysis |
| **Invoice Variance** | PO vs Invoice price differences |
| **Emergency Orders** | Urgent procurement analysis |
| **Cash Flow Projection** | PO payment timeline forecasting |
| **ABC/XYZ Classification** | Spend categorization |
| **Supplier Consolidation** | Supplier concentration analysis |
| **PO Progress** | Purchase order status tracking |
| **Uninvoiced Receipts** | Goods received but not invoiced |

#### Inventory Reports (New)
| Report | Description |
|--------|-------------|
| **Warehouse Summary** | Warehouse-wise stock overview |
| **Inventory Valuation** | Stock valuation report |
| **DSI/GMROI** | Inventory efficiency metrics |
| **Dead Stock** | Slow-moving inventory identification |
| **Safety Stock** | Safety stock level analysis |
| **Stock by Batch** | Inventory stock grouped by batches with quantity, cost, age, and location |
| **Inventory Aging (Batch)** | Inventory aging based on actual batch received dates (0-30, 31-60, 61-90, 91-180, 180+ days) |
| **COGS by Period** | Cost of Goods Sold grouped by month and product |
| **Margin Analysis** | Selling price vs batch cost analysis |
| **Batch P&L** | Per-batch profit and loss analysis |

**Report Methods in `ReportsService`:**
- `get_inventory_kpi_ribbon_data()` - LIFO-based inventory metrics
- `calculate_fifo_aging()` - FIFO aging buckets and COGS
- `get_current_stock()` - Stock with financial timeline
- `get_purchase_order_report()` - PO analytics

**Frontend Pages:**
- `/reports` - Reports dashboard
- `/reports/inventory` - Inventory reports
  - `/reports/inventory/warehouse-summary`
  - `/reports/inventory/valuation`
  - `/reports/inventory/dsi-gmroi`
  - `/reports/inventory/dead-stock`
  - `/reports/inventory/safety-stock
│   │   │   │   │   ├── /reports/inventory/stock-by-batch (NEW)
│   │   │   │   │   ├── /reports/inventory/inventory-aging-batch (NEW)
│   │   │   │   │   ├── /reports/inventory/cogs-by-period (NEW)
│   │   │   │   │   ├── /reports/inventory/margin-analysis (NEW)
│   │   │   │   │   └── /reports/inventory/batch-pnl (NEW)`
- `/reports/purchaseorder` - Purchase order reports
  - `/reports/purchaseorder/maverick-spend`
  - `/reports/purchaseorder/variance`
  - `/reports/purchaseorder/emergency-orders`
  - `/reports/purchaseorder/cash-flow`
  - `/reports/purchaseorder/classification`
  - `/reports/purchaseorder/consolidation`
  - `/reports/purchaseorder/progress`
  - `/reports/purchaseorder/uninvoiced`
- `/reports/sales/` - Sales reports
  - `/reports/sales/fulfillment`
  - `/reports/sales/profitability`
  - `/reports/sales/inventory-performance`
  - `/reports/sales/team-performance`
  - `/reports/sales/advanced`
  - `/reports/sales/product-analysis`
  - `/reports/sales/territory-performance`
  - `/reports/sales/customer-activity`
  - `/reports/sales/pipeline-analysis`
  - `/reports/sales/demand-forecast`

### 9. Security & Multi-Tenancy

**Location:** `app/models/security.py`, `app/api/security.py`, `app/services/security.py`

| Entity | Description |
|--------|-------------|
| **AppClient** | Top-level tenant (business) |
| **AppClientCompany** | Company under a client (multi-company support) |
| **User** | System user (linked to SR or DSR if applicable) |
| **UserCategory** | Role/permission group with `accessible_modules` JSON field |
| **Module/SubModule/Section/Screen** | Navigation hierarchy |
| **UserCategoryWiseScreen** | Permission per role |
| **UserWiseScreen** | Per-user permission overrides |
| **UserCompanyAccess** | Multi-company access per user |

**UserCategory Fields:**
- `accessible_modules` - JSON field storing module access configuration for role-based navigation

**Authentication Flow:**
1. Login → Get token + user info + company context
2. All requests include company_id context
3. All queries filter by company_id (tenant isolation)

**Role Guards (Frontend):**
- `PrivateRoute` - Requires authentication
- `AdminRoute` - Requires admin role
- `SuperAdminRoute` - Requires super admin role
- `SRRoute` - Requires SR role
- `DSRRoute` - Requires DSR role

### 10. Test Account Onboarding

**Location:** `shoudagor_FE/src/components/auth/TestAccountOnboardingGate.tsx`, `app/api/test_user_basic_info.py`

**Purpose:** Collects basic information from test account users on first login to improve user experience and gather feedback.

**Features:**
- Browser-based identification using localStorage
- Modal gate that appears on first login for test accounts
- Backend API to check onboarding status
- Prevents repeated prompts once information is provided
- Non-intrusive for production accounts

**Implementation:**
- `TestAccountOnboardingGate` - Wrapper component that checks onboarding status
- `TestAccountOnboardingModal` - Modal form for collecting user information
- `testUserBasicInfoApi` - API client for onboarding endpoints
- localStorage key: `shoudagor_onboarding_provided_on_this_browser`

---

## 🔍 Elasticsearch Integration

**Location:** `app/services/product_elasticsearch_service.py`, `app/services/customer_elasticsearch_service.py`, `app/services/supplier_elasticsearch_service.py`

### Purpose

Elasticsearch provides **fast, fuzzy search** for:
- **Products & Variants** - Including nested variants, prices, and stock levels
- **Customers** - For quick customer lookup
- **Suppliers** - For procurement workflows

### Key Service: `ProductElasticsearchService`

| Method | Purpose |
|--------|---------|
| `search_products()` | Full-text search with nested field filtering |
| `search_by_sku()` | Dedicated SKU search with fuzzy/partial matching |
| `index_product()` | Index single product with all nested data |
| `index_all_products()` | Bulk reindex all products |
| `delete_product()` | Remove from index |
| `delete_index()` | Delete entire index (reindex scenario) |

### Index Structure

The `products` index uses **nested mappings** for:
- `variants` - Variant details, SKU, barcode
- `prices` - Price history with effective dates
- `stocks` - Inventory levels per location

### Usage Pattern

```python
# In API endpoint
service = ProductElasticsearchService.get_instance()
results = service.search_products(
    query="laptop",
    limit=20,
    filters={"company_id": 1, "category_id": 5}
)
```

### Configuration

Elasticsearch connection configured in `app/core/elasticsearch_config.py`

---

## 🪝 Frontend Hooks

**Location:** `src/hooks/`

| Hook | Purpose | File |
|------|---------|------|
| `useAuth` | Access auth context | `useAuth.ts` |
| `useDebounce` | Debounce inputs for search | `useDebounce.ts` |
| `usePagination` | Pagination state management | `use-pagination.ts` |
| `usePaginationHook` | Alternative pagination | `use-pagination-hook.ts` |
| `useFilter` | Filter state management | `use-filter.ts` |
| `useMobile` | Mobile viewport detection | `use-mobile.ts` |
| `useDevice` | Device type detection | `use-device.ts` |
| `useSliderWithInput` | Slider + input sync | `use-slider-with-input.ts` |
| `useBookmarks` | Access bookmarks context | `useBookmarks.ts` |
| `useSettings` | Access settings context | `useSettings.ts` |
| `useFreezeRefresh` | Prevent query refetch | `useFreezeRefresh.ts` |

### Common Hook Usage

```typescript
// Debounced search
const [search, setSearch] = useState('');
const debouncedSearch = useDebounce(search, 300);

// Pagination
const { page, limit, setPage, offset } = usePagination();

// Mobile detection
const isMobile = useMobile();
```

---

## 🔄 Common Patterns

### Backend Development Patterns

#### 1. Creating a New Feature (Full Stack)

```
1. Model (app/models/{domain}.py)
   └── Define SQLAlchemy class with mixins
   
2. Schema (app/schemas/{domain}/)
   └── Create Pydantic schemas: {Entity}Create, {Entity}Update, {Entity}Read
   
3. Repository (app/repositories/{domain}/)
   └── Implement data access methods
   
4. Service (app/services/{domain}/)
   └── Implement business logic
   
5. API (app/api/{domain}/)
   └── Define FastAPI router with endpoints
   
6. Migration (alembic/)
   └── alembic revision --autogenerate -m "description"
```

#### 2. Effective Trading Price (Eff. TP)
**Used in Sales/Procurement Details** to calculate the net price per item:
```python
@property
def effective_tp(self):
    total_qty = (self.quantity or 0) + (self.free_quantity or 0)
    gross_price = (self.quantity or 0) * (self.unit_price or 0)
    discount = (self.discount_amount or 0)
    return float((gross_price - discount) / total_qty) if total_qty > 0 else 0.0
```

#### 3. Stock Movement Logging (FIFO)
**Location:** `app/services/transaction/stock_log_service.py`
- **IN movements**: Create a new `StockLogBatch` with `remaining_quantity = original_quantity` and `unit_cost = EPP`.
- **OUT movements**: Allocate the quantity across existing batches in chronological order (FIFO), reducing their `remaining_quantity`.
- **Audit**: Every `StockLog` entry contains `quantity_after` for point-in-time reconciliation.

#### 4. Pagination Pattern
# Repository
def get_all(self, start: int = 0, limit: int = 20, company_id: int = None):
    query = self.db.query(Model).filter(Model.is_deleted == False)
    if company_id:
        query = query.filter(Model.company_id == company_id)
    total = query.count()
    items = query.offset(start).limit(limit).all()
    return items, total
```

**Frontend:**
```typescript
const { data } = useQuery({
    queryKey: ['items', start, limit],
    queryFn: () => getItems(start, limit)
});
```

#### 5. Soft Delete Pattern

```python
# Never hard delete - always filter by is_deleted
def delete(self, id: int):
    item = self.db.query(Model).get(id)
    item.is_deleted = True
    self.db.commit()

# All queries must filter
query.filter(Model.is_deleted == False)
```

#### 6. Multi-Tenant Query Pattern

```python
# ALWAYS filter by company_id
def get_items(self, company_id: int):
    return self.db.query(Model).filter(
        Model.company_id == company_id,
        Model.is_deleted == False
    ).all()
```

### Frontend Development Patterns

#### 1. API Call Pattern

```typescript
// lib/api/exampleApi.ts
import { api } from '../api';
import { apiRequest } from '../queryClient';

export const getItems = (start?: number, limit?: number): Promise<ItemsResponse> => {
    const params = new URLSearchParams();
    if (start !== undefined) params.append("start", String(start));
    if (limit !== undefined) params.append("limit", String(limit));
    return apiRequest(api, `/items/?${params.toString()}`);
};

export const createItem = (data: InsertItem): Promise<Item> => 
    apiRequest(api, "/items/", { method: "POST", body: data });
```

#### 2. React Query Usage

```typescript
// List query
const { data, isLoading } = useQuery({
    queryKey: ['items', filters],
    queryFn: () => getItems(start, limit, filters)
});

// Mutation
const mutation = useMutation({
    mutationFn: createItem,
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['items'] });
        toast.success('Item created');
    }
});
```

#### 3. Form Pattern (React Hook Form + Zod)

```typescript
// Schema
const formSchema = z.object({
    name: z.string().min(1, "Required"),
    price: z.coerce.number().min(0)
});

// Form
const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", price: 0 }
});

const onSubmit = (values: z.infer<typeof formSchema>) => {
    mutation.mutate(values);
};
```

#### 4. Protected Route Pattern

```typescript
// components/PrivateRoute.tsx
const PrivateRoute = () => {
    const { user, isLoading } = useUser();
    if (isLoading) return <Loading />;
    if (!user) return <Navigate to="/login" />;
    return <Outlet />;
};
```

#### 5. Error Boundary Pattern

**Location:** `src/components/RouteErrorBoundary.tsx`

```typescript
// Catches routing and rendering errors
const RouteErrorBoundary = () => {
    const error = useRouteError();
    return (
        <div className="error-container">
            <h2>Something went wrong</h2>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
    );
};
```
```

---

## 📍 Quick Reference - Where to Find What

### Backend Locations

| To Find... | Look In |
|------------|---------|
| Database table definition | `app/models/{domain}.py` |
| API endpoint | `app/api/{domain}/` + check `app/main.py` for router registration |
| Business logic | `app/services/{domain}/` |
| Database queries | `app/repositories/{domain}/` |
| Input/Output validation | `app/schemas/{domain}/` |
| DB connection & session | `app/core/database.py` |
| App configuration | `app/core/config.py` |
| JWT authentication | `app/core/security.py` |
| Event listeners (auto-update stock) | `app/subscribers/` |
| Database migrations | `alembic/versions/` |
| DSR logic | `app/api/dsr/`, `app/services/dsr/`, `app/schemas/dsr/` |
| SR logic | `app/api/sr/`, `app/services/sr/`, `app/schemas/sr/` |
| SR Reports (NEW - April 2026) | `app/models/sr_reports.py`, `app/api/sr_reports.py`, `app/services/sr/sr_reports_service.py` |
| SR Program Workflow (NEW - April 2026) | `app/models/sr_program.py`, `app/api/sr_program_admin.py`, `app/services/sr/sr_program_service.py` |
| Claims logic | `app/api/claims.py`, `app/services/claims/`, `app/schemas/claims.py` |
| Reports logic | `app/services/reports.py`, `app/schemas/reports.py`, `app/repositories/reports/` |
| Inventory Reports (NEW - April 2026) | `app/api/reports.py` (10 endpoints), `app/services/reports_inventory.py` |
| Consolidation logic | `app/services/consolidation_service.py` |
| Claim/Scheme logic | `app/services/claims/claim_service.py` |
| Stock Logging / FIFO | `app/services/transaction/stock_log_service.py` |
| Batch logic | `app/models/batch_models.py`, `app/api/inventory/batch.py`, `app/services/inventory/batch_allocation_service.py` |
| Batch backfill | `app/services/inventory/backfill_service.py` |
| Stock to batch conversion | `app/services/inventory/stock_to_batch_service.py` |
| Batch reconciliation | `app/services/inventory/stock_consistency_service.py` |
| Inventory drift/sync | `app/services/inventory/inventory_sync_service.py`, `app/services/inventory/stock_consistency_service.py` |
| Inventory migration | `app/services/inventory/inventory_migration_service.py`, `app/services/inventory/backfill_service.py` |
| Notification logic | `app/services/notification/`, `app/api/notification.py` |
| Admin/Super Admin logic | `app/api/admin.py`, `app/api/admin_miscellaneous.py`, `app/services/admin/` |
| ES sync status | `app/models/admin.py` (FailedIndexQueue), `app/api/admin_miscellaneous.py` |
| Test account onboarding | `app/api/test_user_basic_info.py` |
| Admin SR Dashboard Service (NEW) | `app/services/sr/admin_sr_dashboard_service.py` - SR KPI aggregation |
| Admin DSR Dashboard Service (NEW) | `app/services/dsr/admin_dsr_dashboard_service.py` - DSR KPI aggregation |
| Pending Customer Service (NEW) | `app/services/sr/pending_customer_service.py` - Customer approval workflow |
| DSR Reports API (NEW) | `app/api/dsr_reports.py` - DSR summary, loading, SO breakdown |
| SR Program Workflow API (NEW) | `app/api/sr_program_admin.py` - Channel management |

### Frontend Locations

| To Find... | Look In |
|------------|---------|
| Page component | `src/pages/{domain}/` |
| Batch inventory pages | `src/pages/inventory/` |
| Claims pages | `src/pages/claims/` |
| Settings pages | `src/pages/settings/` |
| DSR pages | `src/pages/dsr/` |
| SR order pages | `src/pages/sr-orders/` |
| SR Reports Pages (NEW - April 2026) | `src/pages/reports/{DamageReport,CostProfitReport,DailyReport,BudgetManagement,ReconciliationReport,DOTrackingReport,LedgerManagement,SlowMovingReport,GroupReport}.tsx` |
| SR Program Workflow (NEW - April 2026) | `src/pages/reports/{SRProgramWorkflow,SRProgramChannelAdmin}.tsx` |
| Inventory Report Pages (10 types, NEW - April 2026) | `src/pages/reports/inventory/{WarehouseSummary,InventoryValuation,DSIGmroi,DeadStock,SafetyStock,StockByBatch,InventoryAgingBatch,COGSByPeriod,MarginAnalysis,BatchPnL}.tsx` |
| SR Price Management | `src/pages/sales-representatives/AdminSRPriceManagement.tsx`, `src/pages/sr-orders/SRPriceManagement.tsx` |
| Report pages | `src/pages/reports/` |
| Reusable form | `src/components/forms/` |
| UI building blocks | `src/components/ui/` (shadcn/ui) |
| API functions | `src/lib/api/{domain}Api.ts` |
| ES sync status | `src/pages/super-admin/ElasticsearchSyncStatus.tsx` |
| Employee management | `src/pages/employees/Users.tsx`, `src/pages/employees/roles/Roles.tsx` |
| Batch API | `src/lib/api/batchApi.ts` |
| Claims API | `src/lib/api/claimsApi.ts` |
| SR Reports API (NEW - April 2026) | `src/lib/api/srReportsApi.ts` |
| DSR API | `src/lib/api/dsrApi.ts`, `dsrInventoryStockApi.ts`, `dsrSettlementApi.ts`, `dsrStorageApi.ts` |
| Notification API | `src/lib/api/notificationApi.ts` |
| Dashboard API | `src/lib/api/dashboardApi.ts` |
| SR Price API | `src/lib/api/srProductAssignmentPriceApi.ts` |
| Phone Suggestion API | `src/lib/api/phoneSuggestionApi.ts` |
| Misc Admin API | `src/lib/api/miscAdminApi.ts` |
| Activity Config | `src/lib/dashboard/activityConfig.ts` |
| TypeScript types | `src/types/` or `src/lib/schema/` |
| React Context | `src/contexts/` |
| Custom hooks | `src/hooks/` |
| Route definitions | `src/App.tsx` |
| Global styles | `src/index.css` |
| API base config | `src/lib/api.ts` |
| Query client config | `src/lib/queryClient.ts` |
| Unified Delivery Form | `src/components/forms/UnifiedDeliveryForm.tsx` |
| Onboarding Gate | `src/components/auth/TestAccountOnboardingGate.tsx` |
| Product Image Gallery (NEW - April 2026) | `src/components/shared/ProductImageGallery.tsx` |
| Consolidated SR Order Details | `src/pages/sr-orders/ViewConsolidatedSROrderDetails.tsx` |
| Settings Context | `src/contexts/SettingsContext.tsx` |
| DraggableDashboard (NEW) | `src/components/draggable-dashboard.tsx` - Draggable widget layout |
| Admin SR Dashboard API (NEW) | `src/lib/api/adminSRDashboardApi.ts` - SR KPI data |
| Admin DSR Dashboard API (NEW) | `src/lib/api/adminDSRDashboardApi.ts` - DSR KPI data |
| DSR Reports API (NEW) | `src/lib/api/dsrReportsApi.ts` - DSR summary reports |
| SR Program Reports API (NEW) | `src/lib/api/srProgramReportsApi.ts` - Channel workflow |
| Pending Customer API (NEW) | `src/lib/api/pendingCustomerApi.ts` - Customer approval workflow |
| DSR Reports Page (NEW) | `src/pages/reports/DSRReports.tsx` - DSR performance reports |
| SR Program Workflow Page (NEW) | `src/pages/reports/SRProgramWorkflow.tsx` - 7-block workflow view |
| SR Program Admin Page (NEW) | `src/pages/reports/SRProgramChannelAdmin.tsx` - Channel management |

### Common Search Patterns

| To Find... | Search For |
|------------|------------|
| All endpoints for a resource | `@router.get`, `@router.post` in `app/api/` |
| Where an API is called from FE | Function name in `src/lib/api/` |
| Database constraint | `UniqueConstraint`, `ForeignKey` in `app/models/` |
| Pydantic validation rules | Class name in `app/schemas/` |
| Route guard/protection | `PrivateRoute`, `AdminRoute`, `SRRoute`, `DSRRoute` in `src/components/` |

### Key Files to Know

| File | Importance |
|------|------------|
| `Shoudagor/app/main.py` | App entry, all routers registered here |
| `Shoudagor/app/models/__init__.py` | All model imports for Alembic |
| `Shoudagor/app/core/database.py` | DB engine, session factory |
| `Shoudagor/alembic/env.py` | Migration configuration |
| `shoudagor_FE/src/App.tsx` | All routes, providers, app structure |
| `shoudagor_FE/src/lib/api.ts` | Base API client with auth headers |
| `shoudagor_FE/src/contexts/UserContext.tsx` | User auth state |
| `shoudagor_FE/src/contexts/SettingsContext.tsx` | Application settings state |
| `Shoudagor/app/services/consolidation_service.py` | SR order consolidation logic with multi-SR support |
| `Shoudagor/app/services/reports.py` | Reporting business logic |
| `Shoudagor/app/services/inventory/batch_allocation_service.py` | Batch allocation for sales orders |
| `Shoudagor/app/services/claims/claim_service.py` | Claims/schemes evaluation logic |
| `shoudagor_FE/src/pages/sr-orders/ViewConsolidatedSROrderDetails.tsx` | Detailed SR consolidation view |
| `shoudagor_FE/src/pages/settings/Settings.tsx` | Unified settings page |
| `Shoudagor/app/api/sr/customer_phone_suggestion.py` | Phone suggestion endpoints |
| `Shoudagor/app/services/sr/customer_phone_suggestion_service.py` | Phone suggestion business logic |
| `shoudagor_FE/src/pages/sales/PhoneNumberSuggestions.tsx` | Admin approval interface |
| `Shoudagor/app/api/inventory/product_variant_image.py` | Product image endpoints |
| `app/services/inventory/product_variant_image_service.py` | Image upload and S3 management |
| `shoudagor_FE/src/components/forms/PhoneSuggestionForm.tsx` | Phone suggestion form |
| `app/services/reports.py` | All 28 report implementations |
| `app/repositories/reports/` | Report-specific repository queries |
| `shoudagor_FE/src/pages/reports/` | All 28 report page components |
| `shoudagor_FE/src/lib/api/reportsApi.ts` | Report API functions |
| `shoudagor_FE/src/lib/dashboard/activityConfig.ts` | Activity type configuration (30+ types) |
| `Shoudagor/app/services/inventory/inventory_sync_service.py` | Centralized inventory sync with batch mode enforcement |
| `shoudagor_FE/src/pages/inventory/DriftApprovals.tsx` | Inventory drift approval workflow |
| `shoudagor_FE/src/pages/super-admin/ElasticsearchSyncStatus.tsx` | ES sync status monitoring |
| `Shoudagor/app/services/storage/s3_service.py` | S3 storage service for product images |
| `Shoudagor/app/models/sr_reports.py` | SR Reports models (ProductDamage, Cost, Ledger, Budget) - NEW April 2026 |
| `Shoudagor/app/api/sr_reports.py` | SR Reports API endpoints (35+) - NEW April 2026 |
| `Shoudagor/app/services/sr/sr_reports_service.py` | SR Reports business logic - NEW April 2026 |
| `Shoudagor/app/models/sr_program.py` | SR Program models (Channel, CustomerChannel) - NEW April 2026 |
| `Shoudagor/app/api/sr_program_admin.py` | SR Program API endpoints - NEW April 2026 |
| `Shoudagor/app/services/sr/sr_program_service.py` | SR Program business logic - NEW April 2026 |
| `shoudagor_FE/src/lib/api/srReportsApi.ts` | SR Reports API client (40+ functions) - NEW April 2026 |
| `shoudagor_FE/src/pages/reports/` | SR Reports pages and Inventory Reports pages (22 new) - NEW April 2026 |
| `shoudagor_FE/src/pages/reports/inventory/` | 10 Inventory Report pages - NEW April 2026 |
| `Shoudagor/app/services/sr/admin_sr_dashboard_service.py` | Admin SR Dashboard KPI aggregation - NEW April 2026 |
| `Shoudagor/app/services/dsr/admin_dsr_dashboard_service.py` | Admin DSR Dashboard KPI aggregation - NEW April 2026 |
| `Shoudagor/app/services/sr/pending_customer_service.py` | Pending Customer approval workflow - NEW April 2026 |
| `shoudagor_FE/src/lib/api/adminSRDashboardApi.ts` | Admin SR Dashboard API client - NEW April 2026 |
| `shoudagor_FE/src/lib/api/adminDSRDashboardApi.ts` | Admin DSR Dashboard API client - NEW April 2026 |
| `shoudagor_FE/src/lib/api/dsrReportsApi.ts` | DSR Reports API client - NEW April 2026 |
| `shoudagor_FE/src/lib/api/srProgramReportsApi.ts` | SR Program Reports API client - NEW April 2026 |
| `shoudagor_FE/src/lib/api/pendingCustomerApi.ts` | Pending Customer API client - NEW April 2026 |
| `shoudagor_FE/src/pages/reports/DSRReports.tsx` | DSR Reports page - NEW April 2026 |
| `shoudagor_FE/src/pages/reports/SRProgramWorkflow.tsx` | SR Program 7-block workflow dashboard - NEW April 2026 |
| `shoudagor_FE/src/components/draggable-dashboard.tsx` | Draggable dashboard layout component - NEW April 2026 |

---

##Recent Implementations Summary

### Backend Summary (March 31 - April 7, 2026)

**Total New Implementations Added (April 1-3, 2026):**
- **4 New Models** - SR Reports (ProductDamage, DailyCostExpense, SalesLedger, SalesBudget) + SR Program (SRProgramChannel, SRProgramCustomerChannel)
- **3 New Services** - SR Reports Service, SR Program Service, Inventory Reports Service
- **55+ New API Endpoints** - 35+ SR Reports endpoints, 9 SR Program endpoints, 10 Inventory Report endpoints
- **20+ New Pydantic Schemas** - All new SR Reports and SR Program schemas

**April Implementation Summary:**

| Feature | Models | Services | API Endpoints | Status |
|---------|--------|----------|---------------|--------|
| **SR Reports System** | 4 | 1 | 35+ | ✅ 100% |
| **SR Program Workflow** | 2 | 1 | 9 | ✅ 100% |
| **Inventory Reports (10 types)** | - | 1 | 10 | ✅ 100% |
| **Product Image Gallery** | - | - | - | ✅ 100% |
| **Bulk SR Order Approval** | - | - | - | ✅ 100% |

### Backend Summary (April 7-15, 2026)

**Total New Implementations Added (April 7-15, 2026):**
- **2 New Services** - Admin SR Dashboard Service, Admin DSR Dashboard Service, Pending Customer Service
- **10+ New API Endpoints** - SR Dashboard Summary, DSR Dashboard Summary, DSR Reports (3), Pending Customer (6)
- **5 New Frontend API Files** - adminSRDashboardApi, adminDSRDashboardApi, dsrReportsApi, srProgramReportsApi, pendingCustomerApi

**April 7-15 Implementation Summary:**

| Feature | Models | Services | API Endpoints | Status |
|---------|--------|----------|---------------|--------|
| **Admin SR Dashboard KPIs** | - | 1 | 1 | ✅ 100% |
| **Admin DSR Dashboard KPIs** | - | 1 | 1 | ✅ 100% |
| **Pending Customer Workflow** | 1 | 1 | 10 | ✅ 100% |
| **DSR Reports** | - | - | 3 | ✅ 100% |
| **SR Program Reports API** | - | - | 1 | ✅ 100% |
| **DraggableDashboard Component** | - | - | - | ✅ 100% |

### Frontend Summary (April 1-3, 2026)

**New Pages Added:**
- **SR Reports Pages (9):** DamageReport, CostProfitReport, DailyReport, BudgetManagement, ReconciliationReport, DOTrackingReport, LedgerManagement, SlowMovingReport, GroupReport
- **SR Program Pages (2):** SRProgramWorkflow, SRProgramChannelAdmin
- **Inventory Report Pages (10):** WarehouseSummary, InventoryValuation, DSIGmroi, DeadStock, SafetyStock, StockByBatch, InventoryAgingBatch, COGSByPeriod, MarginAnalysis, BatchPnL
- **DSR Report Page (1):** DSRReports

**New Components & UI:**
- Extended API client with `srReportsApi.ts` (40+ functions)
- ProductImageGallery with S3 integration and drag-and-drop
- Bulk selection in UnconsolidatedSROrders

**Routes Added (22):**
- `/reports/damage`, `/reports/cost-profit`, `/reports/daily`, `/reports/budget`
- `/reports/reconciliation`, `/reports/do-tracking`, `/reports/ledger`, `/reports/slow-moving`, `/reports/group`
- `/reports/sr-program`, `/reports/sr-program/admin`, `/reports/dsr`
- `/reports/inventory/warehouse-summary`, `/reports/inventory/valuation`, `/reports/inventory/dsi-gmroi`
- `/reports/inventory/dead-stock`, `/reports/inventory/safety-stock`
- `/reports/inventory/stock-by-batch`, `/reports/inventory/inventory-aging-batch`
- `/reports/inventory/cogs-by-period`, `/reports/inventory/margin-analysis`, `/reports/inventory/batch-pnl`

### Frontend Summary (April 7-15, 2026)

**New Components & API Files:**
- **Admin Dashboard KPI Components:** DraggableDashboard with persistence, DateRangePicker
- **5 New API Files:** `adminSRDashboardApi.ts`, `adminDSRDashboardApi.ts`, `dsrReportsApi.ts`, `srProgramReportsApi.ts`, `pendingCustomerApi.ts`
- **Dashboard Enhancements:** KPI widgets, top performers leaderboards, activity monitoring

**New & Enhanced Pages:**
- `/` (Admin Dashboard) - Enhanced with draggable KPI widgets
- `/reports/dsr` - DSR performance reports (enhanced)
- `/reports/sr-program` - 7-block workflow visualization
- `/sr/pending-customers` - SR customer submission workflow

**New Routes:**
- SR Program Workflow routes with channel management
- Pending Customer approval workflow routes

### Historical Backend Summary (Through March 31)

**Total Implementations (Through March 31):**
- **35+ Models** - Including batch, DSR, claims, notifications, and transaction models
- **50+ Services** - Organized by business domain with clear separation of concerns
- **100+ API Endpoints** - Across 10+ major business domains
- **80+ Pydantic Schemas** - Request/response validation for all endpoints
- **40+ Repositories** - Data access abstraction layer mirroring service structure

**Major Components Added:**
1. Batch-Based Inventory System (8 services, 21+ API endpoints)
2. SR Order Consolidation (1 core service, 4 endpoints)
3. DSR Management (3 services, 18+ endpoints)
4. Claims & Schemes (3 services, 14 endpoints)
5. Notifications (3 services, 6 endpoints)
6. Advanced Reports (1 service, 20+ endpoints)
7. Admin/Onboarding (2 services, 10+ endpoints)
8. Phone Suggestions (1 service, 6 endpoints)
9. Product Images (1 service, 8+ endpoints)
10. Elasticsearch Integration (3 services, reindex operations)

### Historical Frontend Summary (Through March 31)

**Total Implementations (Through March 31):**
- **70+ Pages** - New feature pages across 6+ major business areas
- **45+ Forms** - Specialized forms for complex entity creation/editing
- **75+ Components** - UI components, charts, modals, and utilities
- **36+ API Files** - API client modules organized by business domain
- **150+ API Functions** - Frontend API layer matching backend endpoints
- **13 Custom Hooks** - Reusable React logic (notifications, pagination, filtering, etc.)
- **19 Schema Files** - TypeScript type definitions with Zod validation

**Major Feature Additions:**
1. **Batch Management UI** (6 pages, complete batch drill-down, movement ledger, reconciliation)
2. **Claims Management UI** (4 pages, scheme management, claim reports)
3. **DSR Management UI** (7 pages, DSR assignments, storage management, settlements)
4. **Advanced Reports UI** (28 report pages, comprehensive business analytics)
5. **SR Orders Management** (12 pages, consolidated orders, disbursements)
6. **Notifications System** (3 components, notification center, real-time updates)
7. **Dashboard System** (4 pages, admin & DSR dashboards, activity feeds)
8. **Phone Suggestions UI** (1 page, admin approval interface)
9. **Chart Library** (17+ chart components for data visualization)
10. **Report Components** (10+ specialized report display components)

### Integration Points

**Frontend ↔ Backend Communication:**
- All 150+ frontend API functions map to 100+ backend endpoints
- Comprehensive request/response validation
- Consistent error handling and toast notifications
- Real-time query invalidation and data refetch patterns
- Async operations with loading states

### Code Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Lines of Backend Code | 60,000+ | ✅ |
| Lines of Frontend Code | 90,000+ | ✅ |
| Database Schemas | 9 multi-schema architecture | ✅ |
| API Documentation | 170+ endpoints documented | ✅ |
| Component Reusability | 90+ reusable components | ✅ |
| Test Coverage | Hooks and utility patterns established | ✅ |

---

## 🛡️ Important Conventions

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Python files | snake_case | `sales_order.py` |
| Python classes | PascalCase | `SalesOrder` |
| Python functions | snake_case | `get_sales_orders()` |
| Database tables | snake_case | `sales_order` |
| TypeScript files | camelCase or PascalCase | `salesApi.ts`, `SaleForm.tsx` |
| React components | PascalCase | `<SalesOrderList />` |
| API endpoints | kebab-case | `/sales-order/` |

### Timezone

- All dates use **Asia/Dhaka (UTC+6)** timezone
- Configured in `app/core/config.py`

### Error Handling

- Backend: Raise `HTTPException` in API layer
- Frontend: Toasts via `sonner` and `react-hot-toast` for user feedback
- Global exception handlers in `app/main.py`

---

*This context document was last updated on 2026-04-15 to reflect current project state and all recently implemented features (April 7-15, 2026 implementations added).*

**Summary of Updates (April 7-15, 2026):**
- Added Admin Dashboard KPIs (SR/DSR Dashboard Summary APIs)
- Added Pending Customer Workflow documentation
- Added 5 new Frontend API files (adminSRDashboardApi, adminDSRDashboardApi, dsrReportsApi, srProgramReportsApi, pendingCustomerApi)
- Added 3 new Backend Services (admin_sr_dashboard_service, admin_dsr_dashboard_service, pending_customer_service)
- Updated metrics: 60,000+ backend LOC, 90,000+ frontend LOC, 170+ API endpoints
