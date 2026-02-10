from playwright_lib import ShoudagorBrowser

def main():
    # Initialize our library
    sb = ShoudagorBrowser(headless=False)
    
    try:
        # Perform login
        page = sb.login(email="admin@myapp.com", password="123456")
        
        # We are now at the dashboard
        print(f"Current Dashboard URL: {page.url}")
        
        # Demonstrate accessibility by waiting
        sb.wait(2)
        
        # Example: Navigate to products if login was successful
        # page.click('text="Products"')
        # sb.wait(1)
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Clean up
        sb.close()

if __name__ == "__main__":
    main()
