import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

def create_tables():
    """Creates necessary tables in the database if they do not exist."""
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS workouts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        exercise TEXT,
                        duration INTEGER,
                        calories INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def register_user(username, password):
    """Registers a new user in the system."""
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists. Try a different one.")
    conn.close()

def login_user(username, password):
    """Verifies user login credentials."""
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def add_workout(user_id, exercise, duration, calories):
    """Logs a new workout session for the user."""
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    date = str(datetime.date.today())
    cursor.execute("INSERT INTO workouts (user_id, date, exercise, duration, calories) VALUES (?, ?, ?, ?, ?)", 
                   (user_id, date, exercise, duration, calories))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Workout added successfully!")

def plot_progress(user_id, canvas_frame):
    """Displays a progress graph of calories burned over time."""
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, calories FROM workouts WHERE user_id = ? ORDER BY date", (user_id,))
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        messagebox.showwarning("No Data", "No workouts found!")
        return
    
    dates = [datetime.datetime.strptime(d[0], "%Y-%m-%d") for d in data]
    calories = [d[1] for d in data]
    
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(dates, calories, marker='o', linestyle='-', color='b')
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories Burned")
    ax.set_title("Workout Progress Over Time")
    ax.grid()
    
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

def main():
    """Initializes the application with a login/register interface."""
    create_tables()
    root = tk.Tk()
    root.title("Personal Fitness Tracker")
    root.geometry("600x500")
    root.configure(bg="#2C3E50")
    
    frame = tk.Frame(root, bg="#34495E", padx=20, pady=20)
    frame.pack(pady=20)
    
    tk.Label(frame, text="Personal Fitness Tracker", font=("Arial", 20, "bold"), fg="white", bg="#34495E").pack()
    tk.Label(frame, text="Username:", bg="#34495E", fg="white").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack()
    tk.Label(frame, text="Password:", bg="#34495E", fg="white").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack()
    
    def attempt_login():
        """Handles user login attempt."""
        username = username_entry.get()
        password = password_entry.get()
        user_id = login_user(username, password)
        if user_id:
            messagebox.showinfo("Success", "Login successful!")
            show_dashboard(user_id)
        else:
            messagebox.showerror("Error", "Invalid login credentials!")
    
    tk.Button(frame, text="Login", command=attempt_login, bg="#27AE60", fg="white", width=15).pack(pady=5)
    tk.Button(frame, text="Register", command=lambda: register_user(username_entry.get(), password_entry.get()), bg="#2980B9", fg="white", width=15).pack()
    
    root.mainloop()

def show_dashboard(user_id):
    """Displays the main dashboard with workout tracking features."""
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("700x500")
    dashboard.configure(bg="#ECF0F1")
    
    tk.Label(dashboard, text="Dashboard", font=("Arial", 18, "bold"), bg="#ECF0F1").pack(pady=10)
    
    sections_frame = tk.Frame(dashboard, bg="#ECF0F1")
    sections_frame.pack()
    
    tk.Label(sections_frame, text="Exercise:", bg="#ECF0F1").grid(row=0, column=0)
    exercise_entry = tk.Entry(sections_frame)
    exercise_entry.grid(row=0, column=1)
    tk.Label(sections_frame, text="Duration (min):", bg="#ECF0F1").grid(row=1, column=0)
    duration_entry = tk.Entry(sections_frame)
    duration_entry.grid(row=1, column=1)
    tk.Label(sections_frame, text="Calories Burned:", bg="#ECF0F1").grid(row=2, column=0)
    calories_entry = tk.Entry(sections_frame)
    calories_entry.grid(row=2, column=1)
    
    def save_workout():
        """Saves the user's workout session."""
        add_workout(user_id, exercise_entry.get(), int(duration_entry.get()), int(calories_entry.get()))
    
    tk.Button(sections_frame, text="Add Workout", command=save_workout, bg="#27AE60", fg="white", width=15).grid(row=3, columnspan=2, pady=10)
    
    canvas_frame = tk.Frame(dashboard, bg="#ECF0F1")
    canvas_frame.pack(pady=20)
    
    tk.Button(dashboard, text="Show Progress", command=lambda: plot_progress(user_id, canvas_frame), bg="#2980B9", fg="white", width=15).pack()
    
    dashboard.mainloop()

if __name__ == "__main__":
    main()
