# 📸 Camp Snap Photo Framer

A fun and simple Streamlit app to frame your Camp Snap photos with white borders, descriptions, metadata, and filter info — perfect for sharing on Instagram!

![Demo Banner](https://campsnaptools.com/banner-placeholder.jpg) <!-- Optional: add your image -->

## ✨ Features

- Upload one or multiple `.jpg`, `.jpeg`, or `.png` files
- Choose from popular framing formats:
  - Instagram Landscape (1080x566)
  - Instagram Portrait (1080x1350)
  - Instagram Story (1080x1920)
  - Square (1080x1080)
- Optional image scaling and positioning
- Add a "Polaroid-style" description
- Add a filter name (appends `.flt` automatically)
- Extract EXIF metadata (aperture, shutter, ISO, etc.)
- Choose whether to display:
  - No date
  - EXIF date
  - File creation time (upload time)
- Preview images and download:
  - Individually as JPG/PNG
  - In bulk as a ZIP
- Auto-generates an Instagram-friendly caption linking to [CampSnapTools.com](https://campsnaptools.com)

## 🚀 How to run

### Option 1: Run locally
```bash
pip install -r requirements.txt
streamlit run framer.py
