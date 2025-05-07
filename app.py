import tkinter as tk
from tkinter import messagebox, PhotoImage
import threading
import bcrypt
import random

from insta_scraper import InstagramScraperApp
from google_scraper import main as google_main
from whatsapp import main as whatsapp_main
from twitter import TwitterScraperApp
from facebook import FacebookScraperApp


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Social Media Forensic Tool")
        self.geometry("400x300")
        self.configure(bg="white")
        self.resizable(False, False)

        self.stored_username = "admin"
        self.stored_password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())

        self.captcha_result = None
        self._create_widgets()
        self.generate_captcha()

    def _create_widgets(self):
        tk.Label(self, text="Login", font=("Helvetica", 18, "bold"), bg="white").pack(pady=10)

        frame = tk.Frame(self, bg="white")
        frame.pack(pady=10)

        tk.Label(frame, text="Username:", bg="white").grid(row=0, column=0, sticky="e", pady=5)
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:", bg="white").grid(row=1, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        self.captcha_label = tk.Label(frame, text="", bg="white")
        self.captcha_label.grid(row=2, column=0, columnspan=2, pady=5)

        tk.Label(frame, text="Answer:", bg="white").grid(row=3, column=0, sticky="e")
        self.captcha_entry = tk.Entry(frame)
        self.captcha_entry.grid(row=3, column=1, pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.verify_login, bg="#3498db", fg="white")
        self.login_button.pack(pady=10)

    def generate_captcha(self):
        a, b = random.randint(10, 99), random.randint(10, 99)
        operation = random.choice(['+', '-'])
        if operation == '+':
            self.captcha_result = a + b
        else:
            self.captcha_result = a - b
        self.captcha_label.config(text=f"What is {a} {operation} {b}?")

    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        captcha_answer = self.captcha_entry.get()

        if username != self.stored_username:
            messagebox.showerror("Error", "Invalid username.")
            return

        if not bcrypt.checkpw(password.encode(), self.stored_password_hash):
            messagebox.showerror("Error", "Invalid password.")
            return

        try:
            if int(captcha_answer) != self.captcha_result:
                messagebox.showerror("Error", "Incorrect CAPTCHA.")
                self.generate_captcha()
                return
        except:
            messagebox.showerror("Error", "CAPTCHA must be a number.")
            return

        self.destroy()
        app = MainApp()
        app.mainloop()



class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, color, command=None, width=150, height=40, radius=20):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)

        self.command = command
        self.color = color
        self.radius = radius
        self.width = width
        self.height = height

        self._draw_button()
        self.create_text(width // 2, height // 2, text=text, fill="white", font=("Helvetica", 10, "bold"))
        self.bind("<Button-1>", lambda event: self._on_click())

    def _draw_button(self):
        r, w, h = self.radius, self.width, self.height

        self.create_oval(0, 0, 2*r, 2*r, fill=self.color, outline=self.color)
        self.create_oval(w-2*r, 0, w, 2*r, fill=self.color, outline=self.color)
        self.create_oval(0, h-2*r, 2*r, h, fill=self.color, outline=self.color)
        self.create_oval(w-2*r, h-2*r, w, h, fill=self.color, outline=self.color)

        self.create_rectangle(r, 0, w-r, h, fill=self.color, outline=self.color)
        self.create_rectangle(0, r, w, h-r, fill=self.color, outline=self.color)

    def _on_click(self):
        if self.command:
            self.command()

# ---------------- MAIN APP ----------------

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Forensic Tool")
        self.geometry("650x550")
        self.resizable(False, False)

        try:
            self.bg_image = PhotoImage(file="background.png")
            self.bg_label = tk.Label(self, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not loaded:", e)
            self.configure(bg="white")

        self._create_widgets()

    def _create_widgets(self):
        header = tk.Label(self, text="Social Media Forensic Tool", font=("Helvetica", 20, "bold"), bg='white', fg='#2c3e50')
        header.pack(pady=30)

        button_frame = tk.Frame(self, bg='white')
        button_frame.pack()

        buttons = [
            ("Instagram", "#f56040", self.start_instagram),
            ("Google", "#34a853", self.start_google),
            ("WhatsApp", "#075e54", self.start_whatsapp),
            ("Twitter", "#000000", self.start_twitter),
            ("Facebook", "#3b5998", self.start_facebook)
        ]

        for idx, (text, color, command) in enumerate(buttons):
            btn = RoundedButton(button_frame, text=text, color=color, command=command)
            btn.grid(row=idx // 2, column=idx % 2, padx=30, pady=20)

        quit_btn = RoundedButton(self, text="Quit", color="#95a5a6", command=self.quit)
        quit_btn.pack(pady=20)

    def start_instagram(self):
        self._launch_app(InstagramScraperApp)

    def start_google(self):
        self._run_in_thread(google_main, "Google")

    def start_whatsapp(self):
        self._run_in_thread(whatsapp_main, "WhatsApp")

    def start_twitter(self):
        self._launch_app(TwitterScraperApp)

    def start_facebook(self):
        self._launch_app(FacebookScraperApp)

    def _launch_app(self, AppClass):
        self.destroy()
        app = AppClass()
        app.mainloop()

    def _run_in_thread(self, func, name):
        def task():
            try:
                func()
            except Exception as e:
                self._show_error(f"{name} scraping error: {str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def _show_error(self, message):
        self.after(0, lambda: messagebox.showerror("Error", message))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
