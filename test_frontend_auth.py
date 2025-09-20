#!/usr/bin/env python3
"""
Frontend Authentication Testing Script
Tests the complete authentication flow through the UI using Selenium
"""

import time
import json
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FrontendAuthTester:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"
        self.test_user = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Set Chrome binary path for macOS
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome driver initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            return False
    
    def check_database_user(self, email):
        """Check if user exists in PostgreSQL database"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="ibs_wellness",
                user="ayushagarwal",
                password="ayush1"
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, email, first_name, last_name, is_active, created_at FROM users WHERE email = %s",
                (email,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"✅ User found in database: {result[1]} ({result[2]} {result[3]})")
                return True
            else:
                print(f"❌ User not found in database: {email}")
                return False
                
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            return False
    
    def clean_test_user(self):
        """Remove test user from database"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="ibs_wellness",
                user="ayushagarwal",
                password="ayush1"
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = %s", (self.test_user["email"],))
            conn.commit()
            conn.close()
            print(f"🧹 Cleaned up test user: {self.test_user['email']}")
        except Exception as e:
            print(f"⚠️ Failed to clean up test user: {e}")
    
    def test_registration_flow(self):
        """Test the complete registration flow"""
        print("\n🧪 Testing Registration Flow...")
        
        try:
            # Navigate to registration page
            self.driver.get(f"{self.base_url}/register")
            print("📍 Navigated to registration page")
            
            # Wait for form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            # Check for any error messages on page load
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .error, .text-red-500, .text-destructive")
                if error_elements:
                    print(f"⚠️ Found error messages on page: {[el.text for el in error_elements]}")
            except:
                pass
            
            # Fill out registration form
            full_name_field = self.driver.find_element(By.NAME, "fullName")
            email_field = self.driver.find_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")
            confirm_password_field = self.driver.find_element(By.NAME, "confirmPassword")
            
            # Clear fields first
            full_name_field.clear()
            email_field.clear()
            password_field.clear()
            confirm_password_field.clear()
            
            # Fill with test data
            full_name_field.send_keys(self.test_user["full_name"])
            email_field.send_keys(self.test_user["email"])
            password_field.send_keys(self.test_user["password"])
            confirm_password_field.send_keys(self.test_user["password"])
            
            print("📝 Filled out registration form")
            
            # Check if submit button is enabled
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            if submit_button.get_attribute("disabled"):
                print("❌ Submit button is disabled")
                return False
            
            # Submit form
            submit_button.click()
            print("🚀 Submitted registration form")
            
            # Wait a bit longer for processing
            time.sleep(5)
            
            # Check for any error messages after submission
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .error, .text-red-500, .text-destructive")
                if error_elements:
                    print(f"❌ Registration errors found: {[el.text for el in error_elements]}")
                    return False
            except:
                pass
            
            # Check current URL
            current_url = self.driver.current_url
            print(f"📍 Current URL after submission: {current_url}")
            
            # Check if redirected to onboarding or dashboard
            if "/onboarding" in current_url or "/dashboard" in current_url:
                print("✅ Registration successful - redirected to:", current_url)
                
                # Verify user was created in database
                if self.check_database_user(self.test_user["email"]):
                    print("✅ Registration flow completed successfully")
                    return True
                else:
                    print("❌ User not found in database after registration")
                    return False
            elif current_url == f"{self.base_url}/register":
                print("❌ Still on registration page - form submission may have failed")
                # Try to get page source for debugging
                try:
                    page_title = self.driver.title
                    print(f"📄 Page title: {page_title}")
                except:
                    pass
                return False
            else:
                print(f"❌ Unexpected redirect - current URL: {current_url}")
                return False
                
        except TimeoutException:
            print("❌ Registration form did not load in time")
            return False
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
            # Try to get more debugging info
            try:
                current_url = self.driver.current_url
                page_title = self.driver.title
                print(f"🔍 Debug info - URL: {current_url}, Title: {page_title}")
            except:
                pass
            return False
    
    def test_login_flow(self):
        """Test the login flow with the registered user"""
        print("\n🧪 Testing Login Flow...")
        
        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/login")
            print("📍 Navigated to login page")
            
            # Wait for form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            # Fill out login form
            email_field = self.driver.find_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.send_keys(self.test_user["email"])
            password_field.send_keys(self.test_user["password"])
            
            print("📝 Filled out login form")
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            print("🚀 Submitted login form")
            
            # Wait for redirect
            time.sleep(3)
            
            # Check if redirected to dashboard or onboarding
            current_url = self.driver.current_url
            if "/dashboard" in current_url or "/onboarding" in current_url:
                print("✅ Login successful - redirected to:", current_url)
                return True
            else:
                print(f"❌ Login failed - current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    def run_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Frontend Authentication Tests")
        print("=" * 50)
        
        # Setup
        if not self.setup_driver():
            return False
        
        # Clean up any existing test user
        self.clean_test_user()
        
        try:
            # Test registration
            registration_success = self.test_registration_flow()
            
            if registration_success:
                # Test login (logout first if needed)
                self.driver.get(f"{self.base_url}/login")
                time.sleep(2)
                login_success = self.test_login_flow()
                
                print("\n" + "=" * 50)
                print("📊 TEST RESULTS:")
                print(f"Registration: {'✅ PASS' if registration_success else '❌ FAIL'}")
                print(f"Login: {'✅ PASS' if login_success else '❌ FAIL'}")
                
                if registration_success and login_success:
                    print("🎉 All authentication tests PASSED!")
                    return True
                else:
                    print("❌ Some tests FAILED!")
                    return False
            else:
                print("❌ Registration failed, skipping login test")
                return False
                
        finally:
            # Cleanup
            self.clean_test_user()
            if self.driver:
                self.driver.quit()
                print("🧹 Browser closed")

if __name__ == "__main__":
    tester = FrontendAuthTester()
    success = tester.run_tests()
    exit(0 if success else 1)
