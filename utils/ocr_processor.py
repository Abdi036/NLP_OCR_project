"""
OCR Processor Module
Uses EasyOCR to extract text from license plate images.
"""
import easyocr
import numpy as np
from typing import List, Tuple, Optional
import re


class OCRProcessor:
    """Processes images to extract text using EasyOCR."""
    
    def __init__(self, languages: List[str] = ['en'], gpu: bool = False):
        """
        Initialize the OCR processor.
        
        Args:
            languages: List of language codes for OCR
            gpu: Whether to use GPU acceleration
        """
        self.reader = easyocr.Reader(languages, gpu=gpu)
    
    def extract_text(self, img: np.ndarray) -> List[Tuple[str, float]]:
        """
        Extract text from image using EasyOCR.
        
        Args:
            img: OpenCV image (can be BGR or grayscale)
            
        Returns:
            List of tuples (text, confidence)
        """
        results = self.reader.readtext(img)
        
        # Extract text and confidence
        text_results = [(text, conf) for (bbox, text, conf) in results]
        
        return text_results
    
    def extract_plate_number(self, img: np.ndarray) -> Optional[Tuple[str, float]]:
        """
        Extract license plate number from image.
        
        Args:
            img: OpenCV image of license plate
            
        Returns:
            Tuple of (plate_text, confidence) or None
        """
        results = self.extract_text(img)
        
        if not results:
            return None
        
        # Filter and clean results
        cleaned_results = []
        for text, conf in results:
            # Remove spaces and special characters, keep only alphanumeric
            cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
            
            # License plates typically have 4-10 characters
            if 4 <= len(cleaned) <= 10:
                cleaned_results.append((cleaned, conf))
        
        if not cleaned_results:
            # If no valid results after filtering, return the best raw result
            if results:
                text, conf = max(results, key=lambda x: x[1])
                return text.strip().upper(), conf
            return None
        
        # Return the result with highest confidence
        best_result = max(cleaned_results, key=lambda x: x[1])
        return best_result
    
    def extract_all_text(self, img: np.ndarray) -> str:
        """
        Extract all text from image as a single string.
        
        Args:
            img: OpenCV image
            
        Returns:
            Combined text string
        """
        results = self.extract_text(img)
        text_items = [text for text, _ in results]
        return ' '.join(text_items)
    
    @staticmethod
    def format_plate_number(plate_text: str) -> str:
        """
        Format plate number for display (add spacing if needed).
        
        Args:
            plate_text: Raw plate text
            
        Returns:
            Formatted plate text
        """
        # Remove all spaces first
        clean = re.sub(r'\s+', '', plate_text.upper())
        
        # Common format: ABC 1234 or AB 123 CD
        # You can customize this based on your region's plate format
        return clean
