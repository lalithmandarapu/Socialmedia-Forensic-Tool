import tkinter as tk
from tkinter import messagebox, font
import threading

import os
import time
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# New function to create and get the report folder path
def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Facebook Report")
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    return report_folder


# Function to log in to Facebook
def login_facebook(driver, email, password):
    driver.get("https://www.facebook.com/login")
    time.sleep(2)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    time.sleep(5)

# Function to take a screenshot
def take_screenshot(driver, file_path):
    driver.save_screenshot(file_path)

def take_screenshot(driver, name):
    report_folder = get_report_folder()
    screenshot_name = os.path.join(report_folder, f"facebook_{name}.png")
    driver.save_screenshot(screenshot_name)
    print(f"Screenshot saved as {screenshot_name}")

# Function to close notifications
def close_notifications(driver):
    try:
        notification_close_button = driver.find_element(By.XPATH, "//div[@aria-label='Close']")
        notification_close_button.click()
        time.sleep(2)  # Allow time for notification to close
    except Exception as e:
        print("No notifications to close or error in closing:", e)

def extract_friends(driver, username):
    report_folder = get_report_folder()
    friends_file_path = os.path.join(report_folder, f"{username}_friends.txt")
    
    driver.get("https://www.facebook.com/me/friends")
    time.sleep(5)  # Wait for the page to load
    
    friends = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for page to load
        
        # Extract friends
        friend_elements = driver.find_elements(By.XPATH, "//div[@class='x1iyjqo2 x1pi30zi']/div/a")
        for element in friend_elements:
            friend_name = element.text.strip()
            if friend_name and friend_name not in friends:
                friends.append(friend_name)
        
        # Check if we've reached the end of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Save friends to file
    with open(friends_file_path, 'w', encoding='utf-8') as f:
        for friend in friends:
            f.write(f"{friend}\n")
    
    print(f"Extracted {len(friends)} friends and saved to {friends_file_path}")
    return friends_file_path

# Function to generate a PDF report using FPDF
def generate_pdf_report(username):
    report_folder = get_report_folder()
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(200, 10, txt="Facebook Report", ln=True, align="C")
    pdf.ln(10)
    
    # Function to add a section with image and title
    def add_section(title, image_path):
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt=title, ln=True)
        pdf.image(image_path, x=10, y=pdf.get_y(), w=190)
        pdf.ln(140)  # Adjust this value based on your image size

    # Homepage screenshot
    homepage_screenshot = os.path.join(report_folder, "facebook_homepage.png")
    add_section("Homepage", homepage_screenshot)

    # Profile screenshot
    profile_screenshot = os.path.join(report_folder, "facebook_profile.png")
    add_section("Profile", profile_screenshot)

    # Friends List
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Friends List", ln=True)
    pdf.ln(5)

    friends_file_path = os.path.join(report_folder, f"{username}_friends.txt")
    if os.path.exists(friends_file_path):
        pdf.set_font("Arial", size=10)
        with open(friends_file_path, 'r', encoding='utf-8') as f:
            friends = f.readlines()
        
        # Calculate the number of columns based on the page width
        col_width = 60
        num_cols = 3
        
        for i, friend in enumerate(friends):
            if i % num_cols == 0 and i != 0:
                pdf.ln()
            pdf.cell(col_width, 10, txt=friend.strip()[:30], border=1)  # Limit name length to 30 characters
        
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Total Friends: {len(friends)}", ln=True)
    else:
        pdf.cell(200, 10, txt="Friends list not available", ln=True)

    # Save the PDF
    pdf_output_path = os.path.join(report_folder, f"{username}_facebook_report.pdf")
    pdf.output(pdf_output_path)
    
    print(f"Generated PDF report for user {username} at {pdf_output_path}")


class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, relief="flat", 
                           highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5 * width or cornerradius > 0.5 * height:
            print("Error: cornerradius is too large.")
            return None

        rad = 2 * cornerradius

        def shape():
            self.create_polygon((padding, height - cornerradius - padding, padding, cornerradius + padding,
                                 padding + cornerradius, padding, width - padding - cornerradius, padding,
                                 width - padding, cornerradius + padding, width - padding, height - cornerradius - padding,
                                 width - padding - cornerradius, height - padding, padding + cornerradius, height - padding),
                                fill=color, outline=color)
            self.create_arc((padding, padding + rad, padding + rad, padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width - padding - rad, padding, width - padding, padding + rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width - padding, height - rad - padding, width - padding - rad, height - padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding, height - padding - rad, padding + rad, height - padding), start=180, extent=90, fill=color, outline=color)

        shape()
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.textid = self.create_text(width / 2, height / 2, text=text, fill='white', font=('Helvetica', '10', 'bold'))

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()

class FacebookScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Facebook Scraper")
        self.geometry("500x400")
        self.configure(bg='#f0f0f0')

        self.custom_font = font.Font(family="Helvetica", size=12)
        self.header_font = font.Font(family="Helvetica", size=16, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Label(self, text="Facebook Data Extractor", font=self.header_font, bg='#f0f0f0', fg='#2c3e50')
        header.pack(pady=20)

        # Frame for input fields
        input_frame = tk.Frame(self, bg='#f0f0f0')
        input_frame.pack(pady=10)

        # Username Label and Entry
        username_label = tk.Label(input_frame, text="Facebook Username:", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
        username_label.grid(row=0, column=0, pady=5, sticky='e')
        self.username_entry = tk.Entry(input_frame, width=30, font=self.custom_font)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        # Password Label and Entry
        password_label = tk.Label(input_frame, text="Facebook Password:", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
        password_label.grid(row=1, column=0, pady=5, sticky='e')
        self.password_entry = tk.Entry(input_frame, show='*', width=30, font=self.custom_font)
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)

        # Start Button
        self.start_button = RoundedButton(self, 150, 40, 10, 2, '#2ecc71', "Start Extraction", self.start_scraper)
        self.start_button.pack(pady=20)

        # Status Label
        self.status_label = tk.Label(self, text="", font=self.custom_font, bg='#f0f0f0', fg='#2c3e50')
        self.status_label.pack(pady=10)

        # Quit Button
        self.quit_button = RoundedButton(self, 100, 40, 10, 2, '#e74c3c', "Quit", self.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=20)

    def start_scraper(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password")
            return

        threading.Thread(target=self.run_scraper, args=(username, password)).start()

    def run_scraper(self, username, password):
        try:
            self.status_label.config(text="Extracting data... Please wait.")
            # Call your Facebook scraping function here
            main(username, password)
            self.status_label.config(text="Extraction completed successfully!")
            messagebox.showinfo("Success", "The Facebook data extraction process completed successfully.")
            
            result_folder = get_report_folder()
            os.startfile(result_folder)
        except Exception as e:
            self.status_label.config(text="Error occurred during extraction.")
            messagebox.showerror("Error", str(e))



def main(e_mail, pass_word):
    # Your Facebook credentials (ensure these are stored securely)
    email = e_mail
    password = pass_word
    username = email.split('@')[0]  # Use part of the email as username for directory names

    # Set up Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Login and capture Facebook content
    login_facebook(driver, email, password)
    close_notifications(driver)
    
    # Capture homepage
    take_screenshot(driver, "homepage")
    
    # Capture profile
    driver.get("https://www.facebook.com/me")
    time.sleep(3)
    take_screenshot(driver, "profile")

    # Extract friends list
    extract_friends(driver, username)

    # Generate PDF report
    generate_pdf_report(username)
    
    driver.quit()


if __name__ == "__main__":
    app = FacebookScraperApp()
    app.mainloop()