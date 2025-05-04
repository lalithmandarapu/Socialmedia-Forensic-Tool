import tkinter as tk
from tkinter import messagebox, font
import threading

import pdfkit
import os
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


# New function to create and get the report folder path
def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Instagram Report")
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    return report_folder



def dismiss_popup(driver, xpath, timeout=10):
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        button.click()
        time.sleep(1)  # Short wait after clicking
    except TimeoutException:
        print(f"Popup with XPath '{xpath}' not found or already dismissed")

def take_screenshot(driver, name):
    report_folder = get_report_folder()
    screenshot_name = os.path.join(report_folder, f"instagram_{name}.png")
    driver.save_screenshot(screenshot_name)
    print(f"Screenshot saved as {screenshot_name}")


def generate_pdf_report():
    report_folder = get_report_folder()
    html_template_path = os.path.abspath("C:/Users/Admin/projects/social media parser/report_template.html")
    pdf_file = os.path.join(report_folder, "instagram_report.pdf")
    followers_file = os.path.join(report_folder, "followers_list.txt")
    following_file = os.path.join(report_folder, "following_list.txt")
    
    try:
        with open(html_template_path, 'r') as file:
            html_content = file.read()
        
        with open(followers_file, 'r') as file:
            followers_list = file.read()
        
        with open(following_file, 'r') as file:
            following_list = file.read()
        
        # Replace placeholders in the HTML template
        html_content = html_content.replace("{{ followers_list }}", followers_list)
        html_content = html_content.replace("{{ following_list }}", following_list)
        
        # Write the modified HTML to a temporary file
        temp_html_path = os.path.join(report_folder, "temp_report.html")
        with open(temp_html_path, 'w') as file:
            file.write(html_content)
        
        # Generate PDF from the temporary HTML file
        pdfkit.from_file(temp_html_path, pdf_file, options={"enable-local-file-access": ""})
        
        # Remove the temporary HTML file
        os.remove(temp_html_path)
        
        print("PDF generated successfully!")
    except Exception as e:
        print(f"Error generating PDF: {e}")

def scroll_dialog_to_load_all(driver):
     # Define the two possible class patterns for the dialog box
    script = """
    var scrollableDiv = document.querySelector('div[class*="xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq"]') || 
                        document.querySelector('div[class*="x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1sxyh0 xurb0ha x1uhb9sk x6ikm8r x1rife3k x1iyjqo2 x2lwn1j xeuugli xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1 x1l90r2v"]');
    if (scrollableDiv) {
        scrollableDiv.scrollTop = scrollableDiv.scrollHeight;
    }
    return scrollableDiv ? scrollableDiv.scrollHeight : 0;
    """
    
    last_height = driver.execute_script(script)

    while True:
        time.sleep(2)
        new_height = driver.execute_script(script)
        
        if new_height == last_height:
            break
        last_height = new_height


def extract_followers(driver, followers_file, expected_count):
    followers_list = []

    try:
        dialog = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        
        while len(followers_list) < expected_count:
            # Get current list of followers
            follower_elements = dialog.find_elements(By.XPATH, ".//div[contains(@class, 'x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3')]")
            
            for element in follower_elements:
                try:
                    follow_button = element.find_elements(By.XPATH, ".//div[contains(@class, '_acan _acap _acat')]")
                    if not follow_button:
                        username = element.find_element(By.XPATH, ".//span[@class='_ap3a _aaco _aacw _aacx _aad7 _aade']").text
                        if username and username not in followers_list:
                            followers_list.append(username)
                            print(f"Follower found: {username}")
                            if len(followers_list) >= expected_count:
                                break

                except NoSuchElementException:
                    continue

            if len(followers_list) >= expected_count:
                break

            # Scroll down
            scroll_dialog_to_load_all(driver)

        if len(followers_list) < expected_count:
            print(f"Warning: Only extracted {len(followers_list)} followers out of {expected_count} expected.")

    except Exception as e:
        print(f"Error extracting followers: {str(e)}")

    with open(followers_file, 'w', encoding='utf-8') as f:
        for follower in followers_list:
            f.write(f"{follower}\n")

    print(f"Followers list saved to {followers_file}")
    print(f"Total followers extracted: {len(followers_list)}")


def extract_following(driver, following_file, expected_count):
    following_list = []

    try:
        dialog = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        
        while len(following_list) < expected_count:
            # Get current list of following
            following_elements = dialog.find_elements(By.XPATH, ".//div[contains(@class, 'x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3')]")
            
            for element in following_elements:
                try:
                    follow_button = element.find_elements(By.XPATH, ".//div[contains(@class, '_acan _acap _acat')]")
                    if not follow_button:
                        username = element.find_element(By.XPATH, ".//span[@class='_ap3a _aaco _aacw _aacx _aad7 _aade']").text
                        if username and username not in following_list:
                            following_list.append(username)
                            print(f"Following found: {username}")
                            if len(following_list) >= expected_count:
                                break

                except NoSuchElementException:
                    continue

            if len(following_list) >= expected_count:
                break

            # Scroll down
            scroll_dialog_to_load_all(driver)

        if len(following_list) < expected_count:
            print(f"Warning: Only extracted {len(following_list)} following out of {expected_count} expected.")

    except Exception as e:
        print(f"Error extracting following: {str(e)}")

    with open(following_file, 'w', encoding='utf-8') as f:
        for following in following_list:
            f.write(f"{following}\n")

    print(f"Following list saved to {following_file}")
    print(f"Total following extracted: {len(following_list)}")






def navigate_to_profile(driver):
    try:
        page_source = driver.page_source
        username = None

        meta_tag_pattern = re.compile(r'"username":"(.*?)"')
        match = meta_tag_pattern.search(page_source)
        if match:
            username = match.group(1)

        if not username:
            json_pattern = re.compile(r'window\._sharedData\s*=\s*(\{.*?\});')
            match = json_pattern.search(page_source)
            if match:
                json_data = match.group(1)
                import json
                data = json.loads(json_data)
                user = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})
                username = user.get('username') if user else None
        print("Username:", username)
        
        profile_url = f"https://www.instagram.com/{username}/"
        driver.get(profile_url)
        print(profile_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//header[@role='banner']"))
        )
        
        print(f"Successfully navigated to profile page: {profile_url}")
        
        take_screenshot(driver, "profile")
        
    except Exception as e:
        print(f"Error navigating to profile: {str(e)}")
        print("Current URL:", driver.current_url)
        # take_screenshot(driver, "navigation_error")






def create_posts_folder():
    report_folder = get_report_folder()
    folder_name = os.path.join(report_folder, "Insta Posts")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def scroll_to_load_all_posts(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_post_urls(driver):
    post_elements = driver.find_elements(By.XPATH, "//div[@class='_aagv']/img")
    return [elem.get_attribute('src') for elem in post_elements]

def download_posts(urls, folder):
    for i, url in enumerate(urls, 1):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_extension = url.split('?')[0].split('.')[-1]
                file_name = f"post_{i}.{file_extension}"
                file_path = os.path.join(folder, file_name)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {file_name}")
            else:
                print(f"Failed to download post {i}")
        except Exception as e:
            print(f"Error downloading post {i}: {str(e)}")

def extract_and_save_posts(driver):
    try:
        folder = create_posts_folder()
        
        # Navigate to profile page (assuming we're already on the profile page)
        # If not, uncomment the next line and replace with the correct profile URL
        # driver.get("https://www.instagram.com/username")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='_aagv']"))
        )
        
        scroll_to_load_all_posts(driver)
        post_urls = extract_post_urls(driver)
        download_posts(post_urls, folder)
        
        print(f"All posts downloaded to {folder}")
    except Exception as e:
        print(f"Error extracting posts: {str(e)}")
        # take_screenshot(driver, "post_extraction_error")








def main(user_name, pass_word):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.instagram.com")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys(user_name)
        password_field.send_keys(pass_word)
        password_field.send_keys(Keys.RETURN)

        time.sleep(5)
        dismiss_popup(driver, "//div[@role='button' and text()='Not now']", timeout=10)
        dismiss_popup(driver, "//button[text()='Not Now']", timeout=10)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//main[@role='main']"))
        )
        time.sleep(5)
        take_screenshot(driver, "homepage")
        navigate_to_profile(driver)
        take_screenshot(driver, "profile")

        # Extract followers
        followers_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers')]"))
        )
        followers_count_text = followers_link.text
        followers_count = int(re.search(r'\d+', followers_count_text).group())
        print(f"Followers count: {followers_count}")
        followers_link.click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )

        time.sleep(5)
        take_screenshot(driver, "followers")
        
        followers_file = os.path.join(get_report_folder(), "followers_list.txt")
        extract_followers(driver, followers_file, followers_count)

        # Close the followers dialog
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(@class, '_abl-')]"))
        )
        close_button.click()
        time.sleep(2)

        # Extract following
        following_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following')]"))
        )
        following_count_text = following_link.text
        following_count = int(re.search(r'\d+', following_count_text).group())
        print(f"Following count: {following_count}")
        following_link.click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )

        time.sleep(5)
        take_screenshot(driver, "following")
        
        following_file = os.path.join(get_report_folder(), "following_list.txt")
        extract_following(driver, following_file, following_count)




        # Close the followers dialog
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(@class, '_abl-')]"))
        )
        close_button.click()
        time.sleep(2)

        # Add the new post extraction feature
        extract_and_save_posts(driver)






    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # take_screenshot(driver, "error")
    finally:
        driver.quit()
        generate_pdf_report()




class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5*width:
            print("Error: cornerradius is greater than width.")
            return None

        if cornerradius > 0.5*height:
            print("Error: cornerradius is greater than height.")
            return None

        rad = 2*cornerradius
        def shape():
            self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill=color, outline=color)
            self.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90, fill=color, outline=color)

        id = shape()
        (x0,y0,x1,y1)  = self.bbox("all")
        width = (x1-x0)
        height = (y1-y0)
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.textid = self.create_text(width/2, height/2, text=text, fill='white', font=('Helvetica', '10', 'bold'))

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()

class InstagramScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Forensic Tool")
        self.geometry("500x400")
        self.configure(bg='#f0f0f0')

        self.custom_font = font.Font(family="Helvetica", size=12)
        self.header_font = font.Font(family="Helvetica", size=16, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Label(self, text="Instagram Data Extractor", font=self.header_font, bg='#f0f0f0', fg='#2c3e50')
        header.pack(pady=20)

        # Frame for input fields
        input_frame = tk.Frame(self, bg='#f0f0f0')
        input_frame.pack(pady=10)

        # Username Label and Entry
        username_label = tk.Label(input_frame, text="Instagram Username: ", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
        username_label.grid(row=0, column=0, pady=5, sticky='e')
        self.username_entry = tk.Entry(input_frame, width=30, font=self.custom_font)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        # Password Label and Entry
        password_label = tk.Label(input_frame, text="Instagram Password: ", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
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
            main(username, password)
            self.status_label.config(text="Extraction completed successfully!")
            messagebox.showinfo("Success", "The Instagram data extraction process completed successfully.")
            
            result_folder = get_report_folder()
            os.startfile(result_folder)
        except Exception as e:
            self.status_label.config(text="Error occurred during extraction.")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = InstagramScraperApp()
    app.mainloop()