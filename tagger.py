from detect_objects import load_custom_trained_model, detect_objects, filter_results
from image_processing import load_image, save_image_with_annotations, format_detection_results
from train_model import train_custom_yolov5
from commons import values as common_values
import os
import base64
from io import BytesIO
import PIL
from PIL import  ImageOps
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Train and save the custom YOLOv5 model
def train_and_save_model(config_path, epochs=35):
    train_custom_yolov5(config_path, epochs=epochs)

# Save detection results to a JSON file
def save_detections_to_json(detections, output_path):
    import json
    try:
        with open(output_path, 'w') as f:
            json.dump(detections, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving detections to JSON: {e}", exc_info=True)
        
def resize_with_padding(image, target_size=(640, 640)):
    old_width, old_height = image.size
    target_width, target_height = target_size

    # Scale and preserve aspect ratio
    ratio = min(target_width / old_width, target_height / old_height)
    new_width, new_height = int(old_width * ratio), int(old_height * ratio)
    image = image.resize((new_width, new_height), PIL.Image.LANCZOS)

    # Create new image with padding
    new_image = PIL.Image.new("RGB", target_size, (0, 0, 0))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_image.paste(image, (paste_x, paste_y))

    return new_image

# Use the trained model to predict and return a list of qualified labels
def predict_and_list_labels(imgstr, image_name,model, confidence=0.6, boxes_dir="boxes"):
    try:
        
        # Load image from base64 string
        image = PIL.Image.open(BytesIO(base64.b64decode(imgstr)))

        # Applies a sharpening filter
        image = image.filter(PIL.ImageFilter.SHARPEN)

        # Resize image
        input_width, input_height = 640, 640
        image = resize_with_padding(image, (input_width, input_height))

        # Detect objects
        results = detect_objects(model, image)
        
        # Filter confident results
        detections = filter_results(results, confidence)
        
        # Save annotated image and detections
        os.makedirs(boxes_dir, exist_ok=True)
        save_image_with_annotations(image, detections, f'{boxes_dir}/{image_name}-boxes.jpg')
        save_detections_to_json(detections, f'{boxes_dir}/{image_name}-boxes.json')
        
        # Generate and return recommended tags
        detections_ = [common_values["classNames"][i["class"]] for i in detections]

        recommended_tags = sorted(list(set(detections_)), key=detections_.index)
        return recommended_tags
    except Exception as e:
        logger.error(f"Error in prediction pipeline: {e}", exc_info=True)
        return []

if __name__ == "__main__":
 predict_and_list_labels('test.jpg')