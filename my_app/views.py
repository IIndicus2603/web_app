from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from tagger import predict_and_list_labels
import logging
import os
from detect_objects import load_custom_trained_model
import random

logger = logging.getLogger(__name__)
CONFIDENCE=0.55
model = load_custom_trained_model('ai_capstone.pt')

try:
    # Path to the mappings.json file
    mapping_file_path = os.path.join(settings.BASE_DIR, 'mappings.json')

    # Read and load JSON data from the file
    with open(mapping_file_path, 'r') as file:
        mappings_data = json.load(file)
except Exception as e:
    # Log error and set mappings_data to an empty dictionary
    logger.error(f"Error reading mappings.json: {e}")
    mappings_data = {}

# Function to handle the main page
def index(request):
    return render(request, 'index.html')

# Function to handle image-to-tag prediction requests
@csrf_exempt
def image2tag(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            base64_image = data.get('image')
            file_name = data.get('fileName')

            # Validate if image data is provided
            if not base64_image:
                return JsonResponse({'error': 'No image data provided'}, status=400)
            if ';base64,' not in base64_image:
                return JsonResponse({'error': 'Invalid base64 image format'}, status=400)

            # Split the Base64 image string into format and image data
            format, imgstr = base64_image.split(';base64,') 
            
            # Generate tags using the prediction function
            try:
                tags = predict_and_list_labels(imgstr, file_name,model, confidence=CONFIDENCE)
            except Exception as predict_error:
                logger.error("Error in predict_and_list_labels: %s", str(predict_error))
                return JsonResponse({'error': 'Error generating tags', 'details': str(predict_error)}, status=500)
            
            synonymous_tag = set()
            image_tags = []

            for tag in tags:
                # Add synonymous tags from mappings
                if tag in mappings_data:
                    synonymous_tag.update(mappings_data[tag])
                # Split tags with "/" and add them separately
                if "/" in tag:
                    image_tags.extend(part.strip() for part in tag.split("/"))
                else:
                    image_tags.append(tag)

            for tag in image_tags:
                if tag in synonymous_tag: synonymous_tag.remove(tag)
                
            # Limit total tags to 28-32 by removing excess tags
            max_tags = random.randint(28, 32)
            target_size = max_tags - len(image_tags)
            synonymous_tag = set(random.sample(list(synonymous_tag), min(len(synonymous_tag), target_size)))

            # Combine main tags and synonymous tags
            image_tags.extend(synonymous_tag)

            # Return tags as a JSON response
            return JsonResponse({'tags': image_tags}, status=200)

        except Exception as e:
            # Log any errors encountered
            logger.error("Error in image2tag: %s", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    # Handle non-POST requests
    return JsonResponse({'error': 'Invalid request method'}, status=405)
