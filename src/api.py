from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import uuid 
import logging


#from .main_pipeline import process_single_image_pipeline # This might need adjustment

from .process import preprocess_image
from .ocr_extract import extract_text_from_image
from .text_clean import clean_ocr_text, structure_text


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Handwritten Text OCR API")

# Define base paths relative to this api.py file
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_SCRIPT_DIR) # This assumes api.py is in src/

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "temp_uploads")
PROCESSED_DIR_API = os.path.join(UPLOAD_DIR, "processed") # Store processed images for API requests temporarily

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR_API, exist_ok=True)


async def process_uploaded_image(image_path: str, original_filename: str):
    """
    Simplified pipeline for a single uploaded image.
    Takes an image path, processes it, and returns cleaned text.
    """
    logger.info(f"API: Starting processing for {original_filename}")
    
    # 1. Preprocess
    processed_image_name = f"processed_{uuid.uuid4().hex}_{original_filename}"
    processed_image_api_path = os.path.join(PROCESSED_DIR_API, processed_image_name)
    
    try:
        logger.info(f"API: Preprocessing {image_path} -> {processed_image_api_path}")
        preprocess_image(image_path, processed_image_api_path)
        if not os.path.exists(processed_image_api_path):
            logger.error("API: Preprocessing failed to create output file.")
            raise HTTPException(status_code=500, detail="Image preprocessing failed.")
    except Exception as e:
        logger.error(f"API: Preprocessing error: {e}")
        raise HTTPException(status_code=500, detail=f"Image preprocessing error: {str(e)}")

    # 2. OCR (on processed image)
    logger.info(f"API: Performing OCR on {processed_image_api_path}")
    try:
        ocr_text = extract_text_from_image(processed_image_api_path)
        if not ocr_text and os.path.exists(processed_image_api_path): # If no text, maybe try raw
            logger.warning("API: OCR on processed image yielded no text. Trying raw image.")
            ocr_text = extract_text_from_image(image_path) # Fallback to raw if processed yields nothing
    except Exception as e:
        logger.error(f"API: OCR extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR extraction error: {str(e)}")

    # 3. Clean and Structure
    logger.info("API: Cleaning and structuring text.")
    cleaned_text = clean_ocr_text(ocr_text)
    final_text = structure_text(cleaned_text)
    
    logger.info(f"API: Successfully processed {original_filename}")
    return final_text


@app.post("/extract-text/")
async def extract_text_endpoint(image: UploadFile = File(...)):
    """
    Accepts an image upload, processes it through the OCR pipeline,
    and returns the cleaned text as JSON.
    """
    # Create a unique filename for the uploaded image to avoid collisions
    unique_id = uuid.uuid4().hex
    original_filename = image.filename if image.filename else "unknown_image"
    temp_filename = f"{unique_id}_{original_filename}"
    temp_file_path = os.path.join(UPLOAD_DIR, temp_filename)

    logger.info(f"API: Received file: {original_filename}, saving to {temp_file_path}")

    try:
        # Save uploaded file temporarily
        with open(temp_file_path, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        
        # Process the saved image
        cleaned_text_result = await process_uploaded_image(temp_file_path, original_filename)

        return JSONResponse(content={
            "filename": original_filename,
            "cleaned_text": cleaned_text_result
        })
    except HTTPException as http_exc: # Re-raise HTTPExceptions
        logger.error(f"API: HTTPException during processing: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"API: General error during processing {original_filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        # Clean up: remove the temporary uploaded file and its processed version
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"API: Removed temporary raw file: {temp_file_path}")

            
        processed_image_api_path_to_clean = os.path.join(PROCESSED_DIR_API, f"processed_{unique_id}_{original_filename}")
        if os.path.exists(processed_image_api_path_to_clean):
            os.remove(processed_image_api_path_to_clean)
            logger.info(f"API: Removed temporary processed file: {processed_image_api_path_to_clean}")


if __name__ == "__main__":
    import uvicorn
    # uvicorn src.api:app --reload
    print("Starting FastAPI server. Access at http://127.0.0.1:8000/docs")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)