"""
License Plate Detector Module
Uses OpenCV and Haarcascade classifier to detect license plates in images.
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
import urllib.request
import os


class PlateDetector:
    """Detects license plates in images using OpenCV."""
    
    # Haarcascade classifier for Russian license plates (works well for many plate types)
    HAARCASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_russian_plate_number.xml"
    HAARCASCADE_PATH = "haarcascade_russian_plate_number.xml"
    
    def __init__(self):
        """Initialize the plate detector and download cascade if needed."""
        self._download_cascade()
        self.plate_cascade = cv2.CascadeClassifier(self.HAARCASCADE_PATH)
    
    def _download_cascade(self):
        """Download Haarcascade classifier if not present."""
        if not os.path.exists(self.HAARCASCADE_PATH):
            try:
                print("Downloading Haarcascade classifier...")
                urllib.request.urlretrieve(self.HAARCASCADE_URL, self.HAARCASCADE_PATH)
                print("Cascade downloaded successfully!")
            except Exception as e:
                print(f"Error downloading cascade: {e}")
                raise
    
    def detect_plates(self, img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect license plates in the image.
        
        Args:
            img: OpenCV image (BGR format)
            
        Returns:
            List of bounding boxes [(x, y, w, h), ...]
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect plates using cascade classifier
        plates = self.plate_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25)
        )
        
        return plates.tolist() if len(plates) > 0 else []
    
    def detect_plates_contour_method(self, img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Alternative detection method using contour detection.
        Useful as fallback if Haarcascade fails.
        
        Args:
            img: OpenCV image
            
        Returns:
            List of potential plate bounding boxes
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter
        bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Edge detection
        edged = cv2.Canny(bilateral, 30, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        plates = []
        for contour in contours:
            # Approximate the contour
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # Look for rectangles (4 corners)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                
                # License plates typically have aspect ratio between 2:1 and 5:1
                if 2.0 <= aspect_ratio <= 5.0:
                    plates.append((x, y, w, h))
        
        return plates
    
    def get_best_plate(self, img: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        Detect and return the best (largest) license plate region.
        
        Args:
            img: OpenCV image
            
        Returns:
            Tuple of (plate_image, bounding_box) or None if no plate found
        """
        # Try Haarcascade first
        plates = self.detect_plates(img)
        
        # If no plates found, try contour method
        if not plates:
            plates = self.detect_plates_contour_method(img)
        
        if not plates:
            return None
        
        # Get the largest plate
        plates = sorted(plates, key=lambda p: p[2] * p[3], reverse=True)
        x, y, w, h = plates[0]
        
        # Extract plate region with some padding
        padding = 5
        y1 = max(0, y - padding)
        y2 = min(img.shape[0], y + h + padding)
        x1 = max(0, x - padding)
        x2 = min(img.shape[1], x + w + padding)
        
        plate_img = img[y1:y2, x1:x2]
        
        return plate_img, (x, y, w, h)
    
    def draw_plates(self, img: np.ndarray, plates: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Draw bounding boxes around detected plates.
        
        Args:
            img: OpenCV image
            plates: List of bounding boxes
            
        Returns:
            Image with drawn rectangles
        """
        img_copy = img.copy()
        
        for (x, y, w, h) in plates:
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(
                img_copy, "License Plate", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
            )
        
        return img_copy
