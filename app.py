import io
import os
import numpy as np
from flask import Flask, request, send_file
from PIL import Image, ImageFilter
import random

app = Flask(__name__)

def process_image_for_bypass(image_bytes):
    # 1. Load image
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Convert to NumPy array
        img_np = np.array(img)
        
        # --- STRATEGY: Noise Injection (Breaks AI Signals) ---
        # Add Gaussian noise to break AI's smooth gradients
        noise = np.random.normal(0, 5, img_np.shape).astype(np.int16) # Reduced noise slightly for stability
        img_np = np.clip(img_np.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Convert back to PIL Image
        img_pil = Image.fromarray(img_np)
        
        # Slight Blur for realism
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        # Compress to JPEG (Adds artifacts detectors look for)
        output_buffer = io.BytesIO()
        img_pil.save(output_buffer, format='JPEG', quality=85, optimize=True)
        output_buffer.seek(0)
        return output_buffer
    except Exception as e:
        raise Exception(f"Processing error: {str(e)}")

@app.route('/')
def home():
    return "AI Bypass Server is Running!"

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
        
        return send_file(
            processed_bytes,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='bypassed_image.jpg'
        )
    except Exception as e:
        # Log the error for debugging
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # 🔴 IMPORTANT: Use dynamic port for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
