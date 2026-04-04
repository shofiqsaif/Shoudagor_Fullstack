# SR Program Workflow - Detailed Implementation Plan

**Project:** Shoudagor Fullstack  
**Created:** April 1, 2026  
**Status:** Implementation Plan (Ready for Execution)  
**Source Spreadsheet:** `Sales March-25.xlsx` — Sheet: `SR Proggram`

---

## 1. Executive Summary

This plan details the implementation of a **new SR Program Workflow report** that replicates the 7-block spreadsheet workflow currently managed manually in Excel. The feature adds a dedicated page at `/reports/sr-program` with group-centric analytics, channel splits, sales projections, cash tracking, undelivery analysis, and year-over-year growth comparison.

**Key decisions:**
- Keep existing `/reports/sr` profitability report unchanged
- Add new `/reports/sr-program` page with 7 workflow blocks
- Fix the `order_source` bug (`'sr_order'` vs `'sr_consolidated'`) as part of this work
- Build full admin UI for channel mapping management
- Implement backend + frontend together in one pass

---

## 2. Spreadsheet Reverse Engineering

### 2.1 Source Structure (SR Proggram Sheet)

The sheet contains **7 distinct workflow blocks** across rows 4–104, columns B–AJ:

| Block | Rows | Columns | Purpose |
|-------|------|---------|---------|
| **A** | 4–20 | AD–AJ | SR Report vs Khata Reconciliation (daily comparison) |
| **B** | 31–41 | C–F | Group-wise Commission & Market Credit |
| **C** | 31–39 | K–O | Distributor Channel Split (Muslim Bakary / Traders / Auto) |
| **D** | 42–57 | B–F | Sales Projection (avg/day × full month) |
| **E** | 72–82 | D–E | Group-wise DO Cash |
| **F** | 84–94 | C–F | Group-wise Undelivery (Total / Web / Sample) |
| **G** | 98–104 | B–T | Year-over-Year Growth Comparison |

### 2.2 Product Groups Identified

From the spreadsheet, **7 product groups** are tracked:

| Group | Daily Report Source | Commission Cell | Market Credit Cell |
|-------|---------------------|-----------------|-------------------|
| Gems | `Daily Report!AX` | `Daily Report!AY40` | `Daily Report!AZ40` |
| Ketchup | `Daily Report!W` | `Daily Report!X40` | `Daily Report!Y40` |
| Juicepack | `Daily Report!E` | `Daily Report!F40` | `Daily Report!G40` |
| Treat | `Daily Report!BG` | `Daily Report!BH40` | `Daily Report!BI40` |
| milkman | `Daily Report!AF` | `Daily Report!AG40` | `Daily Report!AH40` |
| Wonder | `Daily Report!N` | `Daily Report!O40` | `Daily Report!P40` |
| Danish | `Daily Report!AO` | `Daily Report!AP40` | `Daily Report!AQ40` |

### 2.3 Channel Mapping (Block C)

| Group | Muslim Bakary | Traders | Auto |
|-------|---------------|---------|------|
| Gems | `Daily Report!BA49` | `Daily Report!BA51` | `Daily Report!BA56` |
| Ketchup | `Daily Report!Z45` | `Daily Report!Z46` | `Daily Report!Z50` |
| Juicepack | `Daily Report!H48` | `0` | `Daily Report!H51` |
| Wonder | `Daily Report!P51` | `0` | `0` |
| Treat | `Daily Report!BJ46` | `Daily Report!BJ51` | `Daily Report!BJ47` |
| Danish | `0` | `0` | `Daily Report!AQ54` |
| milkman | `0` | `Daily Report!AI49` | `0` |

### 2.4 Key Formulas Locked

| Metric | Formula | Source |
|--------|---------|--------|
| **Commission** | Pulled from `Daily Report!{col}40` per group | Block B |
| **Market Credit** | Pulled from `Daily Report!{col}40` per group | Block B |
| **Total (Block B)** | `D32+D33+...+D38` (sum of all groups) | Row 41 |
| **Grand Total** | `SUM(D41:E41)` (commission + market credit) | F41 |
| **Avg Sales/Day** | `Sales Report / 23` (elapsed working days) | Block D |
| **Sales Projection** | `Avg/Day × 24` (full month projection) | Block D |
| **DO Cash** | Pulled from `Daily Report!{col}38` per group | Block E |
| **Sample Product** | `Total Undelivery - Web Undelivery` | Block F |
| **Growth Volume** | `2024 Total - 2023 Total` | Block G |
| **Growth %** | `(2024 - 2023) / 2023 × 100` | Block G |

---

## 3. Current State Analysis

### 3.1 Existing SR Report Stack

**Backend:**
- Repository: `Shoudagor/app/repositories/reports/sr_reports.py` (3 queries)
- Service: `Shoudagor/app/services/reports.py` methods `get_sr_summary_report()`, `get_sr_product_variants()`, `get_sr_product_variant_details()`
- API: `Shoudagor/app/api/reports.py` endpoints `/sr-summary`, `/sr-product-variants/{sr_id}`, `/sr-product-variant-details/{sr_id}`

**Frontend:**
- Page: `shoudagor_FE/src/pages/reports/SRReports.tsx` (180 lines)
- API Client: `shoudagor_FE/src/lib/api/srReportsApi.ts` (3 functions, 7 interfaces)
- Modals: `SRDetailModal.tsx`, `SRProductVariantDetailModal.tsx`

### 3.2 Critical Bug: Order Source Inconsistency

**Problem:**
- `consolidation_service.py:401` sets `order_source = 'sr_consolidated'`
- `sales_reports.py:504` and `:728` query `order_source = 'sr_order'`
- Result: Pipeline and conversion reports return **zero records** for SR-originated orders

**Fix:** Update queries to use `order_source IN ('sr_order', 'sr_consolidated')` or normalize to a single value.

### 3.3 Data Model Readiness

| Entity | Status | Notes |
|--------|--------|-------|
| `inventory.product_group` | ✅ Ready | `group_name` maps to spreadsheet groups |
| `inventory.product_group_items` | ✅ Ready | Links products to groups |
| `sales.customer` | ⚠️ No channel field | Has `store_credit` but no channel dimension |
| `sales.sr_order` | ✅ Ready | `commission_amount`, `commission_disbursed` |
| `sales.sr_order_detail` | ✅ Ready | `negotiated_price`, `shipped_quantity`, `returned_quantity` |
| `sales.sales_order` | ✅ Ready | `order_source`, `status`, `total_amount` |
| Channel mapping | ❌ Missing | New tables needed |

---

## 4. Gap Analysis

| Area | Existing | Required | Gap |
|------|----------|----------|-----|
| Primary dimension | SR-centric | Group-centric | New group-first aggregates |
| Channel split | Not present | Muslim Bakary / Traders / Auto | Configurable customer-channel mapping |
| Commission by group | Not present | Per-group commission | Aggregate from SR orders by product group |
| Market credit | Not present | Per-group market credit | Define source (store_credit? payment adjustments?) |
| Sales projection | Not present | Avg/day × full month | New metric with configurable day counts |
| DO cash | Not present | Per-group DO cash | Aggregate from payment collections |
| Undelivery split | Partial | Total / Web / Sample | New consolidated workflow metric |
| Growth matrix | Not present | Dynamic period comparison | New comparison endpoint + UI |
| Channel admin UI | Not present | Full CRUD | New admin page for channel management |

---

## 5. Target Architecture

### 5.1 Backend Components

```
app/
├── models/
│   └── sr_program.py                    # NEW: Channel mapping models
├── schemas/
│   └── sr_program_reports.py            # NEW: Request/response schemas
├── repositories/reports/
│   └── sr_program_reports.py            # NEW: SQL queries for all 7 blocks
├── services/
│   └── reports.py                       # ADD: get_sr_program_workflow() method
├── api/
│   ├── reports.py                       # ADD: SR Program endpoints
│   └── sr_program_admin.py              # NEW: Channel mapping CRUD endpoints
└── alembic/versions/
    └── {timestamp}_add_sr_program_channel_tables.py  # NEW: Migration
```

### 5.2 Frontend Components

```
shoudagor_FE/src/
├── pages/reports/
│   ├── SRProgramWorkflow.tsx            # NEW: Main workflow page
│   └── SRProgramChannelAdmin.tsx        # NEW: Channel mapping admin
├── components/sections/
│   ├── SRProgramReconciliation.tsx      # NEW: Block A
│   ├── SRProgramFinancials.tsx          # NEW: Block B
│   ├── SRProgramChannelSplit.tsx        # NEW: Block C
│   ├── SRProgramProjection.tsx          # NEW: Block D
│   ├── SRProgramDOCash.tsx              # NEW: Block E
│   ├── SRProgramUndelivery.tsx          # NEW: Block F
│   └── SRProgramGrowth.tsx              # NEW: Block G
├── lib/api/
│   └── srProgramReportsApi.ts           # NEW: API client
├── App.tsx                              # EDIT: Add routes
└── data/navigation.ts                   # EDIT: Add nav items
```

---

## 6. Database Schema Design

### 6.1 New Tables

#### A) Channel Master Table

```sql
CREATE TABLE reports.sr_program_channel (
    channel_id          SERIAL PRIMARY KEY,
    channel_name        VARCHAR(100) NOT NULL,
    display_order       INTEGER NOT NULL DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    company_id          INTEGER NOT NULL,
    cb                  INTEGER,
    cd                  TIMESTAMP DEFAULT NOW(),
    mb                  INTEGER,
    md                  TIMESTAMP DEFAULT NOW(),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT uq_channel_company_name UNIQUE (company_id, channel_name, is_deleted),
    CONSTRAINT fk_channel_company FOREIGN KEY (company_id)
        REFERENCES security.app_client_company(company_id)
);

CREATE INDEX idx_sr_program_channel_company ON reports.sr_program_channel(company_id);
CREATE INDEX idx_sr_program_channel_active ON reports.sr_program_channel(company_id, is_active);
```

#### B) Customer-Channel Mapping Table

```sql
CREATE TABLE reports.sr_program_customer_channel (
    mapping_id          SERIAL PRIMARY KEY,
    customer_id         INTEGER NOT NULL,
    channel_id          INTEGER NOT NULL,
    company_id          INTEGER NOT NULL,
    cb                  INTEGER,
    cd                  TIMESTAMP DEFAULT NOW(),
    mb                  INTEGER,
    mb                  INTEGER,
    md                  TIMESTAMP DEFAULT NOW(),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT uq_customer_channel UNIQUE (company_id, customer_id, is_deleted),
    CONSTRAINT fk_mapping_customer FOREIGN KEY (customer_id)
        REFERENCES sales.customer(customer_id),
    CONSTRAINT fk_mapping_channel FOREIGN KEY (channel_id)
        REFERENCES reports.sr_program_channel(channel_id)
);

CREATE INDEX idx_sr_program_customer_channel_company ON reports.sr_program_customer_channel(company_id);
CREATE INDEX idx_sr_program_customer_channel_customer ON reports.sr_program_customer_channel(customer_id);
CREATE INDEX idx_sr_program_customer_channel_channel ON reports.sr_program_customer_channel(channel_id);
```

### 6.2 Seed Data

Default channels for initial setup:

```sql
INSERT INTO reports.sr_program_channel (channel_name, display_order, company_id) VALUES
    ('Muslim Bakary', 1, 1),
    ('Traders', 2, 1),
    ('Auto', 3, 1);
```

---

## 7. Backend Implementation Details

### 7.1 Models (`app/models/sr_program.py`)

```python
class SRProgramChannel(Base, TimestampMixin, IsDeletedMixin, CompanyMixin):
    """Channel master for SR Program workflow."""
    __tablename__ = "sr_program_channel"
    __table_args__ = (
        UniqueConstraint("company_id", "channel_name", "is_deleted",
                        name="uq_channel_company_name"),
        Index("idx_sr_program_channel_company", "company_id"),
        {"schema": "reports"},
    )

    channel_id = Column(Integer, primary_key=True)
    channel_name = Column(String(100), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

class SRProgramCustomerChannel(Base, TimestampMixin, IsDeletedMixin, CompanyMixin):
    """Maps customers to channels for SR Program workflow."""
    __tablename__ = "sr_program_customer_channel"
    __table_args__ = (
        UniqueConstraint("company_id", "customer_id", "is_deleted",
                        name="uq_customer_channel"),
        Index("idx_sr_program_cc_company", "company_id"),
        Index("idx_sr_program_cc_customer", "customer_id"),
        Index("idx_sr_program_cc_channel", "channel_id"),
        {"schema": "reports"},
    )

    mapping_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("sales.customer.customer_id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("reports.sr_program_channel.channel_id"), nullable=False)
```

### 7.2 Schemas (`app/schemas/sr_program_reports.py`)

```python
# Request schemas
class SRProgramWorkflowRequest(BaseModel):
    start_date: date
    end_date: date
    compare_start_date: Optional[date] = None
    compare_end_date: Optional[date] = None
    group_ids: Optional[List[int]] = None
    channel_ids: Optional[List[int]] = None
    projection_days: int = 24
    elapsed_days: int = 23

# Response schemas - per block
class GroupFinancialRow(BaseModel):
    group_name: str
    commission: float
    market_credit: float
    total: float

class ChannelSplitRow(BaseModel):
    group_name: str
    channels: Dict[str, float]  # channel_name -> value
    row_total: float

class SalesProjectionRow(BaseModel):
    group_name: str
    sales_report: float
    avg_per_day: float
    projection: float

class DOCashRow(BaseModel):
    group_name: str
    do_cash: float

class UndeliveryRow(BaseModel):
    group_name: str
    total_undelivery: float
    web_undelivery: float
    sample_product: float

class GrowthRow(BaseModel):
    group_name: str
    base_period: float
    compare_period: float
    growth_volume: float
    growth_percent: Optional[float] = None

class SRProgramWorkflowResponse(BaseModel):
    meta: Dict[str, Any]
    group_financials: List[GroupFinancialRow]
    channel_split: List[ChannelSplitRow]
    sales_projection: List[SalesProjectionRow]
    do_cash: List[DOCashRow]
    undelivery: List[UndeliveryRow]
    growth: List[GrowthRow]
    totals: Dict[str, Any]
```

### 7.3 Repository (`app/repositories/reports/sr_program_reports.py`)

**Key queries (all use `sqlalchemy.text()` with CTEs):**

#### Query 1: Base Facts CTE

```sql
WITH base_facts AS (
    SELECT
        pg.group_name,
        c.customer_id,
        c.customer_name,
        COALESCE(cc.channel_name, 'Unmapped') AS channel_name,
        so.order_date,
        so.status,
        so.total_amount,
        so.order_source,
        sod.quantity,
        sod.shipped_quantity,
        sod.returned_quantity,
        sod.negotiated_price,
        sod.product_id,
        sod.variant_id
    FROM sales.sales_order so
    JOIN sales.sales_order_detail sod ON so.sales_order_id = sod.sales_order_id
    JOIN sales.customer c ON so.customer_id = c.customer_id
    LEFT JOIN inventory.product_group_items pgi ON sod.product_id = pgi.product_id
    LEFT JOIN inventory.product_group pg ON pgi.product_group_id = pg.product_group_id
    LEFT JOIN reports.sr_program_customer_channel scc ON c.customer_id = scc.customer_id
    LEFT JOIN reports.sr_program_channel cc ON scc.channel_id = cc.channel_id
    WHERE so.company_id = :company_id
      AND so.order_date BETWEEN :start_date AND :end_date
      AND so.is_deleted = FALSE
      AND sod.is_deleted = FALSE
      AND (so.order_source IN ('direct', 'sr_consolidated') OR so.order_source = 'sr_order')
)
```

#### Query 2: Group Financials (Block B)

```sql
SELECT
    COALESCE(group_name, 'Ungrouped') AS group_name,
    SUM(commission) AS commission,
    SUM(market_credit) AS market_credit,
    SUM(commission + market_credit) AS total
FROM (
    SELECT
        COALESCE(bf.group_name, 'Ungrouped') AS group_name,
        COALESCE(sro.commission_amount, 0) AS commission,
        COALESCE(c.store_credit, 0) AS market_credit
    FROM base_facts bf
    JOIN sales.sr_order sro ON bf.order_source LIKE '%sr%'
    JOIN sales.customer c ON bf.customer_id = c.customer_id
) sub
GROUP BY group_name
ORDER BY group_name
```

#### Query 3: Channel Split (Block C)

```sql
SELECT
    COALESCE(group_name, 'Ungrouped') AS group_name,
    channel_name,
    SUM(total_amount) AS channel_value
FROM base_facts
GROUP BY group_name, channel_name
PIVOT BY channel_name
ORDER BY group_name
```

#### Query 4: Sales Projection (Block D)

```sql
SELECT
    COALESCE(group_name, 'Ungrouped') AS group_name,
    SUM(total_amount) AS sales_report,
    SUM(total_amount) / :elapsed_days AS avg_per_day,
    (SUM(total_amount) / :elapsed_days) * :projection_days AS projection
FROM base_facts
GROUP BY group_name
ORDER BY group_name
```

#### Query 5: DO Cash (Block E)

```sql
SELECT
    COALESCE(pg.group_name, 'Ungrouped') AS group_name,
    SUM(sopd.amount) AS do_cash
FROM sales.sales_order so
JOIN sales.sales_order_payment_detail sopd ON so.sales_order_id = sopd.sales_order_id
JOIN sales.customer c ON so.customer_id = c.customer_id
LEFT JOIN inventory.product_group_items pgi ON ...
LEFT JOIN inventory.product_group pg ON pgi.product_group_id = pg.product_group_id
WHERE so.company_id = :company_id
  AND so.order_date BETWEEN :start_date AND :end_date
  AND so.status IN ('delivered', 'completed')
GROUP BY pg.group_name
```

#### Query 6: Undelivery (Block F)

```sql
SELECT
    COALESCE(pg.group_name, 'Ungrouped') AS group_name,
    SUM(sod.quantity - COALESCE(sod.shipped_quantity, 0)) AS total_undelivery,
    SUM(CASE WHEN so.order_source = 'direct'
        THEN (sod.quantity - COALESCE(sod.shipped_quantity, 0)) ELSE 0 END) AS web_undelivery,
    SUM(CASE WHEN sod.quantity > 0 AND sod.shipped_quantity = 0
        THEN sod.quantity ELSE 0 END) AS sample_product
FROM sales.sales_order so
JOIN sales.sales_order_detail sod ON so.sales_order_id = sod.sales_order_id
...
WHERE so.status NOT IN ('delivered', 'completed', 'cancelled')
GROUP BY pg.group_name
```

#### Query 7: Growth Comparison (Block G)

```sql
-- Base period
SELECT COALESCE(pg.group_name, 'Ungrouped') AS group_name,
       SUM(so.total_amount) AS base_value
FROM sales.sales_order so
...
WHERE so.order_date BETWEEN :compare_start AND :compare_end

-- Compare period
SELECT COALESCE(pg.group_name, 'Ungrouped') AS group_name,
       SUM(so.total_amount) AS compare_value
FROM sales.sales_order so
...
WHERE so.order_date BETWEEN :start_date AND :end_date

-- Growth calculation (in service layer)
growth_volume = compare_value - base_value
growth_percent = (compare_value - base_value) / base_value * 100
```

### 7.4 Service Layer (`app/services/reports.py`)

Add method to existing `ReportsService` class:

```python
async def get_sr_program_workflow(
    self,
    company_id: int,
    start_date: date,
    end_date: date,
    compare_start_date: Optional[date] = None,
    compare_end_date: Optional[date] = None,
    group_ids: Optional[List[int]] = None,
    channel_ids: Optional[List[int]] = None,
    projection_days: int = 24,
    elapsed_days: int = 23,
) -> SRProgramWorkflowResponse:
    """Execute all 7 workflow block queries and assemble response."""

    # 1. Execute base facts query
    base_facts = await self.sr_program_repo.get_base_facts(...)

    # 2. Execute each block query
    group_financials = await self.sr_program_repo.get_group_financials(...)
    channel_split = await self.sr_program_repo.get_channel_split(...)
    sales_projection = await self.sr_program_repo.get_sales_projection(...)
    do_cash = await self.sr_program_repo.get_do_cash(...)
    undelivery = await self.sr_program_repo.get_undelivery(...)
    growth = await self.sr_program_repo.get_growth_comparison(...)

    # 3. Calculate totals
    totals = self._calculate_totals(...)

    # 4. Assemble response
    return SRProgramWorkflowResponse(
        meta={...},
        group_financials=group_financials,
        channel_split=channel_split,
        sales_projection=sales_projection,
        do_cash=do_cash,
        undelivery=undelivery,
        growth=growth,
        totals=totals,
    )
```

### 7.5 API Endpoints (`app/api/reports.py`)

Add to existing reports router:

```python
@router.get("/sr-program/workflow")
async def get_sr_program_workflow(
    start_date: date = Query(...),
    end_date: date = Query(...),
    compare_start_date: Optional[date] = None,
    compare_end_date: Optional[date] = None,
    group_ids: Optional[str] = None,
    channel_ids: Optional[str] = None,
    projection_days: int = Query(24, ge=1, le=31),
    elapsed_days: int = Query(23, ge=1, le=31),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get SR Program Workflow data for all 7 blocks."""
    try:
        service = ReportsService(db)
        result = await service.get_sr_program_workflow(...)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 7.6 Channel Mapping Admin API (`app/api/sr_program_admin.py`)

New router for channel management:

```python
router = APIRouter(prefix="/api/company/sr-program/channels", tags=["SR Program Channels"])

@router.get("/")
async def list_channels(company_id, db, current_user):
    """List all channels for company."""

@router.post("/")
async def create_channel(data, company_id, db, current_user):
    """Create new channel."""

@router.put("/{channel_id}")
async def update_channel(channel_id, data, company_id, db, current_user):
    """Update channel."""

@router.delete("/{channel_id}")
async def delete_channel(channel_id, company_id, db, current_user):
    """Soft delete channel."""

@router.get("/mappings")
async def list_mappings(company_id, db, current_user):
    """List all customer-channel mappings."""

@router.post("/mappings")
async def create_mapping(data, company_id, db, current_user):
    """Create customer-channel mapping."""

@router.put("/mappings/{mapping_id}")
async def update_mapping(mapping_id, data, company_id, db, current_user):
    """Update mapping."""

@router.delete("/mappings/{mapping_id}")
async def delete_mapping(mapping_id, company_id, db, current_user):
    """Delete mapping."""

@router.post("/mappings/bulk")
async def bulk_update_mappings(data, company_id, db, current_user):
    """Bulk upsert mappings (replace all for company)."""
```

### 7.7 Migration File

```python
"""add sr program channel tables

Revision ID: {auto_generated}
Revises: {previous}
Create Date: 2026-04-01
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS reports")

    # Create channel master table
    op.create_table(
        'sr_program_channel',
        sa.Column('channel_id', sa.Integer(), primary_key=True),
        sa.Column('channel_name', sa.String(100), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('cb', sa.Integer()),
        sa.Column('cd', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('mb', sa.Integer()),
        sa.Column('md', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.UniqueConstraint('company_id', 'channel_name', 'is_deleted',
                           name='uq_channel_company_name'),
        schema='reports'
    )

    # Create customer-channel mapping table
    op.create_table(
        'sr_program_customer_channel',
        sa.Column('mapping_id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('cb', sa.Integer()),
        sa.Column('cd', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('mb', sa.Integer()),
        sa.Column('md', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.UniqueConstraint('company_id', 'customer_id', 'is_deleted',
                           name='uq_customer_channel'),
        sa.ForeignKeyConstraint(['customer_id'], ['sales.customer.customer_id']),
        sa.ForeignKeyConstraint(['channel_id'], ['reports.sr_program_channel.channel_id']),
        schema='reports'
    )

    # Create indexes
    op.create_index('idx_sr_program_channel_company', 'sr_program_channel',
                   ['company_id'], schema='reports')
    op.create_index('idx_sr_program_cc_company', 'sr_program_customer_channel',
                   ['company_id'], schema='reports')
    op.create_index('idx_sr_program_cc_customer', 'sr_program_customer_channel',
                   ['customer_id'], schema='reports')
    op.create_index('idx_sr_program_cc_channel', 'sr_program_customer_channel',
                   ['channel_id'], schema='reports')

def downgrade():
    op.drop_table('sr_program_customer_channel', schema='reports')
    op.drop_table('sr_program_channel', schema='reports')
```

### 7.8 Bug Fix: Order Source Inconsistency

**Files to modify:**
- `Shoudagor/app/repositories/reports/sales_reports.py` lines ~504 and ~728

**Change:**
```python
# Before
AND so.order_source = 'sr_order'

# After
AND so.order_source IN ('sr_order', 'sr_consolidated')
```

---

## 8. Frontend Implementation Details

### 8.1 API Client (`shoudagor_FE/src/lib/api/srProgramReportsApi.ts`)

```typescript
import { api } from '../api';
import { apiRequest } from '../queryClient';

// Types
export interface SRProgramWorkflowParams {
    start_date: string;
    end_date: string;
    compare_start_date?: string;
    compare_end_date?: string;
    group_ids?: string;
    channel_ids?: string;
    projection_days?: number;
    elapsed_days?: number;
}

export interface GroupFinancialRow {
    group_name: string;
    commission: number;
    market_credit: number;
    total: number;
}

export interface ChannelSplitRow {
    group_name: string;
    channels: Record<string, number>;
    row_total: number;
}

export interface SalesProjectionRow {
    group_name: string;
    sales_report: number;
    avg_per_day: number;
    projection: number;
}

export interface DOCashRow {
    group_name: string;
    do_cash: number;
}

export interface UndeliveryRow {
    group_name: string;
    total_undelivery: number;
    web_undelivery: number;
    sample_product: number;
}

export interface GrowthRow {
    group_name: string;
    base_period: number;
    compare_period: number;
    growth_volume: number;
    growth_percent: number | null;
}

export interface SRProgramWorkflowResponse {
    meta: Record<string, any>;
    group_financials: GroupFinancialRow[];
    channel_split: ChannelSplitRow[];
    sales_projection: SalesProjectionRow[];
    do_cash: DOCashRow[];
    undelivery: UndeliveryRow[];
    growth: GrowthRow[];
    totals: Record<string, any>;
}

export interface Channel {
    channel_id: number;
    channel_name: string;
    display_order: number;
    is_active: boolean;
}

export interface CustomerChannelMapping {
    mapping_id: number;
    customer_id: number;
    customer_name: string;
    channel_id: number;
    channel_name: string;
}

// API Functions
export const getSRProgramWorkflow = (params: SRProgramWorkflowParams): Promise<SRProgramWorkflowResponse> => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            searchParams.append(key, String(value));
        }
    });
    return apiRequest(api, `/reports/sr-program/workflow?${searchParams.toString()}`);
};

export const getChannels = (): Promise<Channel[]> =>
    apiRequest(api, '/sr-program/channels/');

export const createChannel = (data: Partial<Channel>): Promise<Channel> =>
    apiRequest(api, '/sr-program/channels/', { method: 'POST', body: data });

export const updateChannel = (id: number, data: Partial<Channel>): Promise<Channel> =>
    apiRequest(api, `/sr-program/channels/${id}`, { method: 'PUT', body: data });

export const deleteChannel = (id: number): Promise<void> =>
    apiRequest(api, `/sr-program/channels/${id}`, { method: 'DELETE' });

export const getChannelMappings = (): Promise<CustomerChannelMapping[]> =>
    apiRequest(api, '/sr-program/channels/mappings');

export const bulkUpdateMappings = (mappings: Partial<CustomerChannelMapping>[]): Promise<void> =>
    apiRequest(api, '/sr-program/channels/mappings/bulk', { method: 'POST', body: { mappings } });
```

### 8.2 Main Page (`shoudagor_FE/src/pages/reports/SRProgramWorkflow.tsx`)

```tsx
// Structure:
// 1. Header with title + filter controls
// 2. Date range picker (primary + compare)
// 3. Filter bar (group, channel)
// 4. Section A: Reconciliation (optional - may skip if not needed)
// 5. Section B: Group Financial Summary
// 6. Section C: Channel Split Matrix
// 7. Section D: Sales Projection
// 8. Section E: DO Cash
// 9. Section F: Undelivery
// 10. Section G: Growth Comparison

// Key patterns:
// - useQuery for data fetching
// - Skeleton loading states
// - Error handling with Alert
// - Empty states with message
// - BDT currency formatting
// - Frozen table headers with horizontal scroll
// - Export to CSV functionality
```

### 8.3 Section Components

Each section component follows this pattern:

```tsx
// Example: SRProgramFinancials.tsx (Block B)
interface SRProgramFinancialsProps {
    data: GroupFinancialRow[];
    loading: boolean;
}

export function SRProgramFinancials({ data, loading }: SRProgramFinancialsProps) {
    if (loading) return <SkeletonTable rows={7} cols={4} />;
    if (!data.length) return <EmptyState message="No financial data for this period" />;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Group Financial Summary</CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Group</TableHead>
                            <TableHead className="text-right">Commission</TableHead>
                            <TableHead className="text-right">Market Credit</TableHead>
                            <TableHead className="text-right">Total</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((row) => (
                            <TableRow key={row.group_name}>
                                <TableCell>{row.group_name}</TableCell>
                                <TableCell className="text-right">
                                    {formatBDT(row.commission)}
                                </TableCell>
                                <TableCell className="text-right">
                                    {formatBDT(row.market_credit)}
                                </TableCell>
                                <TableCell className="text-right font-semibold">
                                    {formatBDT(row.total)}
                                </TableCell>
                            </TableRow>
                        ))}
                        <TableRow className="font-bold bg-muted/50">
                            <TableCell>Total</TableCell>
                            <TableCell className="text-right">{formatBDT(totals.commission)}</TableCell>
                            <TableCell className="text-right">{formatBDT(totals.market_credit)}</TableCell>
                            <TableCell className="text-right">{formatBDT(totals.total)}</TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
```

### 8.4 Channel Split Matrix (Block C)

Special rendering for the pivot table:

```tsx
// Dynamic columns based on channels
const channelNames = [...new Set(data.flatMap(row => Object.keys(row.channels)))];

<Table>
    <TableHeader>
        <TableRow>
            <TableHead>Group</TableHead>
            {channelNames.map(ch => (
                <TableHead key={ch} className="text-right">{ch}</TableHead>
            ))}
            <TableHead className="text-right">Total</TableHead>
        </TableRow>
    </TableHeader>
    <TableBody>
        {data.map(row => (
            <TableRow key={row.group_name}>
                <TableCell>{row.group_name}</TableCell>
                {channelNames.map(ch => (
                    <TableCell key={ch} className="text-right">
                        {formatBDT(row.channels[ch] || 0)}
                    </TableCell>
                ))}
                <TableCell className="text-right font-semibold">
                    {formatBDT(row.row_total)}
                </TableCell>
            </TableRow>
        ))}
    </TableBody>
</Table>
```

### 8.5 Growth Comparison Table (Block G)

```tsx
<Table>
    <TableHeader>
        <TableRow>
            <TableHead>Group</TableHead>
            <TableHead className="text-right">Base Period</TableHead>
            <TableHead className="text-right">Compare Period</TableHead>
            <TableHead className="text-right">Growth Volume</TableHead>
            <TableHead className="text-right">Growth %</TableHead>
        </TableRow>
    </TableHeader>
    <TableBody>
        {data.map(row => (
            <TableRow key={row.group_name}>
                <TableCell>{row.group_name}</TableCell>
                <TableCell className="text-right">{formatBDT(row.base_period)}</TableCell>
                <TableCell className="text-right">{formatBDT(row.compare_period)}</TableCell>
                <TableCell className={`text-right ${row.growth_volume >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatBDT(row.growth_volume)}
                </TableCell>
                <TableCell className={`text-right ${row.growth_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {row.growth_percent?.toFixed(1)}%
                </TableCell>
            </TableRow>
        ))}
    </TableBody>
</Table>
```

### 8.6 Channel Admin Page (`shoudagor_FE/src/pages/reports/SRProgramChannelAdmin.tsx`)

```tsx
// Features:
// 1. Channel list with CRUD operations
// 2. Customer-channel mapping table
// 3. Bulk assignment UI (select customers, assign to channel)
// 4. Unmapped customers list
// 5. Channel reorder (drag & drop or display_order input)

// Layout:
// - Tabs: Channels | Customer Mappings | Unmapped Customers
// - Channel tab: Table with add/edit/delete
// - Mappings tab: Table with customer search, channel dropdown
// - Unmapped tab: List of customers without channel assignment
```

### 8.7 Route Configuration

**`shoudagor_FE/src/App.tsx`:**

```tsx
// Add inside AdminRoute children:
{ path: "/reports/sr-program", element: <SRProgramWorkflow /> },
{ path: "/reports/sr-program/admin", element: <SRProgramChannelAdmin /> },
```

### 8.8 Navigation Configuration

**`shoudagor_FE/src/data/navigation.ts`:**

```tsx
// Add to Reports section:
{
    title: "SR Program Workflow",
    url: "/reports/sr-program",
    icon: BarChart3,  // or appropriate icon
},
{
    title: "Channel Admin",
    url: "/reports/sr-program/admin",
    icon: Settings,
},
```

---

## 9. Metric Definitions

### 9.1 Commission (Block B)

**Definition:** Total commission amount attributed to each product group.

**Source:** `sr_order.commission_amount` distributed by product group via order details.

**Formula:**
```sql
SUM(sro.commission_amount * (sod.quantity / total_order_quantity))
GROUP BY product_group
```

**Fallback:** If `commission_amount` is null, calculate as percentage of revenue.

### 9.2 Market Credit (Block B)

**Definition:** Credit adjustments or store credit applied to orders.

**Source:** `customer.store_credit` changes during the period, or payment adjustments.

**Clarification Needed:** Confirm exact source — is this:
- Option A: `customer.store_credit` balance at period end?
- Option B: Payment adjustments/discounts applied?
- Option C: Separate credit transactions?

**Assumption for implementation:** Option A (store_credit balance), adjustable after clarification.

### 9.3 Channel Split (Block C)

**Definition:** Sales value distributed by customer channel.

**Source:** Sales orders joined with customer-channel mapping.

**Formula:**
```sql
SUM(so.total_amount)
GROUP BY product_group, channel_name
```

**Unmapped customers:** Route to 'Unmapped' bucket until assigned.

### 9.4 Sales Projection (Block D)

**Definition:** Current period sales, daily average, and full month projection.

**Formulas:**
- `Sales Report` = SUM(total_amount) for period
- `Avg/Day` = Sales Report / elapsed_days (default: 23)
- `Projection` = Avg/Day × projection_days (default: 24)

**Configurable:** Both day counts are query parameters.

### 9.5 DO Cash (Block E)

**Definition:** Cash collected from delivered orders, by product group.

**Source:** `sales_order_payment_detail` for orders with status = 'delivered' or 'completed'.

**Formula:**
```sql
SUM(sopd.amount)
WHERE so.status IN ('delivered', 'completed')
GROUP BY product_group
```

### 9.6 Undelivery (Block F)

**Definition:** Unfulfilled order value/quantity breakdown.

**Formulas:**
- `Total Undelivery` = SUM(quantity - shipped_quantity) for non-delivered orders
- `Web Undelivery` = SUM for orders with order_source = 'direct'
- `Sample Product` = Total Undelivery - Web Undelivery

**Status filter:** Orders NOT IN ('delivered', 'completed', 'cancelled')

### 9.7 Growth Comparison (Block G)

**Definition:** Year-over-year or period-over-period comparison.

**Formulas:**
- `Growth Volume` = compare_period_value - base_period_value
- `Growth %` = (compare_period_value - base_period_value) / base_period_value × 100

**Edge case:** If base_period_value = 0, growth_percent = null (avoid division by zero).

---

## 10. Testing Plan

### 10.1 Backend Unit Tests

| Test | Description |
|------|-------------|
| `test_group_financials_calculation` | Verify commission + market credit sums per group |
| `test_channel_split_pivot` | Verify channel values pivot correctly |
| `test_sales_projection_formula` | Verify avg/day and projection calculations |
| `test_do_cash_filtering` | Verify only delivered orders counted |
| `test_undelivery_breakdown` | Verify total = web + sample |
| `test_growth_division_by_zero` | Verify null growth% when base = 0 |
| `test_unmapped_customers` | Verify unmapped customers route to 'Unmapped' bucket |
| `test_ungrouped_products` | Verify products without group route to 'Ungrouped' |
| `test_company_isolation` | Verify data filtered by company_id |
| `test_date_range_filtering` | Verify start/end date filters work correctly |

### 10.2 Integration Tests

| Test | Description |
|------|-------------|
| `test_full_workflow_endpoint` | End-to-end GET /reports/sr-program/workflow |
| `test_channel_mapping_crud` | Create, read, update, delete channel mappings |
| `test_bulk_mapping_update` | Bulk upsert mappings |
| `test_compare_period_optional` | Workflow without compare period |
| `test_custom_day_counts` | Custom elapsed_days and projection_days |

### 10.3 Frontend Tests

| Test | Description |
|------|-------------|
| `test_page_render_all_sections` | All 7 sections render with data |
| `test_loading_state` | Skeleton loaders shown during fetch |
| `test_empty_state` | Empty message when no data |
| `test_error_state` | Error alert on API failure |
| `test_filter_interaction` | Date range and filter changes trigger refetch |
| `test_currency_formatting` | BDT format with correct decimals |
| `test_growth_color_coding` | Positive = green, negative = red |
| `test_channel_admin_crud` | Channel CRUD operations work |
| `test_mapping_assignment` | Customer-channel assignment works |

### 10.4 Regression Tests

| Test | Description |
|------|-------------|
| `test_existing_sr_report_unchanged` | /reports/sr still works as before |
| `test_existing_dsr_report_unchanged` | /reports/dsr unaffected |
| `test_sales_reports_fixed` | Pipeline reports now return SR data |

---

## 11. Performance Considerations

### 11.1 Query Optimization

- **Shared base CTE:** All blocks use the same base facts CTE to avoid repeated scans
- **Indexes:** Created on mapping tables and common filter columns
- **Date range filtering:** Applied early in CTE to reduce dataset
- **Company isolation:** Filtered at base level for all queries

### 11.2 Caching Strategy

- **Channel mappings:** Cache in-memory or Redis (static data, infrequent changes)
- **Product groups:** Cache (rarely changes)
- **Workflow data:** No caching (date-range dependent, real-time expected)

### 11.3 Expected Performance

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Workflow query (1 month) | < 500ms | With proper indexes |
| Channel mapping CRUD | < 100ms | Simple queries |
| Bulk mapping update | < 200ms | Batch upsert |

---

## 12. Rollout Plan

### Stage 1: Internal QA
- Run parity tests with known period data
- Validate against spreadsheet outputs
- Fix any formula mismatches

### Stage 2: Feature Flag
- Gate new page via permission toggle
- Enable for reporting/admin users only

### Stage 3: Controlled Launch
- Monitor response times
- Track mismatch incidents
- Gather user feedback

### Stage 4: Full Availability
- Update user documentation
- Create quick walkthrough guide
- Enable for all authorized users

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Formula mismatch | High | Lock metric spec before implementation, golden parity tests |
| Ambiguous market credit definition | Medium | Clarify with stakeholders before coding |
| Channel mapping complexity | Medium | Start with seed data, build admin UI iteratively |
| Performance with large datasets | Medium | Shared CTEs, indexes, pagination if needed |
| Unmapped products/customers | Low | Explicit 'Ungrouped'/'Unmapped' buckets |
| Order source bug side effects | Low | Regression tests on existing reports |

---

## 14. Acceptance Criteria

- [ ] New `/reports/sr-program` page renders all 7 workflow blocks
- [ ] All blocks show correct totals and formatting
- [ ] Date range filter works for primary period
- [ ] Compare period filter works for growth section
- [ ] Channel mapping endpoints functional and company-scoped
- [ ] Channel admin UI allows full CRUD operations
- [ ] Formula parity validated against spreadsheet outputs
- [ ] Existing `/reports/sr` profitability report unchanged
- [ ] Order source bug fixed (pipeline reports return SR data)
- [ ] All tests pass (unit, integration, frontend, regression)
- [ ] Performance meets targets (<500ms for workflow query)

---

## 15. File Change Summary

### New Files (11)

| File | Type | Lines (est.) | Purpose |
|------|------|-------------|---------|
| `Shoudagor/app/models/sr_program.py` | Backend Model | 60 | Channel mapping models |
| `Shoudagor/app/schemas/sr_program_reports.py` | Backend Schema | 120 | Request/response schemas |
| `Shoudagor/app/repositories/reports/sr_program_reports.py` | Backend Repo | 400 | SQL queries for 7 blocks |
| `Shoudagor/app/api/sr_program_admin.py` | Backend API | 200 | Channel mapping CRUD |
| `Shoudagor/alembic/versions/{ts}_add_sr_program_channel_tables.py` | Migration | 80 | Database schema |
| `shoudagor_FE/src/pages/reports/SRProgramWorkflow.tsx` | Frontend Page | 350 | Main workflow page |
| `shoudagor_FE/src/pages/reports/SRProgramChannelAdmin.tsx` | Frontend Page | 400 | Channel admin UI |
| `shoudagor_FE/src/lib/api/srProgramReportsApi.ts` | Frontend API | 150 | API client |
| `shoudagor_FE/src/components/sections/SRProgramFinancials.tsx` | Component | 100 | Block B |
| `shoudagor_FE/src/components/sections/SRProgramChannelSplit.tsx` | Component | 120 | Block C |
| `shoudagor_FE/src/components/sections/SRProgramGrowth.tsx` | Component | 100 | Block G |

### Modified Files (6)

| File | Changes | Purpose |
|------|---------|---------|
| `Shoudagor/app/services/reports.py` | +80 lines | Add get_sr_program_workflow() |
| `Shoudagor/app/api/reports.py` | +30 lines | Add workflow endpoint |
| `Shoudagor/app/main.py` | +5 lines | Register new router |
| `Shoudagor/app/repositories/reports/sales_reports.py` | ~2 lines | Fix order_source bug |
| `shoudagor_FE/src/App.tsx` | +5 lines | Add routes |
| `shoudagor_FE/src/data/navigation.ts` | +10 lines | Add nav items |

**Total estimated changes: ~2,200 lines of new code, ~150 lines modified**

---

## 16. Implementation Order

### Phase 1: Foundation (Day 1)
1. Create migration for channel tables
2. Create models and schemas
3. Fix order_source bug

### Phase 2: Backend Core (Day 2-3)
1. Implement repository queries (7 blocks)
2. Implement service orchestrator
3. Add API endpoints
4. Write unit tests

### Phase 3: Frontend Core (Day 4-5)
1. Create API client
2. Build main page with filter bar
3. Build section components (B, C, D, E, F, G)
4. Add routes and navigation

### Phase 4: Admin UI (Day 6)
1. Build channel admin page
2. Implement CRUD operations
3. Add bulk mapping UI

### Phase 5: Testing & Polish (Day 7)
1. Integration tests
2. Frontend tests
3. Performance optimization
4. Regression testing
5. Documentation

---

## 17. Open Questions for Stakeholders

1. **Market Credit Definition:** What exact business logic does "Market Credit" represent?
   - Is it `customer.store_credit` balance?
   - Payment adjustments/discounts?
   - Separate credit transaction system?

2. **Channel Mapping Source:** How should initial customer-channel mappings be determined?
   - Manual assignment via admin UI?
   - Import from existing data?
   - Seed based on spreadsheet patterns?

3. **Day Count Configuration:** Should elapsed_days (23) and projection_days (24) be:
   - Fixed constants matching spreadsheet?
   - Auto-calculated from date range?
   - User-configurable parameters?

4. **Reconciliation Block (A):** Is Block A (SR Report vs Khata) needed in the system?
   - This appears to be a manual reconciliation check
   - May not have direct system data source
   - Recommend skipping unless explicitly required

5. **Growth Period Defaults:** What should the default comparison periods be?
   - Previous month?
   - Same month last year?
   - User-selectable?

---

## 18. Notes

- All code follows existing project conventions (5-layer architecture, raw SQL in repos, TanStack Query in frontend)
- Multi-tenancy enforced via `company_id` filtering at all levels
- Soft delete pattern used for all new tables
- BDT currency formatting throughout frontend
- Existing SR profitability report (`/reports/sr`) remains completely unchanged
- The order_source bug fix is included as it affects data accuracy for SR-originated sales

---

*This plan is implementation-ready. All architectural decisions are documented, file locations are specified, and code patterns match the existing codebase.*
