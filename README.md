# Windscribe 10GB Account Generator

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

Automate the creation of **Windscribe accounts with 10GB/month free bandwidth** by using temporary email addresses from [temp-mail.org](https://temp-mail.org/). The script handles signup, temporary email retrieval, email confirmation, and credential storage all in one click – it even installs any missing Python packages automatically.

---

## ⚠️ Disclaimer

This project is intended **for educational purposes only**. Creating multiple Windscribe accounts may violate [Windscribe's Terms of Service](https://windscribe.com/terms). Use this tool responsibly and at your own risk. The developers are not responsible for any account bans, legal consequences, or misuse.

---

## ✨ Features

- ✅ **One-click setup** – automatically installs required Python packages on first run.
- ✅ **Fully automated signup** – no manual interaction except CAPTCHA solving.
- ✅ **Temporary email integration** – uses [temp-mail.org](https://temp-mail.org/) automatically.
- ✅ **Email filled directly in signup form** – no post-signup modal, no 2GB fallback.
- ✅ **Automatic email confirmation** – retrieves and clicks the confirmation link.
- ✅ **Retry logic** – if an email is rejected, it tries a new one (up to 10 attempts).
- ✅ **CAPTCHA handling** – waits a configurable number of seconds for manual solving.
- ✅ **Credential saving** – stores accounts in a clean, numbered format in `windscribe_accounts.txt`.
- ✅ **Stealth mode** – uses `undetected-chromedriver` to avoid bot detection.

---

## 🧠 How It Works

1. Launches an undetected Chrome browser.
2. Opens [temp-mail.org](https://temp-mail.org/) in a new tab and extracts a temporary email address.
3. Opens the Windscribe signup page and fills in a random username, password, and the temporary email.
4. If a CAPTCHA appears, the script waits for you to solve it (default 10 seconds).
5. Submits the signup form.
6. Waits for the confirmation email in [temp-mail.org](https://temp-mail.org/), clicks it, and opens the confirmation link.
7. Saves the account details to `windscribe_accounts.txt`.

---

## 📋 Requirements

- **Python 3.7 or higher** (tested on 3.10–3.14)
- **Google Chrome** installed on your system
- Internet connection

> **Note:** No manual installation of Python packages is needed – the script will install them automatically on first run.

---

## 🚀 Usage

1. Download `windscribe_automation.py`.
2. Run it:

```bash
python windscribe_automation.py
```

*Or simply double-click the file if Python is associated.*

### What the script does:
1. Checks for missing packages and installs them automatically.
2. Opens Chrome and starts the process.
3. Waits for you to solve any CAPTCHA (default 10 seconds).
4. Saves the account to `windscribe_accounts.txt`.

### Output format

```text
Account #1
Username: AbC123XyZ
Password: Passw0rd123
Email: example@temp-mail.org
------------------------------
```

> If email addition fails, `Email` will be `NO_EMAIL` (account still works with 2GB).

---

## ⚙️ Configuration

You can modify these variables at the top of `windscribe_automation.py`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SAVE_FILE` | `"windscribe_accounts.txt"` | File where credentials are saved |
| `CAPTCHA_WAIT_TIME` | `10` | Seconds to wait for manual CAPTCHA solving |
| `TEMP_MAIL_URL` | `"https://temp-mail.org/en/"` | Temporary email service URL |
| `MAX_EMAIL_ATTEMPTS` | `10` | Maximum attempts to get a working email |
| `CONFIRM_WAIT_TIMEOUT` | `180` | Seconds to wait for confirmation email |

> **Tip:** To run headless (no GUI), add `--headless=new` to the Chrome options in the script.

---

## 🛠 Troubleshooting

### `OSError: [WinError 6] The handle is invalid`
This harmless error appears during cleanup. It does not affect functionality. Ignore it.

### `temp-mail.org is blocked (Cloudflare)`
The script uses `undetected-chromedriver` to reduce detection, but sometimes it still gets blocked.
- Try using a different network or a proxy.
- Add a proxy to Chrome options:

```python
options.add_argument('--proxy-server=http://user:pass@host:port')
```

### CAPTCHA not being solved
The script waits a fixed time (`CAPTCHA_WAIT_TIME`). Increase this value if you need more time.

### Email rejected as disposable
The script automatically tries a new temp email (up to `MAX_EMAIL_ATTEMPTS`).

---

## 📁 File Structure

```text
.
├── windscribe_automation.py   # Main script (self-installing)
├── README.md                  # This file
└── .gitignore                 # Ignore generated files
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
