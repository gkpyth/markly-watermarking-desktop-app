import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

file_path = None
image = None
img_display_width = None
img_display_height = None

root = tk.Tk()
root.title("Markly")
root.geometry("1910x1025")
root.minsize(1910, 1025)

style = ttk.Style(root)
style.theme_use("clam")

style.configure("Main.TFrame", background="#1e1e2e")
style.configure("Panel.TFrame", background="#1e1e2e")
style.configure("TButton", background="#7c6af7", foreground="white", font=("Arial", 12), padding=30)

class RoundedButton:
    def __init__(self, parent, text, command, width=200, height=50, color="#7c6af7", bg="#2a2a3e"):
        self.parent = parent
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.normal_color = color
        self.hover_color = "#9d8ff9"
        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.draw(self.normal_color)
        self.canvas.bind("<Button-1>", lambda e: command())
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)

    def draw(self, color):
        self.canvas.delete("all")
        rounded_rectangle(self.canvas, 2, 2, self.width - 2, self.height - 2, radius=15, fill=color, outline="")
        self.canvas.create_text(self.width // 2, self.height // 2, text=self.text, fill="white", font=("Arial", 12))

    def on_enter(self, event):
        self.draw(self.hover_color)

    def on_leave(self, event):
        self.draw(self.normal_color)

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

def draw_empty_state():
    canvas.delete("all")
    rounded_rectangle(canvas, 1, 1, canvas.winfo_width() - 1, canvas.winfo_height() - 1, radius=20, outline="#444466", fill="#2a2a3e", width=3)
    canvas.create_text(canvas.winfo_width() // 2, canvas.winfo_height() // 2 - 80, text="Drop image here", fill="#888899", font=("Arial", 16))
    canvas.create_line(canvas.winfo_width() // 2 - 30, canvas.winfo_height() // 2, canvas.winfo_width() // 2- 115, canvas.winfo_height() // 2, fill="#888899", width=2)
    canvas.create_text(canvas.winfo_width() // 2, canvas.winfo_height() // 2, text="OR", fill="#888899", font=("Arial", 9))
    canvas.create_line(canvas.winfo_width() // 2 + 30, canvas.winfo_height() // 2, canvas.winfo_width() // 2 + 115, canvas.winfo_height() // 2,fill="#888899", width=2)
    canvas.create_window(canvas.winfo_width() // 2, canvas.winfo_height() // 2 + 105, window=browse_btn.canvas)

def draw_loaded_state():
    canvas.delete("all")
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=photo, anchor="center")
    canvas.image = photo
    img_x = (canvas.winfo_width() - img_display_width) // 2
    img_y = (canvas.winfo_height() - img_display_height) // 2
    canvas.create_rectangle(img_x, img_y, img_x + img_display_width, img_y + img_display_height, outline="#444466", width=3)

def on_canvas_resize(event):
    if file_path:
        draw_loaded_state()
    else:
        draw_empty_state()

def browse_image():
    global file_path, image, img_display_width, img_display_height
    filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp")]
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        image = Image.open(file_path)

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)

        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        img_display_width = new_width
        img_display_height = new_height

        image = image.resize((new_width, new_height))

        draw_loaded_state()

main_frame = ttk.Frame(root, style="Main.TFrame")
panel_frame = ttk.Frame(root, style="Panel.TFrame")
canvas = tk.Canvas(main_frame, bg="#1e1e2e", highlightthickness=0)
browse_btn = RoundedButton(canvas, text="Browse Image", width=240, height = 80, command=browse_image)

canvas.bind("<Configure>", on_canvas_resize)

root.columnconfigure(index=0, weight=4)
root.columnconfigure(index=1, weight=1)
root.rowconfigure(index=0, weight=1)

main_frame.columnconfigure(index=0, weight=1)
main_frame.rowconfigure(index=0, weight=1)

main_frame.grid(row=0, column=0,sticky="nsew")
panel_frame.grid(row=0, column=1, sticky="nsew")
canvas.grid(row=0, column=0, sticky="nsew", pady=17, padx=17)

root.mainloop()