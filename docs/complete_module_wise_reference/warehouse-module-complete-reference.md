# Warehouse Module - Complete Reference Guide

**Generated:** April 16, 2026  
**Scope:** Full-stack analysis of the Warehouse Management Module  
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
│                           FRONTEND LAYER                                     │
│  React + TypeScript + Tailwind CSS + shadcn/ui + React Query + Zod          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │    Pages    │ │  Components │ │   Contexts  │ │    Hooks    │          │
│  │             │ │             │ │             │ │             │          │
│  │ Inventory   │ │StorageLoc   │ │  Auth       │ │useFreeze    │          │
│  │ StockTrans  │ │Form         │ │  Settings   │ │Refresh      │          │
│  │ StorageLoc  │ │StockAdjForm  │ │  ProductSel │ │useAuth       │          │
│  │ DSRStor     │ │StockTransForm│ │             │ │             │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
└─────────┼───────────────┼───────────────┼───────────────┼─────────────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API LAYER (Frontend)                               │
│  axios + custom apiRequest wrapper + React Query                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │warehousesApi│ │storageLocApi│ │inventoryApi │ │dsrStorageApi│          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
└─────────┼───────────────┼───────────────┼───────────────┼─────────────────┘
          │               │               │               │
          └───────────────┴───────────────┴───────────────┘
                              │
                              ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND LAYER                                      │
│  FastAPI + SQLAlchemy + Pydantic + PostgreSQL                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         API ROUTES                                   │   │
│  │  /api/company/warehouse/storage-locations/*                         │   │
│  │  /api/company/warehouse/inventory-stock/*                         │   │
│  │  /api/company/warehouse/stock-transfer/*                           │   │
│  │  /api/company/warehouse/dsr-storage/*                               │   │
│  │  /api/company/warehouse/dsr-stock-transfer/*                        │   │
│  │  /api/company/inventory/batches/*                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Services  │ │ Repositories│ │   Schemas   │ │   Models    │          │
│  │             │ │             │ │             │ │             │          │
│  │WarehouseSvc │ │StorageLocRep│ │StorageLocSch│ │Warehouse    │          │
│  │StockTransSvc│ │InvStockRep  │ │InvStockSch  │ │StorageLoc   │          │
│  │BatchAllocSvc│ │StockTransRep│ │StockTransSch│ │InvStock     │          │
│  │InvSyncSvc   │ │DSRStorageRep │ │DSRStorageSch│ │DSRStorage   │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
└─────────┼───────────────┼───────────────┼───────────────┼─────────────────┘
          │               │               │               │
          └───────────────┴───────────────┴───────────────┘
                              │
                              ▼ SQL
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                       │
│  PostgreSQL + SQLAlchemy ORM + Alembic Migrations                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Schemas: warehouse, inventory, transaction, sales, settings...     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ENTITY RELATIONSHIP DIAGRAM                          │
└─────────────────────────────────────────────────────────────────────────────┘

warehouse.warehouse (1)
    │
    │ 1:N
    ▼
warehouse.storage_location (*)
    │
    │ 1:N                                    ┌──────────────────────────┐
    ▼                                        │   inventory.product      │
warehouse.inventory_stock (*) ────────N:M────┤   inventory.product_variant│
    │                                        └──────────────────────────┘
    │ N:M (via batches)
    ▼
inventory.batch (*)
    │
    │ 1:N
    ▼
inventory.inventory_movement (*)

warehouse.stock_transfer (1) ──────1:N────── warehouse.stock_transfer_details (*)
    │                                            │
    │                                            │ N:M
    │                                            ▼
    └─────────────────────────────────────────► inventory.product
                                               inventory.product_variant

sales.delivery_sales_representative (1) ─────1:1────── warehouse.dsr_storage (*)
                                                          │
                                                          │ 1:N
                                                          ▼
                                              warehouse.dsr_inventory_stock (*)

warehouse.dsr_stock_transfer (1) ─────1:N─── warehouse.dsr_stock_transfer_detail (*)
    │
    │ (Source/Target: either storage_location OR dsr_storage)
    ▼
warehouse.storage_location (*)
warehouse.dsr_storage (*)

purchase.purchase_order_detail (*) ─────N:M────── inventory.batch (*)

sales.sales_order_detail (*) ─────N:M (allocations)────── inventory.batch (*)

settings.app_client_company (1)
    │
    │ 1:N (isolated per company)
    ▼
warehouse.warehouse, storage_location, inventory_stock, dsr_storage...
```

**Cardinality Summary:**
- Warehouse 1:N StorageLocation
- StorageLocation 1:N InventoryStock
- StorageLocation 1:N StockTransfer (as source)
- StockTransfer 1:N StockTransferDetails
- Product/Variant N:M InventoryStock (via location)
- Product/Variant N:M Batch
- Batch 1:N InventoryMovement
- DSR 1:1 DSRStorage
- DSRStorage 1:N DSRInventoryStock
- Company 1:N (all warehouse entities - multi-tenant)

### 1.3 Technology Stack

| Layer | Technology | Version/Details |
|-------|------------|-----------------|
| **Frontend Framework** | React | v18+ with TypeScript |
| **Build Tool** | Vite | Fast development server |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **UI Components** | shadcn/ui | Radix-based accessible components |
| **Form Handling** | React Hook Form + Zod | Schema validation |
| **State Management** | React Query (TanStack) | Server state caching |
| **HTTP Client** | Axios | Wrapped with custom apiRequest |
| **Backend Framework** | FastAPI | Python async web framework |
| **ORM** | SQLAlchemy | v2.0+ with async support |
| **Validation** | Pydantic | Request/response schemas |
| **Database** | PostgreSQL | v14+ with schema isolation |
| **Migrations** | Alembic | Database versioning |
| **Search (optional)** | Elasticsearch | For product/catalog search |
| **File Storage** | AWS S3 | Product images, documents |

---

## 2. Entity Inventory

### 2.1 warehouse.warehouse

**Table:** `warehouse.warehouse`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| warehouse_id | Integer | PK, Auto-increment | Unique identifier |
| warehouse_name | String(100) | NOT NULL | Warehouse name |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant isolation |
| address | String(255) | Nullable | Street address |
| country_id | Integer | FK → settings.country | Country reference |
| state_id | Integer | FK → settings.state | State/province reference |
| city_id | Integer | FK → settings.city | City reference |
| zip_code | String(20) | Nullable | Postal code |
| is_active | Boolean | DEFAULT TRUE | Active status |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Relationships:**
- `company` → `AppClientCompany` (N:1)
- `country` → `Country` (N:1)
- `state` → `State` (N:1)
- `city` → `City` (N:1)
- `storage_locations` → `StorageLocation` (1:N)

---

### 2.2 warehouse.storage_location

**Table:** `warehouse.storage_location`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| location_id | Integer | PK, Auto-increment | Unique identifier |
| warehouse_id | Integer | FK → warehouse.warehouse | Parent warehouse |
| location_name | String(100) | NOT NULL | Location name |
| location_code | String(50) | NOT NULL | Unique code |
| location_type | String(20) | NOT NULL | Type (e.g., 'rack', 'bin') |
| max_capacity | Integer | Nullable | Maximum storage capacity |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant |
| is_active | Boolean | DEFAULT TRUE | Active status |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_storage_location_warehouse_id` - For warehouse filtering
- `idx_storage_location_code` - For code lookups

**Relationships:**
- `warehouse` → `Warehouse` (N:1)
- `company` → `AppClientCompany` (N:1)
- `inventory_stocks` → `InventoryStock` (1:N)
- `stock_transfers` → `StockTransfer` (1:N, as source)
- `purchase_orders` → `PurchaseOrder` (1:N)
- `sales_orders` → `SalesOrder` (1:N)
- `inventory_adjustments` → `InventoryAdjustment` (1:N)
- `batches` → `Batch` (1:N)

---

### 2.3 warehouse.inventory_stock

**Table:** `warehouse.inventory_stock`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| stock_id | Integer | PK, Auto-increment | Unique identifier |
| product_id | Integer | FK → inventory.product | Product reference |
| variant_id | Integer | FK → inventory.product_variant | Variant reference (nullable) |
| location_id | Integer | FK → warehouse.storage_location | Location reference |
| quantity | Numeric(18,4) | NOT NULL | Current stock quantity |
| uom_id | Integer | FK → inventory.unit_of_measure | Unit of measure |
| last_stock_take_date | TIMESTAMP | Nullable | Last physical count |
| version | Integer | DEFAULT 1, NOT NULL | Optimistic locking version |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_inv_stock_product_variant_location` - Composite for stock lookups

**Relationships:**
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `location` → `StorageLocation` (N:1)
- `uom` → `UnitOfMeasure` (N:1)

---

### 2.4 warehouse.stock_transfer

**Table:** `warehouse.stock_transfer`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| transfer_id | Integer | PK, Auto-increment | Unique identifier |
| transfer_code | String(50) | UNIQUE, NOT NULL | Auto-generated code |
| transfer_date | TIMESTAMP | NOT NULL | Transfer date |
| status | String(20) | DEFAULT 'COMPLETED' | Transfer status |
| source_location_id | Integer | FK → warehouse.storage_location | Source location |
| notes | Text | Nullable | Transfer notes |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_stock_transfer_code` - Code lookups
- `idx_stock_transfer_source_location` - Source filtering
- `idx_stock_transfer_date` - Date range queries

**Relationships:**
- `source_location` → `StorageLocation` (N:1)
- `details` → `StockTransferDetails` (1:N, cascade delete)
- `company` → `AppClientCompany` (N:1)

---

### 2.5 warehouse.stock_transfer_details

**Table:** `warehouse.stock_transfer_details`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| detail_id | Integer | PK, Auto-increment | Unique identifier |
| transfer_id | Integer | FK → warehouse.stock_transfer | Parent transfer |
| target_location_id | Integer | FK → warehouse.storage_location | Destination |
| product_id | Integer | FK → inventory.product | Product |
| variant_id | Integer | FK → inventory.product_variant | Variant (nullable) |
| quantity | Numeric(18,4) | NOT NULL | Transfer quantity |
| uom_id | Integer | FK → inventory.unit_of_measure | Unit of measure |
| notes | Text | Nullable | Detail notes |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_stock_transfer_details_transfer_id` - Transfer filtering
- `idx_stock_transfer_details_target_location` - Target filtering
- `idx_stock_transfer_details_product_variant` - Product lookups

**Relationships:**
- `stock_transfer` → `StockTransfer` (N:1)
- `target_location` → `StorageLocation` (N:1)
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `uom` → `UnitOfMeasure` (N:1)

---

### 2.6 warehouse.dsr_storage

**Table:** `warehouse.dsr_storage`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| dsr_storage_id | Integer | PK, Auto-increment | Unique identifier |
| dsr_id | Integer | FK → sales.delivery_sales_representative, UNIQUE | One-to-one with DSR |
| storage_name | String(100) | NOT NULL | Storage name |
| storage_code | String(50) | NOT NULL | Unique code |
| storage_type | String(20) | NOT NULL | Type (vehicle/shop/warehouse) |
| max_capacity | Integer | Nullable | Maximum capacity |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant |
| is_active | Boolean | DEFAULT TRUE | Active status |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `uq_dsr_storage_dsr_id` - Unique constraint on dsr_id
- `idx_dsr_storage_code` - Code lookups

**Relationships:**
- `dsr` → `DeliverySalesRepresentative` (1:1)
- `company` → `AppClientCompany` (N:1)
- `inventory_stocks` → `DSRInventoryStock` (1:N)

---

### 2.7 warehouse.dsr_inventory_stock

**Table:** `warehouse.dsr_inventory_stock`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| stock_id | Integer | PK, Auto-increment | Unique identifier |
| product_id | Integer | FK → inventory.product | Product |
| variant_id | Integer | FK → inventory.product_variant | Variant (nullable) |
| dsr_storage_id | Integer | FK → warehouse.dsr_storage | DSR storage |
| quantity | Numeric(18,4) | NOT NULL | Current quantity |
| last_stock_take_date | TIMESTAMP | Nullable | Last count |
| uom_id | Integer | FK → inventory.unit_of_measure | Unit of measure |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_dsr_inventory_stock_product_variant_storage` - Composite lookup

**Relationships:**
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `dsr_storage` → `DSRStorage` (N:1)
- `uom` → `UnitOfMeasure` (N:1)

---

### 2.8 warehouse.dsr_stock_transfer

**Table:** `warehouse.dsr_stock_transfer`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| transfer_id | Integer | PK, Auto-increment | Unique identifier |
| transfer_code | String(50) | UNIQUE, NOT NULL | Auto-generated code |
| transfer_date | TIMESTAMP | NOT NULL | Transfer date |
| status | String(20) | DEFAULT 'COMPLETED' | Transfer status |
| source_location_id | Integer | FK → warehouse.storage_location | Source (nullable) |
| source_dsr_storage_id | Integer | FK → warehouse.dsr_storage | Source DSR (nullable) |
| target_location_id | Integer | FK → warehouse.storage_location | Target (nullable) |
| target_dsr_storage_id | Integer | FK → warehouse.dsr_storage | Target DSR (nullable) |
| notes | Text | Nullable | Transfer notes |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_dsr_stock_transfer_code` - Code lookups
- `idx_dsr_stock_transfer_date` - Date filtering
- `idx_dsr_stock_transfer_source_location` - Source filtering
- `idx_dsr_stock_transfer_source_dsr_storage` - DSR source
- `idx_dsr_stock_transfer_target_location` - Target filtering
- `idx_dsr_stock_transfer_target_dsr_storage` - DSR target

**Relationships:**
- `source_location` → `StorageLocation` (N:1, optional)
- `source_dsr_storage` → `DSRStorage` (N:1, optional)
- `target_location` → `StorageLocation` (N:1, optional)
- `target_dsr_storage` → `DSRStorage` (N:1, optional)
- `details` → `DSRStockTransferDetail` (1:N, cascade)
- `company` → `AppClientCompany` (N:1)

**Validation:** Exactly one source and one target must be specified (mutually exclusive between location and DSR storage).

---

### 2.9 warehouse.dsr_stock_transfer_detail

**Table:** `warehouse.dsr_stock_transfer_detail`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| detail_id | Integer | PK, Auto-increment | Unique identifier |
| transfer_id | Integer | FK → warehouse.dsr_stock_transfer | Parent transfer |
| product_id | Integer | FK → inventory.product | Product |
| variant_id | Integer | FK → inventory.product_variant | Variant (nullable) |
| quantity | Numeric(18,4) | NOT NULL | Transfer quantity |
| notes | Text | Nullable | Detail notes |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_dsr_stock_transfer_detail_transfer_id` - Transfer filtering
- `idx_dsr_stock_transfer_detail_product_variant` - Product lookups

**Relationships:**
- `transfer` → `DSRStockTransfer` (N:1)
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)

---

### 2.10 inventory.batch

**Table:** `inventory.batch`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| batch_id | Integer | PK, Auto-increment | Unique identifier |
| batch_number | String(50) | NOT NULL | Unique batch number |
| product_id | Integer | FK → inventory.product | Product |
| variant_id | Integer | FK → inventory.product_variant | Variant (nullable) |
| location_id | Integer | FK → warehouse.storage_location | Storage location |
| purchase_order_detail_id | Integer | FK → purchase.purchase_order_detail | Source PO line |
| supplier_id | Integer | FK → procurement.supplier | Supplier |
| initial_quantity | Numeric(18,4) | NOT NULL | Original quantity |
| remaining_quantity | Numeric(18,4) | NOT NULL | Current quantity |
| unit_cost | Numeric(18,4) | NOT NULL | Cost per unit |
| received_date | TIMESTAMP | NOT NULL | Receipt date |
| expiry_date | TIMESTAMP | Nullable | Expiration date |
| status | String(20) | DEFAULT 'ACTIVE' | ACTIVE/DEPLETED/EXPIRED |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_batch_product_variant` - Product lookups
- `idx_batch_location` - Location filtering
- `idx_batch_status` - Status filtering
- `idx_batch_received_date` - Date range queries
- `idx_batch_expiry_date` - Expiry monitoring

**Relationships:**
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `location` → `StorageLocation` (N:1)
- `purchase_order_detail` → `PurchaseOrderDetail` (N:1)
- `supplier` → `Supplier` (N:1)
- `company` → `AppClientCompany` (N:1)
- `movements` → `InventoryMovement` (1:N)
- `allocations` → `SalesOrderBatchAllocation` (1:N)

---

### 2.11 inventory.inventory_movement

**Table:** `inventory.inventory_movement`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| movement_id | Integer | PK, Auto-increment | Unique identifier |
| batch_id | Integer | FK → inventory.batch | Parent batch |
| movement_type | String(20) | NOT NULL | INBOUND/OUTBOUND/ADJUSTMENT |
| quantity | Numeric(18,4) | NOT NULL | Movement quantity |
| reference_type | String(50) | Nullable | Source document type |
| reference_id | Integer | Nullable | Source document ID |
| reference_detail_id | Integer | Nullable | Source line item ID |
| unit_cost | Numeric(18,4) | Nullable | Cost at movement time |
| total_cost | Numeric(18,4) | Nullable | Total movement cost |
| location_id | Integer | FK → warehouse.storage_location | Location |
| company_id | Integer | FK → settings.app_client_company | Multi-tenant |
| is_deleted | Boolean | DEFAULT FALSE | Soft delete flag |
| cb | Integer | NOT NULL | Created by user ID |
| mb | Integer | NOT NULL | Modified by user ID |
| cd | TIMESTAMP | DEFAULT NOW() | Creation date |
| md | TIMESTAMP | DEFAULT NOW() | Modification date |

**Indexes:**
- `idx_movement_batch_id` - Batch filtering
- `idx_movement_reference` - Reference lookups
- `idx_movement_date` - Date range queries

**Relationships:**
- `batch` → `Batch` (N:1)
- `location` → `StorageLocation` (N:1)
- `company` → `AppClientCompany` (N:1)

---

## 3. Backend Operations Reference

### 3.1 Storage Location Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/warehouse/storage-locations/` | `WarehouseService.list_storage_locations()` | Paginated list with filters |
| Get Single | GET | `/api/company/warehouse/storage-locations/{id}` | `StorageLocationRepository.get()` | Get by ID |
| Create | POST | `/api/company/warehouse/storage-locations/` | `WarehouseService.create_storage_location()` | Create new location |
| Update | PATCH | `/api/company/warehouse/storage-locations/{id}` | `WarehouseService.update_storage_location()` | Update location |
| Delete | DELETE | `/api/company/warehouse/storage-locations/{id}` | `WarehouseService.delete_storage_location()` | Soft delete (blocks if stock exists) |
| **Special: Filter** | GET | `/api/company/warehouse/storage-locations/?warehouse_id=X` | `WarehouseService.list_storage_locations()` | Filter by warehouse |
| **Special: Sort** | GET | `/api/company/warehouse/storage-locations/?sort_by=cd_desc` | `WarehouseService.list_storage_locations()` | Multi-field sorting |

**Filter Parameters:**
- `warehouse_id` - Filter by warehouse
- `location_type` - Filter by type
- `is_active` - Filter by status
- `cd_start`, `cd_end` - Date range
- `max_capacity_min`, `max_capacity_max` - Capacity range
- `sort_by` - Array: 'cd_desc', 'cd_asc', 'location_name_asc', 'location_name_desc', 'max_capacity_asc', 'max_capacity_desc'

---

### 3.2 Inventory Stock Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/warehouse/inventory-stock/` | `WarehouseService.list_inventory_stocks()` | Paginated list |
| Get Single | GET | `/api/company/warehouse/inventory-stock/{id}` | `WarehouseService.get_inventory_stock()` | Get by ID |
| Create | POST | `/api/company/warehouse/inventory-stock/` | `WarehouseService.create_inventory_stock()` | Create stock (blocked if batch mode) |
| Update | PATCH | `/api/company/warehouse/inventory-stock/{id}` | `WarehouseService.update_inventory_stock()` | Update quantity (blocked if batch mode) |
| Delete | DELETE | `/api/company/warehouse/inventory-stock/{id}` | `WarehouseService.delete_inventory_stock()` | Delete (blocked if batch mode) |
| **Special: Transfer** | POST | `/api/company/warehouse/inventory-stock/transfer` | `StockTransferService.create_stock_transfer()` | Transfer stock between locations |
| **Special: Filter** | GET | `?product_id=X&location_id=Y&variant_id=Z` | `WarehouseService.list_inventory_stocks()` | Multi-field filter |

**Important:** Manual stock mutations are blocked when batch tracking is enabled (via `block_stock_mutation_in_batch_mode()` guard).

---

### 3.3 Stock Transfer Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/warehouse/stock-transfer/` | `StockTransferService.get_all_stock_transfers()` | Paginated with meta |
| Get Single | GET | `/api/company/warehouse/stock-transfer/{id}` | `StockTransferService.get_stock_transfer()` | Get with details |
| Create | POST | `/api/company/warehouse/stock-transfer/` | `StockTransferService.create_stock_transfer()` | Create transfer with batch support |
| Update | PATCH | `/api/company/warehouse/stock-transfer/{id}` | `StockTransferService.update_stock_transfer()` | Update transfer |
| Delete | DELETE | `/api/company/warehouse/stock-transfer/{id}` | `StockTransferService.delete_stock_transfer()` | Soft delete |
| **Special: Filter** | GET | `?source_location_id=X&target_location_id=Y` | `StockTransferService.get_all_stock_transfers()` | Filter by locations |
| **Special: Date Filter** | GET | `?transfer_date_start=X&transfer_date_end=Y` | `StockTransferService.get_all_stock_transfers()` | Date range filter |

**Stock Transfer Flow (with batch tracking):**
1. Pre-fetch products, variants, locations (avoid N+1)
2. Validate source location belongs to company
3. Check batch tracking enabled via `BatchAllocationService`
4. If batch enabled: use `InventorySyncService.apply_stock_mutation()`
5. If legacy mode: manual stock decrement/increment with transaction logging
6. Create `InventoryTransaction` records for audit trail

---

### 3.4 DSR Storage Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/warehouse/dsr-storage/` | `DSRStorageService.get_all_dsr_storages()` | Paginated list |
| Get Single | GET | `/api/company/warehouse/dsr-storage/{id}` | `DSRStorageService.get_dsr_storage()` | Get by ID |
| Get By DSR | GET | `/api/company/warehouse/dsr-storage/by-dsr/{dsr_id}` | `DSRStorageService.get_by_dsr()` | Get by DSR ID |
| Create | POST | `/api/company/warehouse/dsr-storage/` | `DSRStorageService.create_dsr_storage()` | Create DSR storage |
| Update | PATCH | `/api/company/warehouse/dsr-storage/{id}` | `DSRStorageService.update_dsr_storage()` | Update |
| Delete | DELETE | `/api/company/warehouse/dsr-storage/{id}` | `DSRStorageService.delete_dsr_storage()` | Soft delete |

---

### 3.5 DSR Stock Transfer Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/warehouse/dsr-stock-transfer/` | `DSRStockTransferService.get_all_transfers()` | Paginated list |
| Get Single | GET | `/api/company/warehouse/dsr-stock-transfer/{id}` | `DSRStockTransferService.get_transfer()` | Get by ID |
| Create | POST | `/api/company/warehouse/dsr-stock-transfer/` | `DSRStockTransferService.create_transfer()` | Create transfer |
| Update | PATCH | `/api/company/warehouse/dsr-stock-transfer/{id}` | `DSRStockTransferService.update_transfer()` | Update |
| Delete | DELETE | `/api/company/warehouse/dsr-stock-transfer/{id}` | `DSRStockTransferService.delete_transfer()` | Soft delete |

**DSR Transfer Validation:**
- Exactly one source (location_id OR dsr_storage_id)
- Exactly one target (location_id OR dsr_storage_id)
- Source and target cannot be the same

---

### 3.6 Batch Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/inventory/batches/` | `BatchRepository.get_batches()` | Paginated with filters |
| Get Single | GET | `/api/company/inventory/batches/{id}/` | `BatchRepository.get_batch()` | Get with movements |
| Create | POST | `/api/company/inventory/batches/` | `BatchService.create_batch()` | Create batch |
| Update | PATCH | `/api/company/inventory/batches/{id}/` | `BatchService.update_batch()` | Update batch |
| Delete | DELETE | `/api/company/inventory/batches/{id}/` | `BatchService.delete_batch()` | Soft delete |
| **Special: Allocate** | POST | `/api/company/inventory/batches/allocate/` | `BatchAllocationService.allocate_sales_order()` | Allocate batches to SO |
| **Special: Return** | POST | `/api/company/inventory/batches/return/` | `BatchAllocationService.process_return()` | Process returns |
| **Special: Stock-to-Batch** | POST | `/api/company/inventory/batches/stock-to-batch/` | `StockToBatchService.preview/execute()` | Migrate legacy stock |
| **Special: Drill-down** | GET | `/api/company/products/{id}/batches` | `BatchRepository.get_product_batches()` | Product batch view |
| **Special: Aging Report** | GET | `/api/company/reports/inventory-aging/` | `BatchService.get_aging_report()` | Age analysis |
| **Special: COGS** | GET | `/api/company/reports/cogs/` | `BatchService.get_cogs_report()` | Cost of goods sold |

---

### 3.7 Inventory Movement Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/api/company/inventory/movements/` | `InventoryMovementRepository.list()` | Paginated movements |
| Get Single | GET | `/api/company/inventory/movements/{id}/` | `InventoryMovementRepository.get()` | Get by ID |
| **Special: Ledger** | GET | `/api/company/inventory/movement-ledger/` | `InventoryMovementRepository.get_ledger()` | Full movement history |
| **Special: By Batch** | GET | `/api/company/inventory/batches/{id}/movements/` | `InventoryMovementRepository.get_by_batch()` | Batch movements |
| **Special: By Product** | GET | `/api/company/inventory/products/{id}/movements/` | `InventoryMovementRepository.get_by_product()` | Product movements |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| Inventory Dashboard | `/warehouse/inventory` | ✅ Active | Main inventory management with stocks, adjustments, transfers |
| Storage Locations | `/warehouses/storage-locations` | ✅ Active | List and manage storage locations |
| Add Storage Location | `/warehouses/storage-locations/new` | ✅ Active | Create new storage location |
| Bulk Stock Transfer | `/warehouse/inventory-stock/transfer` | ✅ Active | Transfer stock between locations |
| New Adjustment | `/warehouse/inventory-stock/adjustment` | ✅ Active | Create inventory adjustment |
| Batch Drill-down | `/inventory/batch-drilldown` | ✅ Active | View batches by product |
| Movement Ledger | `/inventory/movement-ledger` | ✅ Active | Full inventory movement history |
| Batch Reconciliation | `/inventory/reconciliation` | ✅ Active | Reconcile batch vs stock quantities |
| Batch Backfill | `/inventory/backfill` | ✅ Active | Migrate legacy stock to batch |
| SO Allocations | `/inventory/allocations` | ✅ Active | View sales order batch allocations |
| Stock to Batch | `/inventory/stock-to-batch` | ✅ Active | Convert stock records to batches |
| Drift Approvals | `/inventory/drift-approvals` | ✅ Active | Approve quantity corrections |
| DSR Storage (User) | `/dsr/storage` | ✅ Active | DSR view of their storage |
| DSR Inventory | `/dsr/inventory` | ✅ Active | DSR inventory management |
| DSR Storages (Admin) | `/super-admin/dsr-storages` | ✅ Active | Admin DSR storage management |
| Add DSR Storage | `/super-admin/dsr-storages/new` | ✅ Active | Create DSR storage |
| Warehouses | `/warehouses` | ⚠️ Placeholder | Warehouse list (commented out) |
| Add Warehouse | `/warehouses/new` | ⚠️ Placeholder | Create warehouse (commented out) |

---

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| StorageLocationForm | `src/components/forms/StorageLocationForm.tsx` | Create/edit storage locations |
| StockAdjustmentForm | `src/components/forms/StockAdjustmentForm.tsx` | Adjust inventory quantities |
| StockTransferForm | `src/components/forms/StockTransferForm.tsx` | Transfer stock (single item) |
| WarehouseForm | `src/components/forms/WarehouseForm.tsx` | Create/edit warehouses (commented out) |
| DSRStorageForm | `src/components/forms/DSRStorageForm.tsx` | Create/edit DSR storages |

---

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| CustomTable | `src/components/Table.tsx` | Reusable data table with pagination |
| Pagination | `src/components/shared/Pagination.tsx` | Pagination controls |
| SearchInput | `src/components/SearchInput.tsx` | Fuzzy search input |
| LoadingOverlay | `src/components/shared/LoadingOverlay.tsx` | Loading state overlay |
| ActiveInactiveStatus | `src/components/shared/ActiveInactiveStatus.tsx` | Status badge |
| ConfirmDeleteDialog | `src/components/shared/ConfirmDeleteDialog.tsx` | Delete confirmation |
| StockTransferHistory | `src/components/StockTransferHistory.tsx` | Transfer history view |
| AdjustmentHistory | `src/components/AdjustmentHistory.tsx` | Adjustment history view |

---

### 4.4 Context Providers

| Context | File Path | Purpose |
|---------|-----------|---------|
| AuthContext | `src/hooks/useAuth.tsx` | User authentication state |
| SettingsContext | `src/contexts/SettingsContext.tsx` | App settings |
| ProductSelectionContext | `src/contexts/ProductSelectionContext.tsx` | Selected products |
| POSContext | `src/contexts/POSContext.tsx` | POS state |
| BookmarksContext | `src/contexts/BookmarksContext.tsx` | User bookmarks |

---

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `warehousesApi.ts` | `getWarehousesByCompany()`, `getLocationsByWarehouse()`, `getLocationsByCompany()`, `getAllLocations()` |
| `storageLocationsApi.ts` | `getStorageLocations()`, `createStorageLocation()`, `updateStorageLocation()`, `deleteStorageLocation()` |
| `inventoryApi.ts` | `getInventoryStockByVariant()`, `createInventoryStock()`, `transferSingleStock()`, `transferStock()`, `adjustStock()`, `getStockTransfers()` |
| `dsrStorageApi.ts` | `getDSRStorages()`, `getDSRStorage()`, `getDSRStorageByDSR()`, `createDSRStorage()`, `updateDSRStorage()`, `deleteDSRStorage()` |
| `batchApi.ts` | `getBatches()`, `getBatch()`, `createBatch()`, `updateBatch()`, `deleteBatch()`, `allocateBatches()`, `getProductBatches()`, `getBatchStockReport()`, `getInventoryAging()`, `getCOGSReport()` |
| `adjustmentApi.ts` | `getAdjustments()`, `createAdjustment()` |

---

### 4.6 Types & Zod Schemas

| Schema | File | Fields |
|--------|------|--------|
| StorageLocation | `src/lib/schema/index.ts` | `warehouse_id`, `location_name`, `location_code`, `location_type`, `max_capacity`, `is_active`, `company_id` |
| InsertStorageLocation | `src/lib/schema/index.ts` | Same as StorageLocation (Zod schema) |
| DSRStorage | `src/lib/schema/dsrStorage.ts` | `dsr_id`, `storage_name`, `storage_code`, `storage_type`, `max_capacity`, `is_active` |
| StockTransfer | `src/types/stockTransfer.ts` | `transfer_id`, `transfer_date`, `source_location_id`, `source_location_name`, `status`, `notes`, `details`, `transfer_code` |
| StockTransferDetail | `src/types/stockTransfer.ts` | `product_id`, `variant_id`, `target_location_id`, `quantity`, `product_name`, `variant_name`, `target_location_name` |
| InventoryStock | `src/types/inventory.ts` | `current_stock`, `units_sold`, `total_revenue`, `total_profit`, `product_inventory_timeline`, `variant_status` |
| Batch | `src/lib/schema/batch.ts` | `batch_number`, `product_id`, `variant_id`, `location_id`, `initial_quantity`, `remaining_quantity`, `unit_cost`, `received_date`, `expiry_date`, `status` |

---

## 5. Interconnected Workflows

### 5.1 Storage Location Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: User clicks "New Storage" in StorageLocations page                │
│ UI: Button in CardHeader → Link to /warehouses/storage-locations/new       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: AddStorageLocation page renders with StorageLocationForm          │
│ UI: Form with warehouse_id, location_name, location_code, location_type,   │
│     max_capacity, is_active fields                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: User fills form and submits                                       │
│ → Frontend validation via Zod schema (insertStorageLocationSchema)       │
│ → Checks for duplicate name/code in existing locations                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: React Query mutation calls createStorageLocation()                │
│ → POST /api/company/warehouse/storage-locations/                         │
│ → Body: StorageLocationCreate schema                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 5: Backend processes request                                          │
│ → WarehouseService.create_storage_location()                               │
│ → StorageLocationRepository.create()                                       │
│ → DB insert into warehouse.storage_location                                │
│ → Returns StorageLocationRead                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 6: Frontend handles success                                           │
│ → executeFreezeRefresh() invalidates ["/locations"] query                 │
│ → Navigates to /warehouses/storage-locations                               │
│ → Toast success message                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Stock Transfer Flow (Batch-Enabled Company)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: User initiates transfer from Inventory page                        │
│ UI: "Transfer stocks" dropdown action → Opens StockTransferForm modal      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: User selects target location and confirms quantity                │
│ UI: Select dropdown for target location, quantity input                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: Frontend prepares transfer data                                    │
│ → Formats as StockTransferCreate with single detail                        │
│ → Calls transferStock() → POST /api/company/warehouse/inventory-stock/   │
│   /transfer OR POST /api/company/warehouse/stock-transfer/               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: Backend validates and executes                                     │
│ → StockTransferService.create_stock_transfer()                              │
│ → 4.1: Pre-fetch all products, variants, locations (N+1 prevention)       │
│ → 4.2: Validate source location belongs to company                         │
│ → 4.3: Check batch_tracking_enabled via BatchAllocationService          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 5: Batch-enabled path (InventorySyncService)                          │
│ → Apply stock mutation via sync service:                                   │
│   StockChangeContext(company_id, product_id, variant_id,                   │
│                      source_location_id, -qty, TRANSFER,                   │
│                      ref_type="STOCK_TRANSFER", ref_id=transfer_id,       │
│                      to_location_id=target_id)                           │
│ → InventorySyncService.apply_stock_mutation(ctx)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 6: Batch allocation and stock update                                  │
│ → 6.1: Call allocate() to deduct from source batches (FEFO)             │
│ → 6.2: Create inbound movement for target location (new batch)            │
│ → 6.3: Update inventory_stock records for both locations                │
│ → 6.4: Create InventoryTransaction records (OUT and IN)                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 7: Commit and return                                                  │
│ → Commit transaction                                                       │
│ → Return StockTransferRead with details                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 8: Frontend refresh                                                   │
│ → executeFreezeRefresh() invalidates queries                              │
│ → Refreshes inventory table with updated quantities                          │
│ → Closes modal, shows success toast                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.3 DSR Stock Loading Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Admin creates DSR Stock Transfer                                   │
│ UI: Navigate to DSR section → Create transfer                              │
│ → Source: Storage Location (warehouse)                                     │
│ → Target: DSR Storage                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: API validates mutual exclusivity                                   │
│ → Schema validates: source_location_id provided (not source_dsr)          │
│ → Schema validates: target_dsr_storage_id provided (not target_location)  │
│ → Schema validates: source ≠ target                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: Execute DSR Stock Transfer                                         │
│ → POST /api/company/warehouse/dsr-stock-transfer/                          │
│ → DSRStockTransferService.create_transfer()                                │
│ → 3.1: Deduct from source storage location inventory                       │
│ → 3.2: Add to target DSR storage inventory                               │
│ → 3.3: Create InventoryTransaction records                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: DSR now has stock available                                        │
│ → DSR can view stock in /dsr/inventory                                     │
│ → DSR can create sales orders against their storage                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.4 Batch Purchase Order Receipt Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Purchase Order delivered                                            │
│ → Procurement module marks PO as delivered                                 │
│ → Triggers batch creation for each line item                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: Batch creation for each PO detail                                  │
│ → POST /api/company/inventory/batches/ (internal)                          │
│ → BatchService.create_batch()                                              │
│ → Creates batch with:                                                      │
│   - batch_number (auto-generated)                                          │
│   - product_id, variant_id                                                 │
│   - location_id (from PO delivery location)                                │
│   - purchase_order_detail_id (link to source)                            │
│   - initial_quantity = PO delivered qty                                    │
│   - remaining_quantity = same                                              │
│   - unit_cost = PO unit price                                              │
│   - received_date = now                                                    │
│   - status = 'ACTIVE'                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: Inventory movement recorded                                        │
│ → Creates InventoryMovement:                                               │
│   - batch_id = new batch                                                   │
│   - movement_type = 'INBOUND'                                              │
│   - quantity = received qty                                                │
│   - reference_type = 'PURCHASE_ORDER'                                        │
│   - reference_id = PO ID                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: Inventory stock synchronized                                       │
│ → InventorySyncService updates inventory_stock.remaining_quantity          │
│ → Or creates new stock record if doesn't exist                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.5 Sales Order Batch Allocation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Sales order requires stock reservation                             │
│ → Sales order line item needs quantity                                     │
│ → System checks if batch tracking enabled for company                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: Batch allocation initiated                                         │
│ → POST /api/company/inventory/batches/allocate/                            │
│ → BatchAllocationService.allocate_sales_order()                            │
│ → Request: {sales_order_id, items: [{product_id, variant_id, quantity}]} │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: FEFO allocation algorithm                                          │
│ → For each item:                                                           │
│   3.1: Find ACTIVE batches for product/variant/location                   │
│   3.2: Sort by expiry_date ASC (FEFO - First Expired First Out)            │
│   3.3: Allocate from earliest expiring batches first                       │
│   3.4: Stop when full quantity allocated or stock exhausted                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: Allocation records created                                         │
│ → Creates SalesOrderBatchAllocation records:                             │
│   - sales_order_detail_id                                                  │
│   - batch_id                                                               │
│   - allocated_quantity                                                     │
│   - status = 'RESERVED'                                                    │
│ → Batch.remaining_quantity reduced                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 5: On delivery confirmation                                           │
│ → Allocation status changes to 'CONSUMED'                                  │
│ → Creates InventoryMovement (OUTBOUND)                                     │
│ → If partial delivery, remaining quantity released back to batch          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Batch Tracking Integration

**Overview:**
Batch tracking provides FEFO (First Expired First Out) inventory allocation for companies that need to track products by batch/lot numbers, expiry dates, and unit costs at the batch level.

**Company-Level Setting:**
```python
# CompanyInventorySetting model
class CompanyInventorySetting(Base):
    company_id = Column(Integer, FK, unique=True)
    batch_tracking_enabled = Column(Boolean, default=False)
    default_allocation_method = Column(String, default='FEFO')  # FEFO, FIFO, LIFO
    allow_negative_stock = Column(Boolean, default=False)
    drift_threshold_percent = Column(Numeric, default=5.0)  # % threshold for drift alerts
```

**Key Services:**

1. **BatchAllocationService** (`services/inventory/batch_allocation_service.py`)
   - `allocate_sales_order()` - Allocates batches to sales orders using FEFO
   - `process_return()` - Handles returns and updates batch quantities
   - `get_available_batches()` - Returns batches available for allocation
   - `recalculate_batch_quantities()` - Recalculates from movements

2. **InventorySyncService** (`services/inventory/inventory_sync_service.py`)
   - Centralized service for all stock mutations
   - Ensures batch and inventory_stock remain synchronized
   - `apply_stock_mutation()` - Single entry point for all stock changes

**FEFO Allocation Algorithm:**
```python
def allocate_fefo(product_id, variant_id, location_id, required_qty):
    batches = get_active_batches_ordered_by_expiry(
        product_id, variant_id, location_id
    )
    
    allocations = []
    remaining = required_qty
    
    for batch in batches:
        if remaining <= 0:
            break
            
        available = batch.remaining_quantity
        allocate_qty = min(available, remaining)
        
        allocations.append({
            'batch_id': batch.batch_id,
            'allocated_quantity': allocate_qty
        })
        
        batch.remaining_quantity -= allocate_qty
        remaining -= allocate_qty
    
    if remaining > 0:
        raise InsufficientStockError(f"Short by {remaining}")
    
    return allocations
```

**Stock Change Context:**
```python
class StockChangeContext:
    company_id: int
    product_id: int
    variant_id: Optional[int]
    location_id: int
    qty_delta: Decimal  # Negative for outbound, positive for inbound
    source: StockSource  # PURCHASE, SALE, TRANSFER, ADJUSTMENT
    ref_type: str
    ref_id: int
    user_id: int
    to_location_id: Optional[int]  # For transfers
```

---

### 6.2 InventorySyncService Architecture

**Purpose:** Centralized coordination of all inventory mutations to maintain consistency between batch and stock-level quantities.

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `apply_stock_mutation(ctx)` | Main entry point - applies any stock change |
| `get_sync_service()` | Factory with batch mode detection |
| `is_batch_tracking_enabled(company_id)` | Check company setting |

**Mutation Flow:**

```
apply_stock_mutation(ctx)
    │
    ├── If batch tracking enabled:
    │   ├── For OUTBOUND (qty_delta < 0):
    │   │   ├── allocate() from batches (FEFO)
    │   │   ├── create OUTBOUND movements
    │   │   └── decrement inventory_stock
    │   │
    │   └── For INBOUND (qty_delta > 0):
    │       ├── create new batch (if from PO) or find existing
    │       ├── create INBOUND movement
    │       └── increment inventory_stock
    │
    └── If batch tracking disabled (legacy):
        └── Direct inventory_stock update only
```

**Guard Functions:**

```python
# batch_guard.py - Prevents manual mutations in batch mode
def block_stock_mutation_in_batch_mode(db, company_id, operation_name):
    """Raises HTTPException if trying to manually mutate stock when batch tracking enabled."""
    sync_service = get_sync_service(db)
    if sync_service and sync_service.is_batch_tracking_enabled(company_id):
        raise HTTPException(
            status_code=400,
            detail=f"{operation_name} is not allowed when batch tracking is enabled. "
                   "Use batch operations instead."
        )
```

---

### 6.3 DSR Storage Management

**Overview:**
DSR (Delivery Sales Representative) storages are dedicated inventory locations tied to specific DSRs. Each DSR has exactly one storage (1:1 relationship enforced at DB level).

**Storage Types:**
- `vehicle` - Mobile storage in delivery vehicle
- `shop` - Fixed shop location
- `warehouse` - Dedicated warehouse space
- `other` - Other storage types

**Transfer Patterns:**

1. **Loading DSR (Warehouse → DSR):**
   ```
   source_location_id = warehouse_location_id
   source_dsr_storage_id = null
   target_location_id = null
   target_dsr_storage_id = dsr_storage_id
   ```

2. **Unloading Returns (DSR → Warehouse):**
   ```
   source_location_id = null
   source_dsr_storage_id = dsr_storage_id
   target_location_id = warehouse_location_id
   target_dsr_storage_id = null
   ```

3. **DSR-to-DSR Transfer:**
   ```
   source_location_id = null
   source_dsr_storage_id = source_dsr_id
   target_location_id = null
   target_dsr_storage_id = target_dsr_id
   ```

---

### 6.4 Multi-Tenant Data Isolation

**Implementation:**
All warehouse entities include `company_id` field with foreign key to `settings.app_client_company`.

**Automatic Filtering:**
```python
# Dependency injection
def get_current_company_id(request: Request) -> int:
    return request.state.user["company_id"]

# API endpoint
@router.get("/")
def list_items(
    company_id: int = Depends(get_current_company_id)  # Auto-injected
):
    return service.list(company_id=company_id)  # Always filtered
```

**Repository Pattern:**
```python
class StorageLocationRepository:
    def list(self, company_id: int, **filters):
        query = self.db.query(StorageLocation).filter(
            StorageLocation.company_id == company_id,
            StorageLocation.is_deleted == False
        )
        # Apply additional filters...
        return query.all()
```

---

### 6.5 Soft Delete Behavior

**All entities** use `IsDeletedMixin` providing:
- `is_deleted` boolean column (default: False)
- `cd`, `md`, `cb`, `mb` audit columns

**Delete Operation:**
```python
def delete(self, entity):
    entity.is_deleted = True  # Soft delete
    entity.md = datetime.now()  # Update modification
    self.db.add(entity)
```

**Query Filtering:**
```python
# All queries automatically filter deleted records
query.filter(StorageLocation.is_deleted == False)
```

**Cascade Considerations:**
- StorageLocation cannot be deleted if InventoryStock records exist
- InventoryStock cannot be deleted if Batch records exist (when batch tracking enabled)
- All deletes cascade to related transaction records

---

### 6.6 UOM Conversion Handling

**Unit of Measure Hierarchy:**
```
Base Unit (is_base=True, base_id=null)
    │
    ├── Derived Unit 1 (is_base=False, base_id=base_unit_id, conversion_factor=12)
    └── Derived Unit 2 (is_base=False, base_id=base_unit_id, conversion_factor=0.5)
```

**Conversion Functions:**
```python
# uom_utils.py
def get_base_uom_id(db, uom_id) -> int:
    """Returns the base UOM ID for any unit (itself if base)."""
    uom = db.query(UnitOfMeasure).get(uom_id)
    return uom.base_id if uom.base_id else uom.unit_id

def convert_to_base(db, quantity, from_uom_id) -> Decimal:
    """Converts quantity from any UOM to base UOM."""
    uom = db.query(UnitOfMeasure).get(from_uom_id)
    if uom.is_base:
        return quantity
    return quantity * uom.conversion_factor
```

**Usage in Stock Operations:**
All stock quantities are stored in base UOM for consistency:
```python
# Stock transfer service
base_quantity = convert_to_base(db, detail.quantity, detail.uom_id)
source_stock.quantity -= base_quantity
target_stock.quantity += base_quantity
```

---

### 6.7 Optimistic Locking

**Implementation:**
InventoryStock model includes version column for optimistic locking:
```python
class InventoryStock(Base):
    version = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version}
```

**Behavior:**
- SQLAlchemy automatically increments version on UPDATE
- Concurrent modifications raise `StaleDataError`
- Application should catch and retry or notify user

---

### 6.8 Transaction Logging

**InventoryTransaction Records:**
All stock mutations create audit records:

```python
class InventoryTransaction(Base):
    transaction_type = Column(String)  # STOCK_TRANSFER_OUT, STOCK_TRANSFER_IN, ADJUSTMENT, SALE, PURCHASE
    transaction_date = Column(TIMESTAMP)
    product_id = Column(Integer, FK)
    variant_id = Column(Integer, FK)
    location_id = Column(Integer, FK)
    quantity = Column(Numeric)  # Positive or negative
    reference_type = Column(String)  # StockTransfer, SalesOrder, PurchaseOrder
    reference_id = Column(Integer)
    notes = Column(Text)
```

**Generated For:**
- Stock transfers (both OUT and IN records)
- Manual adjustments
- Sales order fulfillment
- Purchase order receipts
- DSR stock transfers

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **Storage Location** | `GET /warehouse/storage-locations/` | `GET /{id}` | `POST /` | `PATCH /{id}` | `DELETE /{id}` | Filter, Sort |
| **Inventory Stock** | `GET /warehouse/inventory-stock/` | `GET /{id}` | `POST /` | `PATCH /{id}` | `DELETE /{id}` | Transfer |
| **Stock Transfer** | `GET /warehouse/stock-transfer/` | `GET /{id}` | `POST /` | `PATCH /{id}` | `DELETE /{id}` | Multi-filter |
| **DSR Storage** | `GET /warehouse/dsr-storage/` | `GET /{id}` | `POST /` | `PATCH /{id}` | `DELETE /{id}` | Get by DSR |
| **DSR Transfer** | `GET /warehouse/dsr-stock-transfer/` | `GET /{id}` | `POST /` | `PATCH /{id}` | `DELETE /{id}` | - |
| **Batch** | `GET /inventory/batches/` | `GET /{id}/` | `POST /` | `PATCH /{id}/` | `DELETE /{id}/` | Allocate, Return |
| **Movement** | `GET /inventory/movements/` | `GET /{id}/` | - | - | - | Ledger, By batch |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|--------------------|------------------|
| List Storage Locations | `getStorageLocations()` | `GET /warehouse/storage-locations/` |
| Create Storage Location | `createStorageLocation(data)` | `POST /warehouse/storage-locations/` |
| Update Storage Location | `updateStorageLocation(id, data)` | `PATCH /warehouse/storage-locations/{id}` |
| Delete Storage Location | `deleteStorageLocation(id)` | `DELETE /warehouse/storage-locations/{id}` |
| Get Inventory Stock | `fetchInventory(locationId)` | `GET /warehouse/inventory-stock/?location_id=X` |
| Transfer Stock | `transferStock(data)` | `POST /warehouse/stock-transfer/` |
| Single Stock Transfer | `transferSingleStock(data)` | `POST /warehouse/inventory-stock/transfer` |
| Adjust Stock | `adjustStock(data)` | `POST /transaction/inventory-adjustment/` |
| Get Stock Transfers | `getStockTransfers(locationId)` | `GET /warehouse/stock-transfer/?location_id=X` |
| List DSR Storages | `getDSRStorages()` | `GET /warehouse/dsr-storage/` |
| Get DSR Storage by DSR | `getDSRStorageByDSR(dsrId)` | `GET /warehouse/dsr-storage/by-dsr/{dsrId}` |
| Create DSR Storage | `createDSRStorage(data)` | `POST /warehouse/dsr-storage/` |
| Update DSR Storage | `updateDSRStorage(id, data)` | `PATCH /warehouse/dsr-storage/{id}` |
| Delete DSR Storage | `deleteDSRStorage(id)` | `DELETE /warehouse/dsr-storage/{id}` |
| List Batches | `getBatches(params)` | `GET /inventory/batches/` |
| Get Batch | `getBatch(id)` | `GET /inventory/batches/{id}/` |
| Allocate Batches | `allocateBatches(data)` | `POST /inventory/batches/allocate/` |
| Get Product Batches | `getProductBatches(productId)` | `GET /products/{productId}/batches` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/warehouse.py` | Warehouse, StorageLocation, InventoryStock, StockTransfer, DSR entities |
| **Models** | `Shoudagor/app/models/inventory.py` | Product, ProductVariant, ProductCategory, UnitOfMeasure, ProductGroup, VariantGroup, ProductVariantImage |
| **Models** | `Shoudagor/app/models/batch_models.py` | Batch, InventoryMovement, SalesOrderBatchAllocation, CompanyInventorySetting |
| **Models** | `Shoudagor/app/models/transaction.py` | InventoryTransaction, InventoryAdjustment |
| **Schemas** | `Shoudagor/app/schemas/warehouse/storage_location.py` | StorageLocationCreate, Read, Update |
| **Schemas** | `Shoudagor/app/schemas/warehouse/inventory_stock.py` | InventoryStock schemas |
| **Schemas** | `Shoudagor/app/schemas/warehouse/stock_transfer.py` | StockTransfer schemas with nested details |
| **Schemas** | `Shoudagor/app/schemas/warehouse/dsr_storage.py` | DSRStorage schemas |
| **Schemas** | `Shoudagor/app/schemas/warehouse/dsr_stock_transfer.py` | DSRStockTransfer schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/batch.py` | Batch, Movement, Allocation schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/stock_change.py` | StockChange, StockMutationResult |
| **Repositories** | `Shoudagor/app/repositories/warehouse/storage_location.py` | StorageLocationRepository |
| **Repositories** | `Shoudagor/app/repositories/warehouse/inventory_stock.py` | InventoryStockRepository |
| **Repositories** | `Shoudagor/app/repositories/warehouse/stock_transfer.py` | StockTransferRepository |
| **Repositories** | `Shoudagor/app/repositories/warehouse/dsr_storage.py` | DSRStorageRepository |
| **Repositories** | `Shoudagor/app/repositories/inventory/batch.py` | BatchRepository, InventoryMovementRepository |
| **Services** | `Shoudagor/app/services/warehouse/warehouse.py` | WarehouseService (storage locations, inventory stock) |
| **Services** | `Shoudagor/app/services/warehouse/stock_transfer.py` | StockTransferService |
| **Services** | `Shoudagor/app/services/warehouse/dsr_storage.py` | DSRStorageService |
| **Services** | `Shoudagor/app/services/warehouse/dsr_stock_transfer.py` | DSRStockTransferService |
| **Services** | `Shoudagor/app/services/inventory/batch_allocation_service.py` | BatchAllocationService |
| **Services** | `Shoudagor/app/services/inventory/inventory_sync_service.py` | InventorySyncService |
| **Services** | `Shoudagor/app/services/inventory/batch_guard.py` | block_stock_mutation_in_batch_mode |
| **Services** | `Shoudagor/app/services/uom_utils.py` | UOM conversion utilities |
| **API** | `Shoudagor/app/api/warehouse/warehouse.py` | Storage location and inventory stock endpoints |
| **API** | `Shoudagor/app/api/warehouse/stock_transfer.py` | Stock transfer endpoints |
| **API** | `Shoudagor/app/api/warehouse/dsr_storage.py` | DSR storage endpoints |
| **API** | `Shoudagor/app/api/warehouse/dsr_stock_transfer.py` | DSR stock transfer endpoints |
| **API** | `Shoudagor/app/api/warehouse/dsr_inventory_stock.py` | DSR inventory stock endpoints |
| **API** | `Shoudagor/app/api/inventory/batch.py` | Batch management endpoints |
| **API** | `Shoudagor/app/api/inventory/inventory_movement.py` | Movement ledger endpoints |
| **API** | `Shoudagor/app/api/transaction/inventory_adjustment.py` | Adjustment endpoints |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages** | `shoudagor_FE/src/pages/warehouse/Inventory.tsx` | Main inventory dashboard |
| **Pages** | `shoudagor_FE/src/pages/warehouse/Warehouses.tsx` | Warehouse list (placeholder) |
| **Pages** | `shoudagor_FE/src/pages/warehouse/storage/StorageLocations.tsx` | Storage locations list |
| **Pages** | `shoudagor_FE/src/pages/warehouse/storage/new/AddStorageLocation.tsx` | Add storage location |
| **Pages** | `shoudagor_FE/src/pages/warehouse/adjustment/NewInventoryAdjustment.tsx` | Create adjustment |
| **Pages** | `shoudagor_FE/src/pages/InventoryStockTransfer.tsx` | Bulk stock transfer |
| **Pages** | `shoudagor_FE/src/pages/dsr/DSRStorages.tsx` | User DSR storages |
| **Pages** | `shoudagor_FE/src/pages/dsr/DSRInventoryStock.tsx` | DSR inventory |
| **Pages** | `shoudagor_FE/src/pages/super-admin/dsr-storage/DSRStorages.tsx` | Admin DSR storages |
| **Pages** | `shoudagor_FE/src/pages/super-admin/dsr-storage/new/AddDSRStorage.tsx` | Add DSR storage |
| **Pages** | `shoudagor_FE/src/pages/inventory/BatchDrillDown.tsx` | Batch drill-down |
| **Pages** | `shoudagor_FE/src/pages/inventory/MovementLedger.tsx` | Movement ledger |
| **Pages** | `shoudagor_FE/src/pages/inventory/BatchReconciliation.tsx` | Reconciliation |
| **Pages** | `shoudagor_FE/src/pages/inventory/BatchBackfill.tsx` | Batch backfill |
| **Pages** | `shoudagor_FE/src/pages/inventory/SalesOrderBatchAllocations.tsx` | SO allocations |
| **Pages** | `shoudagor_FE/src/pages/inventory/StockToBatch.tsx` | Stock-to-batch |
| **Pages** | `shoudagor_FE/src/pages/inventory/DriftApprovals.tsx` | Drift approvals |
| **Components** | `shoudagor_FE/src/components/forms/StorageLocationForm.tsx` | Storage location form |
| **Components** | `shoudagor_FE/src/components/forms/StockAdjustmentForm.tsx` | Adjustment form |
| **Components** | `shoudagor_FE/src/components/forms/StockTransferForm.tsx` | Stock transfer form |
| **Components** | `shoudagor_FE/src/components/forms/WarehouseForm.tsx` | Warehouse form |
| **Components** | `shoudagor_FE/src/components/StockTransferHistory.tsx` | Transfer history |
| **Components** | `shoudagor_FE/src/components/AdjustmentHistory.tsx` | Adjustment history |
| **API** | `shoudagor_FE/src/lib/api/warehousesApi.ts` | Warehouse API functions |
| **API** | `shoudagor_FE/src/lib/api/storageLocationsApi.ts` | Storage location API |
| **API** | `shoudagor_FE/src/lib/api/inventoryApi.ts` | Inventory API |
| **API** | `shoudagor_FE/src/lib/api/dsrStorageApi.ts` | DSR storage API |
| **API** | `shoudagor_FE/src/lib/api/batchApi.ts` | Batch API |
| **API** | `shoudagor_FE/src/lib/api/adjustmentApi.ts` | Adjustment API |
| **Schemas** | `shoudagor_FE/src/lib/schema/index.ts` | Main schema definitions |
| **Schemas** | `shoudagor_FE/src/lib/schema/dsrStorage.ts` | DSR storage schema |
| **Schemas** | `shoudagor_FE/src/lib/schema/batch.ts` | Batch schema |
| **Types** | `shoudagor_FE/src/types/stockTransfer.ts` | Stock transfer types |
| **Types** | `shoudagor_FE/src/types/inventory.ts` | Inventory types |
| **Routes** | `shoudagor_FE/src/App.tsx` | Route definitions (lines 197-210) |

---

## 9. Appendix: Operation Counts

### 9.1 Backend Operations Summary

| Entity | CRUD Ops | Special Ops | Total |
|--------|----------|-------------|-------|
| Storage Location | 5 | 2 (filter, sort) | 7 |
| Inventory Stock | 5 | 2 (filter, batch-guard) | 7 |
| Stock Transfer | 5 | 3 (multi-filter, batch-allocation) | 8 |
| DSR Storage | 5 | 1 (get by DSR) | 6 |
| DSR Stock Transfer | 5 | 1 (mutual exclusion validation) | 6 |
| DSR Inventory Stock | 5 | 1 (filter) | 6 |
| Batch | 5 | 9 (allocate, return, drill-down, aging, COGS, PnL, stock-to-batch, drift, reconcile) | 14 |
| Inventory Movement | 2 | 3 (ledger, by batch, by product) | 5 |
| **TOTAL** | **37** | **22** | **59** |

### 9.2 Frontend Operations Summary

| Entity | API Functions | Components | Total |
|--------|--------------|------------|-------|
| Storage Location | 4 | 2 (StorageLocations, AddStorageLocation, StorageLocationForm) | 7 |
| Inventory Stock | 5 | 2 (Inventory, StockAdjustmentForm) | 7 |
| Stock Transfer | 3 | 2 (InventoryStockTransfer, StockTransferForm, StockTransferHistory) | 6 |
| DSR Storage | 6 | 3 (DSRStorages, AddDSRStorage, DSRStorageForm, UserDSRStorages) | 10 |
| Batch | 15+ | 6 (BatchDrillDown, MovementLedger, BatchReconciliation, BatchBackfill, SalesOrderBatchAllocations, StockToBatch, DriftApprovals) | 21+ |
| **TOTAL** | **33+** | **15+** | **51+** |

---

## Document Summary

This comprehensive reference guide covers the complete Warehouse module for the Shoudagor ERP system:

- **11 Core Entities** with full field specifications and relationships
- **59 Backend Operations** across CRUD and special operations
- **51+ Frontend Components** and API functions
- **5 Detailed Workflows** showing end-to-end processes
- **8 Special Features** including batch tracking, DSR management, and multi-tenancy
- **Complete File Map** for both backend and frontend codebases

**Key Integration Points:**
- Procurement (Purchase Orders → Batches)
- Sales (Sales Orders → Batch Allocations)
- DSR Program (DSR Storage → Stock Loading/Unloading)
- Product Catalog (Products, Variants → Stock tracking)

---

*End of Warehouse Module Reference Guide*
