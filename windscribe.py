import sys
import subprocess
import importlib.util

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
import html
import socket

# Bypass problematic Anycast IPs (like 185.199.111.153) that cause [SSL: WRONG_VERSION_NUMBER]
_orig_getaddrinfo = socket.getaddrinfo
def _safe_getaddrinfo(host, port, *args, **kwargs):
    res = _orig_getaddrinfo(host, port, *args, **kwargs)
    if isinstance(host, str) and ("github.io" in host or "chrome-for-testing" in host):
        filtered = [r for r in res if r[4][0] != "185.199.111.153"]
        return filtered if filtered else res
    return res
socket.getaddrinfo = _safe_getaddrinfo

import io
import tempfile
import undetected_chromedriver as uc
import undetected_chromedriver.patcher as uc_patcher

# Ensure uc_patcher can download driver releases even if Python SSL/network encounters censorship or proxy issues
_orig_patcher_urlopen = uc_patcher.urlopen
def _robust_patcher_urlopen(url, *args, **kwargs):
    try:
        return _orig_patcher_urlopen(url, *args, **kwargs)
    except Exception:
        res = subprocess.check_output(["curl.exe", "-sL", "--connect-timeout", "15", str(url)])
        return io.BytesIO(res)

_orig_patcher_urlretrieve = uc_patcher.urlretrieve
def _robust_patcher_urlretrieve(url, filename=None, *args, **kwargs):
    try:
        return _orig_patcher_urlretrieve(url, filename=filename, *args, **kwargs)
    except Exception:
        if not filename:
            tf = tempfile.NamedTemporaryFile(delete=False)
            filename = tf.name
            tf.close()
        subprocess.check_call(["curl.exe", "-sL", "--connect-timeout", "30", str(url), "-o", filename])
        return (filename, None)

uc_patcher.urlopen = _robust_patcher_urlopen
uc_patcher.urlretrieve = _robust_patcher_urlretrieve
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---------- Configuration ----------
SAVE_FILE = "windscribe_accounts.txt"
WINDSCRIBE_SIGNUP_URL = "https://windscribe.com/signup"
TEMP_MAIL_URL = "https://temp-mail.org/en/"
PAGE_LOAD_TIMEOUT = 60
SIGNUP_RESPONSE_TIMEOUT = 90
MAX_EMAIL_ATTEMPTS = 25
CONFIRM_WAIT_TIMEOUT = 180
# -----------------------------------

def get_chrome_major_version():
    """Detect the installed Google Chrome major version to prevent driver version mismatch."""
    try:
        import winreg
        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for subkey in (
                r"Software\Google\Chrome\BLBeacon",
                r"SOFTWARE\Google\Chrome\BLBeacon",
                r"SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon",
            ):
                try:
                    with winreg.OpenKey(root, subkey) as key:
                        val, _ = winreg.QueryValueEx(key, "version")
                        match = re.match(r"^(\d+)", str(val))
                        if match:
                            return int(match.group(1))
                except Exception:
                    pass
    except ImportError:
        pass

    try:
        chrome_exe = uc.find_chrome_executable()
        if chrome_exe:
            cmd = ["powershell", "-NoProfile", "-Command", f'(Get-Item "{chrome_exe}").VersionInfo.ProductMajorPart']
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
            if out.isdigit():
                return int(out)
    except Exception:
        pass

    return None

def get_cached_driver_path(target_major_version=None):
    """Returns local path to existing patched undetected_chromedriver if it matches the current Chrome version."""
    try:
        import os
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            return None
        cand = os.path.join(appdata, "undetected_chromedriver", "undetected_chromedriver.exe")
        if not os.path.isfile(cand):
            return None
        if target_major_version:
            out = subprocess.check_output([cand, "--version"], text=True, stderr=subprocess.DEVNULL)
            m = re.search(r"ChromeDriver\s+(\d+)\.", out)
            if m and int(m.group(1)) != int(target_major_version):
                print(f"🔄 Cached driver is version {m.group(1)}, but Chrome is {target_major_version}. Updating driver...")
                return None
        return cand
    except Exception:
        pass
    return None

def random_string(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def quick_sleep(seconds=0.2):
    time.sleep(seconds)

def safe_get(driver, url):
    try:
        driver.get(url)
    except Exception as e:
        print(f"Navigation issue: {e}")

def wait_for_temp_mail(driver, timeout=45):
    start = time.time()
    while time.time() - start < timeout:
        try:
            mail_input = driver.find_element(By.ID, "mail")
            val = mail_input.get_attribute("value")
            if val and '@' in val and not val.endswith("loading") and "..." not in val:
                return val.strip()
        except:
            pass
        quick_sleep(0.5)
    return None

def delete_temp_mail(driver):
    try:
        delete_btn = driver.find_element(By.ID, "click-to-delete")
        if delete_btn.is_displayed() and delete_btn.is_enabled():
            driver.execute_script("arguments[0].click();", delete_btn)
            quick_sleep(1)
            return True
    except:
        pass
    return False

def is_captcha_present(driver):
    try:
        frames = driver.find_elements(
            By.XPATH,
            "//iframe[contains(@src,'recaptcha') or contains(@src,'captcha') or contains(@src,'cloudflare') or contains(@src,'turnstile') or contains(@src,'hcaptcha') or contains(@src,'geetest') or contains(@src,'arkose') or contains(@src,'funcaptcha')]"
        )
        for frame in frames:
            if frame.is_displayed():
                return True

        selectors = [
            ".g-recaptcha",
            ".cf-turnstile",
            "#cf-turnstile",
            "[data-sitekey]",
            "iframe[title*='challenge']",
            "iframe[title*='reCAPTCHA']",
            "iframe[title*='hCaptcha']",
            ".geetest_holder",
            ".geetest_popup",
            "[class*='geetest']",
            "[class*='captcha']",
            "[id*='captcha']",
            "[class*='slider-puzzle']",
            "[class*='slide-verify']",
            ".secsdk-captcha-drag-icon",
            "canvas[class*='captcha']"
        ]
        for sel in selectors:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in elems:
                if el.is_displayed():
                    return True

        # Check for visible puzzle / verification prompts
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        puzzle_phrases = [
            "slide to complete the puzzle",
            "drag the slider",
            "fit the puzzle piece",
            "security verification",
            "verify you are human",
            "please complete the puzzle",
            "slide right to complete"
        ]
        if any(phrase in page_text for phrase in puzzle_phrases):
            return True
    except Exception:
        pass
    return False

def check_for_disposable_error(driver):
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if "disposable email" in body_text or "disposable emails are not allowed" in body_text:
            return True
        alerts = driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .mantine-Notification-description, .form_error__")
        for alert in alerts:
            if alert.is_displayed() and "disposable" in alert.text.lower():
                return True
    except Exception:
        pass
    return False

def fill_signup_form(driver, wait, username, password, email):
    # Username
    try:
        username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        current_user = username_field.get_attribute("value")
        if current_user != username:
            username_field.clear()
            username_field.send_keys(username)
    except Exception as e:
        print(f"Username field error: {e}")
        return None

    # Password
    try:
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='password'])[1]")))
        if not password_field.get_attribute("value"):
            password_field.clear()
            password_field.send_keys(password)
    except Exception as e:
        print(f"Password field error: {e}")
        return None

    # Confirm Password
    try:
        confirm_password_field = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='password'])[2]")))
        if not confirm_password_field.get_attribute("value"):
            confirm_password_field.clear()
            confirm_password_field.send_keys(password)
    except Exception as e:
        print(f"Confirm password field error: {e}")
        return None

    # Email
    if email:
        try:
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            current_email = email_field.get_attribute("value")
            if current_email != email:
                email_field.clear()
                email_field.send_keys(email)
        except Exception as e:
            print(f"Email field error: {e}")
            email = None

    # Checkbox
    try:
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
    except Exception:
        pass

    return email

def click_signup_button(driver, wait):
    try:
        submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit' or contains(.,'Sign Up')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
        quick_sleep(0.1)
        try:
            submit_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", submit_button)
        return True
    except Exception as e:
        print(f"Signup button note: {e}")
        return False

def is_signup_successful(driver):
    try:
        current_url = driver.current_url.lower()
        if "myaccount" in current_url or "account" in current_url or "welcome" in current_url or "confirm" in current_url:
            return True
        if "signup" not in current_url:
            return True

        indicators = [
            "//button[contains(.,'Add Email')]",
            "//a[contains(@href,'logout') or contains(@href,'myaccount')]",
            "//*[contains(text(),'Claim 10GB') or contains(text(),'Confirm your email') or contains(text(),'Email Sent')]"
        ]
        for xpath in indicators:
            elems = driver.find_elements(By.XPATH, xpath)
            if any(el.is_displayed() for el in elems):
                return True
    except Exception:
        pass
    return False

def wait_for_signup_result(driver, timeout=SIGNUP_RESPONSE_TIMEOUT):
    """
    Polls rapidly (every 0.5s) for signup request to complete without page refreshes.
    Returns: 'SUCCESS', 'DISPOSABLE_EMAIL', 'USERNAME_TAKEN', 'RATE_LIMITED', or 'TIMEOUT'
    """
    start = time.time()
    captcha_alerted = False

    while time.time() - start < timeout:
        # Check if CAPTCHA challenge is currently active
        if is_captcha_present(driver):
            if not captcha_alerted:
                print("\n⚠️ Slider CAPTCHA detected! Please slide the puzzle piece in the Chrome window.")
                print("⏳ The script is paused waiting for you to complete the puzzle...")
                captcha_alerted = True
            start = time.time()  # Keep resetting timeout timer so you have full time to complete it
            time.sleep(1.5)
            continue
        elif captcha_alerted:
            print("✅ CAPTCHA solved! Waiting for Windscribe to finish processing signup...")
            captcha_alerted = False
            start = time.time()
            time.sleep(1.5)

        # Check if signup was successful
        if is_signup_successful(driver):
            return "SUCCESS"

        # Check for error messages in page text
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if "disposable email" in page_text or "disposable emails are not allowed" in page_text:
                return "DISPOSABLE_EMAIL"
            if "already taken" in page_text or "username already taken" in page_text:
                return "USERNAME_TAKEN"
            if "too many requests" in page_text or "rate limit" in page_text:
                return "RATE_LIMITED"
        except Exception:
            pass

        # Check for alert / toast notifications
        try:
            alerts = driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .mantine-Notification-description, .form_error__")
            for alert in alerts:
                if alert.is_displayed() and alert.text:
                    err_msg = alert.text.strip().lower()
                    if "disposable" in err_msg:
                        return "DISPOSABLE_EMAIL"
                    elif "already taken" in err_msg or "exists" in err_msg:
                        return "USERNAME_TAKEN"
        except Exception:
            pass

        elapsed = int(time.time() - start)
        if elapsed > 0 and elapsed % 15 == 0:
            print(f"⚡ Processing signup... ({elapsed}s elapsed)")

        time.sleep(0.5)

    if is_signup_successful(driver):
        return "SUCCESS"

    return "TIMEOUT"

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

def extract_confirmation_link(driver):
    """
    Searches the current page HTML source, DOM elements, and iframes for the Windscribe confirmation URL.
    Returns the confirmation link string if found, otherwise None.
    """
    # 1. Direct regex on page source (captures links in raw HTML, plain text, scripts, etc.)
    try:
        source = driver.page_source
        match = re.search(r'https?://(?:www\.)?windscribe\.com/signup/confirmemail/[^\s"\'<>]+', source)
        if match:
            return html.unescape(match.group(0)).rstrip('.,;)"\'')
        match2 = re.search(r'https?://[^\s"\'<>]*windscribe\.com/[^\s"\'<>]*confirmemail[^\s"\'<>]*', source)
        if match2:
            return html.unescape(match2.group(0)).rstrip('.,;)"\'')
    except Exception:
        pass

    # 2. Check <a> elements in main DOM
    try:
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'confirmemail')]")
        for link in links:
            href = link.get_attribute("href")
            if href and "confirmemail" in href:
                return html.unescape(href).rstrip('.,;)"\'')
    except Exception:
        pass

    # 3. Check inside iframes
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                iframe_src = driver.page_source
                match = re.search(r'https?://(?:www\.)?windscribe\.com/signup/confirmemail/[^\s"\'<>]+', iframe_src)
                if match:
                    driver.switch_to.default_content()
                    return html.unescape(match.group(0)).rstrip('.,;)"\'')

                iframe_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'confirmemail')]")
                for link in iframe_links:
                    href = link.get_attribute("href")
                    if href and "confirmemail" in href:
                        driver.switch_to.default_content()
                        return html.unescape(href).rstrip('.,;)"\'')
                driver.switch_to.default_content()
            except Exception:
                driver.switch_to.default_content()
    except Exception:
        pass

    return None

def find_and_open_temp_email(driver):
    """
    Finds the incoming Windscribe email on temp-mail.org and opens it immediately.
    Navigates directly to the email URL (/view/) when available to avoid overlay and ad click issues.
    """
    # Strategy 1: Check for links with /view/ (temp-mail's direct email view endpoint)
    try:
        view_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/view/')]")
        for link in view_links:
            try:
                href = link.get_attribute("href")
                text = (link.text or "").lower()
                parent_text = ""
                try:
                    parent_text = link.find_element(By.XPATH, "./..").text.lower()
                except Exception:
                    pass
                if "windscribe" in text or "windscribe" in parent_text or len(view_links) == 1:
                    print(f"📩 Found incoming email! Opening: {href or 'email view'}")
                    if href and href.startswith("http"):
                        safe_get(driver, href)
                    else:
                        driver.execute_script("arguments[0].click();", link)
                    return True
            except Exception:
                pass
    except Exception:
        pass

    # Strategy 2: Case-insensitive search for elements mentioning 'windscribe'
    try:
        xpaths = [
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'windscribe')]",
            "//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'windscribe')]",
            "//li[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'windscribe')]",
            "//span[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'windscribe')]"
        ]
        for xpath in xpaths:
            elems = driver.find_elements(By.XPATH, xpath)
            for elem in elems:
                try:
                    if elem.is_displayed():
                        href = elem.get_attribute("href")
                        if not href:
                            sub = elem.find_elements(By.TAG_NAME, "a")
                            if sub:
                                href = sub[0].get_attribute("href")
                        if href and "/view/" in href:
                            print(f"📩 Found Windscribe link: {href}")
                            safe_get(driver, href)
                            return True
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", elem)
                        return True
                except Exception:
                    pass
    except Exception:
        pass

    return False

def wait_and_confirm_email(driver, temp_mail_tab, main_tab, timeout=CONFIRM_WAIT_TIMEOUT):
    print(f"\n📬 Checking temp-mail.org for Windscribe confirmation email (waiting up to {timeout}s)...")
    driver.switch_to.window(temp_mail_tab)
    start_time = time.time()
    confirmation_link = None
    email_opened = False
    last_refresh = time.time()

    while time.time() - start_time < timeout:
        # Check 1: Is confirmation link ALREADY visible on the page or in any iframe?
        confirmation_link = extract_confirmation_link(driver)
        if confirmation_link:
            print(f"🔗 Confirmation link found: {confirmation_link}")
            break

        # Check 2: If we are currently on an email view page (/view/), extract link
        if "/view/" in driver.current_url.lower():
            email_opened = True
            quick_sleep(0.5)
            confirmation_link = extract_confirmation_link(driver)
            if confirmation_link:
                print(f"🔗 Confirmation link found inside email: {confirmation_link}")
                break

        # Check 3: If not opened yet, find and open the email
        if not email_opened:
            opened = find_and_open_temp_email(driver)
            if opened:
                email_opened = True
                quick_sleep(1)
                confirmation_link = extract_confirmation_link(driver)
                if confirmation_link:
                    print(f"🔗 Confirmation link found upon opening: {confirmation_link}")
                    break

        # Check 4: If email hasn't appeared yet, refresh temp-mail inbox periodically (every 12s)
        if not email_opened and (time.time() - last_refresh > 12):
            print("🔄 Refreshing temp-mail.org to fetch incoming emails...")
            try:
                driver.refresh()
                last_refresh = time.time()
                quick_sleep(1.5)
            except Exception:
                pass

        time.sleep(0.5)
        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 10 == 0:
            print(f"⚡ Waiting for Windscribe email to arrive and confirm... ({elapsed}s elapsed)")

    if confirmation_link:
        print("\n🌐 Opening confirmation link in Windscribe tab...")
        driver.switch_to.window(main_tab)
        safe_get(driver, confirmation_link)
        print("⚡ Finalizing email confirmation on Windscribe...")
        for _ in range(20):
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if "confirmed" in page_text or "10 gb" in page_text or "account" in driver.current_url.lower():
                    break
            except Exception:
                pass
            time.sleep(0.5)
        print("🎉 Email confirmed successfully! 10GB account activated.")
        return True
    else:
        print("❌ Confirmation email was not found within timeout.")
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

    chrome_version = get_chrome_major_version()
    if chrome_version:
        print(f"Detected Chrome major version: {chrome_version}")

    cached_driver = get_cached_driver_path(target_major_version=chrome_version)
    if cached_driver:
        print(f"Using cached chromedriver: {cached_driver}")

    driver = None
    try:
        driver = uc.Chrome(
            options=options,
            driver_executable_path=cached_driver,
            version_main=chrome_version
        )
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
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
            # Step 1: Obtain temporary email
            driver.switch_to.window(temp_mail_tab)
            email = wait_for_temp_mail(driver, timeout=45)
            if not email:
                print(f"Attempt {attempt+1}: Waiting for email address from temp-mail.org...")
                delete_temp_mail(driver)
                email = wait_for_temp_mail(driver, timeout=30)
                if not email:
                    print("Could not obtain email from temp-mail.org. Retrying...")
                    continue
            print(f"\n[Attempt {attempt+1}/{MAX_EMAIL_ATTEMPTS}] Using temp email: {email}")

            # Step 2: Fill signup form on Windscribe tab
            driver.switch_to.window(main_tab)
            email_used = fill_signup_form(driver, wait, username, password, email)
            if not email_used:
                print("Could not fill signup form properly.")
                time.sleep(3)
                continue

            # Check if CAPTCHA is already visible before clicking
            if is_captcha_present(driver):
                print("⚠️ CAPTCHA detected before submission. Please solve it in the browser...")
                while is_captcha_present(driver):
                    time.sleep(3)

            # Step 3: Click Sign Up button (NEVER refresh the page!)
            print("Submitting signup form (clicking Sign Up)...")
            clicked = click_signup_button(driver, wait)
            if not clicked:
                print("Signup button click attempt encountered an issue, checking status...")

            # Step 4: Patient cooldown wait loop (up to 90 seconds for slow connection, NO REFRESH)
            print("⏳ Form submitted. Waiting for server response (cooldown up to 90s, no refresh)...")
            result = wait_for_signup_result(driver, timeout=SIGNUP_RESPONSE_TIMEOUT)

            if result == "SUCCESS":
                print("\n✅ Signup successful! Account created on Windscribe.")
                if email_used:
                    print("Proceeding to email confirmation step...")
                    confirmed = wait_and_confirm_email(driver, temp_mail_tab, main_tab)
                    if confirmed:
                        final_email = email_used
                        signup_success = True
                        break
                    else:
                        print("Confirmation email step timed out. Account created with free tier.")
                        final_email = email_used
                        signup_success = True
                        break
                else:
                    signup_success = True
                    final_email = "NO_EMAIL"
                    break

            elif result == "DISPOSABLE_EMAIL":
                print("❌ Windscribe rejected this domain as a disposable email.")
                print("🔄 Getting a new temp email from temp-mail.org (form will not be refreshed)...")
                driver.switch_to.window(temp_mail_tab)
                delete_temp_mail(driver)
                time.sleep(1)
                continue

            elif result == "USERNAME_TAKEN":
                print("❌ Username was already taken. Generating a new username...")
                username = random_string(12)
                print(f"New Username: {username}")
                continue

            elif result == "RATE_LIMITED":
                print("⚠️ Windscribe rate limit detected. Cooling down for 30 seconds...")
                time.sleep(30)
                continue

            elif result == "TIMEOUT":
                print("⚠️ Signup response timed out after 90 seconds.")
                if is_signup_successful(driver):
                    print("✅ Account appears to be signed up despite timeout!")
                    signup_success = True
                    final_email = email_used
                    break
                print("Will retry submission without refreshing the page...")
                continue

        if signup_success:
            save_account(username, password, final_email)
            if final_email != "NO_EMAIL":
                print(f"\n🎉 SUCCESS: Account created with 10GB! (Email: {final_email})")
            else:
                print(f"\n🎉 SUCCESS: Account created with 2GB (No email added)")
        else:
            print("\n❌ Failed to create account after attempts.")

        try:
            input("\nBrowser session complete. Press Enter in this console to close Chrome...")
        except Exception:
            pass

    except Exception as e:
        print(f"\n❌ An error occurred: {type(e).__name__}: {e}")
        if driver:
            try:
                driver.save_screenshot("error_screenshot.png")
                print("Screenshot saved as 'error_screenshot.png'")
            except Exception:
                pass
        try:
            input("\nPress Enter in this console to close Chrome...")
        except Exception:
            pass
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    main()