import io
import os
import numpy as np
from flask import Flask, request, send_file
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import random

app = Flask(__name__)

def process_image_for_bypass(image_bytes):
    # 1. Load image
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Convert to NumPy array for pixel manipulation
    img_np = np.array(img)
    h, w, c = img_np.shape
    
    # --- STRATEGY 1: Noise Injection (Breaks AI Smooth Gradients) ---
    # AI images smooth hoti hain. Hum artificial noise dalenge jo real cameras ka signature hai.
    noise = np.random.normal(0, 10, img_np.shape).astype(np.int16) # 10 is noise strength
    img_np = np.clip(img_np.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # --- STRATEGY 2: Slight Blur (Simulates Lens Imperfection) ---
    # AI images aksar "too sharp" hoti hain. Thoda blur lens effect deta hai.
    img_pil = Image.fromarray(img_np)
    img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=0.5)) # Very slight blur
    
    # --- STRATEGY 3: JPEG Compression Artifacts ---
    # AI images usually high-quality PNG/JPEG hoti hain. Hum ise compress karenge taaki 
    # "blocking artifacts" aayein, jo real photos ka signature hote hain.
    output_buffer = io.BytesIO()
    img_pil.save(output_buffer, format='JPEG', quality=85, optimize=True)
    output_buffer.seek(0)
    
    return output_buffer

@app.route('/')
def home():
    return "AI Bypass Server is Running! Upload via /upload endpoint."

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    try:
        processed_bytes = process_image_for_bypass(file.read())
        processed_bytes.seek(0)
        
        # Return the processed image
        return send_file(
            processed_bytes,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='bypassed_ai_image.jpg'
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
