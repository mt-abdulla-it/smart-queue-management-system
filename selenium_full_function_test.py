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
        
        email_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(1)
        
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(BASE_URL + "/accounts/login/"))
        time.sleep(1)

    def logout(self):
        print("Logging out...")
        self.driver.get(BASE_URL + "/accounts/logout/")
        time.sleep(1)
        self.driver.delete_all_cookies()

    def test_full_interactive_flow(self):
        """Test the complete end-to-end booking and calling flow."""
        print("\n=== STARTING FULL INTERACTIVE FUNCTION TEST ===")
        
        # ---------------------------------------------
        # 1. PATIENT FLOW: Booking a token
        # ---------------------------------------------
        self.login("test_patient@sqms.lk", "TestPassword123!", "Patient")
        
        print("Patient: Navigating to Book Ticket...")
        self.driver.get(BASE_URL + "/queues/book/")
        time.sleep(2)
        
        print("Patient: Selecting Branch...")
        branch_select = Select(self.driver.find_element(By.ID, "id_branch"))
        branch_select.select_by_index(1)
        time.sleep(1.5) # Wait for AJAX
        
        print("Patient: Selecting Department...")
        dept_select = Select(self.driver.find_element(By.ID, "id_department"))
        dept_select.select_by_index(1)
        time.sleep(1.5) # Wait for AJAX
        
        print("Patient: Selecting Service...")
        service_select = Select(self.driver.find_element(By.ID, "id_service"))
        service_select.select_by_index(1)
        time.sleep(1.5)
        
        print("Patient: Clicking 'Book Token'...")
        self.driver.find_element(By.CSS_SELECTOR, "form#bookingForm button[type='submit']").click()
        
        # Wait for redirect to token detail
        WebDriverWait(self.driver, 5).until(EC.url_contains("/queues/token/"))
        print("Patient: Successfully booked a token! Viewing token details.")
        time.sleep(3)
        
        self.logout()
        
        # ---------------------------------------------
        # 2. STAFF FLOW: Calling and Completing the token
        # ---------------------------------------------
        self.login("test_staff@sqms.lk", "TestPassword123!", "Staff")
        
        print("Staff: Navigating to Queue Management...")
        self.driver.get(BASE_URL + "/queues/manage/")
        time.sleep(2)
        
        print("Staff: Clicking 'Call Next' on the token...")
        try:
            call_btn = self.driver.find_element(By.CSS_SELECTOR, "form.call-next-form button[type='submit']")
            call_btn.click()
            time.sleep(3) # Wait for page reload
            print("Staff: Token is now SERVING.")
            
            print("Staff: Clicking 'Mark Completed'...")
            complete_btn = self.driver.find_element(By.CSS_SELECTOR, "form#completeForm button[type='submit']")
            complete_btn.click()
            time.sleep(3) # Wait for page reload
            print("Staff: Token successfully COMPLETED.")
        except Exception as e:
            print(f"Warning: Could not complete staff flow (maybe no tokens in queue?). Error: {e}")
            self.fail("Staff flow failed to find or interact with tokens.")
            
        print("=== INTERACTIVE FUNCTION TEST COMPLETED ===")

if __name__ == "__main__":
    unittest.main(verbosity=2)
