import cv2
import numpy as np
from skimage.transform import radon # For skew detection
from skimage.color import rgb2gray

def convert_to_grayscale(image_path):
    """Converts an image to grayscale."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_img

def denoise_image(gray_img):
    """Applies Gaussian blur for denoising."""
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    return blurred_img

def binarize_image(blurred_img):
    """Applies Otsu's binarization."""
    _, binary_img = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary_img

def correct_skew(image_cv):
    """
    Corrects skew in a binary image using Radon transform.
    This is a more robust method but can be computationally intensive.
    Input image should be binary (black and white).
    """
    if len(image_cv.shape) == 3: # Ensure it's grayscale or binary
        image_gray = rgb2gray(image_cv)
    else:
        image_gray = image_cv

    # Binarize if not already (Radon works best on binary)
    if image_gray.max() > 1: # Assuming it's not already 0-1 range
        thresh = np.median(image_gray) # Simple thresholding, consider Otsu
        image_binary = (image_gray > thresh).astype(np.uint8) * 255
    else:
        image_binary = (image_gray * 255).astype(np.uint8)


    # Radon transform
    sinogram = radon(image_binary)

    # Find the rotation angle
    r = np.array([np.sqrt(np.mean(np.abs(line) ** 2)) for line in sinogram.transpose()])
    rotation_angle_radon = np.argmax(r)
    # The radon function in scikit-image returns angles from 0 to 180 degrees.
    # We need to adjust this if the peak is near 0 or 180.
    # The angle from radon is theta, and the skew angle is often 90 - theta or theta - 90.
    skew_angle = -(90 - rotation_angle_radon) # Common heuristic

    # Rotate the image to correct skew
    (h, w) = image_cv.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
    rotated_img = cv2.warpAffine(image_cv, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # print(f"Detected skew angle: {skew_angle} degrees")
    return rotated_img


def preprocess_image(image_path, output_path):
    """Full preprocessing pipeline."""
    img_cv = cv2.imread(image_path)
    if img_cv is None:
        print(f"Error: Image not found at {image_path}")
        return None

    # 1. Grayscale Conversion
    gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # 2. Denoising
    denoised_img = denoise_image(gray_img)

    # 3. Binarization (Otsu's)
    # binary_img = binarize_image(denoised_img)
    # For skew correction, often better to apply it on grayscale or less harshly binarized
    # Let's try skew correction before final binarization

    # 4. Skew Correction (on denoised grayscale image)
    # Note: Skew correction is complex. This is one method.
    # It might be better to apply it to a binarized image if text contrast is very high.
    # Or, if Radon fails, a simpler projection profile method could be tried.
    # try:
    #     skew_corrected_img = correct_skew(denoised_img) # Pass the original color image if using rgb2gray inside
    # except Exception as e:
    #     print(f"Could not apply skew correction on {image_path}: {e}. Using denoised image.")
    #     skew_corrected_img = denoised_img # Fallback

    # 5. Binarization (apply after skew correction)
    final_binary_img = binarize_image(denoised_img)

    cv2.imwrite(output_path, final_binary_img)
    return output_path

if __name__ == '__main__':
    # Example usage:
    # Create dummy images if they don't exist for testing
    # Ensure you have images in 'images_raw/'
    import os
    if not os.path.exists('../images_raw/image_raw_1.png'):
        # Create a dummy image if it doesn't exist
        dummy_image = np.zeros((100, 400), dtype=np.uint8)
        cv2.putText(dummy_image, "Test Text Line 1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255), 2)
        cv2.putText(dummy_image, "Another skewed line", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255), 2)
        # Introduce a slight skew for testing correct_skew
        (h, w) = dummy_image.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, 5, 1.0) # 5 degree skew
        skewed_dummy_image = cv2.warpAffine(dummy_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        cv2.imwrite('../images_raw/image_raw_1.png', skewed_dummy_image)
        print("Created a dummy 'image_raw_1.png' for testing preprocess.py")

    if not os.path.exists('../images_processed/'):
        os.makedirs('../images_processed/')

    processed_file = preprocess_image('../images_raw/image_raw_1.png', '../images_processed/image_processed_1.png')
    if processed_file:
        print(f"Processed image saved to: {processed_file}")
    else:
        print("Preprocessing failed for image_raw_1.png")

