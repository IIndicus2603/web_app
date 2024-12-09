from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from tagger import predict_and_list_labels
import logging
import os

logger = logging.getLogger(__name__)
CONFIDENCE=0.55

# Function to handle the main page
def index(request):
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

    # Pass JSON data to the index.html template
    return render(request, 'index.html', {'mappings_data': json.dumps(mappings_data)})

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
                tags = predict_and_list_labels(imgstr, file_name, confidence=CONFIDENCE)
            except Exception as predict_error:
                logger.error("Error in predict_and_list_labels: %s", str(predict_error))
                return JsonResponse({'error': 'Error generating tags', 'details': str(predict_error)}, status=500)
            
            # Return tags as a JSON response
            return JsonResponse({'tags': tags}, status=200)

        except Exception as e:
            # Log any errors encountered
            logger.error("Error in image2tag: %s", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    # Handle non-POST requests
    return JsonResponse({'error': 'Invalid request method'}, status=405)
