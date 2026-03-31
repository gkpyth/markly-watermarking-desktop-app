import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Markly")
root.geometry("1910x1025")
root.minsize(1910, 1025)

style = ttk.Style(root)
style.theme_use("clam")

style.configure("Main.TFrame", background="#1e1e2e")
style.configure("Panel.TFrame", background="#1e1e2e")
# style.configure("Canvas.TFrame", background="#2a2a3e")
style.configure("TButton", background="#7c6af7", foreground="white", font=("Arial", 12), padding=30)

class RoundedButton:
    def __init__(self, parent, text, command, width=200, height=50, color="#7c6af7"):
        self.parent = parent
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.normal_color = color
        self.hover_color = "#9d8ff9"
        self.canvas = tk.Canvas(parent, width=width, height=height, bg="#2a2a3e", highlightthickness=0)
        self.draw(self.normal_color)
        self.canvas.bind("<Button-1>", lambda e: command())
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)

    def draw(self, color):
        self.canvas.delete("all")
        rounded_rectangle(self.canvas, 2, 2, self.width - 2, self.height - 2, radius=15, fill=color, outline="")
        self.canvas.create_text(self.width // 2, self.height // 2, text=self.text, fill="white", font=("Arial", 12, "bold"))

    def on_enter(self, event):
        pass

    def on_leave(self, event):
        pass

def rounded_rectangle(canvas, x1, y1, x2, y2, radius=30, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def draw_border(event):
    canvas.delete("all")
    rounded_rectangle(canvas, 1, 1, event.width-1, event.height-1, radius=20, outline="#444466", fill="#2a2a3e", width=3)
    canvas.create_text(event.width // 2, event.height // 2 - 80, text="Drop image here", fill="#888899", font=("Arial", 16))
    canvas.create_line(event.width // 2 - 30, event.height // 2, event.width // 2- 115, event.height//2, fill="#888899", width=2)
    canvas.create_text(event.width // 2, event.height // 2, text="OR", fill="#888899", font=("Arial", 9))
    canvas.create_line(event.width // 2 + 30, event.height // 2, event.width // 2 + 115, event.height // 2,fill="#888899", width=2)
    canvas.create_window(event.width // 2, event.height // 2 + 115, window=browse_btn)

main_frame = ttk.Frame(root, style="Main.TFrame")
panel_frame = ttk.Frame(root, style="Panel.TFrame")
canvas = tk.Canvas(main_frame, bg="#1e1e2e", highlightthickness=0)
browse_btn = ttk.Button(canvas, text="Browse Images")

canvas.bind("<Configure>", draw_border)

root.columnconfigure(index=0, weight=4)
root.columnconfigure(index=1, weight=1)
root.rowconfigure(index=0, weight=1)

main_frame.columnconfigure(index=0, weight=1)
main_frame.rowconfigure(index=0, weight=1)

main_frame.grid(row=0, column=0,sticky="nsew")
panel_frame.grid(row=0, column=1, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew", pady=17, padx=17)

root.mainloop()