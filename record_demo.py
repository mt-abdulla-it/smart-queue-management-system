#!/usr/bin/env python3
"""
SQMS Demo Screen Recording Script
===================================
Uses Selenium + headless Chrome to capture Full HD (1920×1080) screenshots
at key moments through the SQMS demo flow, then assembles them into an
animated WebP video file with smooth transitions.

Flow:
  1. Login Page → Login as patient
  2. User Dashboard
  3. Book Queue (Branch → Department → Service cascade)
  4. Token Detail (QR code, progress bar, live status)
  5. Live Queue Display (dark TV view)
  6. Staff Login → Staff Queue Management → Call Next
  7. Token Detail showing "IT'S YOUR TURN!" alert
  8. Admin Login → Admin Dashboard Analytics
"""

import os
import sys
import time
import json
import glob
import shutil
from io import BytesIO
from pathlib import Path

# Django setup for direct DB manipulation
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from apps.queues.models import QueueToken, QueueHistory
from apps.accounts.models import User

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════
BASE_URL = "http://localhost:8000"
FRAME_DIR = Path(__file__).parent / "_demo_frames"
OUTPUT_DIR = Path(__file__).parent / "docs"
OUTPUT_FILE = OUTPUT_DIR / "sqms_demo_recording.webp"
WIDTH, HEIGHT = 1920, 1080
FRAME_DURATION_MS = 120  # ~8.3 FPS base, but we vary per-frame for pacing
TRANSITION_STEPS = 6     # Cross-fade transition frames between scenes

# Credentials
PATIENT_EMAIL = "test_patient@sqms.lk"
STAFF_EMAIL = "test_staff@sqms.lk"
ADMIN_EMAIL = "test_admin@sqms.lk"
PASSWORD = "Demo@12345"


def create_driver():
    """Create a headless Chrome driver at Full HD."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument(f"--window-size={WIDTH},{HEIGHT}")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    # Fake a reasonable user agent
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(WIDTH, HEIGHT)
    return driver


class DemoRecorder:
    """Captures frames and assembles them into animated WebP."""

    def __init__(self):
        self.driver = create_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self.frames = []  # List of (PIL.Image, duration_ms)
        self.frame_count = 0

        # Clean and create frame directory
        if FRAME_DIR.exists():
            shutil.rmtree(FRAME_DIR)
        FRAME_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def capture(self, duration_ms=FRAME_DURATION_MS, label=""):
        """Capture current page as a frame."""
        png = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(png)).convert("RGBA")
        # Ensure exact dimensions
        if img.size != (WIDTH, HEIGHT):
            img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        self.frames.append((img, duration_ms))
        self.frame_count += 1
        # Save numbered frame for debugging
        img.save(FRAME_DIR / f"frame_{self.frame_count:04d}.png")
        if label:
            print(f"  📸 Frame {self.frame_count}: {label} ({duration_ms}ms)")
        return img

    def capture_sequence(self, count=3, interval=0.3, duration_ms=FRAME_DURATION_MS, label=""):
        """Capture multiple frames over time (for showing animations)."""
        for i in range(count):
            self.capture(duration_ms, f"{label} [{i+1}/{count}]" if label else "")
            if i < count - 1:
                time.sleep(interval)

    def add_crossfade(self, img_from, img_to, steps=TRANSITION_STEPS):
        """Add cross-fade transition frames between two scenes."""
        for i in range(1, steps + 1):
            alpha = i / (steps + 1)
            blended = Image.blend(img_from, img_to, alpha)
            self.frames.append((blended, 80))  # Fast transition frames
            self.frame_count += 1

    def hold_frame(self, seconds=2.0, label="Hold"):
        """Repeat the current screenshot for a specified duration."""
        png = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(png)).convert("RGBA")
        if img.size != (WIDTH, HEIGHT):
            img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        # Single frame with long duration
        self.frames.append((img, int(seconds * 1000)))
        self.frame_count += 1
        print(f"  ⏸️  Hold {seconds}s: {label}")

    def login(self, email, password=PASSWORD):
        """Login with given credentials."""
        self.driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(1.5)

        # Fill email (Django auth form uses 'username' field name even for email)
        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(0.3)

        # Fill password
        pass_field = self.driver.find_element(By.ID, "id_password")
        pass_field.clear()
        pass_field.send_keys(password)
        time.sleep(0.3)

        # Click sign in
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        time.sleep(2)

    def logout(self):
        """Logout current user."""
        self.driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def scroll_to_bottom(self, steps=4, pause=0.4):
        """Smooth scroll to bottom of page."""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_per_step = (total_height - viewport_height) / steps

        for i in range(1, steps + 1):
            scroll_y = int(scroll_per_step * i)
            self.driver.execute_script(f"window.scrollTo({{top: {scroll_y}, behavior: 'smooth'}})")
            time.sleep(pause)
            self.capture(200, f"Scroll step {i}/{steps}")

    def scroll_to_top(self):
        """Scroll back to top."""
        self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(0.5)

    # ═══════════════════════════════════════════════════════════════════════════
    # Demo Scenes
    # ═══════════════════════════════════════════════════════════════════════════

    def scene_01_login_page(self):
        """Scene 1: Show the beautiful login page."""
        print("\n🎬 SCENE 1: Login Page")
        self.driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(3)
        self.hold_frame(6.0, "Login Page — Beautiful split-screen auth UI")
        self.capture_sequence(3, 0.8, 800, "Login page micro-animations")
        last_frame = self.frames[-1][0]
        return last_frame

    def scene_02_patient_login(self):
        """Scene 2: Patient types credentials and logs in."""
        print("\n🎬 SCENE 2: Patient Login")

        # Type email slowly (capture after each part)
        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        email_field.clear()

        # Type email in smaller chunks for realistic typing
        email = PATIENT_EMAIL
        chunks = [email[:2], email[:5], email[:8], email[:13], email[:18], email[:22], email]
        for chunk in chunks:
            email_field.clear()
            email_field.send_keys(chunk)
            time.sleep(0.15)
            self.capture(400, f"Typing email: {chunk}")

        self.hold_frame(1.0, "Email fully typed")

        # Type password character by character
        pass_field = self.driver.find_element(By.ID, "id_password")
        pass_field.clear()
        for i in range(1, len(PASSWORD) + 1):
            pass_field.clear()
            pass_field.send_keys(PASSWORD[:i])
            time.sleep(0.1)
        self.capture(600, "Password filled")

        # Capture the filled form
        self.hold_frame(3.0, "Filled login form — ready to sign in")

        before_login = self.frames[-1][0]

        # Click Sign In
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        time.sleep(1)
        self.capture(400, "Loading after click")
        time.sleep(2)

        # After login - should be on dashboard
        self.capture(500, "After login redirect")
        return before_login

    def scene_03_user_dashboard(self):
        """Scene 3: User dashboard overview."""
        print("\n🎬 SCENE 3: User Dashboard")
        self.driver.get(f"{BASE_URL}/dashboard/user/")
        time.sleep(2.5)
        self.hold_frame(5.0, "User Dashboard — Welcome header + Stats cards")
        self.capture_sequence(2, 0.5, 600, "Stats cards hover effects")
        self.scroll_to_bottom(steps=5, pause=0.6)
        self.hold_frame(4.0, "Recent Tokens table + Quick Actions")
        self.scroll_to_top()
        time.sleep(0.5)
        last = self.capture(600, "Dashboard top view")
        return last

    def scene_04_book_queue(self):
        """Scene 4: Book a queue token with cascading dropdowns."""
        print("\n🎬 SCENE 4: Book Queue — Branch → Dept → Service")
        self.driver.get(f"{BASE_URL}/queues/book/")
        time.sleep(2.5)

        # Show the booking page with step wizard
        self.hold_frame(5.0, "Booking page — Step 1 active, wizard visible")

        # Select Branch
        branch_select = Select(self.wait.until(
            EC.presence_of_element_located((By.ID, "id_branch"))
        ))
        self.capture(600, "Branch dropdown ready")

        # Select Colombo General Hospital — text includes code suffix like "(CGH)"
        for opt in branch_select.options:
            if "Colombo General Hospital" in opt.text:
                branch_select.select_by_visible_text(opt.text)
                break
        time.sleep(1)
        self.capture(500, "Branch selected")
        time.sleep(1.5)  # Wait for AJAX
        self.hold_frame(3.0, "Step 2 active — Departments loaded via AJAX")
        self.capture_sequence(2, 0.5, 500, "Step wizard animated to step 2")

        # Select Department — match partial text
        dept_select = Select(self.driver.find_element(By.ID, "id_department"))
        for opt in dept_select.options:
            if "Cardiology" in opt.text:
                dept_select.select_by_visible_text(opt.text)
                break
        time.sleep(1)
        self.capture(500, "Department selected")
        time.sleep(1.5)  # Wait for AJAX
        self.hold_frame(3.0, "Services loaded for Cardiology Unit")
        self.capture_sequence(2, 0.5, 500, "Services dropdown populated")

        # Select Service — match partial text
        service_select = Select(self.driver.find_element(By.ID, "id_service"))
        for opt in service_select.options:
            if "ECG" in opt.text:
                service_select.select_by_visible_text(opt.text)
                break
        time.sleep(1)
        self.capture(500, "ECG service selected")
        time.sleep(1)
        self.hold_frame(4.0, "Step 3 — All selections complete, wizard fully progressed")
        self.capture_sequence(3, 0.5, 600, "Wait estimate card shimmer animation")

        # Show the wait estimate card
        self.hold_frame(4.0, "Wait estimate card — live queue estimate visible")

        before_submit = self.frames[-1][0]

        # Submit
        submit_btn = self.driver.find_element(By.ID, "submitBtn")
        submit_btn.click()
        time.sleep(1)
        self.capture(500, "Submitting — spinner visible")
        time.sleep(3)

        # After submit — token detail page
        self.capture(500, "After submit — redirected to token detail")
        return before_submit

    def scene_05_token_detail(self):
        """Scene 5: Token detail with QR code, progress bar, countdown."""
        print("\n🎬 SCENE 5: Token Detail — QR + Progress + Metrics")

        # We should already be on the token detail page after booking
        time.sleep(2.5)
        self.hold_frame(5.0, "Token Pass Card — header + token number + status badge")
        self.capture_sequence(2, 0.5, 600, "Live sync indicator")

        # Scroll to show progress bar and metrics
        self.driver.execute_script("window.scrollTo({top: 250, behavior: 'smooth'})")
        time.sleep(0.8)
        self.hold_frame(4.0, "Progress bar + timeline + position metrics")

        # Scroll to show QR code and full ticket
        self.scroll_to_bottom(steps=5, pause=0.6)
        self.hold_frame(4.0, "QR Code + Download PDF button visible")

        self.scroll_to_top()
        time.sleep(0.5)

        # Wait for live sync to update
        time.sleep(5)
        self.capture_sequence(4, 1.5, 700, "Live sync auto-refresh — progress bar updating")

        last = self.frames[-1][0]
        return last

    def scene_05b_my_tokens(self):
        """Scene 5b: My Tokens list page."""
        print("\n🎬 SCENE 5b: My Tokens List")
        self.driver.get(f"{BASE_URL}/queues/my-tokens/")
        time.sleep(2)
        self.hold_frame(5.0, "My Tokens — List of all user tokens with status badges")
        self.scroll_to_bottom(steps=3, pause=0.5)
        self.hold_frame(3.0, "Token history table scrolled")
        self.scroll_to_top()
        time.sleep(0.5)
        last = self.capture(500, "My Tokens top")
        return last

    def scene_06_live_display(self):
        """Scene 6: Live Queue TV Display."""
        print("\n🎬 SCENE 6: Live Queue TV Display")
        self.driver.get(f"{BASE_URL}/queues/display/")
        time.sleep(3.5)

        self.hold_frame(6.0, "Live TV Display — Dark theme, Now Serving + Upcoming")

        # Capture multiple frames to show clock ticking and ticker
        self.capture_sequence(6, 2.0, 800, "Live display — clock + multilingual ticker")

        self.hold_frame(4.0, "TV display — fullscreen button + sound controls")

        last = self.frames[-1][0]
        return last

    def scene_07_staff_login(self):
        """Scene 7a: Staff login page."""
        print("\n🎬 SCENE 7a: Staff Login")
        self.logout()
        self.driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        email_field.clear()
        email_field.send_keys(STAFF_EMAIL)
        time.sleep(0.3)
        self.capture(500, "Staff email entered")

        pass_field = self.driver.find_element(By.ID, "id_password")
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        time.sleep(0.3)
        self.capture(500, "Staff password entered")
        self.hold_frame(2.0, "Staff credentials filled")

        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        time.sleep(2.5)
        self.capture(500, "Staff logged in")
        last = self.frames[-1][0]
        return last

    def scene_07_staff_manage(self):
        """Scene 7b: Staff manages queue — calls next token."""
        print("\n🎬 SCENE 7b: Staff Queue Management")

        self.driver.get(f"{BASE_URL}/queues/manage/")
        time.sleep(2.5)

        # Show the staff panel
        self.hold_frame(5.0, "Staff Counter Panel — Hotkeys bar + Stats summary")
        self.capture_sequence(2, 0.5, 600, "Counter panel cards")

        # Scroll to see the queue list
        self.scroll_to_bottom(steps=4, pause=0.5)
        self.hold_frame(4.0, "Waiting queue list — tokens with Call Next + Skip buttons")

        self.scroll_to_top()
        time.sleep(0.5)
        self.capture(500, "Staff panel top view")

        # Click "Call Next" on the first waiting token
        try:
            call_btn = self.driver.find_element(By.CSS_SELECTOR, ".call-next-btn")
            self.hold_frame(2.0, "Highlighting Call Next button")
            call_btn.click()
            time.sleep(1)
            self.capture(500, "Calling next token...")
            time.sleep(2)
            self.hold_frame(4.0, "Token called — now SERVING at counter")
            self.capture_sequence(2, 0.5, 600, "Serving token hero card updated")
        except Exception as e:
            print(f"  ⚠️ Could not find Call Next button: {e}")
            self.capture(500, "Staff panel (no waiting tokens to call)")

        last = self.frames[-1][0]
        return last

    def scene_08_its_your_turn(self):
        """Scene 8: Show the 'IT'S YOUR TURN!' alert on token detail."""
        print("\n🎬 SCENE 8: IT'S YOUR TURN! Alert")

        # Find a token that is now SERVING
        serving_token = QueueToken.objects.filter(status='SERVING').order_by('-updated_at').first()

        if serving_token:
            # Login as patient to see their token
            self.logout()
            self.login(PATIENT_EMAIL)
            time.sleep(1)

            self.driver.get(f"{BASE_URL}/queues/token/{serving_token.pk}/")
            time.sleep(3)

            # Wait for live sync to detect SERVING status
            time.sleep(6)

            self.hold_frame(6.0, "IT'S YOUR TURN! — Green alert banner + PROCEED TO COUNTER")
            self.capture_sequence(4, 1.5, 800, "Serving alert pulsing — progress at 95%")

            # Scroll to show full card
            self.scroll_to_bottom(steps=3, pause=0.5)
            self.hold_frame(3.0, "Token detail — serving status + QR code")
            self.scroll_to_top()
            time.sleep(0.5)
        else:
            print("  ⚠️ No serving token found, skipping IT'S YOUR TURN scene")

        last = self.frames[-1][0]
        return last

    def scene_09_admin_login(self):
        """Scene 9a: Admin login."""
        print("\n🎬 SCENE 9a: Admin Login")
        self.logout()
        self.driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        email_field.clear()
        email_field.send_keys(ADMIN_EMAIL)
        time.sleep(0.3)

        pass_field = self.driver.find_element(By.ID, "id_password")
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        time.sleep(0.3)
        self.capture(500, "Admin credentials filled")
        self.hold_frame(2.0, "Admin login ready")

        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn.click()
        time.sleep(2.5)
        self.capture(500, "Admin logged in")
        last = self.frames[-1][0]
        return last

    def scene_09_admin_dashboard(self):
        """Scene 9b: Admin dashboard with analytics."""
        print("\n🎬 SCENE 9b: Admin Dashboard — Analytics")

        self.driver.get(f"{BASE_URL}/dashboard/admin/")
        time.sleep(3.5)

        self.hold_frame(6.0, "Admin Dashboard — Key metrics cards row")
        self.capture_sequence(3, 0.5, 600, "Metrics cards — shimmer animation")

        # Scroll to show charts
        self.driver.execute_script("window.scrollTo({top: 350, behavior: 'smooth'})")
        time.sleep(0.8)
        self.hold_frame(5.0, "7-Day Token Trend chart — line graph with gradient fill")

        self.driver.execute_script("window.scrollTo({top: 600, behavior: 'smooth'})")
        time.sleep(0.8)
        self.hold_frame(4.0, "Service Distribution donut chart")

        self.scroll_to_bottom(steps=3, pause=0.5)
        self.hold_frame(5.0, "Quick Actions + System Status — all services operational")

        self.scroll_to_top()
        time.sleep(0.5)
        self.hold_frame(4.0, "Admin Dashboard — Final overview")

        last = self.frames[-1][0]
        return last

    # ═══════════════════════════════════════════════════════════════════════════
    # Assembly
    # ═══════════════════════════════════════════════════════════════════════════

    def assemble_webp(self):
        """Assemble all frames into animated WebP."""
        print(f"\n🎬 Assembling {len(self.frames)} frames into animated WebP...")

        if not self.frames:
            print("❌ No frames captured!")
            return

        # Convert all to RGB for WebP
        rgb_frames = []
        durations = []
        for img, dur in self.frames:
            rgb_frames.append(img.convert("RGB"))
            durations.append(dur)

        # Calculate total duration
        total_ms = sum(durations)
        total_sec = total_ms / 1000
        print(f"  Total duration: {total_sec:.1f}s ({len(rgb_frames)} frames)")

        # Save as animated WebP
        first_frame = rgb_frames[0]
        remaining = rgb_frames[1:]

        first_frame.save(
            str(OUTPUT_FILE),
            format="WEBP",
            save_all=True,
            append_images=remaining,
            duration=durations,
            loop=0,  # Infinite loop
            quality=85,
            method=4,
        )

        file_size = OUTPUT_FILE.stat().st_size
        print(f"  ✅ Saved: {OUTPUT_FILE}")
        print(f"  📦 File size: {file_size / (1024*1024):.1f} MB")
        print(f"  🕐 Duration: {total_sec:.1f}s")
        print(f"  📐 Resolution: {WIDTH}×{HEIGHT}")

    def run(self):
        """Execute the full demo recording."""
        print("═" * 70)
        print("  SQMS DEMO RECORDING — Smart Queue Management System")
        print("═" * 70)
        print(f"  Resolution: {WIDTH}×{HEIGHT}")
        print(f"  Output: {OUTPUT_FILE}")
        print(f"  Target Duration: 150–300 seconds")
        print()

        try:
            # Run all scenes
            self.scene_01_login_page()
            self.scene_02_patient_login()
            self.scene_03_user_dashboard()
            self.scene_04_book_queue()
            self.scene_05_token_detail()
            self.scene_05b_my_tokens()
            self.scene_06_live_display()
            self.scene_07_staff_login()
            self.scene_07_staff_manage()
            self.scene_08_its_your_turn()
            self.scene_09_admin_login()
            self.scene_09_admin_dashboard()

            # Assemble into WebP
            self.assemble_webp()

        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            import traceback
            traceback.print_exc()

            # Still try to assemble what we have
            if self.frames:
                print("\n🔄 Assembling partial recording...")
                self.assemble_webp()
        finally:
            self.driver.quit()
            # Clean up frame directory
            if FRAME_DIR.exists():
                shutil.rmtree(FRAME_DIR)
            print("\n🎬 Recording complete!")


if __name__ == "__main__":
    recorder = DemoRecorder()
    recorder.run()
