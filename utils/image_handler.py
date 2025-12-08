"""
Image Handler Module
Handles image validation, preprocessing, and conversion for OCR processing.
"""
import io
import base64
from PIL import Image
import numpy as np
import cv2
from typing import Tuple, Optional


class ImageHandler:
    """Handles image processing operations for license plate detection."""
    
    SUPPORTED_FORMATS = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_image(file_content: bytes, content_type: str) -> Tuple[bool, str]:
        """
        Validate uploaded image file.
        
        Args:
            file_content: Raw file bytes
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_content) > ImageHandler.MAX_FILE_SIZE:
            return False, "File size exceeds 10MB limit"
        
        # Check content type
        if content_type not in ImageHandler.SUPPORTED_FORMATS:
            return False, f"Unsupported format. Use: {', '.join(ImageHandler.SUPPORTED_FORMATS)}"
        
        # Try to open image
        try:
            img = Image.open(io.BytesIO(file_content))
            img.verify()
            return True, ""
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def bytes_to_cv2(file_content: bytes) -> np.ndarray:
        """
        Convert bytes to OpenCV image format.
        
        Args:
            file_content: Raw image bytes
            
        Returns:
            OpenCV image (numpy array)
        """
        nparr = np.frombuffer(file_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    
    @staticmethod
    def cv2_to_base64(img: np.ndarray) -> str:
        """
        Convert OpenCV image to base64 string for frontend display.
        
        Args:
            img: OpenCV image
            
        Returns:
            Base64 encoded image string
        """
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    
    @staticmethod
    def preprocess_for_ocr(img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            img: OpenCV image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    @staticmethod
    def resize_if_needed(img: np.ndarray, max_dimension: int = 1920) -> np.ndarray:
        """
        Resize image if it's too large while maintaining aspect ratio.
        
        Args:
            img: OpenCV image
            max_dimension: Maximum width or height
            
        Returns:
            Resized image
        """
        height, width = img.shape[:2]
        
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
