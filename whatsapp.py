import os
import time
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
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Whatsapp Report")
    os.makedirs(report_folder, exist_ok=True)
    return report_folder

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'WhatsApp Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def capture_chat_list(driver):
    chats = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@aria-label='Chat list']//span[@title]"))
    )
    return [chat.get_attribute("title") for chat in chats[:10]]

def extract_chat_messages(driver, chat_name):
    try:
        chat = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@title='{chat_name}']"))
        )
        chat.click()
        time.sleep(2)
        messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in') or contains(@class, 'message-out')]")
        chat_content = []
        for msg in messages:
            sender = "You" if "message-out" in msg.get_attribute("class") else chat_name
            text = msg.text.strip()
            if text:
                chat_content.append(f"{sender}: {text}")
        return chat_content
    except Exception as e:
        print(f"Error extracting chat {chat_name}: {e}")
        return []

def create_pdf(chat_data, profile_pics, pdf_file):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for chat_name, messages in chat_data.items():
        pdf.cell(0, 10, f"Chat: {chat_name}", ln=True, align='L')
        for msg in messages:
            pdf.multi_cell(0, 10, msg)
        pdf.ln(5)
    pdf.output(pdf_file)

def main():
    driver = setup_driver()
    report_folder = get_report_folder()
    pdf_file = os.path.join(report_folder, "whatsapp_report.pdf")
    
    try:
        driver.get("https://web.whatsapp.com/")
        print("Please scan the QR code to continue...")
        WebDriverWait(driver, 160).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chat list']"))
        )
        print("QR code scanned successfully!")
        
        chat_list = capture_chat_list(driver)
        print(f"Chats Found: {chat_list}")
        
        chat_data = {}
        for chat in chat_list:
            chat_data[chat] = extract_chat_messages(driver, chat)
        
        create_pdf(chat_data, [], pdf_file)
        print("PDF report generated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Success", "WhatsApp data extraction completed successfully!")
        os.startfile(report_folder)

if __name__ == "__main__":
    main()
