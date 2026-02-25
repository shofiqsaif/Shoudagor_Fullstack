# SR Order Consolidation: Individual Details Preservation Implementation Plan

## Executive Summary

**Problem**: Current SR order consolidation aggregates same product variants from multiple SR orders into single line items, losing individual SR order details.

**Solution**: Modify consolidation logic to preserve individual SR order details for same product variants, creating separate line items in consolidated orders.

**Impact**: Enables traceability of each consolidated item back to its original SR order, maintaining SR-level accountability and commission tracking.

---

## Current System Analysis

### Existing Data Flow
1. Multiple SR orders for same customer are selected for consolidation
2. System validates orders and checks stock availability
3. **Current Aggregation Logic**: Groups by `(product_id, variant_id)` tuple
4. Creates single SalesOrder with aggregated quantities
5. SR orders marked as 'consolidated'

### Current Issue Example
- **SR Order 1**: Product A (Variant X) - 10 units @ $100
- **SR Order 2**: Product A (Variant X) - 5 units @ $110
- **Current Result**: 15 units @ $105 (average) as single line item
- **Desired Result**: Two separate line items preserving individual SR details

---

## Technical Requirements

### 1. Database Schema Changes

#### 1.1 SalesOrderDetail Model Enhancement
**Current Structure**:
```python
class SalesOrderDetail(OrderDetailBase):
    sr_order_detail_id = Column(Integer, ForeignKey("sales.sr_order_detail.sr_order_detail_id"), nullable=True)
```

**Proposed Changes**:
```python
class SalesOrderDetail(OrderDetailBase):
    # Keep for backward compatibility (first SR detail)
    sr_order_detail_id = Column(Integer, ForeignKey("sales.sr_order_detail.sr_order_detail_id"), nullable=True)
    
    # New fields for multiple SR details
    sr_order_detail_ids = Column(JSON, nullable=True)  # Array of sr_order_detail_id references
    sr_details = Column(JSON, nullable=True)  # Structured SR data
```

**JSON Structure for `sr_details`**:
```json
[
  {
    "sr_order_detail_id": 123,
    "sr_id": 456,
    "sr_name": "John Doe",
    "sr_order_id": 789,
    "sr_order_number": "SR-001",
    "quantity": 10.0,
    "negotiated_price": 100.00,
    "sale_price": 95.00,
    "price_adjustment": 50.00
  }
]
```

#### 1.2 Alternative: Junction Table Approach
```python
class SalesOrderDetail_SR_Order_Detail(Base, TimestampMixin):
    __tablename__ = "sales_order_detail_sr_order_detail"
    __table_args__ = {"schema": "sales"}
    
    id = Column(Integer, primary_key=True, index=True)
    sales_order_detail_id = Column(Integer, ForeignKey("sales.sales_order_detail.sales_order_detail_id"))
    sr_order_detail_id = Column(Integer, ForeignKey("sales.sr_order_detail.sr_order_detail_id"))
    quantity = Column(Numeric(18, 4), nullable=False)
    negotiated_price = Column(Numeric(18, 4), nullable=False)
    sale_price = Column(Numeric(18, 4), nullable=True)
    price_adjustment = Column(Numeric(18, 4), nullable=True)
```

**Recommendation**: Use JSON column approach for Phase 1, consider junction table for Phase 2 if query performance becomes an issue.

### 2. Backend Service Changes

#### 2.1 ConsolidationService.py - Core Logic Update

**Current `calculate_consolidated_details()` Method** (lines 175-220):
- Groups by `product_key = f"{detail.product_id}_{detail.variant_id or 'base'}"`
- Aggregates quantities, calculates average price
- Creates single entry per product+variant

**New Implementation**:
```python
def calculate_consolidated_details(self, sr_orders: List[SR_Order], final_prices: Optional[Dict[str, float]] = None):
    """
    Calculate consolidated order details WITHOUT aggregating same product variants
    from different SR orders. Each SR order detail becomes separate line item.
    """
    consolidated_details = []
    total_price_adjustment = Decimal(0)
    
    for sr_order in sr_orders:
        for detail in sr_order.details:
            product_key = f"{detail.product_id}_{detail.variant_id or 'base'}"
            
            # Apply final price adjustment if provided
            if final_prices and product_key in final_prices:
                final_price = Decimal(str(final_prices[product_key]))
                price_adjustment = (final_price - detail.negotiated_price) * detail.quantity
            else:
                final_price = detail.negotiated_price
                price_adjustment = Decimal(0)
            
            total_price_adjustment += price_adjustment
            
            consolidated_details.append({
                'product_id': detail.product_id,
                'variant_id': detail.variant_id,
                'unit_of_measure_id': detail.unit_of_measure_id,
                'quantity': float(detail.quantity),
                'unit_price': float(final_price),
                'sr_order_detail_id': detail.sr_order_detail_id,  # First/primary SR detail
                'sr_order_detail_ids': [detail.sr_order_detail_id],  # Array for multiple
                'sr_id': sr_order.sr_id,
                'sr_name': sr_order.sales_representative.sr_name,
                'sr_order_id': sr_order.sr_order_id,
                'sr_order_number': sr_order.order_number,
                'negotiated_price': float(detail.negotiated_price),
                'sale_price': float(detail.sale_price) if detail.sale_price else None,
                'price_adjustment': float(price_adjustment),
                'sr_details': [{
                    'sr_order_detail_id': detail.sr_order_detail_id,
                    'sr_id': sr_order.sr_id,
                    'sr_name': sr_order.sales_representative.sr_name,
                    'sr_order_id': sr_order.sr_order_id,
                    'sr_order_number': sr_order.order_number,
                    'quantity': float(detail.quantity),
                    'negotiated_price': float(detail.negotiated_price),
                    'sale_price': float(detail.sale_price) if detail.sale_price else None,
                    'price_adjustment': float(price_adjustment)
                }]
            })
    
    return {
        'details': consolidated_details,
        'total_price_adjustment': total_price_adjustment
    }
```

#### 2.2 SalesOrderService.py Updates
Modify `create_sales_order_detail()` to:
1. Set `sr_order_detail_id` to first SR detail (backward compatibility)
2. Populate `sr_order_detail_ids` array
3. Store `sr_details` JSON structure
4. Validate that sum of SR quantities equals line item quantity

#### 2.3 API Schema Updates
**Current Schema** (`shoudagor_FE/src/lib/schema/sales.ts`):
```typescript
sr_order_detail_id: z.number()
```

**Updated Schema**:
```typescript
sr_order_detail_id: z.number().optional(),  // Backward compatibility
sr_order_detail_ids: z.array(z.number()).optional(),
sr_details: z.array(z.object({
    sr_order_detail_id: z.number(),
    sr_id: z.number(),
    sr_name: z.string(),
    sr_order_id: z.number(),
    sr_order_number: z.string(),
    quantity: z.number(),
    negotiated_price: z.number(),
    sale_price: z.number().optional(),
    price_adjustment: z.number().optional()
})).optional()
```

### 3. Frontend Changes

#### 3.1 ViewConsolidatedSROrderDetails.tsx
**Current Display**: Aggregated items table
**New Display**: Individual SR order details with grouping

**Proposed Table Structure**:
```typescript
// Group by product+variant for readability, expand to show SR details
const groupedDetails = groupBy(order.details, item => 
    `${item.product_id}_${item.variant_id}`
);

// Table columns
const columns = [
    { header: "Product", accessor: "product_name" },
    { header: "Variant", accessor: "variant_name" },
    { header: "Total Qty", accessor: "total_quantity" },
    { header: "SR Count", accessor: "sr_count" },
    { header: "Actions", accessor: "actions" } // Expand/collapse
];

// Expanded view for each product+variant
const srDetailColumns = [
    { header: "SR Name", accessor: "sr_name" },
    { header: "SR Order #", accessor: "sr_order_number" },
    { header: "Quantity", accessor: "quantity" },
    { header: "Negotiated Price", accessor: "negotiated_price" },
    { header: "Final Price", accessor: "unit_price" },
    { header: "Price Adjustment", accessor: "price_adjustment" }
];
```

#### 3.2 UnconsolidatedSROrders.tsx
Add validation preview showing:
- Number of line items that will be created
- Warning for duplicate product+variant across SR orders
- Toggle between aggregated vs individual view preview

#### 3.3 New Component: ConsolidatedOrderSRDetails.tsx
Create reusable component to display SR details for a consolidated order item.

### 4. Database Migration Plan

#### 4.1 Alembic Migration Script
```python
# Migration: add_sr_details_to_sales_order_detail.py

def upgrade():
    # Add new columns
    op.add_column('sales_order_detail', 
        sa.Column('sr_order_detail_ids', sa.JSON(), nullable=True),
        schema='sales'
    )
    op.add_column('sales_order_detail',
        sa.Column('sr_details', sa.JSON(), nullable=True),
        schema='sales'
    )
    
    # Migrate existing data
    connection = op.get_bind()
    
    # For consolidated orders (is_consolidated = true)
    consolidated_details = connection.execute("""
        SELECT sales_order_detail_id, sr_order_detail_id 
        FROM sales.sales_order_detail 
        WHERE sr_order_detail_id IS NOT NULL
    """).fetchall()
    
    for detail in consolidated_details:
        sr_order_detail_id = detail.sr_order_detail_id
        if sr_order_detail_id:
            # Get SR details from sr_order_detail
            sr_detail = connection.execute("""
                SELECT sod.sr_order_detail_id, so.sr_id, sr.sr_name,
                       so.sr_order_id, so.order_number as sr_order_number,
                       sod.quantity, sod.negotiated_price, sod.sale_price
                FROM sales.sr_order_detail sod
                JOIN sales.sr_order so ON sod.sr_order_id = so.sr_order_id
                JOIN sales.sales_representative sr ON so.sr_id = sr.sr_id
                WHERE sod.sr_order_detail_id = %s
            """, (sr_order_detail_id,)).fetchone()
            
            if sr_detail:
                sr_details = [{
                    'sr_order_detail_id': sr_detail.sr_order_detail_id,
                    'sr_id': sr_detail.sr_id,
                    'sr_name': sr_detail.sr_name,
                    'sr_order_id': sr_detail.sr_order_id,
                    'sr_order_number': sr_detail.sr_order_number,
                    'quantity': float(sr_detail.quantity),
                    'negotiated_price': float(sr_detail.negotiated_price),
                    'sale_price': float(sr_detail.sale_price) if sr_detail.sale_price else None
                }]
                
                connection.execute("""
                    UPDATE sales.sales_order_detail 
                    SET sr_order_detail_ids = %s, sr_details = %s
                    WHERE sales_order_detail_id = %s
                """, ([sr_order_detail_id], sr_details, detail.sales_order_detail_id))

def downgrade():
    # Backup data if needed
    op.drop_column('sales_order_detail', 'sr_details', schema='sales')
    op.drop_column('sales_order_detail', 'sr_order_detail_ids', schema='sales')
```

#### 4.2 Data Validation Script
Create script to validate migrated data:
1. Check that all consolidated orders have `sr_details` populated
2. Verify `sr_order_detail_ids` array matches `sr_details` structure
3. Validate quantity sums match
4. Generate migration report

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Objective**: Database changes and backward-compatible updates

**Tasks**:
1. Create database migration script
2. Update SalesOrderDetail model
3. Update Pydantic schemas
4. Update TypeScript schemas
5. Deploy migration to development environment
6. Test data migration

**Deliverables**:
- Database migration script
- Updated models and schemas
- Data migration validation report

### Phase 2: Backend Logic (Week 3-4)
**Objective**: Update consolidation logic to preserve individual details

**Tasks**:
1. Modify `ConsolidationService.calculate_consolidated_details()`
2. Update `SalesOrderService.create_sales_order_detail()`
3. Update repository methods
4. Add unit tests for new logic
5. Update API response structures
6. Add feature flag for new behavior

**Deliverables**:
- Updated consolidation service
- Comprehensive unit tests
- Feature flag implementation
- Updated API documentation

### Phase 3: Frontend Updates (Week 5-6)
**Objective**: Update UI to display individual SR details

**Tasks**:
1. Update `ViewConsolidatedSROrderDetails.tsx`
2. Update `UnconsolidatedSROrders.tsx` validation preview
3. Create `ConsolidatedOrderSRDetails.tsx` component
4. Update any other components displaying consolidated orders
5. Add toggle between aggregated/individual views
6. Update TypeScript types and interfaces

**Deliverables**:
- Updated frontend components
- New reusable components
- Updated TypeScript definitions
- UI/UX testing results

### Phase 4: Testing & Deployment (Week 7-8)
**Objective**: Thorough testing and production deployment

**Tasks**:
1. End-to-end testing with existing data
2. Performance testing with large consolidations
3. User acceptance testing
4. Update documentation
5. Deploy to staging environment
6. Production deployment with feature flag
7. Monitor and address issues
8. Remove feature flag after validation

**Deliverables**:
- Test reports
- Updated documentation
- Production deployment
- Monitoring dashboard

---

## Risk Assessment & Mitigation

### High Risk Areas

#### 1. Data Migration Issues
**Risk**: Data corruption during migration
**Mitigation**:
- Full database backup before migration
- Run migration on copy first
- Validation scripts to check data integrity
- Rollback plan with backup restoration

#### 2. Performance Degradation
**Risk**: Increased query time for consolidated orders
**Mitigation**:
- Add indexes on new JSON columns
- Implement pagination for details view
- Cache frequently accessed data
- Monitor query performance

#### 3. Commission Calculation Errors
**Risk**: SR commissions calculated incorrectly
**Mitigation**:
- Parallel calculation with old/new logic
- Validation scripts for commission amounts
- Audit trail for commission changes
- Manual review of first few consolidations

#### 4. Frontend Display Issues
**Risk**: UI becomes cluttered with many line items
**Mitigation**:
- Implement expand/collapse grouping
- Add pagination for details
- Provide aggregated summary view
- User testing for usability

### Medium Risk Areas

#### 1. Backward Compatibility
**Risk**: Existing integrations break
**Mitigation**:
- Keep `sr_order_detail_id` field
- API versioning
- Feature flag for new behavior
- Comprehensive integration tests

#### 2. Stock Management
**Risk**: Stock allocation logic affected
**Mitigation**:
- Review and update stock allocation logic
- Test with various scenarios
- Add validation for stock availability per SR detail

### Low Risk Areas

#### 1. Reporting Updates
**Risk**: Reports show incorrect data
**Mitigation**:
- Update report queries gradually
- Add report versioning
- Notify users of changes

---

## Success Criteria

### Technical Success Criteria
1. **Data Integrity**: 100% of SR order details preserved in consolidated orders
2. **Performance**: < 2x increase in consolidation processing time
3. **Backward Compatibility**: Existing API endpoints continue to work
4. **Migration Success**: 100% of existing consolidated orders migrated correctly

### Business Success Criteria
1. **Traceability**: Users can trace each consolidated item to original SR order
2. **Commission Accuracy**: SR commissions calculated correctly for new structure
3. **User Satisfaction**: Users find new display more informative and usable
4. **Adoption Rate**: > 90% of new consolidations use individual details feature

### Quality Metrics
1. **Test Coverage**: > 80% for new code
2. **Bug Rate**: < 5 critical bugs post-deployment
3. **Performance**: Page load time < 3 seconds for consolidated order view
4. **Data Validation**: 100% of migrated data passes validation checks

---

## Rollback Plan

### Scenario 1: Critical Bug in Production
**Actions**:
1. Disable feature flag immediately
2. Revert to old consolidation logic
3. Investigate and fix issue
4. Re-deploy with fix

### Scenario 2: Performance Issues
**Actions**:
1. Enable performance optimizations
2. Add caching layer
3. Implement pagination if not already done
4. Monitor and tune database queries

### Scenario 3: Data Corruption
**Actions**:
1. Restore from backup
2. Disable feature
3. Investigate root cause
4. Fix migration script
5. Re-run migration on test environment

### Rollback Checklist
- [ ] Feature flag control available
- [ ] Database backup available
- [ ] Old code preserved in version control
- [ ] Rollback deployment script ready
- [ ] Team trained on rollback procedure

---

## Resource Requirements

### Development Team
- **Backend Developer**: 2 weeks (Phases 1-2)
- **Frontend Developer**: 2 weeks (Phase 3)
- **Database Administrator**: 1 week (Phase 1, 4)
- **QA Engineer**: 2 weeks (Phase 4)
- **Project Manager**: Ongoing coordination

### Infrastructure
- **Development Environment**: Existing
- **Staging Environment**: For testing
- **Database Resources**: Additional storage for JSON data
- **Monitoring Tools**: Performance monitoring setup

### Timeline
- **Total Duration**: 8 weeks
- **Start Date**: [To be determined]
- **Phase Completion**: Every 2 weeks
- **Go-Live**: Week 8

---

## Appendix

### A. Database Schema Changes Details

#### Current Schema
```sql
CREATE TABLE sales.sales_order_detail (
    sales_order_detail_id SERIAL PRIMARY KEY,
    sales_order_id INTEGER REFERENCES sales.sales_order(sales_order_id),
    product_id INTEGER NOT NULL,
    variant_id INTEGER,
    unit_of_measure_id INTEGER NOT NULL,
    quantity NUMERIC(18,4) NOT NULL,
    unit_price NUMERIC(18,4) NOT NULL,
    sr_order_detail_id INTEGER REFERENCES sales.sr_order_detail(sr_order_detail_id),
    -- ... other columns
);
```

#### New Schema
```sql
ALTER TABLE sales.sales_order_detail 
ADD COLUMN sr_order_detail_ids JSONB,
ADD COLUMN sr_details JSONB;

-- Create index for JSON querying
CREATE INDEX idx_sales_order_detail_sr_details 
ON sales.sales_order_detail USING GIN (sr_details);

-- Create index for array queries
CREATE INDEX idx_sales_order_detail_sr_detail_ids 
ON sales.sales_order_detail USING GIN (sr_order_detail_ids);
```

### B. API Endpoint Changes

#### Existing Endpoints (No Change)
- `POST /api/company/sales/consolidation/`
- `GET /api/company/sales/consolidation/sr-consolidated-orders`
- `GET /api/company/sales/consolidation/sr-consolidated-orders/{sales_order_id}`

#### New Optional Parameters
```typescript
// Consolidation request with option for individual details
interface ConsolidationRequest {
    sr_order_ids: number[];
    location_id: number;
    expected_shipment_date?: string;
    consolidation_notes?: string;
    preserve_individual_details?: boolean;  // New parameter
    final_prices?: Record<string, number>;
}
```

### C. Testing Strategy

#### Unit Tests
1. **ConsolidationService Tests**
   - Test individual details preservation
   - Test price adjustment calculations
   - Test backward compatibility

2. **SalesOrderService Tests**
   - Test SalesOrderDetail creation with SR details
   - Test data validation
   - Test error handling

3. **Repository Tests**
   - Test JSON column queries
   - Test data retrieval with SR details

#### Integration Tests
1. **End-to-End Consolidation Flow**
   - Create SR orders
   - Consolidate with individual details
   - Verify data preservation
   - Verify commission calculations

2. **API Tests**
   - Test all consolidation endpoints
   - Test error responses
   - Test performance with large data sets

#### Performance Tests
1. **Load Testing**
   - Consolidate 100+ SR orders
   - Measure response times
   - Monitor memory usage

2. **Database Performance**
   - Query performance with JSON columns
   - Index effectiveness
   - Migration performance

### D. Documentation Updates

#### Technical Documentation
1. **Database Schema**: Update ER diagrams
2. **API Documentation**: Update OpenAPI specs
3. **Code Documentation**: Update docstrings and comments

#### User Documentation
1. **User Guide**: How to use individual details feature
2. **Admin Guide**: How to manage and monitor
3. **Troubleshooting Guide**: Common issues and solutions

#### Operational Documentation
1. **Deployment Guide**: Step-by-step deployment instructions
2. **Monitoring Guide**: What to monitor and alert on
3. **Rollback Guide**: Rollback procedures

---

## Conclusion

This implementation plan provides a comprehensive approach to preserving individual SR order details during consolidation. The phased approach ensures minimal disruption, maintains backward compatibility, and allows for thorough testing at each stage.

The key benefits of this implementation are:
1. **Enhanced Traceability**: Complete audit trail from consolidated items to original SR orders
2. **Improved Accountability**: Clear attribution of sales to individual SRs
3. **Accurate Commission Tracking**: Precise commission calculations based on actual SR contributions
4. **Better Decision Making**: Data visibility for sales analysis and performance tracking

By following this plan, we can successfully implement the requested feature while maintaining system stability and data integrity.