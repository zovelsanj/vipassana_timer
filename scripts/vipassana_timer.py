import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

if getattr(sys, "frozen", False):
    ROOT_DIR = sys._MEIPASS
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

INTRO_AUDIO = os.path.join(ASSETS_DIR, "intro.mp3")
END_AUDIO = os.path.join(ASSETS_DIR, "end.mp3")
METTA_AUDIO = os.path.join(ASSETS_DIR, "metta.mp3")

class VipassanaTimer:
    """Vipassana Timer application for managing meditation sessions with optional chantings 
    and Metta Bhawana practice as done in S. N. Goenka's Vipassana courses."""
    def __init__(self, root):
        self.root = root
        self.root.title("Vipassana Timer")
        self.root.geometry("600x600")
        self.root.minsize(600, 600)
        self.root.bind("<Configure>", self.resize_ui)

        self.remaining = 0
        self.running = False
        self.audio_process = None
        self.timer_job = None

        self.hours_var = tk.StringVar(value="00")
        self.minutes_var = tk.StringVar(value="30")
        self.display_var = tk.StringVar(value="00:30")

        self.intro_var = tk.BooleanVar(value=True)
        self.end_var = tk.BooleanVar(value=True)
        self.metta_var = tk.BooleanVar(value=False)

        self.build_ui()

    def build_ui(self):
        self.title_label = tk.Label(self.root, text="Vipassana Timer", font=("Arial", 32, "bold"))
        self.title_label.pack(pady=(30, 20))

        self.timer_frame = tk.Frame(self.root)
        self.timer_frame.pack(pady=8)

        self.hours_entry = tk.Entry(self.timer_frame, textvariable=self.hours_var, font=("Arial", 18), width=2, justify="center")
        self.hours_entry.pack(side="left")

        self.hours_label = tk.Label(self.timer_frame, text=" Hr ", font=("Arial", 24))
        self.hours_label.pack(side="left")

        self.minutes_entry = tk.Entry(self.timer_frame, textvariable=self.minutes_var, font=("Arial", 18), width=2, justify="center")
        self.minutes_entry.pack(side="left")

        self.minutes_label = tk.Label(self.timer_frame, text=" Min", font=("Arial", 24))
        self.minutes_label.pack(side="left")

        self.display = tk.Label(self.root, textvariable=self.display_var, font=("Arial", 40, "bold"))
        self.display.pack(pady=25)

        self.create_toggle("Intro Chanting", self.intro_var)
        self.create_toggle("End Chanting", self.end_var)
        self.create_toggle("Metta Bhawana", self.metta_var)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=30)

        self.start_button = tk.Button(self.button_frame, text="Start", font=("Arial", 12, "bold"), width=10, fg="green", command=self.start)
        self.start_button.pack(side="left", padx=8)

        self.stop_button = tk.Button(self.button_frame, text="Stop", font=("Arial", 12, "bold"), width=10, fg="red", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=8)

    def create_toggle(self, text, variable):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=70, pady=5)

        label = tk.Label(frame, text=text, font=("Arial", 12))
        label.pack(side="left")

        canvas = tk.Canvas(frame, width=50, height=26, highlightthickness=0, bd=0)
        canvas.pack(side="right")

        def draw_toggle(*args):
            canvas.delete("all")

            width = canvas.winfo_width()
            height = canvas.winfo_height()

            if width <= 1 or height <= 1:
                width = 50
                height = 26

            radius = height / 2
            knob = height - 6

            if variable.get():
                canvas.create_oval(0, 0, height, height, fill="green", outline="green")
                canvas.create_oval(width - height, 0, width, height,fill="green",outline="green")
                canvas.create_rectangle(radius, 0, width - radius, height, fill="green", outline="green")
                canvas.create_oval(width - height + 3, 3, width - 3, height - 3, fill="white", outline="white")
            else:
                canvas.create_oval(0, 0, height, height, fill="gray", outline="gray")
                canvas.create_oval(width - height, 0, width, height,fill="gray",outline="gray")
                canvas.create_rectangle(radius, 0, width - radius, height, fill="gray", outline="gray")
                canvas.create_oval(3, 3, knob + 3, knob + 3, fill="white", outline="white")

        def toggle(event):
            variable.set(not variable.get())

        canvas.bind("<Button-1>", toggle)
        variable.trace_add("write", draw_toggle)

        frame.label = label
        frame.canvas = canvas
        frame.toggle_variable = variable

        self.root.after(10, draw_toggle)

    def resize_ui(self, event):
        if event.widget != self.root:
            return

        scale = min(event.width / 420, event.height / 480)
        scale = max(0.75, min(scale, 2.0))

        self.title_label.config(font=("Arial", max(16, int(26 * scale)), "bold"))

        self.hours_entry.config(font=("Arial", max(12, int(18 * scale))))
        self.minutes_entry.config(font=("Arial", max(12, int(18 * scale))))
        self.hours_label.config(font=("Arial", max(9, int(12 * scale))))
        self.minutes_label.config(font=("Arial", max(9, int(12 * scale))))

        self.display.config(font=("Arial", max(24, int(40 * scale)), "bold"))

        self.start_button.config(font=("Arial", max(9, int(12 * scale)), "bold"), width=max(7, int(10 * scale)))
        self.stop_button.config(font=("Arial", max(9, int(12 * scale))), width=max(7, int(10 * scale)))

        for widget in self.root.winfo_children():
            if hasattr(widget, "label"):
                widget.label.config(font=("Arial", max(9, int(12 * scale))))

            if hasattr(widget, "canvas"):
                widget.canvas.config(width=int(50 * scale),height=int(26 * scale))

        self.button_frame.pack_configure(pady=int(30 * scale))
        
    def parse_time(self):
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())

            if hours < 0 or minutes < 0 or minutes >= 60:
                raise ValueError

            total = hours * 3600 + minutes * 60

            if total <= 0:
                raise ValueError

            return total

        except ValueError:
            messagebox.showerror("Invalid Time. Please enter a valid number of hours and minutes.")
            return None

    def start(self):
        if self.running:
            return

        total = self.parse_time()

        if total is None:
            return

        self.remaining = total
        self.running = True

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        if self.intro_var.get():
            self.play_audio(INTRO_AUDIO, self.start_countdown)
        else:
            self.start_countdown()

    def start_countdown(self):
        if not self.running:
            return

        self.update_display()
        self.timer_job = self.root.after(1000, self.update_timer)

    def update_timer(self):
        if not self.running:
            return

        self.remaining -= 1

        if self.remaining <= 0:
            self.display_var.set("00:00:00")
            self.finish()
            return

        self.update_display()
        self.timer_job = self.root.after(1000, self.update_timer)

    def update_display(self):
        hours, remainder = divmod(self.remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.display_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def timer_finished(self):
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
    def finish(self):
        self.running = False

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        if self.end_var.get():
            self.play_audio(END_AUDIO, self.play_metta)
        else:
            self.play_metta()

        if not self.end_var.get() and not self.metta_var.get():
            self.timer_finished()


    def play_metta(self):
        if self.metta_var.get():
            self.play_audio(METTA_AUDIO, self.timer_finished)
        else:
            self.timer_finished()

    def play_audio(self, path, callback=None):
        if not os.path.exists(path):
            messagebox.showerror("Missing Audio", f"File not found:\n{path}")

            if callback:
                callback()
            return

        try:
            self.audio_process = subprocess.Popen(["afplay", path])
            self.wait_for_audio(callback)

        except Exception as e:
            messagebox.showerror("Audio Error", str(e))

    def wait_for_audio(self, callback):
        if self.audio_process is not None:
            if self.audio_process.poll() is None:
                self.root.after(100, self.wait_for_audio, callback)
                return

        self.audio_process = None

        if callback:
            callback()

    def stop(self):
        self.running = False

        if self.audio_process is not None:
            if self.audio_process.poll() is None:
                self.audio_process.terminate()

            self.audio_process = None

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    VipassanaTimer(root)
    root.mainloop()
