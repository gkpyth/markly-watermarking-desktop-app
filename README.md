# Markly

A desktop image watermarking app built with Python, Tkinter, and Pillow.

## Features
- Load images from your file system
- Add text watermarks with custom content
- Add image watermarks using a logo or graphic
- Preview watermark before saving
- Export the watermarked image to your file system

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
- Click **Browse Images** (or drag and drop an image onto the canvas to load it - visual only - Tkinter limitation)
- Select watermark type: **Text** or **Image**
- Enter your watermark text or load a watermark image from the panel
- Click **Preview** to see the result
- Click **Save** to export the watermarked image

## Limitations
- Drag and drop is visual only — use Browse Images to load files
- Supported image formats: PNG, JPG, JPEG, BMP

## Author
Ghaleb Khadra