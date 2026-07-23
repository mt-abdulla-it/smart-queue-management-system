# Smart Queue Management System (SQMS) — Full 6-Minute Production Demo Script
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

def smooth_full_page_scroll(driver, pause=2.5):
    """Perform realistic smooth full page scrolling from top to bottom and back up."""
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight / 3, behavior: 'smooth'});")
    time.sleep(pause)
    driver.execute_script("window.scrollTo({top: (document.body.scrollHeight / 3) * 2, behavior: 'smooth'});")
    time.sleep(pause)
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
    time.sleep(pause)
    driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
    time.sleep(pause)

def run_full_sqms_demo():
    print("\n=======================================================")
    print(" 🚀 LAUNCHING 6-MINUTE SMART QUEUE MANAGEMENT SYSTEM DEMO ")
    print("=======================================================\n")

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(5)

    try:
        # -------------------------------------------------------------
        # SECTION 1: Home Page & UI Overview (30s)
        # -------------------------------------------------------------
        print("▶ Section 1: Opening SQMS Home Page...")
        driver.get(BASE_URL + "/")
        time.sleep(3)
        print("  - Smooth full page scrolling on Home Page...")
        smooth_full_page_scroll(driver, pause=3)

        # Helper login function
        def login_user(email, password, role_name):
            print(f"\n▶ Logging in as {role_name} ({email})...")
            driver.get(BASE_URL + "/accounts/login/")
            time.sleep(2)
            
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            pass_field = driver.find_element(By.NAME, "password")
            
            email_field.clear()
            for char in email:
                email_field.send_keys(char)
                time.sleep(0.04)
                
            pass_field.clear()
            for char in password:
                pass_field.send_keys(char)
                time.sleep(0.04)
                
            time.sleep(1.5)
            submit_btn = driver.find_element(By.CSS_SELECTOR, ".auth-form-side form button[type='submit']")
            driver.execute_script("arguments[0].click();", submit_btn)
            
            WebDriverWait(driver, 10).until(EC.url_changes(BASE_URL + "/accounts/login/"))
            time.sleep(2.5)
            print(f"  ✓ Logged in as {role_name} successfully!")

        def logout_user():
            print("  - Logging out current session...")
            driver.get(BASE_URL + "/accounts/logout/")
            time.sleep(2)
            driver.delete_all_cookies()

        # -------------------------------------------------------------
        # SECTION 2: Patient Queue Booking (45s)
        # -------------------------------------------------------------
        login_user("test_patient@sqms.lk", "TestPassword123!", "Patient")

        print("\n▶ Section 2: Patient Queue Booking Wizard...")
        driver.get(BASE_URL + "/queues/book/")
        time.sleep(3)

        print("  - Step 1: Selecting Branch...")
        branch_select = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_branch"))))
        branch_select.select_by_index(1)
        time.sleep(2.5)

        print("  - Step 2: Selecting Department...")
        dept_select = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_department"))))
        WebDriverWait(driver, 5).until(lambda d: len(Select(d.find_element(By.ID, "id_department")).options) > 1)
        dept_select.select_by_index(1)
        time.sleep(2.5)

        print("  - Step 3: Selecting Service & Checking Est. Wait Time...")
        service_select = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_service"))))
        WebDriverWait(driver, 5).until(lambda d: len(Select(d.find_element(By.ID, "id_service")).options) > 1)
        service_select.select_by_index(1)
        time.sleep(3) # Wait estimate card

        print("  - Smooth scrolling on Queue Booking form...")
        smooth_full_page_scroll(driver, pause=2)

        print("  - Confirming & Issuing Queue Token...")
        submit_booking = driver.find_element(By.CSS_SELECTOR, "form#bookingForm button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", submit_booking)

        # -------------------------------------------------------------
        # SECTION 3: Digital Ticket Pass & Live Progress Bar (45s)
        # -------------------------------------------------------------
        WebDriverWait(driver, 10).until(EC.url_contains("/queues/token/"))
        print("\n▶ Section 3: Digital Ticket Pass & Live Queue Progress Tracker...")
        time.sleep(4)
        print("  - Smooth full page scrolling on Digital Ticket Pass...")
        smooth_full_page_scroll(driver, pause=3)
        time.sleep(3)

        # -------------------------------------------------------------
        # SECTION 4: My Tokens Page (30s)
        # -------------------------------------------------------------
        print("\n▶ Section 4: Opening 'My Tokens' Dashboard...")
        driver.get(BASE_URL + "/queues/my-tokens/")
        time.sleep(3)
        print("  - Smooth full page scrolling on My Tokens...")
        smooth_full_page_scroll(driver, pause=2.5)

        # -------------------------------------------------------------
        # SECTION 5: Public Live Display Board (40s)
        # -------------------------------------------------------------
        print("\n▶ Section 5: Opening Public Live Display Screen (TV Board)...")
        driver.get(BASE_URL + "/queues/live/")
        time.sleep(4)
        print("  - Smooth full page scrolling on Public Live Display...")
        smooth_full_page_scroll(driver, pause=3)
        time.sleep(3)

        # -------------------------------------------------------------
        # SECTION 6: Staff Queue Management Panel (45s)
        # -------------------------------------------------------------
        logout_user()
        login_user("test_staff@sqms.lk", "TestPassword123!", "Staff Counter Operator")

        print("\n▶ Section 6: Staff Queue Control Panel...")
        driver.get(BASE_URL + "/queues/manage/")
        time.sleep(3)
        print("  - Smooth full page scrolling on Staff Control Panel...")
        smooth_full_page_scroll(driver, pause=3)
        time.sleep(3)

        # -------------------------------------------------------------
        # SECTION 7: Admin Analytics Dashboard & Management (45s)
        # -------------------------------------------------------------
        logout_user()
        login_user("test_admin@sqms.lk", "TestPassword123!", "System Administrator")

        print("\n▶ Section 7: Admin Analytics Command Center...")
        driver.get(BASE_URL + "/dashboard/admin/")
        time.sleep(3)
        print("  - Smooth full page scrolling on Admin Dashboard...")
        smooth_full_page_scroll(driver, pause=3)

        print("  - Navigating to Branch & Service Management...")
        driver.get(BASE_URL + "/branches/")
        time.sleep(3)
        print("  - Smooth full page scrolling on Branch Management...")
        smooth_full_page_scroll(driver, pause=3)

        # -------------------------------------------------------------
        # SECTION 9: Responsive Design Demonstration (30s)
        # -------------------------------------------------------------
        print("\n▶ Section 9: Responsive Layout Testing...")
        print("  - Tablet Mode (768 x 1024)...")
        driver.set_window_size(768, 1024)
        smooth_full_page_scroll(driver, pause=2)

        print("  - Mobile Mode (375 x 812)...")
        driver.set_window_size(375, 812)
        smooth_full_page_scroll(driver, pause=2)

        print("  - Restoring Desktop Full HD (1920 x 1080)...")
        driver.set_window_size(1920, 1080)
        time.sleep(3)

        # -------------------------------------------------------------
        # SECTION 10: Final Walkthrough & Conclusion (20s)
        # -------------------------------------------------------------
        print("\n▶ Section 10: Final System Verification & Wrap-up...")
        driver.get(BASE_URL + "/dashboard/admin/")
        smooth_full_page_scroll(driver, pause=2)
        time.sleep(4)

        print("\n=======================================================")
        print(" ✨ 6-MINUTE SQMS DEMO WALKTHROUGH COMPLETED! ")
        print("=======================================================\n")

    except Exception as e:
        print(f"\n❌ Error during demo walkthrough: {e}")
    finally:
        print("Closing browser in 4 seconds...")
        time.sleep(4)
        driver.quit()

if __name__ == "__main__":
    run_full_sqms_demo()
