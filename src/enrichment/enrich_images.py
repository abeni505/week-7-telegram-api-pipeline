
import os
import json
from ultralytics import YOLO
from PIL import Image
import logging

# --- Configuration ---
# Configure logging to provide informative output. This helps in tracking the
# script's progress and debugging any issues.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Path Definitions ---
# Define the necessary paths. Using environment variables is a good practice
# for configurability, but we provide default values for ease of use.
RAW_IMAGES_DIR = os.getenv('RAW_IMAGES_DIR', 'data/raw/images')
PROCESSED_RESULTS_DIR = os.getenv('PROCESSED_RESULTS_DIR', 'data/processed/image_detections')
PROCESSED_LOG_FILE = os.path.join(PROCESSED_RESULTS_DIR, 'processed_log.json')

# --- Model Loading ---
# Load the pre-trained YOLOv8 model. 'yolov8n.pt' is a small and fast model,
# ideal for getting started with general object detection.
try:
    model = YOLO('yolov8n.pt')
    logging.info("YOLOv8 model loaded successfully.")
except Exception as e:
    logging.error(f"Fatal: Error loading YOLOv8 model: {e}")
    # If the model can't be loaded, the script cannot function.
    exit()

def load_processed_images():
    """
    Loads the set of already processed image file paths from a log file.
    This is a crucial step to avoid re-processing images every time the
    script runs, making the pipeline efficient.
    """
    try:
        if os.path.exists(PROCESSED_LOG_FILE):
            with open(PROCESSED_LOG_FILE, 'r') as f:
                return set(json.load(f))
    except (IOError, json.JSONDecodeError) as e:
        logging.warning(f"Could not read or parse the processed log file. Starting fresh. Error: {e}")
    return set()

def save_processed_images(processed_set):
    """
    Saves the updated set of processed image file paths to the log file.
    This maintains the state of our processing pipeline.
    """
    try:
        # Ensure the directory exists before saving the file.
        os.makedirs(PROCESSED_RESULTS_DIR, exist_ok=True)
        with open(PROCESSED_LOG_FILE, 'w') as f:
            json.dump(list(processed_set), f, indent=4)
    except IOError as e:
        logging.error(f"Could not write to the processed log file: {e}")

def process_new_images():
    """
    This is the main function. It recursively scans the image directory,
    identifies new images that haven't been processed, runs the YOLO model
    on them, and saves the detection results.
    """
    logging.info("Starting image processing run...")
    processed_images = load_processed_images()
    new_images_processed_count = 0

    if not os.path.exists(RAW_IMAGES_DIR):
        logging.error(f"Input directory not found: {RAW_IMAGES_DIR}. Please check the path.")
        return

    # Use os.walk() to recursively scan through the directory tree.
    for root, dirs, files in os.walk(RAW_IMAGES_DIR):
        for image_filename in files:
            full_image_path = os.path.join(root, image_filename)
            relative_path = os.path.relpath(full_image_path, RAW_IMAGES_DIR)

            if relative_path in processed_images:
                continue

            if not image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                continue

            # The message_id is derived from the image filename (e.g., "12345.jpg")
            filename_without_ext, _ = os.path.splitext(image_filename)

            try:
                # ** FIX: Attempt to convert filename to integer for message_id **
                message_id = int(filename_without_ext)
            except ValueError:
                # If conversion fails, log a warning and skip this file.
                logging.warning(f"Could not determine message_id from filename '{image_filename}'. Skipping file.")
                continue

            try:
                # Use Pillow to open the image; this also helps validate that it's a proper image file.
                with Image.open(full_image_path) as img:
                    # Perform object detection on the image.
                    results = model(img)

                detections = []
                for result in results:
                    for box in result.boxes:
                        detections.append({
                            'message_id': message_id,
                            'detected_object_class': model.names[int(box.cls)],
                            'confidence_score': float(box.conf),
                            'bounding_box': box.xyxy.tolist()[0] # [x1, y1, x2, y2]
                        })

                if detections:
                    output_filename = f'{message_id}.json'
                    output_path = os.path.join(PROCESSED_RESULTS_DIR, output_filename)
                    with open(output_path, 'w') as f:
                        json.dump(detections, f, indent=4)
                    logging.info(f"Saved {len(detections)} detections for image '{relative_path}'")

                # Mark this image's relative path as processed.
                processed_images.add(relative_path)
                new_images_processed_count += 1

            except Exception as e:
                logging.error(f"Failed to process image '{full_image_path}': {e}")

    if new_images_processed_count > 0:
        save_processed_images(processed_images)
        logging.info(f"Processing complete. Processed {new_images_processed_count} new image(s).")
    else:
        logging.info("No new images found to process.")


if __name__ == '__main__':
    process_new_images()
