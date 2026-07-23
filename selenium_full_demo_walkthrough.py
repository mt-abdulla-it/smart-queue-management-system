"""
Smart Queue Management System (SQMS) — Full Interactive Demo Walkthrough
Executes the complete 10-section demonstration in Google Chrome on the desktop.
"""
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

def run_full_sqms_demo():
    print("\n=======================================================")
    print(" 🚀 LAUNCHING SMART QUEUE MANAGEMENT SYSTEM (SQMS) DEMO ")
    print("=======================================================\n")

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(5)

    try:
        # -------------------------------------------------------------
        # SECTION 1: Home Page & UI Overview
        # -------------------------------------------------------------
        print("▶ Section 1: Opening SQMS Home Page...")
        driver.get(BASE_URL + "/")
        time.sleep(3) # Let animations play

        print("  - Smooth scrolling through feature sections...")
        driver.execute_script("window.scrollTo({top: 600, behavior: 'smooth'});")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo({top: 1200, behavior: 'smooth'});")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(2)

        # Helper login function
        def login_user(email, password, role_name):
            print(f"\n▶ Logging in as {role_name} ({email})...")
            driver.get(BASE_URL + "/accounts/login/")
            time.sleep(1.5)
            
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            pass_field = driver.find_element(By.NAME, "password")
            
            email_field.clear()
            for char in email:
                email_field.send_keys(char)
                time.sleep(0.02)
                
            pass_field.clear()
            for char in password:
                pass_field.send_keys(char)
                time.sleep(0.02)
                
            time.sleep(1)
            submit_btn = driver.find_element(By.CSS_SELECTOR, ".auth-form-side form button[type='submit']")
            driver.execute_script("arguments[0].click();", submit_btn)
            
            WebDriverWait(driver, 10).until(EC.url_changes(BASE_URL + "/accounts/login/"))
            time.sleep(2)
            print(f"  ✓ Logged in as {role_name} successfully!")

        def logout_user():
            print("  - Logging out current session...")
            driver.get(BASE_URL + "/accounts/logout/")
            time.sleep(1.5)
            driver.delete_all_cookies()

        # -------------------------------------------------------------
        # SECTION 2: Patient Queue Booking
        # -------------------------------------------------------------
        login_user("test_patient@sqms.lk", "TestPassword123!", "Patient")

        print("\n▶ Section 2: Patient Queue Booking Wizard...")
        driver.get(BASE_URL + "/queues/book/")
        time.sleep(2.5)

        print("  - Step 1: Selecting Branch...")
        branch_select = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_branch"))))
        branch_select.select_by_index(1)
        time.sleep(2) # AJAX loading

        print("  - Step 2: Selecting Department...")
        dept_select = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_department"))))
        WebDriverWait(driver, 5).until(lambda d: len(Select(d.find_element(By.ID, "id_department")).options) > 1)
        dept_select.select_by_index(1)
        time.sleep(2) # AJAX loading

        print("  - Step 3: Selecting Service & Checking Est. Wait Time...")
        service_select = Select(WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_service"))))
        WebDriverWait(driver, 5).until(lambda d: len(Select(d.find_element(By.ID, "id_service")).options) > 1)
        service_select.select_by_index(1)
        time.sleep(2) # Show wait estimate analysis card

        print("  - Confirming & Issuing Queue Token...")
        submit_booking = driver.find_element(By.CSS_SELECTOR, "form#bookingForm button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", submit_booking)

        # -------------------------------------------------------------
        # SECTION 3: Digital Ticket Pass & Live Progress Bar
        # -------------------------------------------------------------
        WebDriverWait(driver, 10).until(EC.url_contains("/queues/token/"))
        print("\n▶ Section 3: Digital Ticket Pass & Live Queue Progress Tracker...")
        time.sleep(4) # Demonstrate live sync dot, animated progress bar, QR code, and stage milestones

        # -------------------------------------------------------------
        # SECTION 4: My Tokens Page
        # -------------------------------------------------------------
        print("\n▶ Section 4: Opening 'My Tokens' Dashboard...")
        driver.get(BASE_URL + "/queues/my-tokens/")
        time.sleep(3)

        # -------------------------------------------------------------
        # SECTION 5: Public Live Display Board
        # -------------------------------------------------------------
        print("\n▶ Section 5: Opening Public Live Display Screen (TV Board)...")
        driver.get(BASE_URL + "/queues/live/")
        time.sleep(4) # Demonstrate big screen TV display board

        # -------------------------------------------------------------
        # SECTION 6: Staff Queue Management Panel
        # -------------------------------------------------------------
        logout_user()
        login_user("test_staff@sqms.lk", "TestPassword123!", "Staff Counter Operator")

        print("\n▶ Section 6: Staff Queue Control Panel...")
        driver.get(BASE_URL + "/queues/manage/")
        time.sleep(3.5) # Demonstrate waiting queue and counter hotkeys

        # -------------------------------------------------------------
        # SECTION 7: Admin Dashboard & System Management
        # -------------------------------------------------------------
        logout_user()
        login_user("test_admin@sqms.lk", "TestPassword123!", "System Administrator")

        print("\n▶ Section 7: Admin Analytics Command Center...")
        driver.get(BASE_URL + "/dashboard/admin/")
        time.sleep(3.5) # Show queue metrics, counter stats, and throughput analytics

        print("  - Navigating to Branch & Service Management...")
        driver.get(BASE_URL + "/branches/")
        time.sleep(3) # Show branch CRUD management table

        # -------------------------------------------------------------
        # SECTION 9: Responsive Design Demonstration
        # -------------------------------------------------------------
        print("\n▶ Section 9: Responsive Layout Testing...")
        print("  - Tablet Mode (768 x 1024)...")
        driver.set_window_size(768, 1024)
        time.sleep(3)

        print("  - Mobile Mode (375 x 812)...")
        driver.set_window_size(375, 812)
        time.sleep(3)

        print("  - Restoring Desktop Full HD (1920 x 1080)...")
        driver.set_window_size(1920, 1080)
        time.sleep(2)

        # -------------------------------------------------------------
        # SECTION 10: Final Walkthrough & Conclusion
        # -------------------------------------------------------------
        print("\n▶ Section 10: Final System Verification & Wrap-up...")
        driver.get(BASE_URL + "/dashboard/admin/")
        time.sleep(4)

        print("\n=======================================================")
        print(" ✨ SQMS FULL DEMO WALKTHROUGH COMPLETED SUCCESSFULLY! ")
        print("=======================================================\n")

    except Exception as e:
        print(f"\n❌ Error during demo walkthrough: {e}")
    finally:
        print("Closing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    run_full_sqms_demo()
