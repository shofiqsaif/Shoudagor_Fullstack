# SR (Sales Representative) Module - Complete Reference

**Generated:** April 16, 2026

**Scope:** Full-stack analysis of the SR Module

**Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                    │
│  React 18 + TypeScript + TanStack Query + Zod + Tailwind CSS + shadcn/ui   │
├─────────────────────────────────────────────────────────────────────────────┤
│                              API LAYER                                      │
│          RESTful API via Axios (apiRequest pattern)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                           BACKEND LAYER                                     │
│  FastAPI + SQLAlchemy ORM + Pydantic Schemas + PostgreSQL                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                           DATABASE LAYER                                    │
│  PostgreSQL 15+ (Multi-tenant via company_id isolation)                     │
│  Schema: sales, reports, inventory, security, settings                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                        EXTERNAL SERVICES                                    │
│  Elasticsearch (optional - for product/customer search)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIP DIAGRAM                        │
└─────────────────────────────────────────────────────────────────────────────┘

sales.sales_representative (1)
    │
    ├──< (1:N) sales.sr_order
    │       │
    │       ├──< (1:N) sales.sr_order_detail ───────> (N:1) inventory.product
    │       │                                          (N:1) inventory.product_variant
    │       │                                          (N:1) inventory.unit_of_measure
    │       │
    │       └──> (N:1) sales.customer
    │
    ├──< (1:N) sales.sr_product_assignment ────────> (N:1) inventory.product
    │       │                                          (N:1) inventory.product_variant
    │       │
    │       └──< (1:N) sales.sr_product_assignment_price_history
    │
    ├──< (1:N) sales.customer_sr_assignment ──────> (N:1) sales.customer
    │       │                                          (N:1) sales.beat
    │
    ├──< (1:N) sales.pending_customer (added_by_sr_id)
    │       │
    │       └──> (N:1) sales.customer (approved_customer_id)
    │
    ├──< (1:N) sales.customer_phone_suggestion
    │
    ├──< (1:N) sales.sr_disbursement
    │
    └──> (1:N) security.app_user (sr_id link)

sales.delivery_sales_representative (DSR) (1)
    │
    ├──< (1:N) sales.dsr_so_assignment ───────────> (N:1) sales.sales_order
    ├──< (1:N) sales.dsr_payment_settlement
    └──< (1:1) sales.dsr_storage

reports.sr_program_channel (1)
    │
    └──< (1:N) reports.sr_program_customer_channel ─> (N:1) sales.customer

inventory.product_damage ────> (N:1) inventory.product
inventory.daily_cost_expense -> (N:1) inventory.variant_group
reports.sales_ledger ────────> (N:1) sales.customer
reports.sales_budget ────────> (N:1) inventory.variant_group
```

### 1.3 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend Framework | React | 18.x | UI rendering |
| Frontend Language | TypeScript | 5.x | Type safety |
| State Management | TanStack Query | 5.x | Server state, caching |
| Validation | Zod | 3.x | Schema validation |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| UI Components | shadcn/ui | - | Pre-built accessible components |
| Backend Framework | FastAPI | 0.115+ | API framework |
| Backend Language | Python | 3.10+ | Business logic |
| ORM | SQLAlchemy | 2.x | Database abstraction |
| Validation | Pydantic | 2.x | Schema validation |
| Database | PostgreSQL | 15+ | Primary datastore |
| Migration | Alembic | - | Schema versioning |

---

## 2. Entity Inventory

### 2.1 sales.sales_representative

Primary entity for managing sales representatives.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sr_id | Integer | PK, auto | Unique identifier |
| sr_name | String(200) | NOT NULL | Full name |
| sr_code | String(50) | UNIQUE, NOT NULL | Unique code (e.g., "SR001") |
| contact_email | String(100) | NULLABLE | Email address |
| contact_phone | String(20) | NULLABLE | Phone number |
| commission_amount | Numeric(18,2) | DEFAULT 0 | Current commission balance |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_active | Boolean | DEFAULT TRUE | Status flag |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by user ID |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by user ID |
| md | TIMESTAMP | AUTO UPDATE | Modified date |
| version | Integer | DEFAULT 1 | Optimistic locking |

**Indexes:**
- `idx_sales_representative_code` on `sr_code`

**Relationships:**
- `product_assignments` → `SR_Product_Assignment` (1:N)
- `customer_assignments` → `Customer_SR_Assignment` (1:N)
- `sr_orders` → `SR_Order` (1:N)
- `sales_order_details` → `SalesOrderDetail` (1:N)
- `users` → `User` (1:N)
- `phone_suggestions` → `CustomerPhoneSuggestion` (1:N)
- `disbursements` → `SRDisbursement` (1:N)

---

### 2.2 sales.sr_product_assignment

Maps products/variants to sales representatives with optional custom pricing.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| assignment_id | Integer | PK, auto | Unique identifier |
| sr_id | Integer | FK, NOT NULL | Sales representative |
| product_id | Integer | FK, NOT NULL | Product reference |
| variant_id | Integer | FK, NULLABLE | Variant reference |
| assigned_date | TIMESTAMP | DEFAULT NOW | Assignment date |
| assigned_sale_price | Numeric(18,4) | NULLABLE | Custom price for SR |
| price_effective_date | TIMESTAMP | NULLABLE | Price activation date |
| price_expiry_date | TIMESTAMP | NULLABLE | Price expiration date |
| allow_price_override | Boolean | DEFAULT TRUE | Can SR negotiate? |
| min_override_price | Numeric(18,4) | NULLABLE | Minimum negotiated price |
| max_override_price | Numeric(18,4) | NULLABLE | Maximum negotiated price |
| price_notes | Text | NULLABLE | Internal notes |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_sr_product_assignment_sr_id` on `sr_id`
- `idx_sr_product_assignment_product_variant` on `product_id`, `variant_id`
- `idx_sr_product_assignment_assigned_date` on `assigned_date`

**Properties:**
- `current_sale_price`: Computed effective price based on dates
- `is_price_active`: Boolean if price is currently valid

---

### 2.3 sales.sr_product_assignment_price_history

Audit trail for price changes on SR product assignments.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| history_id | Integer | PK, auto | Unique identifier |
| assignment_id | Integer | FK, NOT NULL | Reference to assignment |
| old_sale_price | Numeric(18,4) | NULLABLE | Previous price |
| new_sale_price | Numeric(18,4) | NOT NULL | New price set |
| effective_date | TIMESTAMP | NOT NULL | When price becomes active |
| expiry_date | TIMESTAMP | NULLABLE | When price expires |
| change_reason | String(500) | NULLABLE | Reason for change |
| changed_by | Integer | FK, NULLABLE | User who changed |
| changed_at | TIMESTAMP | DEFAULT NOW | Change timestamp |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |

**Indexes:**
- `idx_sr_product_assignment_price_history_assignment_id` on `assignment_id`
- `idx_sr_product_assignment_price_history_effective_date` on `effective_date`

---

### 2.4 sales.customer_sr_assignment

Maps customers to sales representatives.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| assignment_id | Integer | PK, auto | Unique identifier |
| sr_id | Integer | FK, NOT NULL | Sales representative |
| customer_id | Integer | FK, NOT NULL | Customer reference |
| assigned_date | TIMESTAMP | DEFAULT NOW | Assignment date |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_active | Boolean | DEFAULT TRUE | Status flag |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_customer_sr_assignment_sr_id` on `sr_id`
- `idx_customer_sr_assignment_customer_id` on `customer_id`

---

### 2.5 sales.sr_order

Orders created by sales representatives on behalf of customers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sr_order_id | Integer | PK, auto | Unique identifier |
| sr_id | Integer | FK, NOT NULL | Creating SR |
| customer_id | Integer | FK, NOT NULL | Target customer |
| order_number | String(50) | NOT NULL | Unique order number |
| order_date | TIMESTAMP | NOT NULL | Order date |
| status | String(20) | DEFAULT 'pending' | Order status |
| total_amount | Numeric(18,4) | NOT NULL | Order total |
| amount_paid | Numeric(18,4) | DEFAULT 0 | Amount received |
| location_id | Integer | FK, NULLABLE | Storage location |
| commission_disbursed | String(20) | DEFAULT 'pending' | Commission status |
| commission_amount | Numeric(18,4) | NULLABLE | Calculated commission |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |

**Indexes:**
- `idx_sr_order_sr_id` on `sr_id`
- `idx_sr_order_customer_id` on `customer_id`
- `idx_sr_order_status` on `status`

**Order Number Format:** `SR-YYYYMMDD-SRID-SEQ` (e.g., `SR-20251028-0009-0001`)

---

### 2.6 sales.sr_order_detail

Line items for SR orders.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sr_order_detail_id | Integer | PK, auto | Unique identifier |
| sr_order_id | Integer | FK, NOT NULL | Parent order |
| product_id | Integer | FK, NOT NULL | Product reference |
| variant_id | Integer | FK, NULLABLE | Variant reference |
| unit_of_measure_id | Integer | FK, NULLABLE | UOM reference |
| quantity | Numeric(18,4) | NOT NULL | Ordered quantity |
| unit_price | Numeric(18,4) | NOT NULL | Unit price |
| negotiated_price | Numeric(18,4) | NOT NULL | SR-negotiated price |
| sale_price | Numeric(18,4) | NULLABLE | Standard sale price |
| shipped_quantity | Numeric(18,4) | DEFAULT 0 | Delivered quantity |
| returned_quantity | Numeric(18,4) | DEFAULT 0 | Returned quantity |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_sr_order_detail_sr_order_id` on `sr_order_id`
- `idx_sr_order_detail_product_variant` on `product_id`, `variant_id`

---

### 2.7 sales.pending_customer

Customers added by SRs awaiting admin approval.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| pending_customer_id | Integer | PK, auto | Unique identifier |
| customer_name | String(200) | NOT NULL | Customer name |
| customer_code | String(50) | NULLABLE | Customer code |
| contact_person | String(100) | NULLABLE | Contact person |
| contact_email | String(100) | NULLABLE | Email |
| contact_phone | String(20) | NULLABLE | Phone |
| address | String(500) | NULLABLE | Address |
| country_id | Integer | FK, NULLABLE | Country |
| state_id | Integer | FK, NULLABLE | State |
| city_id | Integer | FK, NULLABLE | City |
| zip_code | String(20) | NULLABLE | ZIP code |
| credit_limit | Numeric(18,2) | NULLABLE | Credit limit |
| balance_amount | Numeric(18,2) | DEFAULT 0 | Opening balance |
| beat_id | Integer | FK, NULLABLE | Beat assignment |
| status | String(20) | DEFAULT 'pending' | Approval status |
| is_active | Boolean | DEFAULT TRUE | Active flag |
| added_by_sr_id | Integer | FK, NOT NULL | SR who added |
| approved_by | Integer | FK, NULLABLE | Admin who approved |
| approved_at | TIMESTAMP | NULLABLE | Approval timestamp |
| rejected_by | Integer | FK, NULLABLE | Admin who rejected |
| rejected_at | TIMESTAMP | NULLABLE | Rejection timestamp |
| rejection_reason | String(500) | NULLABLE | Rejection reason |
| assign_to_sr_on_approval | Boolean | DEFAULT TRUE | Auto-assign flag |
| assigned_sr_id | Integer | FK, NULLABLE | SR to assign |
| approved_customer_id | Integer | FK, NULLABLE | Final customer ID |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_pending_customer_status` on `status`
- `idx_pending_customer_sr_id` on `added_by_sr_id`
- `idx_pending_customer_company` on `company_id`
- `idx_pending_customer_approved_id` on `approved_customer_id`

---

### 2.8 sales.sr_disbursement

Tracks commission disbursements to SRs.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| disbursement_id | Integer | PK, auto | Unique identifier |
| sr_id | Integer | FK, NOT NULL | SR receiving payment |
| sr_order_id | Integer | FK, NULLABLE | Related order |
| disbursement_date | TIMESTAMP | DEFAULT NOW | Payment date |
| amount | Numeric(18,2) | NOT NULL | Disbursement amount |
| payment_method | String(50) | NULLABLE | Payment method |
| reference_number | String(100) | NULLABLE | Transaction reference |
| notes | String(500) | NULLABLE | Notes |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_sr_disbursement_sr_id` on `sr_id`
- `idx_sr_disbursement_sr_order_id` on `sr_order_id`
- `idx_sr_disbursement_date` on `disbursement_date`

---

### 2.9 sales.customer_phone_suggestion

SR-suggested phone number updates for customers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| suggestion_id | Integer | PK, auto | Unique identifier |
| customer_id | Integer | FK, NOT NULL | Target customer |
| sr_id | Integer | FK, NOT NULL | Suggesting SR |
| current_phone | String(20) | NULLABLE | Existing phone |
| suggested_phone | String(20) | NOT NULL | Proposed phone |
| suggestion_reason | String(500) | NULLABLE | Reason for change |
| status | String(20) | DEFAULT 'pending' | Review status |
| admin_user_id | Integer | FK, NULLABLE | Reviewing admin |
| admin_comments | String(500) | NULLABLE | Admin notes |
| processed_date | TIMESTAMP | NULLABLE | Processing date |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_customer_phone_suggestion_customer_id` on `customer_id`
- `idx_customer_phone_suggestion_sr_id` on `sr_id`
- `idx_customer_phone_suggestion_status` on `status`

---

### 2.10 reports.sr_program_channel

Channel master for SR Program workflow reports.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| channel_id | Integer | PK, auto | Unique identifier |
| channel_name | String(100) | NOT NULL | Channel name |
| display_order | Integer | DEFAULT 0 | Sort order |
| is_active | Boolean | DEFAULT TRUE | Active flag |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_sr_program_channel_company` on `company_id`
- `idx_sr_program_channel_active` on `company_id`, `is_active`

---

### 2.11 reports.sr_program_customer_channel

Maps customers to channels for SR Program reports.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| mapping_id | Integer | PK, auto | Unique identifier |
| customer_id | Integer | FK, NOT NULL | Customer reference |
| channel_id | Integer | FK, NOT NULL | Channel reference |
| company_id | Integer | FK, NOT NULL | Tenant isolation |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete |
| cb | Integer | NULLABLE | Created by |
| cd | TIMESTAMP | DEFAULT NOW | Created date |
| mb | Integer | NULLABLE | Modified by |
| md | TIMESTAMP | AUTO UPDATE | Modified date |

**Indexes:**
- `idx_sr_program_cc_company` on `company_id`
- `idx_sr_program_cc_customer` on `customer_id`
- `idx_sr_program_cc_channel` on `channel_id`

---

### 2.12 SR Reports Entities

#### inventory.product_damage
Tracks product damage/loss by date.

| Field | Type | Description |
|------|------|-------------|
| damage_id | Integer PK | Unique ID |
| damage_date | Date | Date of damage |
| product_id | Integer FK | Product reference |
| variant_id | Integer FK | Variant reference |
| quantity | Numeric(12,3) | Damaged quantity |
| unit_cost | Numeric(12,2) | Cost per unit |
| total_value | Numeric(14,2) | Total damage value |
| reason | String(100) | Damage reason |

#### reports.daily_cost_expense
Daily operational cost tracking.

| Field | Type | Description |
|------|------|-------------|
| cost_id | Integer PK | Unique ID |
| expense_date | Date | Date of expense |
| variant_group_id | Integer FK | Product group |
| van_cost | Numeric(14,2) | Van operational cost |
| oil_cost | Numeric(14,2) | Fuel cost |
| labour_cost | Numeric(14,2) | Labor cost |
| office_cost | Numeric(14,2) | Office expenses |
| other_cost | Numeric(14,2) | Miscellaneous |
| total_cost | Numeric(14,2) | Sum of all costs |

#### reports.sales_ledger
Manual ledger entries for reconciliation.

| Field | Type | Description |
|------|------|-------------|
| ledger_id | Integer PK | Unique ID |
| entry_date | Date | Entry date |
| entry_type | String(20) | Entry classification |
| order_amount | Numeric(14,2) | Order value |
| sales_amount | Numeric(14,2) | Sales value |
| payment_amount | Numeric(14,2) | Payment received |
| reference_type | String(20) | Source document type |
| reference_id | Integer | Source document ID |

#### reports.sales_budget
Monthly sales targets by product group.

| Field | Type | Description |
|------|------|-------------|
| budget_id | Integer PK | Unique ID |
| variant_group_id | Integer FK | Product group |
| budget_month | Date | Target month |
| budget_amount | Numeric(14,2) | Target amount |

---

## 3. Backend Operations Reference

### 3.1 Sales Representative Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sales-representative/` | `list_sales_representatives` | Paginated list with filters |
| Get Single | GET | `/api/company/sales/sales-representative/{sr_id}` | `get_sales_representative` | Get SR by ID |
| Create | POST | `/api/company/sales/sales-representative/` | `create_sales_representative` | Create new SR |
| Update | PATCH | `/api/company/sales/sales-representative/{sr_id}` | `update_sales_representative` | Update SR |
| Delete | DELETE | `/api/company/sales/sales-representative/{sr_id}` | `delete_sales_representative` | Soft delete SR |
| Search by Code | GET | `/api/company/sales/sales-representative/search/{sr_code}` | `get_sales_representative_by_code` | Find by code |

### 3.2 SR Product Assignment Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List by SR | GET | `/api/company/sales/sales-representative/{sr_id}/product-assignments/` | `list_sr_assignments` | Get SR's products |
| Create | POST | `/api/company/sales/sales-representative/{sr_id}/product-assignments/` | `create_sr_assignment` | Assign product |
| Get Single | GET | `/api/company/sales/sales-representative/{sr_id}/product-assignments/{assignment_id}` | `get_sr_assignment` | Get assignment |
| Update | PATCH | `/api/company/sales/sales-representative/{sr_id}/product-assignments/{assignment_id}` | `update_sr_assignment` | Update assignment |
| Delete | DELETE | `/api/company/sales/sales-representative/{sr_id}/product-assignments/{assignment_id}` | `delete_sr_assignment` | Unassign product |
| Bulk from Group | POST | `/api/company/sales/sales-representative/{sr_id}/product-assignments/bulk-from-group` | `bulk_assign_products_from_group` | Assign all variants from group |

### 3.3 SR Product Assignment Price Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| Update Price | PATCH | `/api/company/sr/product-assignments/{assignment_id}/price` | `assign_sale_price` | Set custom price |
| Price History | GET | `/api/company/sr/product-assignments/{assignment_id}/price-history` | `get_price_history` | View audit trail |
| Bulk Update | POST | `/api/company/sr/product-assignments/bulk-price-update` | `bulk_assign_prices` | Update multiple |
| Validate Price | GET | `/api/company/sr/product-assignments/{assignment_id}/validate-price` | `validate_price_override` | Check override bounds |
| SR Assigned Prices | GET | `/api/company/sr/product-assignments/sr/{sr_id}/assigned-prices` | `list_sr_assignments` | Get all with prices |

### 3.4 Customer-SR Assignment Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sales-representative/customer-assignments/` | `list_customer_assignments` | All assignments |
| Create | POST | `/api/company/sales/sales-representative/customer-assignments/` | `create_customer_assignment` | Assign customer |
| Get Single | GET | `/api/company/sales/sales-representative/customer-assignments/{assignment_id}` | `get_customer_assignment` | Get assignment |
| Update | PATCH | `/api/company/sales/sales-representative/customer-assignments/{assignment_id}` | `update_customer_assignment` | Update assignment |
| Delete | DELETE | `/api/company/sales/sales-representative/customer-assignments/{assignment_id}` | `delete_customer_assignment` | Unassign customer |
| Assign Beat | POST | `/api/company/sales/sales-representative/assign-beat-customers/` | `assign_beat_customers_to_sr` | Bulk assign by beat |

### 3.5 SR Order Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/sales/sr-orders/` | `list_sr_orders` | Paginated with filters |
| Get Single | GET | `/api/company/sales/sr-orders/{sr_order_id}` | `get_sr_order` | Get order by ID |
| Create | POST | `/api/company/sales/sr-orders/` | `create_sr_order` | Create new order |
| Update | PATCH | `/api/company/sales/sr-orders/{sr_order_id}` | `update_sr_order` | Update order |
| Delete | DELETE | `/api/company/sales/sr-orders/{sr_order_id}` | `delete_sr_order` | Soft delete |
| Unconsolidated by Customer | GET | `/api/company/sales/sr-orders/unconsolidated-by-customer` | `get_unconsolidated_orders_by_customer` | Group by customer |
| Bulk Approve | POST | `/api/company/sales/sr-orders/bulk-approve` | `bulk_approve_sr_orders` | Approve multiple |
| Bulk Details | POST | `/api/company/sales/sr-orders/bulk-details` | `get_sr_orders_by_ids` | Get multiple details |
| Disburse | POST | `/api/company/sales/sr-orders/{sr_order_id}/disburse` | `disburse_sr_order` | Pay commission |
| Bulk Disburse | POST | `/api/company/sales/sr-orders/bulk-disburse` | `bulk_disburse_sr_orders` | Pay multiple |
| Filtered Disburse | POST | `/api/company/sales/sr-orders/bulk-disburse-by-filters` | `bulk_disburse_sr_orders_by_filters` | Pay by criteria |
| List Disbursements | GET | `/api/company/sales/sr-orders/disbursements` | `list_disbursements` | View payment history |

### 3.6 Pending Customer Operations (SR Routes)

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List My | GET | `/api/company/sales/sales-representative/pending-customers/` | `list_my_pending_customers` | SR's own additions |
| Get My | GET | `/api/company/sales/sales-representative/pending-customers/{id}` | `get_pending_customer` | Get specific |
| Create | POST | `/api/company/sales/sales-representative/pending-customers/` | `create_pending_customer` | Add new customer |
| Update | PATCH | `/api/company/sales/sales-representative/pending-customers/{id}` | `update_pending_customer` | Edit pending |
| Delete | DELETE | `/api/company/sales/sales-representative/pending-customers/{id}` | `delete_pending_customer` | Remove pending |

### 3.7 Pending Customer Operations (Admin Routes)

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List All | GET | `/api/company/sales/sales-representative/admin/pending-customers/` | `list_all_pending_customers` | All company pending |
| Get | GET | `/api/company/sales/sales-representative/admin/pending-customers/{id}` | `get_pending_customer` | Get specific |
| Approve | POST | `/api/company/sales/sales-representative/admin/pending-customers/{id}/approve` | `approve_pending_customer` | Approve & create customer |
| Reject | POST | `/api/company/sales/sales-representative/admin/pending-customers/{id}/reject` | `reject_pending_customer` | Reject with reason |

### 3.8 SR Program Channel Operations

| Operation | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| List Channels | GET | `/api/company/sr-program/channels/` | Get all channels |
| Create Channel | POST | `/api/company/sr-program/channels/` | Add channel |
| Update Channel | PUT | `/api/company/sr-program/channels/{channel_id}` | Edit channel |
| Delete Channel | DELETE | `/api/company/sr-program/channels/{channel_id}` | Soft delete |
| List Mappings | GET | `/api/company/sr-program/channels/mappings` | Customer-channel pairs |
| Create Mapping | POST | `/api/company/sr-program/channels/mappings` | Map customer |
| Update Mapping | PUT | `/api/company/sr-program/channels/mappings/{mapping_id}` | Edit mapping |
| Delete Mapping | DELETE | `/api/company/sr-program/channels/mappings/{mapping_id}` | Remove mapping |
| Bulk Update | POST | `/api/company/sr-program/channels/mappings/bulk` | Replace all |
| Unmapped Customers | GET | `/api/company/sr-program/channels/unmapped-customers` | List without channel |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| Sales Representatives List | `/sales-representatives` | ✅ | Main SR management page |
| Add SR | `/sales-representatives/new` | ✅ | Create new SR form |
| View SR | `/sales-representatives/:id` | ✅ | SR detail view |
| SR Products | `/sr-products` | ✅ | SR product assignments |
| SR Assigned Products | `/sr-assigned-products` | ✅ | View assigned products |
| SR Admin Price Mgmt | `/sr-admin-price-management` | ✅ | Bulk price assignment |
| All SR Orders | `/sr-orders/all` | ✅ | Admin view all orders |
| My SR Orders | `/sr-orders` | ✅ | SR view own orders |
| Unconsolidated Orders | `/sr-orders/unconsolidated` | ✅ | Orders ready for consolidation |
| Consolidated Orders | `/sr-orders/consolidated` | ✅ | Already consolidated |
| Undisbursed Orders | `/sr-orders/undisbursed` | ✅ | Orders awaiting payment |
| SR Order Details | `/sr-orders/:id` | ✅ | View single order |
| New SR Order | `/sr-orders/new` | ✅ | Create SR order |
| My Pending Customers | `/my-pending-customers` | ✅ | SR's pending customers |
| Assigned Customers | `/sr-orders/assigned-customers` | ✅ | Customers assigned to SR |
| Disbursement History | `/sr-orders/disbursement-history` | ✅ | Commission payment log |
| SR Price Management | `/sr-orders/sr-price-management` | ✅ | SR views their prices |
| SR Products | `/sr-orders/sr-products` | ✅ | SR views assigned products |
| SR Dashboard | `/dashboard/sr` | ✅ | SR metrics dashboard |
| Admin SR Dashboard | `/dashboard/admin-sr` | ✅ | Admin SR analytics |
| SR Reports | `/reports/sr-reports` | ✅ | SR performance reports |
| SR Program Channel Admin | `/reports/sr-program-channel` | ✅ | Channel configuration |
| SR Program Workflow | `/reports/sr-program-workflow` | ✅ | Program execution view |

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| SRForm | `@/components/forms/SRForm.tsx` | Create/edit SR |
| AssignProductToSRForm | `@/components/forms/AssignProductToSRForm.tsx` | Assign products with pricing |
| AssignCustomerToSRForm | `@/components/forms/AssignCustomerToSRForm.tsx` | Assign customers |
| NewSROrder | `@/pages/sr-orders/new/NewSROrder.tsx` | Create/edit SR order |
| AssignProductWithPriceModal | `@/components/sr/AssignProductWithPriceModal.tsx` | Price assignment modal |
| SRDetailModal | `@/components/modals/SRDetailModal.tsx` | SR quick view |
| SRProductVariantDetailModal | `@/components/modals/SRProductVariantDetailModal.tsx` | Product details |

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| SRAssignedCustomersList | `@/components/SRAssignedCustomersList.tsx` | Display SR's customers |
| SRPriceHistory | `@/components/sr/SRPriceHistory.tsx` | Show price change history |
| SROrdersFilter | `@/components/SROrdersFilter.tsx` | Filter controls for orders |
| SRRoute | `@/components/SRRoute.tsx` | Route guard for SR access |
| OrderStatus | `@/components/shared/OrderStatus.tsx` | Status badge component |
| ConfirmDeleteDialog | `@/components/shared/ConfirmDeleteDialog.tsx` | Delete confirmation |
| ActiveInactiveStatus | `@/components/shared/ActiveInactiveStatus.tsx` | Status indicator |

### 4.4 Context Providers

The SR module uses TanStack Query for server state management rather than React Context. Key query keys:

| Query Key | Purpose |
|-----------|---------|
| `/sales-representatives` | SR list data |
| `/sr-orders` | SR orders data |
| `/sr-product-assignments` | Product assignments |
| `/pending-customers` | Pending customers |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `salesRepresentativeApi.ts` | `getSRs`, `createSR`, `updateSR`, `deleteSR`, `getSRAssignedProducts`, `assignProductToSR`, `unassignProductFromSR`, `assignBeatCustomersToSR`, `getSRAssignedCustomers`, `assignCustomerToSR`, `unassignCustomerFromSR` |
| `srOrderApi.ts` | `getSrOrders`, `getSrOrderById`, `createSrOrder`, `updateSrOrder`, `deleteSrOrder`, `getUnconsolidatedSROrders`, `disburseSrOrder`, `bulkDisburseSrOrders`, `bulkDisburseByFilters`, `bulkApproveSrOrders`, `getDisbursements` |
| `pendingCustomerApi.ts` | `getMyPendingCustomers`, `createPendingCustomer`, `updatePendingCustomer`, `deletePendingCustomer`, `getAllPendingCustomers`, `approvePendingCustomer`, `rejectPendingCustomer` |
| `srProductAssignmentPriceApi.ts` | `updateAssignmentPrice`, `getPriceHistory`, `bulkUpdatePrices`, `validatePriceOverride`, `getSrAssignedPrices` |
| `srDashboardApi.ts` | `getSRDashboardStats`, `getSRPerformanceMetrics` |
| `adminSRDashboardApi.ts` | `getAdminSRDashboardStats`, `getSRComparisonData` |
| `srReportsApi.ts` | `getSRReports`, `getSRProgramReport` |
| `srProgramReportsApi.ts` | `getProgramChannelData`, `getUndeliveredItems` |

### 4.6 Types & Zod Schemas

| Schema | File | Key Fields |
|--------|------|------------|
| `insertSRSchema` | `salesRepresentative.ts` | sr_name, sr_code, contact_email, contact_phone, is_active |
| `srOrderSchema` | `srOrder.ts` | sr_id, customer_id, order_number, status, total_amount, details |
| `insertSrOrderDetailSchema` | `srOrder.ts` | product_id, variant_id, unit_of_measure_id, quantity, negotiated_price |
| `pendingCustomerBaseSchema` | `srPendingCustomer.ts` | customer_name, contact_phone/email, country_id, state_id, city_id |
| `priceAssignmentSchema` | `srProductAssignmentPrice.ts` | assigned_sale_price, price_effective_date, allow_price_override, min/max_override_price |
| `AssignedProduct` | `srAssignedProducts.ts` | assignment_id, product_name, variant_name, assigned_sale_price, inventory_stock |

---

## 5. Interconnected Workflows

### 5.1 SR Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Admin navigates to Sales Representatives page                      │
│ → Component: SalesRepresentatives.tsx                                        │
│ → Route: /sales-representatives                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Admin clicks "Add SR" button                                        │
│ → Action: Navigate to /sales-representatives/new                             │
│ → Component: SRForm (create mode)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Admin fills SR details (name, code, contact info)                   │
│ → Validation: insertSRSchema (Zod)                                           │
│ → Fields: sr_name*, sr_code*, contact_email, contact_phone                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Form submission                                                      │
│ → API: createSR() in salesRepresentativeApi.ts                               │
│ → POST /api/company/sales/sales-representative/                               │
│ → Backend: SalesRepresentativeService.create_sales_representative()         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Database insert                                                      │
│ → Table: sales.sales_representative                                          │
│ → Constraint check: sr_code uniqueness per company                            │
│ → Record created with cb, cd, mb, md audit fields                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: User account linking (optional)                                     │
│ → Create User with sr_id pointing to new SR                                 │
│ → Enables SR login to mobile/web app                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 SR Order Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: SR logs in and navigates to New Order page                          │
│ → Route: /sr-orders/new or /sales-representatives (SR view)               │
│ → Component: NewSROrder.tsx or SR dashboard                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Select customer from assigned customers list                        │
│ → API: getSRAssignedCustomers() - returns customers assigned to this SR    │
│ → Validation: SR can only order for assigned customers                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Add order line items                                                 │
│ → Select from SR's assigned products                                         │
│ → API: getSRAssignedProducts()                                              │
│ → Enter quantity and negotiated price                                       │
│ → Validation: negotiated_price must be within min/max if set                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Submit order                                                         │
│ → API: createSrOrder() in srOrderApi.ts                                     │
│ → POST /api/company/sales/sr-orders/                                          │
│ → Body: {sr_id, customer_id, order_date, status: "pending", details: [...]}
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Backend processing                                                   │
│ → Service: SR_OrderService.create_sr_order()                                │
│ → Generate order number: SR-YYYYMMDD-SRID-SEQ                              │
│ → Validate SR and customer access                                           │
│ → Calculate total_amount from details                                       │
│ → Insert to sales.sr_order and sales.sr_order_detail                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Order approval workflow                                             │
│ → Status: "pending" → Admin reviews                                          │
│ → API: bulkApproveSrOrders() to approve multiple                           │
│ → Or individual approve via updateSrOrder()                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Order Consolidation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Identify unconsolidated orders                                       │
│ → API: getUnconsolidatedSROrders()                                          │
│ → GET /api/company/sales/sr-orders/unconsolidated-by-customer               │
│ → Returns orders grouped by customer                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Admin selects orders to consolidate                                 │
│ → Component: ConsolidatedSROrders.tsx or UnconsolidatedSROrders.tsx        │
│ → Select customer → select their unconsolidated orders                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Bulk fetch order details                                             │
│ → API: bulk-details endpoint (POST /sr-orders/bulk-details)                │
│ → Get full details for selected order IDs                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Create consolidated Sales Order                                     │
│ → Service: ConsolidationService (separate module)                          │
│ → Creates sales.sales_order with order_source = "sr_consolidated"           │
│ → Links SR order details via sr_order_detail_id references                  │
│ → Updates SR orders: status = "consolidated"                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Pending Customer Approval Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: SR creates pending customer                                           │
│ → Component: MyPendingCustomers.tsx (SR view)                              │
│ → API: createPendingCustomer()                                               │
│ → POST /sales/sales-representative/pending-customers/                       │
│ → Status: "pending"                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Admin reviews pending customers                                     │
│ → Component: PendingCustomers (admin view)                                 │
│ → API: getAllPendingCustomers()                                              │
│ → GET /sales/sales-representative/admin/pending-customers/                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3a: Admin approves customer                                             │
│ → API: approvePendingCustomer()                                              │
│ → POST /admin/pending-customers/{id}/approve                                 │
│ → Creates sales.customer record                                              │
│ → Optionally creates customer_sr_assignment                                 │
│ → Updates pending_customer: status="approved", approved_customer_id       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3b: Admin rejects customer (alternative)                              │
│ → API: rejectPendingCustomer()                                               │
│ → POST /admin/pending-customers/{id}/reject                                  │
│ → Requires: rejection_reason                                                 │
│ → Updates pending_customer: status="rejected", rejection fields            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Commission Disbursement Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Identify orders ready for disbursement                               │
│ → Commission status: "Ready" (calculated after order approved/consolidated)  │
│ → Route: /sr-orders/undisbursed                                            │
│ → Component: UndisbursedSROrders.tsx                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Calculate commission                                                │
│ → Formula: Based on negotiated_price vs sale_price difference              │
│ → Or: Fixed commission percentage configuration                              │
│ → Utils: calculateSrOrderCommission() in commission.ts                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Disburse commission                                                 │
│ → Individual: disburseSrOrder(sr_order_id, payment_method, ref)          │
│ → Bulk: bulkDisburseSrOrders([ids], payment_method, ref)                  │
│ → Or by filters: bulkDisburseByFilters(filters)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Backend processing                                                   │
│ → Creates sales.sr_disbursement record                                      │
│ → Updates sr_order.commission_disbursed = "Disbursed"                       │
│ → Updates sales_representative.commission_amount (deduct paid)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 SR Product Price Assignment

The SR module supports custom pricing per SR-product-variant combination:

```json
{
  "assignment_id": 1,
  "sr_id": 5,
  "product_id": 10,
  "variant_id": 3,
  "assigned_sale_price": 150.00,
  "price_effective_date": "2026-01-01",
  "price_expiry_date": "2026-12-31",
  "allow_price_override": true,
  "min_override_price": 140.00,
  "max_override_price": 160.00,
  "price_notes": "Special pricing for Q1"
}
```

**Price Resolution Logic:**
1. If `assigned_sale_price` exists and current date is within effective/expiry range, use it
2. Otherwise, fall back to product's standard `sale_price`
3. If `allow_price_override` is true, SR can negotiate within min/max bounds
4. Commission is calculated based on: `(negotiated_price - cost_price) * quantity`

**Price History Tracking:**
Every price change creates an entry in `sr_product_assignment_price_history`:
- Old vs new price
- Who changed it and when
- Effective dates
- Optional change reason

### 6.2 Order Number Generation

SR orders use a structured numbering system:

```python
Format: SR-YYYYMMDD-SRID-SEQ
Example: SR-20251028-0009-0001

Components:
- SR: Fixed prefix
- 20251028: Order date (YYYYMMDD)
- 0009: SR ID (zero-padded to 4 digits)
- 0001: Daily sequence (resets each day per SR)
```

**Implementation Details:**
```python
def generate_unique_order_number(self, sr_id: int, company_id: int) -> str:
    today = datetime.now().strftime("%Y%m%d")
    today_start = datetime.strptime(today, "%Y%m%d")
    
    # Count existing orders for this SR today
    existing_count = (
        self.db.query(func.count(SR_Order.sr_order_id))
        .filter(
            SR_Order.sr_id == sr_id,
            SR_Order.company_id == company_id,
            SR_Order.order_date >= today_start,
            SR_Order.is_deleted == False,
        )
        .scalar() or 0
    )
    
    sequence = existing_count + 1
    return f"SR-{today}-{sr_id:04d}-{sequence:04d}"
```

### 6.3 Bulk Operations

The SR module supports efficient bulk operations:

**Bulk Approve:**
```typescript
const result = await bulkApproveSrOrders([1, 2, 3, 4, 5]);
// Returns: { approved_count, failed_count, approved_orders[], failed_orders[] }
```

**Bulk Disburse by Filters:**
```typescript
const result = await bulkDisburseByFilters({
  sr_id: 5,
  status: "approved",
  order_date_start: "2026-01-01",
  order_date_end: "2026-01-31"
}, "Bank Transfer", "REF-001");
```

**Bulk Price Update:**
```typescript
const result = await bulkUpdatePrices({
  assignments: [
    { assignment_id: 1, assigned_sale_price: 100, allow_price_override: true },
    { assignment_id: 2, assigned_sale_price: 200, allow_price_override: false }
  ]
});
```

### 6.4 Commission Calculation

Commission calculation logic:

```typescript
// lib/utils/commission.ts
export function calculateSrOrderCommission(order: SrOrder): number {
  let totalCommission = 0;
  
  for (const detail of order.details) {
    // Method 1: Based on sale price vs negotiated price
    if (detail.sale_price && detail.negotiated_price) {
      const priceDifference = detail.sale_price - detail.negotiated_price;
      // Commission is percentage of the spread
      const commissionRate = 0.10; // 10% configurable
      totalCommission += priceDifference * detail.quantity * commissionRate;
    }
    
    // Method 2: Fixed commission per unit
    // const fixedCommission = 5.00; // ৶5 per unit
    // totalCommission += fixedCommission * detail.quantity;
  }
  
  return Math.max(0, totalCommission);
}
```

**Disbursement Status Flow:**
1. `pending` - Order created, not yet approved
2. `ready` - Order approved/consolidated, commission calculated
3. `disbursed` - Payment made to SR

### 6.5 Multi-tenant Data Isolation

All SR module queries include `company_id` filtering:

```python
# Repository pattern example
class SalesRepresentativeRepository:
    def list(self, company_id: int, ...):
        query = self.db.query(SalesRepresentative).filter(
            SalesRepresentative.company_id == company_id,
            SalesRepresentative.is_deleted == False
        )
        # ... additional filters
```

**Tenant Isolation Points:**
- API layer: `get_current_company_id()` dependency
- Service layer: All methods require `company_id` parameter
- Repository layer: All queries filter by `company_id`
- Database: Unique constraints include `company_id` (e.g., `uq_channel_company_name`)

### 6.6 Soft Delete Pattern

All SR entities use soft delete:

```sql
-- Instead of DELETE, UPDATE:
UPDATE sales.sales_representative 
SET is_deleted = TRUE, mb = :user_id, md = NOW() 
WHERE sr_id = :id;

-- All queries filter:
SELECT * FROM sales.sales_representative 
WHERE company_id = :company_id 
AND is_deleted = FALSE;
```

**Cascading Soft Deletes:**
- When SR is deleted, related assignments remain (orphan check prevents if active orders exist)
- Orders can be deleted only in "pending" or "draft" status

### 6.7 Pending Customer Workflow

The pending customer feature enables SRs to propose new customers:

**Validation Rules:**
- SR must have `sr_id` in their user profile
- Customer name is required
- Either phone or email must be provided
- Only "pending" records can be edited/deleted by SR

**Approval Actions:**
```json
{
  "assign_to_sr": true,
  "assigned_sr_id": null, // null = assign to adding SR
  "customer_name": "Modified Name", // Optional edits
  "contact_phone": "01712345678"
}
```

**Rejection Requirements:**
- Must provide `rejection_reason`
- SR sees rejection with reason in their pending list
- Rejected records remain for audit trail

### 6.8 Beat-based Customer Assignment

Assign all customers from a beat to an SR in one operation:

```typescript
// Assign all customers from beat_id=3 to sr_id=5
await assignBeatCustomersToSR({ sr_id: 5, beat_id: 3 });
```

**Business Rules:**
- All-or-none transaction: either all customers assigned or none
- Skips customers already assigned to the same SR
- Creates individual `customer_sr_assignment` records
- Returns detailed result with success/failure per customer

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| SalesRepresentative | GET / | GET /{id} | POST / | PATCH /{id} | DELETE /{id} | GET /search/{code} |
| SR_Product_Assignment | GET /{sr_id}/product-assignments/ | GET /{sr_id}/product-assignments/{id} | POST /{sr_id}/product-assignments/ | PATCH /{sr_id}/product-assignments/{id} | DELETE /{sr_id}/product-assignments/{id} | POST /bulk-from-group |
| Customer_SR_Assignment | GET /customer-assignments/ | GET /customer-assignments/{id} | POST /customer-assignments/ | PATCH /customer-assignments/{id} | DELETE /customer-assignments/{id} | POST /assign-beat-customers/ |
| SR_Order | GET /sr-orders/ | GET /sr-orders/{id} | POST /sr-orders/ | PATCH /sr-orders/{id} | DELETE /sr-orders/{id} | POST /bulk-approve, POST /bulk-disburse |
| PendingCustomer (SR) | GET /pending-customers/ | GET /pending-customers/{id} | POST /pending-customers/ | PATCH /pending-customers/{id} | DELETE /pending-customers/{id} | - |
| PendingCustomer (Admin) | GET /admin/pending-customers/ | GET /admin/pending-customers/{id} | - | POST /{id}/approve, POST /{id}/reject | - | - |
| SRDisbursement | GET /sr-orders/disbursements | - | POST /{id}/disburse | - | - | POST /bulk-disburse |
| SRProgramChannel | GET /sr-program/channels/ | - | POST / | PUT /{id} | DELETE /{id} | - |
| CustomerChannelMapping | GET /mappings | - | POST /mappings | PUT /mappings/{id} | DELETE /mappings/{id} | POST /mappings/bulk |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-------------------|------------------|
| Get SRs | `getSRs()` | GET /sales/sales-representative/ |
| Create SR | `createSR(sr)` | POST /sales/sales-representative/ |
| Update SR | `updateSR(id, sr)` | PATCH /sales/sales-representative/{id} |
| Delete SR | `deleteSR(id)` | DELETE /sales/sales-representative/{id} |
| Get SR Orders | `getSrOrders()` | GET /sales/sr-orders/ |
| Create SR Order | `createSrOrder(data)` | POST /sales/sr-orders/ |
| Get Unconsolidated | `getUnconsolidatedSROrders()` | GET /sales/sr-orders/unconsolidated-by-customer |
| Disburse Order | `disburseSrOrder(id)` | POST /sales/sr-orders/{id}/disburse |
| Bulk Disburse | `bulkDisburseSrOrders(ids)` | POST /sales/sr-orders/bulk-disburse |
| Get My Pending | `getMyPendingCustomers()` | GET /sales/sales-representative/pending-customers/ |
| Create Pending | `createPendingCustomer(data)` | POST /sales/sales-representative/pending-customers/ |
| Approve Pending | `approvePendingCustomer(id, data)` | POST /admin/pending-customers/{id}/approve |
| Get SR Products | `getSRAssignedProducts(srId)` | GET /sales/sales-representative/{id}/product-assignments/ |
| Assign Product | `assignProductToSR(srId, productId, variantId, priceData)` | POST /sales/sales-representative/{id}/product-assignments/ |
| Assign Beat | `assignBeatCustomersToSR(data)` | POST /sales/sales-representative/assign-beat-customers/ |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| Models | `Shoudagor/app/models/sales.py` | SalesRepresentative, SR_Order, SR_Order_Detail, SR_Product_Assignment, Customer_SR_Assignment, PendingCustomer, SRDisbursement, CustomerPhoneSuggestion |
| Models | `Shoudagor/app/models/sr_program.py` | SRProgramChannel, SRProgramCustomerChannel |
| Models | `Shoudagor/app/models/sr_reports.py` | ProductDamage, DailyCostExpense, SalesLedger, SalesBudget |
| Schemas | `Shoudagor/app/schemas/sr/sales_representative.py` | SR CRUD schemas |
| Schemas | `Shoudagor/app/schemas/sr/sr_product_assignment.py` | Product assignment schemas, price schemas |
| Schemas | `Shoudagor/app/schemas/sr/sr_order.py` | Order and detail schemas |
| Schemas | `Shoudagor/app/schemas/sr/customer_sr_assignment.py` | Customer assignment schemas |
| Schemas | `Shoudagor/app/schemas/sr/pending_customer.py` | Pending customer schemas |
| Schemas | `Shoudagor/app/schemas/sr/bulk_operations.py` | Bulk operation request/response |
| Schemas | `Shoudagor/app/schemas/sr/disbursement.py` | Disbursement schemas |
| Schemas | `Shoudagor/app/schemas/sr_program_reports.py` | Channel and mapping schemas |
| Services | `Shoudagor/app/services/sr/sales_representative_service.py` | SR CRUD, assignments |
| Services | `Shoudagor/app/services/sr/sr_order_service.py` | Order CRUD, disbursement |
| Services | `Shoudagor/app/services/sr/sr_product_assignment_service.py` | Price assignment |
| Services | `Shoudagor/app/services/sr/pending_customer_service.py` | Pending customer workflow |
| Services | `Shoudagor/app/services/sr/sr_dashboard_service.py` | SR metrics |
| Repositories | `Shoudagor/app/repositories/sr/sales_representative.py` | SR data access |
| Repositories | `Shoudagor/app/repositories/sr/sr_order.py` | Order data access |
| Repositories | `Shoudagor/app/repositories/sr/sr_product_assignment.py` | Assignment data access |
| Repositories | `Shoudagor/app/repositories/sr/pending_customer_repository.py` | Pending customer queries |
| API | `Shoudagor/app/api/sr/__init__.py` | Router composition |
| API | `Shoudagor/app/api/sr/sales_representative.py` | SR endpoints |
| API | `Shoudagor/app/api/sr/sr_product_assignment.py` | Product assignment endpoints |
| API | `Shoudagor/app/api/sr/sr_product_assignment_price.py` | Price management endpoints |
| API | `Shoudagor/app/api/sr/sr_order.py` | Order endpoints |
| API | `Shoudagor/app/api/sr/pending_customer.py` | Pending customer endpoints |
| API | `Shoudagor/app/api/sr/customer_sr_assignment.py` | Customer assignment endpoints |
| API | `Shoudagor/app/api/sr_program_admin.py` | Channel/mapping admin |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| Pages | `shoudagor_FE/src/pages/sales-representatives/SalesRepresentatives.tsx` | SR list |
| Pages | `shoudagor_FE/src/pages/sales-representatives/new/` | Add SR |
| Pages | `shoudagor_FE/src/pages/sales-representatives/SRAssignedProducts.tsx` | Product assignments |
| Pages | `shoudagor_FE/src/pages/sales-representatives/AdminSRPriceManagement.tsx` | Price management |
| Pages | `shoudagor_FE/src/pages/sr-orders/AllSROrders.tsx` | All orders (admin) |
| Pages | `shoudagor_FE/src/pages/sr-orders/SROrders.tsx` | My orders (SR) |
| Pages | `shoudagor_FE/src/pages/sr-orders/UnconsolidatedSROrders.tsx` | Unconsolidated |
| Pages | `shoudagor_FE/src/pages/sr-orders/ConsolidatedSROrders.tsx` | Consolidated |
| Pages | `shoudagor_FE/src/pages/sr-orders/UndisbursedSROrders.tsx` | Awaiting payment |
| Pages | `shoudagor_FE/src/pages/sr-orders/new/NewSROrder.tsx` | Create order |
| Pages | `shoudagor_FE/src/pages/sr-orders/MyPendingCustomers.tsx` | Pending customers |
| Pages | `shoudagor_FE/src/pages/sr-orders/AssignedCustomers.tsx` | Assigned customers |
| Pages | `shoudagor_FE/src/pages/sr-orders/DisbursementHistory.tsx` | Payment log |
| Pages | `shoudagor_FE/src/pages/dashboard/SRDashboard.tsx` | SR dashboard |
| Pages | `shoudagor_FE/src/pages/reports/SRReports.tsx` | SR reports |
| Pages | `shoudagor_FE/src/pages/reports/SRProgramChannelAdmin.tsx` | Channel admin |
| Forms | `shoudagor_FE/src/components/forms/SRForm.tsx` | SR create/edit |
| Forms | `shoudagor_FE/src/components/forms/AssignProductToSRForm.tsx` | Product assignment |
| Forms | `shoudagor_FE/src/components/forms/AssignCustomerToSRForm.tsx` | Customer assignment |
| Components | `shoudagor_FE/src/components/sr/AssignProductWithPriceModal.tsx` | Price assignment modal |
| Components | `shoudagor_FE/src/components/sr/SRPriceHistory.tsx` | Price history display |
| Components | `shoudagor_FE/src/components/SRAssignedCustomersList.tsx` | Assigned customers list |
| Components | `shoudagor_FE/src/components/SROrdersFilter.tsx` | Order filters |
| API | `shoudagor_FE/src/lib/api/salesRepresentativeApi.ts` | SR API functions |
| API | `shoudagor_FE/src/lib/api/srOrderApi.ts` | Order API functions |
| API | `shoudagor_FE/src/lib/api/pendingCustomerApi.ts` | Pending customer API |
| API | `shoudagor_FE/src/lib/api/srProductAssignmentPriceApi.ts` | Price API |
| Schemas | `shoudagor_FE/src/lib/schema/salesRepresentative.ts` | SR Zod schemas |
| Schemas | `shoudagor_FE/src/lib/schema/srOrder.ts` | Order Zod schemas |
| Schemas | `shoudagor_FE/src/lib/schema/srPendingCustomer.ts` | Pending customer schemas |
| Schemas | `shoudagor_FE/src/lib/schema/srAssignedProducts.ts` | Product assignment types |
| Schemas | `shoudagor_FE/src/lib/schema/srProductAssignmentPrice.ts` | Price assignment schemas |

---

## 9. Appendix: Operation Counts

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|----------------------|---------------------|
| SalesRepresentative | 5 | 2 (search, stats) | 6 | 4 (list, form, view, dashboard) |
| SR_Product_Assignment | 5 | 3 (bulk-from-group, price-mgmt, history) | 4 | 3 (assign form, price modal, history) |
| SR_Product_Assignment_Price | 2 | 3 (bulk-update, validate, history) | 4 | 2 (price modal, history) |
| Customer_SR_Assignment | 5 | 1 (beat-assign) | 3 | 2 (assign form, list) |
| SR_Order | 5 | 8 (bulk-approve, bulk-disburse, filter-disburse, unconsolidated, disbursements, stats) | 9 | 6 (list, detail, create, undisbursed, consolidated, filters) |
| SR_Order_Detail | 4 | 1 (bulk) | 2 | 2 (order form, detail view) |
| PendingCustomer | 5 | 2 (approve, reject) | 7 | 3 (list, form, admin review) |
| SRDisbursement | 1 | 4 (disburse, bulk, filter, list) | 4 | 2 (disburse dialog, history) |
| CustomerPhoneSuggestion | 4 | 1 (approval) | 3 | 1 (suggestion form) |
| SRProgramChannel | 4 | 1 (bulk mapping) | 4 | 2 (channel admin, mapping) |
| **TOTAL** | **40** | **26** | **46** | **31** |

---

## Quick Navigation

- **Backend Models**: `Shoudagor/app/models/sales.py` (lines 323-860)
- **Backend API**: `Shoudagor/app/api/sr/`
- **Frontend Pages**: `shoudagor_FE/src/pages/sales-representatives/`, `shoudagor_FE/src/pages/sr-orders/`
- **Frontend API**: `shoudagor_FE/src/lib/api/salesRepresentativeApi.ts`, `shoudagor_FE/src/lib/api/srOrderApi.ts`
- **Frontend Schemas**: `shoudagor_FE/src/lib/schema/salesRepresentative.ts`, `shoudagor_FE/src/lib/schema/srOrder.ts`

---

*End of SR Module Complete Reference*
