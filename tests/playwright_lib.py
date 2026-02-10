from playwright.sync_api import sync_playwright, Page, Browser
import time
from typing import Optional

class ShoudagorBrowser:
    def __init__(self, headless: bool = False):
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page: Page = self.context.new_page()

    def login(self, email: str = "admin@myapp.com", password: str = "123456", url: str = "http://localhost:5173/"):
        """
        Automates login process.
        """
        print(f"Navigating to {url}...")
        self.page.goto(url)

        print(f"Logging in as {email}...")
        self.page.fill("#email", email)
        self.page.fill("#password", password)
        self.page.click('button[type="submit"]')

        # Wait for navigation to dashboard
        self.page.wait_for_url("**/dashboard**", timeout=10000)
        print("Login successful.")
        return self.page

    def wait(self, seconds: int = 2):
        print(f"Waiting for {seconds} seconds...")
        time.sleep(seconds)

    def close(self):
        print("Closing browser...")
        self.browser.close()
        self.playwright.stop()

def perform_login(email: str = "admin@myapp.com", password: str = "123456", wait_time: int = 2):
    """
    Functional wrapper for a quick login session.
    """
    sb = ShoudagorBrowser()
    try:
        sb.login(email, password)
        sb.wait(wait_time)
        return sb.page
    finally:
        sb.close()
