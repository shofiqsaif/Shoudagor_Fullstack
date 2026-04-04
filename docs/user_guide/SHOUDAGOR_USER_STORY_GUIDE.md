# Shoudagor ERP - User Story Guide

**A Simple Guide for Everyone**  
**Version:** 1.0  
**Date:** March 26, 2026

---

## Welcome to Shoudagor! 🎉

This guide tells the story of how different people use Shoudagor ERP in their daily work. Whether you're a warehouse manager, sales person, or business owner, you'll find your story here.

---

## Table of Contents

1. [Getting Started - Your First Day](#getting-started---your-first-day)
2. [Story 1: The Warehouse Manager - Receiving Stock](#story-1-the-warehouse-manager---receiving-stock)
3. [Story 2: The Sales Person - Making a Sale](#story-2-the-sales-person---making-a-sale)
4. [Story 3: The Field Sales Rep - Taking Orders on the Go](#story-3-the-field-sales-rep---taking-orders-on-the-go)
5. [Story 4: The Delivery Driver - Delivering Orders](#story-4-the-delivery-driver---delivering-orders)
6. [Story 5: The Admin - Consolidating Orders](#story-5-the-admin---consolidating-orders)
7. [Story 6: The Business Owner - Running Reports](#story-6-the-business-owner---running-reports)
8. [Story 7: The Accountant - Managing Payments](#story-7-the-accountant---managing-payments)
9. [Story 8: The Marketing Manager - Creating Promotions](#story-8-the-marketing-manager---creating-promotions)
10. [Quick Reference Guide](#quick-reference-guide)

---

## Getting Started - Your First Day

### Meet Sarah - New Employee

**Sarah's Story:**
"It's my first day at ABC Trading Company. My manager gave me a username and password for Shoudagor. Let me log in..."

**What Sarah Does:**

1. **Opens the Shoudagor website** in her browser
2. **Sees the login screen** with a nice image
3. **Enters her username and password**
4. **Clicks "Login"**
5. **Sees the dashboard** - her home screen with colorful cards showing:
   - Today's sales
   - Pending orders
   - Low stock alerts
   - Recent activities

**Sarah's Tip:** "The dashboard is like my command center. Everything I need is just a click away!"

---

## Story 1: The Warehouse Manager - Receiving Stock

### Meet John - Warehouse Manager

**John's Story:**
"A truck just arrived with 500 boxes of soap from our supplier. I need to check them in and update our inventory."

### Step-by-Step: Receiving a Purchase Order

**1. Finding the Purchase Order**

John opens Shoudagor and clicks:
- **Purchases** from the sidebar
- Sees a list of all purchase orders
- Finds PO #PO-20260326-001 (today's delivery)
- Status shows: "Open" (waiting for delivery)

**2. Recording the Delivery**

John clicks the **"Receive"** button and sees:

```
┌─────────────────────────────────────────────────┐
│         Receive Purchase Order Items            │
├─────────────────────────────────────────────────┤
│                                                 │
│  Delivery Date: [March 26, 2026]               │
│                                                 │
│  Items to Receive:                              │
│  ┌───────────────────────────────────────────┐ │
│  │ Product: Dove Soap 100g                   │ │
│  │ Ordered: 500 boxes                        │ │
│  │ Already Received: 0                       │ │
│  │ Pending: 500                              │ │
│  │                                           │ │
│  │ Delivered Qty: [500] ✓                   │ │
│  │ Rejected Qty: [0]                         │ │
│  │ Free Qty: [50] (Bonus from supplier!)    │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  [Cancel]  [Save Delivery]                     │
└─────────────────────────────────────────────────┘
```

**3. What Happens Behind the Scenes** (John doesn't see this, but it's important!)

When John clicks "Save Delivery":
- ✅ Stock increases in the warehouse
- ✅ A batch is created with cost information
- ✅ The system logs the movement
- ✅ The supplier's balance is updated
- ✅ PO status changes to "Completed"

**John's Tip:** "I always check the free quantity! Sometimes suppliers give us bonus items with promotions."

**Real-World Example:**
```
Before: Dove Soap stock = 100 boxes
After:  Dove Soap stock = 650 boxes (100 + 500 + 50 free)
```

---

## Story 2: The Sales Person - Making a Sale

### Meet Maria - Sales Counter Staff

**Maria's Story:**
"A customer just walked in wanting to buy 20 boxes of Dove Soap and 10 bottles of shampoo. Let me create a sales order."

### Step-by-Step: Creating a Sales Order

**1. Starting a New Sale**

Maria clicks:
- **Sales** from the sidebar
- **"+ New Sale"** button
- Sees a blank sales form

**2. Filling in Customer Details**

```
┌─────────────────────────────────────────────────┐
│           Create Sales Order                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  Customer: [Search...] → "ABC Retail Store"    │
│  Order Date: March 26, 2026                     │
│  Delivery Date: March 28, 2026                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

**3. Adding Products**

Maria clicks **"Add Product"** and searches:

```
┌─────────────────────────────────────────────────┐
│  Product 1:                                     │
│  ┌───────────────────────────────────────────┐ │
│  │ Product: Dove Soap 100g                   │ │
│  │ Available Stock: 650 boxes ✓              │ │
│  │ Quantity: [20] boxes                      │ │
│  │ Price: $5.00 per box                      │ │
│  │ Total: $100.00                            │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Product 2:                                     │
│  ┌───────────────────────────────────────────┐ │
│  │ Product: Herbal Shampoo 500ml             │ │
│  │ Available Stock: 200 bottles ✓            │ │
│  │ Quantity: [10] bottles                    │ │
│  │ Price: $8.00 per bottle                   │ │
│  │ Total: $80.00                             │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  🎁 Promotion Applied!                          │
│  Buy 20 Dove Soap, Get 2 Free!                 │
│                                                 │
│  Order Total: $180.00                           │
│  [Cancel]  [Create Order]                      │
└─────────────────────────────────────────────────┘
```

**4. What the Customer Sees**

Maria prints the order confirmation:
```
ABC Trading Company
Sales Order: SO-20260326-001

Customer: ABC Retail Store
Date: March 26, 2026

Items:
1. Dove Soap 100g        20 boxes @ $5.00  = $100.00
   FREE BONUS             2 boxes @ $0.00  = $0.00
2. Herbal Shampoo 500ml  10 bottles @ $8.00 = $80.00

Total Amount: $180.00
Status: Pending Delivery

Thank you for your business!
```

**Maria's Tip:** "Always check the 'Available Stock' before adding items. The system won't let me sell more than we have!"

---

## Story 3: The Field Sales Rep - Taking Orders on the Go

### Meet Ahmed - Sales Representative (SR)

**Ahmed's Story:**
"I visit 20 shops every day in my area. I take orders on my phone and send them to the office for approval."

### Step-by-Step: SR Taking Orders

**1. Ahmed's Morning Routine**

Ahmed opens Shoudagor on his phone:
- Logs in with his SR account
- Sees his **assigned customers** (only shops in his area)
- Sees his **assigned products** (products he's allowed to sell)
- Checks today's route

**2. Visiting Shop #1 - "Corner Store"**

Ahmed arrives at Corner Store:

```
📱 Ahmed's Phone Screen:
┌─────────────────────────────────────┐
│  🏪 Corner Store                    │
│  Last Order: 5 days ago             │
│  Outstanding: $250                  │
│                                     │
│  [Create New Order]                 │
└─────────────────────────────────────┘
```

**3. Taking the Order**

Shop owner: "I need 10 boxes of Dove Soap"

Ahmed creates an SR Order:
```
┌─────────────────────────────────────┐
│  SR Order for Corner Store          │
├─────────────────────────────────────┤
│  Product: Dove Soap 100g            │
│  Company Price: $5.00               │
│  My Negotiated Price: $4.80         │
│  Quantity: 10 boxes                 │
│                                     │
│  My Commission: $2.00               │
│  (10 boxes × $0.20 difference)      │
│                                     │
│  [Add to Order]                     │
└─────────────────────────────────────┘
```

**4. End of Day**

Ahmed has taken 15 orders today:
- All orders show status: "Pending Approval"
- He submits them to the office
- Goes home and waits for approval

**Ahmed's Tip:** "The better price I negotiate, the more commission I earn! But I can't go below the minimum price set by the company."

---

## Story 4: The Delivery Driver - Delivering Orders

### Meet David - Delivery Sales Representative (DSR)

**David's Story:**
"Every morning, the admin loads orders into my van. I deliver them to customers and collect payments."

### Step-by-Step: DSR Daily Workflow

**1. Morning - Loading the Van**

Admin (Lisa) assigns orders to David:
```
┌─────────────────────────────────────────────────┐
│  Assign Orders to DSR: David                    │
├─────────────────────────────────────────────────┤
│  ☑ SO-20260326-001 (ABC Retail)    $180.00     │
│  ☑ SO-20260326-005 (Corner Store)  $48.00      │
│  ☑ SO-20260326-008 (Mini Mart)     $95.00      │
│                                                 │
│  Total: 3 orders, $323.00                       │
│  [Load to DSR Van]                              │
└─────────────────────────────────────────────────┘
```

When Lisa clicks "Load to DSR Van":
- Stock moves from warehouse to David's van inventory
- David can now see these orders on his phone
- Orders are marked as "Loaded"

**2. David's Phone - Delivery List**

```
📱 David's Delivery App:
┌─────────────────────────────────────┐
│  Today's Deliveries (3)             │
├─────────────────────────────────────┤
│  1. ABC Retail Store                │
│     20 Dove Soap, 10 Shampoo        │
│     Amount: $180.00                 │
│     [Navigate] [Deliver]            │
│                                     │
│  2. Corner Store                    │
│     10 Dove Soap                    │
│     Amount: $48.00                  │
│     [Navigate] [Deliver]            │
│                                     │
│  3. Mini Mart                       │
│     15 Shampoo                      │
│     Amount: $95.00                  │
│     [Navigate] [Deliver]            │
└─────────────────────────────────────┘
```

**3. At ABC Retail Store**

David arrives and clicks "Deliver":
```
┌─────────────────────────────────────┐
│  Deliver to ABC Retail Store        │
├─────────────────────────────────────┤
│  Items:                             │
│  ☑ Dove Soap: 20 boxes ✓            │
│  ☑ Shampoo: 10 bottles ✓            │
│                                     │
│  Payment Collection:                │
│  Amount Due: $180.00                │
│  Received: [$180.00]                │
│  Method: [Cash ▼]                   │
│                                     │
│  Customer Signature: [____]         │
│  [Complete Delivery]                │
└─────────────────────────────────────┘
```

**4. End of Day - Settlement**

David returns to office with cash:
```
David's Cash on Hand: $323.00
- ABC Retail: $180.00
- Corner Store: $48.00
- Mini Mart: $95.00

Admin settles with David:
✓ Cash received: $323.00
✓ David's account cleared
✓ Orders marked as "Paid"
```

**David's Tip:** "I always get customer signatures on delivery. It protects both of us!"

---

## Story 5: The Admin - Consolidating Orders

### Meet Lisa - Office Administrator

**Lisa's Story:**
"Ahmed (SR) submitted 15 orders yesterday. I need to approve them and consolidate orders for the same customers."

### Step-by-Step: Consolidating SR Orders

**1. Reviewing SR Orders**

Lisa opens **SR Orders** section:
```
┌─────────────────────────────────────────────────┐
│  SR Orders - Pending Approval                   │
├─────────────────────────────────────────────────┤
│  SR: Ahmed                                      │
│  Date: March 25, 2026                           │
│                                                 │
│  ☑ Corner Store    10 Dove Soap    $48.00      │
│  ☑ Corner Store     5 Shampoo      $40.00      │
│  ☑ Mini Mart       15 Dove Soap    $72.00      │
│  ☑ Big Shop        20 Dove Soap    $96.00      │
│                                                 │
│  [Approve Selected] [Reject]                    │
└─────────────────────────────────────────────────┘
```

**2. Approving Orders**

Lisa reviews each order:
- Checks if customer has credit limit available
- Checks if products are in stock
- Clicks "Approve Selected"

**3. Consolidating Orders**

Lisa notices Corner Store has 2 orders:
```
┌─────────────────────────────────────────────────┐
│  Consolidate SR Orders                          │
├─────────────────────────────────────────────────┤
│  Customer: Corner Store                         │
│                                                 │
│  Selected Orders:                               │
│  ☑ SR Order #1: 10 Dove Soap ($48.00)          │
│  ☑ SR Order #2: 5 Shampoo ($40.00)             │
│                                                 │
│  Consolidated Sales Order will have:            │
│  - 10 Dove Soap (from Ahmed)                    │
│  - 5 Shampoo (from Ahmed)                       │
│  Total: $88.00                                  │
│                                                 │
│  Ahmed's Commission: $4.00                      │
│                                                 │
│  [Consolidate into Sales Order]                 │
└─────────────────────────────────────────────────┘
```

**4. Result**

After consolidation:
- ✅ New Sales Order created: SO-20260326-010
- ✅ Both SR orders marked as "Consolidated"
- ✅ Ahmed's commission recorded: $4.00
- ✅ Order ready for delivery

**Lisa's Tip:** "Consolidating saves time! Instead of processing 2 separate deliveries to Corner Store, we do it in one trip."

---

## Story 6: The Business Owner - Running Reports

### Meet Mr. Rahman - Business Owner

**Mr. Rahman's Story:**
"It's month-end. I need to see how my business is performing."

### Step-by-Step: Viewing Business Reports

**1. Opening the Dashboard**

Mr. Rahman logs in and sees:

```
┌─────────────────────────────────────────────────┐
│  Dashboard - March 2026                         │
├─────────────────────────────────────────────────┤
│  📊 This Month:                                 │
│  Sales: $45,230                                 │
│  Purchases: $32,100                             │
│  Profit: $13,130                                │
│                                                 │
│  📦 Inventory:                                  │
│  Total Value: $89,500                           │
│  Low Stock Items: 5                             │
│                                                 │
│  💰 Financials:                                 │
│  Receivables: $12,300 (customers owe us)        │
│  Payables: $8,900 (we owe suppliers)            │
└─────────────────────────────────────────────────┘
```

**2. Sales Report**

Mr. Rahman clicks **Reports → Sales Report**:
```
┌─────────────────────────────────────────────────┐
│  Sales Report - March 2026                      │
├─────────────────────────────────────────────────┤
│  Top Selling Products:                          │
│  1. Dove Soap 100g        450 boxes  $2,250     │
│  2. Herbal Shampoo        320 bottles $2,560    │
│  3. Toothpaste            280 tubes   $1,680    │
│                                                 │
│  Top Customers:                                 │
│  1. ABC Retail Store               $5,600       │
│  2. Big Shop                       $4,200       │
│  3. Corner Store                   $3,800       │
│                                                 │
│  Sales by SR:                                   │
│  1. Ahmed                          $8,900       │
│  2. Fatima                         $7,200       │
│  3. Hassan                         $6,100       │
│                                                 │
│  [Export to Excel] [Print]                      │
└─────────────────────────────────────────────────┘
```

**3. Inventory Report**

Mr. Rahman checks stock levels:
```
┌─────────────────────────────────────────────────┐
│  Inventory Report                               │
├─────────────────────────────────────────────────┤
│  ⚠️ Low Stock Alerts:                           │
│  - Toothpaste: 15 tubes (Reorder: 50)          │
│  - Hand Soap: 8 boxes (Reorder: 30)            │
│                                                 │
│  📦 Stock by Category:                          │
│  - Personal Care: $45,200                       │
│  - Household: $32,100                           │
│  - Food Items: $12,200                          │
│                                                 │
│  🔄 Fast Moving Items:                          │
│  - Dove Soap (sold 450 this month)             │
│  - Shampoo (sold 320 this month)               │
│                                                 │
│  🐌 Slow Moving Items:                          │
│  - Premium Perfume (sold 5 this month)          │
└─────────────────────────────────────────────────┘
```

**Mr. Rahman's Tip:** "I check reports every week. It helps me make smart decisions about what to buy and what to promote."

---

## Story 7: The Accountant - Managing Payments

### Meet Fatima - Accountant

**Fatima's Story:**
"I handle all payments - both from customers and to suppliers. Let me show you a typical day."

### Step-by-Step: Payment Management

**1. Customer Payments**

Fatima opens **Sales → Payments**:
```
┌─────────────────────────────────────────────────┐
│  Customer Payments Due                          │
├─────────────────────────────────────────────────┤
│  ABC Retail Store                               │
│  Outstanding: $1,250                            │
│  Orders:                                        │
│  - SO-001: $450 (15 days old)                   │
│  - SO-005: $800 (5 days old)                    │
│  [Record Payment]                               │
│                                                 │
│  Corner Store                                   │
│  Outstanding: $380                              │
│  Orders:                                        │
│  - SO-003: $380 (3 days old)                    │
│  [Record Payment]                               │
└─────────────────────────────────────────────────┘
```

**2. Recording a Payment**

ABC Retail calls: "We're paying $450 for SO-001"

Fatima clicks "Record Payment":
```
┌─────────────────────────────────────────────────┐
│  Record Payment                                 │
├─────────────────────────────────────────────────┤
│  Customer: ABC Retail Store                     │
│  Order: SO-001                                  │
│  Amount Due: $450                               │
│                                                 │
│  Payment Details:                               │
│  Amount: [$450.00]                              │
│  Date: [March 26, 2026]                         │
│  Method: [Bank Transfer ▼]                      │
│  Reference: [TXN-12345]                         │
│                                                 │
│  [Save Payment]                                 │
└─────────────────────────────────────────────────┘
```

**3. Supplier Payments**

Fatima also pays suppliers:
```
┌─────────────────────────────────────────────────┐
│  Supplier Payments Due                          │
├─────────────────────────────────────────────────┤
│  Unilever Bangladesh                            │
│  We Owe: $8,500                                 │
│  Purchase Orders:                               │
│  - PO-001: $5,000 (Due: March 30)              │
│  - PO-003: $3,500 (Due: April 5)               │
│  [Make Payment]                                 │
└─────────────────────────────────────────────────┘
```

**Fatima's Tip:** "I always enter the bank reference number. It makes reconciliation so much easier!"

---

## Story 8: The Marketing Manager - Creating Promotions

### Meet Zara - Marketing Manager

**Zara's Story:**
"We're launching a promotion: Buy 10 Dove Soap, Get 1 Free! Let me set it up in the system."

### Step-by-Step: Creating a Promotion Scheme

**1. Opening Schemes**

Zara clicks **Claims & Schemes → New Scheme**:

```
┌─────────────────────────────────────────────────┐
│  Create Promotion Scheme                        │
├─────────────────────────────────────────────────┤
│  Scheme Name: [Dove Soap March Promo]          │
│  Type: [Buy X Get Y Free ▼]                    │
│  Start Date: [March 26, 2026]                   │
│  End Date: [March 31, 2026]                     │
│                                                 │
│  Trigger Product: [Dove Soap 100g]             │
│                                                 │
│  Scheme Tiers:                                  │
│  ┌───────────────────────────────────────────┐ │
│  │ Buy 10 boxes → Get 1 box FREE             │ │
│  │ Buy 20 boxes → Get 2 boxes FREE           │ │
│  │ Buy 50 boxes → Get 5 boxes FREE           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  [Save Scheme]                                  │
└─────────────────────────────────────────────────┘
```

**2. How It Works**

When Maria (sales person) creates an order:
```
Customer orders: 25 boxes of Dove Soap

System automatically calculates:
- 20 boxes → 2 free boxes
- 5 boxes → 0 free boxes (doesn't reach next tier)
- Total free: 2 boxes

Order shows:
Dove Soap: 25 boxes @ $5.00 = $125.00
FREE BONUS: 2 boxes @ $0.00 = $0.00
```

**3. Tracking Promotion Performance**

Zara checks the report:
```
┌─────────────────────────────────────────────────┐
│  Promotion Performance Report                   │
│  Dove Soap March Promo                          │
├─────────────────────────────────────────────────┤
│  Period: March 26-31, 2026                      │
│                                                 │
│  📊 Results:                                    │
│  - Orders with promotion: 45                    │
│  - Total sold: 680 boxes                        │
│  - Free items given: 68 boxes                   │
│  - Revenue: $3,400                              │
│                                                 │
│  💡 Impact:                                     │
│  - 35% increase vs last week                    │
│  - Cost of free items: $340                     │
│  - Net benefit: $850 extra profit               │
└─────────────────────────────────────────────────┘
```

**Zara's Tip:** "Promotions boost sales! But I always track the cost to make sure we're still profitable."

---

## Quick Reference Guide

### Common Tasks - Quick Steps

**🛒 Create a Purchase Order**
1. Click **Purchases** → **New Purchase**
2. Select Supplier
3. Add Products
4. Click **Create Order**

**📦 Receive Stock**
1. Click **Purchases** → Find PO
2. Click **Receive**
3. Enter delivered quantities
4. Click **Save Delivery**

**💰 Create a Sales Order**
1. Click **Sales** → **New Sale**
2. Select Customer
3. Add Products (system checks stock)
4. Click **Create Order**

**🚚 Deliver an Order**
1. Click **Sales** → Find SO
2. Click **Deliver**
3. Enter delivered quantities
4. Click **Save Delivery**

**💵 Record Payment**
1. Click **Sales** or **Purchases**
2. Find Order → Click **Payment**
3. Enter amount and details
4. Click **Save Payment**

**📱 SR Takes Order (Mobile)**
1. Open Shoudagor on phone
2. Select Customer (from assigned list)
3. Add Products (from assigned list)
4. Enter negotiated price
5. Submit for approval

**🎁 Create Promotion**
1. Click **Claims & Schemes** → **New Scheme**
2. Choose scheme type
3. Set trigger product and rewards
4. Set dates
5. Click **Save**

---

## Understanding Order Status

### Purchase Order Status
- **Open** = Created, waiting for delivery
- **Partial** = Some items received, some pending
- **Completed** = All items received and paid

### Sales Order Status
- **Open** = Created, not yet delivered
- **Partial** = Some items delivered or partially paid
- **Completed** = Fully delivered and paid
- **Cancelled** = Order cancelled

### Payment Status
- **Pending** = No payment received
- **Partial** = Some payment received
- **Completed** = Fully paid

### Delivery Status
- **Pending** = Not yet delivered
- **In Progress** = Partially delivered
- **Completed** = Fully delivered

---

## Tips for Success

### For Warehouse Staff
✅ Always count items carefully when receiving
✅ Check for damaged items and mark as rejected
✅ Record free items separately
✅ Update the system immediately

### For Sales Staff
✅ Check stock before promising delivery
✅ Explain promotions to customers
✅ Get customer signatures on delivery
✅ Record payments immediately

### For Sales Reps (SR)
✅ Visit customers regularly
✅ Know your assigned products well
✅ Negotiate good prices (more commission!)
✅ Submit orders daily

### For Admins
✅ Approve SR orders quickly
✅ Consolidate orders to save delivery costs
✅ Monitor stock levels daily
✅ Assign DSRs efficiently

### For Business Owners
✅ Check dashboard daily
✅ Review reports weekly
✅ Monitor slow-moving items
✅ Track customer payments

---

## Common Questions

**Q: Can I sell more than available stock?**
A: No, the system will show an error if you try to sell more than available stock.

**Q: What happens if a customer returns items?**
A: Create a return, and the stock will be added back to inventory.

**Q: How do I know my commission as an SR?**
A: The system calculates it automatically: (Your Price - Company Price) × Quantity

**Q: Can I cancel an order?**
A: Yes, but only if it hasn't been delivered yet.

**Q: How do promotions work?**
A: The system automatically applies promotions when you create orders. You'll see free items added.

**Q: What if I make a mistake?**
A: Contact your admin immediately. Some things can be edited, others may need to be cancelled and recreated.

---

## Need Help?

**Contact Your System Administrator**
- For login issues
- For permission problems
- For training requests

**Check the Dashboard**
- Recent activities show what happened
- Notifications alert you to important events

**Use the Search**
- Search for customers, products, orders
- Quick way to find anything

---

## Conclusion

Shoudagor ERP makes business management simple! Whether you're receiving stock, making sales, or running reports, everything is just a few clicks away.

**Remember:**
- 🔐 Always log out when done
- 💾 Save your work frequently
- 📱 Mobile app works offline (syncs when online)
- 🆘 Ask for help when needed

**Happy Selling! 🎉**

---

*This guide is designed for easy understanding. For technical details, refer to the technical documentation.*
