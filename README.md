# Windscribe 10GB Account Generator

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

Automate the creation of **Windscribe accounts with 10GB/month free bandwidth** by using temporary email addresses from [temp-mail.org](https://temp-mail.org). The script handles signup, temporary email retrieval, email confirmation, and credential storage.

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
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If you’re using Python 3.14+ and get a `ModuleNotFoundError: No module named 'distutils'`, run:

```bash
pip install setuptools
```

---

## 🚀 Usage

Run the script:

```bash
python windscribe_automation.py
```

The script will open a Chrome window and start the process. Do not close the browser while it runs.

### What you need to do manually:

Solve CAPTCHAs when prompted. The script will wait for you to solve them and press Enter in the terminal.

### Output

Generated accounts are appended to `windscribe_accounts.txt` in the format:

```text
username:password:email
```

**Example:**

```text
Ta7rLWoWedHn:Xk3nF9pQz2:gokiweg233@mediseat.com
```

If email addition fails, the email field will be `NO_EMAIL` (account still works with 2GB).

---

## ⚙️ Configuration

You can modify the script’s variables at the top:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SAVE_FILE` | `"windscribe_accounts.txt"` | File where credentials are saved |
| `CAPTCHA_WAIT_TIMEOUT` | `300` | Seconds to wait for manual CAPTCHA solving |
| `TEMP_MAIL_URL` | `"https://temp-mail.org/en/"` | Temporary email service URL |
| `MAX_TEMP_MAIL_ATTEMPTS` | `10` | Maximum attempts to get a working email |
| `PAGE_LOAD_TIMEOUT` | `30` | Page load timeout in seconds |

> **Tip:** To run headless (no GUI), add `--headless=new` to Chrome options in the script.

---

## 🛠 Troubleshooting

### `OSError: [WinError 6] The handle is invalid`
This harmless error appears during cleanup. It does not affect functionality. You can ignore it.

### `temp-mail.org is blocked (Cloudflare)`
The script uses `undetected-chromedriver` to reduce detection, but sometimes it still gets blocked.
- Try using a different network or a proxy.
- If you set up a proxy, add it to the Chrome options:

```python
options.add_argument('--proxy-server=http://user:pass@host:port')
```

### CAPTCHA not being solved
The script waits for manual solving. Ensure the browser window is visible and you have enough time.
For full automation, integrate a CAPTCHA solving service like [2captcha](https://2captcha.com/) or [Anti-Captcha](https://anti-captcha.com/).

### Email rejected as disposable
The script automatically tries a new temp email (up to `MAX_TEMP_MAIL_ATTEMPTS`).
If all attempts fail, you can manually add a different temporary email provider by editing the script.

---

## 🌐 Deploying on a VPS (Headless Server)

To run this on a Linux VPS without a GUI, you need to:
1. Install Chrome/Chromium and dependencies (see Dockerfile).
2. Use `--headless=new` in Chrome options.
3. Integrate a CAPTCHA solving service (manual solving is not possible on a server).

A Dockerfile is provided for easy containerization:

```bash
docker build -t windscribe-generator .
docker run -it --rm -v $(pwd):/app windscribe-generator
```

> **Note:** For production web service, consider wrapping the script in Flask/FastAPI with a queue system, proxy rotation, and CAPTCHA solver.

---

## 📁 File Structure

```text
.
├── windscribe_automation.py   # Main script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Ignore generated files
└── Dockerfile                 # For containerized deployment (optional)
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⭐ Show Your Support

If this project helped you, please give it a star on GitHub!
