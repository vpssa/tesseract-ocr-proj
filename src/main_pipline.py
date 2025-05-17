import os
import shutil
from process import preprocess_image
from ocr_extract import extract_text_from_image
from text_clean import clean_ocr_text, structure_text

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Goes up one level to project root
RAW_IMAGES_DIR = os.path.join(BASE_DIR, "images_raw")
PROCESSED_IMAGES_DIR = os.path.join(BASE_DIR, "images_processed")
OCR_RAW_DIR = os.path.join(BASE_DIR, "ocr_output_raw")
OCR_PROCESSED_DIR = os.path.join(BASE_DIR, "ocr_output_processed")
CLEANED_TEXT_DIR = os.path.join(BASE_DIR, "cleaned_text")

# Create directories if they don't exist
DIRS_TO_CREATE = [
    RAW_IMAGES_DIR, PROCESSED_IMAGES_DIR, OCR_RAW_DIR,
    OCR_PROCESSED_DIR, CLEANED_TEXT_DIR
]
for directory in DIRS_TO_CREATE:
    os.makedirs(directory, exist_ok=True)

def process_single_image_pipeline(raw_image_filename):
    """
    Runs the full OCR pipeline for a single image.
    Returns the cleaned and structured text.
    """
    image_name_no_ext = os.path.splitext(raw_image_filename)[0]
    raw_image_path = os.path.join(RAW_IMAGES_DIR, raw_image_filename)

    if not os.path.exists(raw_image_path):
        print(f"Raw image {raw_image_path} not found. Skipping.")
        return None

    print(f"\n--- Processing: {raw_image_filename} ---")

    # 1. Preprocess Image
    print("Step 1: Preprocessing image...")
    processed_image_filename = f"{image_name_no_ext}_processed.png"
    processed_image_path = os.path.join(PROCESSED_IMAGES_DIR, processed_image_filename)
    preprocess_image(raw_image_path, processed_image_path)
    if not os.path.exists(processed_image_path):
        print(f"Failed to preprocess {raw_image_filename}. Skipping further steps for this image.")
        return None
    print(f"Processed image saved to: {processed_image_path}")

    # 2. OCR on Raw Image
    print("\nStep 2a: OCR on raw image...")
    raw_ocr_text = extract_text_from_image(raw_image_path)
    raw_ocr_output_path = os.path.join(OCR_RAW_DIR, f"{image_name_no_ext}_ocr_raw.txt")
    with open(raw_ocr_output_path, 'w', encoding='utf-8') as f:
        f.write(raw_ocr_text)
    print(f"Raw OCR output saved to: {raw_ocr_output_path}")

    # 3. OCR on Processed Image
    print("\nStep 2b: OCR on processed image...")
    processed_ocr_text = extract_text_from_image(processed_image_path)
    processed_ocr_output_path = os.path.join(OCR_PROCESSED_DIR, f"{image_name_no_ext}_ocr_processed.txt")
    with open(processed_ocr_output_path, 'w', encoding='utf-8') as f:
        f.write(processed_ocr_text)
    print(f"Processed OCR output saved to: {processed_ocr_output_path}")

    # 4. Text Cleaning and Structuring (using text from processed image)
    print("\nStep 3: Cleaning and structuring text...")
    # Prefer OCR from processed image for cleaning
    text_to_clean = processed_ocr_text if processed_ocr_text else raw_ocr_text
    
    cleaned_text = clean_ocr_text(text_to_clean)
    final_structured_text = structure_text(cleaned_text)

    cleaned_text_output_path = os.path.join(CLEANED_TEXT_DIR, f"{image_name_no_ext}_cleaned.txt")
    with open(cleaned_text_output_path, 'w', encoding='utf-8') as f:
        f.write(final_structured_text)
    print(f"Cleaned and structured text saved to: {cleaned_text_output_path}")
    print(f"--- Finished processing: {raw_image_filename} ---")
    
    return final_structured_text


def run_full_pipeline():
    """
    Runs the OCR pipeline for all images in the RAW_IMAGES_DIR.
    """
    raw_image_files = [f for f in os.listdir(RAW_IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]

    if not raw_image_files:
        print(f"No images found in {RAW_IMAGES_DIR}. Please add images to process.")
        print("Expected image names like 'image_raw_1.png', 'image_raw_2.png', etc.")
        # Create dummy images if they don't exist for a first run
        dummy_image_path1 = os.path.join(RAW_IMAGES_DIR, 'image_raw_1.png')
        dummy_image_path2 = os.path.join(RAW_IMAGES_DIR, 'image_raw_2.png')

        if not os.path.exists(dummy_image_path1):
            dummy_img = np.zeros((100, 400,3), dtype=np.uint8)
            cv2.putText(dummy_img, "Hello OCR World 1", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            cv2.imwrite(dummy_image_path1, dummy_img)
            print(f"Created dummy image: {dummy_image_path1}")
        if not os.path.exists(dummy_image_path2):
            dummy_img = np.zeros((100, 400,3), dtype=np.uint8)
            cv2.putText(dummy_img, "Test Note Number Two", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,200), 2)
            cv2.imwrite(dummy_image_path2, dummy_img)
            print(f"Created dummy image: {dummy_image_path2}")
        raw_image_files = [f for f in os.listdir(RAW_IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]


    for raw_image_filename in raw_image_files:
        process_single_image_pipeline(raw_image_filename)

if __name__ == '__main__':
    # This makes sure cv2 and other imports are available when running main_pipeline directly
    import cv2 # For dummy image creation if needed
    import numpy as np # For dummy image creation if needed
    run_full_pipeline()
    print("\n--- OCR Pipeline Complete ---")
    print(f"Check the directories: {PROCESSED_IMAGES_DIR}, {OCR_RAW_DIR}, {OCR_PROCESSED_DIR}, {CLEANED_TEXT_DIR}")