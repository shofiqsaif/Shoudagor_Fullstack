# Batch Inventory User Guide

## Overview

Batch Inventory is a feature that enables per-receipt cost tracking for your inventory. Instead of using a single average cost, the system tracks each purchase receipt as a separate "batch" with its own cost, allowing for accurate FIFO (First-In-First-Out), LIFO (Last-In-First-Out), or Weighted Average Cost valuation.

## Key Concepts

### Batches

A **batch** represents a group of inventory items received together in a single purchase. Each batch contains:
- **Quantity Received**: Total units received
- **Quantity on Hand**: Available units remaining
- **Unit Cost**: Cost per unit at time of receipt
- **Received Date**: Date the batch was received
- **Status**: active, depleted, expired, returned, quarantined

### Movement Ledger

Every inventory change is recorded in an immutable movement ledger:
- **IN**: Purchase receipt
- **OUT**: Sales delivery
- **RETURN_IN**: Sales return
- **ADJUSTMENT**: Inventory adjustment
- **TRANSFER_IN/TRANSFER_OUT**: Stock transfer

## Enabling Batch Tracking

1. Navigate to **Settings** → **Inventory**
2. Toggle "Enable Batch Tracking"
3. Select your **Valuation Mode**:
   - **FIFO**: Use oldest batches first (default)
   - **LIFO**: Use newest batches first
   - **WEIGHTED_AVG**: Use average cost across all batches

## Viewing Batches

### Batch Drill-Down

1. Go to **Inventory** → **Batch Drill-Down**
2. Filter by product, location, supplier, or status
3. Click on a batch to view:
   - Batch details
   - Movement history
   - Cost lock status

### Movement Ledger

1. Go to **Inventory** → **Movement Ledger**
2. View all inventory movements
3. Filter by:
   - Date range
   - Movement type
   - Product
   - Location

## Reports

### Stock by Batch

View current inventory levels grouped by batch.

### Inventory Aging

See how long inventory has been in stock, categorized by age:
- 0-30 days
- 31-60 days
- 61-90 days
- 90+ days

### COGS by Period

Cost of Goods Sold by month, calculated from actual batch costs.

### Margin Analysis

Analyze profit margins using actual batch costs vs. sales prices.

### Batch P&L

Profit and loss by batch, showing:
- Revenue
- Cost
- Profit
- Margin %

## Returns with Batch Tracking

When processing a sales return:
1. System looks up the original batch allocation
2. If batch still exists and is active, returns to that batch
3. If batch is depleted, creates a "synthetic" batch for the return

This maintains full traceability from return back to original purchase.

## Cost Immutability

Once a batch has been used in a sale (has OUT movements), the unit cost is locked and cannot be modified. This ensures COGS accuracy. To change the cost, you must create an accounting journal entry.

## Backfill (Admin Only)

If you're enabling batch tracking for the first time on existing data:

1. Run **dry-run** to preview changes:
   ```
   python scripts/backfill_batches.py --company_id=1 --dry-run
   ```

2. Review reconciliation report

3. Execute backfill:
   ```
   python scripts/backfill_batches.py --company_id=1 --execute
   ```

4. Run reconciliation to verify:
   ```
   python scripts/backfill_batches.py --company_id=1 --reconcile-only
   ```

## Troubleshooting

### Negative Quantity on Hand

This indicates a data integrity issue. Contact your administrator.

### Mismatch in Reconciliation

Run the reconciliation report to identify discrepancies between batch totals and inventory stock.

### Cost Locked Error

The batch has been used in sales and cannot have its cost modified.
