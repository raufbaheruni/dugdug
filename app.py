import io
import os
import numpy as np
from flask import Flask, request, send_file
from PIL import Image, ImageFilter
import random
import logging

# Configure logging to see errors in Render logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def process_image_for_bypass(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB if it's RGBA (transparency)
        if img.mode == 'RGBA':
            # Fill black background for JPEG conversion
            background = Image.new('RGB', img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[3])
            img = background
        else:
            img = img.convert('RGB')
        
        # Convert to NumPy array
        img_np = np.array(img)
        
        # --- STRATEGY: Noise Injection & Compression ---
        
        # 1. Add Noise (Breaks AI patterns)
        # Generate noise with mean 0 and standard deviation 5
        noise = np.random.normal(0, 5, img_np.shape).astype(np.int16)
        img_np = np.clip(img_np.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # 2. Slight Blur (Simulates lens imperfection)
        img_pil = Image.fromarray(img_np)
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # 3. Compress to JPEG (Adds artifacts)
        output_buffer = io.BytesIO()
        img_pil.save(output_buffer, format='JPEG', quality=85, optimize=True)
        output_buffer.seek(0)
        return output_buffer
        
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        raise

@app.route('/')
def home():
    return "AI Bypass Server is Running! Port: " + str(os.environ.get('PORT', 8000))

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
        logger.error(f"Upload error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Force port 8000 for Render compatibility if ENV var is missing
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
