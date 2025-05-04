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


def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Twitter Report")
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    return report_folder

def login_twitter(driver, username, password):
    driver.get("https://twitter.com/login")
    
    username_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
    )
    username_field.send_keys(username)
    driver.find_element(By.XPATH, "//span[text()='Next']").click()
    
    password_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
    )
    password_field.send_keys(password)
    driver.find_element(By.XPATH, "//span[text()='Log in']").click()
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
    )

def take_screenshot(driver, name):
    report_folder = get_report_folder()
    screenshot_name = os.path.join(report_folder, f"twitter_{name}.png")
    driver.save_screenshot(screenshot_name)
    print(f"Screenshot saved as {screenshot_name}")
    return screenshot_name

def wait_for_content_load(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='cellInnerDiv']"))
    )

def scroll_dialog_to_load_all(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_users(driver, expected_count, user_type):
    users_list = []
    try:
        timeline = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@aria-label='Timeline: {user_type.capitalize()}']"))
        )
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while len(users_list) < expected_count:
            user_elements = timeline.find_elements(By.XPATH, ".//div[@data-testid='cellInnerDiv']//a[@role='link']")
            
            for element in user_elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        username = href.split('/')[-1]
                        if username and username not in users_list:
                            users_list.append(username)
                            print(f"{user_type.capitalize()} found: {username}")
                            if len(users_list) >= expected_count:
                                break
                except Exception as e:
                    print(f"Error extracting username: {str(e)}")
                    continue

            if len(users_list) >= expected_count:
                break

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        if len(users_list) < expected_count:
            print(f"Warning: Only extracted {len(users_list)} {user_type} out of {expected_count} expected.")

    except Exception as e:
        print(f"Error extracting {user_type}: {str(e)}")

    return users_list

def get_followers_and_following(driver, username):
    report_folder = get_report_folder()
    
    driver.get(f"https://twitter.com/{username}/followers")
    wait_for_content_load(driver)
    followers_screenshot = take_screenshot(driver, "followers")
    followers = extract_users(driver, 100, "followers")  # Adjust the number as needed
    
    with open(os.path.join(report_folder, "followers.txt"), "w", encoding="utf-8") as f:
        for follower in followers:
            f.write(f"{follower}\n")
    
    driver.get(f"https://twitter.com/{username}/following")
    wait_for_content_load(driver)
    following_screenshot = take_screenshot(driver, "following")
    following = extract_users(driver, 100, "following")  # Adjust the number as needed
    
    with open(os.path.join(report_folder, "following.txt"), "w", encoding="utf-8") as f:
        for follow in following:
            f.write(f"{follow}\n")

    driver.get('https://twitter.com/notifications')
    time.sleep(5)
    notifications_screenshot = take_screenshot(driver, 'notifications')
    
    return followers, following, followers_screenshot, following_screenshot, notifications_screenshot



from PIL import Image, ImageDraw, ImageFont

def tweets_to_image(tweets, image_path):
    # Create a blank white image
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)

    # Use a truetype font (change path to your local font path)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font = ImageFont.load_default()

    # Write tweets onto the image
    text_y_position = 10
    for tweet in tweets:
        d.text((10, text_y_position), tweet, font=font, fill=(0, 0, 0))
        text_y_position += 20  # Adjust spacing between lines

    # Save the image
    img.save(image_path)



def generate_pdf_report(username, followers, following, homepage_screenshot, profile_screenshot, followers_screenshot, following_screenshot, notifications_screenshot, tweets_file):
    report_folder = get_report_folder()
    pdf_file = os.path.join(report_folder, f"{username}_twitter_report.pdf")
    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Add header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Twitter Report', 0, 1, 'C')
    pdf.ln(10)

    # Add screenshots
    pdf.set_font('Arial', 'B', 14)
    for screenshot_name, screenshot_path in [
        ('Homepage Screenshot', homepage_screenshot),
        ('Profile Screenshot', profile_screenshot),
        ('Followers Screenshot', followers_screenshot),
        ('Following Screenshot', following_screenshot),
        ('Notifications Screenshot', notifications_screenshot)
    ]:
        if os.path.exists(screenshot_path):
            pdf.cell(0, 7, screenshot_name, 0, 1)
            pdf.image(screenshot_path, 20, pdf.get_y(), 170)
            pdf.ln(80)
    
    # Add followers section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Followers', 0, 1)
    pdf.set_font('Arial', '', 12)
    for follower in followers[:20]:  # Limit to 20 followers to save space
        pdf.cell(0, 7, follower, 0, 1)
    if len(followers) > 20:
        pdf.cell(0, 7, f"... and {len(followers) - 20} more", 0, 1)
    pdf.ln(10)
    
    # Add following section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Following', 0, 1)
    pdf.set_font('Arial', '', 12)
    for following in following[:20]:  # Limit to 20 following to save space
        pdf.cell(0, 7, following, 0, 1)
    if len(following) > 20:
        pdf.cell(0, 7, f"... and {len(following) - 20} more", 0, 1)
    pdf.ln(10)
    
    # Add tweets section as image
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Tweets', 0, 1)
    tweets_image_path = os.path.join(report_folder, "tweets_image.png")
    
    # Convert the tweets into an image and add it to the PDF
    with open(tweets_file, 'r', encoding="utf-8") as f:
        tweets = f.readlines()
    tweets_to_image(tweets, tweets_image_path)
    
    pdf.image(tweets_image_path, 10, pdf.get_y(), 190)  # Adjust size as needed
    
    # Save PDF report
    pdf.output(pdf_file, 'F')
    print(f"PDF report generated successfully at {pdf_file}")





def capture_tweets(driver, username, tweet_count=50):
    """Capture tweets from the user's timeline and store them in a text file."""
    report_folder = get_report_folder()
    tweet_file_path = os.path.join(report_folder, "tweets.txt")
    
    driver.get(f"https://twitter.com/{username}")
    wait_for_content_load(driver)
    
    tweets = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(tweets) < tweet_count:
        # Locate tweet elements (using a more specific XPath for tweet content)
        tweet_elements = driver.find_elements(By.XPATH, "//article[@role='article']//div[@lang]")

        for element in tweet_elements:
            try:
                tweet_text = element.text.strip()
                if tweet_text and tweet_text not in tweets:
                    tweets.append(tweet_text)
                    print(f"Tweet found: {tweet_text}")
                    if len(tweets) >= tweet_count:
                        break
            except Exception as e:
                print(f"Error extracting tweet: {str(e)}")
                continue
        
        # Check if enough tweets have been captured
        if len(tweets) >= tweet_count:
            break

        # Scroll down to load more tweets
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Add a delay to ensure the next set of tweets loads
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Exit if no new content is loaded
        last_height = new_height

    # Save tweets to the text file
    with open(tweet_file_path, "w", encoding="utf-8") as f:
        for tweet in tweets:
            f.write(f"{tweet}\n\n\n\n")
    
    print(f"Tweets saved in {tweet_file_path}")
    return tweet_file_path



def main(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    login_twitter(driver, username, password)
    
    # Capture homepage
    wait_for_content_load(driver)
    homepage_screenshot = take_screenshot(driver, "homepage")
    
    # Capture profile
    driver.get(f"https://twitter.com/{username}")
    wait_for_content_load(driver)
    profile_screenshot = take_screenshot(driver, "profile")

    # Get followers and following
    followers, following, followers_screenshot, following_screenshot, notifications_screenshot = get_followers_and_following(driver, username)

    # Capture tweets
    tweet_files= capture_tweets(driver, username, tweet_count=50)  # Adjust the tweet_count as needed

    # Generate PDF report
    generate_pdf_report(username, followers, following, homepage_screenshot, profile_screenshot, followers_screenshot, following_screenshot, notifications_screenshot, tweet_files)
    
    driver.quit()

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

        shape()
        (x0, y0, x1, y1) = self.bbox("all")
        width = (x1 - x0)
        height = (y1 - y0)
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


class TwitterScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Twitter Scraper")
        self.geometry("500x400")
        self.configure(bg='#f0f0f0')

        self.custom_font = font.Font(family="Helvetica", size=12)
        self.header_font = font.Font(family="Helvetica", size=16, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Label(self, text="Twitter Data Extractor", font=self.header_font, bg='#f0f0f0', fg='#2c3e50')
        header.pack(pady=20)

        # Frame for input fields
        input_frame = tk.Frame(self, bg='#f0f0f0')
        input_frame.pack(pady=10)

        # Username Label and Entry
        username_label = tk.Label(input_frame, text="Twitter Username:", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
        username_label.grid(row=0, column=0, pady=5, sticky='e')
        self.username_entry = tk.Entry(input_frame, width=30, font=self.custom_font)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        # Password Label and Entry
        password_label = tk.Label(input_frame, text="Twitter Password:", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
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
            # Assuming `main` is your Twitter scraping function
            main(username, password)  # Replace this with your scraping function for Twitter
            self.status_label.config(text="Extraction completed successfully!")
            messagebox.showinfo("Success", "The Twitter data extraction process completed successfully.")
            
            # Assuming `get_report_folder` returns the folder where the data is saved
            result_folder = get_report_folder()  # Adjust this based on your implementation
            os.startfile(result_folder)
        except Exception as e:
            self.status_label.config(text="Error occurred during extraction.")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = TwitterScraperApp()
    app.mainloop()