# Sales Order (Sales) Module - Complete Reference

**Generated:** April 16, 2026  
**Scope:** Full-stack analysis of the Sales Order Module  
**Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   React      │  │  TypeScript  │  │   TanStack   │  │    Zod       │  │
│  │  Components  │  │   Types      │  │   Query      │  │   Schemas    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        FastAPI (Python 3.11+)                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │   API      │  │  Service   │  │ Repository │  │   Model    │    │  │
│  │  │  Routes    │──│   Layer    │──│   Layer    │──│   Layer    │    │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ SQLAlchemy
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                                     │
│                    PostgreSQL 15+                                       │
│                         │                                               │
│            ┌────────────┼────────────┐                                  │
│            ▼            ▼            ▼                                  │
│      ┌─────────┐  ┌─────────┐  ┌─────────┐                             │
│      │  sales  │  │security│  │warehouse│                             │
│      │ schema  │  │ schema  │  │ schema  │                             │
│      └─────────┘  └─────────┘  └─────────┘                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │ Elasticsearch    │  │   Batch/COGS     │  │  Unit of Measure │        │
│  │ (Customer Search)│  │     Service      │  │    Utilities     │        │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ENTITY RELATIONSHIP DIAGRAM                              │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Beat        │       │    Customer     │       │  SalesOrder     │
│   (sales.beat)  │◄──────│(sales.customer) │◄──────│(sales.sales_   │
│                 │  1:N  │                 │  N:1  │    order)       │
│ - beat_id (PK)  │       │ - customer_id   │       │ - sales_order_id│
│ - beat_name     │       │ - beat_id (FK)  │       │ - customer_id   │
│ - beat_code     │       │ - customer_name │       │ - order_number  │
└─────────────────┘       │ - credit_limit  │       │ - status        │
                          └─────────────────┘       │ - total_amount  │
                                  │                 └─────────────────┘
                                  │ 1:N                      │ 1:N
                                  ▼                          ▼
                    ┌─────────────────────────┐    ┌─────────────────────────┐
                    │  Customer_SR_Assignment │    │   SalesOrderDetail      │
                    │(sales.customer_sr_       │    │ (sales.sales_order_     │
                    │     assignment)          │    │      detail)            │
                    │                         │    │                         │
                    │ - assignment_id (PK)    │    │ - sales_order_detail_id │
                    │ - sr_id (FK)            │    │ - sales_order_id (FK)   │
                    │ - customer_id (FK)      │    │ - product_id (FK)       │
                    └─────────────────────────┘    │ - variant_id (FK)       │
                                                   │ - quantity              │
┌─────────────────┐                                 │ - unit_price            │
│ SalesRepresenta │◄────────────────────────────────│ - shipped_quantity      │
│   tive          │        1:N via details        │ - returned_quantity     │
│(sales.sales_    │                                │ - free_quantity         │
│ representative)│                                └─────────────────────────┘
│                 │                                           │
│ - sr_id (PK)    │                                           │ 1:N
│ - sr_name       │                                           ▼
│ - sr_code       │                              ┌─────────────────────────┐
│ - commission    │                              │SalesOrderDeliveryDetail │
└─────────────────┘                              │(sales.sales_order_     │
        │                                        │    delivery_detail)     │
        │ 1:N                                    │                         │
        ▼                                        │ - delivery_detail_id    │
┌─────────────────┐                              │ - sales_order_detail_id │
│   SR_Order      │                              │ - delivery_date         │
│(sales.sr_order) │                              │ - delivered_quantity    │
│                 │                              └─────────────────────────┘
│ - sr_order_id   │
│ - sr_id (FK)    │         ┌─────────────────────────┐
│ - customer_id   │         │SalesOrderPaymentDetail  │
│ - status        │         │(sales.sales_order_     │
└─────────────────┘         │    payment_detail)      │
        │                   │                         │
        │ 1:N               │ - payment_detail_id     │
        ▼                 │ - sales_order_id (FK)   │
┌─────────────────┐       │ - amount_paid           │
│  SR_Order_Detail│       │ - payment_date          │
│(sales.sr_order_ │       └─────────────────────────┘
│     detail)     │
│                 │
│ - sr_order_detail_id      ┌─────────────────────────┐
│ - sr_order_id (FK)        │   PendingCustomer       │
│ - negotiated_price         │ (sales.pending_customer)│
│ - sale_price               │                         │
└─────────────────┘       │ - pending_customer_id   │
                          │ - status (pending/      │
┌────────────────────────┐│   approved/rejected)    │
│  DeliverySalesRepresen ││ - added_by_sr_id        │
│        tative          ││ - approved_customer_id  │
│(sales.delivery_sales_  │└─────────────────────────┘
│  representative)       │
│                        │       ┌─────────────────────────┐
│ - dsr_id (PK)          │       │   DSRSOAssignment       │
│ - dsr_code             │       │  (sales.dsr_so_         │
│ - payment_on_hand      │       │       assignment)       │
└────────────────────────┘       │                         │
                                 │ - assignment_id         │
        │ 1:N                    │ - dsr_id (FK)           │
        ▼                        │ - sales_order_id (FK)     │
┌────────────────────────┐       │ - status                │
│   DSRPaymentSettlement │       └─────────────────────────┘
│(sales.dsr_payment_     │
│     settlement)        │
│                        │
│ - settlement_id        │
│ - dsr_id (FK)          │
│ - amount               │
└────────────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend Framework | React | 18.x | UI Components |
| Frontend Language | TypeScript | 5.x | Type Safety |
| State Management | TanStack Query | 5.x | Server State |
| Forms/Validation | Zod | 3.x | Schema Validation |
| UI Components | shadcn/ui | Latest | Component Library |
| Styling | Tailwind CSS | 3.x | CSS Framework |
| Backend Framework | FastAPI | 0.115+ | API Framework |
| Backend Language | Python | 3.11+ | Business Logic |
| ORM | SQLAlchemy | 2.x | Database Access |
| Database | PostgreSQL | 15+ | Data Storage |
| Search | Elasticsearch | 8.x | Customer Search |
| HTTP Client | Axios | 1.x | API Communication |

---

## 2. Entity Inventory

### 2.1 Customer (`sales.customer`)

**Description:** Stores customer information including contact details, location, and financial limits.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| customer_id | Integer | PK, Index | Unique identifier |
| customer_name | String(200) | NOT NULL | Customer full name |
| customer_code | String(50) | Index, Nullable | Unique customer code |
| credit_limit | Numeric(18,2) | Nullable | Maximum credit allowed |
| store_credit | Numeric(18,2) | NOT NULL, Default 0 | Store credit balance |
| balance_amount | Numeric(18,2) | NOT NULL, Default 0 | Outstanding balance |
| beat_id | Integer | FK → sales.beat | Assigned sales beat |
| contact_person | String(100) | Nullable | Primary contact name |
| contact_email | String(100) | Nullable | Email address |
| contact_phone | String(20) | Nullable | Phone number |
| address | String(500) | Nullable | Street address |
| country_id | Integer | FK → settings.country | Country reference |
| state_id | Integer | FK → settings.state | State/Province reference |
| city_id | Integer | FK → settings.city | City reference |
| zip_code | String(20) | Nullable | Postal code |
| is_active | Boolean | NOT NULL, Default true | Active status |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb | Integer | NOT NULL | Created by user |
| cd | DateTime | NOT NULL | Creation timestamp |
| mb | Integer | NOT NULL | Modified by user |
| md | DateTime | NOT NULL | Modification timestamp |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete flag |
| version | Integer | NOT NULL, Default 1 | Optimistic locking |

**Relationships:**
- `beat` → `Beat` (N:1) - Customer belongs to one beat
- `sales_orders` → `SalesOrder` (1:N) - Customer has many sales orders
- `sr_orders` → `SR_Order` (1:N) - Customer has many SR orders
- `sr_assignments` → `Customer_SR_Assignment` (1:N) - Multiple SR assignments
- `phone_suggestions` → `CustomerPhoneSuggestion` (1:N) - Phone update suggestions
- `country` → `Country` (N:1)
- `state` → `State` (N:1)
- `city` → `City` (N:1)
- `company` → `AppClientCompany` (N:1)

---

### 2.2 Beat (`sales.beat`)

**Description:** Geographic sales routes/zones for organizing customer territories.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| beat_id | Integer | PK, Index | Unique identifier |
| beat_name | String(100) | NOT NULL | Beat name |
| beat_code | String(50) | Unique, NOT NULL | Unique code |
| description | String(500) | Nullable | Description |
| is_active | Boolean | NOT NULL, Default true | Active status |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `customers` → `Customer` (1:N) - Beat has many customers
- `company` → `AppClientCompany` (N:1)

---

### 2.3 SalesOrder (`sales.sales_order`)

**Description:** Main sales order entity with order tracking, consolidation, and DSR loading support.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sales_order_id | Integer | PK, Index | Unique identifier |
| order_number | String(50) | Indexed | Order reference number |
| customer_id | Integer | FK → sales.customer, NOT NULL | Customer reference |
| order_date | TIMESTAMP | NOT NULL | Order creation date |
| expected_shipment_date | TIMESTAMP | Nullable | Expected delivery |
| status | String(20) | NOT NULL | Order status |
| total_amount | Numeric(18,2) | NOT NULL | Total order value |
| amount_paid | Numeric(18,2) | NOT NULL, Default 0 | Amount paid |
| invoice_id | String(100) | Nullable | Linked invoice reference |
| payment_status | String(20) | NOT NULL, Default "Pending" | Payment tracking |
| delivery_status | String(20) | NOT NULL, Default "Pending" | Delivery tracking |
| commission_disbursed | String(20) | NOT NULL, Default "pending" | Commission status |
| order_source | String(20) | NOT NULL, Default "direct" | Source (direct/sr) |
| is_consolidated | Boolean | NOT NULL, Default false | From SR consolidation |
| consolidated_sr_orders | JSON | Nullable | Array of SR orders |
| total_price_adjustment | Numeric(18,2) | NOT NULL, Default 0 | Price adjustment |
| consolidation_date | TIMESTAMP | Nullable | When consolidated |
| consolidated_by | Integer | Nullable | User who consolidated |
| is_loaded | Boolean | NOT NULL, Default false | Loaded to DSR |
| loaded_by_dsr_id | Integer | FK → sales.delivery_sales_representative | DSR who loaded |
| loaded_at | TIMESTAMP | Nullable | Loading timestamp |
| do_number | String(50) | Nullable | Delivery order number |
| location_id | Integer | FK → warehouse.storage_location | Storage location |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |
| version | Integer | NOT NULL, Default 1 | Optimistic locking |

**Relationships:**
- `customer` → `Customer` (N:1)
- `company` → `AppClientCompany` (N:1)
- `location` → `StorageLocation` (N:1)
- `details` → `SalesOrderDetail` (1:N, cascade delete)
- `payment_details` → `SalesOrderPaymentDetail` (1:N, cascade delete)
- `invoices` → `Invoice` (1:N)
- `creator` → `User` (N:1)
- `dsr_assignment` → `DSRSOAssignment` (1:1)
- `loaded_by_dsr` → `DeliverySalesRepresentative` (N:1)

**Indexes:**
- `idx_so_order_number` - Order number lookups
- `idx_so_company_status` - Company + status filtering
- `idx_so_customer_date` - Customer order history
- `idx_so_payment_status` - Payment queries
- `idx_so_delivery_status` - Delivery queries
- `idx_so_consolidated` - Consolidation queries

---

### 2.4 SalesOrderDetail (`sales.sales_order_detail`)

**Description:** Line items for sales orders with product, quantity, pricing, and tracking.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sales_order_detail_id | Integer | PK, Index | Unique identifier |
| sales_order_id | Integer | FK → sales.sales_order, NOT NULL | Parent order |
| product_id | Integer | FK → inventory.product, NOT NULL | Product reference |
| variant_id | Integer | FK → inventory.product_variant | Variant reference |
| unit_of_measure_id | Integer | FK → inventory.unit_of_measure | UOM reference |
| quantity | Numeric(18,4) | NOT NULL | Ordered quantity |
| unit_price | Numeric(18,4) | NOT NULL | Price per unit |
| discount_amount | Numeric(18,2) | NOT NULL, Default 0 | Discount value |
| shipped_quantity | Numeric(18,4) | NOT NULL, Default 0 | Quantity shipped |
| free_quantity | Numeric(18,4) | NOT NULL, Default 0 | Free items |
| shipped_free_quantity | Numeric(18,4) | NOT NULL, Default 0 | Free items shipped |
| returned_quantity | Numeric(18,4) | NOT NULL, Default 0 | Quantity returned |
| returned_free_quantity | Numeric(18,4) | NOT NULL, Default 0 | Free items returned |
| applied_scheme_id | Integer | Nullable | Applied claim scheme |
| is_free_item | Boolean | Nullable, Default false | Is this a free item line |
| parent_detail_id | Integer | FK → self | Parent for free items |
| sr_order_detail_id | Integer | FK → sales.sr_order_detail | Source SR detail |
| negotiated_price | Numeric(18,4) | Nullable | SR negotiated price |
| price_difference | Numeric(18,4) | NOT NULL, Default 0 | Price adjustment |
| sr_id | Integer | FK → sales.sales_representative | SR who created |
| provided_sale_price_to_sr | Numeric(18,4) | Nullable | Price given to SR |
| sr_order_detail_ids | JSON | Nullable | Array of SR detail IDs |
| sr_details | JSON | Nullable | Structured SR data |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_order` → `SalesOrder` (N:1)
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `unit_of_measure` → `UnitOfMeasure` (N:1)
- `delivery_details` → `SalesOrderDeliveryDetail` (1:N)
- `sr_order_detail` → `SR_Order_Detail` (N:1)
- `sales_representative` → `SalesRepresentative` (N:1)
- `batch_allocations` → `SalesOrderBatchAllocation` (1:N)

**Indexes:**
- `idx_sod_product_variant` - Product/variant queries
- `idx_sod_sr_order_detail` - SR detail references

---

### 2.5 SalesOrderDeliveryDetail (`sales.sales_order_delivery_detail`)

**Description:** Records individual delivery/shipment events for order line items.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| delivery_detail_id | Integer | PK, Index | Unique identifier |
| sales_order_detail_id | Integer | FK → sales.sales_order_detail, NOT NULL | Parent detail |
| delivery_date | TIMESTAMP | NOT NULL | When delivered |
| delivered_quantity | Numeric(18,4) | NOT NULL | Quantity delivered |
| delivered_free_quantity | Numeric(18,4) | NOT NULL, Default 0 | Free items delivered |
| shipped_by | Integer | Nullable | User who shipped |
| remarks | String(500) | Nullable | Delivery notes |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_order_detail` → `SalesOrderDetail` (N:1)

---

### 2.6 SalesOrderPaymentDetail (`sales.sales_order_payment_detail`)

**Description:** Payment records against sales orders.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| payment_detail_id | Integer | PK, Index | Unique identifier |
| sales_order_id | Integer | FK → sales.sales_order, NOT NULL | Parent order |
| payment_date | TIMESTAMP | NOT NULL | When paid |
| amount_paid | Numeric(18,2) | NOT NULL | Payment amount |
| payment_method | String(50) | Nullable | Payment method |
| transaction_reference | String(100) | Nullable | Reference number |
| remarks | String(500) | Nullable | Payment notes |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_order` → `SalesOrder` (N:1)

---

### 2.7 SalesRepresentative (`sales.sales_representative`)

**Description:** Sales representative (SR) master data with commission tracking.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sr_id | Integer | PK, Index | Unique identifier |
| sr_name | String(200) | NOT NULL | SR full name |
| sr_code | String(50) | Unique, NOT NULL, Indexed | Unique code |
| contact_email | String(100) | Nullable | Email address |
| contact_phone | String(20) | Nullable | Phone number |
| commission_amount | Numeric(18,2) | NOT NULL, Default 0 | Commission balance |
| is_active | Boolean | NOT NULL, Default true | Active status |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `company` → `AppClientCompany` (N:1)
- `product_assignments` → `SR_Product_Assignment` (1:N)
- `customer_assignments` → `Customer_SR_Assignment` (1:N)
- `sr_orders` → `SR_Order` (1:N)
- `sales_order_details` → `SalesOrderDetail` (1:N)
- `users` → `User` (1:N)
- `phone_suggestions` → `CustomerPhoneSuggestion` (1:N)
- `disbursements` → `SRDisbursement` (1:N)

---

### 2.8 SR_Product_Assignment (`sales.sr_product_assignment`)

**Description:** Products assigned to SRs with pricing and date constraints.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| assignment_id | Integer | PK, Index | Unique identifier |
| sr_id | Integer | FK → sales.sales_representative, NOT NULL, Indexed | SR reference |
| product_id | Integer | FK → inventory.product, NOT NULL, Indexed | Product reference |
| variant_id | Integer | FK → inventory.product_variant, Indexed | Variant reference |
| assigned_date | TIMESTAMP | NOT NULL, Default now | Assignment date |
| assigned_sale_price | Numeric(18,4) | Nullable | Sale price to customer |
| price_effective_date | TIMESTAMP | Nullable | When price starts |
| price_expiry_date | TIMESTAMP | Nullable | When price ends |
| allow_price_override | Boolean | NOT NULL, Default true | Can SR negotiate |
| min_override_price | Numeric(18,4) | Nullable | Minimum negotiated price |
| max_override_price | Numeric(18,4) | Nullable | Maximum negotiated price |
| price_notes | Text | Nullable | Pricing notes |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_representative` → `SalesRepresentative` (N:1)
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `price_history` → `SR_Product_Assignment_Price_History` (1:N)

---

### 2.9 Customer_SR_Assignment (`sales.customer_sr_assignment`)

**Description:** Junction table linking SRs to customers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| assignment_id | Integer | PK, Index | Unique identifier |
| sr_id | Integer | FK → sales.sales_representative, NOT NULL, Indexed | SR reference |
| customer_id | Integer | FK → sales.customer, NOT NULL, Indexed | Customer reference |
| assigned_date | TIMESTAMP | NOT NULL, Default now | Assignment date |
| is_active | Boolean | NOT NULL, Default true | Active status |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_representative` → `SalesRepresentative` (N:1)
- `customer` → `Customer` (N:1)

---

### 2.10 SR_Order (`sales.sr_order`)

**Description:** Orders created by Sales Representatives before consolidation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sr_order_id | Integer | PK, Index | Unique identifier |
| sr_id | Integer | FK → sales.sales_representative, NOT NULL, Indexed | SR reference |
| customer_id | Integer | FK → sales.customer, NOT NULL, Indexed | Customer reference |
| order_number | String(50) | NOT NULL | Order reference |
| order_date | TIMESTAMP | NOT NULL | Order date |
| status | String(20) | NOT NULL, Indexed | Order status |
| total_amount | Numeric(18,2) | NOT NULL | Order total |
| amount_paid | Numeric(18,2) | NOT NULL, Default 0 | Amount paid |
| commission_disbursed | String(20) | NOT NULL, Default "pending" | Commission status |
| commission_amount | Numeric(18,4) | Nullable | Calculated commission |
| location_id | Integer | FK → warehouse.storage_location | Storage location |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_representative` → `SalesRepresentative` (N:1)
- `customer` → `Customer` (N:1)
- `company` → `AppClientCompany` (N:1)
- `location` → `StorageLocation` (N:1)
- `details` → `SR_Order_Detail` (1:N, cascade delete)

---

### 2.11 SR_Order_Detail (`sales.sr_order_detail`)

**Description:** Line items for SR orders with negotiated pricing.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sr_order_detail_id | Integer | PK, Index | Unique identifier |
| sr_order_id | Integer | FK → sales.sr_order, NOT NULL, Indexed | Parent order |
| product_id | Integer | FK → inventory.product, NOT NULL | Product reference |
| variant_id | Integer | FK → inventory.product_variant | Variant reference |
| unit_of_measure_id | Integer | FK → inventory.unit_of_measure | UOM reference |
| quantity | Numeric(18,4) | NOT NULL | Ordered quantity |
| unit_price | Numeric(18,4) | NOT NULL | Base unit price |
| negotiated_price | Numeric(18,4) | NOT NULL | SR negotiated price |
| sale_price | Numeric(18,4) | Nullable | Final sale price |
| discount_amount | Numeric(18,2) | NOT NULL, Default 0 | Discount |
| shipped_quantity | Numeric(18,4) | NOT NULL, Default 0 | Quantity shipped |
| returned_quantity | Numeric(18,4) | NOT NULL, Default 0 | Quantity returned |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sr_order` → `SR_Order` (N:1)
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `unit_of_measure` → `UnitOfMeasure` (N:1)
- `sales_order_details` → `SalesOrderDetail` (1:N)

---

### 2.12 PendingCustomer (`sales.pending_customer`)

**Description:** Customers added by SRs awaiting admin approval.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| pending_customer_id | Integer | PK, Index | Unique identifier |
| customer_name | String(200) | NOT NULL | Customer name |
| customer_code | String(50) | Nullable | Proposed code |
| contact_person | String(100) | Nullable | Contact name |
| contact_email | String(100) | Nullable | Email |
| contact_phone | String(20) | Nullable | Phone |
| address | String(500) | Nullable | Address |
| country_id | Integer | FK → settings.country | Country |
| state_id | Integer | FK → settings.state | State |
| city_id | Integer | FK → settings.city | City |
| zip_code | String(20) | Nullable | Postal code |
| credit_limit | Numeric(18,2) | Nullable | Credit limit |
| balance_amount | Numeric(18,2) | Default 0 | Balance |
| beat_id | Integer | FK → sales.beat | Beat |
| status | String(20) | NOT NULL, Default "pending", Indexed | Approval status |
| is_active | Boolean | NOT NULL, Default true | Active flag |
| added_by_sr_id | Integer | FK → sales.sales_representative, NOT NULL, Indexed | SR who added |
| approved_by | Integer | FK → security.app_user | Admin approver |
| approved_at | TIMESTAMP | Nullable | Approval timestamp |
| rejected_by | Integer | FK → security.app_user | Admin rejecter |
| rejected_at | TIMESTAMP | Nullable | Rejection timestamp |
| rejection_reason | String(500) | Nullable | Why rejected |
| assign_to_sr_on_approval | Boolean | NOT NULL, Default true | Auto-assign flag |
| assigned_sr_id | Integer | FK → sales.sales_representative | SR to assign |
| approved_customer_id | Integer | FK → sales.customer | Link to final customer |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `sales_representative` → `SalesRepresentative` (added_by_sr_id) (N:1)
- `assigned_sr` → `SalesRepresentative` (assigned_sr_id) (N:1)
- `approved_by_user` → `User` (N:1)
- `rejected_by_user` → `User` (N:1)
- `approved_customer` → `Customer` (N:1)
- `beat` → `Beat` (N:1)
- `country` → `Country` (N:1)
- `state` → `State` (N:1)
- `city` → `City` (N:1)

---

### 2.13 DeliverySalesRepresentative (`sales.delivery_sales_representative`)

**Description:** Delivery SRs (DSRs) who handle physical delivery and collect payments.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| dsr_id | Integer | PK, Index | Unique identifier |
| dsr_name | String(200) | NOT NULL | DSR full name |
| dsr_code | String(50) | Unique, NOT NULL, Indexed | Unique code |
| contact_email | String(100) | Nullable | Email |
| contact_phone | String(20) | Nullable | Phone |
| payment_on_hand | Numeric(18,2) | NOT NULL, Default 0 | Cash in hand |
| commission_amount | Numeric(18,2) | NOT NULL, Default 0 | Commission balance |
| is_active | Boolean | NOT NULL, Default true | Active status |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |
| version | Integer | NOT NULL, Default 1 | Optimistic locking |

**Relationships:**
- `company` → `AppClientCompany` (N:1)
- `users` → `User` (1:N)
- `dsr_storage` → `DSRStorage` (1:1)
- `so_assignments` → `DSRSOAssignment` (1:N)
- `payment_settlements` → `DSRPaymentSettlement` (1:N)

---

### 2.14 DSRSOAssignment (`sales.dsr_so_assignment`)

**Description:** Assigns Sales Orders to DSRs for delivery.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| assignment_id | Integer | PK, Index | Unique identifier |
| dsr_id | Integer | FK → sales.delivery_sales_representative, NOT NULL, Indexed | DSR reference |
| sales_order_id | Integer | FK → sales.sales_order, NOT NULL, Indexed, Unique | SO reference |
| assigned_date | TIMESTAMP | NOT NULL, Default now | Assignment date |
| status | String(20) | NOT NULL, Default "assigned", Indexed | Assignment status |
| notes | String(500) | Nullable | Notes |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `dsr` → `DeliverySalesRepresentative` (N:1)
- `sales_order` → `SalesOrder` (N:1)
- `company` → `AppClientCompany` (N:1)

---

### 2.15 DSRPaymentSettlement (`sales.dsr_payment_settlement`)

**Description:** Records when admin collects payments from DSRs.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| settlement_id | Integer | PK, Index | Unique identifier |
| dsr_id | Integer | FK → sales.delivery_sales_representative, NOT NULL, Indexed | DSR reference |
| settlement_date | TIMESTAMP | NOT NULL, Default now | Settlement date |
| amount | Numeric(18,2) | NOT NULL | Amount collected |
| payment_method | String(50) | Nullable | Payment method |
| reference_number | String(100) | Nullable | Transaction ref |
| notes | String(500) | Nullable | Notes |
| company_id | Integer | FK → security.app_client_company | Tenant ID |
| cb, cd, mb, md | Audit | NOT NULL | Audit timestamps |
| is_deleted | Boolean | NOT NULL, Default false | Soft delete |

**Relationships:**
- `dsr` → `DeliverySalesRepresentative` (N:1)

---

## 3. Backend Operations Reference

### 3.1 Customer Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/customer/` | `CustomerService.list_customers()` | Paginated list with filters |
| Get Single | GET | `/api/company/sales/customer/{id}` | `CustomerService.get_customer()` | Get customer by ID |
| Create | POST | `/api/company/sales/customer/` | `CustomerService.create_customer()` | Create new customer + ES index |
| Update | PATCH | `/api/company/sales/customer/{id}` | `CustomerService.update_customer()` | Update customer + ES reindex |
| Delete | DELETE | `/api/company/sales/customer/{id}` | `CustomerService.delete_customer()` | Soft delete + ES delete |
| Batch Delete | POST | `/api/company/sales/customer/batch-delete` | `CustomerService.batch_delete_customers()` | Delete multiple |
| Search | GET | `/api/company/sales/customer/search` | `CustomerElasticsearchService.search_customers()` | ES search |
| Reindex | POST | `/api/company/sales/customer/reindex` | `CustomerElasticsearchService.reindex_atomic()` | Rebuild ES index |
| Add Store Credit | POST | `/api/company/sales/customer/{id}/add-store-credit` | Customer update | Increase credit |
| Subtract Store Credit | POST | `/api/company/sales/customer/{id}/subtract-store-credit` | Customer update | Decrease credit |
| Request Phone Update | POST | `/api/company/sales/customer/{id}/request-phone-update` | `CustomerPhoneSuggestionService.create_suggestion()` | SR requests phone change |
| Get By IDs | POST | `/api/company/sales/customer/by-ids` | `CustomerService.get_customers_by_ids()` | Bulk fetch |
| Import Excel | POST | `/api/company/sales/customer/import-excel` | API handler | Import customers |

### 3.2 Beat Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/beat/` | `BeatService.list_beats()` | Paginated list |
| Get Single | GET | `/api/company/sales/beat/{id}` | `BeatService.get_beat()` | Get beat by ID |
| Create | POST | `/api/company/sales/beat/` | `BeatService.create_beat()` | Create new beat |
| Update | PUT | `/api/company/sales/beat/{id}` | `BeatService.update_beat()` | Update beat |
| Delete | DELETE | `/api/company/sales/beat/{id}` | `BeatService.delete_beat()` | Soft delete |
| Assign Customers | POST | `/api/company/sales/beat/{id}/assign-customers` | `BeatService.assign_customers_to_beat()` | Link customers |
| Unassign Customers | POST | `/api/company/sales/beat/{id}/unassign-customers` | `BeatService.unassign_customers_from_beat()` | Unlink customers |
| List Customers | GET | `/api/company/sales/beat/{id}/customers` | `BeatService.list_customers_in_beat()` | Customers in beat |

### 3.3 Sales Order Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sales-order/` | `SalesOrderService.list_sales_orders()` | Paginated with filters |
| Get Single | GET | `/api/company/sales/sales-order/{id}` | `SalesOrderService.get_sales_order()` | Get order by ID |
| Create | POST | `/api/company/sales/sales-order/` | `SalesOrderService.create_sales_order()` | Create with validation |
| Update | PATCH | `/api/company/sales/sales-order/{id}` | `SalesOrderService.update_sales_order()` | Update order |
| Delete | DELETE | `/api/company/sales/sales-order/{id}` | `SalesOrderService.delete_sales_order()` | Soft delete |
| Cancel | POST | `/api/company/sales/sales-order/{id}/cancel` | `SalesOrderService.cancel_sales_order()` | Cancel order |
| Process Return | POST | `/api/company/sales/sales-order/{id}/return` | `SalesOrderService.process_return()` | Handle returns |
| Process Rejection | POST | `/api/company/sales/sales-order/{id}/rejection` | `SalesOrderService.process_rejection()` | Delivery rejection |
| Allocate Batch | POST | `/api/company/sales/{id}/allocate` | `BatchAllocationService.allocate()` | Batch allocation |
| Process Sales Return | POST | `/api/company/sales/{id}/returns` | `BatchAllocationService.process_return()` | Batch traceable returns |

### 3.4 Sales Order Detail Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sales-order-detail/` | `SalesOrderDetailService.list_sales_order_details()` | List details |
| Get Single | GET | `/api/company/sales/sales-order-detail/{id}` | `SalesOrderDetailService.get_sales_order_detail()` | Get detail |
| Create | POST | `/api/company/sales/sales-order-detail/` | `SalesOrderDetailService.create_sales_order_detail()` | Add line item |
| Update | PATCH | `/api/company/sales/sales-order-detail/{id}` | `SalesOrderDetailService.update_sales_order_detail()` | Update detail |
| Delete | DELETE | `/api/company/sales/sales-order-detail/{id}` | `SalesOrderDetailService.delete_sales_order_detail()` | Remove line |
| Return Items | PATCH | `/api/company/sales/sales-order-detail/{id}/return` | `SalesOrderDetailService.return_items()` | Record return |

### 3.5 Sales Order Delivery Detail Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sales-order-delivery-detail/` | `SalesOrderDeliveryDetailService.list_delivery_details()` | List deliveries |
| Get Single | GET | `/api/company/sales/sales-order-delivery-detail/{id}` | `SalesOrderDeliveryDetailService.get_delivery_detail()` | Get delivery |
| Create | POST | `/api/company/sales/sales-order-delivery-detail/` | `SalesOrderDeliveryDetailService.create_delivery_detail()` | Record delivery |
| Update | PATCH | `/api/company/sales/sales-order-delivery-detail/{id}` | `SalesOrderDeliveryDetailService.update_delivery_detail()` | Update delivery |
| Delete | DELETE | `/api/company/sales/sales-order-delivery-detail/{id}` | `SalesOrderDeliveryDetailService.delete_delivery_detail()` | Remove record |

### 3.6 Sales Order Payment Detail Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sales-order-payment-detail/` | `SalesOrderPaymentDetailService.list_payment_details()` | List payments |
| Get Single | GET | `/api/company/sales/sales-order-payment-detail/{id}` | `SalesOrderPaymentDetailService.get_payment_detail()` | Get payment |
| Create | POST | `/api/company/sales/sales-order-payment-detail/` | `SalesOrderPaymentDetailService.create_payment_detail()` | Record payment |
| Update | PATCH | `/api/company/sales/sales-order-payment-detail/{id}` | `SalesOrderPaymentDetailService.update_payment_detail()` | Update payment |
| Delete | DELETE | `/api/company/sales/sales-order-payment-detail/{id}` | `SalesOrderPaymentDetailService.delete_payment_detail()` | Remove record |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| Sales List | `/sales` | ✅ | Main sales orders listing with filters |
| New Sale | `/sales/new` | ✅ | Create new sales order |
| View Sale Details | `/sales/details` | ✅ | View order details modal |
| Customers List | `/customers` | ✅ | Customer management with search |
| New Customer | `/customers/new` | ✅ | Create new customer |
| Customer Dues | `/customers/dues` | ✅ | Outstanding balances view |
| Pending Approvals | `/customers/pending-approvals` | ✅ | Approve SR-added customers |
| Beats List | `/customers/beats` | ✅ | Beat/territory management |
| New Beat | `/customers/beats/new` | ✅ | Create new beat |
| Phone Suggestions | `/sales/phone-suggestions` | ✅ | Approve phone number updates |

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| SaleForm | `components/forms/SaleForm.tsx` | Create/edit sales orders |
| CustomerForm | `components/forms/CustomerForm.tsx` | Create/edit customers |
| BeatForm | `components/forms/BeatForm.tsx` | Create/edit beats |
| SalesPaymentForm | `components/forms/SalesPaymentForm.tsx` | Record payments |
| UnifiedDeliveryForm | `components/forms/UnifiedDeliveryForm.tsx` | Process deliveries |
| SalesReturnForm | `components/forms/SalesReturnForm.tsx` | Handle returns |
| DSRAssignmentForm | `components/forms/DSRAssignmentForm.tsx` | Assign to DSR |
| AssignCustomersToBeatForm | `components/forms/AssignCustomersToBeatForm.tsx` | Link customers to beat |
| AssignSRToCustomerForm | `components/forms/AssignSRToCustomerForm.tsx` | Assign SR to customer |
| PhoneSuggestionForm | `components/forms/PhoneSuggestionForm.tsx` | Request phone update |
| PendingCustomerForm | `components/forms/PendingCustomerForm.tsx` | SR creates pending customer |

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| SalesFilter | `components/SalesFilter.tsx` | Filter bar for sales list |
| CustomerFilter | `components/CustomerFilter.tsx` | Filter bar for customers |
| BeatFilter | `components/BeatFilter.tsx` | Filter for beats |
| BeatCustomersList | `components/BeatCustomersList.tsx` | Show customers in beat |
| CustomerPhoneSuggestion | `components/CustomerPhoneSuggestion.tsx` | Display phone suggestions |
| ViewOrderDetails | `components/shared/ViewOrderDetails.tsx` | Order detail view |
| OrderStatus | `components/shared/OrderStatus.tsx` | Status badge display |
| ImportExportButton | `components/ImportExportButton.tsx` | Import/export actions |
| ConfirmDeleteDialog | `components/shared/ConfirmDeleteDialog.tsx` | Delete confirmation |

### 4.4 Context Providers

| Context | File Path | Purpose |
|---------|-----------|---------|
| POSContext | `contexts/POSContext.tsx` | Point of sale state |
| UserContext | `contexts/UserContext.tsx` | Current user data |
| SettingsContext | `contexts/SettingsContext.tsx` | App settings |
| BookmarksContext | `contexts/BookmarksContext.tsx` | User bookmarks |
| ProductSelectionContext | `contexts/ProductSelectionContext.tsx` | Product picker state |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `lib/api/salesApi.ts` | `getSales()`, `createSale()`, `updateSale()`, `deleteSale()`, `returnSalesOrder()`, `consolidateSROrders()` |
| `lib/api/customerApi.ts` | `getCustomers()`, `createCustomer()`, `updateCustomer()`, `deleteCustomer()`, `searchCustomers()`, `batchDeleteCustomers()` |
| `lib/api/beatApi.ts` | `getBeats()`, `createBeat()`, `updateBeat()`, `deleteBeat()`, `assignCustomersToBeat()`, `unassignCustomersFromBeat()` |
| `lib/api/pendingCustomerApi.ts` | `getPendingCustomers()`, `approvePendingCustomer()`, `rejectPendingCustomer()` |
| `lib/api/phoneSuggestionApi.ts` | `getSuggestions()`, `approveSuggestion()`, `rejectSuggestion()` |

### 4.6 Types & Zod Schemas

| Schema | File | Fields |
|--------|------|--------|
| `insertCustomerSchema` | `lib/schema/sales.ts` | customer_code, customer_name, contact_person, contact_email, contact_phone, address, country_id, state_id, city_id, zip_code, credit_limit, is_active, company_id, beat_id |
| `insertSaleSchema` | `lib/schema/sales.ts` | order_number, customer_id, order_date, expected_shipment_date, status, total_amount, amount_paid, company_id, location_id, payment_status, delivery_status, details[] |
| `insertSaleDetailSchema` | `lib/schema/sales.ts` | product_id, variant_id, unit_of_measure_id, quantity, unit_price, shipped_quantity, applied_scheme_id, free_quantity, shipped_free_quantity, discount_amount, is_free_item, parent_detail_id |
| `salesPaymentSchema` | `lib/schema/sales.ts` | payment_date, amount_paid, payment_method, transaction_reference, remarks |
| `salesDeliverySchema` | `lib/schema/sales.ts` | delivery_date, delivered_quantity, delivered_free_quantity, remarks |
| `consolidatedOrderSchema` | `lib/schema/sales.ts` | sales_order_id, order_number, customer_id, is_consolidated, consolidated_sr_orders[], total_price_adjustment, details[], sr_details[] |
| `beatSchema` | `lib/schema/beat.ts` | beat_name, beat_code, description, company_id, is_active |

---

## 5. Interconnected Workflows

### 5.1 Sales Order Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: User clicks "New Sale"                                               │
│ → Component: Sales.tsx renders with "New Sale" button                       │
│ → Route: Navigate to `/sales/new`                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: SaleForm component loads                                             │
│ → File: `components/forms/SaleForm.tsx`                                     │
│ → Fetches: customers, locations, products                                   │
│ → Uses: `useQuery` with `getCustomers()`, `getStorageLocations()`          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: User fills order details                                             │
│ → Selects: customer (from customer dropdown)                                │
│ → Selects: location (from location dropdown)                                │
│ → Adds: products via SelectProductModal                                     │
│ → Enter: quantities, prices (with scheme auto-apply)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Submit form                                                          │
│ → Validation: `insertSaleSchema.safeParse()`                                │
│ → API Call: `createSale()` → POST `/api/company/sales/sales-order/`        │
│ → Service: `SalesOrderService.create_sales_order()`                         │
│ → Actions:                                                                   │
│   1. Validate stock availability (`_validate_stock_availability()`)         │
│   2. Apply schemes via `ClaimService.evaluate_schemes()`                    │
│   3. Create order header in `sales.sales_order`                              │
│   4. Create detail lines in `sales.sales_order_detail`                     │
│   5. Deduct inventory from `warehouse.inventory_stock`                        │
│   6. Create batch allocations if enabled                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Return to list                                                       │
│ → Invalidate: `queryClient.invalidateQueries({ queryKey: ["/sales"] })`      │
│ → Toast: "Sale created successfully"                                        │
│ → Redirect: Back to `/sales`                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Customer Management Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CUSTOMER CREATION                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. User clicks "New Customer" in Customers.tsx                                │
│ 2. Navigate to `/customers/new` → renders AddCustomer page                   │
│ 3. CustomerForm.tsx loads with location data (countries, states, cities)    │
│ 4. User fills: name, code, contact, address, beat assignment                  │
│ 5. Submit → `createCustomer()` → POST `/api/company/sales/customer/`         │
│ 6. Backend: `CustomerService.create_customer()`                               │
│    - Check for duplicates via `CustomerRepository.check_duplicate_customer()`│
│    - Create in DB → `sales.customer`                                         │
│    - Index in Elasticsearch via `CustomerElasticsearchService.index_customer()`│
│ 7. Return to list, show success toast                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CUSTOMER SEARCH (Elasticsearch)                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. User types in search box in Customers.tsx                                  │
│ 2. Debounced search triggers after 300ms                                      │
│ 3. `searchCustomers(query)` → GET `/api/company/sales/customer/search`       │
│ 4. Backend: `CustomerElasticsearchService.search_customers()`                 │
│    - Query ES index `customers_{company_id}`                                  │
│    - Fallback to DB search if ES unavailable                                  │
│ 5. Results displayed in table                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ BATCH DELETE                                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. User selects multiple customers via checkboxes                             │
│ 2. Clicks "Delete Selected" → ConfirmDeleteDialog opens                      │
│ 3. Confirm → `batchDeleteCustomers(customer_ids)`                            │
│ 4. POST `/api/company/sales/customer/batch-delete`                           │
│ 5. Backend: `CustomerService.batch_delete_customers()`                         │
│    - Pre-validate all IDs exist and not already deleted                       │
│    - Soft delete each customer in transaction                                 │
│    - Delete from Elasticsearch                                                │
│ 6. Return success/failure counts                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Delivery Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ RECORD DELIVERY                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. In Sales list, user clicks actions menu → "Record Delivery"                │
│ 2. UnifiedDeliveryForm.tsx opens as dialog                                    │
│ 3. Fetches: order details, available stock                                    │
│ 4. User enters: delivery quantities, date, remarks                            │
│ 5. If batch tracking enabled: shows batch allocation UI                       │
│ 6. Submit → `createSalesDelivery()` → POST `/sales/sales-order-delivery-detail/`│
│ 7. Backend: `SalesOrderDeliveryDetailService.create_delivery_detail()`        │
│    - Create delivery detail record                                            │
│    - Update `shipped_quantity` in order detail                                │
│    - Update order `delivery_status`                                           │
│    - If batch enabled: create `inventory_batch.sales_order_batch_allocation` │
│    - Reduce inventory stock                                                   │
│ 8. Return updated order, refresh list                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 SR Order Consolidation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONSOLIDATE SR ORDERS INTO SALES ORDER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. User navigates to `/sales-representatives/unconsolidated`                │
│ 2. UnconsolidatedSROrders.tsx loads SR orders with status="confirmed"         │
│ 3. User selects multiple SR orders, clicks "Consolidate"                     │
│ 4. System calls `validateConsolidation(sr_order_ids, location_id)`            │
│    → POST `/api/company/sales/consolidation/validate-consolidation`        │
│ 5. Validation checks:                                                         │
│    - Same customer across all orders                                          │
│    - Sufficient stock at location                                             │
│    - Orders not already consolidated                                          │
│ 6. On pass, ConsolidationModal opens with price adjustment interface          │
│ 7. User reviews final prices, sets location, shipment date                    │
│ 8. Submit → `consolidateSROrders()` → POST `/api/company/sales/consolidation/`│
│ 9. Backend: `ConsolidationService.consolidate_sr_orders()`                    │
│    - Create SalesOrder with `is_consolidated=true`                            │
│    - Create SalesOrderDetail lines from SR_Order_Detail lines                 │
│    - Store SR references in `consolidated_sr_orders` JSON                     │
│    - Update SR_Orders status to "consolidated"                                │
│    - Calculate `total_price_adjustment`                                       │
│ 10. Return new sales order, redirect to consolidated orders list              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 DSR Assignment & Loading Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ASSIGN SALES ORDER TO DSR                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. In Sales list, user clicks actions → "Assign to DSR"                     │
│ 2. DSRAssignmentForm.tsx opens                                               │
│ 3. Fetches: available DSRs list                                              │
│ 4. User selects DSR, confirms assignment                                      │
│ 5. Submit → POST `/api/company/sales/dsr-so-assignment/`                     │
│ 6. Backend creates DSRSOAssignment record                                    │
│ 7. Order status updated to "assigned"                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DSR LOADS ORDER (Mobile/App)                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. DSR logs in, sees assigned orders                                          │
│ 2. Selects order to load into vehicle/storage                                 │
│ 3. System transfers inventory:                                                │
│    - From: `warehouse.inventory_stock` (location)                            │
│    - To: `warehouse.dsr_storage` (DSR's virtual storage)                     │
│ 4. SalesOrder updated: `is_loaded=true`, `loaded_by_dsr_id`, `loaded_at`     │
│ 5. DSR can now deliver from their storage                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DSR DELIVERY & PAYMENT COLLECTION                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. DSR delivers to customer, records delivery                                 │
│ 2. If payment collected: DSRPaymentForm records amount                        │
│ 3. `payment_on_hand` increased for DSR                                        │
│ 4. Admin settles via DSRSettlementForm → creates DSRPaymentSettlement         │
│ 5. `payment_on_hand` reduced, cash transferred to company                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.6 Pending Customer Approval Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SR CREATES PENDING CUSTOMER                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. SR uses mobile app or web interface                                        │
│ 2. Navigates to My Pending Customers → New                                    │
│ 3. PendingCustomerForm.tsx opens (SR view)                                    │
│ 4. SR enters: customer name, contact, location, beat                          │
│ 5. Submit → `createPendingCustomer()` → POST `/api/company/sr/pending-customer/`│
│ 6. Backend: `PendingCustomerService.create()`                                 │
│    - Create in `sales.pending_customer` with status="pending"                 │
│    - Set `added_by_sr_id` to current SR                                       │
│ 7. Admin notified via notification system                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ADMIN APPROVES PENDING CUSTOMER                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Admin navigates to `/customers/pending-approvals`                         │
│ 2. PendingCustomerApprovals.tsx loads all pending customers                   │
│ 3. Admin reviews details, clicks "Approve"                                     │
│ 4. ApprovePendingCustomerModal.tsx opens                                       │
│ 5. Admin confirms: assign_to_sr_on_approval, credit_limit                      │
│ 6. Submit → `approvePendingCustomer()`                                       │
│    → POST `/api/company/sr/pending-customer/{id}/approve`                    │
│ 7. Backend:                                                                   │
│    - Create Customer in `sales.customer`                                        │
│    - Update PendingCustomer: status="approved", approved_customer_id         │
│    - If assign_to_sr: create Customer_SR_Assignment                          │
│    - Index in Elasticsearch                                                   │
│ 8. SR notified of approval                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Elasticsearch Integration (Customer Search)

**Index Structure:**
```json
{
  "customers_{company_id}": {
    "mappings": {
      "properties": {
        "customer_id": { "type": "integer" },
        "customer_name": { 
          "type": "text", 
          "analyzer": "standard",
          "fields": {
            "keyword": { "type": "keyword" },
            "ngram": { "type": "text", "analyzer": "ngram_analyzer" }
          }
        },
        "customer_code": { "type": "keyword" },
        "contact_phone": { "type": "keyword" },
        "beat_name": { "type": "keyword" },
        "company_id": { "type": "integer" }
      }
    }
  }
}
```

**Auto-Indexing:**
- **Create:** `CustomerService.create_customer()` → `es.index_customer()`
- **Update:** `CustomerService.update_customer()` → `es.index_customer()` (reindex)
- **Delete:** `CustomerService.delete_customer()` → `es.delete_customer()`

**Search Capabilities:**
- Full-text search on customer name (ngram for partial matches)
- Exact match on customer code and phone
- Fuzzy matching for typo tolerance
- Fallback to database if ES unavailable

**Endpoint:** `GET /api/company/sales/customer/search?query={search}&limit={n}`

---

### 6.2 Batch Tracking Integration

**Allocation Flow:**
```python
# When delivery is recorded with batch tracking enabled:
allocation_service = BatchAllocationService(db)
allocations = allocation_service.allocate(
    company_id=company_id,
    product_id=product_id,
    variant_id=variant_id,
    location_id=location_id,
    qty_needed=quantity,
    sales_order_detail_id=sod_id,
    user_id=user_id
)
```

**Valuation Modes:**
| Mode | Description | Use Case |
|------|-------------|----------|
| FIFO | First In, First Out | Standard inventory |
| LIFO | Last In, First Out | Tax optimization |
| WAC | Weighted Average Cost | Simplified accounting |

**Tables:**
- `inventory_batch.batch` - Master batch records
- `inventory_batch.sales_order_batch_allocation` - SO to batch links
- `inventory_batch.inventory_movement` - All stock movements

**API Endpoints:**
- `POST /api/company/sales/{id}/allocate` - Allocate batches for delivery
- `POST /api/company/sales/{id}/returns` - Process returns with batch tracking
- `GET /api/company/reports/stock-by-batch` - Batch stock report

---

### 6.3 Scheme/Claim Application

**Automatic Scheme Evaluation:**
```python
# During order creation, schemes are auto-evaluated:
claim_service = ClaimService(self.db)
evaluated_items = claim_service.evaluate_schemes(
    customer_id=sales_order.customer_id,
    items=details_data,
    order_date=sales_order.order_date
)
```

**Scheme Types Supported:**
- Buy X Get Y (same product)
- Buy X Get Y (different product)
- Percentage discount
- Fixed amount discount
- Free quantity

**Application:**
- Schemes stored in `claims.scheme` and `claims.scheme_rule`
- Applied scheme ID stored in `sales_order_detail.applied_scheme_id`
- Free quantities tracked separately from billable quantities

---

### 6.4 Multi-Tenant Considerations

**Tenant Isolation:**
- All entities have `company_id` FK to `security.app_client_company`
- API endpoints use `get_current_company_id()` dependency
- Repository queries always filter by `company_id`
- Elasticsearch indexes are per-company: `customers_{company_id}`

**Example:**
```python
@app.get("/api/company/sales/sales-order/")
def list_sales_orders(
    company_id: int = Depends(get_current_company_id),  # Extracted from JWT
    ...
):
    service = SalesOrderService(db)
    return service.list_sales_orders(company_id=company_id, ...)
```

---

### 6.5 Soft Delete & Cascade Behavior

**Soft Delete Pattern:**
- All entities have `is_deleted` boolean flag
- Repository queries filter `is_deleted=false` by default
- Deletion sets flag instead of removing row

**Cascade Behavior:**
```python
# SalesOrder.details - cascade delete
sales_order.details = relationship(
    "SalesOrderDetail",
    back_populates="sales_order",
    cascade="all, delete-orphan"  # Delete details when order deleted
)

# SalesOrder.payment_details - cascade delete
payment_details = relationship(
    "SalesOrderPaymentDetail",
    back_populates="sales_order",
    cascade="all, delete-orphan"
)
```

---

### 6.6 Import Validation & Error Reporting

**Excel Import Process:**
1. **Parse Phase:** Read Excel, validate format
2. **Validation Phase:** Check each row:
   - Required fields present
   - Country/state/city names resolve to IDs
   - Beat name exists
   - No duplicate customer codes
3. **All-or-Nothing:** If any row invalid, entire import rejected
4. **Error Report:** Detailed per-row error messages

**Import Endpoint:**
```python
@customer_router.post("/import-excel")
def import_customers_excel(
    file: UploadFile = File(...),
    request: CustomerImportRequest = Depends(),
    ...
)
```

**Error Response Format:**
```json
{
  "valid": false,
  "total_rows": 100,
  "errors": [
    {
      "row": 5,
      "customer_name": "Acme Corp",
      "field_errors": [
        {"field": "country_name", "message": "Country 'Xyzland' not found"}
      ]
    }
  ]
}
```

---

### 6.7 Unit of Measure (UOM) Conversions

**Automatic Conversion:**
```python
# Convert ordered quantity to base UOM for inventory
def convert_to_base(db: Session, quantity: Decimal, from_uom_id: int) -> Decimal:
    uom = db.query(UnitOfMeasure).get(from_uom_id)
    if uom and uom.conversion_factor:
        return quantity * uom.conversion_factor
    return quantity
```

**Applied During:**
- Stock availability validation
- Inventory deduction
- Batch allocation
- Returns processing

---

### 6.8 Price Calculation Logic

**Effective Total Amount:**
```python
@property
def effective_total_amount(self):
    total = 0
    for detail in self.details:
        # Skip free items
        if getattr(detail, "is_free_item", False):
            continue
        # Account for returns
        returned = detail.returned_quantity or 0
        effective_qty = detail.quantity - returned
        # Apply discount
        total += (effective_qty * detail.unit_price) - (detail.discount_amount or 0)
    return total
```

**Price Components:**
- Base unit price
- Discount amount
- Scheme discounts (free quantities)
- SR negotiated price (for consolidated orders)
- Price adjustments from consolidation

---

### 6.9 Role-Based Access Patterns

**Route Guards:**
| Route | Guard | Access |
|-------|-------|--------|
| `/sales/*` | `PrivateRoute` | Any authenticated user |
| `/customers/*` | `PrivateRoute` | Any authenticated user |
| `/sales-representatives/*` | `AdminRoute` | Admin only |
| `/dsr/*` | `AdminRoute` | Admin only |
| `/sr-orders/*` | `SRRoute` | SR users |
| `/dsr/my-assignments` | `DSRRoute` | DSR users |

**Backend Enforcement:**
```python
@sales_order_router.get("/{id}")
def get_sales_order(
    sales_order_id: int,
    company_id: int = Depends(get_current_company_id),  # Tenant isolation
    current_user: dict = Depends(get_current_user),
    ...
):
    # Only returns if order belongs to user's company
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| Customer | GET `/sales/customer/` | GET `/sales/customer/{id}` | POST `/sales/customer/` | PATCH `/sales/customer/{id}` | DELETE `/sales/customer/{id}` | Search, Batch Delete, Import |
| Beat | GET `/sales/beat/` | GET `/sales/beat/{id}` | POST `/sales/beat/` | PUT `/sales/beat/{id}` | DELETE `/sales/beat/{id}` | Assign/Unassign Customers |
| SalesOrder | GET `/sales/sales-order/` | GET `/sales/sales-order/{id}` | POST `/sales/sales-order/` | PATCH `/sales/sales-order/{id}` | DELETE `/sales/sales-order/{id}` | Cancel, Return, Reject, Allocate |
| SalesOrderDetail | GET `/sales/sales-order-detail/` | GET `/sales/sales-order-detail/{id}` | POST `/sales/sales-order-detail/` | PATCH `/sales/sales-order-detail/{id}` | DELETE `/sales/sales-order-detail/{id}` | Return Items |
| SalesOrderDelivery | GET `/sales/sales-order-delivery-detail/` | GET `/sales/sales-order-delivery-detail/{id}` | POST `/sales/sales-order-delivery-detail/` | PATCH `/sales/sales-order-delivery-detail/{id}` | DELETE `/sales/sales-order-delivery-detail/{id}` | - |
| SalesOrderPayment | GET `/sales/sales-order-payment-detail/` | GET `/sales/sales-order-payment-detail/{id}` | POST `/sales/sales-order-payment-detail/` | PATCH `/sales/sales-order-payment-detail/{id}` | DELETE `/sales/sales-order-payment-detail/{id}` | - |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|------------------|------------------|
| Get Sales List | `getSales()` | `GET /sales/sales-order/` |
| Create Sale | `createSale(data)` | `POST /sales/sales-order/` |
| Update Sale | `updateSale(id, data)` | `PATCH /sales/sales-order/{id}` |
| Delete Sale | `deleteSale(id)` | `DELETE /sales/sales-order/{id}` |
| Return Sale | `returnSalesOrder(id, data)` | `POST /sales/sales-order/{id}/return` |
| Create Payment | `createSalePayment(data)` | `POST /sales/sales-order-payment-detail/` |
| Create Delivery | `createSalesDelivery(data)` | `POST /sales/sales-order-delivery-detail/` |
| Get Customers | `getCustomers()` | `GET /sales/customer/` |
| Search Customers | `searchCustomers(query)` | `GET /sales/customer/search` |
| Create Customer | `createCustomer(data)` | `POST /sales/customer/` |
| Update Customer | `updateCustomer(id, data)` | `PATCH /sales/customer/{id}` |
| Delete Customer | `deleteCustomer(id)` | `DELETE /sales/customer/{id}` |
| Batch Delete | `batchDeleteCustomers(ids)` | `POST /sales/customer/batch-delete` |
| Get Beats | `getBeats()` | `GET /sales/beat/` |
| Create Beat | `createBeat(data)` | `POST /sales/beat/` |
| Update Beat | `updateBeat(id, data)` | `PUT /sales/beat/{id}` |
| Assign to Beat | `assignCustomersToBeat(id, ids)` | `POST /sales/beat/{id}/assign-customers` |
| Consolidate SR Orders | `consolidateSROrders(data)` | `POST /sales/consolidation/` |
| Validate Consolidation | `validateConsolidation(data)` | `POST /sales/consolidation/validate-consolidation` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| Models | `Shoudagor/app/models/sales.py` | All sales entities (17 tables) |
| Mixins | `Shoudagor/app/models/mixins.py` | OrderBase, OrderDetailBase, PaymentDetailBase, DeliveryDetailBase |
| Schemas | `Shoudagor/app/schemas/sales/customer.py` | Customer CRUD schemas |
| Schemas | `Shoudagor/app/schemas/sales/sales_order.py` | SalesOrder, Delivery, Payment schemas |
| Schemas | `Shoudagor/app/schemas/sales/sales_order_detail.py` | Line item schemas |
| Schemas | `Shoudagor/app/schemas/sales/beat.py` | Beat schemas |
| Schemas | `Shoudagor/app/schemas/sales/consolidation.py` | SR consolidation schemas |
| Services | `Shoudagor/app/services/sales/customer_service.py` | Customer business logic |
| Services | `Shoudagor/app/services/sales/sales_order_service.py` | SalesOrder CRUD + validation |
| Services | `Shoudagor/app/services/sales/beat_service.py` | Beat management |
| Services | `Shoudagor/app/services/sales/sales_order_detail_service.py` | Line item operations |
| Services | `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py` | Delivery tracking |
| Services | `Shoudagor/app/services/sales/sales_order_payment_detail_service.py` | Payment tracking |
| Repositories | `Shoudagor/app/repositories/sales/customer.py` | Customer data access |
| Repositories | `Shoudagor/app/repositories/sales/sales_order.py` | SalesOrder queries |
| Repositories | `Shoudagor/app/repositories/sales/sales_order_detail.py` | Detail queries |
| Repositories | `Shoudagor/app/repositories/sales/beat.py` | Beat queries |
| Repositories | `Shoudagor/app/repositories/sales/sales_order_delivery_detail.py` | Delivery queries |
| Repositories | `Shoudagor/app/repositories/sales/sales_order_payment_detail.py` | Payment queries |
| API | `Shoudagor/app/api/sales/customer.py` | Customer endpoints |
| API | `Shoudagor/app/api/sales/sales_order.py` | SalesOrder endpoints |
| API | `Shoudagor/app/api/sales/beat.py` | Beat endpoints |
| API | `Shoudagor/app/api/sales/sales_order_detail.py` | Detail endpoints |
| API | `Shoudagor/app/api/sales/sales_order_delivery_detail.py` | Delivery endpoints |
| API | `Shoudagor/app/api/sales/sales_order_payment_detail.py` | Payment endpoints |
| API | `Shoudagor/app/api/sales/batch_allocation.py` | Batch allocation endpoints |
| ES Service | `Shoudagor/app/services/customer_elasticsearch_service.py` | Search integration |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| Pages | `shoudagor_FE/src/pages/sales/Sales.tsx` | Sales orders list |
| Pages | `shoudagor_FE/src/pages/sales/new/AddSale.tsx` | New sale wrapper |
| Pages | `shoudagor_FE/src/pages/sales/ViewSaleDetails.tsx` | Sale detail view |
| Pages | `shoudagor_FE/src/pages/customers/Customers.tsx` | Customer management |
| Pages | `shoudagor_FE/src/pages/customers/new/AddCustomer.tsx` | New customer wrapper |
| Pages | `shoudagor_FE/src/pages/customers/PendingCustomerApprovals.tsx` | Approval workflow |
| Pages | `shoudagor_FE/src/pages/beats/Beats.tsx` | Beat management |
| Pages | `shoudagor_FE/src/pages/beats/new/index.tsx` | New beat wrapper |
| Pages | `shoudagor_FE/src/pages/sales/PhoneNumberSuggestions.tsx` | Phone update approvals |
| Forms | `shoudagor_FE/src/components/forms/SaleForm.tsx` | Sales order form |
| Forms | `shoudagor_FE/src/components/forms/CustomerForm.tsx` | Customer form |
| Forms | `shoudagor_FE/src/components/forms/BeatForm.tsx` | Beat form |
| Forms | `shoudagor_FE/src/components/forms/SalesPaymentForm.tsx` | Payment entry |
| Forms | `shoudagor_FE/src/components/forms/UnifiedDeliveryForm.tsx` | Delivery recording |
| Forms | `shoudagor_FE/src/components/forms/SalesReturnForm.tsx` | Return processing |
| Forms | `shoudagor_FE/src/components/forms/DSRAssignmentForm.tsx` | DSR assignment |
| Forms | `shoudagor_FE/src/components/forms/AssignCustomersToBeatForm.tsx` | Beat assignment |
| Forms | `shoudagor_FE/src/components/forms/AssignSRToCustomerForm.tsx` | SR assignment |
| Forms | `shoudagor_FE/src/components/forms/PendingCustomerForm.tsx` | SR creates pending customer |
| Forms | `shoudagor_FE/src/components/forms/PhoneSuggestionForm.tsx` | Phone update request |
| Shared | `shoudagor_FE/src/components/SalesFilter.tsx` | Sales filters |
| Shared | `shoudagor_FE/src/components/CustomerFilter.tsx` | Customer filters |
| Shared | `shoudagor_FE/src/components/BeatCustomersList.tsx` | Beat customer display |
| Shared | `shoudagor_FE/src/components/shared/ViewOrderDetails.tsx` | Order detail display |
| Shared | `shoudagor_FE/src/components/shared/OrderStatus.tsx` | Status badges |
| API | `shoudagor_FE/src/lib/api/salesApi.ts` | Sales API functions |
| API | `shoudagor_FE/src/lib/api/customerApi.ts` | Customer API functions |
| API | `shoudagor_FE/src/lib/api/beatApi.ts` | Beat API functions |
| API | `shoudagor_FE/src/lib/api/pendingCustomerApi.ts` | Pending customer API |
| Schemas | `shoudagor_FE/src/lib/schema/sales.ts` | Sales Zod schemas |
| Schemas | `shoudagor_FE/src/lib/schema/beat.ts` | Beat Zod schema |
| Routes | `shoudagor_FE/src/App.tsx` | Route definitions |

---

## 9. Appendix: Operation Counts

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|------------------------|---------------------|
| Customer | 5 | 6 (search, reindex, credit, batch delete, import, phone) | 8 | 4 (form, list, filter, import) |
| Beat | 5 | 2 (assign/unassign) | 7 | 3 (form, list, assign) |
| SalesOrder | 5 | 4 (cancel, return, reject, allocate) | 10 | 5 (form, list, payment, delivery, return) |
| SalesOrderDetail | 5 | 1 (return items) | 5 | 1 (inline in SaleForm) |
| SalesOrderDelivery | 5 | 0 | 4 | 1 (UnifiedDeliveryForm) |
| SalesOrderPayment | 5 | 0 | 4 | 1 (SalesPaymentForm) |
| SR Consolidation | - | 2 (validate, consolidate) | 3 | 2 (list, modal) |
| Pending Customer | 5 | 2 (approve, reject) | 5 | 3 (form, list, modal) |
| **TOTAL** | **35** | **17** | **46** | **20** |

---

## Key Indexes

### Database Indexes (Performance)

| Table | Index Name | Columns | Purpose |
|-------|-----------|---------|---------|
| sales_order | idx_so_order_number | order_number | Order lookups |
| sales_order | idx_so_company_status | company_id, status | Company filtering |
| sales_order | idx_so_customer_date | customer_id, order_date | Customer history |
| sales_order | idx_so_payment_status | payment_status | Payment queries |
| sales_order | idx_so_delivery_status | delivery_status | Delivery queries |
| sales_order | idx_so_consolidated | is_consolidated, consolidation_date | Consolidation reports |
| sales_order_detail | idx_sod_product_variant | product_id, variant_id | Product queries |
| sales_order_detail | idx_sod_sr_order_detail | sr_order_detail_id | SR detail lookups |
| customer | (via ES) | customer_name, code, phone | Full-text search |
| beat | - | beat_code | Unique code lookups |

---

*End of Sales Order Module Reference Documentation*
