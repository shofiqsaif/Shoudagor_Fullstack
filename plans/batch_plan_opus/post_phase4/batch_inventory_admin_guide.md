# Batch Inventory Admin Guide

## System Architecture

### Database Tables

| Table | Schema | Description |
|-------|--------|-------------|
| `inventory.batch` | inventory | Stores batch records |
| `inventory.inventory_movement` | inventory | Immutable movement ledger |
| `settings.company_inventory_setting` | settings | Company configuration |
| `sales.sales_order_batch_allocation` | sales | Links sales to batches |

### Key Models

- **Batch**: Represents a receipt batch with cost tracking
- **InventoryMovement**: Immutable ledger entries
- **SalesOrderBatchAllocation**: Links sales to allocated batches
- **CompanyInventorySetting**: Per-company configuration

## Configuration

### Valuation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| FIFO | Oldest batches allocated first | Retail, perishables |
| LIFO | Newest batches allocated first | Commodities, fungible goods |
| WEIGHTED_AVG | Average cost across batches | General purpose |

### Feature Flags

- `batch_tracking_enabled`: Enables batch mode for a company
- When disabled, system uses legacy inventory_stock table

## Backfill Process

### Prerequisites

1. Ensure database migration is applied: `alembic upgrade head`
2. Verify no active transactions on the database
3. Schedule during off-peak hours for large datasets

### Running Backfill

```bash
# Dry run (preview)
python scripts/backfill_batches.py --company_id=1 --dry-run

# Execute
python scripts/backfill_batches.py --company_id=1 --execute

# With custom chunk size
python scripts/backfill_batches.py --company_id=1 --chunk-size=1000
```

### Reconciliation

```bash
# Reconcile after backfill
python scripts/backfill_batches.py --company_id=1 --reconcile-only

# Export to CSV
python scripts/backfill_batches.py --company_id=1 --reconcile --output=reconciliation.csv
```

## API Endpoints

### Batch Management
- `POST /api/company/inventory/batches` - Create batch
- `GET /api/company/inventory/batches` - List batches
- `GET /api/company/inventory/batches/{id}` - Get batch details
- `PATCH /api/company/inventory/batches/{id}` - Update batch

### Movement Ledger
- `GET /api/company/inventory/movements` - List movements

### Settings
- `GET /api/company/inventory/settings` - Get settings
- `POST /api/company/inventory/settings` - Update settings

### Reconciliation
- `GET /api/company/inventory/reconciliation` - Get reconciliation report
- `POST /api/company/inventory/reconciliation/backfill` - Run backfill

## Performance Considerations

### Indexes

The migration creates the following indexes:
- `idx_batch_company_product` - Company + product lookups
- `idx_batch_product_date` - Product + date ordering
- `idx_movement_batch` - Movement lookups by batch
- `idx_movement_company_date` - Company + date reporting

### Large Datasets

For companies with large transaction histories:
1. Run backfill in chunks (--chunk-size)
2. Schedule during off-peak hours
3. Use read replica for report queries

## Troubleshooting

### Concurrency Issues

If you see double allocation errors:
- Verify `SELECT FOR UPDATE SKIP LOCKED` is working
- Check transaction isolation level
- Review retry logic

### Reconciliation Mismatches

Common causes:
1. Manual inventory adjustments not recorded in batches
2. Data entry errors in legacy system
3. System crashes during transactions

### Cost Immutability Violations

If you cannot modify a batch cost:
- This is by design - cost is locked after OUT movements
- Use accounting journal entries instead

## Rollback Procedure

If you need to disable batch tracking:

1. Keep `batch_tracking_enabled = False`
2. Legacy inventory_stock continues to work
3. Existing batches and movements are preserved (read-only)

## Monitoring

### Log Locations

- Backend: Application logs
- Database: PostgreSQL logs

### Key Metrics to Monitor

- Batch allocation latency
- Reconciliation mismatch rate
- Movement ledger growth rate

## Security

### RBAC

Ensure users have appropriate roles:
- `inventory.batch.view` - View batches
- `inventory.batch.create` - Create batches
- `inventory.settings.manage` - Manage settings
