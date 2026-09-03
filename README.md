# Windscribe 10GB Account Generator

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

Automate the creation of **Windscribe accounts with 10GB/month free bandwidth** by using temporary email addresses. The script handles signup, temporary email retrieval, email confirmation, and credential storage.

---

## ⚠️ Disclaimer

This project is intended **for educational purposes only**. Creating multiple Windscribe accounts may violate [Windscribe's Terms of Service](https://windscribe.com/terms). Use this tool responsibly and at your own risk. The developers are not responsible for any account bans, legal consequences, or misuse.

---

## ✨ Features

- ✅ **Fully automated signup** – no manual interaction except CAPTCHA solving.
- ✅ **Temporary email integration** – uses temp-mail.org automatically.
- ✅ **Automatic email confirmation** – retrieves and clicks the confirmation link.
- ✅ **Retry logic** – if an email is rejected (disposable), it tries a new one.
- ✅ **CAPTCHA handling** – pauses for manual solving when required.
- ✅ **Credential saving** – stores accounts in `windscribe_accounts.txt` as `username:password:email`.
- ✅ **Handles both 10GB and 2GB accounts** – if email addition fails, account is saved without email.
- ✅ **Stealth mode** – uses `undetected-chromedriver` to avoid bot detection.

---

## 🧠 How It Works

1. Launches a Chrome browser (undetected).
2. Opens the Windscribe signup page and fills in a random username and password.
3. Leaves the email field empty during initial signup.
4. After signup, it clicks **Add Email** in the post-signup modal.
5. Opens temp-mail.org in a new tab, extracts the temporary email address.
6. Pastes that email into Windscribe and submits.
7. If a CAPTCHA appears, you must solve it manually.
8. Once accepted, the script switches back to temp-mail.org, waits for the Windscribe confirmation email, clicks it, and opens the confirmation link.
9. Credentials are saved to `windscribe_accounts.txt`.

---

## 📋 Requirements

- **Python 3.7 or higher** (tested on 3.10–3.14)
- **Google Chrome** installed on your system
- Internet connection

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/windscribe-10gb-account-generator.git
cd windscribe-10gb-account-generator
