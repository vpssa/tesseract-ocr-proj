# ✍️ Handwritten Text OCR Pipeline

**Extract text from handwritten images with advanced preprocessing, OCR, and text cleaning.**  
A robust pipeline utilizing OpenCV, Tesseract, and FastAPI for seamless image-to-text conversion.

[![Google Colab](https://img.shields.io/badge/Open%20in%20Colab-blue?logo=googlecolab)](https://colab.research.google.com/github/keras-team/keras-io/blob/master/examples/vision/ipynb/handwriting_recognition.ipynb)
- **OCR Training and Inferencing Demo (Keras)☝️**

## 🚀 Features
- **Image Preprocessing**: Grayscale conversion, denoising, binarization, and skew correction.
- **OCR Extraction**: Supports multiple languages via Tesseract OCR.
- **Text Cleaning**: Removes noise, fixes common OCR errors, and structures text.
- **FastAPI Integration**: REST API endpoint for easy integration into applications.
- **Batch Processing**: Process all images in a directory automatically.

## 📦 Installation

### Prerequisites

1. **Install Tesseract OCR** (v5.3.0+ recommended):

   ```bash
   # Linux
   sudo apt-get install tesseract-ocr libtesseract-dev

   # macOS
   brew install tesseract

   # Windows: Download from [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)
   ```
   *Ensure Tesseract is added to your system's PATH.*
   
2. **Clone the repository:**
   
   ```bash
   git clone https://github.com/yourusername/handwritten-ocr-pipeline.git
   cd handwritten-ocr-pipeline
   ```
   
3. **Install Python dependencies:**
   
   ```bash
   pip install -r requirements.txt
   ```

### Project Structure

```bash
your-project-name/
├── images_raw/          # Raw input images
├── images_processed/    # Preprocessed images
├── ocr_output_raw/      # Raw OCR results
├── ocr_output_processed/ # OCR results from processed images
├── cleaned_text/        # Final cleaned text
├── temp_uploads/        # Temporary API uploads
└── src/                 # Source code
```

### 🛠 Usage

### 1. Run the Main Pipeline

  1. Place images in images_raw/ (e.g., image_raw_1.png).
  2. Execute the pipeline:
     
     ```bash
     python src/main_pipeline.py
     ```
  3. Check outputs in:
     images_processed/: Preprocessed images.
     cleaned_text/: Final cleaned text.
     
### 2. Use the FastAPI Endpoint

  1. Start the API server:
     ```bash
     uvicorn src.api:app --reload
     ```
  2. Visit *http://localhost:8000/docs* to access interactive Swagger documentation
  3. Upload an image via the /extract-text/ endpoint to receive JSON-formatted text.

### 🔧 Customization

  - **Preprocessing:** Adjust parameters in src/preprocess.py (e.g., blur kernel size, binarization method).
  - **OCR Language:** Modify the lang parameter in ocr_extract.py (e.g., lang='fra' for French).
  - **Text Cleaning:** Add custom regex rules in text_clean.py to fix domain-specific errors.

### 🐛 Troubleshooting

  - Tesseract Not Found: Set the Tesseract path explicitly in ocr_extract.py:
  ```bash
  pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Linux/macOS example
  ```
  - Image Skew Issues: Tweak the Radon transform parameters in correct_skew() (requires scikit-image).

### 🤝 Contributing

Contributions are welcome! Open an issue or submit a PR for:
  - Improved skew correction algorithms
  - Additional language support
  - Enhanced text structuring rules

