# Product Module — Complete Operations & UI Walkthrough

> **Generated:** 2026-04-03  
> **Scope:** Full-stack analysis of the Product Module in Shoudagor ERP  
> **Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

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

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                │
│  Pages → Forms/Modals → Shared Components → API Layer → Types  │
├─────────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI + Python)                   │
│  API Routes → Services → Repositories → Models → Schemas       │
├─────────────────────────────────────────────────────────────────┤
│                    Database (PostgreSQL)                        │
│  inventory schema: product, product_variant, product_category,  │
│  product_price, product_group, product_group_items,             │
│  variant_group, variant_group_items, product_variant_image,     │
│  unit_of_measure                                               │
├─────────────────────────────────────────────────────────────────┤
│                    Search Engine (Elasticsearch)                │
│  products index: nested variants, prices, stocks, groups        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
ProductCategory (hierarchical, self-referential)
    │
    └── Product (1:N)
            │
            ├── ProductVariant (1:N)
            │       │
            │       ├── ProductPrice (1:N, time-effective)
            │       ├── InventoryStock (1:N, per location)
            │       ├── ProductVariantImage (1:N, S3-backed)
            │       ├── VariantGroupItems (N:M via variant_group)
            │       └── SR_Product_Assignment (N:M)
            │
            ├── ProductGroupItems (N:M via product_group)
            └── ProductPrice (1:N, product-level pricing)

ProductGroup (1:N) ──→ ProductGroupItems (N:M) ──→ Product + Variant

VariantGroup (1:N) ──→ VariantGroupItems (N:M) ──→ ProductVariant

UnitOfMeasure (self-referential, base + derived units)
    │
    └── ProductVariant.unit_id (FK)
```

### 1.3 Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend Framework** | FastAPI (Python) |
| **ORM** | SQLAlchemy 2.0+ |
| **Validation** | Pydantic |
| **Database** | PostgreSQL (multi-schema: `inventory`) |
| **Search** | Elasticsearch 8.x (nested mappings) |
| **Image Storage** | S3 (presigned URLs) |
| **Frontend Framework** | React 19 + TypeScript 5.8 |
| **State Management** | TanStack Query v5 + React Context |
| **Forms** | React Hook Form + Zod |
| **UI Components** | shadcn/ui (Radix-based) |
| **Drag & Drop** | @dnd-kit |
| **Charts** | Recharts |

---

## 2. Entity Inventory

### 2.1 Product

**Table:** `inventory.product`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `product_id` | Integer | PK | Primary key |
| `product_name` | String(200) | NOT NULL | Display name |
| `product_code` | String(50) | NOT NULL, Indexed | Unique code per company |
| `category_id` | Integer | FK → product_category | Category reference |
| `description` | String(500) | Nullable | Product description |
| `reorder_level` | Integer | Nullable | Minimum stock alert threshold |
| `safety_stock` | Integer | Nullable | Buffer stock level |
| `is_active` | Boolean | Default: True | Active/inactive status |
| `is_deleted` | Boolean | Default: False | Soft delete flag |
| `company_id` | Integer | FK → app_client_company | Multi-tenant isolation |
| `cb`, `cd`, `mb`, `md` | Timestamp/Integer | Mixin | Audit trail (created/modified by/date) |

**Relationships:**
- `category` → ProductCategory
- `variants` → List[ProductVariant]
- `prices` → List[ProductPrice]
- `product_groups` → List[ProductGroupItems]
- `batches` → List[Batch]
- `inventory_stocks` → List[InventoryStock]

### 2.2 ProductVariant

**Table:** `inventory.product_variant`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `variant_id` | Integer | PK | Primary key |
| `product_id` | Integer | FK → product | Parent product |
| `sku` | String(50) | NOT NULL, Indexed | Stock keeping unit (unique per company) |
| `attribute_name` | String(50) | NOT NULL | e.g., "Size", "Color" |
| `attribute_value` | String(50) | NOT NULL | e.g., "Medium", "Red" |
| `unit_id` | Integer | FK → unit_of_measure | Unit of measure |
| `reorder_level` | Integer | Nullable | Variant-specific reorder threshold |
| `safety_stock` | Integer | Nullable | Variant-specific buffer |
| `carton_factor` | Integer | Default: 1 | Items per carton |
| `is_active` | Boolean | Default: True | Active/inactive |
| `is_deleted` | Boolean | Default: False | Soft delete |

**Relationships:**
- `product` → Product
- `unit` → UnitOfMeasure
- `prices` → List[ProductPrice]
- `inventory_stocks` → List[InventoryStock]
- `images` → List[ProductVariantImage] (cascade delete)
- `variant_groups` → List[VariantGroupItems]
- `product_groups` → List[ProductGroupItems]

### 2.3 ProductPrice

**Table:** `inventory.product_price`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `price_id` | Integer | PK | Primary key |
| `product_id` | Integer | FK → product | Product reference |
| `variant_id` | Integer | FK → product_variant (nullable) | Variant reference |
| `effective_date` | TIMESTAMP | NOT NULL | When price becomes active |
| `purchase_price` | Numeric(18,4) | NOT NULL | Cost price |
| `retail_price` | Numeric(18,4) | Default: 0 | Standard retail (MRP) |
| `selling_price` | Numeric(18,4) | Default: 0 | Standard selling price |
| `damage_price` | Numeric(18,4) | Nullable | Damaged goods price |
| `dealer_price` | Numeric(18,4) | Nullable | Dealer-specific price |
| `trade_price` | Numeric(18,4) | Nullable | Trade-specific price |
| `maximum_retail_price` | Numeric(18,4) | Nullable | MRP ceiling |
| `minimum_retail_price` | Numeric(18,4) | Nullable | MRP floor |
| `maximum_selling_price` | Numeric(18,4) | Nullable | Selling ceiling |
| `minimum_selling_price` | Numeric(18,4) | Nullable | Selling floor |
| `currency_id` | Integer | FK → currency | Currency reference |
| `is_active` | Boolean | Default: True | Active/inactive |

**Unique Constraint:** `(product_id, variant_id, effective_date)`

### 2.4 ProductCategory

**Table:** `inventory.product_category`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `category_id` | Integer | PK | Primary key |
| `category_name` | String(100) | NOT NULL | Category name |
| `parent_category_id` | Integer | FK → self (nullable) | Hierarchical parent |
| `description` | String(500) | Nullable | Description |
| `company_id` | Integer | FK → app_client_company | Multi-tenant |
| `is_deleted` | Boolean | Default: False | Soft delete |

**Self-Referential:** `parent_category` → ProductCategory (backref: `children_categories`)

### 2.5 ProductGroup

**Table:** `inventory.product_group`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `product_group_id` | Integer | PK | Primary key |
| `group_name` | String(200) | NOT NULL | Group name |
| `description` | String(500) | Nullable | Description |
| `is_active` | Boolean | Default: True | Active/inactive |
| `company_id` | Integer | FK → app_client_company | Multi-tenant |
| `is_deleted` | Boolean | Default: False | Soft delete |

### 2.6 ProductGroupItems

**Table:** `inventory.product_group_items`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `product_group_items_id` | Integer | PK | Primary key |
| `product_group_id` | Integer | FK → product_group | Group reference |
| `product_id` | Integer | FK → product | Product reference |
| `variant_id` | Integer | FK → product_variant (nullable) | NULL = all variants |

**Unique Constraint:** `(product_group_id, product_id, variant_id)`

### 2.7 VariantGroup

**Table:** `inventory.variant_group`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `variant_group_id` | Integer | PK | Primary key |
| `group_name` | String(200) | NOT NULL | Group name |
| `description` | String(500) | Nullable | Description |
| `is_active` | Boolean | Default: True | Active/inactive |
| `company_id` | Integer | FK → app_client_company | Multi-tenant |
| `is_deleted` | Boolean | Default: False | Soft delete |

### 2.8 VariantGroupItems

**Table:** `inventory.variant_group_items`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `variant_group_items_id` | Integer | PK | Primary key |
| `variant_group_id` | Integer | FK → variant_group | Group reference |
| `variant_id` | Integer | FK → product_variant | Variant reference |

**Unique Constraint:** `(variant_group_id, variant_id)`

### 2.9 ProductVariantImage

**Table:** `inventory.product_variant_image`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `image_id` | Integer | PK | Primary key |
| `variant_id` | Integer | FK → product_variant | Variant reference |
| `s3_key` | String(500) | NOT NULL, Unique | S3 object key |
| `file_name` | String(255) | NOT NULL | Original filename |
| `file_size` | Integer | NOT NULL | Size in bytes |
| `mime_type` | String(100) | NOT NULL | MIME type (PNG/JPG/WEBP/GIF) |
| `is_primary` | Boolean | Default: False, Indexed | Primary image flag |
| `alt_text` | String(255) | Nullable | Accessibility text |
| `display_order` | Integer | Default: 0 | Gallery order |
| `width` | Integer | Nullable | Image width (px) |
| `height` | Integer | Nullable | Image height (px) |
| `uploaded_by` | Integer | FK → app_user | Uploader |
| `upload_status` | String(20) | Default: "completed" | pending/completed/failed |
| `upload_attempts` | Integer | Default: 0 | Retry count |
| `upload_source` | String(20) | Default: "backend" | backend/frontend |
| `presigned_url_expires_at` | TIMESTAMP | Nullable | Presigned URL expiry |
| `is_active` | Boolean | Default: True | Active/inactive |
| `company_id` | Integer | FK → app_client_company | Multi-tenant |
| `is_deleted` | Boolean | Default: False | Soft delete |

### 2.10 UnitOfMeasure

**Table:** `inventory.unit_of_measure`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `unit_id` | Integer | PK | Primary key |
| `unit_name` | String(50) | NOT NULL | e.g., "Piece", "Kilogram" |
| `unit_symbol` | String(50) | NOT NULL | e.g., "pcs", "kg" |
| `conversion_factor` | Numeric(18,4) | Nullable | Factor to convert to base unit |
| `base_id` | Integer | FK → self (nullable) | Reference to base unit |
| `is_base` | Boolean | Default: False | Is this a base unit? |
| `company_id` | Integer | FK → app_client_company | Multi-tenant |
| `is_deleted` | Boolean | Default: False | Soft delete |

---

## 3. Backend Operations Reference

### 3.1 Product Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/product/` | `list_products()` | All products with variants, prices, stocks, groups |
| List (Advanced) | GET | `/inventory/product/` + params | `list_products_advanced()` | 35+ filters: category, group, SKU, price ranges, dates, sorting, pagination |
| Get Single | GET | `/inventory/product/{id}` | `get_product_with_nested_data()` | Product with all nested variants, prices, stocks, groups |
| Create | POST | `/inventory/product/` | `create_product()` | Basic creation (creates synthetic batches if enabled) |
| Create (Nested) | POST | `/inventory/product/nested` | `create_product_nested()` | Full nested: product + variants + prices + stocks + groups in one transaction |
| Update | PATCH | `/inventory/product/{id}/` | `update_product()` | Partial update, validates product_code uniqueness |
| Delete | DELETE | `/inventory/product/{id}/` | `delete_product()` | **Cascade soft delete**: product → variants → prices → group items |
| Batch Delete | POST | `/inventory/product/batch-delete` | `batch_delete_products()` | Validate then batch delete multiple products |
| Search | GET | `/inventory/product/search` | ES `search_products()` | Full-text fuzzy search across name, code, SKU, variants |

### 3.2 Product Variant Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/product-variant/` | `list_variants()` | Variants with filtering (product_id, unit_id, SKU, attribute, dates) |
| List (Nested) | GET | `/inventory/product-variant/nested` | `list_variants_nested()` | Enhanced: stock availability, price ranges, variant groups, batch stock summary |
| Get By IDs | POST | `/inventory/product-variant/by-ids` | `get_variants_by_ids()` | Get multiple variants by ID list |
| Get Single | GET | `/inventory/product-variant/{id}` | `get_variant_nested()` | Single variant with nested price and stocks |
| Create | POST | `/inventory/product-variant/` | `create_variant()` | Basic variant creation |
| Create (Nested) | POST | `/inventory/product-variant/nested` | `create_variant_nested()` | Full nested: variant + price + stocks + variant groups. Blocks if batch mode |
| Update | PATCH | `/inventory/product-variant/{id}/` | `update_variant()` | Partial update, validates SKU uniqueness |
| Update (Nested) | PATCH | `/inventory/product-variant/{id}/nested` | `update_variant_nested()` | Full nested update. Syncs stock delta via InventorySyncService in batch mode |
| Delete | DELETE | `/inventory/product-variant/{id}` | `delete_variant()` | Soft delete variant |
| Batch Delete | POST | `/inventory/product-variant/batch-delete` | `batch_delete_variants()` | Pre-validate then batch delete |

### 3.3 Product Category Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/product-category/` | `list_categories()` | Categories with parent name, company name, filtering, pagination |
| Get Single | GET | `/inventory/product-category/{id}` | `get_category()` | Category with parent and company info |
| Create | POST | `/inventory/product-category/` | `create_category()` | Create with optional parent |
| Update | PATCH | `/inventory/product-category/{id}` | `update_category()` | Partial update |
| Delete | DELETE | `/inventory/product-category/{id}` | `delete_category()` | Soft delete |

### 3.4 Product Price Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/product-price/` | `list_prices()` | Prices with product_name, SKU, currency_name |
| Get Single | GET | `/inventory/product-price/{id}/` | `get_price()` | Single price with product, variant, currency |
| Create | POST | `/inventory/product-price/` | `create_price()` | New price record |
| Update | PATCH | `/inventory/product-price/{id}/` | `update_price()` | Partial update |
| Delete | DELETE | `/inventory/product-price/{id}/` | `delete_price()` | Soft delete |

### 3.5 Product Group Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/product-group/` | `list_groups()` | Groups with filtering, pagination |
| Get Single | GET | `/inventory/product-group/{id}` | `get_group()` | Group with items (product_name, product_code) |
| Create | POST | `/inventory/product-group/` | `create_group()` | Create group |
| Update | PATCH | `/inventory/product-group/{id}` | `update_group()` | Partial update |
| Delete | DELETE | `/inventory/product-group/{id}` | `delete_group()` | Soft delete |

### 3.6 Product Group Items Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/product-group-items/` | `list_items()` | Items with product_name, group_name, variant_name |
| Get Single | GET | `/inventory/product-group-items/{id}` | `get_item()` | Single item with full context |
| Create | POST | `/inventory/product-group-items/` | `create_item()` | Assign product to group |
| Update | PATCH | `/inventory/product-group-items/{id}` | `update_item()` | Partial update |
| Delete | DELETE | `/inventory/product-group-items/{id}` | `delete_item()` | Soft delete |
| Delete by Group/Product | DELETE | `/inventory/product-group-items/by-group-product` | `delete_by_group_product_variant()` | Delete specific product/variant from group |
| Bulk Assign | POST | `/inventory/product-group/{id}/items/bulk` | `bulk_assign_products()` | Assign multiple products at once |

### 3.7 Variant Group Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/variant-group/` | `list_groups()` | Variant groups with pagination |
| Get Single | GET | `/inventory/variant-group/{id}` | `get_group()` | Group with items (variant_name, product_name, SKU) |
| Create | POST | `/inventory/variant-group/` | `create_group()` | Create variant group |
| Update | PATCH | `/inventory/variant-group/{id}` | `update_group()` | Partial update |
| Delete | DELETE | `/inventory/variant-group/{id}` | `delete_group()` | Soft delete |
| Bulk Assign | POST | `/inventory/variant-group/{id}/items/bulk` | `bulk_assign_variants()` | Bulk assign variants to group |

### 3.8 Variant Group Items Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/variant-group-items/` | `list_items()` | Items with group_name, variant_name, product_name, SKU |
| Get Single | GET | `/inventory/variant-group-items/{id}` | `get_item()` | Single item |
| Create | POST | `/inventory/variant-group-items/` | `create_item()` | Assign variant to group |
| Create (Variant) | POST | `/inventory/variant-group-items/variant` | `create_item()` | Variant-specific endpoint |
| Update | PATCH | `/inventory/variant-group-items/{id}` | `update_item()` | Partial update |
| Delete | DELETE | `/inventory/variant-group-items/{id}` | `delete_item()` | Soft delete |
| Delete by Group/Variant | DELETE | `/inventory/variant-group/{id}/items` | `delete_by_group_variant()` | Remove variants from group |

### 3.9 Product Variant Image Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List by Variant | GET | `/inventory/product-variant-images/{variantId}` | `get_by_variant()` | All images ordered by display_order |
| Get Primary | GET | `/inventory/product-variant-images/{variantId}/primary` | `get_primary_image()` | Primary image |
| Get Single | GET | `/inventory/product-variant-images/image/{imageId}` | `get_by_id()` | Single image record |
| Get Metadata | GET | `/inventory/product-variant-images/image/{imageId}/metadata` | — | Image metadata |
| Upload (Single) | POST | `/inventory/product-variant-images/upload` | `upload_image()` | Multipart single upload to S3 |
| Upload (Batch) | POST | `/inventory/product-variant-images/batch-upload` | `batch_upload_images()` | Multipart batch upload |
| Update Metadata | PATCH | `/inventory/product-variant-images/{imageId}` | `update_image()` | Update alt_text, display_order |
| Set Primary | PUT | `/inventory/product-variant-images/{variantId}/primary/{imageId}` | `set_primary_image()` | Set primary, unset others |
| Reorder | PUT | `/inventory/product-variant-images/{variantId}/reorder` | `reorder_images()` | Batch update display_order |
| Delete | DELETE | `/inventory/product-variant-images/{imageId}` | `delete_image()` | Soft delete |
| Bulk Operation | POST | `/inventory/product-variant-images/bulk-operation` | `bulk_image_operation()` | Bulk delete/activate/deactivate/set_primary/remove_primary |
| Presigned URL Request | POST | `/inventory/product-variant-images/presigned-url/request` | `request_presigned_url()` | Generate S3 presigned URL |
| Presigned URL Confirm | POST | `/inventory/product-variant-images/presigned-url/confirm` | `confirm_presigned_upload()` | Confirm upload completion |
| Presigned URL Batch | POST | `/inventory/product-variant-images/presigned-url/batch-request` | `batch_request_presigned_urls()` | Batch presigned URL generation |
| Presigned URL Status | GET | `/inventory/product-variant-images/presigned-url/status/{s3Key}` | `get_presigned_url_status()` | Check upload status |
| Presigned URL Retry | POST | `/inventory/product-variant-images/presigned-url/retry/{s3Key}` | `retry_presigned_upload()` | Retry failed upload |
| Presigned URL Cleanup | POST | `/inventory/product-variant-images/presigned-url/cleanup` | `cleanup_presigned_upload()` | Cleanup failed upload records |
| Pending Uploads | GET | `/inventory/product-variant-images/{variantId}/pending-uploads` | `get_pending_uploads()` | Get pending uploads |
| Upload Stats (Variant) | GET | `/inventory/product-variant-images/upload-stats/{variantId}` | `get_upload_statistics()` | Variant upload statistics |
| Upload Stats (Company) | GET | `/inventory/product-variant-images/upload-stats/company` | `get_company_upload_statistics()` | Company-wide upload stats |
| Image Validation | POST | `/inventory/product-variant-images/validate` | `validate_image()` | Validate image file (type, size, dimensions) |

### 3.10 Unit of Measure Entity

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| List | GET | `/inventory/unit-of-measure/` | `list_uoms()` | UOMs with company_name, base_unit_name |
| Get Single | GET | `/inventory/unit-of-measure/{id}` | `get_uom()` | Single UOM with company and base unit |
| Get Related | GET | `/inventory/unit-of-measure/{id}/related` | `get_related_uoms()` | Base unit + all derived units |
| Create | POST | `/inventory/unit-of-measure/` | `create_uom()` | Create UOM with optional base unit |
| Update | PATCH | `/inventory/unit-of-measure/{id}` | `update_uom()` | Partial update |
| Delete | DELETE | `/inventory/unit-of-measure/{id}` | `delete_uom()` | Soft delete |

### 3.11 Product Import Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| Validate (Nested) | POST | `/inventory/product-import/validate-nested` | `validate_nested_import()` | Validate Excel import (4 sheets: Products, Variants, Prices, Stocks) |
| Import (Nested) | POST | `/inventory/product-import/import-nested` | `import_nested_products()` | Full nested import across multiple sheets |
| Download Template | GET | `/inventory/product-import/template` | — | Download Excel template file |

### 3.12 Elasticsearch Operations

| Operation | Service Method | Description |
|-----------|----------------|-------------|
| Index Single | `index_product()` | Index single product to ES |
| Index All | `index_all_products()` | Bulk reindex all products |
| Delete from Index | `delete_product()` | Remove product from ES index |
| Delete Index | `delete_index()` | Delete entire products index |
| Search | `search_products()` | Full-text search with fuzzy matching, nested filtering |
| Search by SKU | `search_by_sku()` | Dedicated SKU search with fuzzy/partial matching |

### 3.13 Other Backend Operations

| Operation | Description |
|-----------|-------------|
| Product Code Generation | `POST /utils/code?product_name=` — AI-generated product code and description |
| Product Subscriber | SQLAlchemy event listeners auto-update ES index on product/variant create/update/delete |
| Batch Tracking Integration | When batch tracking enabled: creates synthetic batches on creation, blocks direct stock mutations, enforces sync via InventorySyncService |
| Unit Conversion | Converts quantities to base UOM using `conversion_factor` during import/creation |
| Image Validation Service | Validates MIME type (PNG/JPG/WEBP/GIF), file size (5MB max), file name security (no path traversal) |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| Products List | `/products` | ✅ Complete | Paginated, filterable, searchable table with bulk actions, import/export |
| Add Product | `/products/new` | ✅ Complete | Two-step workflow: select/create product → add variants |
| Product Stats | `/products/stats` | ⚠️ Incomplete | Placeholder only (all code commented out) |
| Categories List | `/categories` | ✅ Complete | Hierarchical category list with breadcrumb, dependency-aware delete |
| Add Category | `/categories/new` | ✅ Complete | Category creation form |
| Product Groups List | `/product-groups` | ✅ Complete | Groups list with assign/view/remove products |
| Add Product Group | `/product-groups/new` | ✅ Complete | Group creation form |

### 4.2 Forms & Modals

| Component | File | Purpose |
|-----------|------|---------|
| `ProductForm` | `components/forms/ProductForm.tsx` | Core product create/edit with variant management |
| `AddVariantModal` | `components/forms/AddVariantModal.tsx` | Add variant during product creation (in-memory) |
| `CreateVariantDirectlyModal` | `components/forms/CreateVariantDirectlyModal.tsx` | Create variant for existing product (direct API) |
| `EditVariantPriceForm` | `components/forms/EditVariantPriceForm.tsx` | Edit variant details (SKU, attributes, active status) |
| `ProductPriceForm` | `components/forms/ProductPriceForm.tsx` | Create/update pricing for a variant |
| `ProductGroupForm` | `components/forms/ProductGroupForm.tsx` | Create/edit product group |
| `CategoryForm` | `components/forms/CategoryForm.tsx` | Create/edit category with parent selection |
| `VariantEditForm` | `components/forms/VariantEditForm.tsx` | Inline variant editing (embedded) |
| `SelectProductModal` | `components/forms/SelectProductModal.tsx` | Searchable product selection modal |
| `CreateProductModal` | `components/forms/CreateProductModal.tsx` | Modal wrapper for ProductForm |
| `ConfirmProductSelectionModal` | `components/forms/ConfirmProductSelectionModal.tsx` | Confirmation before adding variants |
| `AssignProductForm` | `components/forms/AssignProductForm.tsx` | Assign product variants to a group |
| `AssignProductToSRForm` | `components/forms/AssignProductToSRForm.tsx` | Assign products to SR with custom pricing |
| `AssignProductWithPriceModal` | `components/sr/AssignProductWithPriceModal.tsx` | SR price assignment with override limits |
| `SRPriceHistory` | `components/sr/SRPriceHistory.tsx` | Price change history for SR assignments |

### 4.3 Shared Components

| Component | File | Purpose |
|-----------|------|---------|
| `ProductImageGallery` | `components/shared/ProductImageGallery.tsx` | Image management: drag-drop reorder, primary, alt text, upload |
| `ConfirmProductDeleteDialog` | `components/shared/ConfirmProductDeleteDialog.tsx` | Enhanced delete confirmation (typed variant name required) |
| `ProductsFilter` | `components/ProductsFilter.tsx` | Filter bar: Category, Group, Status, Price Range |
| `ProductGroupFilter` | `components/ProductGroupFilter.tsx` | Custom filter select for product groups |
| `ViewGroupProducts` | `components/ViewGroupProducts.tsx` | View products in a group with remove capability |
| `ViewGroupProductVariants` | `components/ViewGroupProductVariants.tsx` | Variant-level view of group items |
| `InventoryByProduct` | `components/InventoryByProduct.tsx` | Product analytics: KPIs + 6 charts |
| `ImportExportButton` | (referenced in Products.tsx) | Excel import/export with 4-sheet template |

### 4.4 Context Providers

| Context | File | Purpose |
|---------|------|---------|
| `ProductSelectionContext` | `contexts/ProductSelectionContext.tsx` | Persists selected product across navigation (localStorage) |
| `ProductVariantContext` | `contexts/ProductVariantContext.tsx` | Manages in-memory variant list during creation |
| `NewProductContext` | `contexts/NewProductContext.tsx` | Shares newly created product data between components |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `productsApi.ts` | `getProducts`, `searchProducts`, `getProductById`, `createProduct`, `updateProduct`, `deleteProduct`, `generateProductCode`, `updateProductVariant` |
| `productVariantApi.ts` | `getAllVariants`, `getProductVariants`, `createProductVariant`, `updateProductVariant`, `deleteProductVariant`, `deleteProductVariants` (batch) |
| `productPricesApi.ts` | `getProductPrices`, `getProductPriceById`, `createProductPrice`, `updateProductPrice`, `deleteProductPrice` |
| `productGroupApi.ts` | `getProductGroups`, `createProductGroup`, `updateProductGroup`, `deleteProductGroup`, `assignProductsToGroup`, `assignProductToGroup`, `assignVariantToGroup`, `removeProductsFromGroup` |
| `productVariantImageApi.ts` | `getVariantImages`, `getPrimaryImage`, `uploadImage`, `batchUploadImages`, `setPrimaryImage`, `reorderImages`, `deleteImage`, `bulkOperation`, `requestPresignedUrl`, `confirmPresignedUpload`, `batchRequestPresignedUrls`, `getPresignedUrlStatus`, `retryPresignedUpload`, `cleanupPresignedUpload`, `getPendingUploads`, `getCompanyUploadStats` |
| `categoryApi.ts` | `getCategories`, `createCategory`, `updateCategory`, `deleteCategory` |
| `srProductAssignmentPriceApi.ts` | `updateAssignmentPrice`, `getAssignmentPriceHistory`, `bulkUpdatePrices`, `getSRAssignedPrices`, `validatePriceOverride` |

### 4.6 Types & Zod Schemas

| Schema | File | Fields |
|--------|------|--------|
| `insertProductSchema` | `schema/products.ts` | product_name, product_code, category_id, unit_id, description, is_active, company_id, variants, prices, inventory_stocks, product_group_ids |
| `addVariantWithPricesSchema` | `schema/products.ts` | sku, attribute_name, attribute_value, unit_id, reorder_level, safety_stock, is_active, product_price, inventory_stocks |
| `variantWithPricesSchema` | `schema/products.ts` | Full variant with nested prices and stocks |
| `priceSchema` | `schema/products.ts` | purchase_price, retail_price, selling_price, damage_price, currency_id, is_active |
| `inventoryStockSchema` | `schema/products.ts` | location_id, quantity, uom_id |
| `insertCategorySchema` | `schema/index.ts` | category_name, description, parent_category_id, company_id |
| `insertProductGroupSchema` | `schema/index.ts` | group_name, description, company_id, is_active |
| `priceAssignmentSchema` | `schema/srProductAssignmentPrice.ts` | assigned_sale_price, dates, override limits, notes (cross-field validation: min ≤ max, effective < expiry) |
| `bulkPriceAssignmentSchema` | `schema/srProductAssignmentPrice.ts` | Array of price assignments |

---

## 5. Interconnected Workflows

### 5.1 Product Creation Flow

```
Prerequisite: Categories must exist
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Step 1: Navigate to /products/new                  │
│  → SelectProductModal opens automatically            │
│  → Option A: Search & select existing product        │
│  → Option B: Click "Create new product"              │
│     → CreateProductModal opens                       │
│     → Fill: Name, Code (auto-generate), Description, │
│       Category, Active toggle                        │
│     → Submit → product created                       │
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Step 2: Add Variants                                │
│  → ProductForm shows variant management section      │
│  → Click "Add Variant" → AddVariantModal             │
│  → Fill: SKU, Attribute Name/Value, Unit,            │
│    Pricing (purchase, selling, damage, retail),      │
│    Opening Stock (location, quantity, UOM, date)     │
│  → Add to in-memory list (no API call)               │
│  → Repeat for multiple variants                      │
│  → Validation: At least 1 variant required           │
│  → Click "Create Product" → single nested API call   │
│    creates: product + variants + prices + stocks     │
│    + group assignments in one transaction            │
└─────────────────────────────────────────────────────┘
     │
     ▼
  Redirect to /products (table refreshes)
```

### 5.2 Product Management Flow (From List)

```
┌─────────────────────────────────────────────────────┐
│  /products — Main Listing Page                       │
│  ┌─────────────────────────────────────────────┐    │
│  │ Search Bar (Elasticsearch, 500ms debounce)  │    │
│  │ Filters: Category, Group, Status, Price     │    │
│  │ Table: SKU, Variant, Name, Category, Group, │    │
│  │   Reorder, Safety Stock, Qty, Prices, Status│    │
│  │ Bulk Selection + Batch Delete               │    │
│  │ Import/Export buttons                       │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  Row Actions (⋮ dropdown):                          │
│  ├── Edit → EditVariantPriceForm (SKU, attrs, active)│
│  ├── Delete → ConfirmProductDeleteDialog             │
│  │    (must type exact variant name to confirm)      │
│  ├── Create Variant → CreateVariantDirectlyModal     │
│  │    (direct API call for existing product)         │
│  ├── Assign to Group → AssignProductForm             │
│  ├── Update Pricing → ProductPriceForm               │
│  │    (effective date, purchase, selling, damage,    │
│  │     retail prices)                                │
│  └── Manage Images → ProductImageGallery             │
│       (upload, reorder drag-drop, set primary,       │
│        delete, edit alt text)                        │
└─────────────────────────────────────────────────────┘
```

### 5.3 Category Management Flow

```
┌─────────────────────────────────────────────────────┐
│  /categories — Category List                         │
│  Columns: Name, Parent, Hierarchy (breadcrumb),      │
│           Description, Actions                       │
│                                                      │
│  Add → /categories/new → CategoryForm                │
│    Fields: Name (req), Parent (opt), Description     │
│    Duplicate name check on submit                    │
│                                                      │
│  Edit → Pre-filled CategoryForm                      │
│                                                      │
│  Delete → Dependency Check:                          │
│    ├── Has children → DeleteDependencies dialog      │
│    │    (prevents deletion)                          │
│    └── No children → Standard confirmation           │
└─────────────────────────────────────────────────────┘
```

### 5.4 Product Group Management Flow

```
┌─────────────────────────────────────────────────────┐
│  /product-groups — Group List                        │
│  Columns: Group Name, Description, Status, Actions   │
│                                                      │
│  Add → /product-groups/new → ProductGroupForm        │
│    Fields: Name (req), Description, Active toggle    │
│    Duplicate name check                              │
│                                                      │
│  Edit → Pre-filled ProductGroupForm                  │
│                                                      │
│  View Products → ViewGroupProducts dialog            │
│    Table: SKU, Product Name, Variant, Remove action  │
│    "Assign more products" button                     │
│                                                      │
│  Assign Products → AssignProductForm                 │
│    Shows variants NOT in group                       │
│    Warning: assigns ALL variants of the product      │
│                                                      │
│  Delete → Confirmation (type group name)             │
└─────────────────────────────────────────────────────┘
```

### 5.5 Import/Export Flow

```
┌─────────────────────────────────────────────────────┐
│  Export:                                             │
│  → Click "Export" → current table data (with filters)│
│    → Excel file downloads                            │
│                                                      │
│  Import:                                             │
│  → Click "Import" → dialog opens                     │
│  → Download Template → 4 sheets:                     │
│      1. Products (code, name, category_id, etc.)     │
│      2. Variants (code, sku, attrs, unit_id, etc.)   │
│      3. Prices (code, sku, prices, currency_id)      │
│      4. InventoryStocks (code, sku, location, qty)   │
│  → Fill template, link via product_code + sku        │
│  → Upload → Validation Phase:                        │
│      Backend validates all sheets → shows errors     │
│  → If valid → Import Phase:                          │
│      Progress indicator → Summary (imported/skipped) │
│  → Table refreshes                                   │
└─────────────────────────────────────────────────────┘
```

### 5.6 SR Product Assignment Flow

```
┌─────────────────────────────────────────────────────┐
│  Admin: /sales-representatives → Select SR           │
│  → AssignProductToSRForm (two tabs):                 │
│                                                      │
│  Tab 1: Single Product Assignment                    │
│    → Search (debounced) across name, code, SKU       │
│    → Table: Code, Name, Variant, SKU, Sale Price,    │
│      Assigned Price, Actions                         │
│    → Assigned products sorted first                  │
│    → Assign → AssignProductWithPriceModal:           │
│        Fields: Assigned Sale Price (opt),            │
│        Effective Date, Expiry Date (opt),            │
│        Allow Price Override toggle (default: true)   │
│          → Min Override Price (conditional)          │
│          → Max Override Price (conditional)          │
│        Price Notes (max 500 chars)                   │
│        Validation: Min ≤ Max, Effective < Expiry     │
│        Submit: "Assign With Price" or                │
│                "Assign Without Price"                │
│    → Unassign → removes from SR's list               │
│                                                      │
│  Tab 2: By Product Group Assignment                  │
│    → Select product group from dropdown              │
│    → "Assign All" → all products in group assigned   │
│                                                      │
│  View Price History → SRPriceHistory component       │
│    Timeline: Old Price → New Price, timestamps,      │
│    effective/expiry dates, reason, changed by        │
└─────────────────────────────────────────────────────┘
```

### 5.7 Image Management Flow

```
┌─────────────────────────────────────────────────────┐
│  ProductImageGallery (opened from row actions)       │
│                                                      │
│  View: Grid display (2-5 columns responsive)         │
│    Primary image: star badge                         │
│    Hover: star (set primary), trash (delete)         │
│                                                      │
│  Upload:                                             │
│    → Click "Upload" → file picker (PNG/JPG/WEBP)     │
│    → Max 5MB per file                                │
│    → Single or multi-file selection                  │
│    → Upload progress shown                           │
│    → Images appear in grid                           │
│                                                      │
│  Reorder:                                            │
│    → Drag-and-drop using grab handle (@dnd-kit)      │
│    → Order persists on drop → reorderImages() API    │
│                                                      │
│  Set Primary:                                        │
│    → Hover → click star → setPrimaryImage() API      │
│    → Star moves to selected image                    │
│                                                      │
│  Edit Alt Text:                                      │
│    → Click alt text field → inline edit → save blur  │
│                                                      │
│  Delete:                                             │
│    → Click trash → confirmation → deleteImage() API  │
└─────────────────────────────────────────────────────┘
```

### 5.8 Product Analytics Flow

```
┌─────────────────────────────────────────────────────┐
│  InventoryByProduct Component                        │
│                                                      │
│  Selectors:                                          │
│    → Product dropdown (searchable)                   │
│    → Variant dropdown (filtered by product)          │
│                                                      │
│  KPI Cards:                                          │
│    → Current Stock                                   │
│    → Units Sold                                      │
│    → Total Revenue                                   │
│    → Total Profit                                    │
│    → Average Unit Profit                             │
│                                                      │
│  Charts (Recharts):                                  │
│    → Top Suppliers (bar)                             │
│    → Inventory Timeline (line)                       │
│    → Variant Stock (bar)                             │
│    → Variant Sales (pie/bar)                         │
│    → Customer Sales Trend (line)                     │
│    → Top Customers (bar)                             │
└─────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Elasticsearch Integration

**Purpose:** Fast, fuzzy full-text search across products and variants.

**Index Structure (`products` index):**
```json
{
  "product_id": 1,
  "product_name": "Wireless Mouse",
  "product_code": "WM-001",
  "category_id": 5,
  "category_name": "Peripherals",
  "variants": [
    {
      "variant_id": 10,
      "sku": "WM-001-BLK",
      "attribute_name": "Color",
      "attribute_value": "Black",
      "product_price": {
        "purchase_price": 500,
        "selling_price": 800,
        "retail_price": 1000
      },
      "unit_name": "Piece"
    }
  ],
  "inventory_stocks": [
    {
      "location_id": 1,
      "quantity": 150
    }
  ],
  "product_group_ids": [3, 7],
  "product_group_names": ["Computer Accessories", "Best Sellers"]
}
```

**Search Capabilities:**
- Fuzzy matching on product name, code, SKU, variant attributes
- Filtered search: category_id, is_active, price_range_min/max, variant_group_id
- Nested field filtering (search within variants, prices, stocks)
- Dedicated SKU search with partial matching

**Auto-Indexing:**
- SQLAlchemy event subscriber (`product_subscriber.py`) automatically indexes on create/update/delete
- Manual reindex: `POST /admin/reindex/products`

### 6.2 Batch Tracking Integration

**When batch tracking is enabled** (`CompanyInventorySetting.batch_tracking = true`):

1. **On Product/Variant Creation:**
   - Synthetic batches are created automatically for opening stock
   - Batch records link to source type: `opening_balance` or `synthetic`

2. **Stock Mutations:**
   - Direct stock mutations are BLOCKED
   - All stock changes must go through batch allocation service
   - `InventorySyncService.apply_stock_mutation` syncs batch ↔ legacy stock

3. **Variant Nested Update:**
   - Calculates delta between existing and requested stock
   - Syncs via `InventorySyncService` instead of direct stock manipulation

4. **Frontend Behavior:**
   - `list_variants_nested()` returns `batch_stocks` instead of `inventory_stocks`
   - `total_stock` calculated from batch `qty_on_hand`

### 6.3 Unit Conversion System

**Structure:**
```
UnitOfMeasure (Base)
  ├── unit_name: "Piece", is_base: true, conversion_factor: 1
  │
  └── Derived Units (base_id → base unit)
      ├── unit_name: "Dozen", conversion_factor: 12
      ├── unit_name: "Gross", conversion_factor: 144
      └── unit_name: "Carton", conversion_factor: 24
```

**Usage:**
- Variants reference a unit via `unit_id`
- Stock quantities stored in base UOM
- Display converts using `conversion_factor`
- Import/creation converts to base UOM automatically
- `get_related_uoms()` returns base + all derivatives

### 6.4 Multi-Tier Pricing

**Price Types per Variant:**
| Price Type | Purpose |
|------------|---------|
| `purchase_price` | Cost price from supplier |
| `selling_price` | Standard selling price |
| `retail_price` | MRP (Maximum Retail Price) |
| `damage_price` | Price for damaged goods |
| `dealer_price` | Dealer-specific pricing |
| `trade_price` | Trade-specific pricing |
| `maximum_retail_price` | Ceiling for retail |
| `minimum_retail_price` | Floor for retail |
| `maximum_selling_price` | Ceiling for selling |
| `minimum_selling_price` | Floor for selling |

**Time-Effective Pricing:**
- Multiple price records per variant with different `effective_date`
- System uses the most recent price where `effective_date <= now()`
- Price history maintained for audit

**SR-Specific Pricing:**
- `SR_Product_Assignment` links products to SRs with custom prices
- Override limits: `min_override_price`, `max_override_price`
- Price validity: `price_effective_date`, `price_expiry_date`
- Full audit trail in `SR_Product_Assignment_Price_History`

### 6.5 Image Storage (S3)

**Upload Methods:**
1. **Direct Multipart Upload:**
   - File → Backend → S3 → Image record created
   - Used for single and batch uploads

2. **Presigned URL Upload:**
   - Frontend requests presigned URL
   - Frontend uploads directly to S3
   - Frontend confirms upload → Image record created
   - Used for large files, better performance

**Validation:**
- Allowed MIME types: PNG, JPG, JPEG, WEBP, GIF
- Max file size: 5MB
- File name security: no path traversal characters
- Optional dimension validation (width, height)

**Features:**
- Primary image selection (one per variant)
- Display order for gallery sequencing
- Alt text for accessibility
- Upload status tracking (pending/completed/failed)
- Retry mechanism for failed uploads
- Cleanup for abandoned presigned uploads

### 6.6 Hierarchical Categories

**Structure:**
```
Electronics (parent_category_id: NULL)
├── Phones (parent_category_id: Electronics)
│   ├── Smartphones (parent_category_id: Phones)
│   └── Feature Phones (parent_category_id: Phones)
└── Accessories (parent_category_id: Electronics)
    ├── Cases (parent_category_id: Accessories)
    └── Chargers (parent_category_id: Accessories)
```

**Frontend Display:**
- Breadcrumb: "Electronics > Phones > Smartphones"
- Parent category dropdown in forms
- Dependency-aware deletion (prevents deleting categories with children)

### 6.7 Product Groups vs Variant Groups

| Aspect | Product Group | Variant Group |
|--------|--------------|---------------|
| **Purpose** | Group products for bulk operations (SR assignment, batch sales) | Group specific variants for rapid selection (POS, quick order) |
| **Assignment** | Product-level (assigns ALL variants) | Variant-level (specific variants only) |
| **Items Table** | `product_group_items` (product_id + optional variant_id) | `variant_group_items` (variant_id only) |
| **Use Case** | "Assign all products in 'Computer Accessories' to SR" | "Quick-select these 5 specific variants in POS" |
| **Warning** | "Assigning any product to group will assign all variants" | N/A |

### 6.8 Cascade Delete Behavior

**Deleting a Product:**
```
Product.is_deleted = True
  ├── All ProductVariants.is_deleted = True
  │   ├── All ProductPrices.is_deleted = True
  │   └── All ProductVariantImages.is_deleted = True (cascade)
  └── All ProductGroupItems.is_deleted = True
```

**Deleting a Variant:**
```
ProductVariant.is_deleted = True
  ├── All ProductPrices.is_deleted = True
  └── All ProductVariantImages.is_deleted = True (cascade)
```

**Deleting Last Variant:**
- Triggers cascade product deletion
- Confirmation dialog warns about this
- Requires typing exact variant name to confirm

### 6.9 Import Validation & Error Reporting

**Validation Checks:**
1. Product code uniqueness within company
2. Category existence
3. Unit of measure existence
4. Location existence (for stocks)
5. Currency existence (for prices)
6. Required fields presence
7. Numeric field validity
8. Date format validity
9. Duplicate detection (existing products/variants)

**Error Response Format:**
```json
{
  "valid": false,
  "total_rows": 150,
  "errors": [
    {
      "sheet": "Variants",
      "row": 5,
      "product_code": "WM-001",
      "sku": "WM-001-BLK",
      "errors": ["Category 'Electronics' not found", "Unit 'Box' not found"]
    }
  ]
}
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **Product** | GET `/inventory/product/` | GET `/{id}` | POST `/nested` | PATCH `/{id}/` | DELETE `/{id}/` | Search, Batch Delete |
| **Variant** | GET `/product-variant/nested` | GET `/{id}` | POST `/nested` | PATCH `/{id}/nested` | DELETE `/{id}` | By IDs, Batch Delete |
| **Category** | GET `/product-category/` | GET `/{id}` | POST `/` | PATCH `/{id}` | DELETE `/{id}` | — |
| **Price** | GET `/product-price/` | GET `/{id}/` | POST `/` | PATCH `/{id}/` | DELETE `/{id}/` | — |
| **Product Group** | GET `/product-group/` | GET `/{id}` | POST `/` | PATCH `/{id}` | DELETE `/{id}` | Bulk Assign |
| **Group Items** | GET `/product-group-items/` | GET `/{id}` | POST `/` | PATCH `/{id}` | DELETE `/{id}` | By Group/Product |
| **Variant Group** | GET `/variant-group/` | GET `/{id}` | POST `/` | PATCH `/{id}` | DELETE `/{id}` | Bulk Assign |
| **Variant Group Items** | GET `/variant-group-items/` | GET `/{id}` | POST `/` | PATCH `/{id}` | DELETE `/{id}` | By Group/Variant |
| **Images** | GET `/{variantId}` | GET `/image/{imageId}` | POST `/upload` | PATCH `/{imageId}` | DELETE `/{imageId}` | Presigned URLs, Bulk Ops |
| **UOM** | GET `/unit-of-measure/` | GET `/{id}` | POST `/` | PATCH `/{id}` | DELETE `/{id}` | Related UOMs |
| **Import** | — | — | POST `/validate-nested` | — | — | Download Template |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-------------------|------------------|
| List products | `getProducts(start, limit, params)` | GET `/inventory/product/` |
| Search products | `searchProducts(query, params)` | GET `/inventory/product/search` |
| Get product | `getProductById(id)` | GET `/inventory/product/{id}` |
| Create product | `createProduct(data)` | POST `/inventory/product/nested` |
| Update product | `updateProduct(productId, data)` | PATCH `/inventory/product/{productId}/` |
| Delete product | `deleteProduct(id)` | DELETE `/inventory/product/{id}/` |
| List variants | `getAllVariants(start, limit, params)` | GET `/inventory/product-variant/nested` |
| Create variant | `createProductVariant(data, productId)` | POST `/inventory/product-variant/nested` |
| Update variant | `updateProductVariant({id, ...data})` | PATCH `/inventory/product-variant/{id}` |
| Delete variant | `deleteProductVariant(id)` | DELETE `/inventory/product-variant/{id}` |
| Batch delete variants | `deleteProductVariants(ids[])` | POST `/inventory/product-variant/batch-delete` |
| List categories | `getCategories(start, limit, params)` | GET `/inventory/product-category/` |
| Create category | `createCategory(data)` | POST `/inventory/product-category/` |
| Update category | `updateCategory(data)` | PATCH `/inventory/product-category/{id}` |
| Delete category | `deleteCategory(id)` | DELETE `/inventory/product-category/{id}` |
| List groups | `getProductGroups(start, limit)` | GET `/inventory/variant-group/` |
| Create group | `createProductGroup(data)` | POST `/inventory/variant-group/` |
| Update group | `updateProductGroup(data)` | PATCH `/inventory/variant-group/{id}` |
| Delete group | `deleteProductGroup(id)` | DELETE `/inventory/variant-group/{id}` |
| Assign to group | `assignProductsToGroup(variantGroupId, productIds[])` | POST `/inventory/variant-group/{id}/items` |
| Remove from group | `removeProductsFromGroup(variantGroupId, productIds[])` | DELETE `/inventory/variant-group/{id}/items` |
| Get variant images | `getVariantImages(variantId)` | GET `/inventory/product-variant-images/{variantId}` |
| Upload image | `uploadImage(variantId, formData)` | POST `/inventory/product-variant-images/upload` |
| Set primary image | `setPrimaryImage(variantId, imageId)` | PUT `/inventory/product-variant-images/{variantId}/primary/{imageId}` |
| Reorder images | `reorderImages(variantId, imageIds[])` | PUT `/inventory/product-variant-images/{variantId}/reorder` |
| Delete image | `deleteImage(imageId)` | DELETE `/inventory/product-variant-images/{imageId}` |
| Request presigned URL | `requestPresignedUrl(variantId, data)` | POST `/inventory/product-variant-images/presigned-url/request` |
| Confirm presigned upload | `confirmPresignedUpload(variantId, data)` | POST `/inventory/product-variant-images/presigned-url/confirm` |
| Update SR price | `updateAssignmentPrice(assignmentId, data)` | PATCH `/sr/product-assignments/{id}/price` |
| Get price history | `getAssignmentPriceHistory(assignmentId, ...)` | GET `/sr/product-assignments/{id}/price-history` |
| Validate price override | `validatePriceOverride(assignmentId, proposedPrice)` | GET `/sr/product-assignments/{id}/validate-price` |
| Generate product code | `generateProductCode(productName)` | POST `/utils/code?product_name=` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/inventory.py` | All product-related SQLAlchemy models |
| **Schemas** | `Shoudagor/app/schemas/inventory/product.py` | Product Pydantic schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/product_variant.py` | Variant schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/product_category.py` | Category schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/product_price.py` | Price schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/product_group.py` | Group schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/product_variant_image.py` | Image schemas (546 lines) |
| **Schemas** | `Shoudagor/app/schemas/inventory/variant_group.py` | Variant group schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/unit_of_measure.py` | UOM schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/product_import_nested.py` | Import schemas |
| **Schemas** | `Shoudagor/app/schemas/inventory/filters.py` | Filter parameter schemas |
| **Schemas** | `Shoudagor/app/schemas/elasticsearch.py` | ES index schemas |
| **Repositories** | `Shoudagor/app/repositories/inventory/product.py` | Product data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/product_variant.py` | Variant data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/product_category.py` | Category data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/product_price.py` | Price data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/product_group.py` | Group data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/product_group_items.py` | Group items data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/product_variant_image.py` | Image data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/variant_group.py` | Variant group data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/variant_group_items.py` | Variant group items data access |
| **Repositories** | `Shoudagor/app/repositories/inventory/unit_of_measure.py` | UOM data access |
| **Services** | `Shoudagor/app/services/inventory/product_service.py` | Product business logic |
| **Services** | `Shoudagor/app/services/inventory/product_variant_service.py` | Variant business logic |
| **Services** | `Shoudagor/app/services/inventory/product_category_service.py` | Category business logic |
| **Services** | `Shoudagor/app/services/inventory/product_price_service.py` | Price business logic |
| **Services** | `Shoudagor/app/services/inventory/product_group_service.py` | Group business logic |
| **Services** | `Shoudagor/app/services/inventory/product_group_items_service.py` | Group items business logic |
| **Services** | `Shoudagor/app/services/inventory/product_variant_image_service.py` | Image business logic |
| **Services** | `Shoudagor/app/services/inventory/product_import_nested_service.py` | Import business logic |
| **Services** | `Shoudagor/app/services/inventory/variant_group_service.py` | Variant group business logic |
| **Services** | `Shoudagor/app/services/inventory/variant_group_items_service.py` | Variant group items business logic |
| **Services** | `Shoudagor/app/services/inventory/unit_of_measure_service.py` | UOM business logic |
| **Services** | `Shoudagor/app/services/inventory/image_validation_service.py` | Image validation |
| **Services** | `Shoudagor/app/services/product_elasticsearch_service.py` | ES indexing/search |
| **API** | `Shoudagor/app/api/inventory/product.py` | Product endpoints |
| **API** | `Shoudagor/app/api/inventory/product_variant.py` | Variant endpoints |
| **API** | `Shoudagor/app/api/inventory/product_category.py` | Category endpoints |
| **API** | `Shoudagor/app/api/inventory/product_price.py` | Price endpoints |
| **API** | `Shoudagor/app/api/inventory/product_group.py` | Group endpoints |
| **API** | `Shoudagor/app/api/inventory/product_group_items.py` | Group items endpoints |
| **API** | `Shoudagor/app/api/inventory/product_variant_image.py` | Image endpoints |
| **API** | `Shoudagor/app/api/inventory/product_import.py` | Import endpoints |
| **API** | `Shoudagor/app/api/inventory/product_import_nested.py` | Nested import endpoints |
| **API** | `Shoudagor/app/api/inventory/variant_group.py` | Variant group endpoints |
| **API** | `Shoudagor/app/api/inventory/variant_group_items.py` | Variant group items endpoints |
| **API** | `Shoudagor/app/api/inventory/unit_of_measure.py` | UOM endpoints |
| **Subscribers** | `Shoudagor/app/subscribers/product_subscriber.py` | ES auto-indexing events |
| **Config** | `Shoudagor/app/core/elasticsearch_config.py` | ES connection config |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages** | `shoudagor_FE/src/pages/products/Products.tsx` | Product list page |
| **Pages** | `shoudagor_FE/src/pages/products/new/AddProduct.tsx` | Add product page |
| **Pages** | `shoudagor_FE/src/pages/products/ProductStats.tsx` | Product stats (incomplete) |
| **Pages** | `shoudagor_FE/src/pages/categories/Categories.tsx` | Category list page |
| **Pages** | `shoudagor_FE/src/pages/categories/new/AddCategory.tsx` | Add category page |
| **Pages** | `shoudagor_FE/src/pages/product-groups/ProductGroups.tsx` | Group list page |
| **Pages** | `shoudagor_FE/src/pages/product-groups/new/AddProductGroup.tsx` | Add group page |
| **Forms** | `shoudagor_FE/src/components/forms/ProductForm.tsx` | Product create/edit form |
| **Forms** | `shoudagor_FE/src/components/forms/AddVariantModal.tsx` | Add variant modal |
| **Forms** | `shoudagor_FE/src/components/forms/CreateVariantDirectlyModal.tsx` | Direct variant creation |
| **Forms** | `shoudagor_FE/src/components/forms/EditVariantPriceForm.tsx` | Edit variant form |
| **Forms** | `shoudagor_FE/src/components/forms/ProductPriceForm.tsx` | Price form |
| **Forms** | `shoudagor_FE/src/components/forms/ProductGroupForm.tsx` | Group form |
| **Forms** | `shoudagor_FE/src/components/forms/CategoryForm.tsx` | Category form |
| **Forms** | `shoudagor_FE/src/components/forms/VariantEditForm.tsx` | Inline variant edit |
| **Forms** | `shoudagor_FE/src/components/forms/SelectProductModal.tsx` | Product selection modal |
| **Forms** | `shoudagor_FE/src/components/forms/CreateProductModal.tsx` | Create product modal |
| **Forms** | `shoudagor_FE/src/components/forms/ConfirmProductSelectionModal.tsx` | Selection confirmation |
| **Forms** | `shoudagor_FE/src/components/forms/AssignProductForm.tsx` | Assign to group form |
| **Forms** | `shoudagor_FE/src/components/forms/AssignProductToSRForm.tsx` | SR assignment form |
| **Forms** | `shoudagor_FE/src/components/sr/AssignProductWithPriceModal.tsx` | SR price assignment |
| **Forms** | `shoudagor_FE/src/components/sr/SRPriceHistory.tsx` | Price history display |
| **Shared** | `shoudagor_FE/src/components/shared/ProductImageGallery.tsx` | Image management |
| **Shared** | `shoudagor_FE/src/components/shared/ConfirmProductDeleteDialog.tsx` | Delete confirmation |
| **Shared** | `shoudagor_FE/src/components/ProductsFilter.tsx` | Product filter bar |
| **Shared** | `shoudagor_FE/src/components/ProductGroupFilter.tsx` | Group filter |
| **Shared** | `shoudagor_FE/src/components/ViewGroupProducts.tsx` | View group products |
| **Shared** | `shoudagor_FE/src/components/ViewGroupProductVariants.tsx` | View group variants |
| **Shared** | `shoudagor_FE/src/components/InventoryByProduct.tsx` | Product analytics |
| **API** | `shoudagor_FE/src/lib/api/productsApi.ts` | Product API functions |
| **API** | `shoudagor_FE/src/lib/api/productVariantApi.ts` | Variant API functions |
| **API** | `shoudagor_FE/src/lib/api/productPricesApi.ts` | Price API functions |
| **API** | `shoudagor_FE/src/lib/api/productGroupApi.ts` | Group API functions |
| **API** | `shoudagor_FE/src/lib/api/productVariantImageApi.ts` | Image API functions |
| **API** | `shoudagor_FE/src/lib/api/categoryApi.ts` | Category API functions |
| **API** | `shoudagor_FE/src/lib/api/srProductAssignmentPriceApi.ts` | SR price API functions |
| **Contexts** | `shoudagor_FE/src/contexts/ProductSelectionContext.tsx` | Product selection context |
| **Contexts** | `shoudagor_FE/src/contexts/ProductVariantContext.tsx` | Variant context |
| **Contexts** | `shoudagor_FE/src/contexts/NewProductContext.tsx` | New product context |
| **Schemas** | `shoudagor_FE/src/lib/schema/products.ts` | Product Zod schemas + types |
| **Schemas** | `shoudagor_FE/src/lib/schema/productVariants.ts` | Variant types |
| **Schemas** | `shoudagor_FE/src/lib/schema/index.ts` | Shared schemas (Category, Group) |
| **Schemas** | `shoudagor_FE/src/lib/schema/srProductAssignmentPrice.ts` | SR price schemas |
| **Charts** | `shoudagor_FE/src/components/charts/VariantStocksChart.tsx` | Variant stock chart |
| **Charts** | `shoudagor_FE/src/components/charts/VariantSalesChart.tsx` | Variant sales chart |
| **Charts** | `shoudagor_FE/src/components/charts/UnitPriceSuppliers.tsx` | Unit price comparison |
| **Routes** | `shoudagor_FE/src/App.tsx` | Route definitions |

---

## Appendix: Operation Counts

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|----------------------|---------------------|
| Product | 5 | 4 | 11 | 5 |
| Product Variant | 5 | 4 | 6 | 4 |
| Product Category | 5 | 0 | 4 | 1 |
| Product Price | 5 | 0 | 5 | 1 |
| Product Group | 5 | 1 | 9 | 3 |
| Product Group Items | 5 | 1 | — | 2 |
| Variant Group | 5 | 2 | — | — |
| Variant Group Items | 5 | 1 | — | — |
| Product Variant Image | 4 | 14 | 19 | 1 |
| Unit of Measure | 5 | 1 | — | — |
| Product Import | — | 2 | — | 1 |
| Elasticsearch | — | 5 | 1 | — |
| SR Price | — | 5 | 5 | 2 |
| **TOTAL** | **49** | **40** | **60** | **20** |
