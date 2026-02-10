import pytest
from playwright_lib import ShoudagorBrowser

@pytest.fixture
def browser():
    # Setup
    sb = ShoudagorBrowser(headless=True) # Usually run headless for reporting
    yield sb
    # Teardown
    sb.close()

def test_admin_login(browser):
    """Test login with admin credentials"""
    page = browser.login(email="admin@myapp.com", password="123456")
    
    # Assertions make the report meaningful
    assert "/dashboard" in page.url
    print("Assertion passed: User is on dashboard")
    
    # Wait for demo purposes
    browser.wait(1)

def test_invalid_login(browser):
    """Test login with wrong credentials (expected to fail dashboard redirect)"""
    # Note: We don't use the library's login method here directly if we want to test failure 
    # because it has a wait_for_url that will throw.
    page = browser.page
    page.goto("http://localhost:5173/")
    page.fill("#email", "wrong@user.com")
    page.fill("#password", "wrongpass")
    page.click('button[type="submit"]')
    
    # Verify we are NOT on dashboard
    assert "/dashboard" not in page.url
    print("Assertion passed: Invalid user blocked")
