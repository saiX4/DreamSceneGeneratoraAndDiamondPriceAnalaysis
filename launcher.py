import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

# --- Configuration ---
# Color Palette (VS Code Style)
BG_COLOR = "#1e1e1e"       # Dark Background
CARD_COLOR = "#252526"     # Slightly lighter for contrast
TEXT_COLOR = "#ffffff"     # White text
ACCENT_1 = "#007acc"       # VS Code Blue (for Dream AI)
ACCENT_2 = "#4caf50"       # Green (for Diamond/Money)
HOVER_TINT = "#444444"     # Color when hovering

# Fonts
TITLE_FONT = ("Helvetica", 18, "bold")
BTN_FONT = ("Segoe UI", 12, "bold")

def run_dream_ai():
    try:
        subprocess.Popen([sys.executable, "gui.py"], cwd="DreamAi")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open DreamAi: {e}")

def run_diamond_analyzer():
    try:
        subprocess.Popen([sys.executable, "main.py"], cwd="DimonPriceAnalyzer")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Analyzer: {e}")

# --- Hover Effects ---
def on_enter(e, color):
    e.widget['bg'] = color

def on_leave(e, color):
    e.widget['bg'] = color

# --- Main Window Setup ---
root = tk.Tk()
root.title("JackFruit Launcher")
root.geometry("400x350")
root.configure(bg=BG_COLOR)

# Center the content
frame = tk.Frame(root, bg=BG_COLOR)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Title
lbl_title = tk.Label(frame, text="PROJECT LAUNCHER", font=TITLE_FONT, 
                     bg=BG_COLOR, fg=TEXT_COLOR)
lbl_title.pack(pady=(0, 30))

# --- Dream AI Button ---
# We use a Frame to create a 'border' effect if wanted, 
# but here we just use flat buttons with padding.
btn_dream = tk.Button(frame, text="✨ Launch Dream AI", 
                      font=BTN_FONT, 
                      bg=ACCENT_1, 
                      fg="white",
                      activebackground="#005f9e", 
                      activeforeground="white",
                      relief="flat",
                      width=25, height=2,
                      cursor="hand2",
                      command=run_dream_ai)
btn_dream.pack(pady=10)

# --- Diamond Analyzer Button ---
btn_dimon = tk.Button(frame, text="💎 Diamond Price Analyzer", 
                      font=BTN_FONT, 
                      bg=ACCENT_2, 
                      fg="white",
                      activebackground="#388e3c",
                      activeforeground="white",
                      relief="flat",
                      width=25, height=2,
                      cursor="hand2",
                      command=run_diamond_analyzer)
btn_dimon.pack(pady=10)

# Footer
lbl_footer = tk.Label(root, text="v1.0 • Python-Jackfruit", font=("Arial", 8), 
                      bg=BG_COLOR, fg="#666666")
lbl_footer.pack(side="bottom", pady=10)

root.mainloop()