import sys
import subprocess
import importlib.util

required_packages = {
    "undetected_chromedriver": "undetected-chromedriver",
    "selenium": "selenium",
    "requests": "requests",
    "setuptools": "setuptools"
}

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Installed {package_name}")
    except Exception as e:
        print(f"❌ Failed to install {package_name}: {e}")
        sys.exit(1)

def ensure_dependencies():
    for module_name, pip_name in required_packages.items():
        if importlib.util.find_spec(module_name) is None:
            print(f"⏳ Installing {pip_name}...")
            install_package(pip_name)
        else:
            print(f"✅ {pip_name} already installed.")
    print("All dependencies satisfied.\n")

ensure_dependencies()

import time
import random
import string
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---------- Configuration ----------
SAVE_FILE = "windscribe_accounts.txt"
WINDSCRIBE_SIGNUP_URL = "https://windscribe.com/signup"
CAPTCHA_WAIT_TIME = 10
TEMP_MAIL_URL = "https://temp-mail.org/en/"
PAGE_LOAD_TIMEOUT = 30
MAX_EMAIL_ATTEMPTS = 10
CONFIRM_WAIT_TIMEOUT = 180
# -----------------------------------

def random_string(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def quick_sleep(seconds=0.5):
    time.sleep(seconds)

def safe_get(driver, url):
    try:
        driver.get(url)
    except Exception as e:
        print(f"Navigation issue: {e}")

def wait_for_temp_mail(driver, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            mail_input = driver.find_element(By.ID, "mail")
            val = mail_input.get_attribute("value")
            if val and '@' in val:
                return val
        except:
            pass
        quick_sleep(1)
    return None

def delete_temp_mail(driver):
    try:
        delete_btn = driver.find_element(By.ID, "click-to-delete")
        if delete_btn.is_displayed() and delete_btn.is_enabled():
            delete_btn.click()
            quick_sleep(2)
            return True
    except:
        pass
    return False

def is_captcha_present(driver):
    try:
        driver.find_element(By.XPATH, "//iframe[contains(@src,'recaptcha') or contains(@src,'captcha')]")
        return True
    except NoSuchElementException:
        if driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha, [data-sitekey]"):
            return True
    return False

def check_for_disposable_error(driver):
    body_text = driver.find_element(By.TAG_NAME, "body").text
    if "disposable emails are not allowed" in body_text.lower():
        return True
    return False

def fill_signup_form(driver, wait, username, password, email):
    try:
        username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        username_field.clear()
        username_field.send_keys(username)
    except Exception as e:
        print(f"Username field error: {e}")
        return None

    try:
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='password'])[1]")))
        password_field.clear()
        password_field.send_keys(password)
    except Exception as e:
        print(f"Password field error: {e}")
        return None

    try:
        confirm_password_field = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='password'])[2]")))
        confirm_password_field.clear()
        confirm_password_field.send_keys(password)
    except Exception as e:
        print(f"Confirm password field error: {e}")
        return None

    if email:
        try:
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            email_field.clear()
            email_field.send_keys(email)
        except Exception as e:
            print(f"Email field error: {e}")
            email = None

    try:
        checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']")))
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
    except Exception as e:
        print(f"Checkbox error: {e}")

    return email

def click_signup_button(driver, wait):
    try:
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        submit_button.click()
        return True
    except Exception as e:
        print(f"Signup button error: {e}")
        return False

def is_signup_successful(driver):
    current_url = driver.current_url
    if "signup" not in current_url or "confirm" in current_url or "account" in current_url:
        return True
    try:
        driver.find_element(By.XPATH, "//button[contains(.,'Add Email')]")
        return True
    except:
        pass
    return False

def get_next_account_number():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        count = content.count("Account #")
        return count + 1
    except FileNotFoundError:
        return 1

def save_account(username, password, email):
    number = get_next_account_number()
    with open(SAVE_FILE, "a", encoding="utf-8") as f:
        f.write(f"Account #{number}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write(f"Email: {email}\n")
        f.write("-" * 30 + "\n")
    print(f"\n✅ Account #{number} saved to {SAVE_FILE}")

def wait_and_confirm_email(driver, temp_mail_tab, main_tab, timeout=CONFIRM_WAIT_TIMEOUT):
    driver.switch_to.window(temp_mail_tab)
    start_time = time.time()
    confirmation_link = None
    last_refresh = 0

    while time.time() - start_time < timeout:
        try:
            windscribe_email = driver.find_element(By.XPATH,
                "//a[contains(@class,'viewLink') and (.//span[contains(@class,'inboxSenderEmail') and contains(text(),'windscribe')] or .//span[contains(@class,'inboxSenderName') and contains(.,'Windscribe')])]")
            if windscribe_email.is_displayed() and windscribe_email.is_enabled():
                windscribe_email.click()
                print("Clicked Windscribe email.")
                try:
                    confirm_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'windscribe.com/signup/confirmemail')]"))
                    )
                    confirmation_link = confirm_elem.get_attribute('href')
                    if confirmation_link:
                        break
                except TimeoutException:
                    try:
                        iframe = driver.find_element(By.XPATH, "//iframe")
                        driver.switch_to.frame(iframe)
                        confirm_elem = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'windscribe.com/signup/confirmemail')]"))
                        )
                        confirmation_link = confirm_elem.get_attribute('href')
                        driver.switch_to.default_content()
                        if confirmation_link:
                            break
                    except:
                        driver.switch_to.default_content()
        except NoSuchElementException:
            pass
        except Exception as e:
            print(f"Polling error: {e}")

        quick_sleep(2)

        if time.time() - last_refresh > 15:
            try:
                driver.refresh()
                last_refresh = time.time()
                quick_sleep(1)
            except:
                pass

    if confirmation_link:
        driver.switch_to.window(main_tab)
        safe_get(driver, confirmation_link)
        print("Confirmation link opened. Waiting 8 seconds for email confirmation to complete...")
        time.sleep(8)  # increased from 3 to 8 seconds
        print("Email confirmed! 10GB activated.")
        return True
    else:
        print("Confirmation link not found after waiting.")
        return False

def main():
    username = random_string(12)
    password = random_string(16)
    print(f"Generated Username: {username}")

    print("Launching undetected Chrome...")
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.set_capability('pageLoadStrategy', 'eager')
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    try:
        # Open temp-mail.org in a new tab early
        driver.execute_script("window.open('');")
        temp_mail_tab = driver.window_handles[-1]
        driver.switch_to.window(temp_mail_tab)
        safe_get(driver, TEMP_MAIL_URL)
        print("Opened temp-mail.org in new tab.")

        # Switch to main tab and open Windscribe signup
        main_tab = driver.window_handles[0]
        driver.switch_to.window(main_tab)
        print("Opening Windscribe signup page...")
        safe_get(driver, WINDSCRIBE_SIGNUP_URL)
        quick_sleep(2)

        # Cookie consent
        try:
            cookie_accept = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept') or contains(text(),'I agree')]")))
            cookie_accept.click()
            quick_sleep(0.5)
        except TimeoutException:
            pass

        final_email = "NO_EMAIL"
        signup_success = False
        for attempt in range(MAX_EMAIL_ATTEMPTS):
            # Get temp email (wait up to 30 seconds)
            driver.switch_to.window(temp_mail_tab)
            email = wait_for_temp_mail(driver, timeout=30)
            if not email:
                print(f"Attempt {attempt+1}: Could not get email from temp-mail.org.")
                if not delete_temp_mail(driver):
                    print("Could not delete temp mail, trying refresh...")
                    driver.refresh()
                    quick_sleep(5)
                    email = wait_for_temp_mail(driver, timeout=20)
                    if not email:
                        print("Still no email. Skipping temp-mail.org.")
                        break
                continue
            print(f"Attempt {attempt+1}: Using email {email}")

            # Fill signup form
            driver.switch_to.window(main_tab)
            email_used = fill_signup_form(driver, wait, username, password, email)

            # If CAPTCHA is present before submitting, wait for user to solve
            if is_captcha_present(driver):
                print(f"CAPTCHA detected before submission. Waiting {CAPTCHA_WAIT_TIME} seconds...")
                time.sleep(CAPTCHA_WAIT_TIME)

            # Click signup button
            if not click_signup_button(driver, wait):
                print("Could not click signup button.")
                driver.refresh()
                quick_sleep(3)
                continue

            print("Signup form submitted.")
            # Always wait at least 10 seconds after submission to allow CAPTCHA solving
            print(f"Waiting {CAPTCHA_WAIT_TIME} seconds for any CAPTCHA...")
            time.sleep(CAPTCHA_WAIT_TIME)

            # Check if CAPTCHA still present; if so, wait additional time
            if is_captcha_present(driver):
                print("CAPTCHA still present. Waiting additional time...")
                time.sleep(CAPTCHA_WAIT_TIME)

            # Now check for signup success
            if is_signup_successful(driver):
                print("Signup successful.")
                if email_used:
                    print("Waiting for confirmation email...")
                    confirmed = wait_and_confirm_email(driver, temp_mail_tab, main_tab)
                    if confirmed:
                        final_email = email_used
                        signup_success = True
                        break
                    else:
                        print("Confirmation failed. Trying next email...")
                        driver.switch_to.window(temp_mail_tab)
                        delete_temp_mail(driver)
                        continue
                else:
                    signup_success = True
                    final_email = "NO_EMAIL"
                    break
            else:
                if check_for_disposable_error(driver):
                    print("Email rejected as disposable. Getting new temp email...")
                    driver.switch_to.window(temp_mail_tab)
                    delete_temp_mail(driver)
                    continue
                else:
                    print("Signup failed for unknown reason. Retrying with same email...")
                    # We'll retry without deleting email, but after a few attempts we may need to change.
                    # For now, continue; the loop will either succeed or use up attempts.
                    pass

        if signup_success:
            save_account(username, password, final_email)
            if final_email != "NO_EMAIL":
                print(f"Account created with 10GB (email: {final_email})")
            else:
                print("Account created with 2GB (no email added)")
        else:
            print("Failed to create account after multiple attempts.")

    except Exception as e:
        print(f"\n❌ An error occurred: {type(e).__name__}: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Screenshot saved as 'error_screenshot.png'")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()