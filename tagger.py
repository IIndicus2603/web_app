from detect_objects import load_custom_trained_model, detect_objects, filter_results
from image_processing import load_image, save_image_with_annotations, format_detection_results
from train_model import train_custom_yolov5
from commons import values as common_values
import os
import base64
from io import BytesIO
import PIL
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

# Use the trained model to predict and return a list of qualified labels
def predict_and_list_labels(imgstr, image_name, model_path='ai_capstone.pt', confidence=0.6, boxes_dir="boxes"):
    try:
        model = load_custom_trained_model(model_path)
        
        # Load image from base64 string
        image = PIL.Image.open(BytesIO(base64.b64decode(imgstr)))
        
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