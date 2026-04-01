import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix Windows DPI scaling issues

# ============================================================
# IMPORTS
# ============================================================
import tkinter as tk
from tkinter import ttk                                     # Themed widgets (modern look)
from tkinter import filedialog                              # OS file picker dialog
from PIL import Image, ImageTk, ImageDraw, ImageFont        # Pillow: image loading, manipulation, and Tkinter bridge

# ============================================================
# ROOT WINDOW SETUP
# ============================================================
root = tk.Tk()
root.title("Markly")
root.geometry("1910x1025")
root.minsize(1910, 1025)

# ============================================================
# STYLES (ttk theme and widget appearance)
# ============================================================
style = ttk.Style(root)
style.theme_use("clam")

style.configure("Main.TFrame", background="#1e1e2e")
style.configure("Panel.TFrame", background="#1e1e2e")
style.configure("TButton", background="#7c6af7", foreground="white", font=("Arial", 12), padding=30)
style.configure("TEntry", fieldbackground="#3a3a5e", foreground="white", insertcolor="white", borderwidth=0, font=("Arial", 11))

# ============================================================
# GLOBAL STATE VARIABLES
# ============================================================
file_path = None                                    # Path of the loaded image (None = no image loaded)
image = None                                        # The Pillow Image object (for processing)
img_display_width = None                            # Width of the resized image displayed on canvas
img_display_height = None                           # Height of the resized image displayed on canvas

watermark_type = tk.StringVar(value="text")         # Tracks selected watermark mode: "text" or "image"

watermarked_image = None                            # Store the watermarked image so Save can access it
watermark_path = None                               # Path of the loaded watermark image (None = no image loaded)

# ============================================================
# CLASSES (reusable custom widgets)
# ============================================================
class RoundedButton:
    """A clickable button drawn on a Canvas with rounded corners and hover effect."""
    def __init__(self, parent, text, command, width=200, height=50, color="#7c6af7", bg="#2a2a3e"):
        self.parent = parent
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.normal_color = color
        self.hover_color = lighten_color(color)
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

    def disable(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Enter>")
        self.canvas.unbind("<Leave>")
        self.draw("#555566")

    def enable(self):
        self.canvas.bind("<Button-1>", lambda e: self.command())
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.draw(self.normal_color)

class ToggleButton:
    """A toggle button that appears filled (selected) or outlined (deselected).
    Two ToggleButtons sharing the same StringVar will automatically sync with each other."""
    def __init__(self, parent, text, value, variable):
        self.parent = parent
        self.text = text                    # The text to be displayed on the button
        self.value = value                  # The value this button represents e.g. "text" or "image"
        self.variable = variable            # The shared StringVar (watermark_type global variable) that both buttons watch
        self.normal_color = "#7c6af7"
        self.ghost_color = "#2a2a3e"
        self.canvas = tk.Canvas(parent,width=120, height=40, bg="#2a2a3e" , highlightthickness=0)
        self.canvas.bind("<Button-1>", self.on_click)
        self.variable.trace_add("write", self.on_var_change)    # Watching for variable changes and calling on_var_change() to draw()
        self.draw()

    def on_click(self, event):
        self.variable.set(self.value)       # Set the shared variable to this button's value

    def on_var_change(self, *args):
        self.draw()                         # Redraw whenever the variable changes

    def draw(self):
        self.canvas.delete("all")
        if self.variable.get() == self.value:       # This button is selected
            rounded_rectangle(self.canvas, 2, 2, 118, 38, radius=15, fill=self.normal_color, outline="")
        else:                                       # This button is deselected
            rounded_rectangle(self.canvas, 2, 2, 118, 38, radius=15, fill=self.ghost_color, outline="#7c6af7", width=3)
        self.canvas.create_text(60, 20, text=self.text, fill="white", font=("Arial", 10, "bold"))

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def rounded_rectangle(canvas, x1, y1, x2, y2, radius=30, **kwargs):
    """Draws a rounded rectangle on a Canvas using a smoothed polygon.
    **kwargs passes styling args (fill, outline, width) straight through to create_polygon."""
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

def lighten_color(hex_color, amount=30):
    """Takes a hex color string and returns a slightly lighter version."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"

# ============================================================
# DRAW FUNCTIONS (called by <Configure> bindings and state changes)
# ============================================================
def draw_empty_state():
    """Draws the drop zone UI on the main canvas when no image is loaded."""
    canvas.delete("all")
    rounded_rectangle(canvas, 1, 1, canvas.winfo_width() - 1, canvas.winfo_height() - 1, radius=20, outline="#444466", fill="#2a2a3e", width=3)
    canvas.create_text(canvas.winfo_width() // 2, canvas.winfo_height() // 2 - 80, text="Drop image here", fill="#888899", font=("Arial", 16))
    canvas.create_line(canvas.winfo_width() // 2 - 30, canvas.winfo_height() // 2, canvas.winfo_width() // 2- 115, canvas.winfo_height() // 2, fill="#888899", width=2)
    canvas.create_text(canvas.winfo_width() // 2, canvas.winfo_height() // 2, text="OR", fill="#888899", font=("Arial", 9))
    canvas.create_line(canvas.winfo_width() // 2 + 30, canvas.winfo_height() // 2, canvas.winfo_width() // 2 + 115, canvas.winfo_height() // 2,fill="#888899", width=2)
    canvas.create_window(canvas.winfo_width() // 2, canvas.winfo_height() // 2 + 105, window=browse_btn.canvas)

def draw_loaded_state():
    """Draws the loaded image on the main canvas with a border around it."""
    canvas.delete("all")
    photo = ImageTk.PhotoImage(image)       # Converts Pillow image to Tkinter-compatible format
    canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=photo, anchor="center")
    canvas.image = photo                    # Keep reference to prevent garbage collection -> this gave me a headache - !!!REMEMBER!!!
    img_x = (canvas.winfo_width() - img_display_width) // 2
    img_y = (canvas.winfo_height() - img_display_height) // 2
    canvas.create_rectangle(img_x, img_y, img_x + img_display_width, img_y + img_display_height, outline="#444466", width=3)

def draw_type_card(event):
    """Draws the Watermark Type card with label and Text/Image toggle buttons."""
    type_card.delete("all")
    rounded_rectangle(type_card, x1=1, y1=1, x2=event.width - 1, y2=event.height - 1, radius=20, outline="#444466", fill="#2a2a3e", width=3)
    type_card.create_window(type_card.winfo_width() // 2, 35, window=type_label, anchor="center")
    type_card.create_window(type_card.winfo_width() // 2 - 65, 90, window=text_btn.canvas, anchor="center")
    type_card.create_window(type_card.winfo_width() // 2 + 65, 90, window=image_btn.canvas, anchor="center")

def draw_settings_card(event=None):
    """Draws the Watermark Settings card - content changes based on watermark_type's current value."""
    settings_card.delete("all")
    rounded_rectangle(settings_card, x1=1, y1=1, x2=settings_card.winfo_width() - 1, y2=settings_card.winfo_height() - 1, radius=20, outline="#444466", fill="#2a2a3e", width=3)
    if watermark_type.get() == "text":
        settings_label.configure(text="Watermark Text:")
        settings_card.create_window(settings_card.winfo_width() // 2, 45, window=settings_label, anchor="center")
        settings_card.create_window(settings_card.winfo_width() // 2, 100, window=text_entry, anchor="center")
    else:
        settings_label.configure(text="Watermark Image:")
        settings_card.create_window(settings_card.winfo_width() // 2, 45, window=settings_label, anchor="center")
        settings_card.create_window(settings_card.winfo_width() // 2, 100, window=watermark_browse_btn.canvas, anchor="center")

def draw_actions_card(event=None):
    """Draws the Actions card with 3 RoundedButtons - Cancel, Preview, and Save"""
    actions_card.delete("all")
    rounded_rectangle(actions_card, x1=1, y1=1, x2=actions_card.winfo_width() - 1, y2=actions_card.winfo_height() - 1, radius=20, outline="#444466", fill="#2a2a3e", width=3)
    actions_card.create_window(actions_card.winfo_width() // 2, 60, window=cancel_btn.canvas, anchor="center")
    actions_card.create_window(actions_card.winfo_width() // 2 - 80, 120, window=preview_btn.canvas, anchor="center")
    actions_card.create_window(actions_card.winfo_width() // 2 + 80, 120, window=save_btn.canvas, anchor="center")

def cancel():
    global file_path, image, img_display_width, img_display_height
    file_path=None
    image = None
    img_display_width = None
    img_display_height = None
    draw_empty_state()
    cancel_btn.disable()
    preview_btn.disable()
    save_btn.disable()

# ============================================================
# PILLOW FUNCTIONS
# ============================================================
def apply_watermark():
    global watermarked_image
    opacity = int(255 * 0.3)        # 0.0 = invisible, 1.0 = fully opaque
    if not file_path:
        return

    original = Image.open(file_path).convert("RGBA")
    overlay = Image.new("RGBA", original.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if watermark_type.get() == "text":
        text = text_entry.get()
        if not text:
            return

        font = ImageFont.truetype("arial.ttf", size=60)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        center_x = original.width // 2
        center_y = original.height // 2

        txt_img = Image.new("RGBA", original.size, (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)

        txt_draw.text((center_x -text_width // 2, center_y - text_height // 2), text, font=font, fill=(255, 255, 255, opacity))

        txt_img = txt_img.rotate(45, expand=False)
        overlay = Image.alpha_composite(overlay, txt_img)

    else:
        if not watermark_path:
            return

        watermark_img = Image.open(watermark_path).convert("RGBA")

        # Resize watermark to 30% (0.3) of original image width, maintaining aspect ratio
        wm_ratio = original.width * 0.3 / watermark_img.width
        wm_width = int(watermark_img.width * wm_ratio)
        wm_height = int(watermark_img.height * wm_ratio)
        watermark_img = watermark_img.resize((wm_width, wm_height))

        # Apply opacity - e.g. 0.5 = 50%
        opacity = int(255 * 0.5)
        r, g, b, a = watermark_img.split()
        a = a.point(lambda x: int(x * opacity / 255))
        watermark_img = Image.merge("RGBA", (r, g, b, a))

        # Paste centered onto overlay
        center_x = (original.width - wm_width) // 2
        center_y = (original.height - wm_height) // 2
        overlay.paste(watermark_img, (center_x, center_y), watermark_img)

    watermarked_image = Image.alpha_composite(original, overlay)
    display_watermarked()

# ============================================================
# EVENT / LOGIC FUNCTIONS (respond to user actions)
# ============================================================
def on_canvas_resize(event):
    """Fires whenever the main canvas is resized. Redraws the correct state."""
    if watermarked_image:
        display_watermarked()
    elif file_path:
        draw_loaded_state()
    else:
        draw_empty_state()

def browse_image():
    """Opens file dialog, loads selected image, scales it to fit canvas, and displays it."""
    global file_path, image, img_display_width, img_display_height
    filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp")]
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        image = Image.open(file_path)

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)       # Scale to fit without stretching

        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        img_display_width = new_width
        img_display_height = new_height

        image = image.resize((new_width, new_height))

        draw_loaded_state()

        cancel_btn.enable()
        preview_btn.enable()
        save_btn.enable()

def display_watermarked():
    """Converts watermarked image to RGB, resizes to fit canvas, and displays it with border."""
    global image, img_display_width, img_display_height

    # Convert RGBA to RGB for display
    display_img = watermarked_image.convert("RGB")

    # Resize to fit the canvas
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    ratio = min(canvas_width / display_img.width, canvas_height / display_img.height)
    new_width = int(display_img.width * ratio)
    new_height = int(display_img.height * ratio)
    img_display_width = new_width
    img_display_height = new_height
    display_img = display_img.resize((new_width, new_height))

    # Display on the canvas
    photo = ImageTk.PhotoImage(display_img)
    canvas.delete("all")
    canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=photo, anchor="center")
    canvas.image = photo
    img_x = (canvas.winfo_width() - new_width) // 2
    img_y = (canvas.winfo_height() - new_height) // 2
    canvas.create_rectangle(img_x, img_y, img_x + new_width, img_y + new_height, outline="#444466", width=3)

def browse_watermark():
    global watermark_path
    filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp")]
    watermark_path = filedialog.askopenfilename(filetypes=filetypes)

def save_image():
    if not watermarked_image:
        return

    filetypes = [("Image files", "*.png *.jpg *.jpeg")]
    save_path = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".png")

    if save_path:
        if save_path.endswith(".jpg") or save_path.endswith(".jpeg"):
            watermarked_image.convert("RGB").save(save_path)
        else:
            watermarked_image.save(save_path)

# ============================================================
# WIDGET CREATION (instantiate all widgets)
# ============================================================

# === Main Layout Frames ===
main_frame = ttk.Frame(root, style="Main.TFrame")
panel_frame = ttk.Frame(root, style="Panel.TFrame")

# === Main Canvas (image display area) ===
canvas = tk.Canvas(main_frame, bg="#1e1e2e", highlightthickness=0)
browse_btn = RoundedButton(canvas, text="Browse Image", width=240, height = 80, command=browse_image)

# === Panel: Type Card Widgets ===
type_card = tk.Canvas(panel_frame, bg="#1e1e2e", highlightthickness=0, height=150, width=150)
type_label = ttk.Label(type_card, text="Choose Watermark Type", background="#2a2a3e", foreground="#ffffff", font=("Arial", 11, "bold"))
text_btn = ToggleButton(type_card, text="Text", value="text", variable=watermark_type)
image_btn = ToggleButton(type_card, text="Image", value="image", variable=watermark_type)

# === Panel: Settings Card Widgets ===
settings_card = tk.Canvas(panel_frame, bg="#1e1e2e", highlightthickness=0, height=180, width=150)
settings_label = ttk.Label(settings_card, background="#2a2a3e", foreground="#ffffff", font=("Arial", 11, "bold"))
text_entry = ttk.Entry(settings_card, width=30)
watermark_browse_btn = RoundedButton(settings_card, text="Browse Image", width=180, height=45, bg="#2a2a3e", command=browse_watermark)

# === Panel: Actions Card Widgets ===
actions_card = tk.Canvas(panel_frame, bg="#1e1e2e", highlightthickness=0, height=180, width=150)
cancel_btn = RoundedButton(actions_card, text="Cancel", width=300, height=45, color="#e05555", bg="#2a2a3e", command=cancel)
preview_btn = RoundedButton(actions_card, text="Preview", width=140, height=45, color="#7c6af7", bg="#2a2a3e", command=apply_watermark)
save_btn = RoundedButton(actions_card, text="Save", width=140, height=45, color="#4caf82", bg="#2a2a3e", command=save_image)
cancel_btn.disable()
preview_btn.disable()
save_btn.disable()

# ============================================================
# EVENT BINDINGS
# ============================================================
canvas.bind("<Configure>", on_canvas_resize)
type_card.bind("<Configure>", draw_type_card)
settings_card.bind("<Configure>", draw_settings_card)
watermark_type.trace_add("write", lambda *args: draw_settings_card())
actions_card.bind("<Configure>", draw_actions_card)

# ============================================================
# GRID LAYOUT (place all widgets on screen)
# ============================================================

# Root Grid - 2 columns: main area (weight 4) and panel (weight 1)
root.columnconfigure(index=0, weight=4)
root.columnconfigure(index=1, weight=1)
root.rowconfigure(index=0, weight=1)

# Main Frame Grid - single cell, canvas fills it
main_frame.columnconfigure(index=0, weight=1)
main_frame.rowconfigure(index=0, weight=1)

# Panel Frame Grid - cards stack vertically with a spacer row at the bottom pushing cards up
panel_frame.columnconfigure(index=0, weight=1)
panel_frame.rowconfigure(index=0, weight=0)
panel_frame.rowconfigure(index=1, weight=0)
panel_frame.rowconfigure(index=2, weight=0)
panel_frame.rowconfigure(index=3, weight=1)

# Place Frames
main_frame.grid(row=0, column=0,sticky="nsew")
panel_frame.grid(row=0, column=1, sticky="nsew")

# Place Main Canvas
canvas.grid(row=0, column=0, sticky="nsew", pady=17, padx=(17, 0))

# Place Panel Cards
type_card.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 8))
settings_card.grid(row=1, column=0, sticky="ew", padx=15, pady=(15, 8))
actions_card.grid(row=2, column=0, sticky="ew", padx=15, pady=(15, 8))

# ============================================================
# START APPLICATION
# ============================================================
root.mainloop()
