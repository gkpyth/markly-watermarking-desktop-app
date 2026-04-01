# Markly

A desktop image watermarking app built with Python, Tkinter, and Pillow. Built as part of personal bootcamp portfolio projects.

## Features
- Load images from your file system via a modern drop zone UI
- Add **text watermarks** — diagonal, centered, semi-transparent
- Add **image watermarks** — centered logo/graphic overlay
- Preview the watermarked result before saving
- Export the watermarked image as PNG or JPG
- Cancel and reset to load a new image at any time
- Clean, modern dark UI with custom rounded buttons and card-based panel layout

## Requirements
- Python 3
- Pillow

## Installation
Install dependencies with:
```
pip install Pillow
```

## How to Run
```
python markly.py
```

## How to Use
1. Click **Browse Image** to load an image from your file system
2. Select watermark type: **Text** or **Image** using the toggle buttons
3. For **Text** mode — type your watermark text in the input field
4. For **Image** mode — click **Browse Image** in the settings panel to load a watermark graphic (PNG recommended)
5. Click **Preview** to apply and preview the watermark
6. Click **Save** to export the watermarked image to your file system
7. Click **Cancel** at any time to reset and start over

## Notes
- Text watermarks are applied diagonally at 45° centered on the image
- Image watermarks are scaled to 30% of the original image width and centered
- Text watermark types are applied at 25% opacity
- Image watermark types are applied at 50% opacity
- Cancel, Preview and Save buttons are disabled until an image is loaded
- Drag and drop is visual only — use Browse Image to load files

## Supported Formats
- Input: PNG, JPG, JPEG, BMP
- Output: PNG, JPG, JPEG

## Limitations
- Drag and drop is visual only due to Tkinter limitations on Windows
- Text watermark font size is fixed at 60px regardless of image resolution
- Watermark position and opacity are not currently user-configurable

## Author
Ghaleb Khadra