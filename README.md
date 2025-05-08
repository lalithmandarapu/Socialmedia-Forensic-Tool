# 📊 Social Media Forensic Tool

A powerful forensic tool designed to extract and analyze user data from major social media platforms including **Facebook**, **WhatsApp**, **Instagram**, **Google**, and **Twitter**. This tool helps in the investigation of user behavior, friend connections, and content interactions by creating structured reports with screenshots and data exports.

---

## 🚀 Features

| Platform   | Features                                                                 |
|------------|--------------------------------------------------------------------------|
| **Facebook** | Login automation, screenshot capture (homepage/profile), friend list extraction, PDF report generation |
| **WhatsApp** | Chat export parsing (from `.txt`), contact extraction, date-wise message analysis |
| **Instagram** | Follower/following scraping, profile picture capture, PDF generation |
| **Google** | Search history extraction, PDF report of queries and timestamps (requires access to user data export) |
| **Twitter** | Tweet scraping (latest tweets), follower list, screenshots, PDF summary |

---

## 🔐 Security Features

- Password fields are masked.
- PDF reports are encrypted with user-defined passwords using `PyPDF2`.
- No sensitive information is stored or logged permanently.
- HTTPS-based automated login to ensure encrypted transmission.
- Folder structure is secured and created per-user session.

---

## 🛠️ Installation

### ✅ Requirements

- Python 3.7 or higher
- Google Chrome browser (latest version)
- ChromeDriver (automatically handled by `webdriver-manager`)

### 📦 Dependencies

Install all required Python packages:

```bash
pip install selenium
pip install webdriver-manager
pip install fpdf
pip install cryptography
pip install PyPDF2
