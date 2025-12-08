/**
 * License Plate OCR - Frontend JavaScript
 * Handles image upload, drag-and-drop, and result display
 */

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadCard = document.getElementById('uploadCard');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const errorBox = document.getElementById('errorBox');
const errorMessage = document.getElementById('errorMessage');
const warningBox = document.getElementById('warningBox');
const warningMessage = document.getElementById('warningMessage');
const plateNumber = document.getElementById('plateNumber');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceBadge = document.getElementById('confidenceBadge');
const originalImage = document.getElementById('originalImage');
const plateImage = document.getElementById('plateImage');
const uploadAnotherBtn = document.getElementById('uploadAnotherBtn');

// API Configuration
const API_URL = '/upload';

// State
let isProcessing = false;

/**
 * Initialize event listeners
 */
function init() {
    // Click to upload
    uploadZone.addEventListener('click', () => {
        if (!isProcessing) {
            fileInput.click();
        }
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop events
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);

    // Upload another button
    uploadAnotherBtn.addEventListener('click', resetUI);

    // Prevent default drag behavior on document
    document.addEventListener('dragover', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => e.preventDefault());
}

/**
 * Handle drag over event
 */
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.remove('drag-over');
}

/**
 * Handle drop event
 */
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.remove('drag-over');

    if (isProcessing) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Handle file selection from input
 */
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Validate file before upload
 */
function validateFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
        return {
            valid: false,
            error: 'Invalid file type. Please upload a JPG, PNG, or WebP image.'
        };
    }

    if (file.size > maxSize) {
        return {
            valid: false,
            error: 'File size exceeds 10MB. Please upload a smaller image.'
        };
    }

    return { valid: true };
}

/**
 * Handle file processing
 */
async function handleFile(file) {
    // Validate file
    const validation = validateFile(file);
    if (!validation.valid) {
        showError(validation.error);
        return;
    }

    // Hide previous results and errors
    hideError();
    hideWarning();
    resultsSection.style.display = 'none';

    // Show loading state
    showLoading();

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload and process image
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to process image');
        }

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error processing image:', error);
        showError(error.message || 'Failed to process image. Please try again.');
        hideLoading();
    }
}

/**
 * Display processing results
 */
function displayResults(data) {
    hideLoading();

    if (!data.success) {
        // Show warning for unsuccessful detection
        showWarning(data.message);
        
        // Still show the original image if available
        if (data.original_image) {
            originalImage.src = data.original_image;
            resultsSection.style.display = 'block';
            
            // Hide plate-specific elements
            document.getElementById('plateDisplay').style.display = 'none';
            document.querySelector('.image-card:last-child').style.display = 'none';
        }
        return;
    }

    // Show all result elements
    document.getElementById('plateDisplay').style.display = 'block';
    document.querySelector('.image-card:last-child').style.display = 'block';

    // Display plate number
    plateNumber.textContent = data.plate_text || 'N/A';

    // Display confidence
    const confidence = Math.round(data.confidence * 100);
    confidenceValue.textContent = `${confidence}%`;
    
    // Update confidence badge color based on value
    updateConfidenceBadge(confidence);

    // Display images
    if (data.original_image) {
        originalImage.src = data.original_image;
    }
    
    if (data.plate_image) {
        plateImage.src = data.plate_image;
    }

    // Show results section with animation
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Update confidence badge styling based on confidence value
 */
function updateConfidenceBadge(confidence) {
    const badge = confidenceBadge;
    
    // Remove existing classes
    badge.style.background = '';
    badge.style.borderColor = '';
    badge.style.color = '';

    if (confidence >= 80) {
        // High confidence - green
        badge.style.background = 'rgba(72, 187, 120, 0.1)';
        badge.style.borderColor = 'rgba(72, 187, 120, 0.3)';
        badge.style.color = '#48bb78';
    } else if (confidence >= 50) {
        // Medium confidence - yellow/orange
        badge.style.background = 'rgba(237, 137, 54, 0.1)';
        badge.style.borderColor = 'rgba(237, 137, 54, 0.3)';
        badge.style.color = '#ed8936';
    } else {
        // Low confidence - red
        badge.style.background = 'rgba(245, 101, 101, 0.1)';
        badge.style.borderColor = 'rgba(245, 101, 101, 0.3)';
        badge.style.color = '#f56565';
    }
}

/**
 * Show loading state
 */
function showLoading() {
    isProcessing = true;
    uploadZone.style.display = 'none';
    loadingState.style.display = 'block';
}

/**
 * Hide loading state
 */
function hideLoading() {
    isProcessing = false;
    loadingState.style.display = 'none';
    uploadZone.style.display = 'block';
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorBox.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    errorBox.style.display = 'none';
}

/**
 * Show warning message
 */
function showWarning(message) {
    warningMessage.textContent = message;
    warningBox.style.display = 'flex';
}

/**
 * Hide warning message
 */
function hideWarning() {
    warningBox.style.display = 'none';
}

/**
 * Reset UI to initial state
 */
function resetUI() {
    resultsSection.style.display = 'none';
    hideError();
    hideWarning();
    fileInput.value = '';
    
    // Reset display elements
    document.getElementById('plateDisplay').style.display = 'block';
    document.querySelector('.image-card:last-child').style.display = 'block';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
