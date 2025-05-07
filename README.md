# 🔍 Social Media Forensic Tool

A Python-based GUI application that performs social media scraping with a secure login system. The tool supports scraping from platforms like Instagram, Google, WhatsApp, Twitter, and Facebook. It features a login system with hashed passwords and a custom CAPTCHA using two-digit math problems (addition and subtraction) to enhance security.

---

## 🚀 Features

- 🔐 **Secure Login System**
  - Passwords are hashed using bcrypt
  - CAPTCHA with two-digit addition or subtraction
- 🧩 **Modular Platform Integration**
  - Instagram
  - Google
  - WhatsApp
  - Twitter
  - Facebook
- 🧵 **Threaded Execution**
  - Prevents GUI freezing during scraping
- 🎨 **Custom GUI**
  - Built using `tkinter`
  - Custom rounded buttons
  - Optional background image

---

## 📦 Requirements

- Python 3.x
- Libraries:
  - `bcrypt`
  - `tkinter` (built-in with Python)
- Custom scraper modules:
  - `insta_scraper.py`
  - `google_scraper.py`
  - `whatsapp.py`
  - `twitter.py`
  - `facebook.py`

Install required external packages:

```bash
pip install bcrypt
