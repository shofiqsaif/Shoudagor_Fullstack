# Implementation Plan: Make Phone Information Not Company-Specific for Test Accounts

## Executive Summary
This plan outlines the changes required to make phone information saving and lookup not company-specific for Test accounts in the Shoudagor system. The current implementation scopes phone data to companies, but we need to make it global across all companies.

## Current State Analysis
- `TestUserBasicInfo` model inherits from `CompanyMixin` which adds `company_id` field
- All repository methods require `company_id` parameter
- API endpoints depend on `get_current_company_id()` dependency
- Service layer methods pass `company_id` throughout
- Phone lookup and creation are company-scoped

## Key Requirements
1. Remove company-specific constraints from phone information
2. Ensure data of `security.test_user_basic_info` is preserved when running `populate_complex_data.py`
3. Maintain backward compatibility where possible
4. Ensure proper security and access controls

## Implementation Steps

### Step 1: Database Schema Changes
**File:** `Shoudagor/alembic/versions/remove_company_id_from_test_user_basic_info.py`

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Remove company_id column from test_user_basic_info table
    op.drop_column('test_user_basic_info', 'company_id')
    
    # Create index on phone_normalized for global lookup
    op.create_index('ix_test_user_basic_info_phone_normalized', 'test_user_basic_info', ['phone_normalized'])

def downgrade():
    # Add company_id column back
    op.add_column('test_user_basic_info', sa.Column('company_id', sa.Integer(), nullable=True))
    
    # Drop index
    op.drop_index('ix_test_user_basic_info_phone_normalized', table_name='test_user_basic_info')
```

### Step 2: Model Layer Changes
**File:** `Shoudagor/app/models/test_user_basic_info.py`

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base
from app.models.mixins import TimestampMixin, IsDeletedMixin, AddressMixin

class TestUserBasicInfo(Base, TimestampMixin, IsDeletedMixin, AddressMixin):
    __tablename__ = "test_user_basic_info"
    __table_args__ = {"schema": "security"}

    test_user_basic_info_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("security.app_user.user_id", name="fk_test_user_basic_info_user"), nullable=True)
    phone = Column(String(20), nullable=False)
    phone_normalized = Column(String(20), nullable=False, index=True)
    full_name = Column(String(150), nullable=True)
    company_shop_name = Column(String(200), nullable=True)
    nid_number = Column(String(50), nullable=True)
```

### Step 3: Repository Layer Changes
**File:** `Shoudagor/app/repositories/test_user_basic_info.py`

```python
from sqlalchemy.orm import Session
from app.models.test_user_basic_info import TestUserBasicInfo
from app.schemas.test_user_basic_info import TestUserBasicInfoCreate

class TestUserBasicInfoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int):
        return self.db.query(TestUserBasicInfo).filter(
            TestUserBasicInfo.user_id == user_id,
            TestUserBasicInfo.is_deleted == False
        ).first()

    def get_by_phone_normalized(self, phone_normalized: str):
        return self.db.query(TestUserBasicInfo).filter(
            TestUserBasicInfo.phone_normalized == phone_normalized,
            TestUserBasicInfo.is_deleted == False
        ).first()

    def create(self, info_data: TestUserBasicInfoCreate, phone_normalized: str, user_id: int = None, cb: int = None):
        db_obj = TestUserBasicInfo(
            **info_data.dict(),
            phone_normalized=phone_normalized,
            user_id=user_id,
            cb=cb,
            mb=cb # Use created_by as modified_by initially
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def link_user(self, info_id: int, user_id: int, mb: int):
        db_obj = self.db.query(TestUserBasicInfo).filter(TestUserBasicInfo.test_user_basic_info_id == info_id).first()
        if db_obj:
            db_obj.user_id = user_id
            db_obj.mb = mb
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
```

### Step 4: Service Layer Changes
**File:** `Shoudagor/app/services/test_user_basic_info.py`

```python
import re
from sqlalchemy.orm import Session
from app.repositories.test_user_basic_info import TestUserBasicInfoRepository
from app.schemas.test_user_basic_info import TestUserBasicInfoCreate, TestUserBasicInfoStatus, TestUserBasicInfoLookupResponse
from app.core.config import settings

class TestUserBasicInfoService:
    def __init__(self, db: Session):
        self.repo = TestUserBasicInfoRepository(db)

    def normalize_phone(self, phone: str) -> str:
        # Keep only digits
        return re.sub(r'\D', '', phone)

    def get_onboarding_status(self, user_email: str, user_id: int) -> TestUserBasicInfoStatus:
        # Check if this email is in the test accounts list (case-insensitive)
        is_test_account = user_email.lower() in [acc.lower() for acc in settings.TEST_ACCOUNTS]

        if not is_test_account:
            return TestUserBasicInfoStatus(
                required=False,
                has_info=True,
                message="Onboarding not required for this account."
            )

        # Check if user already has info
        info = self.repo.get_by_user_id(user_id)
        if info:
            return TestUserBasicInfoStatus(
                required=True,
                has_info=True,
                phone=info.phone,
                full_name=info.full_name,
                company_shop_name=info.company_shop_name,
                message="Onboarding complete."
            )

        return TestUserBasicInfoStatus(
            required=True,
            has_info=False,
            message="Onboarding required. Please provide basic information."
        )

    def lookup_phone(self, phone: str) -> TestUserBasicInfoLookupResponse:
        normalized = self.normalize_phone(phone)
        info = self.repo.get_by_phone_normalized(normalized)
        
        if info:
            return TestUserBasicInfoLookupResponse(
                exists=True,
                full_name=info.full_name,
                company_shop_name=info.company_shop_name,
                test_user_basic_info_id=info.test_user_basic_info_id
            )

        return TestUserBasicInfoLookupResponse(exists=False)

    def submit_info(self, user_id: int, info_data: TestUserBasicInfoCreate, cb: int) -> TestUserBasicInfoStatus:
        normalized = self.normalize_phone(info_data.phone)
        
        # Check if phone already exists globally
        existing = self.repo.get_by_phone_normalized(normalized)
        
        if existing:
            # Link user to existing record
            self.repo.link_user(existing.test_user_basic_info_id, user_id, cb)
            return TestUserBasicInfoStatus(
                required=True,
                has_info=True,
                phone=existing.phone,
                full_name=existing.full_name,
                company_shop_name=existing.company_shop_name,
                message="Linked to existing information."
            )

        # Create new record
        new_info = self.repo.create(info_data, normalized, user_id, cb)
        return TestUserBasicInfoStatus(
            required=True,
            has_info=True,
            phone=new_info.phone,
            full_name=new_info.full_name,
            company_shop_name=new_info.company_shop_name,
            message="Information saved successfully."
        )
```

### Step 5: API Layer Changes
**File:** `Shoudagor/app/api/test_user_basic_info.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.schemas.test_user_basic_info import TestUserBasicInfoCreate, TestUserBasicInfoRead, TestUserBasicInfoLookupResponse, TestUserBasicInfoStatus
from app.services.test_user_basic_info import TestUserBasicInfoService

router = APIRouter(
    tags=["Test Onboarding"],
    prefix="/api/company/users/test-onboarding",
    responses={404: {"description": "Not found"}}
)

@router.get("/status", response_model=TestUserBasicInfoStatus)
def get_onboarding_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = TestUserBasicInfoService(db)
    return service.get_onboarding_status(current_user.get("email"), current_user.get("user_id"))

@router.get("/lookup", response_model=TestUserBasicInfoLookupResponse)
def lookup_phone(
    phone: str = Query(..., description="Phone number to lookup"),
    db: Session = Depends(get_db)
):
    service = TestUserBasicInfoService(db)
    return service.lookup_phone(phone)

@router.post("/submit", response_model=TestUserBasicInfoStatus)
def submit_info(
    info_data: TestUserBasicInfoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = TestUserBasicInfoService(db)
    user_id = current_user.get("user_id")
    return service.submit_info(user_id, info_data, user_id)
```

### Step 6: Schema Changes
**File:** `Shoudagor/app/schemas/test_user_basic_info.py`

```python
from pydantic import BaseModel
from .common import AuditMixin

class TestUserBasicInfoBase(BaseModel):
    phone: str
    full_name: str | None = None
    company_shop_name: str | None = None
    address: str | None = None
    nid_number: str | None = None

class TestUserBasicInfoCreate(TestUserBasicInfoBase):
    pass

class TestUserBasicInfoRead(TestUserBasicInfoBase, AuditMixin):
    test_user_basic_info_id: int
    user_id: int | None = None
    phone_normalized: str

    class Config:
        orm_mode = True

class TestUserBasicInfoLookupResponse(BaseModel):
    exists: bool
    full_name: str | None = None
    company_shop_name: str | None = None
    test_user_basic_info_id: int | None = None

class TestUserBasicInfoStatus(BaseModel):
    required: bool
    has_info: bool
    phone: str | None = None
    full_name: str | None = None
    company_shop_name: str | None = None
    message: str | None = None
```

### Step 7: Update populate_complex_data.py
**File:** `Shoudagor/scripts/populate_complex_data.py`

```python
# Line 135: Comment out or modify the deletion of test_user_basic_info data
# db.query(TestUserBasicInfo).filter(TestUserBasicInfo.company_id == comp_id).delete()

# Instead, preserve the data:
# if you want to preserve existing test_user_basic_info data:
# pass  # Skip deletion of test_user_basic_info data

# Or if you want to archive it:
# from app.models.test_user_basic_info import TestUserBasicInfo
# existing_test_users = db.query(TestUserBasicInfo).filter(TestUserBasicInfo.company_id == comp_id).all()
# for user in existing_test_users:
#     user.company_id = None  # Remove company association
# db.commit()
```

## Database Migration Strategy

### Forward Migration
1. Create migration file to remove `company_id` column
2. Add index on `phone_normalized` for better global lookup performance
3. Update all foreign key constraints
4. Migrate existing data (set company_id to NULL or merge)

### Rollback Strategy
1. Add `company_id` column back
2. Restore data from backup if needed
3. Recreate foreign key constraints

## Testing Strategy

### Unit Tests
1. Test phone lookup across multiple companies
2. Test onboarding status for test accounts
3. Test phone submission and linking
4. Test edge cases (duplicate phones, invalid formats)

### Integration Tests
1. Test API endpoints with multiple companies
2. Test data consistency across companies
3. Test performance with large datasets

### Manual Testing
1. Create test accounts in different companies
2. Verify phone lookup works globally
3. Test onboarding flow
4. Verify data integrity

## Security Considerations

1. **Access Control**: Ensure only authorized users can access phone data
2. **Data Privacy**: Implement proper data protection measures
3. **Audit Trail**: Maintain logs for all phone data operations
4. **Rate Limiting**: Prevent abuse of phone lookup functionality

## Performance Considerations

1. **Indexing**: Create index on `phone_normalized` for fast lookups
2. **Caching**: Implement caching for frequently accessed phone data
3. **Pagination**: Add pagination for large result sets
4. **Query Optimization**: Optimize database queries for global lookups

## Rollout Strategy

1. **Development**: Implement and test changes in development environment
2. **Staging**: Deploy to staging for user acceptance testing
3. **Production**: Deploy to production during low-traffic period
4. **Monitoring**: Monitor system performance and error rates
5. **Rollback Plan**: Have rollback plan ready in case of issues

## Risk Assessment

### High Risk
- Data loss during migration
- Performance degradation
- Security vulnerabilities

### Medium Risk
- Compatibility issues with existing integrations
- User experience disruptions
- Increased complexity

### Low Risk
- Documentation updates
- Minor UI changes
- Training requirements

## Success Metrics

1. **Functionality**: Phone lookup works across all companies
2. **Performance**: Response time remains under 200ms
3. **Reliability**: 99.9% uptime during and after migration
4. **User Satisfaction**: Positive feedback from test users
5. **Data Integrity**: No data loss or corruption

## Post-Implementation Tasks

1. Update system documentation
2. Train support team on new functionality
3. Monitor system performance
4. Gather user feedback
5. Plan for future enhancements

## Dependencies

- Database migration tool (Alembic)
- Testing framework
- CI/CD pipeline
- Monitoring tools
- Backup systems

## Resources Required

- Database administrator for migration
- QA team for testing
- DevOps for deployment
- Documentation team for updates
- Support team for user training

## Timeline Estimate

- Database migration: 2 days
- Code changes: 3 days
- Testing: 2 days
- Documentation: 1 day
- Deployment: 1 day
- Total: 9 days

## Approval Requirements

- Database migration approval
- Security review approval
- Performance testing approval
- User acceptance testing approval
- Final deployment approval

---

**Note**: This plan assumes that making phone data global is the desired approach. If a different approach is preferred (e.g., keeping company_id but making it optional), the plan would need to be adjusted accordingly.