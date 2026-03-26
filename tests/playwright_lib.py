from playwright.sync_api import sync_playwright, Page, Browser
import time
from typing import Optional, Union
import os


class ShoudagorBrowser:
    def __init__(self, headless: bool = False):
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page: Page = self.context.new_page()

    def login(
        self,
        email: str = "admin@complex.com",
        password: str = "1234",
        url: str = "http://192.168.1.7:5173/login",
    ):
        """
        Automates login process.
        """
        print(f"Navigating to {url}...")
        self.page.goto(url)

        print(f"Logging in as {email}...")
        # Updated selectors based on observed UI (2026-03-24)
        self.page.fill('input[placeholder*="admin"]', email)
        self.page.fill('input[placeholder*="********"]', password)
        self.page.click('button:has-text("Login")')

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

    def fill_number_input(
        self, placeholder: str, value: Union[str, int, float], index: int = 0
    ) -> bool:
        """
        Fill a number input field by placeholder text.

        Args:
            placeholder: The placeholder text of the input field (e.g., "0" for quantity, "0.00" for unit price)
            value: The value to fill
            index: Which input to select if multiple have the same placeholder (0-based)

        Returns:
            True if successful, False if element not found
        """
        try:
            selector = f'input[placeholder="{placeholder}"]'
            element = self.page.locator(selector).nth(index)
            if element.is_visible(timeout=2000):
                element.fill(str(value))
                print(
                    f"OK: Filled input with placeholder '{placeholder}' with value '{value}'"
                )
                return True
            else:
                print(f"WARNING: Input with placeholder '{placeholder}' not visible")
                return False
        except Exception as e:
            print(f"ERROR: Could not fill input with placeholder '{placeholder}': {e}")
            return False

    def select_dropdown_option(
        self, input_placeholder: str, option_text: str, type_text: Optional[str] = None
    ) -> bool:
        """
        Select an option from a SearchableSelect dropdown.

        Args:
            input_placeholder: The placeholder text of the dropdown input (e.g., "Select a location")
            option_text: The text of the option to select (e.g., "Bulk Storage")
            type_text: Optional text to type in the search box to filter (defaults to option_text)

        Returns:
            True if successful, False if element not found
        """
        try:
            # Find and click the dropdown input
            dropdown_input = self.page.locator(
                f'input[placeholder="{input_placeholder}"]'
            )
            if not dropdown_input.is_visible(timeout=2000):
                print(
                    f"ERROR: Dropdown input with placeholder '{input_placeholder}' not found"
                )
                return False

            dropdown_input.click()
            time.sleep(0.5)  # Wait for dropdown to appear

            # Type to filter if needed
            if type_text is None:
                type_text = option_text
            self.page.keyboard.type(type_text)
            time.sleep(0.5)  # Wait for filtering

            # Select the option - try different selectors
            # First try cmdk-item (from cmdk library used by SearchableSelect)
            cmdk_item = self.page.locator(f'[cmdk-item]:has-text("{option_text}")')
            if cmdk_item.count() > 0:
                cmdk_item.first.click()
                print(f"OK: Selected option '{option_text}' from dropdown")
                return True

            # Try div with role option
            option = self.page.locator(f'div[role="option"]:has-text("{option_text}")')
            if option.count() > 0:
                option.first.click()
                print(f"OK: Selected option '{option_text}' from dropdown")
                return True

            # Try li element
            option = self.page.locator(f'li:has-text("{option_text}")')
            if option.count() > 0:
                option.first.click()
                print(f"OK: Selected option '{option_text}' from dropdown")
                return True

            # Try exact text match
            option = self.page.get_by_text(option_text, exact=True)
            if option.count() > 0:
                option.first.click()
                print(f"OK: Selected option '{option_text}' from dropdown")
                return True

            print(f"ERROR: Could not find option '{option_text}' in dropdown")
            return False

        except Exception as e:
            print(f"ERROR: Could not select option '{option_text}' from dropdown: {e}")
            return False

    def click_submit_button(
        self, button_text: str = "Create Purchase", wait_for_valid: bool = True
    ) -> bool:
        """
        Click a submit button, optionally waiting for it to be enabled.

        Args:
            button_text: The text on the button (e.g., "Create Purchase", "Submit")
            wait_for_valid: Whether to wait for the button to be enabled (not disabled)

        Returns:
            True if successful, False if button not found or disabled
        """
        try:
            button = self.page.locator(f'button:has-text("{button_text}")').first

            if wait_for_valid:
                # Wait for button to be enabled (not disabled)
                # React Hook Form validates asynchronously, so we may need to wait
                print(f"Waiting for button '{button_text}' to be enabled...")
                for attempt in range(10):  # Try for up to 10 seconds
                    try:
                        if button.is_visible(timeout=1000) and not button.is_disabled():
                            print(f"OK: Button '{button_text}' is enabled")
                            break
                        else:
                            if attempt % 3 == 0:  # Print every 3 seconds
                                print(
                                    f"  Button still disabled, waiting... (attempt {attempt + 1}/10)"
                                )
                            time.sleep(1)
                    except Exception:
                        time.sleep(1)

                # Check final state
                if button.is_disabled():
                    print(
                        f"WARNING: Button '{button_text}' is still disabled after waiting"
                    )

            # Try to click the button
            if button.is_visible(timeout=2000):
                button.click()
                print(f"OK: Clicked button '{button_text}'")
                return True
            else:
                print(f"ERROR: Button '{button_text}' not visible")
                return False

        except Exception as e:
            print(f"ERROR: Could not click button '{button_text}': {e}")
            return False

    def save_debug_info(self, prefix: str = "debug"):
        """
        Save screenshot and HTML dump for debugging.

        Args:
            prefix: Prefix for the debug files
        """
        try:
            # Save screenshot
            screenshot_path = f"{prefix}_screenshot.png"
            self.page.screenshot(path=screenshot_path)
            print(f"DEBUG: Screenshot saved as {screenshot_path}")

            # Save HTML dump
            html_path = f"{prefix}_page.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.page.content())
            print(f"DEBUG: HTML saved as {html_path}")

        except Exception as e:
            print(f"WARNING: Could not save debug info: {e}")


def perform_login(
    email: str = "admin@complex.com", password: str = "1234", wait_time: int = 2
):
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
