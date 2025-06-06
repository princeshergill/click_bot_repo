import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from pathlib import Path

def run_bot():
    os.environ["XDG_SESSION_TYPE"] = "x11"
    script_path = Path(__file__).parent / "simulation.py"
    subprocess.run(["python", str(script_path)])

def main():
    root = tk.Tk()
    root.title("Search Click Bot")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack()

    label = tk.Label(frame, text="Click the button to start the simulation")
    label.pack(pady=(0, 10))

    start_btn = tk.Button(frame, text="Run Simulation", command=run_bot)
    start_btn.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
