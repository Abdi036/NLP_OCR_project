"""
FastAPI License Plate OCR Application
Main application file with API endpoints for license plate detection and OCR.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any
import logging

from utils import ImageHandler, PlateDetector, OCRProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="License Plate OCR API",
    description="API for detecting and extracting text from license plates",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize processors
image_handler = ImageHandler()
plate_detector = PlateDetector()
ocr_processor = OCRProcessor(languages=['en'], gpu=False)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>License Plate OCR</h1><p>Frontend not found. Please ensure static/index.html exists.</p>",
            status_code=404
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "License Plate OCR API"}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process an image to detect and extract license plate text.
    
    Args:
        file: Uploaded image file
        
    Returns:
        JSON response with plate text, confidence, and processed images
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate image
        is_valid, error_msg = image_handler.validate_image(file_content, file.content_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Convert to OpenCV format
        img = image_handler.bytes_to_cv2(file_content)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Failed to process image")
        
        # Resize if needed
        img = image_handler.resize_if_needed(img)
        
        # Detect license plate
        logger.info("Detecting license plate...")
        plate_result = plate_detector.get_best_plate(img)
        
        if plate_result is None:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "No license plate detected in the image",
                    "plate_text": None,
                    "confidence": 0.0,
                    "original_image": image_handler.cv2_to_base64(img),
                    "plate_image": None
                }
            )
        
        plate_img, bbox = plate_result
        x, y, w, h = bbox
        
        # Draw bounding box on original image
        img_with_box = plate_detector.draw_plates(img, [bbox])
        
        # Preprocess plate image for OCR
        logger.info("Extracting text from license plate...")
        plate_preprocessed = image_handler.preprocess_for_ocr(plate_img)
        
        # Extract text using OCR
        ocr_result = ocr_processor.extract_plate_number(plate_img)
        
        if ocr_result is None:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "License plate detected but no text could be extracted",
                    "plate_text": None,
                    "confidence": 0.0,
                    "original_image": image_handler.cv2_to_base64(img_with_box),
                    "plate_image": image_handler.cv2_to_base64(plate_img)
                }
            )
        
        plate_text, confidence = ocr_result
        
        # Format response
        logger.info(f"Successfully extracted plate: {plate_text} (confidence: {confidence:.2f})")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "License plate successfully detected and extracted",
                "plate_text": plate_text,
                "confidence": float(confidence),
                "original_image": image_handler.cv2_to_base64(img_with_box),
                "plate_image": image_handler.cv2_to_base64(plate_img),
                "bounding_box": {"x": x, "y": y, "width": w, "height": h}
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing image: {str(e)}"
        )


@app.get("/api/info")
async def api_info():
    """Get API information and capabilities."""
    return {
        "name": "License Plate OCR API",
        "version": "1.0.0",
        "features": [
            "License plate detection using OpenCV",
            "Text extraction using EasyOCR",
            "Support for multiple image formats (JPEG, PNG, WebP)",
            "Automatic image preprocessing",
            "Confidence scoring"
        ],
        "supported_formats": list(ImageHandler.SUPPORTED_FORMATS),
        "max_file_size": f"{ImageHandler.MAX_FILE_SIZE / (1024*1024):.0f}MB"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
