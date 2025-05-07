import tkinter as tk
from tkinter import messagebox, PhotoImage
import bcrypt
import random
import time
import threading

# Importing scraper modules
from insta_scraper import InstagramScraperApp
from google_scraper import main as google_main
from whatsapp import main as whatsapp_main
from twitter import TwitterScraperApp
from facebook import FacebookScraperApp

# Hashed credentials
USERNAME = "admin"
PASSWORD_HASH = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())

# Login attempt limit
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 30  # seconds

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
        r = self.radius
        w = self.width
        h = self.height
        self.create_oval(0, 0, 2*r, 2*r, fill=self.color, outline=self.color)
        self.create_oval(w-2*r, 0, w, 2*r, fill=self.color, outline=self.color)
        self.create_oval(0, h-2*r, 2*r, h, fill=self.color, outline=self.color)
        self.create_oval(w-2*r, h-2*r, w, h, fill=self.color, outline=self.color)
        self.create_rectangle(r, 0, w - r, h, fill=self.color, outline=self.color)
        self.create_rectangle(0, r, w, h - r, fill=self.color, outline=self.color)

    def _on_click(self):
        if self.command:
            self.command()

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x350")
        self.configure(bg="white")
        self.resizable(False, False)

        self.attempts = 0
        self.locked_until = 0
        self._create_widgets()
        self._generate_captcha()

    def _create_widgets(self):
        tk.Label(self, text="Login", font=("Helvetica", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=20)

        self.user_entry = self._create_labeled_entry("Username")
        self.pass_entry = self._create_labeled_entry("Password", show="*")

        self.captcha_label = tk.Label(self, text="", bg="white", font=("Helvetica", 12))
        self.captcha_label.pack(pady=(10, 2))
        self.captcha_entry = tk.Entry(self)
        self.captcha_entry.pack()

        RoundedButton(self, text="Login", color="#2980b9", command=self._check_login).pack(pady=20)

    def _create_labeled_entry(self, label, show=None):
        tk.Label(self, text=label, bg="white", anchor="w").pack(pady=(5, 0), padx=30, anchor="w")
        entry = tk.Entry(self, show=show)
        entry.pack(padx=30, fill="x")
        return entry

    def _generate_captcha(self):
        self.num1 = random.randint(10, 99)
        self.num2 = random.randint(10, 99)
        self.operator = random.choice(["+", "-"])
        self.answer = self.num1 + self.num2 if self.operator == "+" else self.num1 - self.num2
        self.captcha_label.config(text=f"Solve: {self.num1} {self.operator} {self.num2}")

    def _check_login(self):
        if time.time() < self.locked_until:
            remaining = int(self.locked_until - time.time())
            messagebox.showwarning("Locked", f"Too many failed attempts. Try again in {remaining} seconds.")
            return

        username = self.user_entry.get()
        password = self.pass_entry.get()
        captcha_input = self.captcha_entry.get()

        if username != USERNAME or not bcrypt.checkpw(password.encode(), PASSWORD_HASH):
            self._fail_attempt("Incorrect username or password.")
            return

        if not captcha_input.isdigit() or int(captcha_input) != self.answer:
            self._fail_attempt("Incorrect CAPTCHA.")
            return

        self.destroy()
        app = MainApp()
        app.mainloop()

    def _fail_attempt(self, msg):
        self.attempts += 1
        if self.attempts >= MAX_ATTEMPTS:
            self.locked_until = time.time() + LOCKOUT_TIME
            messagebox.showerror("Locked Out", f"Too many failed attempts. Try again in {LOCKOUT_TIME} seconds.")
        else:
            messagebox.showerror("Error", msg)
        self._generate_captcha()
        self.captcha_entry.delete(0, tk.END)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Forensic Tool")
        self.geometry("650x550")
        self.resizable(False, False)

        try:
            self.bg_image = PhotoImage(file="background.png")
            tk.Label(self, image=self.bg_image).place(relwidth=1, relheight=1)
        except:
            self.configure(bg="white")

        self._create_widgets()

    def _create_widgets(self):
        tk.Label(self, text="Social Media Forensic Tool", font=("Helvetica", 20, "bold"),
                 bg='white', fg='#2c3e50').pack(pady=30)

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

        RoundedButton(self, text="Quit", color="#95a5a6", command=self.quit).pack(pady=20)

    def _launch_app(self, AppClass):
        self.destroy()
        AppClass().mainloop()

    def _run_in_thread(self, func, name):
        def task():
            try:
                func()
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"{name} error: {e}"))
        threading.Thread(target=task, daemon=True).start()

    def start_instagram(self): self._launch_app(InstagramScraperApp)
    def start_google(self): self._run_in_thread(google_main, "Google")
    def start_whatsapp(self): self._run_in_thread(whatsapp_main, "WhatsApp")
    def start_twitter(self): self._launch_app(TwitterScraperApp)
    def start_facebook(self): self._launch_app(FacebookScraperApp)

if __name__ == "__main__":
    LoginWindow().mainloop()
