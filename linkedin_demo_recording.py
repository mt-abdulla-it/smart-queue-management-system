import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000"

INJECT_STYLES_JS = """
if (!document.getElementById('demo-styles')) {
    const style = document.createElement('style');
    style.id = 'demo-styles';
    style.innerHTML = `
        html { 
            transition: transform 1.2s cubic-bezier(0.25, 1, 0.5, 1);
            transform-origin: center center;
            scroll-behavior: smooth;
        }
        @keyframes ripple-animation {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(3); opacity: 0; }
        }
        .demo-cursor {
            width: 20px;
            height: 20px;
            background: rgba(0,0,0,0.7);
            border-radius: 50%;
            position: fixed;
            z-index: 999999;
            pointer-events: none;
            transition: top 0.8s cubic-bezier(0.25, 1, 0.5, 1), left 0.8s cubic-bezier(0.25, 1, 0.5, 1);
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            border: 2px solid white;
        }
        .demo-ripple {
            position: fixed;
            width: 20px;
            height: 20px;
            background: rgba(255, 0, 0, 0.6);
            border-radius: 50%;
            pointer-events: none;
            z-index: 999998;
            animation: ripple-animation 0.6s ease-out forwards;
        }
    `;
    document.head.appendChild(style);
    
    const cursor = document.createElement('div');
    cursor.id = 'demo-cursor';
    cursor.className = 'demo-cursor';
    cursor.style.top = '50%';
    cursor.style.left = '50%';
    document.body.appendChild(cursor);
}
"""

MOVE_CURSOR_JS = """
const cursor = document.getElementById('demo-cursor');
const rect = arguments[0].getBoundingClientRect();
cursor.style.left = (rect.left + (rect.width / 2) - 10) + 'px';
cursor.style.top = (rect.top + (rect.height / 2) - 10) + 'px';
"""

CLICK_RIPPLE_JS = """
const rect = arguments[0].getBoundingClientRect();
const ripple = document.createElement('div');
ripple.className = 'demo-ripple';
ripple.style.left = (rect.left + (rect.width / 2) - 10) + 'px';
ripple.style.top = (rect.top + (rect.height / 2) - 10) + 'px';
document.body.appendChild(ripple);
setTimeout(() => ripple.remove(), 600);
"""

ZOOM_IN_JS = """
const rect = arguments[0].getBoundingClientRect();
const x = (rect.left + rect.width / 2) / window.innerWidth * 100;
const y = (rect.top + rect.height / 2) / window.innerHeight * 100;
document.documentElement.style.transformOrigin = `${x}% ${y}%`;
document.documentElement.style.transform = 'scale(1.2)';
"""

ZOOM_OUT_JS = """
document.documentElement.style.transform = 'scale(1)';
"""

def smooth_click(driver, element, pause=1.5, zoom=False):
    if zoom:
        driver.execute_script(ZOOM_IN_JS, element)
        time.sleep(1)
        
    driver.execute_script(MOVE_CURSOR_JS, element)
    time.sleep(pause)
    driver.execute_script(CLICK_RIPPLE_JS, element)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(1)
    
    if zoom:
        driver.execute_script(ZOOM_OUT_JS)
        time.sleep(1)

def smooth_full_page_scroll(driver, pause=2.0):
    """Perform realistic smooth full page scrolling from top to bottom and back up."""
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight / 3, behavior: 'smooth'});")
    time.sleep(pause)
    driver.execute_script("window.scrollTo({top: (document.body.scrollHeight / 3) * 2, behavior: 'smooth'});")
    time.sleep(pause)
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
    time.sleep(pause)
    driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
    time.sleep(pause)

def login_user(driver, wait, email, password, role_name):
    print(f"▶ Logging in as {role_name}...")
    driver.get(BASE_URL + "/accounts/login/")
    time.sleep(2)
    driver.execute_script(INJECT_STYLES_JS)
    
    email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.execute_script(ZOOM_IN_JS, email_field)
    driver.execute_script(MOVE_CURSOR_JS, email_field)
    time.sleep(1)
    
    email_field.clear()
    for char in email:
        email_field.send_keys(char)
        time.sleep(0.04)
        
    pass_field = driver.find_element(By.NAME, "password")
    pass_field.clear()
    for char in password:
        pass_field.send_keys(char)
        time.sleep(0.04)
        
    time.sleep(1)
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    smooth_click(driver, submit_btn)
    driver.execute_script(ZOOM_OUT_JS)
    time.sleep(2)

def logout_user(driver):
    print("▶ Logging out...")
    driver.get(BASE_URL + "/accounts/logout/")
    time.sleep(2)

def run_linkedin_demo():
    print("🎬 Starting MEGA Cinematic LinkedIn Demo Script...")
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # --- 1. HOME PAGE ---
        print("▶ 1. Opening SQMS Home Page...")
        driver.get(BASE_URL)
        time.sleep(2)
        driver.execute_script(INJECT_STYLES_JS)
        smooth_full_page_scroll(driver, pause=2)
        
        # --- 2. PATIENT QUEUE BOOKING ---
        login_user(driver, wait, "test_patient@sqms.lk", "Demo@12345", "Patient")
        
        print("▶ 2. Booking Queue...")
        driver.get(BASE_URL + "/queues/book/")
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(2)
        
        try:
            branch_select = Select(wait.until(EC.presence_of_element_located((By.ID, "id_branch"))))
            branch_select.select_by_index(1)
            time.sleep(2)
            dept_select = Select(wait.until(EC.presence_of_element_located((By.ID, "id_department"))))
            dept_select.select_by_index(1)
            time.sleep(2)
            service_select = Select(wait.until(EC.presence_of_element_located((By.ID, "id_service"))))
            service_select.select_by_index(1)
            time.sleep(2)
            
            submit_booking = driver.find_element(By.CSS_SELECTOR, "form#bookingForm button[type='submit']")
            smooth_click(driver, submit_booking, zoom=True)
            time.sleep(3)
        except Exception as e:
            print("Skipped booking details:", e)

        # --- 3. DIGITAL TICKET ---
        print("▶ 3. Digital Ticket Pass...")
        WebDriverWait(driver, 10).until(EC.url_contains("/queues/token/"))
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(3)
        smooth_full_page_scroll(driver, pause=2)

        # --- 4. MY TOKENS ---
        print("▶ 4. My Tokens...")
        driver.get(BASE_URL + "/queues/my-tokens/")
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(2)
        smooth_full_page_scroll(driver, pause=2)

        # --- 5. LIVE DISPLAY SCREEN ---
        print("▶ 5. Live Display Screen...")
        driver.get(BASE_URL + "/queues/live/")
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(4)
        smooth_full_page_scroll(driver, pause=2)
        
        logout_user(driver)

        # --- 6. STAFF DASHBOARD ---
        login_user(driver, wait, "test_staff@sqms.lk", "Demo@12345", "Staff")
        print("▶ 6. Staff Dashboard...")
        driver.get(BASE_URL + "/queues/manage/")
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(2)
        smooth_full_page_scroll(driver, pause=2)
        
        print("   - Demonstrating Staff Actions...")
        try:
            # Simulate keyboard shortcut for calling next token
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.SPACE)
            time.sleep(3)
        except:
            pass

        logout_user(driver)

        # --- 7. ADMIN DASHBOARD ---
        login_user(driver, wait, "test_admin@sqms.lk", "Demo@12345", "Admin")
        print("▶ 7. Admin Dashboard & Reports...")
        driver.get(BASE_URL + "/dashboard/admin/")
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(2)
        smooth_full_page_scroll(driver, pause=2)

        print("▶ Navigating to Branch Management...")
        driver.get(BASE_URL + "/branches/")
        driver.execute_script(INJECT_STYLES_JS)
        time.sleep(2)
        smooth_full_page_scroll(driver, pause=2)

        # --- 8 & 9. RESPONSIVE DESIGN ---
        print("▶ 9. Responsive Design Testing...")
        driver.set_window_size(768, 1024)
        time.sleep(2)
        smooth_full_page_scroll(driver, pause=1)

        driver.set_window_size(375, 812)
        time.sleep(2)
        smooth_full_page_scroll(driver, pause=1)

        driver.set_window_size(1920, 1080)
        time.sleep(2)

        # --- 10. LOGOUT & VERIFY ---
        print("▶ 10. Final Verification...")
        logout_user(driver)
        login_user(driver, wait, "test_patient@sqms.lk", "Demo@12345", "Patient")
        driver.get(BASE_URL + "/queues/my-tokens/")
        time.sleep(3)

        print("✅ FULL Mega Demo complete! You can stop your screen recorder now.")
        time.sleep(4)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_linkedin_demo()
