import io
import os
import numpy as np
from flask import Flask, request, send_file
from PIL import Image, ImageFilter
import logging

# Setup logging for Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def process_image(image_bytes):
    try:
        # Load image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB (removes transparency issues)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        else:
            img = img.convert('RGB')
        
        # Convert to NumPy array for noise injection
        img_np = np.array(img)
        
        # 1. Add Noise (Breaks AI fingerprints)
        noise = np.random.normal(0, 10, img_np.shape).astype(np.int16)
        img_np = np.clip(img_np.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # 2. Slight Blur (Simulates camera lens)
        img_pil = Image.fromarray(img_np)
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=0.8))
        
        # 3. Compress to JPEG (Adds real-world artifacts)
        output = io.BytesIO()
        img_pil.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        return output
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise

@app.route('/')
def home():
    return "AI Bypass Server is Live! 🚀"

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file provided", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400
    
    try:
        processed = process_image(file.read())
        processed.seek(0)
        return send_file(
            processed,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='bypassed_ai_image.jpg'
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
