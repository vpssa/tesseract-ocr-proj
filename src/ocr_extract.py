import pytesseract
from PIL import Image

def extract_text_from_image(image_path, lang='eng'):
    """
    Extracts text from an image using Tesseract OCR.
    :param image_path: Path to the image file.
    :param lang: Language for OCR (default is English).
    :return: Extracted text as a string.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang)
        return text
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return ""
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract is not installed or not found in your PATH.")
        print("Please install Tesseract and make sure it's added to your system's PATH.")
        print("More info: https://tesseract-ocr.github.io/tessdoc/Installation.html")
        return ""
    except Exception as e:
        print(f"An error occurred during OCR extraction: {e}")
        return ""

if __name__ == '__main__':
    # Example usage:
    # Ensure you have an image (e.g., from preprocess.py output)
    import os
    if not os.path.exists('../images_processed/image_processed_1.png'):
        print("Please run preprocess.py first or place a processed image at '../images_processed/image_processed_1.png'")
    else:
        text_output = extract_text_from_image('../images_processed/image_processed_1.png')
        print("\n--- OCR Output ---")
        print(text_output)
        print("--- End of OCR Output ---")

    # Example with a raw image (assuming it exists)
    if not os.path.exists('../images_raw/image_raw_1.png'):
        print("Place a raw image at '../images_raw/image_raw_1.png' for raw OCR test")
    else:
        text_raw_output = extract_text_from_image('../images_raw/image_raw_1.png')
        print("\n--- OCR Output (Raw Image) ---")
        print(text_raw_output)
        print("--- End of OCR Output (Raw Image) ---")