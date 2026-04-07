# Claim Scheme Update Bug - Implementation Plan

> **Created:** 2026-04-07  
> **Status:** Ready for Implementation  
> **Scope:** Frontend + Backend fixes for silent data corruption on scheme update

---

## Problem Statement

Client reports that updating a Scheme shows "Scheme updated successfully", but changes don't persist. This affects **a single specific scheme** in their account — other schemes work fine.

---

## Root Cause Analysis

After thorough code review, **4 interconnected issues** cause the update to fail silently:

### Issue 1: Frontend Select Components Use `defaultValue` (Uncontrolled)
**File:** `shoudagor_FE/src/pages/claims/SchemeForm.tsx:168,191`

```tsx
// BROKEN: defaultValue doesn't update when form.reset() is called
<Select onValueChange={field.onChange} defaultValue={field.value}>
```

**Impact:** When editing a scheme with `applicable_to: "sale"`, the Select still shows `"purchase"` (the default). On submit, it sends the wrong value.

---

### Issue 2: Frontend Sends `0` for Optional Fields Instead of `null`
**File:** `shoudagor_FE/src/pages/claims/SchemeForm.tsx:324,325,345`

```tsx
// When user clears a selection, 0 is sent instead of null:
onChange={(val) => {
    field.onChange(val ? Number(val) : 0);  // ← 0 sent to backend
    form.setValue("trigger_variant_id", 0); // ← 0 sent to backend
}}
```

**Impact:** Database foreign key relationships are corrupted. `0` is not a valid FK — it should be `NULL`.

---

### Issue 3: Frontend Sends Full Form Data on Update
**File:** `shoudagor_FE/src/lib/api/claimsApi.ts:89-106`

```typescript
export const updateScheme = async (id: number, data: Partial<ClaimSchemeType>): Promise<ClaimSchemeType> => {
    const payload = { ...data };
    // Only dates are transformed, no filtering of 0/null values
    // Sends entire form data including 0 values for optional fields
    return await apiRequest(api, `/claims/schemes/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
    });
};
```

**Impact:** The backend's `exclude_unset=True` doesn't help because the frontend explicitly sets these fields to `0`.

---

### Issue 4: Backend Doesn't Normalize `0` Values
**File:** `Shoudagor/app/services/claims/claim_service.py:181-309`

The `update_scheme` method doesn't validate or normalize `0` values for optional integer fields. When `0` reaches the repository, it's set directly on the model.

---

## Data Flow (Current - Broken)

```
User clicks "Edit Scheme"
    ↓
form.reset() loads scheme data (trigger_product_id: 5, trigger_variant_id: 12)
    ↓
Select components DON'T update (defaultValue is uncontrolled)
    ↓
User modifies some fields, clicks "Save"
    ↓
Form submits with:
  - trigger_product_id: 0 (from default/reset value, not from loaded data)
  - trigger_variant_id: 0 (from default/reset value, not from loaded data)
  - applicable_to: "purchase" (from default, not from loaded "sale")
    ↓
Backend receives payload with 0 values
    ↓
Repository sets db_scheme.trigger_product_id = 0
    ↓
Database now has invalid foreign key (0 instead of NULL or valid ID)
    ↓
Success response returned (no validation error for 0)
    ↓
UI shows "Scheme updated successfully" but data is corrupted
```

---

## Implementation Plan

### Phase 1: Frontend Fixes

#### Fix 1.1: Convert Select Components to Controlled Pattern
**File:** `shoudagor_FE/src/pages/claims/SchemeForm.tsx`
**Lines:** 168, 191

Change `defaultValue` → `value`:
```tsx
// FROM (uncontrolled):
<Select onValueChange={field.onChange} defaultValue={field.value}>

// TO (controlled):
<Select onValueChange={field.onChange} value={field.value}>
```

---

#### Fix 1.2: Fix SearchableSelect onChange for Trigger Fields
**File:** `shoudagor_FE/src/pages/claims/SchemeForm.tsx`
**Lines:** 323-326, 345

Change `0` → `null` for optional fields:
```tsx
// trigger_product_id onChange
onChange={(val) => {
    field.onChange(val ? Number(val) : null);
    form.setValue("trigger_variant_id", null);
}}

// trigger_variant_id onChange
onChange={(val) => field.onChange(val ? Number(val) : null)}
```

---

#### Fix 1.3: Update Form Reset to Handle Optional Fields
**File:** `shoudagor_FE/src/pages/claims/SchemeForm.tsx`
**Lines:** 97-105

Convert `null` values from backend to `undefined`:
```tsx
useEffect(() => {
    if (schemeData) {
        form.reset({
            ...schemeData,
            trigger_product_id: schemeData.trigger_product_id || undefined,
            trigger_variant_id: schemeData.trigger_variant_id || undefined,
            free_product_id: schemeData.free_product_id || undefined,
            free_variant_id: schemeData.free_variant_id || undefined,
            start_date: new Date(schemeData.start_date),
            end_date: new Date(schemeData.end_date)
        });
    }
}, [schemeData, form]);
```

---

#### Fix 1.4: Update Form Default Values
**File:** `shoudagor_FE/src/pages/claims/SchemeForm.tsx`
**Lines:** 33-46

Change default values from `0` to `undefined`:
```tsx
const form = useForm<ClaimSchemeType>({
    resolver: zodResolver(ClaimSchemeSchema) as any,
    defaultValues: {
        scheme_name: "",
        description: "",
        scheme_type: "buy_x_get_y",
        start_date: new Date(),
        end_date: new Date(),
        trigger_product_id: undefined,
        trigger_variant_id: undefined,
        free_product_id: undefined,
        free_variant_id: undefined,
        applicable_to: "purchase",
        is_active: true,
        slabs: [{ threshold_qty: 0, free_qty: 0, discount_amount: 0, discount_percentage: 0 }]
    }
});
```

---

#### Fix 1.5: Add Payload Sanitization in `updateScheme`
**File:** `shoudagor_FE/src/lib/api/claimsApi.ts`
**Lines:** 89-106

Filter out `null`/`undefined` values so backend's `exclude_unset=True` preserves existing values:
```typescript
export const updateScheme = async (id: number, data: Partial<ClaimSchemeType>): Promise<ClaimSchemeType> => {
    const payload: any = { ...data };
    
    // Remove null/undefined values so backend doesn't overwrite valid data
    Object.keys(payload).forEach(key => {
        if (payload[key] === null || payload[key] === undefined) {
            delete payload[key];
        }
    });
    
    if (payload.start_date) payload.start_date = new Date(payload.start_date).toISOString();
    if (payload.end_date) payload.end_date = new Date(payload.end_date).toISOString();
    
    return await apiRequest(api, `/claims/schemes/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
    });
};
```

---

### Phase 2: Backend Fixes

#### Fix 2.1: Normalize `0` to `None` in `update_scheme`
**File:** `Shoudagor/app/services/claims/claim_service.py`
**Lines:** After line 190 (after the "Scheme not found" check)

Add defense-in-depth normalization:
```python
def update_scheme(self, scheme_id: int, scheme_update: ClaimSchemeUpdate, company_id: int, user_id: int) -> ClaimScheme:
    db_scheme = self.repo.get(scheme_id, company_id)
    if not db_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Normalize 0 to None for optional integer fields (defense in depth)
    if scheme_update.trigger_product_id == 0:
        scheme_update.trigger_product_id = None
    if scheme_update.trigger_variant_id == 0:
        scheme_update.trigger_variant_id = None
    if scheme_update.free_product_id == 0:
        scheme_update.free_product_id = None
    if scheme_update.free_variant_id == 0:
        scheme_update.free_variant_id = None
    
    # ... rest of existing validation
```

---

### Phase 3: Data Cleanup

Run these SQL queries to fix any existing corrupted `0` values:
```sql
UPDATE inventory.claim_scheme
SET trigger_product_id = NULL
WHERE trigger_product_id = 0;

UPDATE inventory.claim_scheme
SET trigger_variant_id = NULL
WHERE trigger_variant_id = 0;

UPDATE inventory.claim_scheme
SET free_product_id = NULL
WHERE free_product_id = 0;

UPDATE inventory.claim_scheme
SET free_variant_id = NULL
WHERE free_variant_id = 0;
```

---

## Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `shoudagor_FE/src/pages/claims/SchemeForm.tsx` | Fix 1.1, 1.2, 1.3, 1.4 | HIGH |
| `shoudagor_FE/src/lib/api/claimsApi.ts` | Fix 1.5 | HIGH |
| `Shoudagor/app/services/claims/claim_service.py` | Fix 2.1 | MEDIUM |

---

## Test Cases

1. **Edit scheme name only** → Name should update, other fields unchanged
2. **Edit scheme dates** → Dates should update, other fields unchanged
3. **Edit scheme slabs** → Slabs should update correctly
4. **Edit scheme trigger product/variant** → New values should persist
5. **Clear trigger product/variant** → Should set to NULL, not 0
6. **Edit applicable_to** → Should update correctly (was broken due to uncontrolled Select)
7. **Toggle is_active** → Should update correctly

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Existing schemes corrupted with `0` values | High | High | Run data cleanup query (Phase 3) |
| Select component doesn't show initial value | Medium | Medium | Ensure `value` prop is properly set from form state |
| Backend validation rejects valid updates | Low | Medium | Test with all valid field combinations |
