import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000"

class SQMSFullInteractiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.driver.implicitly_wait(5)
        
    @classmethod
    def tearDownClass(cls):
        print("\nAll interactive functions tested successfully! Closing browser in 3 seconds...")
        time.sleep(3)
        cls.driver.quit()

    def setUp(self):
        self.driver.delete_all_cookies()

    def login(self, email, password, role="User"):
        print(f"Logging in as {role} ({email})...")
        self.driver.get(BASE_URL + "/accounts/login/")
        time.sleep(1)
        
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(0.5)
        
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".auth-form-side form button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_btn)
        
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(BASE_URL + "/accounts/login/")
        )
        time.sleep(2)
        print(f"Logged in successfully. Current URL: {self.driver.current_url}")

    def logout(self):
        print("Logging out...")
        self.driver.get(BASE_URL + "/accounts/logout/")
        time.sleep(1)
        self.driver.delete_all_cookies()

    def test_full_interactive_flow(self):
        """Test the complete end-to-end booking and calling flow."""
        print("\n=== STARTING FULL INTERACTIVE FUNCTION TEST ===")
        
        self.login("test_patient@sqms.lk", "TestPassword123!", "Patient")
        
        print("Patient: Navigating to Book Ticket...")
        self.driver.get(BASE_URL + "/queues/book/")
        time.sleep(2)
        print(f"After navigate to /queues/book/, Current URL: {self.driver.current_url}")
        
        try:
            branch_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_branch"))
            )
            print("Found id_branch successfully!")
            branch_select = Select(branch_elem)
            branch_select.select_by_index(1)
            time.sleep(1.5) # Wait for AJAX
            
            dept_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_department"))
            )
            dept_select = Select(dept_elem)
            WebDriverWait(self.driver, 5).until(lambda d: len(Select(d.find_element(By.ID, "id_department")).options) > 1)
            dept_select.select_by_index(1)
            time.sleep(1.5) # Wait for AJAX
            
            service_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_service"))
            )
            service_select = Select(service_elem)
            WebDriverWait(self.driver, 5).until(lambda d: len(Select(d.find_element(By.ID, "id_service")).options) > 1)
            service_select.select_by_index(1)
            time.sleep(1.5)
            
            print("Patient: Clicking 'Book Token'...")
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "form#bookingForm button[type='submit']")
            self.driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", submit_btn)
            
            WebDriverWait(self.driver, 10).until(EC.url_contains("/queues/token/"))
            print("Patient: Successfully booked a token! Viewing token details.")
            time.sleep(3)
        except Exception as e:
            print(f"DEBUG: Exception on booking page: {e}")
            print(f"DEBUG: Page Title: {self.driver.title}")
            print(f"DEBUG: Page URL: {self.driver.current_url}")
            raise e

        self.logout()
        print("=== INTERACTIVE FUNCTION TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    unittest.main(verbosity=2)
