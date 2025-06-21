import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ExifTags
import os
import io
import zipfile
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📸 Camp Snap Photo Framer")

RATIOS = {
    "Instagram Landscape (1080x566)": (1080, 566),
    "Instagram Portrait (1080x1350)": (1080, 1350),
    "Instagram Story (1080x1920)": (1080, 1920),
    "Square (1080x1080)": (1080, 1080)
}

def round_exif_value(val):
    try:
        if isinstance(val, tuple) and len(val) == 2:
            return round(val[0] / val[1], 2)
        return round(float(val), 2)
    except:
        return val

def get_exif_data(img):
    try:
        exif_raw = img._getexif()
        if not exif_raw:
            return {}
        exif = {
            ExifTags.TAGS.get(k, k): v
            for k, v in exif_raw.items()
            if k in ExifTags.TAGS
        }
        return {
            "Aperture": round_exif_value(exif.get("FNumber")),
            "Shutter Speed": round_exif_value(exif.get("ExposureTime")),
            "ISO": round_exif_value(exif.get("ISOSpeedRatings")),
            "Focal Length": round_exif_value(exif.get("FocalLength")),
            "Date": exif.get("DateTimeOriginal")
        }
    except:
        return {}

def process_image(image, canvas_size, scale=1.0, x_offset=0, y_offset=0,
                  metadata=None, description="", filter_name="", font_path="arial.ttf",
                  show_date=True):
    frame = Image.new("RGB", canvas_size, "white")
    img = image.convert("RGB")

    new_width = int(canvas_size[0] * scale)
    aspect = img.height / img.width
    new_height = int(new_width * aspect)
    img = img.resize((new_width, new_height))

    x = int((canvas_size[0] - new_width) / 2 + x_offset)
    y = int((canvas_size[1] - new_height) / 2 + y_offset)
    image_bottom = y + new_height
    frame.paste(img, (x, y))

    draw = ImageDraw.Draw(frame)
    try:
        font = ImageFont.truetype(font_path, 24)
    except:
        font = ImageFont.load_default()

    text_y = image_bottom + 10

    if metadata:
        meta_text = " | ".join([f"{k}: {v}" for k, v in metadata.items() if v and k != "Date"])
        draw.text((30, text_y), meta_text, fill="black", font=font)
        text_y += 30

    if description:
        draw.text((30, text_y), description, fill="black", font=font)
        text_y += 30

    if filter_name:
        draw.text((30, text_y), f"Filter: {filter_name}.flt", fill="black", font=font)
        text_y += 30

    if show_date and metadata and metadata.get("Date"):
        draw.text((30, text_y), f"Date: {metadata['Date']}", fill="black", font=font)

    return frame

uploaded_files = st.file_uploader("Upload Camp Snap photos", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

canvas_type = st.selectbox("Select framing format", list(RATIOS.keys()))
canvas_size = RATIOS[canvas_type]

use_exif = st.checkbox("Extract EXIF metadata", value=True)
date_source = st.selectbox("Include date/time stamp", ["None", "From EXIF", "From file creation time"])
manual_override = st.checkbox("Override/add metadata manually")

manual_meta = {}
if manual_override:
    manual_meta = {
        "Aperture": st.text_input("Aperture"),
        "Shutter Speed": st.text_input("Shutter Speed"),
        "ISO": st.text_input("ISO"),
        "Focal Length": st.text_input("Focal Length"),
        "Date": st.text_input("Date (YYYY:MM:DD HH:MM:SS)")
    }

description = st.text_input("Polaroid-style description")
filter_name = st.text_input("Filter name (optional)")

scale = st.slider("Image scale", 0.2, 2.0, 1.0, 0.01)
x_offset = st.slider("Horizontal offset", -canvas_size[0]//2, canvas_size[0]//2, 0)
y_offset = st.slider("Vertical offset", -canvas_size[1]//2, canvas_size[1]//2, 0)

if uploaded_files:
    preview_img = Image.open(uploaded_files[0])
    meta = get_exif_data(preview_img) if use_exif else {}
    meta.update({k: v for k, v in manual_meta.items() if v})
    if date_source == "From file creation time":
        created_time = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        meta["Date"] = created_time
    elif date_source == "None":
        meta.pop("Date", None)
    preview = process_image(preview_img, canvas_size, scale, x_offset, y_offset,
                            meta, description, filter_name, show_date=(date_source != "None"))
    preview_width = 700
    preview_height = int(preview_width * canvas_size[1] / canvas_size[0])
    st.image(preview.resize((preview_width, preview_height)), caption="Preview", use_column_width=False)

    st.markdown("---")
    st.subheader("📲 Instagram Description")
    instadesc = "Shot on my Camp Snap and framed with Camp Snap Framer from [campsnaptools.com] #campsnaptools"
    st.code(instadesc, language="markdown")

    if len(uploaded_files) == 1:
        img_byte_arr = io.BytesIO()
        ext = os.path.splitext(uploaded_files[0].name)[1].lower().replace(".", "")
        save_format = "JPEG" if ext == "jpg" else ext.upper()
        preview.save(img_byte_arr, format=save_format)
        mime_type = f"image/jpeg" if ext == "jpg" else f"image/{ext}"
        st.download_button("Download JPG/PNG", img_byte_arr.getvalue(), file_name=f"framed_{uploaded_files[0].name}", mime=mime_type)
    else:
        if st.button("Download All as ZIP"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for uploaded_file in uploaded_files:
                    img = Image.open(uploaded_file)
                    meta = get_exif_data(img) if use_exif else {}
                    meta.update({k: v for k, v in manual_meta.items() if v})
                    if date_source == "From file creation time":
                        created_time = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                        meta["Date"] = created_time
                    elif date_source == "None":
                        meta.pop("Date", None)
                    framed = process_image(img, canvas_size, scale, x_offset, y_offset,
                                           meta, description, filter_name, show_date=show_date)
                    img_byte_arr = io.BytesIO()
                    ext = os.path.splitext(uploaded_file.name)[1].lower().replace(".", "")
                    save_format = "JPEG" if ext == "jpg" else ext.upper()
                    framed.save(img_byte_arr, format=save_format)
                    zip_file.writestr(f"framed_{uploaded_file.name}", img_byte_arr.getvalue())
            zip_buffer.seek(0)
            st.download_button("Download ZIP", zip_buffer, file_name="framed_photos.zip", mime="application/zip")
