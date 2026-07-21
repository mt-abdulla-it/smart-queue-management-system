import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000"

class SQMSEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        # Removed --headless so the browser will visibly open on the user's screen
        chrome_options.add_argument("--window-size=1280,720")
        
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.driver.implicitly_wait(5)
        
    @classmethod
    def tearDownClass(cls):
        print("Tests completed! Closing browser in 3 seconds...")
        time.sleep(3)
        cls.driver.quit()

    def setUp(self):
        # Clear cookies before each test to ensure a clean session
        self.driver.delete_all_cookies()

    def test_01_public_pages(self):
        """Test that public pages load correctly without authentication."""
        print("\n--- Testing Public Pages ---")
        
        # Home Page
        print("Opening Home Page...")
        self.driver.get(BASE_URL + "/")
        time.sleep(2)  # Pause to let user see
        self.assertIn("Smart Queue", self.driver.title)
        
        # Live Display
        print("Opening Live Display...")
        self.driver.get(BASE_URL + "/queues/live/")
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)  # Pause to let user see the live display board
        self.assertIn("Live", self.driver.title)

    def login(self, email, password):
        """Helper method to log in."""
        self.driver.get(BASE_URL + "/accounts/login/")
        time.sleep(1) # Pause at login screen
        
        email_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.clear()
        for char in email:
            email_input.send_keys(char)
            time.sleep(0.05)
            
        password_input.clear()
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.05)
            
        time.sleep(1) # Pause before clicking submit
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        
        # Wait until we are redirected off the login page
        WebDriverWait(self.driver, 5).until(
            EC.url_changes(BASE_URL + "/accounts/login/")
        )
        time.sleep(2) # Pause at dashboard after login

    def test_02_patient_flow(self):
        """Test the workflow for a Patient user."""
        print("\n--- Testing Patient Flow ---")
        self.login("test_patient@sqms.lk", "TestPassword123!")
        
        # Go to Book Token page
        print("Opening 'Book Ticket' interface...")
        self.driver.get(BASE_URL + "/queues/book/")
        time.sleep(3) # Pause to let user see the booking form
        
        # Go to My Tokens
        print("Opening 'My Tickets' interface...")
        self.driver.get(BASE_URL + "/queues/my-tokens/")
        time.sleep(3) # Pause to let user see their tokens

    def test_03_staff_flow(self):
        """Test the workflow for a Staff user."""
        print("\n--- Testing Staff Flow ---")
        self.login("test_staff@sqms.lk", "TestPassword123!")
        
        # Go to Staff Manage page
        print("Opening 'Queue Management' interface...")
        self.driver.get(BASE_URL + "/queues/manage/")
        time.sleep(4) # Pause to let user see the staff management panel

    def test_04_admin_flow(self):
        """Test the workflow for an Admin user."""
        print("\n--- Testing Admin Flow ---")
        self.login("test_admin@sqms.lk", "TestPassword123!")
        
        # Check Admin Dashboard
        print("Opening 'Admin Dashboard' interface...")
        self.driver.get(BASE_URL + "/dashboard/")
        time.sleep(4) # Pause to let user see the admin metrics

if __name__ == "__main__":
    unittest.main(verbosity=2)
