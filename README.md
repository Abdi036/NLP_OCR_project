# 🚗 License Plate OCR Web Application

A complete AI-powered web application for detecting and extracting text from license plates using computer vision and optical character recognition.

![License Plate OCR](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## ✨ Features

- 🎯 **Automatic License Plate Detection** - Uses OpenCV with Haarcascade classifier
- 📝 **Text Extraction** - Powered by EasyOCR for accurate OCR
- 🎨 **Modern UI** - Beautiful dark theme with glassmorphism effects
- 📤 **Drag & Drop Upload** - Intuitive image upload interface
- ⚡ **Real-time Processing** - Instant feedback with loading animations
- 📊 **Confidence Scoring** - Shows detection confidence percentage
- 🖼️ **Visual Results** - Displays both original image and detected plate
- 🛡️ **Error Handling** - Comprehensive validation and user feedback
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## 🎬 Demo

Upload a car image → AI detects license plate → Text is extracted and displayed

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB+ RAM (for EasyOCR models)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Installation

### 1. Clone the Repository

```bash
cd /NLP_OCR_project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** The first run will download EasyOCR models (~100MB) automatically.

## 🎯 Running the Application

### Start the FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application

Open your web browser and navigate to:

```
http://localhost:8000
```

You should see the modern license plate OCR interface!

## 📖 Usage Guide

### Step 1: Upload an Image

- **Click** on the upload zone to browse files
- **Drag and drop** an image directly onto the upload zone
- Supported formats: JPG, PNG, WebP (max 10MB)

### Step 2: Processing

- The application automatically detects license plates using OpenCV
- Text is extracted using EasyOCR
- Processing typically takes 2-5 seconds

### Step 3: View Results

- **Plate Number**: Extracted text displayed prominently
- **Confidence Score**: Accuracy percentage with color coding
  - Green (80%+): High confidence
  - Yellow (50-79%): Medium confidence
  - Red (<50%): Low confidence
- **Images**: View original image with bounding box and cropped plate

### Step 4: Upload Another

Click "Upload Another" to process additional images.

## 🏗️ Project Structure

```
NLP_OCR_project/
├── main.py                 # FastAPI application
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── image_handler.py    # Image validation & preprocessing
│   ├── plate_detector.py   # OpenCV plate detection
│   └── ocr_processor.py    # EasyOCR text extraction
├── static/                 # Frontend files
│   ├── index.html          # Main HTML page
│   ├── css/
│   │   └── style.css       # Styling
│   └── js/
│       └── app.js          # Frontend logic
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

## 🔧 API Documentation

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "License Plate OCR API"
}
```

### Upload Image

```bash
POST /upload
Content-Type: multipart/form-data
```

Parameters:
- `file`: Image file (required)

Success Response:
```json
{
  "success": true,
  "message": "License plate successfully detected and extracted",
  "plate_text": "ABC1234",
  "confidence": 0.95,
  "original_image": "data:image/jpeg;base64,...",
  "plate_image": "data:image/jpeg;base64,...",
  "bounding_box": {
    "x": 150,
    "y": 200,
    "width": 300,
    "height": 100
  }
}
```

Error Response:
```json
{
  "success": false,
  "message": "No license plate detected in the image",
  "plate_text": null,
  "confidence": 0.0
}
```

### API Information

```bash
GET /api/info
```

## 🎨 Customization

### Adjust Detection Sensitivity

Edit `utils/plate_detector.py`:

```python
plates = self.plate_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,      # Adjust: 1.05-1.3
    minNeighbors=5,       # Adjust: 3-7
    minSize=(25, 25)      # Adjust minimum plate size
)
```

### Change OCR Languages

Edit `main.py`:

```python
ocr_processor = OCRProcessor(languages=['en', 'ar'], gpu=False)
```

Supported languages: en, ar, zh, fr, de, es, ja, ko, and [many more](https://www.jaided.ai/easyocr/)

### Enable GPU Acceleration

If you have CUDA-compatible GPU:

```python
ocr_processor = OCRProcessor(languages=['en'], gpu=True)
```

### Customize UI Theme

Edit `static/css/style.css` CSS variables:

```css
:root {
    --accent-purple: #667eea;  /* Primary color */
    --accent-pink: #f5576c;    /* Secondary color */
    /* ... more colors */
}
```

## 🐛 Troubleshooting

### Issue: EasyOCR models not downloading

**Solution:** Manually download models:
```bash
python -c "import easyocr; reader = easyocr.Reader(['en'])"
```

### Issue: OpenCV error "cv2.error"

**Solution:** Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install libgl1-mesa-glx libglib2.0-0

# macOS
brew install opencv
```

### Issue: "No license plate detected"

**Solutions:**
- Ensure license plate is clearly visible
- Good lighting conditions
- Plate faces the camera directly
- Image resolution is adequate (min 640x480)

### Issue: Low confidence scores

**Solutions:**
- Use higher resolution images
- Ensure plate is not blurred or obscured
- Try different lighting conditions
- Adjust detection parameters

## 🔒 Security Notes

- File upload size limited to 10MB
- Only image files accepted (JPEG, PNG, WebP)
- Input validation on all endpoints
- CORS configured (adjust for production)

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t plate-ocr .
docker run -p 8000:8000 plate-ocr
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **OpenCV** - Computer vision library
- **EasyOCR** - OCR engine
- **Haarcascade Classifiers** - Pre-trained models

---

Made with ❤️ using Python, FastAPI, OpenCV, and EasyOCR
