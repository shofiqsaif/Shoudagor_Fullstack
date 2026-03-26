# DSR Complete Lifecycle - Comprehensive UI Testing Guide
## SR Order → DSR Assignment → Load/Unload → Delivery → Settlement → Commission

**Document Version:** 2.0  
**Created:** March 26, 2026  
**System:** Shoudagor Distribution Management System  
**Module:** Complete DSR Lifecycle (SR Order → Sales Order → DSR → Settlement)  
**Purpose:** End-to-end UI testing guide covering all DSR workflows, edge cases, validation scenarios, and data consistency verification

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Testing Prerequisites](#3-testing-prerequisites)
4. [SR Order Creation & Approval](#4-sr-order-creation--approval)
5. [SR Order Consolidation to Sales Order](#5-sr-order-consolidation-to-sales-order)
6. [DSR Assignment Testing](#6-dsr-assignment-testing)
7. [DSR Load Operations Testing](#7-dsr-load-operations-testing)
8. [DSR Delivery Operations Testing](#8-dsr-delivery-operations-testing)
9. [DSR Payment Collection Testing](#9-dsr-payment-collection-testing)
10. [DSR Unload Operations Testing](#10-dsr-unload-operations-testing)
11. [DSR Payment Settlement Testing](#11-dsr-payment-settlement-testing)
12. [Commission Disbursement Testing](#12-commission-disbursement-testing)
13. [Edge Cases & Error Scenarios](#13-edge-cases--error-scenarios)
14. [Data Integrity Verification](#14-data-integrity-verification)
15. [Complete Testing Checklist](#15-complete-testing-checklist)

---

## 1. Executive Summary

### 1.1 Document Purpose

This comprehensive guide provides complete UI testing procedures for the entire DSR lifecycle in Shoudagor ERP, covering:
- SR Order creation and approval workflows
- SR Order consolidation into Sales Orders
- DSR assignment and management
- DSR Load/Unload operations with inventory transfers
- DSR delivery and payment collection
- DSR payment settlement with admin
- Commission calculation and disbursement
- Data consistency across all interconnected modules
- Critical edge cases and error handling

### 1.2 DSR Lifecycle Overview

The DSR (Delivery Sales Representative) lifecycle is a complete order-to-cash process:

```
SR Creates Order → Admin Approves → Consolidate to SO → 
Assign to DSR → Load to DSR Van → Deliver to Customer → 
Collect Payment → Unload Remaining → Settle with Admin → 
Disburse Commission
```

### 1.3 Key Business Rules

**SR Order Management:**
- SR creates orders with negotiated prices
- Commission = (Negotiated Price - Sale Price) × Quantity
- Orders must be approved before consolidation
- Multiple SR orders can consolidate into one SO

**DSR Assignment:**
- DSR must have storage configured
- DSR must be active
- SO cannot be already loaded
- Stock validation at SO location

**Load Operations:**
- Transfers inventory from warehouse to DSR storage
- Creates batch allocations for tracking
- Updates SO `is_loaded` flag
- Records `loaded_by_dsr_id` and `loaded_at`

**Delivery Operations:**
- Updates `shipped_quantity` on SO details
- Deducts from DSR inventory
- Handles partial deliveries
- Processes returns/rejections

**Payment Collection:**
- Increases DSR `payment_on_hand`
- Decreases customer balance
- Updates SO `amount_paid`
- Tracks payment method and reference

**Unload Operations:**
- Returns undelivered items to warehouse
- Reverses inventory transfers
- Updates SO `is_loaded` to false
- Clears DSR batch allocations

**Settlement:**
- Admin collects payment from DSR
- Decreases DSR `payment_on_hand`
- Creates settlement record
- Validates amount ≤ payment_on_hand

**Commission:**
- Calculated when SO completes
- Status: pending → Ready → Disbursed
- Increases SR `commission_amount` when Ready
- Decreases when Disbursed

---

## 2. System Architecture Overview

### 2.1 Data Models

**Core Entities:**
