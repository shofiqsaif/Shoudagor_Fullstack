# Testing Guide — Newly Implemented Frontend Features

> **Date:** 2026-04-03  
> **Environment:** `http://192.168.1.7:5173`  
> **Login:** `admin@complex.com` / `1234` (2FA phone: `11111111111`)  
> **Backend:** Docker — run `docker-compose restart` after code changes

---

## Quick Navigation Map

| Feature | Route | Sidebar Path |
|---------|-------|-------------|
| Sales Ledger (Khata) | `/reports/ledger` | Reports → Ledger |
| Unconsolidated SR Orders (Bulk Approve) | `/sales-representatives/unconsolidated` | SR → Unconsolidated Orders |
| Damage Report (Edit) | `/reports/damage` | Reports → Damage |
| Cost & Profit Report (Edit) | `/reports/cost-profit` | Reports → Cost & Profit |
| DSR SO Assignments (Actions) | `/dsr/so-assignments` | DSR → SO Assignments |
| Invoices (Statistics) | `/invoices` | Sales → Invoices |
| Expenses (Statistics) | `/expenses` | Expenses |
| SR Price Management (Validation) | `/sales-representatives/price-management` | SR → Price Management |
| Product Image Gallery | *(component — not yet routed)* | N/A (see integration notes) |

---

## 1. Sales Ledger (Khata) Management

### How to Find
1. Log in as `admin@complex.com`
2. Navigate to **Reports → Ledger** in the sidebar
3. Or go directly to: `http://192.168.1.7:5173/reports/ledger`

### What to Test

#### A. Page Load
- [ ] Page renders without errors
- [ ] 3 KPI cards visible: Total Order Amount, Total Sales Amount, Total Payment Amount
- [ ] KPI cards show `৳ 0` initially (no data)
- [ ] Date range picker shows last 30 days by default
- [ ] Entry type dropdown shows: All Types, Order, Sales, Payment, Return
- [ ] "Add Entry" button visible in top-right

#### B. Create Ledger Entry
1. Click **"Add Entry"** button
2. Fill in the form:
   - **Date:** Pick any date
   - **Entry Type:** Select "Order"
   - **Group:** Select any product group (or leave as None)
   - **Customer:** Select any customer (or leave as None)
   - **Order Amount:** Enter `5000`
   - **Sales Amount:** Enter `4500`
   - **Payment Amount:** Enter `4000`
   - **Notes:** Enter "Test ledger entry"
3. Click **"Create"**
4. **Expected:** Success toast "Ledger entry created successfully", dialog closes, table updates

#### C. View in Table
- [ ] New entry appears in the table
- [ ] Date formatted as "dd MMM yyyy"
- [ ] Entry type shows as "order" (capitalized)
- [ ] Group and customer columns show selected values or "-"
- [ ] Amounts display with ৳ currency formatting
- [ ] Notes column shows "Test ledger entry"
- [ ] Actions column has dropdown menu (⋯)

#### D. Edit Ledger Entry
1. Click the **⋯** dropdown on the entry row
2. Click **"Edit"**
3. **Expected:** Dialog opens with all fields pre-filled
4. Change Order Amount to `6000`
5. Click **"Update"**
6. **Expected:** Success toast "Ledger entry updated successfully", table reflects new amount

#### E. Delete Ledger Entry
1. Click the **⋯** dropdown on the entry row
2. Click **"Delete"**
3. **Expected:** Confirmation dialog appears
4. Click **"Delete"**
5. **Expected:** Success toast "Ledger entry deleted", row removed from table

#### F. Filtering
- [ ] Change entry type filter to "Order" — only order entries show
- [ ] Change date range to last 7 days — entries outside range hidden
- [ ] KPI cards update to reflect filtered data

#### G. Pagination
- [ ] Create 25+ ledger entries
- [ ] Verify pagination controls appear at bottom
- [ ] Click page 2 — next 10 entries load
- [ ] Total count in header updates correctly

#### H. Tooltip
- [ ] Hover over the **ℹ️** icon next to "Sales Ledger (Khata)" title
- [ ] Tooltip appears explaining entry types and purpose

---

## 2. SR Order Bulk Approve

### How to Find
1. Navigate to **SR → Unconsolidated Orders** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/sales-representatives/unconsolidated`

### What to Test

#### A. Page Load
- [ ] Page renders with customer list table
- [ ] Checkbox column appears as first column
- [ ] "Select All" checkbox in header row
- [ ] No "Bulk Approve" button visible initially (no selections)

#### B. Select Individual Rows
1. Click checkbox on first customer row
2. **Expected:** "Bulk Approve Selected (N)" button appears in green with CheckCircle2 icon
3. N should equal the number of SR order IDs for that customer
4. Click checkbox on second customer row
5. **Expected:** Button updates to show combined count

#### C. Select All
1. Click the **"Select All"** checkbox in the header
2. **Expected:** All rows become selected
3. **Expected:** Button shows total count across all customers

#### D. Bulk Approve Action
1. Select 2-3 customer rows
2. Click **"Bulk Approve Selected (N)"**
3. **Expected:** Confirmation dialog appears showing:
   - "Are you sure you want to approve **N** SR order(s)?"
   - Description text about making orders available for consolidation
   - Cancel and Approve buttons
4. Click **"Approve N Order(s)"**
5. **Expected:**
   - Loading spinner on button during API call
   - Success toast: "N order(s) approved successfully"
   - If any fail: Warning toast with failure count
   - Checkboxes reset (all unchecked)
   - Table refreshes

#### E. Cancel Approval
1. Select rows → Click Bulk Approve → Click **Cancel**
2. **Expected:** Dialog closes, selections remain, no API call made

#### F. Empty Selection
1. Deselect all rows
2. **Expected:** "Bulk Approve" button disappears

---

## 3. Damage Report — Edit Functionality

### How to Find
1. Navigate to **Reports → Damage** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/reports/damage`

### What to Test

#### A. Existing Functionality (Regression)
- [ ] Page loads with date range picker, group filter, KPI cards
- [ ] "Record Damage" button works
- [ ] Create a damage record: Date, Quantity=5, Unit Cost=100, Reason="Broken", Notes="Test"
- [ ] Record appears in table

#### B. Edit Damage Record
1. In the Damage Records table, find the row you just created
2. Click the **✏️ (Pencil)** icon in the Actions column
3. **Expected:** Dialog opens with title "Edit Damage"
4. **Expected:** All fields pre-filled:
   - Date: the damage date
   - Quantity: 5
   - Unit Cost: 100
   - Reason: "Broken"
   - Notes: "Test"
5. Change Quantity to `10` and Reason to "Expired"
6. Click **"Update"**
7. **Expected:**
   - Success toast: "Damage updated successfully"
   - Table row updates with new quantity and reason
   - Total Quantity KPI card updates

#### C. Cancel Edit
1. Click ✏️ on any row
2. Click **"Cancel"**
3. **Expected:** Dialog closes, no changes made

#### D. Dialog Title Dynamic
- [ ] Click "Record Damage" → Title shows "Record Damage"
- [ ] Click ✏️ on existing row → Title shows "Edit Damage"

---

## 4. Cost & Profit Report — Edit Functionality

### How to Find
1. Navigate to **Reports → Cost & Profit** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/reports/cost-profit`

### What to Test

#### A. Existing Functionality (Regression)
- [ ] Page loads with 7 KPI cards (Total Cost, VAN, Oil, Labour, Office, Other, Records)
- [ ] "Add Cost" button works
- [ ] Create a cost entry: Date, VAN=500, Oil=300, Labour=200, Office=100, Other=50
- [ ] Record appears in table

#### B. Edit Cost Record
1. In the table, find the row you just created
2. Click the **✏️ (Pencil)** icon in the Actions column
3. **Expected:** Dialog opens with title "Edit Daily Cost"
4. **Expected:** All 5 cost fields pre-filled with original values
5. Change VAN to `800` and Oil to `400`
6. Click **"Save"**
7. **Expected:**
   - Success toast: "Cost updated successfully"
   - Table row updates
   - Total Cost KPI card recalculates

#### C. Dialog Title Dynamic
- [ ] Click "Add Cost" → Title shows "Add Daily Cost"
- [ ] Click ✏️ on existing row → Title shows "Edit Daily Cost"

---

## 5. DSR SO Assignments — Deliver/Pay/Load/Unload Actions

### How to Find
1. Navigate to **DSR → SO Assignments** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/dsr/so-assignments`

### What to Test

#### A. Page Load
- [ ] Page renders with assignments table
- [ ] Filters: DSR dropdown, Status dropdown
- [ ] Actions column has ⋯ dropdown on each row

#### B. Status-Based Actions
Click the ⋯ dropdown on different assignments and verify the correct actions appear:

| Status | Expected Actions |
|--------|-----------------|
| **assigned** | View Order, Load, Mark Delivered, Remove |
| **in_progress** | View Order, Collect Payment, Mark Delivered, Unload, Remove |
| **completed** | View Order, Unload, Remove |

#### C. Load Action (assigned status)
1. Find an assignment with status "assigned"
2. Click ⋯ → **"Load"**
3. **Expected:** Dialog appears with:
   - Title: "Load Sales Order"
   - Description about loading onto DSR storage
   - Optional note textarea
   - Cancel and "Load Order" buttons
4. Enter a note: "Loading for morning delivery"
5. Click **"Load Order"**
6. **Expected:**
   - Loading spinner on button
   - Success toast: "Sales order loaded successfully"
   - Dialog closes
   - Status may change to "in_progress"

#### D. Mark Delivered Action
1. Find an assignment with status "assigned" or "in_progress"
2. Click ⋯ → **"Mark Delivered"**
3. **Expected:** Confirmation dialog:
   - Title: "Mark as Delivered"
   - Description about completing delivery process
   - Cancel and "Mark Delivered" buttons
4. Click **"Mark Delivered"**
5. **Expected:**
   - Success toast: "Assignment marked as delivered"
   - Status changes to "completed"

#### E. Collect Payment Action (in_progress status)
1. Find an assignment with status "in_progress"
2. Click ⋯ → **"Collect Payment"**
3. **Expected:** Dialog appears with:
   - Title: "Collect Payment"
   - Payment Amount input (pre-filled with order total)
   - Optional note textarea
   - Cancel and "Collect Payment" buttons
4. Verify amount is pre-filled
5. Change amount if needed
6. Enter note: "Cash collected"
7. Click **"Collect Payment"**
8. **Expected:**
   - Success toast: "Payment collected successfully"
   - Dialog closes

#### F. Unload Action (in_progress or completed status)
1. Find an assignment with status "in_progress" or "completed"
2. Click ⋯ → **"Unload"**
3. **Expected:** Dialog appears with:
   - Title: "Unload Sales Order"
   - Description about returning stock to warehouse
   - Optional note textarea
   - Cancel and "Unload Order" (red/destructive) buttons
4. Enter note: "Returned unsold items"
5. Click **"Unload Order"**
6. **Expected:**
   - Success toast: "Sales order unloaded successfully"
   - Dialog closes

#### G. Error Handling
1. Try to load an assignment that's already loaded
2. **Expected:** Error toast "Failed to load sales order"
3. Try to collect payment with invalid amount (0 or negative)
4. **Expected:** Error toast "Please enter a valid payment amount"

---

## 6. Invoices — Statistics Summary

### How to Find
1. Navigate to **Sales → Invoices** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/invoices`

### What to Test

#### A. Statistics Cards
- [ ] 4 stat cards appear above the invoices table:
  - 📄 **Total Invoices** — Shows count (blue card)
  - 💰 **Total Amount** — Shows sum (emerald card)
  - 📈 **Average Amount** — Shows mean (purple card)
  - ✅ **Paid / Unpaid** — Shows "X / Y" with "Z Partial" description (amber card)
- [ ] Values match the data in the table below
- [ ] Cards show `0` when no invoices exist

#### B. Data Accuracy
1. Create a few invoices if none exist
2. Verify:
   - Total Invoices = count of rows in table
   - Total Amount = sum of all "Total Amount" column values
   - Average Amount = Total Amount / Total Invoices
   - Paid / Unpaid = count of invoices with each payment status

#### C. Existing Functionality (Regression)
- [ ] Invoice table still renders correctly
- [ ] Print invoice dialog still works
- [ ] Pagination works
- [ ] Filters work (if any)

---

## 7. Expenses — Statistics Summary

### How to Find
1. Navigate to **Expenses** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/expenses`

### What to Test

#### A. Statistics Cards
- [ ] 4 stat cards appear above the filters section:
  - 💼 **Total Expenses** — Shows count (emerald card)
  - 📈 **Total Amount** — Shows sum (blue card)
  - 🧾 **Average Amount** — Shows mean (purple card)
  - 🏷️ **Top Category** — Shows highest-spend category name (amber card)
- [ ] Values update when filters change

#### B. Filter Interaction
1. Apply a category filter
2. **Expected:** Stat cards recalculate to show filtered data only
3. Clear the filter
4. **Expected:** Stats return to full dataset values

#### C. Existing Functionality (Regression)
- [ ] Expense table still renders
- [ ] Edit expense dialog works
- [ ] Delete expense works
- [ ] Add expense works
- [ ] Filters work correctly

---

## 8. SR Price Management — Price Validation

### How to Find
1. Navigate to **SR → Price Management** in the sidebar
2. Or go directly to: `http://192.168.1.7:5173/sales-representatives/price-management`

### What to Test

#### A. Page Load
- [ ] Page renders with SR selector dropdown
- [ ] Select an SR from the dropdown
- [ ] Assigned prices table loads

#### B. Edit Price with Validation
1. Click the **✏️ (Edit)** button on any price assignment row
2. **Expected:** Price assignment form dialog opens
3. Verify the form shows:
   - Assigned Sale Price
   - Effective Date / Expiry Date
   - Allow Price Override toggle
   - Min/Max Override Price fields (if override allowed)
4. If "Allow Price Override" is ON and min/max bounds are set:
   - Try entering a price **below** the minimum
   - Try entering a price **above** the maximum
5. Click **"Save Price"**
6. **Expected:**
   - If price is outside bounds: Warning toast appears with validation message
   - Price still saves (warning is non-blocking)
   - Success toast: "Price assigned successfully"

#### C. Existing Functionality (Regression)
- [ ] Price history dialog still works (👁️ button)
- [ ] Search products works
- [ ] Pagination works
- [ ] Status badges display correctly

---

## 9. Product Image Gallery (Component — Not Yet Routed)

### How to Test (Manual Component Test)

The `ProductImageGallery` component is built but not yet integrated into a page route. To test it:

#### A. Temporary Test Route
Add this to `App.tsx` temporarily:
```tsx
import ProductImageGallery from "@/components/shared/ProductImageGallery";
// ...
{ path: "/test-images", element: <ProductImageGallery variantId={1} variantName="Test Variant" /> },
```

Then navigate to `http://192.168.1.7:5173/test-images`

#### B. What to Test

##### Empty State
- [ ] Shows "No images yet" message with Upload icon
- [ ] "Upload First Image" button visible

##### Upload Images
1. Click **"Upload Images"** or "Upload First Image"
2. **Expected:** Dialog opens with drag-and-drop area
3. Click the area to select files
4. Select 2-3 image files (PNG/JPG/WEBP)
5. **Expected:** File list appears with names and remove (✕) buttons
6. Click **"Upload (3)"**
7. **Expected:**
   - Loading spinner during upload
   - Success toast: "3 image(s) uploaded successfully"
   - Dialog closes
   - Images appear in gallery grid

##### Gallery Display
- [ ] Images display in responsive grid (2-5 columns)
- [ ] Each image shows as a card with the image preview
- [ ] Primary image has a "Primary" badge

##### Set Primary Image
1. Hover over any non-primary image
2. Click the **⭐ (Star)** button
3. **Expected:**
   - "Primary image updated" toast
   - Star fills on selected image
   - "Primary" badge moves to new primary

##### Reorder Images
1. Click and drag any image card by the **⋮⋮ (Grip)** handle
2. Drop it in a different position
3. **Expected:**
   - "Images reordered" toast
   - Images stay in new order

##### Edit Alt Text
1. Click on "Click to add alt text" below any image
2. **Expected:** Input field appears
3. Type "Front view of product"
4. Press Enter or click away
5. **Expected:**
   - "Alt text updated" toast
   - Alt text displays instead of placeholder

##### Delete Image
1. Hover over an image
2. Click the **🗑️ (Trash)** button
3. **Expected:** Browser confirmation dialog
4. Click "OK"
5. **Expected:**
   - "Image deleted" toast
   - Image removed from grid

---

## 10. Claims APIs (Backend — No UI Yet)

The following API functions were added to `claimsApi.ts` but don't have dedicated UI buttons yet. They can be tested via browser console or API client:

### Re-evaluate Order Schemes
```javascript
// In browser console (after login):
import { reevaluateOrderSchemes } from './lib/api/claimsApi';
reevaluateOrderSchemes(1, 'sale'); // Re-evaluate sale order #1
```

### Reverse Claim Logs
```javascript
import { reverseClaimLogs } from './lib/api/claimsApi';
reverseClaimLogs(1, 'sale', 'Order cancelled'); // Reverse claims for order #1
```

### Adjust Claim Logs
```javascript
import { adjustClaimLogs } from './lib/api/claimsApi';
adjustClaimLogs(1, 'sale', 0.5, 'Partial return - 50%'); // Adjust claims by 50%
```

---

## Common Test Scenarios

### A. Network Error Handling
For each feature, test with backend stopped:
1. Stop Docker: `docker-compose down`
2. Try to create/edit/delete data
3. **Expected:** Appropriate error toast (e.g., "Unable to connect to server")
4. Restart Docker: `docker-compose up -d`

### B. Concurrent Edits
1. Open two browser tabs on the same page
2. Edit the same record in both tabs
3. **Expected:** Second save shows conflict error or overwrites (depending on backend)

### C. Session Expiry
1. Log in and navigate to any feature page
2. Wait for token to expire (or manually delete from localStorage)
3. Try to perform an action
4. **Expected:** Redirect to login page

### D. Permission Checks
1. Log in as a non-admin user (if available)
2. Try to access admin-only features
3. **Expected:** Access denied or redirect

---

## Test Data Setup

### Prerequisites for Testing
Before testing, ensure the following data exists:

| Data Type | Minimum Required | How to Create |
|-----------|-----------------|---------------|
| Product Groups | 2+ | `/product-groups/new` |
| Products with Variants | 2+ | `/products/new` |
| Customers | 3+ | `/customers/new` |
| SRs | 2+ | `/sales-representatives/new` |
| DSRs | 1+ | `/dsr/new` |
| Sales Orders | 3+ | `/sales/new` |
| SR Orders (unconsolidated) | 3+ | Via SR mobile or API |
| DSR SO Assignments | 3+ (different statuses) | `/dsr/so-assignments` |
| Invoices | 3+ (mixed statuses) | `/invoices` |
| Expenses | 3+ (mixed categories) | `/expenses/new` |

### Quick Data Setup Script
If you have API access, run these to create test data:
```bash
# Create test ledger entries
curl -X POST http://localhost:8000/api/company/sr-reports/ledger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entry_date":"2026-04-01","entry_type":"order","order_amount":5000,"sales_amount":4500,"payment_amount":4000,"notes":"Test entry"}'
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Page shows blank/white | Route not registered | Check `App.tsx` import and route |
| API returns 404 | Backend not running | `docker-compose up -d` |
| API returns 401 | Token expired | Log out and log back in |
| "Unable to connect" toast | Backend down or wrong URL | Check `src/lib/config.ts` BASE_URL |
| Images don't upload | S3 not configured | Check backend S3 service config |
| Bulk approve button missing | No rows selected | Click checkboxes first |
| DSR actions not showing | Wrong status | Check assignment status in table |
| Stats show 0 | No data in date range | Create test data or expand date range |

---

## Checklist Summary

| Feature | Found? | Create | Read | Update | Delete | Filter | Notes |
|---------|--------|--------|------|--------|--------|--------|-------|
| Sales Ledger | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Bulk Approve | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Damage Edit | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Cost Edit | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| DSR Actions | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Invoice Stats | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Expense Stats | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Price Validation | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | |
| Image Gallery | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Component only |

---

*Testing guide created: 2026-04-03*  
*All features verified against `FRONTEND_MISSING_UI_ANALYSIS.md` requirements*
