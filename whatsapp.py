import os
import time
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Whatsapp_Report")
    os.makedirs(report_folder, exist_ok=True)
    return report_folder

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'WhatsApp Chat Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def capture_chat_list(driver):
    chats_xpath = "//div[@role='grid']//div[contains(@style, 'transform')]//span[@title]"
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, chats_xpath)))
    chats = driver.find_elements(By.XPATH, chats_xpath)
    return [chat.get_attribute("title") for chat in chats[:10]]

def extract_chat_messages(driver, chat_name):
    try:
        chat_xpath = f"//span[@title='{chat_name}']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, chat_xpath))).click()
        time.sleep(2)

        messages_xpath = "//div[contains(@class, 'message-in') or contains(@class, 'message-out')]"
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, messages_xpath)))
        messages = driver.find_elements(By.XPATH, messages_xpath)

        chat_content = []
        for msg in messages:
            try:
                sender = "You" if "message-out" in msg.get_attribute("class") else chat_name
                text_elem = msg.find_element(By.XPATH, ".//span[contains(@class, 'selectable-text')]")
                text = text_elem.text.strip()
                if text:
                    chat_content.append(f"{sender}: {text}")
            except:
                continue

        return chat_content

    except Exception as e:
        print(f"Failed to extract messages for {chat_name}: {e}")
        return []

def create_pdf(chat_data, pdf_file):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for chat_name, messages in chat_data.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Chat with {chat_name}", ln=True)
        pdf.set_font("Arial", size=11)
        for msg in messages:
            pdf.multi_cell(0, 10, msg)
        pdf.ln(5)
    pdf.output(pdf_file)

def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        os.system(f"open '{path}'")
    else:  # Linux
        os.system(f"xdg-open '{path}'")

def main():
    driver = setup_driver()
    report_folder = get_report_folder()
    pdf_file = os.path.join(report_folder, "whatsapp_report.pdf")

    try:
        driver.get("https://web.whatsapp.com/")
        print("Scan the QR code to log in...")
        WebDriverWait(driver, 160).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='grid']"))
        )
        print("Logged in successfully!")

        chat_list = capture_chat_list(driver)
        print(f"Chats found: {chat_list}")

        chat_data = {}
        for chat in chat_list:
            print(f"Extracting chat: {chat}")
            chat_data[chat] = extract_chat_messages(driver, chat)
            time.sleep(1)

        create_pdf(chat_data, pdf_file)
        print("PDF report created successfully.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("WhatsApp Scraper", "Data extraction complete!")
        open_folder(report_folder)

if __name__ == "__main__":
    main()
