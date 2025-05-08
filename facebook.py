import os
import time
from tkinter import Tk, Label, Entry, Button, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF

# Secure password input (optional for CLI)
import getpass

def login_facebook(driver, email, password):
    driver.get("https://www.facebook.com/login")
    time.sleep(2)

    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "pass")
    login_button = driver.find_element(By.NAME, "login")

    email_input.send_keys(email)
    password_input.send_keys(password)
    login_button.click()
    time.sleep(5)

def close_notifications(driver):
    try:
        not_now_button = driver.find_element(By.XPATH, '//div[@aria-label="Not Now"]')
        not_now_button.click()
        time.sleep(2)
    except Exception:
        pass

def extract_friends(driver, username):
    driver.get("https://www.facebook.com/me/friends")
    time.sleep(5)

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    friends = driver.find_elements(By.XPATH, '//a[contains(@href,"/friends/hovercard/")]/div[2]/div[1]/span/span')
    friend_names = [friend.text for friend in friends if friend.text]

    report_folder = get_report_folder()
    friends_file = os.path.join(report_folder, f"{username}_friends.txt")
    with open(friends_file, "w", encoding="utf-8") as f:
        for name in friend_names:
            f.write(name + "\n")

    print(f"Extracted {len(friend_names)} friends to {friends_file}")

def take_screenshot(driver, name):
    report_folder = get_report_folder()
    screenshot_name = os.path.join(report_folder, f"facebook_{name}.png")
    driver.save_screenshot(screenshot_name)
    print(f"Screenshot saved as {screenshot_name}")

def get_report_folder():
    folder = "facebook_data"
    os.makedirs(folder, exist_ok=True)
    return folder

def generate_pdf_report(username):
    report_folder = get_report_folder()
    pdf_output_path = os.path.join(report_folder, f"{username}_report.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Facebook Data Report", ln=True, align="C")

    for image in [f"facebook_homepage.png", f"facebook_profile.png"]:
        image_path = os.path.join(report_folder, image)
        if os.path.exists(image_path):
            pdf.add_page()
            pdf.image(image_path, x=10, y=30, w=180)

    friends_file = os.path.join(report_folder, f"{username}_friends.txt")
    if os.path.exists(friends_file):
        with open(friends_file, "r", encoding="utf-8") as f:
            friends = f.readlines()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="Friends List:\n" + "".join(friends))

    pdf.output(pdf_output_path)
    print(f"PDF report saved to {pdf_output_path}")
    encrypt_pdf(pdf_output_path, "securepassword123")

def encrypt_pdf(path, password):
    reader = PdfReader(path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)
    encrypted_path = path.replace(".pdf", "_encrypted.pdf")
    with open(encrypted_path, "wb") as f:
        writer.write(f)

    print(f"Encrypted PDF saved to {encrypted_path}")

def main(email, password):
    username = email.split('@')[0]

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        login_facebook(driver, email, password)
        close_notifications(driver)

        take_screenshot(driver, "homepage")
        driver.get("https://www.facebook.com/me")
        time.sleep(3)
        take_screenshot(driver, "profile")

        extract_friends(driver, username)
        generate_pdf_report(username)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# GUI
class FacebookScraperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Facebook Data Extractor")
        master.geometry("400x200")

        Label(master, text="Facebook Email:").pack(pady=5)
        self.email_entry = Entry(master, width=40)
        self.email_entry.pack()

        Label(master, text="Facebook Password:").pack(pady=5)
        self.password_entry = Entry(master, show="*", width=40)
        self.password_entry.pack()

        Button(master, text="Start Extraction", command=self.start_scraper).pack(pady=10)

    def start_scraper(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        try:
            main(email, password)
            messagebox.showinfo("Done", "Facebook data extraction completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = FacebookScraperGUI(root)
    root.mainloop()
