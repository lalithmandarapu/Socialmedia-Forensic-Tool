import tkinter as tk
from tkinter import messagebox, font, PhotoImage
import threading
import os

from insta_scraper import InstagramScraperApp
from google_scraper import main as google_main
from whatsapp import main as whatsapp_main
from twitter import TwitterScraperApp
from facebook import FacebookScraperApp

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5 * width or cornerradius > 0.5 * height:
            print("Error: cornerradius is too large.")
            return None

        rad = 2 * cornerradius
        def shape():
            self.create_polygon((padding, height - cornerradius - padding, padding, cornerradius + padding, padding + cornerradius, padding, width - padding - cornerradius, padding, width - padding, cornerradius + padding, width - padding, height - cornerradius - padding, width - padding - cornerradius, height - padding, padding + cornerradius, height - padding), fill=color, outline=color)
            self.create_arc((padding, padding + rad, padding + rad, padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width - padding - rad, padding, width - padding, padding + rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width - padding, height - rad - padding, width - padding - rad, height - padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding, height - padding - rad, padding + rad, height - padding), start=180, extent=90, fill=color, outline=color)
        
        shape()
        (x0, y0, x1, y1) = self.bbox("all")
        self.configure(width=(x1 - x0), height=(y1 - y0))
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.textid = self.create_text(width / 2, height / 2, text=text, fill='white', font=('Helvetica', '10', 'bold'))

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command:
            self.command()

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Forensic Tool")
        self.geometry("600x500")
        
        # Load Background Image
        self.bg_image = PhotoImage(file="background.png")  # Ensure the image is in the same folder
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)  # Set background image to cover entire window

        self.create_widgets()

    def create_widgets(self):
        header = tk.Label(self, text="Social Media Forensic Tool", font=("Helvetica", 16, "bold"), bg='white', fg='#2c3e50')
        header.pack(pady=20)

        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(pady=20)

        self.instagram_button = RoundedButton(button_frame, 150, 40, 10, 2, '#f56040', "Instagram", self.start_instagram)
        self.instagram_button.grid(row=0, column=0, padx=20, pady=20)

        self.google_button = RoundedButton(button_frame, 150, 40, 10, 2, '#34a853', "Google", self.start_google)
        self.google_button.grid(row=0, column=1, padx=20, pady=20)

        self.whatsapp_button = RoundedButton(button_frame, 150, 40, 10, 2, '#075e54', "WhatsApp", self.start_whatsapp)
        self.whatsapp_button.grid(row=0, column=2, padx=20, pady=20)

        self.twitter_button = RoundedButton(button_frame, 150, 40, 10, 2, '#000000', "Twitter", self.start_twitter)
        self.twitter_button.grid(row=1, column=0, padx=20, pady=20)

        self.facebook_button = RoundedButton(button_frame, 150, 40, 10, 2, '#3b5998', "Facebook", self.start_facebook)
        self.facebook_button.grid(row=1, column=1, padx=20, pady=20)

        self.quit_button = RoundedButton(self, 100, 40, 10, 2, '#95a5a6', "Quit", self.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=20)

    def start_instagram(self):
        self.destroy()
        instagram_app = InstagramScraperApp()
        instagram_app.mainloop()

    def start_google(self):
        threading.Thread(target=self.run_google_scraper).start()

    def start_whatsapp(self):
        threading.Thread(target=self.run_whatsapp_scraper).start()

    def start_twitter(self):
        self.destroy()
        twitter_app = TwitterScraperApp()
        twitter_app.mainloop()
    
    def start_facebook(self):
        self.destroy()
        facebook_app = FacebookScraperApp()
        facebook_app.mainloop()

    def run_google_scraper(self):
        try:
            google_main()
        except Exception as e:
            messagebox.showerror("Error", f"Google scraping error: {str(e)}")

    def run_whatsapp_scraper(self):
        try:
            whatsapp_main()
        except Exception as e:
            messagebox.showerror("Error", f"WhatsApp scraping error: {str(e)}")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()