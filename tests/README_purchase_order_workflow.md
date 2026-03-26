# Purchase Order Workflow Automation

This folder contains Playwright scripts to automate the purchase order workflow in the Shoudagor application.

## Files

1. **`test_purchase_order_workflow.py`** – Original script (uses ShoudagorBrowser library).
2. **`test_purchase_order_workflow_v2.py`** – Updated script with improved selectors (standalone, does not rely on library).

## Workflow Overview

The scripts perform the following steps:

1. **Login** with admin credentials (`admin@complex.com` / `1234`).
2. **Create a new purchase order** for product variant `MCP002-V2 Large (MCP Product 2 Large)` at location `Bulk Storage`, supplier `Global Tech`.
   - Quantity: `100`, Unit Price: `50`, Order Number: `PO-2026-001`.
   - Expected delivery date set to tomorrow.
3. **Partial delivery** of `60` units (using the "Get Delivery" action).
4. **Partial payment** of `2500` (using the "Make Payment" action).
5. **Verify** that the purchase order status updates to `Partial` and that a batch is created in the Batch Drilldown page.

## Prerequisites

- Python 3.x
- Playwright for Python installed (`pip install playwright`)
- Chromium browser installed (`playwright install chromium`)
- The Shoudagor application running at `http://192.168.1.7:5173`

## How to Run

1. Navigate to the `tests/` directory.
2. Run the script directly:

   ```bash
   python test_purchase_order_workflow_v2.py
   ```

   The browser will open in headed mode (`headless=False`) so you can watch the automation.

3. If you prefer headless mode, edit the script and change `headless=False` to `headless=True`.

## Important Notes

- **Date Selection**: The script selects tomorrow's date in the calendar. If the date picker UI changes, the selector may need adjustment. Look for the comment “Expected Delivery Date selection” in the script.
- **Selectors**: The selectors are based on the UI observed on 2026‑03‑24. If the UI changes, you may need to update selectors (e.g., placeholders, button texts).
- **Timeouts**: Default timeouts are used; increase them if the application is slow.
- **Error Handling**: The script takes a screenshot on failure (`purchase_order_test_failure.png`).
- **Profile Popup**: A simple check for a phone‑number popup is included; adapt if the popup differs.

## Customization

Edit the configuration section at the top of the script to change:

- `BASE_URL`
- `EMAIL` / `PASSWORD`
- `LOCATION`, `SUPPLIER`, `PRODUCT`, `VARIANT`
- `ORDER_NUMBER`, `QUANTITY`, `UNIT_PRICE`
- `PARTIAL_DELIVERY_QTY`, `PARTIAL_PAYMENT_AMOUNT`

## Integration with Pytest

The scripts can be adapted into pytest tests. See `test_shoudagor.py` for an example of how to use the `ShoudagorBrowser` library in a pytest fixture.

---

*Last updated: 2026‑03‑24*